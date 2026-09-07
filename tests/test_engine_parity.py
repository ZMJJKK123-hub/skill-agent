# -*- coding: utf-8 -*-
"""引擎平价集成测试：Fake 驱动主循环的全路径（守卫/闸/出口/协议行）。

对应重构计划「行为平价清单」的可离线验证项：
①流式协议行 ③空响应熔断 ④GameTest 闸 ⑤打回兜底 ⑥完成闸宽限
⑦双轮数上限 ⑧写前预算骨架 ⑩插话 defer ⑪KNOWN_ISSUES 首轮注入
⑬compact 延后 ⑮[CONCLUDED] ⑰todo nag + spill 豁免。
"""
from __future__ import annotations

import json

from core.domain.messages import UserMessage
from core.domain.session import Mode
from tests.conftest import EngineHarness
from tests.fakes import (FakeModelClient, FakeRegistry, empty_round,
                         text_round, tool_round)


def _run(h: EngineHarness, prompt: str = "做一个红宝石剑"):
    """输入：装配 + 用户提示。返回：引擎最终回复。"""
    return h.engine.run([UserMessage(content=prompt)])


# ---------- ① chat 基本回路 + 协议行 ----------

def test_chat_roundtrip_and_protocol_lines(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[text_round("你", "好")])
    assert _run(h) == "你好"
    reply_lines = [l for l in h.writer.lines if l.startswith("[reply]")]
    assert reply_lines == ['[reply] "你"', '[reply] "好"']  # JSON 编码逐 delta
    assert any(l.startswith("  [0] user") for l in h.writer.lines)  # [round] 快照


def test_chat_checkpoint_saved(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[text_round("ok")])
    _run(h)
    working = tmp_cwd / ".chat" / "working.jsonl"
    assert working.exists()  # 每轮开头落断点


# ---------- ⑪ KNOWN_ISSUES 首轮注入（仅 mod） ----------

def test_mod_known_issues_first_round(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.MOD, rounds=[
        tool_round(("c1", "todo", '{"items": []}')),
        text_round("完成"),
    ])
    (tmp_cwd / "src" / "test" / "java").mkdir(parents=True)
    (tmp_cwd / "src" / "test" / "java" / "T.java").write_text("@GameTest\n", encoding="utf-8")
    (tmp_cwd / "dist").mkdir()
    (tmp_cwd / "dist" / "mymod-1.0.jar").write_bytes(b"jar")
    h.registry.outputs["todo"] = "All required tests passed"
    # 第二轮收到的消息里应有首轮注入的 mandatory-first-step
    _run(h)
    flat = [getattr(m, "content", "") for m in h.client.calls[-1]]
    assert any("<mandatory-first-step>" in str(c) for c in flat)


# ---------- ④⑤ GameTest 出口闸：打回 + 兜底强制收尾 ----------

def test_mod_gametest_gate_reject_then_force(tmp_cwd):
    (tmp_cwd / "dist").mkdir()
    (tmp_cwd / "dist" / "mymod-1.0.jar").write_bytes(b"jar")
    h = EngineHarness(tmp_cwd, Mode.MOD, rounds=[
        text_round("MOD 完成"),   # 第一次打回（无测试文件）
        text_round("MOD 完成"),   # 第二次打回 + 自动构建
        text_round("MOD 完成"),   # 第三次 → dist 有 jar → 强制收尾
    ])
    result = _run(h)
    assert "[system]" in result and "强制收尾" in result
    assert "MOD 完成" in result  # 旧实现：用户内容 + 系统注记拼接
    flat = [str(getattr(m, "content", "")) for m in h.client.calls[-1]]
    assert any("<gametest-check> FAILED" in c for c in flat)


# ---------- ⑥ 完成闸宽限 → 强制收尾总结 ----------

def test_mod_completion_gate_grace_then_summarize(tmp_cwd):
    (tmp_cwd / "src" / "test" / "java").mkdir(parents=True)
    (tmp_cwd / "src" / "test" / "java" / "T.java").write_text("@GameTest\n", encoding="utf-8")
    (tmp_cwd / "dist").mkdir()
    (tmp_cwd / "dist" / "mymod-1.0.jar").write_bytes(b"jar")
    h = EngineHarness(tmp_cwd, Mode.MOD, rounds=[
        tool_round(("c1", "run_mod_test_cycle", "{}")),  # 触发完成闸首达
        tool_round(("c2", "read_file", '{"path": "x"}')),  # 宽限耗尽
    ], outputs={"run_mod_test_cycle": "RESULT: PASS\n(others)"},
        complete=["最终总结：MOD 完成"], completion_grace_rounds=1)
    result = _run(h)
    assert result == "最终总结：MOD 完成"  # 宽限耗尽走 summarize 而非闸文本
    flat = [str(getattr(m, "content", "")) for m in h.client.calls[1]]
    assert any("<completion-gate>" in c for c in flat)  # 首达注入收尾提醒


# ---------- ③ 空响应熔断 5→压缩 / ≥8→强制收尾 ----------

def test_empty_response_force_final(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT,
                      rounds=[empty_round() for _ in range(9)],
                      complete=["summary"])
    result = _run(h)
    assert "8 times in a row" in result
    # 1-4/6-7 轮注入了空响应警告（第 5 轮触发压缩重试不注入）
    warned = sum("<empty-response>" in str(getattr(m, "content", ""))
                 for call in h.client.calls for m in call)
    assert warned >= 6


# ---------- ⑦ 工具轮上限 ----------

def test_max_tool_rounds_force_final(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT,
                      rounds=[tool_round(("c", "bash", '{"command": "dir"}'))] * 10,
                      max_tool_rounds=3)
    result = _run(h)
    assert result.startswith("Max tool rounds reached (3)")
    assert len(h.registry.executed) == 3


# ---------- ⑦' 总轮数上限（守卫在工具批后触发；纯文本轮走出口路径） ----------

def test_max_total_rounds_force_final(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT,
                      rounds=[tool_round(("c", "bash", '{"command": "dir"}'))] * 10,
                      max_total_rounds=5, max_tool_rounds=200)
    result = _run(h)
    assert result.startswith("Max total rounds reached (5)")


# ---------- ⑮ [CONCLUDED] 提前收尾 ----------

def test_concluded_tool_ends_loop(tmp_cwd):
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[
        tool_round(("c1", "ask_user_question", "{}")),
    ], outputs={"ask_user_question": "[CONCLUDED] question sent, turn ended"})
    result = _run(h)
    assert result.startswith("[CONCLUDED]")


# ---------- spill 与协议双行 ----------

def test_tool_protocol_lines_and_spill(tmp_cwd):
    huge = "x" * 5000
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[
        tool_round(("c1", "grep", '{"pattern": "x"}'),
                   ("c2", "read_file", '{"path": "a"}')),
        text_round("done"),
    ], outputs={"grep": huge, "read_file": huge})
    _run(h)
    assert "[tool] grep " + json.dumps({"pattern": "x"}, ensure_ascii=False) in h.writer.lines
    assert any(l.startswith("[tool-result] success") for l in h.writer.lines)
    # grep 超阈值 spill（预览=前1200+后1200，全文 5000 不在）；read_file 豁免原样
    spilled = [l for l in h.writer.lines if "[spilled]" in l]
    assert spilled and "x" * 1500 not in spilled[0]
    assert any(l.startswith("[tool-result]") and huge[:50] in l
               for l in h.writer.lines)  # read_file 结果完整内联


# ---------- ⑩ 插话队列 defer ----------

def test_interjection_deferred(tmp_cwd):
    (tmp_cwd / ".chat").mkdir()
    (tmp_cwd / ".chat" / "pending.jsonl").write_text(
        json.dumps({"role": "user", "content": "插话A"}) + "\n", encoding="utf-8")
    h = EngineHarness(tmp_cwd, Mode.CHAT,
                      rounds=[text_round("ok"), text_round("ok2")],
                      defer_drain=True)  # daemon 模式：daemon 消费，不中途注入
    _run(h)
    flat = [str(getattr(m, "content", "")) for m in h.client.calls[0]]
    assert not any("插话A" in c for c in flat)


def test_interjection_injected_when_not_deferred(tmp_cwd):
    (tmp_cwd / ".chat").mkdir()
    (tmp_cwd / ".chat" / "pending.jsonl").write_text(
        json.dumps({"role": "user", "content": "插话A"}) + "\n", encoding="utf-8")
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[text_round("ok")])
    _run(h)
    flat = [str(getattr(m, "content", "")) for m in h.client.calls[0]]
    assert any("[用户追加的排队消息] 插话A" in c for c in flat)


# ---------- ⑧ 写前预算二振 → 最小骨架 ----------

def test_pre_write_budget_skeleton(tmp_cwd):
    # T.java/dist 必须晚于守卫出现（预置自写 Java 会让 existing_java=True
    # 直接跳过写前守卫——旧实现同样如此），在 gametest 执行时才落盘。
    class WritingRegistry(FakeRegistry):
        def execute(self, name, args):
            if name == "run_test_gametest":
                p = tmp_cwd / "src" / "test" / "java"
                p.mkdir(parents=True, exist_ok=True)
                (p / "T.java").write_text("@GameTest", encoding="utf-8")
                d = tmp_cwd / "dist"
                d.mkdir(exist_ok=True)
                (d / "mymod.jar").write_bytes(b"jar")
            return super().execute(name, args)

    h = EngineHarness(tmp_cwd, Mode.MOD, rounds=[
        tool_round(*[("c%d" % i, "read_file", '{"path": "s%d"}' % i) for i in range(6)]),
        tool_round(("d1", "read_file", '{"path": "t"}')),   # 一振软提醒后再超
        tool_round(("e1", "run_test_gametest", "{}")),      # 跑测试（出口闸证据）
        text_round("骨架已就位，完成"),
    ], outputs={"run_test_gametest": "All required tests passed"})
    h.registry.__class__ = WritingRegistry  # 换成会落盘测试文件的注册表
    result = _run(h, prompt="做一个红宝石剑（rubysword），攻击力 7")
    flat = [str(getattr(m, "content", "")) for m in h.client.calls[-1]]
    assert any("<auto-skeleton>" in c for c in flat)
    skeleton = (tmp_cwd / "src" / "main" / "java" / "com" / "rubysword"
                / "RubyswordMod.java")
    assert skeleton.exists()
    assert "getModBusGroup()" in skeleton.read_text(encoding="utf-8")
    assert result == "骨架已就位，完成"


# ---------- ⑬ compact 延后执行 ----------

def test_deferred_compact_guard(tmp_cwd):
    """compact 工具延后到守卫统一执行：批内不进 registry、事件源记 compaction。

    注：小上下文下 auto_compact 会因"压缩区间为空"拒绝实际压缩
    （与旧实现一致）；守卫路径本身由此测试覆盖，压缩算法见下个用例。
    """
    h = EngineHarness(tmp_cwd, Mode.CHAT, rounds=[
        tool_round(("c1", "compact", "{}"), ("c2", "read_file", '{"path": "x"}')),
        text_round("ok"),
    ])
    _run(h)
    assert ("compact", {}) not in h.registry.executed  # 不经批执行
    assert ("read_file", {"path": "x"}) in h.registry.executed
    assert any(e.type == "compaction" for e in h.log.events)  # 守卫已记账


def test_compaction_service_small_window():
    """直测压缩服务：小窗口下选界→摘要→替换（锚点+checkpoint+尾部）全链路。"""
    from core.infrastructure.config import ModelSettings
    from core.services.compaction import CompactionService

    client = FakeModelClient([], complete_replies=["S"])
    svc = CompactionService(client, lambda: "sys",
                            ModelSettings(context_window=3000))  # retain=480 tok
    msgs = [UserMessage(content="任务锚点：做 MOD")] + [
        UserMessage(content=f"历史轮次 {i}：" + "内容" * 300) for i in range(8)
    ] + [UserMessage(content="最近的尾部消息")]
    out, text = svc.handle_compact(msgs)
    assert text == "Context compacted successfully."
    assert len(out) < len(msgs)
    joined = [m.content for m in out]
    assert any("[Context compacted" in c for c in joined)
    assert any("Continue from where we left off" in c for c in joined)
    assert any(c == "任务锚点：做 MOD" for c in joined)  # 短锚点保留
    assert out[-1].content == "最近的尾部消息"  # 尾部原样保留


# ---------- ⑯ 队友 working 阻止退出 ----------

def test_teammates_working_blocks_exit(tmp_cwd):
    class WorkingTeammates:
        def read_leader_inbox(self):
            return []

        def working_names(self):
            return ["alice"]

    h = EngineHarness(tmp_cwd, Mode.CHAT,
                      rounds=[text_round("想收尾")], max_total_rounds=50,
                      max_tool_rounds=200)
    h.engine._deps.teammates = WorkingTeammates()  # LoopDeps 非冻结，可换端口
    # 队友一直 working：文本轮被打回、工具轮被上限兜底
    h.client.rounds = [text_round("想收尾"), tool_round(("c", "bash", "{}"))]
    result = _run(h)
    assert "想收尾" not in result  # 从未自然退出
    assert result.startswith("Max tool rounds") or result.startswith("Max total rounds")

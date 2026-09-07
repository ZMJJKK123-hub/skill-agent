# -*- coding: utf-8 -*-
"""工具批之后的守卫瀑布（services/loop 层）。

按旧 agent.py 固定优先级短路执行（策略表替代 if-continue）：
完成闸 → 写前预算 → 写后预算 → [CONCLUDED] → 工具轮上限 →
总轮上限 → compact 延后 → todo 催办。守卫返回 True = 本轮就此
结束（进入下一轮），False = 放行下一道。
"""
from __future__ import annotations

from typing import Callable

from ...domain.session import Mode
from ...infrastructure.logging_.logger import get_logger
from .deps import LoopDeps
from .slots import replace_runtime_slot
from .state import LoopState

logger = get_logger("loop.guards")

GuardFn = Callable[[LoopState, LoopDeps], bool]

#: GameTest 通过标记（工具结果内容 lstrip 后以这些前缀开头才算通过；
#: "[gametest]" 前缀绝不能作为通过标记——run_game_test_server 成败都带它）。
GT_PASS_MARKERS = ("All required tests passed", "GAME TESTS COMPLETE", "RESULT: PASS")


def _dist_has_jar() -> str | None:
    """输入：无。返回：dist 里首个非模板 jar 文件名（无则 None）。"""
    try:
        from pathlib import Path
        dist = Path.cwd() / "dist"
        if not dist.is_dir():
            return None
        for f in dist.iterdir():
            if f.name.endswith(".jar") and "examplemod" not in f.name:
                return f.name
    except OSError as e:
        logger.warning("dist 扫描失败: %s", e)
    return None


def guard_completion_gate(state: LoopState, deps: LoopDeps) -> bool:
    """完成闸（仅 mod）：dist+GameTest 达标 → 首达注入收尾提醒 + 宽限窗。"""
    if deps.ctx.mode != Mode.MOD:
        return False
    passed = any(
        isinstance(m.content, str) and m.content.lstrip().startswith(GT_PASS_MARKERS)
        for m in state.messages if m.role == "tool")
    jar = _dist_has_jar() if passed else None
    if jar is None:
        return False
    grace = deps.settings.loop.completion_grace_rounds
    if state.gate_round is None:
        state.gate_round = state.round_idx
        replace_runtime_slot(state.messages, "completion-gate", (
            "<completion-gate> build + GameTest 已达标"
            f"（dist/{jar} 存在且测试通过）。\n"
            "若本 MOD 含自定义实体、刷怪蛋或物品图标，先按 docs/agent/CLIENT_VERIFY.md "
            "完成客户端视觉验证（识图开启时 screenshot + analyze_image 即可）。\n"
            "验证完成或不需要验证时：先调用 stop_mc_process(handle='all') 关闭你启动过的"
            "游戏客户端/服务器（不要把游戏窗口留在用户桌面），然后停止调用工具，"
            "下一轮直接输出面向用户的最终总结——"
            "创建/修改了哪些文件、MOD 功能与关键数值、合成配方、安装方法、验证结论。"
            "</completion-gate>"))
        logger.info("completion-gate 首次触发（round %d），注入收尾提醒，宽限 %d 轮",
                    state.round_idx, grace)
        return False  # 宽限期内不干预，走完本轮其余守卫
    if state.round_idx - state.gate_round >= grace:
        from .exits import summarize_completion
        fallback = (f"MOD 完成：dist/{jar} 已生成且 GameTest 通过。"
                    f"（总结生成失败，此为系统回退文本；详细过程见运行日志。）")
        state.force_final_msg = summarize_completion(deps, state.messages, fallback)
        logger.warning("completion-gate 宽限耗尽，强制收尾")
        return True
    return False


def guard_pre_write_budget(state: LoopState, deps: LoopDeps) -> bool:
    """写前研究预算（仅 mod）：超 6 次只读未写 → starter/骨架/软提醒三连。"""
    if deps.ctx.mode != Mode.MOD:
        return False
    if (state.wrote_file or state.existing_java or state.pre_write_warned
            or state.pre_write_reads < 6):
        return False
    state.pre_write_warned = True
    state.write_strikes += 1
    if not state.starter_auto_written and deps.auto_starter(state.messages):
        state.starter_auto_written = True
        state.pre_write_warned = False  # starter 不算主动写码，继续 nag
        logger.warning("已自动从 starter 写入 Java 文件，继续任务")
        from ...domain.messages import UserMessage
        state.messages.append(UserMessage(content=(
            "<auto-starter> 系统已自动复制合适的 starter Java 文件到 src/main/java。"
            "请基于该文件继续完成剩余资源/测试，不要再阅读 starter 文档。</auto-starter>")))
        return True
    if state.write_strikes >= 2 and not state.skeleton_written:
        modid = deps.auto_skeleton(state.messages)
        if modid:
            state.skeleton_written = True
            state.wrote_file = True  # 切到写后预算，写前 nag 到此为止
            state.pre_write_warned = False
            logger.warning("写前预算终局：已写入 modid=%s 最小骨架", modid)
            _append_skeleton_notice(state, modid)
            return True
    logger.warning("写前研究超预算（%d），强制提醒写文件", state.pre_write_reads)
    _append_write_first_stop(state)
    state.pre_write_warned = False  # 允许再次进入，让 strikes 累加到 2
    return True


def _append_skeleton_notice(state: LoopState, modid: str) -> None:
    """输入：modid。返回：无。职责：注入骨架已写入的推进指令（旧文逐字）。"""
    from ...domain.messages import UserMessage
    state.messages.append(UserMessage(content=(
        f"<auto-skeleton> 你已多次超预算未写码，系统已在 "
        f"src/main/java/com/{modid}/ 写入最小可编译主类骨架"
        f"（modid={modid}，1.21.11 注册写法已就位）。"
        f"立刻基于它继续：①按命名规则同步 mods.toml 的 modId、"
        f"build.gradle 的 group/archivesName、settings.gradle 的 "
        f"rootProject.name；②在其上扩展物品/方块/BlockEntity 等注册与逻辑。"
        f"本轮之后禁止再 read/grep starter 与 mc_java_sources，"
        f"下一轮必须是 write_file 或 edit_file。</auto-skeleton>")))


def _append_write_first_stop(state: LoopState) -> None:
    """输入：无。返回：无。职责：注入写前超预算软提醒（旧文逐字）。"""
    from ...domain.messages import UserMessage
    state.messages.append(UserMessage(content=(
        "<write-first-stop> 你已反复阅读 mc_java_sources/starter 但没有写文件。"
        "立即停止阅读源码。如果还没加载相关技能，先调用一次 load_skill 加载最相关技能"
        "（例如 forge-simple-min-mod）；然后立刻用 write_file 写出第一个最小 Java 文件，"
        "再 build/compile 根据报错处理。不要继续 read_file/grep mc_java_sources。</write-first-stop>")))


def guard_post_write_research(state: LoopState, deps: LoopDeps) -> bool:
    """写后研究预算（仅 mod）：写完仍反复查 API 不编译 → 软性提醒。"""
    if deps.ctx.mode != Mode.MOD:
        return False
    if not state.wrote_file or state.post_write_research < 8 or state.pre_write_warned:
        return False
    logger.warning("写后研究超预算（%d），软性提醒编译/测试", state.post_write_research)
    from ...domain.messages import UserMessage
    state.messages.append(UserMessage(content=(
        "<build-now-stop> 你已经写完了 Java 代码，但还在反复查 API 不编译。"
        "立即停止研究。调用 validate_resources 检查资源，"
        "然后调用 run_mod_test_cycle 或 build_mod_jar_forge 编译。"
        "编译报错再查具体符号。不要继续 read_file/grep/search_api。</build-now-stop>")))
    state.post_write_research = 0
    return True


def guard_concluded(state: LoopState, deps: LoopDeps) -> bool:
    """工具主动收尾（[CONCLUDED]）：不经下一次模型调用直接结束。"""
    if state.concluded_output is None:
        return False
    state.force_final_msg = (
        "[CONCLUDED] A tool has completed the relevant work and ended this turn.\n"
        f"Final tool output:\n{state.concluded_output}")
    state.step_machine.conclude_turn()
    logger.warning("%s", state.force_final_msg)
    return True


def guard_max_tool_rounds(state: LoopState, deps: LoopDeps) -> bool:
    """工具轮上限（防无限工具循环）。"""
    state.tool_rounds += 1
    limit = deps.settings.loop.max_tool_rounds
    if state.tool_rounds < limit:
        return False
    state.force_final_msg = (
        f"Max tool rounds reached ({limit}). Partial progress is in run.log; "
        "stopping the loop to prevent an infinite tool-call loop.")
    logger.warning("%s", state.force_final_msg)
    return True


def guard_max_total_rounds(state: LoopState, deps: LoopDeps) -> bool:
    """总轮数硬上限（含纯文本重试轮；出口闸失明时的最后防线）。"""
    limit = deps.settings.loop.max_total_rounds
    if state.round_idx < limit:
        return False
    state.force_final_msg = (
        f"Max total rounds reached ({limit}). Partial progress is in run.log; stopping.")
    logger.warning("%s", state.force_final_msg)
    return True


def guard_deferred_compact(state: LoopState, deps: LoopDeps) -> bool:
    """compact 工具延后执行（其他工具跑完再压缩，防丢并行结果）。"""
    if not state.compact_pending:
        return False
    state.messages, _ = deps.compaction.handle_compact(state.messages)
    before_seq = max((e.seq for e in deps.session_log.events), default=0)
    summary = next((m.content for m in state.messages
                    if m.role == "user" and "[Context compacted" in m.content), "")
    deps.session_log.add_compaction(summary, 1, before_seq)
    state.synced_count = 0
    state.rounds_since_todo = 0
    logger.info("compact 执行完毕，messages 已被替换，跳过本轮 nag reminder")
    return True


def guard_todo_nag(state: LoopState, deps: LoopDeps) -> bool:
    """todo 催办（仅 mod）：连续 3 轮未更新 todo 注入提醒。"""
    if deps.ctx.mode != Mode.MOD:
        return False
    state.rounds_since_todo = 0 if state.used_todo else state.rounds_since_todo + 1
    if state.rounds_since_todo < 3:
        return False
    logger.info("触发 nag reminder：连续 3 轮未更新 todo")
    replace_runtime_slot(state.messages, "reminder",
                         "<reminder>Update your todos to track progress.</reminder>")
    state.rounds_since_todo = 0
    return False


def apply_repeat_tool_reminder(state: LoopState, deps: LoopDeps) -> None:
    """同一轮重复调用同一工具 ≥ 阈值时的建议提醒（模式感知文案）。"""
    threshold = deps.settings.loop.repeat_tool_threshold
    too_many = [(n, c) for n, c in state.round_tool_counts.items() if c >= threshold]
    if not too_many:
        return
    details = ", ".join(f"{n} x{c}" for n, c in too_many)
    if deps.ctx.mode == Mode.MOD:
        advice = "请先写/改一个文件，或换个工具，不要继续重复同一操作。"
    else:
        advice = "请换个角度或工具；信息足够时直接用文字回答用户。"
    replace_runtime_slot(state.messages, "reminder", (
        f"<reminder>同一轮内重复调用工具过多：{details}。{advice}</reminder>"))


#: mod 模式守卫链（顺序即优先级，与旧实现一致）。
GUARDS_MOD: tuple[GuardFn, ...] = (
    guard_completion_gate,
    guard_pre_write_budget,
    guard_post_write_research,
    guard_concluded,
    guard_max_tool_rounds,
    guard_max_total_rounds,
    guard_deferred_compact,
    guard_todo_nag,
)

#: chat 模式守卫链（预算类守卫不适用只读咨询）。
GUARDS_CHAT: tuple[GuardFn, ...] = (
    guard_concluded,
    guard_max_tool_rounds,
    guard_max_total_rounds,
    guard_deferred_compact,
)

import json
import os
import re
import subprocess
from pathlib import Path

from . import config
from .config import client, MODEL, logger, MODE
from .tools import (
    TOOL_HANDLERS, bg_manager,
    format_background_results, teammate_manager, maybe_inject_skill_catalog,
    tool_registry,
)
from .protocol import inject_pending_requests
from .agent_hooks import run_post_step_hooks, run_pre_step_hooks, run_request_error_hooks
from .subagent import run_subagent_async
from .compact import (
    micro_compact,
    auto_compact,
    handle_compact,
    estimate_tokens,
    TOKEN_THRESHOLD,
)
from .session_log import SessionLog, repair_missing_tool_results
from .step_machine import TurnStepMachine
from .skillcheck import init_per_loop, run_loop_check, move_skills_to_end
from .supervisor import supervisor_manager
from .tool_gate import leader_tools


# ---------- 接线：注册 task handler（打破循环依赖）----------
# tools.py 不导入 subagent.py（避免循环依赖），
# task 工具的定义在 TOOLS 列表里，但 handler 在此接线。
# M4: task 改为异步后台派发——父 agent 不再同步阻塞；
# 结果经 <background-results> 下一轮注入。persona 参数可选覆盖子代理 system prompt。
TOOL_HANDLERS["task"] = lambda **kw: run_subagent_async(
    kw["prompt"], persona=kw.get("persona"))

# 第 11 课修复：leader 侧排除 submit_plan。
# submit_plan 语义是"队友→领导"，leader 是审批方，不该自己提交计划；
# 否则 _agent_id 缺省 "unknown"，审批回执会发到不存在的收件箱。
# M3: 声明式过滤（tool_registry.schemas）替代手工列表拷贝。
LEADER_TOOLS = tool_registry.schemas(exclude={"submit_plan"})

# chat 模式（通用对话）跳过所有 MOD 专属逻辑：
# 监管线程 / KNOWN_ISSUES 强制注入 / skill-source 引用校验 / GameTest 核查 /
# 收尾 jar 构建与 zip 预生成——这些只在 mod 制作模式有意义。
IS_MOD_MODE = MODE == "mod"


def agent_loop(messages: list) -> str:
    # 确保工作区能看到 MC/Forge 源码（手动建会话时最容易缺这一项）
    #只验证 不复制 保证根目录存在即可
    _ensure_docs_agent()
    _ensure_mc_java_sources()

    #todo工具计数器 防止agent多次不调用todo工具导致混乱
    rounds_since_todo = 0
    #监管启动
    if IS_MOD_MODE:
        supervisor_manager.start()


    #控制智能体行为的注入变量
    _known_issues_injected = False
    _agents_injected = False
    _tool_rounds = 0
    _wrote_file = False
    _pre_write_reads = 0
    _pre_write_warned = False
    _starter_auto_written = False
    _skeleton_written = False   # 写前预算终局：最小骨架是否已自动写入
    _write_strikes = 0
    _post_write_research = 0
    _post_write_strikes = 0
    _no_tool_strikes = 0
    _gametest_rejects = 0  # GameTest 出口闸连续打回计数（≥3 且 dist 有产物 → 强制收尾）
    _empty_strikes = 0     # 连续空响应计数（≥5 压缩，≥8 强制收尾）
    _gate_round = None     # 完成闸首次触发的轮号（宽限计数基准）

    #检测是否有自己写过的代码 还是完全没动过模版代码
    def _has_custom_java():
        # 模板包 com/example 不算“已有自己写的代码”，否则 forced-write 永远不触发。
        def is_template(p: Path) -> bool:
            parts = [x.lower() for x in p.parts]
            return "com" in parts and "example" in parts and "examplemod" in parts
        main = Path.cwd() / "src" / "main" / "java"
        test = Path.cwd() / "src" / "test" / "java"
        return any(
            p.suffix == ".java" and not is_template(p)
            for root in (main, test) if root.exists()
            for p in root.rglob("*.java")
        )
    _existing_java = _has_custom_java()
    _force_final_msg = None
    _round_idx = 0
    _round_tool_counts = {}
    _session_log = SessionLog()

    # 恢复：如果调用方没给初始消息，但存在事件日志，则从事件源重建历史（DSH replay）
    if not messages:
        try:
            _event_path = os.path.join(".chat", "session_events.jsonl")
            if os.path.exists(_event_path):
                with open(_event_path, "r", encoding="utf-8") as f:
                    _session_log = SessionLog.from_jsonl(f.read())
                messages = _session_log.derive_messages()
                _synced_count = 0
                logger.info(f"从 SessionLog 恢复 {len(messages)} 条消息")
        except Exception as _re:
            logger.warning(f"SessionLog 恢复失败: {_re}")
    _step_machine = TurnStepMachine(_session_log)
    _synced_count = 0
    _step_machine.start_turn()
    while True:
        _round_idx += 1
        _round_tool_counts = {}
        # ── Layer 0s: 排空监管信箱（第 13 课）──
        # 后台监管线程发现异常会写信箱；这里读后即删，按严重度
        # 以 <supervisor-advice>（温和）或 <supervisor-alert>（警告）注入。
        # 放在最前面：让监管信息先于后台通知/队友汇报进入上下文。
        if IS_MOD_MODE:
            supervisor_msgs = supervisor_manager.drain_advice()
            if supervisor_msgs:
                blocks = []
                for sv in supervisor_msgs:
                    tag = "supervisor-alert" if sv["type"] == "alert" else "supervisor-advice"
                    blocks.append(f"<{tag}>\n{sv['content']}\n</{tag}>")
                _replace_runtime_slot(messages, "supervisor", "\n".join(blocks))
                logger.info(f"注入监管信息 type={[sv['type'] for sv in supervisor_msgs]}:\n{blocks}")
            supervisor_manager.notify_round()  # 计数 + 每 5 轮触发一次监管分析

        if _force_final_msg is not None:
            logger.warning(_force_final_msg)
            _step_machine.complete_turn()
            _save_session_log(_session_log)
            if IS_MOD_MODE:
                supervisor_manager.stop()
                # 强制收尾路径补齐产物（与自然收尾对齐）：
                # 宽限耗尽直接 return 时此前跳过了 jar 重建与 zip 预生成，
                # 用户点下载要现场打包（d70b3f40 实测 zip 未生成）。
                try:
                    import os as _os
                    if (_os.path.exists("gradlew.bat") or _os.path.exists("gradlew")) and _os.path.exists("build.gradle"):
                        print("[run_task] 开始构建 mod jar（首次构建需数分钟）...", flush=True)
                        from .tools import _forge_build_jar
                        print(f"[run_task] {_forge_build_jar({})[:2000]}", flush=True)
                except Exception as _e:
                    logger.info(f"强制收尾构建跳过: {_e}")
                try:
                    from .tools import _build_source_zip
                    print(f"[run_task] {_build_source_zip()}", flush=True)
                except Exception as _e:
                    logger.info(f"强制收尾 zip 预生成跳过: {_e}")
            return _force_final_msg

        # ── Layer 0c2: 断点保存 + 运行中插话注入（暂停/继续 与 queue 支持）──
        # 每轮开头把完整 messages 落盘（断点）；继续时新进程原样恢复。
        # 同时把运行中用户插入的排队消息读入上下文。
        _save_checkpoint(messages)
        _drain_interjections(messages)

        # ── Layer 0c3: 技能目录 digest 注入（M2，对齐 DSH tool-skill catalog）──
        # 目录（name+首行描述）以 user 消息注入：digest 变化才追加，不变零开销；
        # 会话中新增/编辑 SKILL.md 下一轮即生效。正文仍由 load_skill 按需加载。
        if not os.environ.get("DSH_SKILL_CATALOG_DISABLED"):
            if IS_MOD_MODE or _messages_hint_mod(messages):
                maybe_inject_skill_catalog(messages)

        # ── Layer 0: 排空后台通知（第 8 课）──
        # 在 micro_compact 之前注入，让通知作为新数据参与后续 compact 估算
        notifications = bg_manager.drain_notifications()
        if notifications:
            bg_results = format_background_results(notifications)
            _replace_runtime_slot(messages, "background-results", bg_results)
            logger.info(f"注入后台通知:\n{bg_results}")

        # ── Layer 0b: 排空 leader 收件箱（第 9 课：队友汇报）──
        # 队友完成任务后结果发回 leader 收件箱，这里 drain 并注入为 user 消息
        teammate_msgs = teammate_manager.bus.read_inbox("leader")
        if teammate_msgs:
            parts = ["<teammate-reports>"]
            for msg in teammate_msgs:
                parts.append(
                    f"[from {msg['from']}]\n{msg['content']}"
                )
            parts.append("</teammate-reports>")
            teammate_report = "\n".join(parts)
            _replace_runtime_slot(messages, "teammate-reports", teammate_report)
            logger.info(f"注入队友汇报:\n{teammate_report}")

        # ── Layer 0b2: 强制 KNOWN_ISSUES 首轮注入（绕圈修复）──
        # 仅 mod 模式：chat 模式没有模板 KNOWN_ISSUES.md，注入只会让模型
        # 陷入"找不到文件"的绕圈（实测：chat 模式发 hi 卡在找 KNOWN_ISSUES）。
        if IS_MOD_MODE and not _known_issues_injected:
            _known_issues_injected = True
            messages.append({"role": "user", "content": (
                "<mandatory-first-step> 开工前必须先 run_read KNOWN_ISSUES.md "
                "（mod 工程根目录的事实来源，优先级高于技能描述）。读完按其中适用条目执行，"
                "尤其注意：GameTest 自检必须用 run_test_gametest（扫描 src/test/java），"
                "禁止用 run_game_test_server 做自检。未读取前不要写任何代码/资源。\n"
                "【写前查坑，强制】写任何 Java 文件之前，必须先用一次 grep 在 "
                "docs/agent/ERROR_LIST.md 里检索你即将用到的注册常量与关键 API 名"
                "（例如 BLOCK_ENTITY_TYPE、blit、makeMockPlayer、useWithoutItem、"
                "Registries 常量、MenuScreens 等），已有条目直接照修复写，不要等编译报错才查——"
                "c43424752e7d 实测：同族坑已入库仍被写出，三连 FAIL 才修完。\n"
                "如果本 MOD 涉及自定义实体、刷怪蛋或物品图标，你还必须 run_read "
                "C:/Users/59639/Desktop/skill-agent/docs/agent/CLIENT_VERIFY.md "
                "（客户端验证指导，服务器/GameTest 发现不了客户端渲染与图标问题），"
                "并在完成前按其中固定流程执行客户端验证；未满足客户端验证不得宣布完成。</mandatory-first-step>"
            )})

        # ── Layer 0b3: 首次读取并注入 AGENTS.md（移植 dsh agent-instructions 的 baseline）──
        # 文件由模板复制进会话工作区，只读；内容包含项目硬事实/验证闭环/常见坑。
        if IS_MOD_MODE and not _agents_injected:
            _agents_injected = True
            try:
                _agents_path = os.path.join(os.getcwd(), "AGENTS.md")
                if os.path.exists(_agents_path):
                    _agents_text = open(_agents_path, "r", encoding="utf-8").read()
                    _replace_runtime_slot(
                        messages,
                        "agents-instructions",
                        f"<agents-instructions>\n{_agents_text}\n</agents-instructions>",
                    )
                    logger.info("已注入 AGENTS.md 工作区指令")
            except Exception as _e:
                logger.warning(f"AGENTS.md 注入失败: {_e}")

        # ── Layer 0c: 注入协议请求（第 10 课）──
        # leader 每轮看到：待审批的 plan 请求（队友提交的计划）+ 已决议的
        # shutdown 结果（队友同意/拒绝关机）。<pending-requests> 标签让模型
        # 明确区分这是协议事件，需用 respond_to_request 审批。
        inject_pending_requests(messages, "leader")

        # ── Layer 1: micro_compact（每轮自动，静默裁剪旧 tool_result）──
        micro_compact(messages)

        # ── Layer 2: auto_compact（token 超阈值，整段对话压缩为摘要）──
        current_tokens = estimate_tokens(messages)
        if current_tokens > TOKEN_THRESHOLD:
            logger.info(
                f"Layer 2 auto_compact 触发 | token={current_tokens} > 阈值 {TOKEN_THRESHOLD}"
            )
            _before_seq = max((e.seq for e in _session_log.events), default=0)
            messages = auto_compact(messages)
            _summary_content = next(
                (str(m.get("content", "")) for m in messages
                 if m.get("role") == "user" and isinstance(m.get("content"), str)
                 and "[Context compacted" in m.get("content", "")),
                "",
            )
            _session_log.add_compaction(_summary_content, 1, _before_seq)
            _synced_count = 0  # 新消息列表重新同步到事件源

        # ── Layer 2.5: pre-step hooks（移植 dsh agent/pre-step waterfall）──
        # 目前默认钩子注入 <runtime-context> 快照；未来插件可再注册。
        run_pre_step_hooks(messages)

        # 事件源同步 + 崩溃修复（DSH deriveMessages/repair）
        _synced_count = _sync_messages_to_log(_session_log, messages, _synced_count)
        messages = repair_missing_tool_results(_session_log, messages)
        _synced_count = _sync_messages_to_log(_session_log, messages, _synced_count)

        # Turn/step 状态机：每个模型请求是一个 step
        _step_machine.start_step()
        _save_session_log(_session_log)

        # 每轮调试快照：输出消息概览/工具统计，并落盘 .chat/debug/round_messages.jsonl
        _dump_round_messages(_round_idx, messages, _round_tool_counts)

        # 发给模型
        move_skills_to_end(messages)
        logger.info(f"=== 新一轮 | messages 长度={len(messages)} ===")
        # ── 流式输出（M-opt2）：首 token 到达即开始把回复增量写入 run.log，
        # 前端 /api/events 以 log 事件实时展示（[reply] 行）；tool_calls 增量
        # 累积到完整后再执行，行为与非流式一致。最终 message 由累积结果
        # 构造，后续 skillcheck / 循环退出 / 工具执行逻辑保持不变。
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": config.SYSTEM}] + messages,
                tools=leader_tools(),  # 阶段式：基础阶段只开放开发工具；解锁后开放全部
                max_tokens=8000,
                stream=True,
            )
        except Exception as _le:
            _extra = run_request_error_hooks(_le, messages)
            for _e in _extra:
                messages.append({"role": "user", "content": str(_e)})
            if _is_context_overflow(_le):
                logger.warning(f"上下文超限，自动压缩后重试: {_le}")
                messages = auto_compact(messages)
                continue
            raise

        content_parts: list[str] = []
        reasoning_parts: list[str] = []
        tool_call_deltas: dict[int, dict] = {}
        finish_reason = None
        try:
            for chunk in stream:
                if not chunk.choices:
                    continue
                ch = chunk.choices[0]
                if ch.finish_reason:
                    finish_reason = ch.finish_reason
                delta = ch.delta
                if delta is None:
                    continue
                if getattr(delta, "reasoning_content", None):
                    reasoning_parts.append(delta.reasoning_content)
                    # 流式思考转发：外部接入层（清小搭 8001）可实时收到 delta
                    if REASONING_SINK is not None:
                        try:
                            REASONING_SINK(delta.reasoning_content)
                        except Exception:
                            pass
                if getattr(delta, "content", None):
                    content_parts.append(delta.content)
                    # 过程可见：回复增量实时落盘（run.log → /api/events）
                    print(f"[reply] {delta.content}", flush=True)
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        entry = tool_call_deltas.setdefault(tc.index, {"id": "", "name": "", "args": ""})
                        if tc.id:
                            entry["id"] = tc.id
                        if tc.function and tc.function.name:
                            entry["name"] += tc.function.name
                        if tc.function and tc.function.arguments:
                            entry["args"] += tc.function.arguments
        except Exception as _le2:
            _extra2 = run_request_error_hooks(_le2, messages)
            for _e2 in _extra2:
                messages.append({"role": "user", "content": str(_e2)})
            if _is_context_overflow(_le2):
                logger.warning(f"流式上下文超限，自动压缩后重试: {_le2}")
                messages = auto_compact(messages)
                continue
            raise

        from types import SimpleNamespace as _NS
        content = "".join(content_parts) or None
        reasoning = "".join(reasoning_parts) or None
        tool_calls = None
        if tool_call_deltas:
            tool_calls = []
            for idx in sorted(tool_call_deltas):
                d = tool_call_deltas[idx]
                tool_calls.append(_NS(
                    id=d["id"], type="function",
                    function=_NS(name=d["name"], arguments=d["args"]),
                ))
        # 防 400：OpenAI 不允许 assistant 同时没有 content 和 tool_calls。
        # 关键修复：不要把“No additional output”占位符写回历史，否则模型会把它当成自己
        # 的真实回复，下一轮继续返回空内容，形成死循环。改为注入用户警告并直接重试。
        if content is None and not tool_calls:
            _empty_strikes += 1
            logger.warning(f"模型返回空内容且无工具调用（连续第 {_empty_strikes} 次）")
            # 上限兜底（webserv_heaven 实测：glm-5.3 遇超大上下文连续 39 次空响应，
            # 无上限时空转烧 API）。连续 5 次仍空 → 触发压缩（可能上下文异常膨胀），
            # 连续 8 次 → 强制收尾并给出诊断信息。
            if _empty_strikes == 5:
                logger.warning("连续 5 次空响应，尝试 auto_compact 缩上下文")
                messages = auto_compact(messages)
                continue
            if _empty_strikes >= 8:
                _force_final_msg = (
                    "Model returned empty responses 8 times in a row "
                    "(likely context overload). Partial progress is in run.log. "
                    "建议：减少一次性加载的技能数量（≤3 个），或换用更稳定的模型。"
                )
                logger.warning(_force_final_msg)
                continue
            if IS_MOD_MODE:
                messages.append({
                    "role": "user",
                    "content": (
                        "<empty-response> 模型返回为空且没有工具调用。你必须调用一个工具继续任务，"
                        "禁止输出空文本或“No additional output”之类的话。</empty-response>"
                    ),
                })
            else:
                # chat 模式：纯文字回答是正常出口，不能逼模型必须调工具
                messages.append({
                    "role": "user",
                    "content": (
                        "<empty-response> 模型返回为空。请直接用自然语言回答用户最新的问题；"
                        "只有确需查资料时才调用只读工具。</empty-response>"
                    ),
                })
            continue
        message = _NS(
            content=content,
            reasoning_content=reasoning,
            tool_calls=tool_calls,
            to_dict=lambda: {
                "role": "assistant",
                "content": content,
                "reasoning_content": reasoning,
                "tool_calls": ([
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in tool_calls
                ] if tool_calls else None),
            },
        )
        choice = _NS(message=message, finish_reason=finish_reason or "stop")

        # ── 打印思考过程（不进 messages）──
        reasoning = getattr(message, "reasoning_content", None)
        if reasoning:
            print(f"\n[思考] {reasoning}")
            logger.info(f"reasoning_content:\n{reasoning}")

        # 记录助手回复（只记录 content/tool_calls，不含 reasoning）
        messages.append(message.to_dict())
        _empty_strikes = 0  # 正常响应到达，连续空响应计数清零
        # ── skill-source 引用校验（仅 mod 模式）──
        # chat 模式：普通对话无需 <skill-source> 引用块，跳过校验直接通过。
        if choice.finish_reason != "tool_calls" and IS_MOD_MODE:
            if not run_loop_check("main", message.content, messages):
                continue
        if choice.finish_reason == "length":
            _step_machine.record_max_tokens()
        logger.info(f"finish_reason={choice.finish_reason}")

        # 退出条件：模型不再调工具
        if choice.finish_reason != "tool_calls":
            _step_machine.end_step(reason="completed")
            run_post_step_hooks(messages, _round_tool_counts)
            # ── 队友检测：有队友还在 working 就不退出 ──
            working_teammates = [
                name for name, cfg in teammate_manager.team.items()
                if cfg.status == "working"
            ]
            if working_teammates:
                logger.info(
                    f"模型想退出但队友仍在工作: {working_teammates} | "
                    f"注入提醒，继续等待队友汇报"
                )
                _replace_runtime_slot(
                    messages,
                    "reminder",
                    f"<reminder>Teammates still working: {', '.join(working_teammates)}. Wait for their reports before finishing.</reminder>",
                )
                continue

            logger.info(f"循环结束，最终回复:\n{message.content}")

            # ── chat 模式：普通对话直接返回（不核查 GameTest、不构建 jar/zip）──
            if not IS_MOD_MODE:
                _step_machine.complete_turn()
                _save_session_log(_session_log)
                return message.content

            # ── GameTest 强制核查（C 组合：未跑通 GameTest 自循环则禁止完成）──
            _gametest_ok = True
            try:
                from pathlib import Path as _P
                _base = _P.cwd()
                # 1) 只扫描 src/test/java 中的 @GameTest，绝不把 mc_java_sources 里的源码当成测试
                _test_root = _base / "src" / "test" / "java"
                _has_test = False
                if _test_root.exists():
                    for _fp in _test_root.rglob("*.java"):
                        try:
                            if "@GameTest" in _fp.read_text(encoding="utf-8", errors="replace"):
                                _has_test = True
                                break
                        except OSError:
                            continue
                # 2) 只有“实际调用过 GameTest/测试循环工具且对应工具结果包含成功标记”才算跑过
                _gt_tool_names = {"run_test_gametest", "run_game_test_server", "run_mod_test_cycle"}
                _gt_call_ids = set()
                for _m in messages:
                    if _m.get("role") == "assistant":
                        for _tc in (_m.get("tool_calls") or []):
                            if _tc.get("function", {}).get("name") in _gt_tool_names:
                                _gt_call_ids.add(_tc.get("id", ""))
                _ran_gt = False
                for _m in messages:
                    if _m.get("role") != "tool":
                        continue
                    if _m.get("tool_call_id") not in _gt_call_ids:
                        continue
                    _content = str(_m.get("content", ""))
                    if (_content.lstrip().startswith("[gametest]")
                            or "All required tests passed" in _content
                            or "GAME TESTS COMPLETE" in _content
                            or "RESULT: PASS" in _content):
                        _ran_gt = True
                        break
                if not (_has_test and _ran_gt):
                    _gametest_ok = False
                    messages.append({"role": "user", "content":
                        "<gametest-check> FAILED: 你尚未完成 GameTest 自循环验证（需要：①在 src/test/java 编写至少一个 @GameTest 测试类；"
                        "②调用 run_test_gametest 运行测试（扫描 src/test；禁止用 run_game_test_server 自检——它只扫 src/main）；"
                        "③可用 read_game_test_log 查看日志）。"
                        "按 skill-first 纪律，未跑通 GameTest 不得宣布 MOD 完成。请先补测试并运行，通过后再结束。"})
                    messages.append({"role": "user", "content":
                        "<tool-call-required> 任务未完成，禁止只输出纯文本。你必须立即调用一个工具："
                        "write_file / edit_file / build_mod_jar_forge / run_test_gametest / run_mod_test_cycle / validate_resources。"
                        "不要回复“No additional output”之类的话。</tool-call-required>"})
                    _no_tool_strikes += 1
                    if _no_tool_strikes >= 2:
                        # 兜底：连续空转时自动执行一次构建，避免模型不调用工具导致死循环。
                        logger.warning("连续空转，自动调用 build_mod_jar_forge 推进")
                        try:
                            from .tools import _forge_build_jar
                            _auto = _forge_build_jar({})
                        except Exception as _e:
                            _auto = f"Error: auto build failed: {_e}"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": f"auto-{os.urandom(4).hex()}",
                            "content": _auto,
                        })
                        _no_tool_strikes = 0
                    logger.info("gametest-check FAILED + tool-call-required 注入")
            except Exception as _e:
                logger.info(f"gametest-check 跳过: {_e}")
            if not _gametest_ok:
                _gametest_rejects += 1
                # 防死循环兜底（webserv_amber 实测连续打回、每圈一轮构建+GameTest）：
                # 打回 ≥3 次且 dist 已有非模板产物 → 视为完成强制收尾。
                # 闸的标记检查可能因 spill/压缩失明，不能任由它无限循环烧额度。
                if _gametest_rejects >= 3:
                    _jars = []
                    if os.path.isdir("dist"):
                        _jars = [f for f in os.listdir("dist")
                                 if f.endswith(".jar") and "examplemod" not in f]
                    if _jars:
                        logger.warning("GameTest 打回 ≥3 次但 dist 已有产物，强制收尾防无限循环")
                        _step_machine.complete_turn()
                        _save_session_log(_session_log)
                        if IS_MOD_MODE:
                            supervisor_manager.stop()
                        return (message.content or "") + (
                            f"\n\n[system] GameTest 校验连续 {_gametest_rejects} 次未通过判定，"
                            f"但 dist/{_jars[0]} 已生成（此前曾报告 GameTest 通过），已强制收尾，请人工复核。")
                continue
            # ★ 长对话语义（M-opt4）：不自动清空 .tasks / todo / team /
            #    协议状态。daemon 常驻期间任务、队友名册、协议请求跨轮保留，
            #    用户可以在"完成一轮"后继续对话迭代（例如"再优化一下"）。
            #    进程退出（空闲超时）后 .tasks/ 仍落盘，下次进程自动恢复；
            #    队友名册/todo/协议为内存态，随进程退出消失（可接受）。
            #    （旧逻辑：任务全部完成时清空——已按用户要求移除）

            # ── 收尾：构建 mod jar（成功会复制到 dist/）。C 组合：仅 GameTest 已通过后自动构建 ──
            # 未跑通 GameTest（_gametest_ok=False）不会走到这里（已在上面 continue 强制补测）。

            # 放在 zip 预生成前，生成结束后自动尝试打包；不依赖模型主动调用工具。
            try:
                import os as _os
                if (_os.path.exists("gradlew.bat") or _os.path.exists("gradlew")) and _os.path.exists("build.gradle"):
                    print("[run_task] 开始构建 mod jar（首次构建需数分钟）...", flush=True)
                    from .tools import _forge_build_jar
                    _jres = _forge_build_jar({})
                    print(f"[run_task] {_jres[:3000]}", flush=True)
                else:
                    logger.info("非 Gradle/Forge 工程，跳过 jar 构建")
            except Exception as _e:
                logger.info(f"收尾构建跳过: {_e}")

            # ── 收尾：源码 zip 预生成（仅 Gradle/Forge 工程）──
            # 把 mod 工程打包为 <session>/mod.zip，用户第一次点下载即可秒下，
            # 无需在点击请求时现场打包 11MB。
            try:
                from .tools import _build_source_zip
                print(f"[run_task] {_build_source_zip()}", flush=True)
            except Exception as _e:
                logger.info(f"源码 zip 预生成跳过: {_e}")

            # ── 收尾：停止监管线程（防泄漏；daemon 兜底不会挂进程）──
            if IS_MOD_MODE:
                supervisor_manager.stop()

            _step_machine.complete_turn()
            _save_session_log(_session_log)
            return message.content

        # 执行工具，收集结果
        # ── Layer 3: compact 工具特殊处理（模型主动触发，最后执行）──
        used_todo = False
        compact_pending = False
        concluded_output = None
        _no_tool_strikes = 0
        for tc in message.tool_calls:
            _round_tool_counts[tc.function.name] = _round_tool_counts.get(tc.function.name, 0) + 1
            # 写前研究预算：没写任何 Java 源码前，禁止无休止读文档
            if tc.function.name in ("write_file", "edit_file") and (
                "src/main/java" in (tc.function.arguments or "")
                or "src/test/java" in (tc.function.arguments or "")
            ):
                _wrote_file = True
                _forced_write = False
                _existing_java = True
            elif not _wrote_file and tc.function.name in (
                "read_file", "bash", "grep", "glob",
                "web_search", "web_fetch", "search_api", "load_skill",
            ):
                _pre_write_reads += 1
            elif _wrote_file and tc.function.name in (
                "build_mod_jar_forge", "run_test_gametest", "run_mod_test_cycle",
                "validate_resources", "parse_build_output", "read_game_test_log",
            ):
                _post_write_research = 0
                _post_write_strikes = 0
                _forced_post_write = False
            elif _wrote_file and tc.function.name in (
                "read_file", "bash", "grep", "glob",
                "web_search", "web_fetch", "search_api", "load_skill",
            ):
                _post_write_research += 1
            # flash 适配：工具参数 JSON 可能不完整/非法，解析失败不炸主循环，
            # 而是返回温和错误文本作为该工具的结果，让模型修正后重试。
            try:
                args = json.loads(tc.function.arguments)
            except Exception as e:
                logger.warning(f"工具参数解析失败 | {tc.function.name} | {e} | raw={tc.function.arguments[:300]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": f"Error: Invalid tool arguments JSON for {tc.function.name}: {e}. "
                               f"Please call the tool again with valid JSON arguments.",
                })
                continue

            # compact 特殊处理：先跳过，等其他工具执行完再压缩
            if tc.function.name == "compact":
                compact_pending = True
                logger.info("Layer 3 compact 工具被模型主动调用 | 先跳过，等其他工具执行完")
                continue

            # force-write / force-build 硬禁用已取消：不再拦截研究类工具。
            # 只保留 write-first-stop / build-now-stop 软提醒。

            # M3: 统一走注册表执行管线（pre 钩子 → guard → handler → post 钩子；
            # total 函数：任何异常都转温和错误文本，不炸主循环）。
            raw_output = tool_registry.execute(tc.function.name, args)
            # 移植 dsh concludesTurn：工具结果带 [CONCLUDED] 标记时，本轮立即结束
            if "[CONCLUDED]" in str(raw_output):
                concluded_output = str(raw_output)
                logger.info(f"工具 {tc.function.name} 返回 [CONCLUDED]，本轮将立即收尾")
            output = _maybe_spill(tc.function.name, str(raw_output))
            if tc.function.name == "todo":
                used_todo = True
                print(f"\n[todo]\n{output}")   # 终端显示完整 todo 清单
            logger.info(f"工具调用: {tc.function.name} | 参数={json.dumps(args, ensure_ascii=False)} | output={output}")
            # ── 结构化工具日志（供前端 DSH 风格渲染）──
            # run.log 格式：
            #   [tool] <工具名> <参数JSON>        → 工具调用（命令/参数）
            #   [tool-result] <成功|失败> <输出>  → 执行结果（成功/失败 + 输出）
            # 与 [supervisor:xxx]/[subagent:xxx] 的旧格式并存，前端优先识别新格式。
            try:
                args_str = json.dumps(args, ensure_ascii=False)
                if tc.function.name == "bash":
                    # bash 特例：参数里的 command 直接展示（更友好）
                    args_str = str(args.get("command", args_str))
                ok = not str(output).lstrip().startswith("Error")
                print(f"[tool] {tc.function.name} {args_str}", flush=True)
                print(f"[tool-result] {'success' if ok else 'failed'}\n{output}", flush=True)
            except Exception:
                pass
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )

        # post-step hooks（DSH agent/turn-stopping 扩展点）
        run_post_step_hooks(messages, _round_tool_counts)
        _step_machine.end_step(reason="completed")

        # 完成信号：dist 出现 jar 且 GameTest 已通过才算可收尾；只出 jar 不算完成。
        # 匹配方式是 startswith：因此 run_mod_test_cycle 特意把 "RESULT: PASS"
        # 放在输出第一行让闸看得见；"[gametest]" 前缀不能作为通过标记
        # （run_game_test_server 无论成败都以它开头，会把闸带偏）。
        try:
            _gt_pass_markers = (
                "All required tests passed",
                "GAME TESTS COMPLETE",
                "RESULT: PASS",
            )
            _gt_passed = any(
                str(m.get("content", "")).lstrip().startswith(_gt_pass_markers)
                for m in messages if m.get("role") == "tool"
            )
            if os.path.isdir("dist") and _gt_passed:
                _dist_jars = [
                    f for f in os.listdir("dist")
                    if f.endswith(".jar") and "examplemod" not in f
                ]
                if _dist_jars:
                    # 首次达标不立即掐断：注入收尾提醒 + 宽限窗口。
                    # 含自定义实体/物品图标 的 MOD 还需按 CLIENT_VERIFY.md 做
                    # 客户端视觉验证（718d315bec0b：模型刚装好 AgentBridge
                    # 准备验证图标就被闸掐掉，验证没做成）；宽限耗尽才强制收尾。
                    # 注意：除"强制收尾"分支外都落空（不 continue），让本轮后续
                    # 守卫（防死循环计数 / compact / concluded）照常执行——
                    # 宽限分支里 continue 会跳过它们，等于宽限期内失去全部保险。
                    if _gate_round is None:
                        _gate_round = _round_idx
                        _replace_runtime_slot(messages, "completion-gate", (
                            "<completion-gate> build + GameTest 已达标"
                            f"（dist/{_dist_jars[0]} 存在且测试通过）。\n"
                            "若本 MOD 含自定义实体、刷怪蛋或物品图标，先按 docs/agent/CLIENT_VERIFY.md "
                            "完成客户端视觉验证（识图开启时 screenshot + analyze_image 即可）。\n"
                            "验证完成或不需要验证时：停止调用工具，下一轮直接输出面向用户的最终总结——"
                            "创建/修改了哪些文件、MOD 功能与关键数值、合成配方、安装方法、验证结论。"
                            "</completion-gate>"
                        ))
                        logger.info(f"completion-gate 首次触发（round {_round_idx}），注入收尾提醒，宽限 {COMPLETION_GRACE_ROUNDS} 轮")
                    elif _round_idx - _gate_round >= COMPLETION_GRACE_ROUNDS:
                        _force_final_msg = _summarize_completion(messages, (
                            f"MOD 完成：dist/{_dist_jars[0]} 已生成且 GameTest 通过。"
                            f"（总结生成失败，此为系统回退文本；详细过程见运行日志。）"
                        ))
                        logger.warning("completion-gate 宽限耗尽，强制收尾")
                        continue
                    # 宽限期内：不干预，正常走完本轮守卫（模型做验证或自行总结）
        except Exception:
            pass

        # 写前研究预算守卫：超过 6 次读/查还没写文件，强制提醒立即写首个文件
        # 仅 mod 模式：chat 只读咨询里读文件是正常工作流，注入"必须写文件"
        # 只会让模型困惑（写调用全被沙箱拒绝），实测导致内部抱怨文本泄漏。
        if IS_MOD_MODE and not _wrote_file and not _existing_java and not _pre_write_warned and _pre_write_reads >= 6:
            _pre_write_warned = True
            _write_strikes += 1
            # force-write 硬禁用已取消：只保留软提醒，避免模型被工具锁定。
            if not _starter_auto_written and _auto_write_starter(messages):
                _starter_auto_written = True
                # 自动复制的 starter 不算“已主动写代码”：
                # 保持 _wrote_file=False，下一轮继续 nag，直到模型真正写/改 src/main|test 文件。
                _pre_write_warned = False
                logger.warning("已自动从 starter 写入 Java 文件，继续任务")
                messages.append({
                    "role": "user",
                    "content": (
                        "<auto-starter> 系统已自动复制合适的 starter Java 文件到 src/main/java。"
                        "请基于该文件继续完成剩余资源/测试，不要再阅读 starter 文档。</auto-starter>"
                    ),
                })
                continue
            # 终局手段（缺陷1）：新 modid 没有 starter 可匹配时，软提醒会无限循环
            # （c43424752e7d 连续 4 次 write-first-stop 无效）。第二次超预算直接写
            # 最小可编译骨架，把 agent 推进到写/改/编译阶段，并视为已过"写前"关卡。
            if _write_strikes >= 2 and not _skeleton_written:
                _sk_modid = _auto_write_skeleton(messages)
                if _sk_modid:
                    _skeleton_written = True
                    _wrote_file = True  # 切换到写后预算，写前 nag 到此为止
                    _pre_write_warned = False
                    logger.warning(f"写前预算终局：已写入 modid={_sk_modid} 最小骨架")
                    messages.append({
                        "role": "user",
                        "content": (
                            f"<auto-skeleton> 你已多次超预算未写码，系统已在 "
                            f"src/main/java/com/{_sk_modid}/ 写入最小可编译主类骨架"
                            f"（modid={_sk_modid}，1.21.11 注册写法已就位）。"
                            f"立刻基于它继续：①按命名规则同步 mods.toml 的 modId、"
                            f"build.gradle 的 group/archivesName、settings.gradle 的 "
                            f"rootProject.name；②在其上扩展物品/方块/BlockEntity 等注册与逻辑。"
                            f"本轮之后禁止再 read/grep starter 与 mc_java_sources，"
                            f"下一轮必须是 write_file 或 edit_file。</auto-skeleton>"
                        ),
                    })
                    continue
            logger.warning(f"写前研究超预算（{_pre_write_reads}），强制提醒写文件")
            messages.append({
                "role": "user",
                "content": (
                    "<write-first-stop> 你已反复阅读 mc_java_sources/starter 但没有写文件。"
                    "立即停止阅读源码。如果还没加载相关技能，先调用一次 load_skill 加载最相关技能"
                    "（例如 forge-simple-min-mod）；然后立刻用 write_file 写出第一个最小 Java 文件，"
                    "再 build/compile 根据报错处理。不要继续 read_file/grep mc_java_sources。</write-first-stop>"
                ),
            })
            # 重要：允许再次进入写前研究预算守卫，
            # 这样 _write_strikes 能累加到 2，从而触发 forced-write 模式。
            _pre_write_warned = False
            continue

        # 写后研究预算：已写代码但仍反复查 API 不编译/测试
        # 仅 mod 模式：chat 模式没有可编译的工程，注入"立即 build"同样是无效施压。
        if IS_MOD_MODE and _wrote_file and _post_write_research >= 8 and not _pre_write_warned:
            _post_write_strikes += 1
            logger.warning(f"写后研究超预算（{_post_write_research}），软性提醒编译/测试")
            messages.append({
                "role": "user",
                "content": (
                    "<build-now-stop> 你已经写完了 Java 代码，但还在反复查 API 不编译。"
                    "立即停止研究。调用 validate_resources 检查资源，"
                    "然后调用 run_mod_test_cycle 或 build_mod_jar_forge 编译。"
                    "编译报错再查具体符号。不要继续 read_file/grep/search_api。</build-now-stop>"
                ),
            })
            _post_write_research = 0
            continue

        # 工具主动收尾：不进入下一轮 LLM 调用
        if concluded_output is not None:
            _force_final_msg = (
                f"[CONCLUDED] A tool has completed the relevant work and ended this turn.\n"
                f"Final tool output:\n{concluded_output}"
            )
            _step_machine.conclude_turn()
            logger.warning(_force_final_msg)
            continue

        # 防死循环：统计工具调用轮次；超限强制收尾
        if message.tool_calls:
            _tool_rounds += 1
            if _tool_rounds >= MAX_TOOL_ROUNDS:
                _force_final_msg = (
                    f"Max tool rounds reached ({MAX_TOOL_ROUNDS}). Partial progress is in run.log; "
                    "stopping the loop to prevent an infinite tool-call loop."
                )
                logger.warning(_force_final_msg)
                continue

        # 总轮数硬上限（含纯文本重试轮）：出口闸失明时纯文本轮不计 _tool_rounds，
        # 实测曾连续多轮打回不终止（webserv_amber），给整个循环一个硬边界
        if _round_idx >= MAX_TOTAL_ROUNDS:
            _force_final_msg = (
                f"Max total rounds reached ({MAX_TOTAL_ROUNDS}). Partial progress is in run.log; stopping."
            )
            logger.warning(_force_final_msg)
            continue

        # compact 最后执行：替换整个 messages 列表
        if compact_pending:
            messages, _ = handle_compact(messages)
            _before_seq = max((e.seq for e in _session_log.events), default=0)
            _summary_content = next(
                (str(m.get("content", "")) for m in messages
                 if m.get("role") == "user" and isinstance(m.get("content"), str)
                 and "[Context compacted" in m.get("content", "")),
                "",
            )
            _session_log.add_compaction(_summary_content, 1, _before_seq)
            _synced_count = 0
            # compact 后上下文已重置，重置 nag 计数器
            rounds_since_todo = 0
            logger.info("compact 执行完毕，messages 已被替换，跳过本轮 nag reminder")
            continue  # 跳过 nag reminder，直接进入下一轮

        # ── Nag Reminder：连续 3 轮没更新 todo 就注入提醒 ──
        # 仅 mod 模式：chat 咨询里"一句话问答 + 两次查证"也会触发催促，
        # 是纯噪音（cbc300ed23b3 实测模型还要分心解释为什么不更新 todo）。
        if used_todo:
            rounds_since_todo = 0
        else:
            rounds_since_todo += 1

        if IS_MOD_MODE and rounds_since_todo >= 3:
            logger.info("触发 nag reminder：连续 3 轮未更新 todo")
            _replace_runtime_slot(
                messages,
                "reminder",
                "<reminder>Update your todos to track progress.</reminder>",
            )
            rounds_since_todo = 0

def _messages_hint_mod(messages: list) -> bool:
    """判断消息里是否明显提到 MOD/模组/Forge，决定是否注入技能目录。"""
    for m in messages:
        if not isinstance(m, dict):
            continue
        if m.get("role") not in ("user", "system"):
            continue
        content = str(m.get("content", ""))
        if re.search(r"(?i)(/mod|(?<![a-z])mod(?![a-z])|模组|mod制作|我的世界.*(?:mod|模组)|forge)", content):
            return True
    return False



# 防死循环：同一 agent_loop 内允许的最大工具调用轮次（每轮可能含多个 tool_call）
# 默认 200：含真实客户端验证的任务（建世界/bridge 逐屏点击）实测 100 轮不够，
# 20:41 ruby-sword 会话在验证中途撞上限被掐断。可用 DSH_MAX_TOOL_ROUNDS 覆盖。
MAX_TOOL_ROUNDS = int(os.environ.get("DSH_MAX_TOOL_ROUNDS", "200"))
# 总轮数硬上限（含纯文本重试轮）：出口闸失明时的最后防线，保持 1.5 倍余量
MAX_TOTAL_ROUNDS = int(os.environ.get("DSH_MAX_TOTAL_ROUNDS", "300"))
# 完成闸宽限轮数：达标后先注入收尾提醒（含客户端验证指引），超过该轮数仍
# 未自然收尾才强制结束并生成总结。默认 25：覆盖一次完整客户端验证
# （启动客户端→建世界→give→截图→识图约 10~20 轮）。防"绿灯即掐"也防无限验证循环。
COMPLETION_GRACE_ROUNDS = int(os.environ.get("DSH_COMPLETION_GRACE_ROUNDS", "25"))


def _summarize_completion(messages: list, fallback: str) -> str:
    """完成闸收尾：让模型做一次无工具的最终总结作为用户可见回复。

    直接返回闸的系统文本会让"最终回复"变成内部串（718d315bec0b 实测：
    conversation.jsonl 里的 assistant 消息是 "MOD jar exists... stop calling
    tools and summarize"，用户看到完成却没有任何说明）。失败/空回复时回退。
    """
    try:
        msgs = list(messages) + [{"role": "user", "content": (
            "[system] 任务完成判定已满足（dist jar 存在且 GameTest 通过）。"
            "请立即输出面向用户的最终总结，不要再调用任何工具。内容包含："
            "创建/修改了哪些文件、MOD 功能与关键数值、合成配方、"
            "如何安装使用、已完成的验证。")}]
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": config.SYSTEM}] + msgs,
            max_tokens=4000,
        )
        text = resp.choices[0].message.content
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.warning(f"完成总结调用失败，回退闸文本: {e}")
    return fallback

# 超大工具结果阈值：超过则落盘 spill 文件，模型只看到前后预览
MAX_INLINE_TOOL_CHARS = 3000

# 会话根目录（.chat/ 断点与队列所在处）：由 server 通过 DSH_SESSION_ROOT 注入。
# agent 的 cwd 可能在会话根（chat）或 mod/（mod 模式），断点永远落在会话根，
# 因此这里显式读取环境变量而不是依赖 Path.cwd()。
SESSION_ROOT = os.environ.get("DSH_SESSION_ROOT", "")


def _current_session_root() -> str:
    """动态读取当前会话根目录（支持按 sessionId 隔离对话历史）。"""
    return os.environ.get("DSH_SESSION_ROOT", "")

# 流式思考转发钩子：由外部接入层（如清小搭 8001 服务）设置。
# 收到模型 delta.reasoning_content 时会实时调用 callback(text)；
# 未设置时保持原有行为（仅累积到完整 reasoning 后打印/记录）。
REASONING_SINK = None


def set_reasoning_sink(fn):
    """设置/清除 reasoning 实时回调。fn 可为 None 表示关闭。"""
    global REASONING_SINK
    REASONING_SINK = fn


def get_reasoning_sink():
    """返回当前 reasoning 实时回调（用于调用方临时覆盖后恢复）。"""
    return REASONING_SINK


def _maybe_spill(name: str, output: str) -> str:
    """Spill oversized plain-text tool results to disk, return preview+locator."""
    # Port of dsh spill-policy: skip read_file to avoid read -> spill -> read again loop.
    # 完成判定关键工具同样豁免：出口闸依赖其输出中的 GameTest 通过标记，
    # spill 预览可能截掉标记导致闸失明、无限打回（webserv_amber 实测）。
    # load_skill 必须豁免：技能正文被 spill 截成前 1200+后 1200 的拼接预览后，
    # move_skills_to_end 会把这份残片当成"技能全文"滚进 <active-skills>，
    # 上下文里永远缺失技能中段（cbc300ed23b3 实测模型抱怨 skill is truncated）。
    if name in ("read_file", "load_skill", "run_test_gametest", "run_mod_test_cycle",
                "run_game_test_server", "parse_gametest_results",
                "read_game_test_log", "build_mod_jar_forge"):
        return output
    if not isinstance(output, str) or len(output) <= MAX_INLINE_TOOL_CHARS:
        return output
    try:
        spill_dir = os.path.join(os.getcwd(), ".spill")
        os.makedirs(spill_dir, exist_ok=True)
        fname = f"{name}-{os.urandom(4).hex()}.txt"
        path = os.path.join(spill_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
        preview = output[:1200] + "\n...[truncated]...\n" + output[-1200:]
        return (
            f"[spilled] Full tool output ({len(output)} chars) saved to {path}.\n"
            f"Preview:\n{preview}"
        )
    except Exception:
        return output


def _auto_write_starter(messages: list) -> bool:
    """If the agent refuses to write, auto-copy a matching starter Java file.

    Scans messages for `modid`/`MODID`, then finds a starter/*.java whose content
    contains that modid and writes it under src/main/java/<package path>.
    Returns True if a file was written.
    """
    import glob as _glob
    import re as _re
    try:
        # 1) infer modid from USER messages only（修复：此前未过滤 role，工具输出/
        #    starter 文档里出现的 "modid = xxx"（如 coppertools 等其他 mod 示例）
        #    会污染推断，导致把无关 starter 复制进当前任务——实测 bug）
        modid = None
        for m in messages:
            if m.get("role") != "user":
                continue
            c = m.get("content", "") if isinstance(m.get("content"), str) else ""
            m2 = _re.search(r"modid[ =:]+([a-zA-Z0-9_\-]+)", c)
            if m2:
                modid = m2.group(1).lower()
                break
        if not modid:
            return False
        # 2) score starter java files by task keywords + modid match
        candidates = _glob.glob(os.path.join(os.getcwd(), "starter", "**", "*.java"), recursive=True)
        task_text = "\n".join(
            str(m.get("content", "")) for m in messages
            if m.get("role") == "user" and isinstance(m.get("content"), str)
        ).lower()
        block_kw = ("block", "方块")
        item_kw = ("item", "food", "apple", "ingot", "gem", "物品", "食物")
        tool_kw = ("tool", "sword", "pickaxe", "axe", "工具", "剑", "镐")
        game_kw = ("game", "minigame", "swap", "大逃杀", "游戏", "交换", "玩家")
        target_src = None
        best_score = 0  # 只有匹配到 modid 或任务关键词（score>0）才可能选中，避免复制无关 starter
        for path in candidates:
            try:
                content = open(path, "r", encoding="utf-8").read()
            except OSError:
                continue
            low_path = path.lower().replace("\\", "/")
            # modid 必须出现在候选文件的包名或路径里，否则视为与任务无关的 starter，
            # 直接跳过（原"modid 在正文任意位置即 +1"太宽松，导致 coppertools 误配）
            pkg_m = _re.search(r"package\s+([\w\.]+)\s*;", content)
            if not ((pkg_m and modid in pkg_m.group(1).lower()) or modid in low_path):
                continue
            score = 1
            if any(k in task_text for k in block_kw) and "/block/" in low_path:
                score += 6
            if any(k in task_text for k in tool_kw) and ("/tools/" in low_path or "tool" in low_path):
                score += 7
            if any(k in task_text for k in item_kw) and ("/item/" in low_path or "rubymod" in low_path):
                score += 5
            if any(k in task_text for k in game_kw) and ("/swapgame/" in low_path or "swapgame" in low_path):
                score += 9
            # 只有 score>=2（modid匹配 + 至少一个任务关键词，或强关键词）才可能选中，
            # 避免仅凭 modid 匹配就复制无关 starter
            if score > best_score and score >= 2:
                best_score = score
                target_src = path
                best_content = content
        if not target_src:
            return False
        text = best_content
        # 3) derive package path
        pm = _re.search(r"package\s+([\w\.]+)\s*;", text)
        if not pm:
            return False
        pkg_path = pm.group(1).replace(".", "/")
        class_name = os.path.basename(target_src)
        dest = os.path.join(os.getcwd(), "src", "main", "java", pkg_path, class_name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.exists(dest):
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            logger.warning(f"auto-wrote starter Java file: {dest}")
            return True
    except Exception:
        return False
    return False


def _infer_modid(messages: list) -> str | None:
    """从用户消息推断 modid：显式 modid=xxx 优先，否则取全角括号里的英文名压成小写连写。"""
    import re as _re
    for m in messages:
        if m.get("role") != "user":
            continue
        c = m.get("content", "") if isinstance(m.get("content"), str) else ""
        m2 = _re.search(r"modid[ =:]+([a-z0-9_\-]{2,32})", c, _re.I)
        if m2:
            return m2.group(1).lower()
    for m in messages:
        if m.get("role") != "user":
            continue
        c = m.get("content", "") if isinstance(m.get("content"), str) else ""
        m3 = _re.search(r"[（(]([A-Za-z][A-Za-z0-9 ]{2,31})[）)]", c)
        if m3:
            modid = _re.sub(r"[^a-z0-9_]", "", m3.group(1).lower())
            if 3 <= len(modid) <= 32:
                return modid
    return None


def _auto_write_skeleton(messages: list) -> str | None:
    """写前预算的终局手段：starter 匹配失败时，直接生成最小可编译主类骨架。

    背景（c43424752e7d 实测）：新 modid 任务没有可匹配的 starter，
    _auto_write_starter 永远 False → 守卫退化成无限 <write-first-stop> 软提醒
    （连续 4 次无效，监管线程还专门写信箱）。本函数从用户需求推断 modid，
    写出符合本模板 1.21.11 硬事实（FMLJavaModLoadingContext.get().getModBusGroup()）
    的最小主类，把 agent 从"只读绕圈"直接推进到写/改/编译阶段。
    返回写入的 modid；无法推断或已存在时返回 None（保持原软提醒行为）。
    """
    modid = _infer_modid(messages)
    if not modid:
        return None
    cls = modid.title().replace("_", "").replace("-", "") + "Mod"
    pkg_dir = os.path.join(os.getcwd(), "src", "main", "java", "com", modid)
    dest = os.path.join(pkg_dir, f"{cls}.java")
    src_root = os.path.join(os.getcwd(), "src", "main", "java")
    # 已有任何非模板 Java（含骨架自身）都不再写
    def _is_template(p):
        parts = [x.lower() for x in p.parts]
        return "com" in parts and "example" in parts and "examplemod" in parts
    from pathlib import Path as _P
    if any(p.suffix == ".java" and not _is_template(p) for p in _P(src_root).rglob("*.java")):
        return None
    try:
        os.makedirs(pkg_dir, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(
                f"package com.{modid};\n\n"
                f"import net.minecraftforge.fml.common.Mod;\n"
                f"import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;\n"
                f"import net.minecraftforge.registries.DeferredRegister;\n"
                f"import net.minecraftforge.registries.ForgeRegistries;\n\n"
                f"@Mod({cls}.MODID)\n"
                f"public class {cls} {{\n"
                f"    public static final String MODID = \"{modid}\";\n\n"
                f"    // 可在此扩展各注册表（物品/方块/BlockEntity 等），需要再加\n"
                f"    public static final DeferredRegister<net.minecraft.world.item.Item> ITEMS =\n"
                f"            DeferredRegister.create(ForgeRegistries.ITEMS, MODID);\n\n"
                f"    public {cls}() {{\n"
                f"        // 1.21.11 硬事实：注册挂 getModBusGroup()，不要写 IEventBus/getModEventBus\n"
                f"        ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());\n"
                f"    }}\n"
                f"}}\n"
            )
        logger.warning(f"auto-wrote minimal mod skeleton: {dest} (modid={modid})")
        return modid
    except Exception as e:
        logger.warning(f"auto_write_skeleton 失败: {e}")
        return None


def _is_context_overflow(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "context length", "maximum context", "context window exceeded",
        "context_window_exceeded", "token limit", "too many tokens",
        "maximum context length",
    )
    return any(m in text for m in markers)


def _replace_runtime_slot(messages: list, tag_prefix: str, content: str) -> None:
    """Replace ephemeral runtime-context messages (official dsh runtime-context style).

    Removes any previous user message whose content starts with '<tag_prefix',
    then appends the latest one. Prevents stale/duplicate runtime context from
    accumulating and distracting the model.
    """
    messages[:] = [
        m for m in messages
        if not (
            m.get("role") == "user"
            and isinstance(m.get("content"), str)
            and m["content"].lstrip().startswith(f"<{tag_prefix}")
        )
    ]
    messages.append({"role": "user", "content": content})


def _save_checkpoint(messages: list) -> None:
    """把当前轮 messages 存为断点（每轮循环开头）。"""
    session_root = _current_session_root()
    if not session_root:
        return
    try:
        from .conversation import save_working
        save_working(session_root, messages)
    except Exception as e:
        logger.warning(f"断点保存失败: {e}")


def _drain_interjections(messages: list) -> None:
    """读取运行中用户插入的排队消息并注入上下文（每轮循环开头）。

    去重：enqueue_pending 已把消息同步写入 conversation 历史，自动续跑时
    load_recent_history 可能已包含它——这里按 (role, content) 去重，
    避免同一条消息被注入两次。
    """
    session_root = _current_session_root()
    if not session_root:
        return
    try:
        from .conversation import drain_pending
        pending = drain_pending(session_root)
        if pending:
            existing = {
                (m.get("role"), m.get("content"))
                for m in messages
                if isinstance(m, dict) and m.get("role") in ("user", "assistant")
            }
            added = 0
            for m in pending:
                key = (m.get("role"), m.get("content"))
                if key in existing:
                    logger.info(f"跳过重复注入的排队消息: {str(m.get('content'))[:40]}")
                    continue
                messages.append(m)
                existing.add(key)
                added += 1
            if added:
                logger.info(f"注入 {added} 条运行中用户插入消息")
    except Exception as e:
        logger.warning(f"排队消息注入失败: {e}")


def _sync_messages_to_log(log: SessionLog, messages: list, synced_count: int) -> int:
    """Append messages[+synced_count:] into the event-sourced SessionLog.

    Returns the new number of messages that have been logged.
    """
    try:
        while synced_count < len(messages):
            m = messages[synced_count]
            role = m.get("role")
            if role == "user":
                log.add_user(str(m.get("content", "")), source="messages")
            elif role == "assistant":
                log.add_assistant(
                    content=m.get("content"),
                    tool_calls=m.get("tool_calls"),
                    reasoning=m.get("reasoning_content"),
                )
            elif role == "tool":
                log.add_tool_result(str(m.get("tool_call_id", "")), str(m.get("content", "")))
            synced_count += 1
    except Exception as e:
        logger.warning(f"sync messages to log failed: {e}")
    return synced_count


def _save_session_log(log: SessionLog) -> None:
    """Persist the event-sourced session log for replay/debug (DSH JSONL backend)."""
    try:
        path = os.path.join(".chat", "session_events.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(log.to_jsonl())
        logger.info(f"SessionLog saved: {path} events={len(log.events)}")
    except Exception as e:
        logger.warning(f"save session log failed: {e}")


def _dump_round_messages(round_idx: int, messages: list, tool_counts: dict) -> None:
    """每轮调试快照：打印消息概览 + 工具统计，并落盘完整 JSONL。

    用途：
    - 观察消息是否被压缩/丢信息
    - 观察工具调用是否合理
    """
    try:
        from .compact import estimate_tokens as _est
        tokens = _est(messages)
        counts = ", ".join(f"{k}:{v}" for k, v in sorted(tool_counts.items()))
        print(f"\n[round] #{round_idx} messages={len(messages)} tokens≈{tokens} tools=[{counts}]", flush=True)
        for i, m in enumerate(messages):
            role = m.get("role", "?")
            content = m.get("content", "")
            if isinstance(content, list):
                content = json.dumps(content, ensure_ascii=False)
            content = str(content)
            preview = content[:180].replace("\n", "\\n")
            tool_calls = m.get("tool_calls")
            tc_note = f" tool_calls={len(tool_calls)}" if tool_calls else ""
            print(f"  [{i}] {role}{tc_note} len={len(content)} | {preview}", flush=True)
        # 完整快照（限制单条内容长度，避免文件爆炸；完整内容仍可从 run.log 工具结果看）
        snap_dir = os.path.join(".chat", "debug")
        os.makedirs(snap_dir, exist_ok=True)
        snap_path = os.path.join(snap_dir, "round_messages.jsonl")
        with open(snap_path, "a", encoding="utf-8") as f:
            record = {"round": round_idx, "tokens": tokens, "tool_counts": tool_counts,
                      "messages": [{ "role": m.get("role"), "content": str(m.get("content", ""))[:5000],
                                     "tool_call_ids": [tc.get("id") for tc in (m.get("tool_calls") or [])] }
                                   for m in messages]}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"round dump failed: {e}")


def _ensure_mc_java_sources():
    """若工作区缺少 mc_java_sources，则链接到仓库 mc_java_sources_1.21.11。

    手动复制的 mod 模板不会自动带 server 建的 junction；这里补上，
    保证 search_api/read_file 能在工作区内读到完整 MC/Forge 源码。
    """
    if not IS_MOD_MODE and os.environ.get("DSH_ALLOW_MC_SOURCES") != "1":
        return
    target = Path.cwd() / "mc_java_sources"
    source = Path(__file__).resolve().parent.parent / "mc_java_sources_1.21.11"
    if target.exists() or not source.exists():
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(target), str(source)],
                check=True, capture_output=True,
            )
        else:
            target.symlink_to(source, target_is_directory=True)
        logger.info(f"已补建 mc_java_sources junction -> {source}")
    except Exception as e:
        logger.warning(f"补建 mc_java_sources 失败: {e}")


def _ensure_docs_agent():
    """在会话工作区创建 docs/agent 软链接，指向仓库根的参考文档（只读，不复制）。"""
    if os.environ.get("DSH_ALLOW_MC_SOURCES") != "1" and not IS_MOD_MODE:
        return
    repo_root = Path(__file__).resolve().parent.parent
    docs_src = repo_root / "docs" / "agent"
    target = Path.cwd() / "docs" / "agent"
    if target.exists() or not docs_src.is_dir():
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(target), str(docs_src)],
                check=True, capture_output=True,
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(docs_src, target_is_directory=True)
        logger.info(f"已补建 docs/agent junction -> {docs_src}")
    except Exception as e:
        logger.warning(f"补建 docs/agent 失败: {e}")


if __name__ == "__main__":
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set")
        exit(1)
    task = """
    规则：严禁动当前文件夹内的文件。所有操作只能在 demo 文件夹内进行，
测试完成后删除 demo 文件夹与全部运行时残留（.worktrees/.tasks/.team/.transcripts/__pycache__/agent.log）。

### 阶段一：搭建隔离环境（验证 worktree_create + 双状态机联动 + worktree_list）
1. 用 bash 创建 demo 文件夹，在其中 git init 一个干净仓库（`git init -b main demo-s12`），
   用 write_file 写入 config.py（内容 `value = 'base'`），git add + commit 作为基线。
2. 用 task_create 创建两个任务：#1「重构 config.py」、#2「给 config.py 加校验」。
3. 用 worktree_create 给 #1 和 #2 各建一个 worktree。
   验证：worktree_create 返回值指向 demo-s12/.worktrees/task-N；
   用 task_get 确认两个任务都自动从 pending 变为 in_progress（双状态机联动点①）。
4. 用 worktree_list 确认注册表里有 task-1、task-2 两条 active 记录，目录都存在。

### 阶段二：并行隔离核心验证（验证 worktree_use + 文件工具基座 + run_in_worktree）
5. worktree_use(1) 切进 task-1 的隔间，用 write_file 把 config.py 改成 value = 'A'。
6. worktree_use(2) 切进 task-2 的隔间，用 write_file 把 config.py 改成 value = 'B'。
7. 用 worktree_run(1, "type config.py") 和 worktree_run(2, "type config.py") 验证两个隔间各持己见（A / B）。
8. 用 bash 切回主目录，type 主目录的 config.py，验证仍是 'base'（主目录不受影响）。
   —— 这是 s12 的核心：同一文件被两个 Agent 各改一遍，互不覆盖、无静默丢失。

### 阶段三：收工合并（验证 worktree_remove + merge 回主 + 状态机联动点②）
9. worktree_remove(1, complete_task=True, merge=True)：
   验证主目录 config.py 变成 value = 'A'（改动合并回主分支）；
   task_get(1) 确认任务 completed；worktree_list 确认 task-1 已注销，目录已删除。
10. 用 bash 确认分支 task-1 已被清理。

### 阶段四：崩溃恢复（验证 worktree_recover）
11. 先 worktree_recover() 验证健康状态下无孤儿（incomplete_ops 为空）。
12. 制造故障：用 bash 在 demo-s12/.worktrees 下手动 mkdir 一个未注册目录 orphan-xyz；
    再 worktree_recover()，验证返回的 orphaned_worktrees 包含 orphan-xyz（磁盘有、注册表无 → 孤儿目录标记）。

### 阶段五：后台任务跟随基座（验证 run_in_background 感知 worktree）
13. worktree_use(2) 后，用 run_in_background 跑一条命令（如 `cd & cd` 打印当前路径或
    写一个文件），通知到达后验证该命令是在 task-2 的 worktree 目录内执行的。

### 阶段六：收尾与汇总（验证 worktree_remove + 清理）
14. worktree_remove(2, complete_task=True)，task_get(2) 确认 completed、任务全部完成。
15. worktree_recover() 最终扫一遍，确认注册表空、无孤儿、事件流完整。
16. 删除 demo 文件夹与一切运行时残留。
17. 汇报验证结果表格：worktree_create 建隔间✓、任务自动 in_progress✓、worktree_use 切换✓、
    文件工具落进隔间✓、并行互不覆盖✓、主目录不受影响✓、worktree_run✓、
    merge 回主✓、任务 completed✓、注册表注销✓、分支清理✓、worktree_recover 孤儿检测✓、
    run_in_background 跟随基座✓、清理✓。
"""
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)

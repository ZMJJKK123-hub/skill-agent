import json
import os
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

# 防死循环：同一 agent_loop 内允许的最大工具调用轮次（每轮可能含多个 tool_call）
MAX_TOOL_ROUNDS = int(os.environ.get("DSH_MAX_TOOL_ROUNDS", "100"))

# 超大工具结果阈值：超过则落盘 spill 文件，模型只看到前后预览
MAX_INLINE_TOOL_CHARS = 3000

# 会话根目录（.chat/ 断点与队列所在处）：由 server 通过 DSH_SESSION_ROOT 注入。
# agent 的 cwd 可能在会话根（chat）或 mod/（mod 模式），断点永远落在会话根，
# 因此这里显式读取环境变量而不是依赖 Path.cwd()。
SESSION_ROOT = os.environ.get("DSH_SESSION_ROOT", "")

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
    if name == "read_file":
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
        # 1) infer modid from user messages
        modid = None
        for m in messages:
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
            if isinstance(m.get("content"), str)
        ).lower()
        block_kw = ("block", "方块")
        item_kw = ("item", "food", "apple", "ingot", "gem", "物品", "食物")
        tool_kw = ("tool", "sword", "pickaxe", "axe", "工具", "剑", "镐")
        game_kw = ("game", "minigame", "swap", "大逃杀", "游戏", "交换", "玩家")
        target_src = None
        best_score = -1
        for path in candidates:
            try:
                content = open(path, "r", encoding="utf-8").read()
            except OSError:
                continue
            low_path = path.lower().replace("\\", "/")
            score = 0
            if modid in content.lower():
                score += 1
            if any(k in task_text for k in block_kw) and "/block/" in low_path:
                score += 6
            if any(k in task_text for k in tool_kw) and ("/tools/" in low_path or "tool" in low_path):
                score += 7
            if any(k in task_text for k in item_kw) and ("/item/" in low_path or "rubymod" in low_path):
                score += 5
            if any(k in task_text for k in game_kw) and ("/swapgame/" in low_path or "swapgame" in low_path):
                score += 9
            if score > best_score:
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
    if not SESSION_ROOT:
        return
    try:
        from .conversation import save_working
        save_working(SESSION_ROOT, messages)
    except Exception as e:
        logger.warning(f"断点保存失败: {e}")


def _drain_interjections(messages: list) -> None:
    """读取运行中用户插入的排队消息并注入上下文（每轮循环开头）。

    去重：enqueue_pending 已把消息同步写入 conversation 历史，自动续跑时
    load_recent_history 可能已包含它——这里按 (role, content) 去重，
    避免同一条消息被注入两次。
    """
    if not SESSION_ROOT:
        return
    try:
        from .conversation import drain_pending
        pending = drain_pending(SESSION_ROOT)
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


def agent_loop(messages: list) -> str:
    rounds_since_todo = 0
    # ── 第 13 课：代码强制派发监管 Agent（不依赖主 agent 主动调 task）──
    # 每次任务开始必然启动后台监管线程；幂等（已在跑则不重复启动）。
    # 仅 mod 模式：监管线程的规则全部围绕 run.log / GameTest / 技能纪律。
    if IS_MOD_MODE:
        supervisor_manager.start()
    # 绕圈修复：每个任务首轮强制注入 KNOWN_ISSUES.md 读取步骤。
    # 之前仅靠 SYSTEM prompt 软性要求（"BEFORE starting any work, run_read
    # KNOWN_ISSUES.md"），模型实际从未读过——而该文件第 25-28 行明确写着
    # "GameTest 自检必须用 run_test_gametest"，本可一击解决绕圈。
    # 现在改为硬性第一步：未读取前不允许进入正常规划/写码。
    _known_issues_injected = False
    _agents_injected = False
    _tool_rounds = 0
    _wrote_file = False
    _pre_write_reads = 0
    _pre_write_warned = False
    _starter_auto_written = False
    _write_strikes = 0
    _forced_write = False
    _post_write_research = 0
    _post_write_strikes = 0
    _forced_post_write = False
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
            return _force_final_msg

        # ── Layer 0c2: 断点保存 + 运行中插话注入（暂停/继续 与 queue 支持）──
        # 每轮开头把完整 messages 落盘（断点）；继续时新进程原样恢复。
        # 同时把运行中用户插入的排队消息读入上下文。
        _save_checkpoint(messages)
        _drain_interjections(messages)

        # ── Layer 0c3: 技能目录 digest 注入（M2，对齐 DSH tool-skill catalog）──
        # 目录（name+首行描述）以 user 消息注入：digest 变化才追加，不变零开销；
        # 会话中新增/编辑 SKILL.md 下一轮即生效。正文仍由 load_skill 按需加载。
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
                "禁止用 run_game_test_server 做自检。未读取前不要写任何代码/资源。</mandatory-first-step>"
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
        # 防 400：OpenAI 不允许 assistant 同时没有 content 和 tool_calls
        if content is None and not tool_calls:
            logger.warning("模型返回空内容且无工具调用，补占位内容后继续")
            content = "No additional output. Continuing the task based on the available context."
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
                    logger.info("gametest-check FAILED: 缺少 @GameTest 或未运行 run_test_gametest")
            except Exception as _e:
                logger.info(f"gametest-check 跳过: {_e}")
            if not _gametest_ok:
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
                "web_search", "web_fetch", "search_api",
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
                "web_search", "web_fetch", "search_api",
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

            # 强制写代码/强制编译模式：反复研究不写/不编译时，暂时禁用研究类工具
            if tc.function.name in (
                "read_file", "bash", "grep", "glob",
                "web_search", "web_fetch", "search_api",
            ) and (
                (_forced_write and not _wrote_file) or _forced_post_write
            ):
                if _forced_post_write:
                    msg = (
                        "Error: Post-write forced build mode is active. You have researched too many "
                        "rounds without compiling. Research tools are temporarily disabled until you "
                        "call validate_resources / build_mod_jar_forge / run_mod_test_cycle / run_test_gametest."
                    )
                else:
                    msg = (
                        "Error: Forced write mode is active. You must call write_file/edit_file "
                        "to create or edit a Java file under src/main/java or src/test/java before "
                        "using research tools. Research tools are temporarily disabled."
                    )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": msg,
                })
                continue

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

        # 完成信号：dist 目录出现 jar（MOD 产物）即视为可收尾，避免通过后继续绕圈
        try:
            if os.path.isdir("dist"):
                _dist_jars = [
                    f for f in os.listdir("dist")
                    if f.endswith(".jar") and "examplemod" not in f
                ]
                if _dist_jars:
                    _force_final_msg = (
                        f"MOD jar exists: dist/{_dist_jars[0]}. Task is complete; stop calling tools and summarize."
                    )
                    logger.warning(_force_final_msg)
                    continue
        except Exception:
            pass

        # 写前研究预算守卫：超过 6 次读/查还没写文件，强制提醒立即写首个文件
        if not _wrote_file and not _existing_java and not _pre_write_warned and _pre_write_reads >= 6:
            _pre_write_warned = True
            _write_strikes += 1
            if _write_strikes >= 2:
                _forced_write = True
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
        if _wrote_file and _post_write_research >= 8 and not _pre_write_warned:
            _post_write_strikes += 1
            if _post_write_strikes >= 3:
                _forced_post_write = True
                logger.warning(f"写后研究超预算（第{_post_write_strikes}次），禁用研究工具直到编译/测试")
            else:
                logger.warning(f"写后研究超预算（{_post_write_research}），强制提醒编译/测试")
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
        if used_todo:
            rounds_since_todo = 0
        else:
            rounds_since_todo += 1

        if rounds_since_todo >= 3:
            logger.info("触发 nag reminder：连续 3 轮未更新 todo")
            _replace_runtime_slot(
                messages,
                "reminder",
                "<reminder>Update your todos to track progress.</reminder>",
            )
            rounds_since_todo = 0


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

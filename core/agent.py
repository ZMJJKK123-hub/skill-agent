import json
import os

from . import config
from .config import client, MODEL, logger, MODE
from .tools import (
    TOOL_HANDLERS, bg_manager,
    format_background_results, teammate_manager, maybe_inject_skill_catalog,
    tool_registry,
)
from .protocol import inject_pending_requests
from .tools_tasks import task_manager, todo_manager
from .subagent import run_subagent_async
from .compact import (
    micro_compact,
    auto_compact,
    handle_compact,
    estimate_tokens,
    TOKEN_THRESHOLD,
)
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
MAX_TOOL_ROUNDS = 25

# 超大工具结果阈值：超过则落盘 spill 文件，模型只看到前后预览
MAX_INLINE_TOOL_CHARS = 3000

# 会话根目录（.chat/ 断点与队列所在处）：由 server 通过 DSH_SESSION_ROOT 注入。
# agent 的 cwd 可能在会话根（chat）或 mod/（mod 模式），断点永远落在会话根，
# 因此这里显式读取环境变量而不是依赖 Path.cwd()。
SESSION_ROOT = os.environ.get("DSH_SESSION_ROOT", "")


def _maybe_spill(name: str, output: str) -> str:
    """Spill oversized plain-text tool results to disk, return preview+locator."""
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
    _force_final_msg = None
    while True:
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
            messages = auto_compact(messages)

        # ── Layer 2.5: 运行时上下文快照（移植 dsh runtime-context projection）──
        # 用一条可替换的 <runtime-context> 消息汇总当前 todo/任务状态，
        # 防止历史里堆积旧状态导致模型迷失。
        _rt_parts = []
        try:
            if todo_manager.todos:
                _rt_parts.append("Todo progress:\n" + todo_manager.render())
            _tasks = task_manager.list_tasks()
            if _tasks:
                _rt_parts.append("Task board:\n" + "\n".join(
                    f"- #{t.get('id')} [{t.get('status', '?')}] {t.get('subject', '')[:80]}"
                    for t in _tasks
                ))
        except Exception:
            pass
        if _rt_parts:
            _replace_runtime_slot(
                messages,
                "runtime-context",
                "Current runtime context. This snapshot supersedes earlier runtime-context snapshots.\n\n"
                + "\n\n".join(_rt_parts),
            )

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
            if _is_context_overflow(_le):
                logger.warning(f"上下文超限，自动压缩后重试: {_le}")
                messages = auto_compact(messages)
                continue
            raise

        content_parts: list[str] = []
        reasoning_parts: list[str] = []
        tool_call_deltas: dict[int, dict] = {}
        finish_reason = None
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
        logger.info(f"finish_reason={choice.finish_reason}")

        # 退出条件：模型不再调工具
        if choice.finish_reason != "tool_calls":
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
                return message.content

            # ── GameTest 强制核查（C 组合：未跑通 GameTest 自循环则禁止完成）──
            _gametest_ok = True
            try:
                from pathlib import Path as _P
                _base = _P.cwd()
                # 1) 是否在 src/test/java 创建了 @GameTest 测试类
                _has_test = False
                for _fp in _base.rglob("*.java"):
                    try:
                        if "@GameTest" in _fp.read_text(encoding="utf-8", errors="replace"):
                            _has_test = True
                            break
                    except OSError:
                        continue
                # 2) 是否调用过 run_game_test_server（工具返回以 [gametest] 开头 / 或出现过该 tool_call）
                _ran_gt = any(
                    (m.get("role") == "tool" and str(m.get("content", "")).lstrip().startswith("[gametest]"))
                    or (m.get("role") == "assistant" and any(
                        tc.get("function", {}).get("name") in ("run_test_gametest", "run_game_test_server")
                        for tc in (m.get("tool_calls") or [])))
                    for m in messages
                )
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

            return message.content

        # 执行工具，收集结果
        # ── Layer 3: compact 工具特殊处理（模型主动触发，最后执行）──
        used_todo = False
        compact_pending = False
        concluded_output = None
        for tc in message.tool_calls:
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

        # 工具主动收尾：不进入下一轮 LLM 调用
        if concluded_output is not None:
            _force_final_msg = (
                f"[CONCLUDED] A tool has completed the relevant work and ended this turn.\n"
                f"Final tool output:\n{concluded_output}"
            )
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

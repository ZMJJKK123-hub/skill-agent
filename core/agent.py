import json
import os

from .config import client, MODEL, SYSTEM, logger
from .tools import (
    TOOLS, TOOL_HANDLERS, task_manager, todo_manager, bg_manager,
    format_background_results, teammate_manager,
)
from .protocol import inject_pending_requests, coordinator
from .subagent import run_subagent
from .compact import (
    micro_compact,
    auto_compact,
    handle_compact,
    estimate_tokens,
    TOKEN_THRESHOLD,
)
from .skillcheck import init_per_loop, run_loop_check


# ---------- 接线：注册 task handler（打破循环依赖）----------
# tools.py 不导入 subagent.py（避免循环依赖），
# task 工具的定义在 TOOLS 列表里，但 handler 在此接线。
TOOL_HANDLERS["task"] = lambda **kw: run_subagent(kw["prompt"])

# 第 11 课修复：leader 侧排除 submit_plan。
# submit_plan 语义是"队友→领导"，leader 是审批方，不该自己提交计划；
# 否则 _agent_id 缺省 "unknown"，审批回执会发到不存在的收件箱。
LEADER_TOOLS = [t for t in TOOLS if t["function"]["name"] != "submit_plan"]


def agent_loop(messages: list) -> str:
    rounds_since_todo = 0
    while True:
        # ── Layer 0: 排空后台通知（第 8 课）──
        # 在 micro_compact 之前注入，让通知作为新数据参与后续 compact 估算
        notifications = bg_manager.drain_notifications()
        if notifications:
            bg_results = format_background_results(notifications)
            messages.append({"role": "user", "content": bg_results})
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
            messages.append({"role": "user", "content": teammate_report})
            logger.info(f"注入队友汇报:\n{teammate_report}")

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

        # 发给模型
        logger.info(f"=== 新一轮 | messages 长度={len(messages)} ===")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=LEADER_TOOLS,  # 第 11 课：leader 侧排除 submit_plan
            max_tokens=8000,
        )

        choice = response.choices[0]
        message = choice.message

        # ── 打印思考过程（不进 messages）──
        reasoning = getattr(message, "reasoning_content", None)
        if reasoning:
            print(f"\n[思考] {reasoning}")
            logger.info(f"reasoning_content:\n{reasoning}")

        # 记录助手回复（只记录 content/tool_calls，不含 reasoning）
        messages.append(message.to_dict())
        if choice.finish_reason != "tool_calls":
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
                messages.append({
                    "role": "user",
                    "content": f"<reminder>Teammates still working: {', '.join(working_teammates)}. Wait for their reports before finishing.</reminder>",
                })
                continue

            logger.info(f"循环结束，最终回复:\n{message.content}")
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
                        "<gametest-check> FAILED: 你尚未完成 GameTest 自循环验证（需要：①编写至少一个 @GameTest 测试类；"
                        "②调用 run_game_test_server 运行测试；③可用 read_game_test_log 查看日志）。"
                        "按 skill-first 纪律，未跑通 GameTest 不得宣布 MOD 完成。请先补测试并运行，通过后再结束。"})
                    logger.info("gametest-check FAILED: 缺少 @GameTest 或未运行 run_game_test_server")
            except Exception as _e:
                logger.info(f"gametest-check 跳过: {_e}")
            if not _gametest_ok:
                continue
            # ★ 任务全部完成时，自动清空 .tasks、todo 和 team config
            # 每次运行干净开始：不跨 session 持久化（队友无持久记忆，保留名册无意义）
            if task_manager.all_completed():
                task_manager.clear()
                todo_manager.todos = []
                teammate_manager.team.clear()
                teammate_manager.threads.clear()
                teammate_manager._save_team_config()
                teammate_manager.bus.clear_all()  # 第 11 课：清空 .team/inbox/*.jsonl 消息文件
                coordinator.reset()  # 第 10 课：清空协议请求与写入登记
                logger.info("所有任务已完成，已自动清空 .tasks、todo、team config、inbox 和协议状态")

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

            return message.content

        # 执行工具，收集结果
        # ── Layer 3: compact 工具特殊处理（模型主动触发，最后执行）──
        used_todo = False
        compact_pending = False
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

            handler = TOOL_HANDLERS.get(tc.function.name)
            # ── 工具调用兜底防线：任何 handler 抛异常都不能炸掉 agent 主循环 ──
            # 把异常转成温和错误文本塞回给 LLM，让它继续思考而非整个进程崩溃。
            try:
                output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
            except Exception as e:
                logger.exception(f"工具调用异常 | {tc.function.name} | {e}")
                output = f"Error executing {tc.function.name}: {e}"
            if tc.function.name == "todo":
                used_todo = True
                print(f"\n[todo]\n{output}")   # 终端显示完整 todo 清单
            logger.info(f"工具调用: {tc.function.name} | 参数={json.dumps(args, ensure_ascii=False)} | output={output}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )

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
            messages.append(
                {
                    "role": "user",
                    "content": "<reminder>Update your todos to track progress.</reminder>",
                }
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

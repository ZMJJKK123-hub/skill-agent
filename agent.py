import json
import os

from config import client, MODEL, SYSTEM, logger
from tools import (
    TOOLS, TOOL_HANDLERS, task_manager, todo_manager, bg_manager,
    format_background_results, teammate_manager,
)
from protocol import inject_pending_requests, coordinator
from subagent import run_subagent
from compact import (
    micro_compact,
    auto_compact,
    handle_compact,
    estimate_tokens,
    TOKEN_THRESHOLD,
)


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
            return message.content

        # 执行工具，收集结果
        # ── Layer 3: compact 工具特殊处理（模型主动触发，最后执行）──
        used_todo = False
        compact_pending = False
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)

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
    首先 严禁动当前文件夹内的文件。你只能在当前目录下创建一个 demo 新文件夹，你产生和修改的所有文件只能在 demo 文件夹中进行。测试完成后删除 demo 文件夹与一切运行时残留（.team/.tasks/.transcripts/__pycache__/agent.log）。以此为规则，完成以下全功能测试任务：

## 阶段一：任务看板 + 规划系统（第 1/3/7 课）
1. 用 todo 建立 8 步计划，跟踪整个测试流程。
2. 用 task_create 创建 6 个任务，形成 3 层依赖 DAG：
   [1] Design schema（无依赖）
   [2] Build backend  calculator  （blocked_by 1）
   [3] Build frontend  CLI        （blocked_by 1）
   [4] Integration tests          （blocked_by 2,3）   ← 汇聚
   [5] Deploy README+report       （blocked_by 4）
   [6] Code review 安全审查        （blocked_by 4）     ← 并行分支
   用 task_list 确认 DAG 结构正确。

## 阶段二：自组织任务认领（第 11 课）
3. 用 spawn_teammate 创建三个队友：alice(developer)、bob(tester)、eve(reviewer)。
   不要用 send_to_teammate 指派任何任务——完全交给它们自主扫描看板认领。
4. 用 team_status 观察：三个队友从 idle 自动进入 working（自主认领）。
   验证关键行为：
   - 依赖阻塞：任务 4/5/6 在 1/2/3 完成前不可被认领（blocked）
   - 原子认领：同一个任务只可能被一个队友认领成功（另一个认领报错）
   - 依赖解锁：1 完成后 → 2/3 同时解锁；2/3 都完成后 → 4/6 解锁；4 完成后 → 5 解锁
   - 并行分叉与汇聚：2/3 并行、5/6 并行、4 等两者聚拢
5. 用 task_list 最终验证所有任务都有 owner 且全部 completed。

## 阶段三：团队协议（第 10 课）
6. 等队友全部完成自治任务后，对 alice 用 request_shutdown 发起关机握手（reason="任务完成"）。
   → 验证：若 alice 还有未提交写入，第一次被 REJECTED；无未提交则直接 APPROVED→安全退出。
7. 用 protocol_status 展示关机请求的状态流转，用 team_status 确认 alice 已 shutdown。
8. 故意用 respond_to_request 对一个已决议的请求再次审批 → 应返回 "already resolved"（状态守卫温和拦截，不崩溃）。
9. 故意用 respond_to_request 审批一个 shutdown 类型请求 → 应返回 "不是 plan 类型，shutdown 由系统自动处理"（角色守卫）。

## 阶段四：后台执行 + 技能 + 压缩（第 2/5/6/8 课）
10. 用 run_in_background 在 demo 下跑一条慢命令（如 pytest/长循环），确认收到 <background-results> 通知。
11. 用 load_skill 加载 git-workflow 或 testing 技能，确认技能内容注入。
12. 当上下文变长时调用 compact，确认压缩后仍能继续任务（身份重注入会保证队友不丢角色）。

## 阶段五：清理与汇总
13. 确认三个队友中未被协议的自动 shutdown（60s 无活自动退出）。
14. 用 task_list + team_status + protocol_status 汇总最终状态。
15. 删除 demo 文件夹；确认工作区只剩课程代码（agent/compact/config/protocol/subagent/tools + skills + requirements），无任何运行时残留。
16. 汇报以下验证结果表格：DAG 依赖✓、原子认领✓、依赖解锁✓、并行分叉汇聚✓、关机握手✓、状态守卫✓、角色守卫✓、后台执行✓、技能加载✓、自动退出✓、清理✓。
"""
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)

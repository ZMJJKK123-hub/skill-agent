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
            tools=TOOLS,
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
                coordinator.reset()  # 第 10 课：清空协议请求与写入登记
                logger.info("所有任务已完成，已自动清空 .tasks、todo、team config 和协议状态")
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
            output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
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
    task = """首先 严禁动当前文件夹内的文件，你只能在当前目录下创建一个 demo 新文件夹，你产生和修改的所有文件只能在 demo 文件夹中进行，测试完成后删除 demo 文件夹。以此为规则，完成第 10 课全功能测试任务。

## 阶段一：验证 4 个协议工具已注册
先用 protocol_status 查看请求列表（应为空或仅有历史记录），确认你能看到以下工具：
① request_shutdown  ② submit_plan  ③ respond_to_request  ④ protocol_status

## 阶段二：计划审批协议（队友 → 领导）
1. 用 spawn_teammate 创建 alice (coder)。给 alice 发一个高风险重构任务：重构 demo/auth_service.py（删除旧 API、改 token 格式、加回调），明确要求它必须先用 submit_plan 提交计划并等批准。
2. 等 alice 提交计划。当 <pending-requests> 出现 plan 请求时：
   → 检查它的 risk_level。如果是 high：
      用 respond_to_request 拒绝，reason 写"高风险，请拆分为低风险增量步骤"
      → 验证：alice 收到 REJECTED 后没有立即写代码，而是重新 submit_plan（风险降级）
   → 等 alice 第二次提交 medium/low 计划：
      用 respond_to_request 批准
      → 验证：alice 收到 APPROVED 后，才开始真正写文件（用 team_status 确认它从 idle 变 working 后才开始改文件）
3. 用 spawn_teammate 创建 bob (tester)。给 bob 发低风险任务：给 demo/auth_service.py 写单元测试。要求它也必须先 submit_plan。
   → 等 bob 提交计划，确认 risk_level 是 low → 直接批准
   → 验证：bob 拿到 APPROVED 后开始写 test 文件

## 阶段三：关机握手协议（领导 → 队友）
1. 等 alice 完成重构后，用 request_shutdown 给 alice 发起第一次关机（reason="任务完成，检查未提交写入"）。
   → 预期：因为 alice 还有未提交写入（写文件被自动登记在 AgentWriteTracker），第一次应被 REJECTED，alice 继续运行。
   → 用 protocol_status 验证该 shutdown 请求状态为 rejected，且 response 里有 uncommitted_writes 和文件清单。
2. 给 alice 发消息："请把剩余文件写完并确认完成"。
   → alice 完成一轮后写入登记自动 flush。
3. 第二次用 request_shutdown 给 alice 发起关机。
   → 预期：这次无未提交写入 → APPROVED → alice 状态变为 shutdown，线程安全退出。
   → 用 team_status 验证 alice 已 shutdown。

## 阶段四：状态守卫与角色守卫验证
1. 状态守卫：对已 APPROVED 的关闭请求，尝试再次 respond_to_request（或让代码路径再 respond）→ 应报 "already resolved"，不允许双重响应。
2. 角色守卫：尝试用 respond_to_request 去 approve 一个 shutdown 类型的请求 → 应被拒绝（提示"不是 plan 类型，shutdown 由系统自动处理"），不允许手动绕过。
3. 用 protocol_status 完整展示所有请求的状态流转：plan_b3e1a0b5 → rejected → plan_c3a430b9 → approved；shutdown_x1 → rejected → shutdown_x2 → approved。

## 阶段五：<pending-requests> 注入验证
1. 确认你在每轮开头可以看到 <pending-requests> 标签（含待审批 plan / 已决议结果）。
2. 确认 alice/bob 作为队友也能看到自己的 pending 请求（计划审批结果、关机结果）——它们靠这个才知道"批准了可以干"、"被拒了要改"。

## 阶段六：汇总与清理
1. 用 protocol_status + team_status 汇总：alice=shutdown、bob=idle、计划 x 个 rejected + y 个 approved、关机 x 个 rejected + y 个 approved。
2. 验证 demo/auth_service.py 与 demo/test_auth_service.py 存在且内容正确（alice 的 login_v2/logout_v2 已加入、bob 的测试文件覆盖新 API）。
3. 测试全部完成后：删除 demo 文件夹（含 __pycache__/.pytest_cache 缓存），确认工作区只剩课程代码，不留任何测试产物。
"""
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)

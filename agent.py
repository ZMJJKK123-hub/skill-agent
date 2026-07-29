import json
import os

from config import client, MODEL, SYSTEM, logger
from tools import TOOLS, TOOL_HANDLERS
from subagent import run_subagent


# ---------- 接线：注册 task handler（打破循环依赖）----------
# tools.py 不导入 subagent.py（避免循环依赖），
# task 工具的定义在 TOOLS 列表里，但 handler 在此接线。
TOOL_HANDLERS["task"] = lambda **kw: run_subagent(kw["prompt"])


def agent_loop(messages: list) -> str:
    rounds_since_todo = 0
    while True:
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
            logger.info(f"循环结束，最终回复:\n{message.content}")
            return message.content

        # 执行工具，收集结果
        used_todo = False
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
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
    task = """在当前目录创建一个app文件夹完成完整的待办事项 REST API 项目，要求：

    1. 用 Python + Flask 实现，文件名 app.py 不要修改当前目录下任何文件 只能修改app文件夹内的东西
    2. 实现以下接口：
    - GET /api/todos — 返回所有待办
    - POST /api/todos — 创建新待办（body: {"title": "...", "done": false}）
    - PUT /api/todos/<id> — 更新待办状态
    - DELETE /api/todos/<id> — 删除待办
    3. 数据存在内存列表里，不需要数据库
    4. 创建 requirements.txt 写入 flask 依赖
    5. 启动服务，用 curl 测试全部 4 个接口
    6. 加载 testing 技能，按规范写一个 test_app.py 测试文件
    7. 运行测试，确保全部通过
    8. 派发一个子 Agent 做代码审查，检查是否有 bug 或安全问题
    9. 根据子 Agent 的审查意见修复发现的问题
    10. 最终交付：app.py + requirements.txt + test_app.py，全部测试通过

    注意：启动 Flask 服务必须用组合命令（后台启动 → 等待 → curl 测试 → taskkill），禁止单独执行 flask run。
    """
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)
import json

from .config import client, MODEL, SUBAGENT_SYSTEM, MAX_SUBAGENT_TURNS, logger
from .tools import TOOLS, TOOL_HANDLERS
from .skillcheck import init_per_loop, run_loop_check


# ---------- Subagent 执行函数 ----------
def extract_text(message) -> str:
    """从响应消息中提取纯文本，丢弃工具调用块。"""
    parts = []
    if message.content:
        parts.append(message.content)
    return "\n".join(parts) if parts else "(subagent produced no text output)"


def run_subagent(prompt: str) -> str:
    """在隔离上下文中执行子任务，仅返回最终文本。

    子 Agent 拥有除 task 外的所有工具（防递归），
    用独立的 sub_messages 启动——完全干净的上下文。
    子 Agent 的消息历史直接丢弃，不污染父上下文。
    """
    sub_messages = [{"role": "user", "content": prompt}]

    # 子 Agent 可用的工具：排除 task（防递归）+ 主 agent 独占的重工具
    # run_game_test_server / read_game_test_log：GameTest 进程重且会互踩 run 目录
    excluded = {"task", "run_game_test_server", "read_game_test_log"}
    sub_tools = [t for t in TOOLS if t["function"]["name"] not in excluded]

    logger.info(f"=== Subagent 启动 | prompt={prompt[:200]} ===")

    response = None
    for turn in range(MAX_SUBAGENT_TURNS):
        logger.info(f"--- Subagent 第 {turn + 1} 轮 ---")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SUBAGENT_SYSTEM}] + sub_messages,
            tools=sub_tools,
            max_tokens=8000,
        )

        choice = response.choices[0]
        message = choice.message

        # 打印子 Agent 思考过程（不进 sub_messages）
        reasoning = getattr(message, "reasoning_content", None)
        if reasoning:
            print(f"\n[subagent 思考] {reasoning}")
            logger.info(f"subagent reasoning:\n{reasoning}")

        sub_messages.append(message.to_dict())
        if choice.finish_reason != "tool_calls":
            if not run_loop_check("subagent", message.content, sub_messages):
                continue
        logger.info(f"subagent finish_reason={choice.finish_reason}")

        # 子 Agent 决定不再调工具 → 任务完成
        if choice.finish_reason != "tool_calls":
            break

        # 执行工具，收集结果
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            handler = TOOL_HANDLERS.get(tc.function.name)
            output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
            logger.info(f"subagent 工具调用: {tc.function.name}")
            # 调试需要：完整输出写入 run.log，不截断
            print(f"[subagent:{tc.function.name}] {output}")
            sub_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )

    # ★ 关键：只提取最终文本，sub_messages 整个丢弃
    final_text = extract_text(message) if response else "(subagent produced no text output)"
    logger.info(f"=== Subagent 结束 | 最终文本={final_text[:200]} ===")
    return final_text
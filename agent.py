import json
import os

from config import client, MODEL, SYSTEM, logger
from tools import TOOLS, TOOL_HANDLERS
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
            logger.info(f"循环结束，最终回复:\n{message.content}")
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
    task = """
                在当前目录创建一个 `inventory` 文件夹，完成一个完整的库存管理系统 CLI 项目，要求：
            1. 用 Python 实现，核心文件 `inventory/cli.py`，不要修改当前目录下任何文件，只能修改 inventory 文件夹内的东西
            2. 实现以下 CLI 命令（用 argparse）：
            - `python -m inventory.cli add --name "商品名" --qty 10 --price 9.99` — 添加商品
            - `python -m inventory.cli list` — 列出所有商品（表格格式）
            - `python -m inventory.cli update <id> --qty 20` — 更新数量
            - `python -m inventory.cli delete <id>` — 删除商品
            - `python -m inventory.cli search --name "关键词"` — 按名称搜索
            - `python -m inventory.cli stats` — 统计：总商品数、总价值、平均价格
            3. 数据存在 `inventory/data.json`（JSON 文件持久化，非内存）
            4. 创建 `inventory/__init__.py` 使其成为可导入的包
            5. 创建 `inventory/requirements.txt`（如有第三方依赖）
            6. 加载 testing 技能，按规范写 `inventory/test_cli.py` 测试文件，要求：
            - 单元测试覆盖每个命令
            - 每个测试函数至少 3 个用例（正常、边界、异常）
            - 用 tmp_path fixture 隔离测试数据
            7. 运行测试，确保全部通过
            8. 加载 git-workflow 技能，在 inventory 文件夹内初始化 git 仓库并提交代码
            9. 派发一个子 Agent 做代码审查，检查：
            - 边界条件处理（空列表、不存在的 ID、负数数量）
            - 数据持久化的并发安全
            - CLI 参数校验完整性
            - 错误信息是否友好
            10. 根据子 Agent 审查意见修复所有发现的问题
            11. 再次运行测试确保修复后全部通过
            12. 最终交付：cli.py + __init__.py + data.json + test_cli.py + requirements.txt，全部测试通过

            注意：
            - 启动测试用 pytest，禁止单独运行 python -m inventory.cli 交互式等待
            - 所有文件操作只在 inventory 文件夹内
            - 上下文变长时可以主动调用 compact 工具压缩对话
            """
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)
import json
import os

from config import client, MODEL, SYSTEM, logger
from tools import TOOLS, TOOL_HANDLERS, task_manager, todo_manager
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
            # ★ 任务全部完成时，自动清空 .tasks 和 todo（为下次运行保持干净状态）
            if task_manager.all_completed():
                task_manager.clear()
                todo_manager.todos = []
                logger.info("所有任务已完成，已自动清空 .tasks 和 todo")
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
    在当前目录创建一个 `blog` 文件夹，完成一个完整的博客系统项目，要求：

    1. 用 Python 实现，不要修改当前目录下任何文件，只能修改 blog 文件夹内的东西
    2. 项目结构：
       - blog/__init__.py（包初始化）
       - blog/models.py（数据模型：Post、Author、Comment）
       - blog/storage.py（JSON 文件持久化层）
       - blog/api.py（API 层：增删改查逻辑）
       - blog/cli.py（CLI 入口，用 argparse）
       - blog/requirements.txt（依赖）
       - blog/test_models.py（模型测试）
       - blog/test_storage.py（存储层测试）
       - blog/test_api.py（API 测试）
       - blog/test_cli.py（CLI 集成测试）
       - blog/README.md（项目文档）

    3. 数据模型（models.py）：
       - Post: id, title, content, author_id, created_at, updated_at, tags(list), status(draft/published)
       - Author: id, name, email, bio
       - Comment: id, post_id, author_name, content, created_at
       - 实现模型的 __repr__、to_dict、from_dict 方法

    4. 存储层（storage.py）：
       - JSON 文件持久化（blog/data.json）
       - 实现泛型 CRUD：save_all、load_all、find_by_id、delete_by_id
       - 支持 Post、Author、Comment 三种实体的独立存储
       - 写操作要线程安全（用文件锁或原子写入）

    5. API 层（api.py）：
       - create_post(title, content, author_id, tags)
       - get_post(post_id)
       - list_posts(status_filter=None, tag_filter=None)
       - update_post(post_id, **fields)
       - delete_post(post_id)
       - publish_post(post_id)  # draft → published
       - create_author(name, email, bio)
       - get_author(author_id)
       - list_authors()
       - add_comment(post_id, author_name, content)
       - list_comments(post_id)
       - 每个方法返回 (success: bool, data, message: str) 元组

    6. CLI（cli.py）：
       - python -m blog.cli post create --title "标题" --content "内容" --author 1 --tags "tag1,tag2"
       - python -m blog.cli post list [--status published] [--tag "xxx"]
       - python -m blog.cli post get <id>
       - python -m blog.cli post update <id> [--title "新标题"] [--content "新内容"]
       - python -m blog.cli post delete <id>
       - python -m blog.cli post publish <id>
       - python -m blog.cli author create --name "作者名" --email "a@b.com" [--bio "简介"]
       - python -m blog.cli author list
       - python -m blog.cli comment add --post 1 --author "评论者" --content "评论内容"
       - python -m blog.cli comment list <post_id>
       - python -m blog.cli stats  # 统计：总文章数、已发布数、总评论数、作者数
       - 输出用表格格式，错误用红色标记

    7. 加载 testing 技能，按规范写 4 个测试文件：
       - test_models.py：模型创建、序列化、反序列化、字段校验
       - test_storage.py：CRUD 全覆盖、并发写入、文件不存在处理
       - test_api.py：每个 API 方法（正常、边界、异常），publish 状态流转
       - test_cli.py：CLI 命令集成测试，用 subprocess 调用
       - 每个测试函数至少 3 个用例（正常、边界、异常）
       - 用 tmp_path fixture 隔离测试数据
       - 总测试用例数不少于 40 个

    8. 派发一个子 Agent 做代码审查，检查：
       - 边界条件（空列表、不存在的 ID、重复创建、非法 status）
       - 数据持久化的并发安全
       - CLI 参数校验完整性
       - API 返回值一致性
       - 错误信息是否友好
       - 代码风格一致性

    9. 派发一个子 Agent 做安全扫描，检查：
       - JSON 注入风险（恶意构造的 title/content）
       - 路径遍历（文件名是否可被注入 ../）
       - 邮箱格式校验
       - 大输入 DoS 防护（超长 content）
       - 返回安全评估报告

    10. 根据两个子 Agent 的审查意见修复所有发现的问题

    11. 加载 git-workflow 技能，在 blog 文件夹内初始化 git 仓库并提交代码：
        - 初始化仓库
        - 创建 .gitignore（忽略 data.json、__pycache__、.pytest_cache）
        - 分阶段提交（models → storage → api → cli → tests → docs）

    12. 最终交付：所有文件 + 全部测试通过 + git 仓库干净

    注意：
    - 启动测试用 pytest，禁止单独运行 python -m blog.cli 交互式等待
    - 所有文件操作只在 blog 文件夹内
    - 上下文变长时可以主动调用 compact 工具压缩对话
    - 这个任务有 12 步，务必用 todo 工具跟踪进度，每完成一步就更新状态
    - 步骤间有依赖关系：models → storage → api → cli → tests，可以用 task 系列工具管理 DAG
    """
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)
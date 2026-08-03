"""会话入口：为每个用户的 MOD 生成任务启动一个独立子进程。

原理：
  服务器(server.py)收到用户的生成请求后，为这个会话单独启动一个
  Python 子进程，cwd 切到该用户的独立 mod 目录，然后调用核心的
  agent_loop() 跑完整的 12 课 agent。

  为什么用子进程而不是线程？
  - 现有 agent 的 task_manager / teammate_manager / worktree_manager
    都是模块级全局单例，WORKDIR = Path.cwd() 是进程级的。
    单机跑没问题；但网站 = 多用户并发，如果都跑在同一个进程里，
    两个用户会抢同一个 .tasks/、写进同一个目录。
  - 每会话一个子进程 = 每个进程有自己独立的 cwd 和全局单例，
    天然实现用户间隔离，核心代码一字不用改。

用法（由 server.py 调用）：
  python run_task.py <session_dir> <api_key> <task_prompt>
"""

import os
import sys
from pathlib import Path

# 重构：把项目根加入 sys.path，使 core 包可直接导入（与 cwd 无关）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    # 参数：会话目录（独立 mod 工作区）、用户自己的 API Key、任务提示词
    if len(sys.argv) < 4:
        print("Usage: python run_task.py <session_dir> <api_key> <task_prompt>")
        return 1

    session_dir = Path(sys.argv[1]).resolve()
    api_key = sys.argv[2]
    task_prompt = sys.argv[3]

    # 1. 确保会话目录存在并切换进去
    #    cwd 决定了 config.WORKDIR = Path.cwd()，也就是该用户 mod 生成的位置
    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))
    print(f"[run_task] 工作目录 => {session_dir}", flush=True)

    # 2. 注入用户自己的 API Key（只在用户自己机器/会话里生效，不落盘）
    os.environ["DEEPSEEK_API_KEY"] = api_key

    # 3. 延迟导入核心 agent（此时 cwd 已切好，config.WORKDIR 才会正确）
    #    重构后从 core 包导入
    try:
        from core.agent import agent_loop
    except Exception as e:
        print(f"[run_task] 导入 agent 失败: {e}", flush=True)
        return 1

    # 4. 跑完整 agent 循环
    messages = [{"role": "user", "content": task_prompt}]
    final = agent_loop(messages)
    print(f"[run_task] 完成，最终回复:\n{final}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
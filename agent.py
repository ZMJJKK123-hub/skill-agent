from openai import OpenAI
import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# ── 强制 stdout/stderr 走 UTF-8 ──────────────────────
# Windows 终端默认 GBK，print emoji/中文会崩。
# 在导入其他东西之前先 reconfigure，彻底解决 UnicodeEncodeError。
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ---------- 日志系统 ----------
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("agent")

# ---------- 配置 ----------
MODEL = "deepseek-v4-pro"
SYSTEM = r"""你是一个具备规划能力的编码助手，可以执行 bash 命令。
对于多步骤任务，必须始终（ALWAYS）先使用 todo 工具创建计划——
将任务拆解为可验证的子步骤，然后在工作时逐个更新条目状态。
只有验证结果后才标记为 completed。
同一时间只能有一个 in_progress 项目。

重要：不要用 bash 启动会长期运行的服务器进程（如 npm start、node server.js、python -m http.server），
这会导致命令永久阻塞。验证服务请用"后台启动 → curl 测试端口 → 终止进程"的方式，
或直接用 read_file 检查关键代码是否正确，避免命令阻塞。

重要：写入文件内容时，必须使用 write_file 工具，不要用 bash 重定向（如 `echo > file`、`python x.py > out.txt`）。
因为 bash 重定向在 Windows 上走 GBK 编码，遇到 emoji 或特殊字符会丢失成问号；
write_file 工具强制 UTF-8，能保证中文和 emoji 都不丢。如需保存命令输出到文件，先用 bash 拿到输出，
再用 write_file 写入。

重要：你运行在 Windows cmd 上，必须使用 Windows 命令语法，禁止使用 Linux 专属语法：
- 创建目录用 `mkdir 文件夹名`，禁止用 `mkdir -p`（cmd 不识别 -p，会创建名为 -p 的文件夹）
- 列目录用 `dir`，禁止用 `ls`
- 查看文件内容用 `type 文件名`，禁止用 `cat`
- 复制文件用 `copy` 或 `xcopy`，禁止用 `cp`
- 删除文件用 `del 文件名`，删除文件夹用 `rd /s /q 文件夹名`，禁止用 `rm -rf`
- 查找文件用 `where` 或 `dir /s /b`，禁止用 `find` / `which`
- 路径分隔符用反斜杠 `\` 或正斜杠 `/` 都行，但不要在同一命令里混用

每个子步骤应当是可独立验证的原子任务，粒度细化到单个文件或单个功能点。"""

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

# ---------- 路径安全沙箱 ----------
WORKDIR = Path.cwd()

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path

# ---------- 工具函数实现 ----------
def run_bash(command: str) -> str:
    """执行命令并返回 stdout/stderr，含基本安全防护（Windows）"""
    dangerous = [
        "del /f /s", "rd /s /q", "format",
        "diskpart", "reg delete", "shutdown",
    ]
    if any(d in command.lower() for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command, shell=True, cwd=os.getcwd(),
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


# ---------- TodoManager（叠加的规划系统，不改动 Agent Loop 核心）----------
class TodoManager:
    def __init__(self):
        self.todos: list[dict] = []

    def update(self, items: list[dict]) -> str:
        """更新待办列表。核心约束：同一时间只允许一个 in_progress。"""
        logger.info(f"TodoManager.update 被调用，items={json.dumps(items, ensure_ascii=False)}")
        in_progress = [i for i in items if i["status"] == "in_progress"]
        if len(in_progress) > 1:
            return "Error: Only one item can be in_progress at a time."
        self.todos = items
        return self.render()

    def render(self) -> str:
        """渲染待办清单，让模型在每次调用后看到全局进度。"""
        if not self.todos:
            return "(no todos)"
        icons = {"pending": "☐", "in_progress": "▶", "completed": "✓"}
        done = sum(1 for i in self.todos if i["status"] == "completed")
        total = len(self.todos)
        header = f"📋 待办清单 ({done}/{total} 完成)"
        lines = [header]
        for idx, item in enumerate(self.todos, 1):
            icon = icons.get(item["status"], "?")
            lines.append(f"  [{idx}] {icon} {item['content']}")
        rendered = "\n".join(lines)
        logger.info(f"TodoManager.render:\n{rendered}")
        return rendered

todo_manager = TodoManager()


# ---------- 工具调度映射 ----------
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"],
                                        kw["new_text"]),
    "todo":       lambda **kw: todo_manager.update(kw["items"]),
}

# ---------- 工具定义（DeepSeek / OpenAI 格式）----------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace exact text in file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo",
            "description": "Update the task plan. Each item has 'content' (string) and 'status' (pending/in_progress/completed). Use this to track progress on multi-step tasks. Only ONE item should be in_progress at a time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["content", "status"],
                        },
                    },
                },
                "required": ["items"],
            },
        },
    },
]


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
    messages = [{"role": "user", "content": "在当前目录下创建一个子文件夹叫 demo，然后在里面创建一个 Python 文件 hello.py，内容是打印当前时间和一句问候语。运行这个文件确认能输出。最后把运行结果写进 demo 目录下的 result.txt 文件。"}]
    final_response = agent_loop(messages)
    print(final_response)
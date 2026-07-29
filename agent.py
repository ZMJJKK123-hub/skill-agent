from openai import OpenAI
import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv
import yaml

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

重要：禁止把服务器启动命令（npm start、node server.js、python -m http.server、flask run 等）
单独执行——这会触发 30s 超时被强杀。
验证 HTTP 服务的唯一允许方式是用一条组合命令完成
「后台启动 → 等待 → 测试 → 杀进程」：

  start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & taskkill /f /im node.exe

逐段解释：
- start /b cmd /c "..."：后台启动服务，输出重定向到 server.log，不阻塞当前命令
- timeout /t 3 /nobreak >nul：等 3 秒让服务起好
- curl -s http://localhost:PORT/...：发请求测接口
- taskkill /f /im node.exe：测完立刻杀掉 node 进程（Python 服务换成 python.exe）

如果用 Python 启动的服务，把 node.exe 换成 python.exe；
如果端口不是 3000，按实际改。整条命令用 & 串联，一次性执行完。

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

对于需要大量探索/分析但中间过程不需要保留的子任务，使用 task 工具派发给子 Agent。
子 Agent 在隔离上下文中执行，只返回最终摘要，不污染父上下文。

每个子步骤应当是可独立验证的原子任务，粒度细化到单个文件或单个功能点。"""

# ---------- Subagent 系统（第 4 课：隔离上下文的子任务派发）----------
MAX_SUBAGENT_TURNS = 10  # 硬上限，防止子 Agent 失控死循环

SUBAGENT_SYSTEM = """You are a focused research and analysis agent.
Your job is to complete the specific task given to you, then provide
a clear, concise summary of your findings.
Guidelines:
- Stay focused on the given task
- Be thorough but efficient
- End with a clear summary of findings
- Do not ask for clarification — work with what you have
- You are running on Windows cmd. Use Windows command syntax (dir, type, copy, taskkill).
- Do not start long-running servers directly; use the combined
  "start /b ... & timeout /t 3 ... & curl ... & taskkill" pattern.
"""

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
    """执行命令并返回 stdout/stderr，含基本安全防护（Windows）。

    用 Popen + 手动 taskkill /f /t /pid 杀进程树，避免 subprocess.run 在
    shell=True 下 timeout 死锁（cmd.exe 被杀但孙子进程 node.exe 持有管道
    导致 communicate 永不返回）。
    """
    dangerous = [
        "del /f /s", "rd /s /q", "format",
        "diskpart", "reg delete", "shutdown",
    ]
    if any(d in command.lower() for d in dangerous):
        return "Error: Dangerous command blocked"
    proc = subprocess.Popen(
        command, shell=True, cwd=os.getcwd(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )
    try:
        out, _ = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        subprocess.run(
            f"taskkill /f /t /pid {proc.pid}",
            shell=True, capture_output=True,
        )
        try:
            out, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            out = ""
        return ("Error: Timeout (30s) — 进程树已被强杀。\n"
                "如果你在启动服务器（node server.js / npm start / python -m http.server），"
                "禁止单独执行启动命令。必须用一条组合命令完成"
                "「后台启动 → 等待 → 测试 → 杀进程」：\n"
                "  start /b cmd /c \"node server.js > server.log 2>&1\" & "
                "timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & "
                "taskkill /f /im node.exe")
    out = (out or "").strip()
    return out[:50000] if out else "(no output)"


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


# ---------- SkillLoader（第 5 课：两层知识注入）----------
class SkillLoader:
    """扫描 skills/ 目录，提供目录描述和按需加载。

    第一层：get_descriptions() 返回技能目录（名称+描述），拼接到 system prompt。
    第二层：get_content(name) 返回完整技能内容，通过 load_skill 工具按需注入。
    """

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self.skills = {}  # name → {description, content, path}
        self._scan()
        logger.info(
            f"SkillLoader 初始化 | 扫描到 {len(self.skills)} 个技能: "
            f"{list(self.skills.keys())}"
        )

    def _scan(self):
        """扫描所有 skills/*/SKILL.md，解析 frontmatter。"""
        if not os.path.isdir(self.skills_dir):
            logger.info(f"SkillLoader: 目录 {self.skills_dir} 不存在，跳过扫描")
            return
        for entry in sorted(os.listdir(self.skills_dir)):
            skill_path = os.path.join(self.skills_dir, entry, "SKILL.md")
            if not os.path.isfile(skill_path):
                continue
            with open(skill_path, "r", encoding="utf-8") as f:
                raw = f.read()

            meta, body = self._parse_frontmatter(raw)
            name = meta.get("name", entry)
            description = meta.get("description", "")

            self.skills[name] = {
                "description": description,
                "content": body.strip(),
                "path": skill_path,
            }
            logger.info(
                f"SkillLoader 扫描技能: {entry} | name={name} | "
                f"desc={description} | content_len={len(body.strip())}"
            )

    @staticmethod
    def _parse_frontmatter(raw: str) -> tuple[dict, str]:
        """分离 YAML frontmatter 和 markdown 正文。"""
        if not raw.startswith("---"):
            return {}, raw
        parts = raw.split("---", 2)
        if len(parts) < 3:
            return {}, raw
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2]
        return meta, body

    def get_descriptions(self) -> str:
        """生成 system prompt 中的技能目录（第一层注入）。"""
        if not self.skills:
            return ""
        lines = ["Available skills (use load_skill to access):"]
        for name, info in self.skills.items():
            lines.append(f"  - {name}: {info['description']}")
        result = "\n".join(lines)
        logger.info(f"SkillLoader.get_descriptions 生成技能目录:\n{result}")
        return result

    def get_content(self, skill_name: str) -> str:
        """返回完整技能内容（第二层注入），用 XML 标签包裹。"""
        if skill_name not in self.skills:
            available = ", ".join(self.skills.keys())
            logger.info(
                f"SkillLoader.get_content: 技能 '{skill_name}' 未找到 | "
                f"可用: {available}"
            )
            return f"Error: Skill '{skill_name}' not found. Available: {available}"
        content = self.skills[skill_name]["content"]
        result = f'<skill name="{skill_name}">\n{content}\n</skill>'
        logger.info(
            f"SkillLoader.get_content: 加载技能 '{skill_name}' | "
            f"{len(content)} 字符"
        )
        return result


skill_loader = SkillLoader("skills")

# 第一层注入：把技能目录拼接到 system prompt
SYSTEM += (
    "\n\n" + skill_loader.get_descriptions() +
    "\n\nWhen a task involves a specific domain (testing, git, security, etc.), "
    "use the load_skill tool to load the relevant guidelines before proceeding."
)


# ---------- 工具调度映射 ----------
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"],
                                        kw["new_text"]),
    "todo":       lambda **kw: todo_manager.update(kw["items"]),
    "task":       lambda **kw: run_subagent(kw["prompt"]),
    "load_skill": lambda **kw: skill_loader.get_content(kw["skill_name"]),
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
    {
        "type": "function",
        "function": {
            "name": "task",
            "description": "Run a subtask in an isolated context. Use this for research, analysis, or any work whose intermediate output the parent does not need to see. Returns only the final text summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The task description for the subagent",
                    }
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load domain-specific guidelines and best practices. Use this when the current task involves a specific domain like testing, git workflow, code review, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill to load",
                    }
                },
                "required": ["skill_name"],
            },
        },
    },
]


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

    # 子 Agent 可用的工具：排除 task（防递归）
    sub_tools = [t for t in TOOLS if t["function"]["name"] != "task"]

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
        logger.info(f"subagent finish_reason={choice.finish_reason}")

        # 子 Agent 决定不再调工具 → 任务完成
        if choice.finish_reason != "tool_calls":
            break

        # 执行工具，收集结果
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            handler = TOOL_HANDLERS.get(tc.function.name)
            output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
            logger.info(f"subagent 工具调用: {tc.function.name} | output={output[:200]}")
            print(f"[subagent:{tc.function.name}] {output[:200]}")
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
    task ="阅读2025013613-李义鑫文件夹内容 总结这个文件夹干了什么"
    messages = [{"role": "user", "content": task}]
    final_response = agent_loop(messages)
    print(final_response)
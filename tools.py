import json
import os
import subprocess
import yaml

import config
from config import logger, safe_path

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
config.SYSTEM += (
    "\n\n" + skill_loader.get_descriptions() +
    "\n\nWhen a task involves a specific domain (testing, git, security, etc.), "
    "use the load_skill tool to load the relevant guidelines before proceeding."
)


# ---------- 工具调度映射 ----------
# 注意：task handler 不在此注册，由 agent.py 接线（打破循环依赖）
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"],
                                        kw["new_text"]),
    "todo":       lambda **kw: todo_manager.update(kw["items"]),
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
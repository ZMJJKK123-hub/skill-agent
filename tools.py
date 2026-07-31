import json
import os
import subprocess
import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional

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
        # 致命：taskkill /im 会杀掉 Agent 自身进程（python.exe）
        "taskkill /f /im python.exe",
        "taskkill /f /im node.exe",
        "taskkill /f /im cmd.exe",
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
                "for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a\n"
                "注意：禁止用 taskkill /f /im python.exe，会杀掉 Agent 自身。")
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
        header = f"📋 Todo List ({done}/{total} completed)"
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


# ---------- TaskManager（第 7 课：文件级持久化的任务图 DAG）----------
class TaskManager:
    """文件即数据库的任务管理系统。

    每个任务存为一个独立 JSON 文件（.tasks/task_N.json），含 5 个字段：
    id, subject, status, blockedBy, owner。
    完成任务时自动清除下游任务的依赖（被动解锁机制）。
    """

    def __init__(self, task_dir: str = ".tasks"):
        self.task_dir = task_dir
        os.makedirs(task_dir, exist_ok=True)
        self._next_id = self._compute_next_id()
        logger.info(
            f"TaskManager 初始化 | task_dir={task_dir} | "
            f"next_id={self._next_id} | 现有任务数={len(self._all_task_ids())}"
        )

    def _task_path(self, task_id: int) -> str:
        return os.path.join(self.task_dir, f"task_{task_id}.json")

    def _read_task(self, task_id: int) -> dict | None:
        path = self._task_path(task_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_task(self, task: dict):
        path = self._task_path(task["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, ensure_ascii=False)

    def _compute_next_id(self) -> int:
        existing = self._all_task_ids()
        return max(existing, default=0) + 1

    def _all_task_ids(self) -> list[int]:
        ids = []
        for fname in os.listdir(self.task_dir):
            if fname.startswith("task_") and fname.endswith(".json"):
                try:
                    ids.append(int(fname[5:-5]))
                except ValueError:
                    continue
        return sorted(ids)

    def create(self, subject: str, blocked_by: list[int] | None = None) -> dict:
        """创建一个新任务，可选指定依赖。校验依赖任务必须存在。"""
        blocked_by = blocked_by or []
        logger.info(
            f"TaskManager.create | subject={subject} | blocked_by={blocked_by}"
        )
        task = {
            "id": self._next_id,
            "subject": subject,
            "status": "pending",
            "blockedBy": blocked_by,
            "owner": None,
        }
        # 校验依赖的任务确实存在
        for dep_id in task["blockedBy"]:
            if self._read_task(dep_id) is None:
                error_msg = f"Dependency task {dep_id} does not exist"
                logger.warning(f"TaskManager.create 失败: {error_msg}")
                return {"error": error_msg}
        self._write_task(task)
        self._next_id += 1
        logger.info(f"TaskManager.create 成功 | task={json.dumps(task, ensure_ascii=False)}")
        return task

    def update(self, task_id: int, status: str, owner: str | None = None) -> dict:
        """更新任务状态。当任务完成时自动解锁后续任务。"""
        logger.info(
            f"TaskManager.update | task_id={task_id} | status={status} | owner={owner}"
        )
        task = self._read_task(task_id)
        if task is None:
            error_msg = f"Task {task_id} not found"
            logger.warning(f"TaskManager.update 失败: {error_msg}")
            return {"error": error_msg}

        # 不能把被阻塞的任务直接设为 in_progress
        if status == "in_progress" and task["blockedBy"]:
            unfinished = []
            for dep_id in task["blockedBy"]:
                dep = self._read_task(dep_id)
                if dep is None:
                    unfinished.append(dep_id)
                elif dep["status"] != "completed":
                    unfinished.append(dep_id)
            if unfinished:
                error_msg = f"Task {task_id} is blocked by unfinished tasks: {unfinished}"
                logger.warning(f"TaskManager.update 失败: {error_msg}")
                return {"error": error_msg}

        task["status"] = status
        task["owner"] = owner
        self._write_task(task)
        logger.info(f"TaskManager.update 成功 | task={json.dumps(task, ensure_ascii=False)}")

        # ★ 核心：完成时自动清除下游任务的依赖
        if status == "completed":
            self._clear_dependency(task_id)

        return task

    def _clear_dependency(self, completed_id: int):
        """从所有下游任务的 blockedBy 中移除已完成的任务 ID。"""
        logger.info(f"TaskManager._clear_dependency | completed_id={completed_id}")
        cleared = []
        for tid in self._all_task_ids():
            downstream = self._read_task(tid)
            if downstream and completed_id in downstream["blockedBy"]:
                downstream["blockedBy"].remove(completed_id)
                self._write_task(downstream)
                cleared.append(tid)
                logger.info(
                    f"  → 解锁下游 task_{tid}: blockedBy 移除 {completed_id}，"
                    f"剩余={downstream['blockedBy']}"
                )
        if not cleared:
            logger.info(f"  → 无下游任务需要解锁")

    def list_tasks(self, status_filter: str | None = None) -> list[dict]:
        """列出所有任务，可按状态过滤。"""
        tasks = []
        for tid in self._all_task_ids():
            task = self._read_task(tid)
            if task and (status_filter is None or task["status"] == status_filter):
                tasks.append(task)
        logger.info(
            f"TaskManager.list_tasks | filter={status_filter} | 返回 {len(tasks)} 个任务"
        )
        return tasks

    def get_task(self, task_id: int) -> dict:
        """获取单个任务的详情。"""
        task = self._read_task(task_id)
        if task is None:
            error_msg = f"Task {task_id} not found"
            logger.warning(f"TaskManager.get_task 失败: {error_msg}")
            return {"error": error_msg}
        logger.info(f"TaskManager.get_task | task_id={task_id} | 返回 task")
        return task

    def get_actionable(self) -> list[dict]:
        """获取所有可以立即执行的任务（pending + blockedBy 为空）。"""
        return [
            t for t in self.list_tasks()
            if t["status"] == "pending" and not t["blockedBy"]
        ]

    def render(self) -> str:
        """渲染任务图全景，供模型快速了解全局状态。"""
        tasks = self.list_tasks()
        if not tasks:
            return "(no tasks)"
        icons = {"pending": "☐", "in_progress": "▶", "completed": "✓"}
        lines = []
        for t in tasks:
            icon = icons.get(t["status"], "?")
            blocked = f" [blocked by {t['blockedBy']}]" if t["blockedBy"] else ""
            owner = f" ({t['owner']})" if t["owner"] else ""
            lines.append(f"  {icon} #{t['id']} {t['subject']}{blocked}{owner}")
        return "\n".join(lines)

    def all_completed(self) -> bool:
        """检查是否所有任务都完成了（或没有任务）。"""
        tasks = self.list_tasks()
        if not tasks:
            return True
        return all(t["status"] == "completed" for t in tasks)

    def clear(self) -> dict:
        """清空所有任务文件，重置 ID 计数器。"""
        cleared = 0
        for tid in self._all_task_ids():
            path = self._task_path(tid)
            os.remove(path)
            cleared += 1
        self._next_id = 1
        logger.info(f"TaskManager.clear | 已清空 {cleared} 个任务文件")
        return {"cleared": cleared, "next_id": self._next_id}


task_manager = TaskManager()


# ---------- BackgroundManager（第 8 课：异步后台执行 + 通知队列）----------
@dataclass
class BackgroundTask:
    """后台任务数据结构。status: running | completed | failed"""
    task_id: str
    command: str
    status: str = "running"
    result: Optional[str] = None


class BackgroundManager:
    """后台任务管理器。慢操作丢守护线程，主循环不阻塞。

    线程安全：tasks 字典用 lock 保护，通知用 queue.Queue（自带线程安全）。
    主循环每轮开头 drain_notifications()，把完成的结果注入为 user 消息。
    daemon=True 保证主进程退出时自动清理后台线程，无僵尸进程。
    """
    def __init__(self):
        self.tasks: dict[str, BackgroundTask] = {}
        self.notification_queue: queue.Queue = queue.Queue()
        self.lock = threading.Lock()

    def run(self, command: str) -> str:
        """启动后台任务，立即返回 task_id。调用方不阻塞。"""
        # 复用 run_bash 的危险命令检查
        dangerous = [
            "del /f /s", "rd /s /q", "format",
            "diskpart", "reg delete", "shutdown",
            "taskkill /f /im python.exe",
            "taskkill /f /im node.exe",
            "taskkill /f /im cmd.exe",
        ]
        if any(d in command.lower() for d in dangerous):
            return "Error: Dangerous command blocked"

        task_id = f"bg_{len(self.tasks)}_{int(time.time())}"
        task = BackgroundTask(task_id=task_id, command=command)
        with self.lock:
            self.tasks[task_id] = task

        thread = threading.Thread(
            target=self._execute,
            args=(task_id, command),
            daemon=True,
        )
        thread.start()
        logger.info(f"BackgroundManager.run | task_id={task_id} | command={command}")
        return task_id

    def _execute(self, task_id: str, command: str):
        """在守护线程里跑子进程。Windows 适配：Popen + taskkill，不用 subprocess.run。"""
        proc = subprocess.Popen(
            command, shell=True, cwd=os.getcwd(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        try:
            out, _ = proc.communicate(timeout=600)
            result = (out or "").strip()[:50000] or "(no output)"
            status = "completed"
        except subprocess.TimeoutExpired:
            subprocess.run(
                f"taskkill /f /t /pid {proc.pid}",
                shell=True, capture_output=True,
            )
            try:
                proc.communicate(timeout=5)
            except:
                pass
            result = "Error: Background task timed out (600s)"
            status = "failed"
        except Exception as e:
            result = f"Error: {e}"
            status = "failed"

        # 更新任务状态
        with self.lock:
            self.tasks[task_id].status = status
            self.tasks[task_id].result = result

        # 通知主线程
        self.notification_queue.put({
            "task_id": task_id,
            "command": command,
            "status": status,
            "result": result,
        })
        logger.info(
            f"BackgroundManager._execute 完成 | task_id={task_id} | "
            f"status={status} | result_len={len(result)}"
        )

    def drain_notifications(self) -> list[dict]:
        """排空通知队列。非阻塞：有消息就取，没消息立刻返回空列表。"""
        notifications = []
        while True:
            try:
                notifications.append(self.notification_queue.get_nowait())
            except queue.Empty:
                break
        return notifications


bg_manager = BackgroundManager()


def format_background_results(notifications: list[dict]) -> str:
    """把后台通知格式化为 <background-results> 标签包裹的文本。

    让模型明确区分这是异步事件，不是用户输入或工具结果。
    """
    parts = ["<background-results>"]
    for n in notifications:
        parts.append(
            f"[{n['task_id']}] {n['command']}\n"
            f"Status: {n['status']}\n"
            f"Result: {n['result'][:2000]}"
        )
    parts.append("</background-results>")
    return "\n".join(parts)


# ---------- MessageBus（第 9 课：JSONL 收件箱，drain-on-read）----------
class MessageBus:
    """append-only 的 JSONL 收件箱系统。

    每个队友一个 .jsonl 文件，send 追加一行，read_inbox 读取全部并清空。
    drain-on-read：消息只需处理一次，读完就清，不需要已读标记。
    线程安全：用 threading.Lock 保护文件操作（队友在同进程线程中）。
    """

    def __init__(self, inbox_dir: str = ".team/inbox"):
        self.inbox_dir = inbox_dir
        os.makedirs(inbox_dir, exist_ok=True)
        self._lock = threading.Lock()
        logger.info(f"MessageBus 初始化 | inbox_dir={inbox_dir}")

    def send(self, from_name: str, to_name: str, content: str):
        """往目标队友的收件箱追加一条消息。"""
        msg = {
            "from": from_name,
            "to": to_name,
            "content": content,
            "timestamp": time.time(),
        }
        path = os.path.join(self.inbox_dir, f"{to_name}.jsonl")
        with self._lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        logger.info(f"MessageBus.send | {from_name} → {to_name} | content={content[:100]}")

    def broadcast(self, from_name: str, content: str, team: dict):
        """群发给所有队友（除自己外）。"""
        for name in team:
            if name != from_name:
                self.send(from_name, name, content)

    def read_inbox(self, name: str) -> list:
        """读取并清空收件箱（drain-on-read）。"""
        path = os.path.join(self.inbox_dir, f"{name}.jsonl")
        if not os.path.exists(path):
            return []
        with self._lock:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # 读完即清
            with open(path, "w", encoding="utf-8") as f:
                pass  # truncate to empty
        msgs = [json.loads(l) for l in lines if l.strip()]
        logger.info(f"MessageBus.read_inbox | {name} | 读取 {len(msgs)} 条消息")
        return msgs


# ---------- TeammateManager（第 9 课：持久 Agent + 身份管理 + 通信）----------
@dataclass
class TeammateConfig:
    """队友配置：name, system_prompt, status (idle/working/shutdown)。"""
    name: str
    system_prompt: str
    status: str = "idle"


class TeammateManager:
    """团队名册管理器。spawn/shutdown 队友，每个队友在独立线程中运行。

    队友不是函数调用，是被委托任务的独立 Agent——有自己的 messages、
    自己的工具、自己的上下文。跟第 1 课的 while 循环完全一样。
    状态持久化到 .team/config.json，Agent 重启后团队名册还在。
    """

    def __init__(self):
        self.team_dir = ".team"
        self.config_path = os.path.join(self.team_dir, "config.json")
        os.makedirs(self.team_dir, exist_ok=True)
        os.makedirs(os.path.join(self.team_dir, "inbox"), exist_ok=True)
        self.team: dict = self._load_team_config()
        self.bus = MessageBus(os.path.join(self.team_dir, "inbox"))
        self.threads: dict = {}
        self._lock = threading.Lock()
        logger.info(
            f"TeammateManager 初始化 | 现有队友: {list(self.team.keys())}"
        )

    def _load_team_config(self) -> dict:
        """从 .team/config.json 加载团队名册。"""
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # 重建为 TeammateConfig
            team = {}
            for name, cfg in raw.items():
                team[name] = TeammateConfig(
                    name=cfg.get("name", name),
                    system_prompt=cfg.get("system_prompt", ""),
                    status=cfg.get("status", "idle"),
                )
            return team
        except Exception as e:
            logger.warning(f"TeammateManager._load_team_config 失败: {e}")
            return {}

    def _save_team_config(self):
        """保存团队名册到 .team/config.json。"""
        raw = {
            name: {
                "name": cfg.name,
                "system_prompt": cfg.system_prompt,
                "status": cfg.status,
            }
            for name, cfg in self.team.items()
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)

    def spawn(self, name: str, system_prompt: str) -> str:
        """创建队友并启动守护线程。"""
        with self._lock:
            if name in self.team and self.team[name].status != "shutdown":
                return f"Error: Teammate '{name}' already exists and is {self.team[name].status}"
            config_obj = TeammateConfig(name=name, system_prompt=system_prompt)
            self.team[name] = config_obj
            self._save_team_config()

        thread = threading.Thread(
            target=self._teammate_loop, args=(name,), daemon=True
        )
        self.threads[name] = thread
        thread.start()
        logger.info(f"TeammateManager.spawn | 队友 {name} 已创建并启动")
        return f"Teammate {name} spawned and started"

    def send_task(self, to_name: str, task: str) -> str:
        """给队友发送任务消息。"""
        with self._lock:
            if to_name not in self.team:
                return f"Error: Teammate '{to_name}' not found. Use spawn_teammate first."
            if self.team[to_name].status == "shutdown":
                return f"Error: Teammate '{to_name}' is shutdown."
        self.bus.send("leader", to_name, task)
        with self._lock:
            if self.team[to_name].status == "idle":
                self.team[to_name].status = "working"
                self._save_team_config()
        logger.info(f"TeammateManager.send_task | leader → {to_name} | task={task[:100]}")
        return f"Task sent to {to_name}"

    def shutdown(self, name: str) -> str:
        """关闭队友。"""
        with self._lock:
            if name not in self.team:
                return f"Error: Teammate '{name}' not found."
            self.team[name].status = "shutdown"
            self._save_team_config()
        logger.info(f"TeammateManager.shutdown | 队友 {name} 已关闭")
        return f"Teammate {name} shut down"

    def render_status(self) -> str:
        """渲染团队名册，让模型看到全局状态。"""
        if not self.team:
            return "(no teammates)"
        icons = {"idle": "💤", "working": "🔧", "shutdown": "🚫"}
        lines = ["📋 Team Roster:"]
        for name, cfg in self.team.items():
            icon = icons.get(cfg.status, "?")
            prompt_preview = cfg.system_prompt[:50] + "..." if len(cfg.system_prompt) > 50 else cfg.system_prompt
            lines.append(f"  {icon} {name} [{cfg.status}] — {prompt_preview}")
        return "\n".join(lines)

    def _teammate_loop(self, name: str):
        """队友循环：轮询收件箱 → 有消息就跑 Agent Loop → 结果发回 leader。"""
        while True:
            with self._lock:
                cfg = self.team.get(name)
                if cfg is None or cfg.status == "shutdown":
                    logger.info(f"TeammateManager._teammate_loop | {name} 退出")
                    return

            # 检查收件箱
            messages = self.bus.read_inbox(name)
            if not messages:
                time.sleep(1)  # 空闲等待，避免忙轮询
                continue

            # 有消息，设为 working
            with self._lock:
                if self.team[name].status != "shutdown":
                    self.team[name].status = "working"
                    self._save_team_config()

            # 处理每条消息
            for msg in messages:
                # 检查是否被 shutdown 了
                with self._lock:
                    cfg = self.team.get(name)
                    if cfg is None or cfg.status == "shutdown":
                        break

                logger.info(
                    f"TeammateManager._teammate_loop | {name} 处理消息: "
                    f"{msg['content'][:100]}"
                )
                result = self._run_teammate_agent(
                    system=cfg.system_prompt,
                    task=msg["content"],
                )
                # 结果发回 leader
                self.bus.send(name, msg["from"], f"[{name} 完成] {result}")

            # 处理完，设为 idle
            with self._lock:
                if self.team[name].status != "shutdown":
                    self.team[name].status = "idle"
                    self._save_team_config()

    def _run_teammate_agent(self, system: str, task: str) -> str:
        """执行一轮独立的 Agent Loop——跟 subagent.py 模式一样。

        队友拥有除团队管理工具和 task 外的所有工具（防递归）。
        """
        from config import client, MODEL, MAX_SUBAGENT_TURNS

        sub_messages = [{"role": "user", "content": task}]

        # 队友可用的工具：排除团队管理工具（防递归）和 task（防子 Agent 递归）
        excluded = {"spawn_teammate", "send_to_teammate", "team_status", "task"}
        teammate_tools = [t for t in TOOLS if t["function"]["name"] not in excluded]

        logger.info(f"=== 队友 Agent 启动 | task={task[:200]} ===")

        response = None
        message = None
        for turn in range(MAX_SUBAGENT_TURNS):
            logger.info(f"--- 队友 Agent 第 {turn + 1} 轮 ---")
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system}] + sub_messages,
                tools=teammate_tools,
                max_tokens=8000,
            )

            choice = response.choices[0]
            message = choice.message

            # 打印队友思考过程
            reasoning = getattr(message, "reasoning_content", None)
            if reasoning:
                print(f"\n[teammate 思考] {reasoning}")
                logger.info(f"teammate reasoning:\n{reasoning}")

            sub_messages.append(message.to_dict())
            logger.info(f"teammate finish_reason={choice.finish_reason}")

            # 队友决定不再调工具 → 任务完成
            if choice.finish_reason != "tool_calls":
                break

            # 执行工具，收集结果
            for tc in message.tool_calls:
                args = json.loads(tc.function.arguments)
                handler = TOOL_HANDLERS.get(tc.function.name)
                output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
                logger.info(f"teammate 工具调用: {tc.function.name} | output={output[:200]}")
                print(f"[teammate:{tc.function.name}] {output[:200]}")
                sub_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": output,
                    }
                )

        final_text = message.content if message and message.content else "(teammate produced no text output)"
        logger.info(f"=== 队友 Agent 结束 | 最终文本={final_text[:200]} ===")
        return final_text


teammate_manager = TeammateManager()


# ---------- 工具调度映射 ----------
# 注意：task handler 不在此注册，由 agent.py 接线（打破循环依赖）
TOOL_HANDLERS = {
    "bash":         lambda **kw: run_bash(kw["command"]),
    "read_file":    lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file":   lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":    lambda **kw: run_edit(kw["path"], kw["old_text"],
                                          kw["new_text"]),
    "todo":         lambda **kw: todo_manager.update(kw["items"]),
    "load_skill":   lambda **kw: skill_loader.get_content(kw["skill_name"]),
    "task_create":  lambda **kw: json.dumps(task_manager.create(**kw), ensure_ascii=False),
    "task_update":  lambda **kw: json.dumps(task_manager.update(**kw), ensure_ascii=False),
    "task_list":    lambda **kw: json.dumps(task_manager.list_tasks(**kw), ensure_ascii=False),
    "task_get":     lambda **kw: json.dumps(task_manager.get_task(**kw), ensure_ascii=False),
    "task_clear":   lambda **kw: json.dumps(task_manager.clear(), ensure_ascii=False),
    "run_in_background": lambda **kw: bg_manager.run(kw["command"]),
    "spawn_teammate":  lambda **kw: teammate_manager.spawn(kw["name"], kw["system_prompt"]),
    "send_to_teammate": lambda **kw: teammate_manager.send_task(kw["to_name"], kw["task"]),
    "team_status":     lambda **kw: teammate_manager.render_status(),
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
    {
        "type": "function",
        "function": {
            "name": "compact",
            "description": "Compress the conversation history into a summary. Use when the context is getting long and you want to clean up before continuing.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": "Create a new task with optional dependencies. Use this to break down complex work into a DAG of subtasks. Each task is persisted as a JSON file and can be tracked independently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "What the task is about",
                    },
                    "blocked_by": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "IDs of tasks that must complete before this one",
                    },
                },
                "required": ["subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Update a task's status. Set to in_progress when starting work, completed when done. Completing a task automatically unblocks downstream tasks that depend on it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                    "owner": {
                        "type": "string",
                        "description": "Which agent owns this task",
                    },
                },
                "required": ["task_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_list",
            "description": "List all tasks. Optionally filter by status. Use this to see the current state of the task graph.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_get",
            "description": "Get details of a specific task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_clear",
            "description": "Clear all tasks and reset the task ID counter. Use this after all tasks are completed to clean up for the next session.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_in_background",
            "description": "Run a shell command in the background. Returns immediately with a task ID. Use for long-running commands like npm install, pytest, docker build, pip install. Results delivered as background notifications in subsequent turns.",
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
            "name": "spawn_teammate",
            "description": "Create a persistent teammate agent that runs in its own thread with its own Agent Loop. The teammate has an independent context and can use all tools except team management tools (no recursion). Use this to delegate work to specialized agents (e.g., coder, tester, reviewer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Unique name for the teammate (e.g., 'coder', 'tester')",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt defining the teammate's role and expertise",
                    },
                },
                "required": ["name", "system_prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_to_teammate",
            "description": "Send a task message to a teammate. The teammate will process it in its own Agent Loop and send the result back to your inbox. Results arrive as <teammate-reports> in subsequent turns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_name": {
                        "type": "string",
                        "description": "Name of the teammate to send the task to",
                    },
                    "task": {
                        "type": "string",
                        "description": "The task description to send",
                    },
                },
                "required": ["to_name", "task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "team_status",
            "description": "Show the current team roster with each teammate's status (idle/working/shutdown) and role. Use this to check on your team's progress.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

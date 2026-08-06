import json
import os
import subprocess
import threading
import queue
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from . import config
from .config import logger, safe_path
from .protocol import (
    coordinator,
    RequestStatus,
    parse_protocol_flag,
    inject_pending_requests,
)

# ---------- 第 12 课：Worktree 隔离占位 ----------
# worktree_manager 在模块底部 wire（仿 coordinator.wire 打破循环依赖）。
# run_bash / run_read / run_write / run_edit / bg_manager 都通过
# worktree_manager.resolve_dir() 决定当前线程的操作基座：
#   未 worktree_use → 项目根目录（与 s11 行为一致）
#   worktree_use(task_id) → 该任务的 worktree 目录（执行面隔离）
worktree_manager = None

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
    # 第 12 课：cwd 跟随线程 session 基座（worktree_use 后落在 worktree 内）
    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
    proc = subprocess.Popen(
        command, shell=True, cwd=base,
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
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        text = safe_path(path, base).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"

def run_write(path: str, content: str) -> str:
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
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

    重构：skills 目录改为相对本包（core/skills/），不依赖运行时的 cwd——
    这样无论从项目根、server_app 还是任意目录启动，技能都能被找到。
    """

    def __init__(self, skills_dir: str | None = None):
        if skills_dir is None:
            # 默认指向 core/skills（本包所在目录下的 skills）
            skills_dir = str(Path(__file__).resolve().parent / "skills")
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

# 重构：不再传 "skills"——缺省时自动解析为 core/skills（包相对），
# 保证从任意启动目录都能找到技能，与 cwd 无关。
skill_loader = SkillLoader()

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
        # 第 11 课：任务看板的并发访问锁——两个队友抢同一任务时
        # 原子认领必须互斥，否则会同时认领成功（数据竞争）。
        self._lock = threading.Lock()
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
        # Bug A 修复：Agent 收尾阶段可能用 bash 物理删除 .tasks 目录
        # （任务清理指令里就要求删掉 .tasks）。目录不存在时按"空任务列表"
        # 处理，避免 all_completed() 在 os.listdir() 处抛 FileNotFoundError
        # 导致主循环收尾崩溃。
        if not os.path.isdir(self.task_dir):
            logger.info(
                f"TaskManager._all_task_ids | 目录 {self.task_dir} 不存在，"
                f"按空任务列表处理"
            )
            return []
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

    def unclaimed_actionable(self) -> list[dict]:
        """第 11 课：扫描看板，返回可认领任务（pending + 无 owner + 未被阻塞）。

        is_blocked 检查 blockedBy 依赖——任一依赖未完成则任务不可拿。
        """
        result = []
        for t in self.list_tasks():
            if t["status"] != "pending":
                continue
            if t.get("owner") is not None:
                continue
            if self._is_blocked(t):
                continue
            result.append(t)
        logger.info(f"TaskManager.unclaimed_actionable | 返回 {len(result)} 个可认领任务")
        return result

    def _is_blocked(self, task: dict) -> bool:
        """判断任务是否被未完成的依赖阻塞（第 11 课 is_blocked）。"""
        for dep_id in task.get("blockedBy", []):
            dep = self._read_task(dep_id)
            if dep is not None and dep["status"] != "completed":
                return True
        return False

    def claim(self, task_id: int, agent_id: str) -> bool:
        """第 11 课：原子认领任务。

        加锁保证并发安全：多个队友同时看到同一无主任务，
        只有一个能认领成功（pending + owner 为空才可认领）。
        认领失败（被别人抢了 / 已被阻塞）返回 False，调用方下一轮重试。
        """
        with self._lock:
            task = self._read_task(task_id)
            if task is None:
                return False
            if task["status"] != "pending":
                return False
            if task.get("owner") is not None:
                return False
            if self._is_blocked(task):
                return False
            task["status"] = "in_progress"
            task["owner"] = agent_id
            self._write_task(task)
            logger.info(f"TaskManager.claim | task #{task_id} 已被 {agent_id} 认领")
        return True

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

    def update_status(self, task_id: int, status: str) -> dict:
        """第 12 课：WorktreeManager 双状态机联动用的薄封装。

        只改状态、不动 owner（worktree_create 推进 in_progress、
        worktree_remove 推进 completed 时，任务可能还没有 owner——
        保持 owner 原样，避免覆盖队友认领信息）。
        """
        logger.info(
            f"TaskManager.update_status | task_id={task_id} | status={status}"
        )
        task = self._read_task(task_id)
        if task is None:
            error_msg = f"Task {task_id} not found"
            logger.warning(f"TaskManager.update_status 失败: {error_msg}")
            return {"error": error_msg}

        # 不能把被阻塞的任务直接设为 in_progress
        if status == "in_progress" and task["blockedBy"]:
            unfinished = []
            for dep_id in task["blockedBy"]:
                dep = self._read_task(dep_id)
                if dep is None or dep["status"] != "completed":
                    unfinished.append(dep_id)
            if unfinished:
                error_msg = f"Task {task_id} is blocked by unfinished tasks: {unfinished}"
                logger.warning(f"TaskManager.update_status 失败: {error_msg}")
                return {"error": error_msg}

        task["status"] = status
        self._write_task(task)
        logger.info(
            f"TaskManager.update_status 成功 | task={json.dumps(task, ensure_ascii=False)}"
        )
        # 完成时同样自动解锁下游任务
        if status == "completed":
            self._clear_dependency(task_id)
        return task

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

        # Bug C 修复：threading.local 只对当前线程可见。后台线程是新线程，
        # 读不到主线程 worktree_use 设置的 base，必须在这里（启动前、主线程内）
        # 捕获，作为参数传给后台线程，后台任务才能落在主线程当前 worktree 里。
        base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
        thread = threading.Thread(
            target=self._execute,
            args=(task_id, command, base),
            daemon=True,
        )
        thread.start()
        logger.info(
            f"BackgroundManager.run | task_id={task_id} | command={command} | "
            f"base={base}"
        )
        return task_id

    def _execute(self, task_id: str, command: str, base: str):
        """在守护线程里跑子进程。Windows 适配：Popen + taskkill，不用 subprocess.run。

        第 12 课：base 由 run() 在启动前于主线程捕获并传入——
        后台任务落在主线程当前 worktree 内（若已 worktree_use）。
        """
        proc = subprocess.Popen(
            command, shell=True, cwd=base,
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
        # 每次启动清空残留的 inbox 文件——上一次 session 的消息已无意义
        # （队友线程随进程退出而死亡，无人再读取这些孤儿消息）
        self._clean_stale_inbox()
        logger.info(f"MessageBus 初始化 | inbox_dir={inbox_dir} | 已清空残留消息")

    def _clean_stale_inbox(self):
        """清空 inbox 目录下所有 .jsonl 文件的残留内容。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时跳过，避免 os.listdir 抛 FileNotFoundError。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        for fname in os.listdir(self.inbox_dir):
            if fname.endswith(".jsonl"):
                path = os.path.join(self.inbox_dir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    pass  # truncate to empty

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

    def clear_all(self):
        """第 11 课：清空所有收件箱文件（session 收尾时调用）。

        只清空 .jsonl 文件内容，保留目录本身。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时直接跳过，避免 os.listdir 抛 FileNotFoundError 使主循环崩溃。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        with self._lock:
            for fname in os.listdir(self.inbox_dir):
                if fname.endswith(".jsonl"):
                    path = os.path.join(self.inbox_dir, fname)
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            pass  # truncate to empty
                    except OSError:
                        pass
        logger.info(f"MessageBus.clear_all | 已清空 {self.inbox_dir} 下所有收件箱文件")

# ---------- 第 11 课：身份重注入（Context Compact 后防止角色丢失）----------
IDENTITY_THRESHOLD = 3  # 消息列表低于该数时认为刚经历过压缩，需要重注入身份

def maybe_reinject_identity(agent_id: str, role_prompt: str,
                            messages: list) -> list:
    """第 11 课机制四：消息列表过短时在开头插入 <identity> 身份块。

    Context Compact（第 6 课）会压缩消息历史，包括可能丢掉的 system 身份信息。
    若消息列表数量骤降（< IDENTITY_THRESHOLD），说明刚被压缩过——
    此时把"我是谁"用 <identity> 标签重新注入，防止队友角色越权
    （coder 开始审查代码、tester 开始写业务逻辑）。

    用 user 消息而不是改 system——因为 system 在 API 层面只设一次，
    身份重注入需要在对话过程中动态触发。

    :param agent_id: 队友名字（如 "coder"）
    :param role_prompt: 队友的完整 system prompt（角色定义）
    :param messages: 当前对话消息列表
    :return: 注入后的新消息列表（未触发则原样返回）
    """
    if len(messages) >= IDENTITY_THRESHOLD:
        return messages
    identity_block = {
        "role": "user",
        "content": (
            f"<identity>\n你是 {agent_id}。\n"
            f"{role_prompt}\n</identity>"
        ),
    }
    logger.info(f"maybe_reinject_identity | {agent_id} | 消息数={len(messages)} < {IDENTITY_THRESHOLD}，注入身份块")
    return [identity_block] + messages

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
        self.team: dict = {}
        self.bus = MessageBus(os.path.join(self.team_dir, "inbox"))
        self.threads: dict = {}
        self._lock = threading.Lock()
        # 每次运行干净开始：不跨 session 持久化团队状态
        # 队友无持久记忆（每次 task 都是全新 context），跨 session 保留名册无意义
        self._save_team_config()
        logger.info(
            f"TeammateManager 初始化 | 干净启动，team 已清空 | "
            f"活跃线程: {list(self.threads.keys())}"
        )

    def _save_team_config(self):
        """保存团队名册到 .team/config.json。

        Bug D 修复：Agent 收尾可能按任务要求用 bash 物理删除 .team 目录，
        此时 .team 可能不存在。写前确保目录存在（自愈重建空目录），
        避免 open('.team/config.json','w') 抛 FileNotFoundError 使主循环崩溃。
        """
        os.makedirs(self.team_dir, exist_ok=True)
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
        """创建队友并启动守护线程。已存在的 idle 队友会重启线程。"""
        with self._lock:
            if name in self.team:
                if self.team[name].status == "shutdown":
                    # shutdown 状态可以重新创建
                    self.team[name] = TeammateConfig(name=name, system_prompt=system_prompt)
                    self._save_team_config()
                elif self.team[name].status == "idle":
                    # idle 状态：更新 system_prompt，重启线程
                    self.team[name].system_prompt = system_prompt
                    self._save_team_config()
                    logger.info(f"TeammateManager.spawn | 队友 {name} 已存在(idle)，重启线程")
                else:
                    # working 状态：不能重新 spawn
                    return f"Error: Teammate '{name}' already exists and is {self.team[name].status}"
            else:
                self.team[name] = TeammateConfig(name=name, system_prompt=system_prompt)
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
            # 清理线程引用（线程自身会在下次循环检测到 shutdown 后退出）
            self.threads.pop(name, None)
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

    def _try_claim_from_board(self, name: str) -> dict | None:
        """第 11 课：IDLE 阶段扫描看板，认领一个可执行任务。

        返回认领到的任务 dict；没有可认领/被抢返回 None（下一轮重试）。
        """
        for task in task_manager.unclaimed_actionable():
            if task_manager.claim(task["id"], name):
                return task
        return None

    def _teammate_loop(self, name: str):
        """队友循环：IDLE 阶段（收件箱 + 扫看板认领）→ WORK 阶段（跑 Agent Loop）。

        第 11 课自治：
        1. 收件箱有直接指派 → 优先处理（与第 9-10 课一致）
        2. 收件箱无活 → 扫描 .tasks 看板自由认领（pending + 无主 + 未阻塞）
        3. 认领成功 → 构造工作消息走 WORK
        4. 每 5s 扫一次，60s 无活 → 自动 SHUTDOWN
        """
        idle_deadline = time.time() + 60  # IDLE 阶段最多等 60s，超时自动关机

        while True:
            with self._lock:
                cfg = self.team.get(name)
                if cfg is None or cfg.status == "shutdown":
                    logger.info(f"TeammateManager._teammate_loop | {name} 退出")
                    return

            # ── IDLE 阶段 ──
            # 1) 收件箱（直接指派优先）
            messages = self.bus.read_inbox(name)

            # 2) 收件箱没活 → 扫描看板认领（第 11 课）
            if not messages:
                try:
                    claimed = self._try_claim_from_board(name)
                except Exception as e:
                    logger.exception(f"TeammateManager._teammate_loop | {name} 扫看板异常: {e}")
                    claimed = None

                if claimed is None:
                    # 没活干：IDLE 超时自动关机
                    if time.time() >= idle_deadline:
                        logger.info(f"TeammateManager._teammate_loop | {name} IDLE 超时 60s 无任务，自动关机")
                        with self._lock:
                            if self.team[name].status != "shutdown":
                                self.team[name].status = "shutdown"
                                self._save_team_config()
                        return
                    time.sleep(5)  # 每 5s 扫一次看板（课文 idle_poll 间隔）
                    continue

                # 3) 认领成功 → 构造工作消息走 WORK
                idle_deadline = time.time() + 60  # WORK 完成后重置 IDLE 超时
                logger.info(f"TeammateManager._teammate_loop | {name} 认领看板任务 #{claimed['id']}，进入 WORK")
                messages = [{
                    "from": "board",
                    "content": (
                        f"你从任务看板认领了任务 #{claimed['id']}：{claimed['subject']}\n"
                        f"完成该任务后，用 task_update 把任务 #{claimed['id']} 标记为 completed。"
                    ),
                }]

            # ── WORK 阶段 ──
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

                content = msg["content"]

                # ── 协议消息（第 10 课）：确定性代码处理，不走 LLM ──
                parsed = parse_protocol_flag(content)
                if parsed:
                    ptype, pargs = parsed
                    if ptype == "shutdown":
                        outcome = coordinator.handle_shutdown_request(name, pargs[0])
                        if outcome == "exit":
                            self.bus.send(
                                name, "leader",
                                f"[{name} 完成] Shutdown approved & buffers flushed, "
                                f"teammate thread exiting now",
                            )
                            with self._lock:
                                self.team[name].status = "shutdown"
                                self._save_team_config()
                            logger.info(f"TeammateManager._teammate_loop | {name} 安全退出（关机握手批准）")
                            return
                        # REJECTED：把拒绝原因也照常发回 leader（走普通汇报格式）
                        self.bus.send(
                            name, "leader",
                            f"[{name} 完成] {outcome}",
                        )
                        logger.info(f"TeammateManager._teammate_loop | {name} 拒绝关机，继续运行: {outcome[:100]}")
                        continue
                    elif ptype in ("plan_result", "shutdown_result"):
                        # 审批结果回执/关机结果回执：无需队友处理，已由 tracker 记录
                        logger.info(f"TeammateManager._teammate_loop | {name} 收到回执: {content[:100]}")
                        continue
                    else:
                        logger.info(f"TeammateManager._teammate_loop | {name} 未知协议消息: {content[:100]}")
                        continue

                # ── 普通任务消息：跑 Agent Loop ──
                logger.info(
                    f"TeammateManager._teammate_loop | {name} 处理消息: "
                    f"{content[:100]}"
                )
                result = self._run_teammate_agent(
                    system=cfg.system_prompt,
                    task=content,
                    agent_id=name,
                )
                # 结果发回 leader（看板认领的任务回报给 leader，便于观测）
                self.bus.send(name, msg["from"], f"[{name} 完成] {result}")

            # 处理完，回到 idle
            with self._lock:
                if self.team[name].status != "shutdown":
                    self.team[name].status = "idle"
                    self._save_team_config()

    def _run_teammate_agent(self, system: str, task: str, agent_id: str) -> str:
        """执行一轮独立的 Agent Loop——跟 subagent.py 模式一样。

        队友拥有除团队管理工具和 task 外的所有工具（防递归）。

        第 10 课改造：
        1. 每轮注入该队友的 pending-requests（计划审批结果 / 关机请求）
        2. 执行 write_file / edit_file 时自动登记到 AgentWriteTracker
        第 11 课改造：身份重注入——compact 后消息列表骤降（<阈值）时，
        在开头插入 <identity> 块，防止队友忘了"我是谁"导致角色越权。
        """
        from .config import client, MODEL, MAX_SUBAGENT_TURNS, TEAMMATE_SYSTEM_PREFIX

        sub_messages = [{"role": "user", "content": task}]

        # 队友可用的工具：排除团队管理工具（防递归）和 task（防子 Agent 递归）。
        # 队友保留 submit_plan / respond_to_request（第 10 课：队友提计划、响应协议）；
        # 排除 request_shutdown（只有 leader 能发起关机）。
        excluded = {"spawn_teammate", "send_to_teammate", "team_status", "task",
                    "request_shutdown"}
        teammate_tools = [t for t in TOOLS if t["function"]["name"] not in excluded]

        logger.info(f"=== 队友 Agent 启动 | agent={agent_id} | task={task[:200]} ===")

        response = None
        message = None
        for turn in range(MAX_SUBAGENT_TURNS):
            # ── 第 11 课：身份重注入（Context Compact 后消息列表骤降时触发）──
            sub_messages = maybe_reinject_identity(agent_id, system, sub_messages)

            # ── 第 10 课：每轮开始注入协议请求（计划审批结果 / 关机请求）──
            inject_pending_requests(sub_messages, agent_id)

            logger.info(f"--- 队友 Agent 第 {turn + 1} 轮 ---")
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": TEAMMATE_SYSTEM_PREFIX + system}] + sub_messages,
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
                # 第 10 课：submit_plan 需要记录发起方（队友身份）
                if tc.function.name == "submit_plan":
                    args["_agent_id"] = agent_id
                handler = TOOL_HANDLERS.get(tc.function.name)
                output = handler(**args) if handler else f"Unknown tool: {tc.function.name}"
                logger.info(f"teammate 工具调用: {tc.function.name}")
                # 调试需要：完整输出写入 run.log，不截断
                print(f"[teammate:{tc.function.name}] {output}")
                sub_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": output,
                    }
                )

                # 第 10 课：写入文件后自动登记（关机握手依赖此登记判断未提交写入）
                if tc.function.name in ("write_file", "edit_file"):
                    coordinator.writes.record_write(agent_id, args.get("path", "?"))

        final_text = message.content if message and message.content else "(teammate produced no text output)"

        # 第 10 课修复：队友完成一轮任务后，本轮所有 write_file/edit_file 已同步落盘
        # （write_file 是同步写盘，不是异步缓冲），此时清空写入登记是准确反映
        # "已提交"状态。否则登记永久残留，关机握手会无限 REJECTED（死循环）。
        coordinator.writes.flush(agent_id)

        logger.info(f"=== 队友 Agent 结束 | agent={agent_id} | 最终文本={final_text[:200]} ===")
        return final_text

teammate_manager = TeammateManager()

# ---------- 第 10 课接线：协调器注入消息总线 / 团队名册（打破循环依赖）----------
# request_shutdown 的"协议协商"路径：coordinator 通过 bus 发 [PROTOCOL] shutdown，
# 队友 loop 收到后确定性处理并回复；只有 APPROVED 才真正关闭线程（不再直接杀）。
# _force_shutdown 保留为兜底（不自杀场景），协议路径不用它。
coordinator.wire(
    bus=teammate_manager.bus,
    team=teammate_manager.team,
    force_shutdown_fn=teammate_manager.shutdown,
)

# ---------- 工具调度映射 ----------
# 注意：task handler 不在此注册，由 agent.py 接线（打破循环依赖）
def _submit_plan(kw: dict) -> str:
    """队友提交计划审批。用 current_agent_id 记录发起方。"""
    agent = kw.get("_agent_id", "unknown")
    plan = {
        "summary": kw.get("plan_summary", ""),
        "files": kw.get("affected_files", []),
        "risk": kw.get("risk_level", "low"),
        "change_count": kw.get("estimated_changes", 0),
    }
    return coordinator.submit_plan_for_review(agent, plan)

def _respond_to_request(kw: dict) -> str:
    """leader 审批/响应协议请求。decision ∈ approve | reject。

    状态守卫温和化：LLM 可能传一个已决议的 req_id（误用/测试/幻觉），
    此时 tracker.respond() 会抛 ValueError。如果让它冒泡，整个 agent 主循环
    会被一个工具调用炸毁。这里捕获并转成温和错误文本，LLM 拿到的只是
    一条 Error 消息，可以继续思考，程序不中断。
    """
    decision = kw.get("decision", "approve")
    reason = kw.get("reason", "")
    try:
        return coordinator.handle_plan_review(kw["req_id"], decision, reason)
    except ValueError as e:
        logger.info(f"respond_to_request 捕获状态守卫异常 | {e}")
        return f"Error: {e}"

def _claim_task(kw: dict) -> str:
    """第 11 课：队友显式认领任务。调用方需提供自己的 agent_id（由调度层注入）。"""
    agent = kw.get("_agent_id", "unknown")
    ok = task_manager.claim(kw["task_id"], agent)
    if ok:
        return f"Claimed task #{kw['task_id']} for {agent}"
    return f"Error: Task {kw['task_id']} could not be claimed (already claimed / not pending / blocked)"

def _worktree_remove(kw: dict) -> str:
    """第 12 课：拆除 worktree 的工具封装。

    worktree_remove 无返回值，这里补一个可读文本：
    complete_task 决定任务是否推进到 completed；merge 决定是否先合并回主分支。
    """
    worktree_manager.worktree_remove(
        kw["task_id"],
        complete_task=kw.get("complete_task", True),
        merge=kw.get("merge", False),
    )
    merged = "（已合并回主分支）" if kw.get("merge", False) else ""
    completed = "任务已标记 completed" if kw.get("complete_task", True) else "任务保留原状态"
    return f"Removed worktree for task #{kw['task_id']}{merged} | {completed}"

# ========== Forge Mod 生成工具（MC 26.x / Forge 65.x，2026-08） ==========
# 纯模板生成：输入参数 → 生成文件内容 → 用 run_write 写入当前 mod 工作目录。
# 所有 handler 都是工具函数增量，不依赖也不修改 agent 主循环。

def _build_source_zip() -> str:
    """源码 zip 预生成：在 agent 收尾阶段把当前 mod 工程打包为 mod.zip。

    与 server 的 download_mod 采用相同规则（跳过 build/dist/.git 等运行时目录），
    这样用户第一次点击下载时后端直接命中缓存返回，无需现场打包 11MB。
    """
    import zipfile

    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
    zip_path = base.parent / "mod.zip"  # <session>/mod.zip（与 server SESSIONS_DIR 布局一致）
    skip = {"build", "dist", ".worktrees", ".team", ".tasks",
            ".transcripts", "__pycache__", ".git"}
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(base):
                for p in sorted(Path(base).rglob("*")):
                    try:
                        rel = p.relative_to(Path(base))
                    except ValueError:
                        continue
                    if any(part in skip for part in rel.parts):
                        continue
                    if p.is_file():
                        zf.write(p, rel.as_posix())
        return f"[build] 源码 zip 已预生成: {zip_path}"
    except Exception as e:
        return f"[build] 源码 zip 预生成失败: {e}"


def _forge_build_jar(kw: dict) -> str:
    """build_mod_jar_forge：构建 Forge mod 项目为可安装 jar（gradlew build）。

    与 run_bash 的 30s 超时不同，这里用同步长超时（900s）等待 Forge Gradle
    首次构建完成（下载依赖 + 反混淆通常需要数分钟）。构建成功后把
    build/libs/*.jar 复制到工程根的 dist/ 目录便于识别/下载。
    """
    task = kw.get("gradle_task", "build")
    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()

    if os.name == "nt" or sys.platform == "win32":
        if os.path.exists(os.path.join(base, "gradlew.bat")):
            cmd = ["cmd", "/c", "gradlew.bat", task]
        else:
            cmd = ["cmd", "/c", "gradle", task, "--console=plain"]
    else:
        if os.path.exists(os.path.join(base, "gradlew")):
            cmd = ["./gradlew", task, "--console=plain"]
        else:
            cmd = ["gradle", task, "--console=plain"]

    try:
        proc = subprocess.Popen(
            cmd, cwd=base,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
    except Exception as e:
        return f"[build] 无法启动 Gradle: {e}"

    try:
        out, _ = proc.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(f"taskkill /f /t /pid {proc.pid}", shell=True, capture_output=True)
        except Exception:
            pass
        return f"[build] Gradle 构建超时（>900s）。\n日志尾部:\n{(out or '')[-3000:]}"

    ok = proc.returncode == 0
    tail = (out or "")[-3000:]

    if not ok:
        hint = ""
        if "Failed to find JDK for version 8" in (out or "") and "JavaProvisionerException" in (out or ""):
            hint = (
                "原因：ForgeGradle 反混淆需要 JDK 8，但服务器缺少 JDK 8"
                "（且自动下载被 SSL 证书拦截）。\n"
                "解决：在服务器安装 Temurin JDK 8 并设置 JAVA_HOME，"
                "或修复系统证书/代理后重新生成。"
            )
        elif "SSLHandshakeException" in (out or "") or "PKIX path building failed" in (out or ""):
            hint = (
                "原因：Gradle 下载依赖时 SSL 证书校验失败"
                "（多为代理/公司网络拦截或系统根证书不全）。\n"
                "解决：修复证书/代理后重新生成。"
            )
        else:
            hint = "原因：构建过程出错（详见日志尾部）。"
        return (
            f"[build] Gradle 构建失败 (exit={proc.returncode})。\n"
            f"{hint}\n日志尾部:\n{tail}"
        )

    libs_dir = os.path.join(base, "build", "libs")
    jars = []
    if os.path.isdir(libs_dir):
        for fname in sorted(os.listdir(libs_dir)):
            if fname.endswith(".jar"):
                jars.append(fname)
                try:
                    ddist = os.path.join(base, "dist")
                    os.makedirs(ddist, exist_ok=True)
                    import shutil as _sh
                    _sh.copy2(os.path.join(libs_dir, fname), os.path.join(ddist, fname))
                except Exception as e:
                    return f"[build] 构建成功但复制 jar 失败: {e}"

    if not jars:
        return f"[build] 构建完成但未在 build/libs 找到 jar。\n日志尾部:\n{tail}"

    sizes = []
    for j in jars:
        try:
            sizes.append(f"{j} ({os.path.getsize(os.path.join(base,'dist',j))} B)")
        except OSError:
            sizes.append(j)
    return (
        f"[build] 构建成功 ✓ 产出 jar：\n  " + "\n  ".join(sizes) +
        "\n已复制到工程根的 dist/ 目录，可直接放入 .minecraft/mods/。"
    )

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
    "claim_task":   lambda **kw: _claim_task(kw),
    "run_in_background": lambda **kw: bg_manager.run(kw["command"]),
    "spawn_teammate":  lambda **kw: teammate_manager.spawn(kw["name"], kw["system_prompt"]),
    "send_to_teammate": lambda **kw: teammate_manager.send_task(kw["to_name"], kw["task"]),
    "team_status":     lambda **kw: teammate_manager.render_status(),
    "shutdown_teammate": lambda **kw: teammate_manager.shutdown(kw["name"]),
    # ── 第 10 课：协议工具 ──
    "request_shutdown": lambda **kw: coordinator.request_shutdown(
        kw["name"], kw.get("reason", "task_complete")),
    "submit_plan":      lambda **kw: _submit_plan(kw),
    "respond_to_request": lambda **kw: _respond_to_request(kw),
    "protocol_status":  lambda **kw: coordinator.render_status(),
    # ── 第 12 课：Worktree 终极隔离工具 ──
    "worktree_create":  lambda **kw: worktree_manager.worktree_create(
        kw["task_id"], kw.get("branch"), kw.get("repo")),
    "worktree_remove":  lambda **kw: _worktree_remove(kw),
    "worktree_run":     lambda **kw: worktree_manager.run_in_worktree(
        kw["task_id"], kw["command"]),
    "worktree_use":     lambda **kw: worktree_manager.worktree_use(
        kw.get("task_id")),
    "worktree_list":    lambda **kw: worktree_manager.render_list(),
    "worktree_recover": lambda **kw: json.dumps(worktree_manager.recover(),
                                                ensure_ascii=False),
    # ── Forge Mod 生成工具（MC 26.x / Forge 65.x）──
    "build_mod_jar_forge": lambda **kw: _forge_build_jar(kw),
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
    {
        "type": "function",
        "function": {
            "name": "shutdown_teammate",
            "description": "Shut down a teammate agent. The teammate's thread will exit on its next loop iteration. Use this when a teammate's work is done and you want to clean up resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_shutdown",
            "description": "Request a graceful shutdown of a teammate via the Shutdown Handshake Protocol. Sends a shutdown request; the teammate checks for uncommitted writes and either approves (safe exit after flushing buffers) or rejects (still has pending work). Use this instead of shutdown_teammate so the teammate gets a chance to finish/clean up. The result appears in <pending-requests> in a later turn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down gracefully",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why the teammate is being shut down",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_plan",
            "description": "Submit an implementation plan for leader approval (Plan Approval Protocol). High-risk changes MUST be approved before execution. If the plan is rejected, revise it and submit again. Wait for the approval result in <pending-requests> before executing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_summary": {
                        "type": "string",
                        "description": "What you plan to do",
                    },
                    "affected_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files you plan to modify/create",
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Risk level: high = refactor/delete API/database migration",
                    },
                    "estimated_changes": {
                        "type": "integer",
                        "description": "Estimated number of changes",
                    },
                },
                "required": ["plan_summary", "affected_files", "risk_level", "estimated_changes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "respond_to_request",
            "description": "Approve or reject a protocol request (Plan Approval Protocol). Called by the leader to respond to a teammate's plan submission. On reject, provide a reason; the teammate will revise and resubmit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "req_id": {
                        "type": "string",
                        "description": "The request ID shown in <pending-requests>",
                    },
                    "decision": {
                        "type": "string",
                        "enum": ["approve", "reject"],
                        "description": "approve = proceed with execution; reject = revise the plan",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the decision (especially on reject)",
                    },
                },
                "required": ["req_id", "decision"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_status",
            "description": "Show all protocol requests (shutdown handshakes and plan approvals) and their current status: pending/approved/rejected.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "claim_task",
            "description": "Atomically claim a task from the task board (.tasks/) so it becomes yours (in_progress + owner). Only pending, unowned, unblocked tasks can be claimed. If another agent already claimed it, this fails and you should try another task. Use task_list to see available tasks, then claim_task to grab one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to claim",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    # ── 第 12 课：Worktree 终极隔离工具 ──
    {
        "type": "function",
        "function": {
            "name": "worktree_create",
            "description": "Create a git worktree for a task and bind it: the task gets an isolated working directory under <repo>/.worktrees/task-<id> and auto-advances to in_progress. Work on the task inside that directory so parallel agents never overwrite each other. If the target repo is NOT the project root (e.g. a sub-repo like demo/demo-s12), pass repo explicitly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to isolate"},
                    "branch": {"type": "string", "description": "Optional branch name (default: task-<id>)"},
                    "repo": {"type": "string", "description": "Optional git repo root to create the worktree in (default: project root)"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_remove",
            "description": "Tear down a task's worktree: removes the directory, unregisters it, and cleans up the branch. complete_task=True also marks the task completed; merge=True first merges the worktree branch back to the main branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "complete_task": {"type": "boolean", "description": "Mark the task completed (default true)"},
                    "merge": {"type": "boolean", "description": "Merge the worktree branch back to main before removing (default false)"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_run",
            "description": "Run a shell command inside a task's worktree directory without switching your working base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "command": {"type": "string"},
                },
                "required": ["task_id", "command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_use",
            "description": "Switch THIS agent's working base to a task's worktree (thread-isolated). After switching, all your bash/read_file/write_file/edit_file operations are confined to that worktree. Pass task_id=0 or omit to switch back to the main directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task whose worktree to switch into; 0 or null switches back to main"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_list",
            "description": "Show the worktree registry: each worktree's task binding, branch, status and whether its directory exists.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_recover",
            "description": "Rebuild state after a crash by cross-checking the event stream, the worktree registry and the disk: roll back half-finished create ops, clean orphaned registry entries and flag orphaned directories.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    # ── Forge Mod 生成工具（MC 26.x / Forge 65.x）──
    {
        "type": "function",
        "function": {
            "name": "build_mod_jar_forge",
            "description": "Build the Forge mod project into an installable jar by running the Gradle wrapper (gradlew build). This takes several minutes on first build (downloads deps + remaps). On success, copies the jar(s) from build/libs/ into the project's dist/ folder so they can be placed directly in .minecraft/mods/. Parameters: gradle_task (default 'build').",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradle_task": {"type": "string"},
                },
            },
        },
    },
]

# ---------- 第 12 课接线：WorktreeManager 注入（打破循环依赖） ----------
# worktree.py 不 import tools.py（TaskManager 由构造参数注入），因此可以在这里
# 安全地 import worktree 并把真实单例挂到占位符上（顶部 worktree_manager = None）。
# 注入之后：
#   - run_bash / run_read / run_write / run_edit / bg_manager 通过 resolve_dir()
#     感知 worktree_use 切换的 session 基座（线程隔离）
#   - worktree_create/remove 通过 task_manager.update_status 完成双状态机联动
from .worktree import WorktreeManager
worktree_manager = WorktreeManager(str(config.WORKDIR), task_manager)
logger.info(
    f"第 12 课 wiring 完成 | worktree_manager 已注入 | "
    f"root={config.WORKDIR} | 现有 worktree 注册数={len(worktree_manager._load_index())}"
)

# -*- coding: utf-8 -*-
"""Background task manager implementations (moved from core/tools.py)."""
import os
import queue
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Optional

from .config import logger
from .tools_runtime import worktree_manager

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
            "format",
            "diskpart", "reg delete", "shutdown",
            "taskkill /f /im python.exe",
            "taskkill /f /im node.exe",
            "taskkill /f /im cmd.exe",
        ]
        if any(d in command.lower() for d in dangerous):
            return "Error: Dangerous command blocked"

        # 沙箱：与 run_bash 保持一致，禁止越出工作区/read-only 写操作
        from .tools_shell import _escapes_workspace, _is_mutating, _sandbox_mode
        mode = _sandbox_mode()
        if mode != "full-access":
            if _escapes_workspace(command):
                return "Error: 沙箱模式禁止越出工作区（cd .. / cd 绝对路径）"
            if mode == "read-only" and _is_mutating(command):
                return "Error: read-only 模式禁止修改性操作"

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
            from .process_manager import kill_pid
            kill_pid(proc.pid)
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

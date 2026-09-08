# -*- coding: utf-8 -*-
"""TaskManager：文件级持久化的任务图 DAG + 认领入口。
由 tasks.py 原样迁出。
"""
import json
import os
import threading

from ....config import logger
from . import board_store  # 文件存储基座（拆分模块）
from .board_queries import TaskQueriesMixin  # 查询/渲染域（拆分模块）


# ---------- TaskManager（第 7 课：文件级持久化的任务图 DAG）----------
class TaskManager(TaskQueriesMixin):
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
        return board_store._task_path(self.task_dir, task_id)

    def _read_task(self, task_id: int) -> dict | None:
        return board_store._read_task(self.task_dir, task_id)

    def _write_task(self, task: dict):
        board_store._write_task(self.task_dir, task)

    def _compute_next_id(self) -> int:
        return board_store._compute_next_id(self.task_dir)

    def _all_task_ids(self) -> list[int]:
        return board_store._all_task_ids(self.task_dir)

    def create(self, subject: str, blocked_by: list[int] | None = None) -> dict:
        """创建一个新任务，可选指定依赖。校验依赖任务必须存在。"""
        with self._lock:
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


def _claim_task(kw: dict) -> str:
    """第 11 课：队友显式认领任务。调用方需提供自己的 agent_id（由调度层注入）。"""
    agent = kw.get("_agent_id", "unknown")
    ok = task_manager.claim(kw["task_id"], agent)
    if ok:
        return f"Claimed task #{kw['task_id']} for {agent}"
    return f"Error: Task {kw['task_id']} could not be claimed (already claimed / not pending / blocked)"

# -*- coding: utf-8 -*-
"""TaskManager 的查询/渲染方法族（由 board.py 拆出，Mixin 模式）。

类职责：列表过滤 / 单查 / 可执行集 / 未认领集 / 依赖阻塞判定 /
看板渲染 / 全完成判定——纯读操作，不含写。
生命周期：TaskManager 继承本 Mixin 组合使用。
"""
from ....config import logger


class TaskQueriesMixin:
    """查询与渲染方法族（self 依赖 TaskManager 的存储基座）。"""

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

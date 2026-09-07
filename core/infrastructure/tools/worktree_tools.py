# -*- coding: utf-8 -*-
"""Worktree tool wrapper implementations (moved from core/tools.py)."""


def _worktree_remove(kw: dict) -> str:
    """第 12 课：拆除 worktree 的工具封装。"""
    from .tools_runtime import worktree_manager
    worktree_manager.worktree_remove(
        kw["task_id"],
        complete_task=kw.get("complete_task", True),
        merge=kw.get("merge", False),
    )
    merged = "（已合并回主分支）" if kw.get("merge", False) else ""
    completed = "任务已标记 completed" if kw.get("complete_task", True) else "任务保留原状态"
    return f"Removed worktree for task #{kw['task_id']}{merged} | {completed}"

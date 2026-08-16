# -*- coding: utf-8 -*-
"""Runtime singletons and wiring for tool implementations (moved from core/tools.py).

This module owns the cross-module wiring that used to live at the bottom of
core/tools.py: WorktreeManager instantiation and TeamCoordinator wiring.
"""
from . import config
from .config import logger
from .protocol import coordinator
from .tools_tasks import task_manager
from .tools_team import teammate_manager
from .worktree import WorktreeManager

# ---------- 第 12 课接线：WorktreeManager 注入（打破循环依赖） ----------
# worktree.py 不 import tools.py（TaskManager 由构造参数注入），因此可以在这里
# 安全地 import worktree 并把真实单例挂到占位符上。
worktree_manager = WorktreeManager(str(config.WORKDIR), task_manager)
logger.info(
    f"第 12 课 wiring 完成 | worktree_manager 已注入 | "
    f"root={config.WORKDIR} | 现有 worktree 注册数={len(worktree_manager._load_index())}"
)

# ---------- 第 10 课接线：协调器注入消息总线 / 团队名册（打破循环依赖） ----------
coordinator.wire(
    bus=teammate_manager.bus,
    team=teammate_manager.team,
    force_shutdown_fn=teammate_manager.shutdown,
)

# -*- coding: utf-8 -*-
"""任务域包：TodoManager（规划清单）+ TaskManager（任务图 DAG）。

由单文件 tasks.py 拆分；再导出保持旧导入路径兼容。
"""
from .todo import todo_manager  # noqa: F401
from .board import task_manager, _claim_task  # noqa: F401

# -*- coding: utf-8 -*-
"""interfaces 层包入口：全部抽象契约（Protocol），不含实现。

services 层只允许 import 本包与 domain；任何 concrete 类只在
infrastructure 与 bootstrap 出现（依赖倒置，Rule 2.2）。
"""
from .event_writer import EventWriter
from .model_client import ModelClient, ToolSchema
from .session_store import SessionStore
from .skill_repository import SkillRepository
from .tool_registry import ToolDefinition, ToolRegistry

__all__ = [
    "EventWriter",
    "ModelClient",
    "ToolSchema",
    "SessionStore",
    "SkillRepository",
    "ToolDefinition",
    "ToolRegistry",
]

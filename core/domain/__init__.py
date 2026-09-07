# -*- coding: utf-8 -*-
"""domain 层包入口：纯类型与异常，零副作用、零 IO、零第三方依赖。

分层约定（agent.md Rule 2）：
    domain    —— 纯类型（消息/事件/会话/异常）
    interfaces—— 抽象契约（Protocol）
    services  —— 业务编排（只依赖 domain + interfaces）
    infrastructure —— 副作用实现（OpenAI SDK、文件、进程、工具）
"""
from .errors import (
    ConfigError,
    ContextOverflowError,
    EngineError,
    LoopAbortError,
    SandboxViolationError,
    SessionStoreError,
    ToolExecutionError,
)
from .events import RoundReport, StreamDelta
from .messages import (
    AssistantMessage,
    Message,
    ToolCallSpec,
    ToolResultMessage,
    UserMessage,
    from_transport,
    transport_messages,
    typed_messages,
)
from .session import Mode, SandboxMode, SessionContext

__all__ = [
    "ConfigError", "ContextOverflowError", "EngineError", "LoopAbortError",
    "SandboxViolationError", "SessionStoreError",
    "ToolExecutionError", "RoundReport", "StreamDelta",
    "AssistantMessage", "Message", "ToolCallSpec", "ToolResultMessage",
    "UserMessage", "from_transport", "transport_messages", "typed_messages",
    "Mode", "SandboxMode", "SessionContext",
]

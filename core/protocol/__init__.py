# -*- coding: utf-8 -*-
"""团队协议包：状态机 + 追踪器 + 协调器 + 上下文注入。
由单文件 protocol.py 拆分；再导出保持兼容。

[PROTOCOL] 前缀：MessageBus 里标记协议消息，不走普通任务 Agent Loop。
"""
from .tracker import ProtocolRequest, ProtocolTracker, RequestStatus  # noqa: F401
from .coordinator import (AgentWriteTracker, TeamCoordinator,  # noqa: F401
                          coordinator, PROTOCOL_FLAG)
from .inject import inject_pending_requests, parse_protocol_flag  # noqa: F401

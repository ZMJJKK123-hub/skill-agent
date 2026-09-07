# -*- coding: utf-8 -*-
"""队友系统包：JSONL 收件箱 + 持久 Agent 管理。
由单文件 team.py 拆分；再导出保持兼容。
"""
from .bus import MessageBus  # noqa: F401
from .manager import (TeammateManager, TeammateConfig,  # noqa: F401
                      teammate_manager, maybe_reinject_identity,
                      _submit_plan, _respond_to_request, _is_safe_agent_name)

# -*- coding: utf-8 -*-
"""loop 包入口：主循环引擎与门面函数。

对外 API：
    AgentLoopEngine — 引擎实例（daemon 模式逐 turn 复用）。
    run_agent_loop(messages) — 兼容旧 core.agent.agent_loop 签名的
    进程级门面（transport dict 进出），P3/P5 接入方切换点。
"""
from .deps import LoopDeps
from .model_call import get_reasoning_sink, set_reasoning_sink
from .runner import AgentLoopEngine
from .state import LoopState

__all__ = [
    "AgentLoopEngine",
    "LoopDeps",
    "LoopState",
    "run_agent_loop",
    "set_reasoning_sink",
    "get_reasoning_sink",
]


def run_agent_loop(messages: list[dict]) -> str:
    """进程级门面：构建引擎并执行一个 turn（签名兼容旧 agent_loop）。

    Globals Used:
        无（全部依赖由 Settings.from_env 显式构建）。
    Args:
        messages: transport 格式消息（空列表 = 从事件日志重放）。
    Returns:
        最终回复文本。
    """
    from ...bootstrap import build_engine  # 延迟导入避免环
    from ...domain.messages import typed_messages
    from ...infrastructure.config import Settings
    engine = build_engine(Settings.from_env())
    return engine.run(typed_messages(messages))

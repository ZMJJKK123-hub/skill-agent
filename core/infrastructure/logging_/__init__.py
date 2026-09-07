# -*- coding: utf-8 -*-
"""logging_ 包入口：统一 logger 与 run.log 协议写入器。

命名说明：目录名带下划线以避免与标准库 logging 在任何相对导入
语境下混淆（agent.md Rule 1 注释基线）。
"""
from .logger import agent_log_path, configure_root_logger, get_logger, log_failure
from .runlog_writer import MemoryEventWriter, RunlogEventWriter

__all__ = [
    "agent_log_path",
    "configure_root_logger",
    "get_logger",
    "log_failure",
    "MemoryEventWriter",
    "RunlogEventWriter",
]

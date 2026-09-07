# -*- coding: utf-8 -*-
"""统一 logger 工厂（infrastructure 层）。

按 agent.md Rule 2.5：禁 print（协议输出走 EventWriter），全部
运行轨迹用统一 logger 输出到 agent.log；级别语义——
DEBUG 诊断细节 / INFO 关键生命周期 / WARNING 可恢复降级 /
ERROR 失败与违约（带上下文与堆栈）。
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

#: agent.log 的固定文件名（写在进程 cwd，与会话目录绑定）。
LOG_FILENAME = "agent.log"

#: 输出格式：时间 [级别] 消息（与旧 core/config.py 逐字节一致，
#: 便于既有日志检索习惯延续）。
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

_configured = False  # 模块级哨兵：basicConfig 只允许生效一次


def _ensure_utf8_streams() -> None:
    """输入：无。返回：无。职责：把 stdout/stderr 强制 UTF-8（Windows GBK 防崩）。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            # 非标准流（已被测试替换/重定向）无 reconfigure——跳过即可。
            pass


def configure_root_logger() -> logging.Logger:
    """初始化并返回项目根 logger "agent"（幂等）。

    Globals Used:
        _configured — 模块级哨兵，防止重复 basicConfig。
        LOG_FILENAME / LOG_FORMAT — 本模块常量。
    Returns:
        根 logger；重复调用只返回已配置实例。
    """
    global _configured
    _ensure_utf8_streams()
    root = logging.getLogger("agent")
    if not _configured and not root.handlers:
        logging.basicConfig(
            filename=LOG_FILENAME,
            level=logging.INFO,
            format=LOG_FORMAT,
            encoding="utf-8",
        )
        _configured = True
    return root


def get_logger(name: str) -> logging.Logger:
    """取 "agent.<name>" 子 logger（自动确保根已配置）。

    Args:
        name: 子模块名（如 "loop.runner" → logger "agent.loop.runner"）。
    Returns:
        配置完毕的 logger 实例。
    """
    configure_root_logger()
    return logging.getLogger(f"agent.{name}")


def log_failure(logger: logging.Logger, action: str, exc: Exception) -> None:
    """按 ERROR 级别记录一次失败（上下文 + 堆栈，Rule 2.5）。

    Args:
        logger: 目标 logger。
        action: 正在做什么（人读短语，如 "保存断点"）。
        exc: 捕获到的异常。
    """
    logger.error("%s失败 | %s: %s", action, type(exc).__name__, exc,
                 exc_info=exc)


def agent_log_path() -> Path:
    """输入：无。返回：当前 cwd 下 agent.log 的绝对路径（排障指引用）。"""
    return Path.cwd() / LOG_FILENAME

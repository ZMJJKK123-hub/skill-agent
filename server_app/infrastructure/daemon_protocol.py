# -*- coding: utf-8 -*-
"""daemon 文件协议（server_app/infrastructure 层）。

server 侧对 .chat/ 运行时文件的读取契约——run_task 子进程（见
services/daemon_runner.py 的 DaemonFiles 写侧）与 server（本模块读侧）
围绕同一组文件协作，读写口径集中在这两个模块，消灭两处漂移：
    .chat/daemon.state — waiting（空闲=上一轮完成）| working（跑轮中）
    .chat/daemon.pid   — daemon pid（重启清理遗留进程）
    .chat/pending.jsonl — 插话队列（由 core FileSessionStore 持有格式）
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.infrastructure.logging_.logger import get_logger
from core.infrastructure.session_files import FileSessionStore

logger = get_logger("server.daemon_protocol")

#: daemon 状态的合法取值（其他值视为无状态文件）。
VALID_STATES = ("waiting", "working")


def read_daemon_state(session_root: Path) -> Optional[str]:
    """输入：会话根。返回：daemon.state（waiting|working）；无/坏值 None。"""
    try:
        val = (session_root / ".chat" / "daemon.state").read_text(
            encoding="utf-8").strip()
        return val if val in VALID_STATES else None
    except OSError:
        return None


def clear_daemon_files(session_root: Path) -> None:
    """输入：会话根。返回：无。职责：daemon 被强杀时清 pid/state（写侧 finally 不执行）。"""
    for name in ("daemon.pid", "daemon.state"):
        try:
            (session_root / ".chat" / name).unlink(missing_ok=True)
        except OSError as e:
            logger.warning("daemon 文件清理失败 | %s | err=%s", name, e)


def pending_count(session_root: Path) -> int:
    """输入：会话根。返回：插话队列剩余条数（IO 异常按 0）。"""
    try:
        return FileSessionStore(str(session_root)).pending_count()
    except Exception as e:
        logger.warning("pending 计数失败（按 0）: %s", e)
        return 0


def enqueue_pending(session_root: Path, content: str,
                    images: Optional[list[str]] = None) -> None:
    """把运行中用户消息排入队列（daemon 一轮消费一条）。"""
    FileSessionStore(str(session_root)).enqueue_pending(content, images)


def has_working_checkpoint(session_root: Path) -> bool:
    """输入：会话根。返回：是否存在断点（暂停判定：进程没了但断点在）。"""
    return (session_root / ".chat" / "working.jsonl").exists()

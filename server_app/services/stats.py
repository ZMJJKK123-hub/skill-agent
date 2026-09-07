# -*- coding: utf-8 -*-
"""会话状态汇总（server_app/services 层；原 _session_stats/_daemon_state 迁移）。

daemon 状态机（chat 常驻进程的空闲/工作判定）是本模块核心：
    waiting + pending>0 → 视同新轮开始（防前端秒提旧回复，实测修复）；
    working 首次出现 → 重置计时；回到 waiting → 锁定一次结束时刻。
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

from core.infrastructure.logging_.logger import get_logger

from infrastructure.daemon_protocol import (pending_count,
                                              read_daemon_state)
from .session_manager import Session

logger = get_logger("server.stats")

#: 产物统计时跳过的目录（运行时/只读参考，不算产物）。
STATS_SKIP_DIRS = {".worktrees", ".team", ".tasks", ".transcripts",
                   "__pycache__", ".git", "mc_java_sources"}


def daemon_state(sess: Session) -> Optional[str]:
    """输入：会话。返回：daemon.state（仅进程存活时有意义；否则 None）。"""
    if sess.proc is None or sess.proc.poll() is not None:
        return None
    return read_daemon_state(sess.mod_dir.parent)


def _count_artifacts(mod_dir: Path) -> "tuple[int, int]":
    """输入：mod 目录。返回：(文件数, 总字节数)（跳过运行时目录）。"""
    file_count = total_bytes = 0
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d not in STATS_SKIP_DIRS]
        for fn in files:
            try:
                total_bytes += (Path(root) / fn).stat().st_size
                file_count += 1
            except OSError:
                continue
    return file_count, total_bytes


def _has_jar(mod_dir: Path) -> bool:
    """输入：mod 目录。返回：dist/ 下是否存在 jar（收尾构建成功标志）。"""
    dist = mod_dir / "dist"
    try:
        return dist.is_dir() and any(dist.glob("*.jar"))
    except OSError:
        return False


def session_stats(sess: Session) -> dict:
    """汇总会话状态：运行状态 / 耗时 / 产物统计（含 daemon 状态机维护）。

    Globals Used: 无（状态写回 sess 自身字段）。
    Args:
        sess: 目标会话。
    Returns:
        {session_id, state(running|finished|pending), running, finished,
         started_at, finished_at, elapsed, file_count, total_bytes, has_jar}。
    """
    daemon_st = daemon_state(sess)
    proc_alive = sess.proc is not None and sess.proc.poll() is None
    daemon_idle = daemon_st == "waiting" and proc_alive
    daemon_working = daemon_st == "working" and proc_alive

    if daemon_idle and pending_count(sess.mod_dir.parent) > 0:
        # 用户刚发消息、daemon 尚未消费（最长 0.5s 窗口）：不能算 finished，
        # 否则前端把上一轮 log_tail 误提取为本次回复（实测秒回旧回复）。
        daemon_idle = False
        if sess.daemon_prev_state == "waiting":
            sess.finished_at = None
            sess.started_at = time.time()

    running = proc_alive and not daemon_idle
    finished = ((sess.proc is not None and not proc_alive)
                or (sess.proc is None and sess.finished_at is not None)
                or daemon_idle)
    state = "running" if running else ("finished" if finished else "pending")

    if daemon_working and sess.daemon_prev_state == "waiting":
        sess.finished_at = None
        sess.started_at = time.time()  # 新轮开始：elapsed 重新起算
    sess.daemon_prev_state = daemon_st
    if daemon_idle and sess.finished_at is None:
        sess.finished_at = time.time()  # 幂等锁定本轮结束时刻

    file_count, total_bytes = _count_artifacts(sess.mod_dir)
    elapsed = _elapsed(sess, running, finished)
    return {"session_id": sess.id, "state": state, "running": running,
            "finished": finished, "started_at": sess.started_at,
            "finished_at": sess.finished_at, "elapsed": elapsed,
            "file_count": file_count, "total_bytes": total_bytes,
            "has_jar": _has_jar(sess.mod_dir)}


def _elapsed(sess: Session, running: bool, finished: bool) -> Optional[int]:
    """输入：会话 + 状态。返回：耗时秒数（未开始返回 None；幂等锁定结束时刻）。"""
    if not sess.started_at:
        return None
    if (sess.finished_at is None and sess.proc is not None
            and not running and finished):
        sess.finished_at = time.time()
    end = sess.finished_at if sess.finished_at else time.time()
    return int(end - sess.started_at)


def read_log_tail(log_path: Path, max_chars: int = 20000) -> str:
    """输入：日志路径。返回：尾部预览（只读尾部，避免全量读大日志）。"""
    if not log_path.exists():
        return ""
    try:
        size = log_path.stat().st_size
        with log_path.open("r", encoding="utf-8", errors="replace") as f:
            if size > max_chars:
                f.seek(size - max_chars)
            return f.read()
    except OSError as e:
        logger.warning("日志尾部读取失败: %s", e)
        return ""


def session_title(session_dir: Path) -> str:
    """输入：会话目录。返回：侧栏标题（首条 user 消息截 24 字，无则 ID 前 8 位）。"""
    conv = session_dir / ".chat" / "conversation.jsonl"
    import json
    try:
        for line in conv.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and msg.get("role") == "user":
                text = str(msg.get("content", "")).strip()
                if text:
                    return text if len(text) <= 24 else text[:24] + "…"
    except OSError:
        pass
    return session_dir.name[:8]

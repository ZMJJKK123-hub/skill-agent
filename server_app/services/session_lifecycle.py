# -*- coding: utf-8 -*-
"""会话生命周期操作（由 session_manager.py 拆出）。

类职责：purge（彻底删除）/ kill（暂停用）/ reset（重置工作区）/
孤儿清理——全部围绕 Session 的进程与磁盘副作用。
生命周期：api 层与 session_manager 调用；模块级单例状态在
session_manager.sessions。
"""
import shutil
import time
from pathlib import Path

from infrastructure.process_governor import (kill_session_game_processes,
                                              purge_session_dir)
from infrastructure.session_disk import SessionDisk
from .session_manager import SESSIONS_DIR, Session, get_session, sessions

def purge_session(sess: Session) -> None:
    """彻底清理会话：kill 子进程 + 杀游戏/Gradle 进程 + 删目录 + 移除记录。"""
    if sess.proc is not None and sess.proc.poll() is None:
        try:
            sess.proc.kill()
            sess.proc.wait(timeout=5)
        except Exception as e:
            logger.warning("子进程终止失败（忽略）: %s", e)
    sessions.pop(sess.id, None)
    session_root = sess.mod_dir.parent
    kill_session_game_processes(session_root)
    purge_session_dir(session_root)


def purge_session_for_user(session_id: str, username: str,
                           safe_id: bool) -> bool:
    """删除接口专用：先校验归属再清理（防跨用户删除）。

    Args:
        session_id: 会话 ID。
        username: 当前用户。
        safe_id: session_id 已通过安全校验（未通过直接 False）。
    Returns:
        是否执行了清理（归属他人/非法 ID 返回 False）。
    """
    if not safe_id:
        return False
    sess = sessions.get(session_id)
    if sess is not None:
        if sess.owner != username:
            return False
        purge_session(sess)
        return True
    owner = SessionDisk(SESSIONS_DIR / session_id).read_owner()
    if owner and owner != username:
        return False
    purge_session_dir(SESSIONS_DIR / session_id)
    return True


def kill_session_process(sess: Session) -> None:
    """输入：会话。返回：无。职责：杀运行中的子进程（暂停/重置共用）。"""
    if sess.proc is not None and sess.proc.poll() is None:
        try:
            sess.proc.kill()
            sess.proc.wait(timeout=5)
        except Exception as e:
            logger.warning("子进程终止失败（忽略）: %s", e)


def reset_session_workspace(sess: Session, copy_template) -> None:
    """重置会话：杀进程 + 清运行态 + 重建骨架（保留 id/key/配置）。

    Args:
        sess: 目标会话。
        copy_template: 模板复制函数（services/templates 提供，避免环依赖）。
    """
    kill_session_process(sess)
    sess.proc = None
    sess.started_at = None
    sess.finished_at = None
    sess.result = None
    sess.event_cursor = None
    shutil.rmtree(sess.mod_dir, ignore_errors=True)
    if sess.log_path.exists():
        try:
            sess.log_path.unlink()
        except OSError as e:
            logger.warning("run.log 清理失败: %s", e)
    copy_template(sess.game, sess.mod_dir, sess.loader, sess.version)


def cleanup_orphan_sessions() -> None:
    """清理从未生成过的废弃会话目录（无 run.log/mod.zip 且超时未访问）。"""
    if not SESSIONS_DIR.exists():
        return
    now = time.time()
    for child in SESSIONS_DIR.iterdir():
        if not child.is_dir():
            continue
        if (child / "run.log").exists() or (child / "mod.zip").exists():
            continue
        try:
            if now - child.stat().st_mtime < ORPHAN_TTL_S:
                continue
        except OSError:
            continue
        sess = sessions.get(child.name)
        if sess:
            purge_session(sess)
        else:
            purge_session_dir(child)
        logger.info("清除废弃会话 %s", child.name)

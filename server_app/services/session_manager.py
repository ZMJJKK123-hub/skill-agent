# -*- coding: utf-8 -*-
"""会话管理（server_app/services 层）。

Session 运行时实体 + 内存会话表 + 磁盘恢复 + 废弃会话清理。
生命周期入口（api 层只做参数转换，全部业务在这里）：
    create → prepare_mod（模板复制见 templates 模块）→ start_task
    （见 task_dispatcher）→ pause/resume/delete/reset。
"""
from __future__ import annotations

import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

from core.infrastructure.logging_.logger import get_logger

from infrastructure.process_governor import (kill_session_game_processes, 
                                               kill_stale_daemon,
                                               purge_session_dir,
                                               rmtree_with_retry)
from infrastructure.session_disk import SessionDisk

logger = get_logger("server.session_manager")

#: 目录布局（服务器项目根下）。
BASE_DIR = Path(__file__).resolve().parents[2]
SESSIONS_DIR = BASE_DIR / "data" / "sessions"
TEMPLATES_DIR = BASE_DIR / "mod_templates"

#: 废弃会话判定：无 run.log 且无 mod.zip，超时未访问即清理。
ORPHAN_TTL_S = 60 * 60


class Session:
    """一个用户的生成会话：独立工作目录 + 子进程运行态。

    类职责：会话身份 + 配置 + 进程运行态的内存载体。
    实例属性：
        id/mod_dir/api_key/owner —— 身份与归属（owner 空 = 历史遗留）。
        game/loader/version/mode —— 工作区定位与运行模式记忆。
        model/base_url/sandbox/vision_*/auto_mode/search_api_key —— 引擎配置。
        proc/started_at/finished_at/result —— 子进程运行态。
        event_cursor/daemon_prev_state/daemon_mode —— 轮询与 daemon 状态机。
    生命周期：创建/恢复进内存表 → 多轮任务复用 → 删除/重置销毁。
    """

    def __init__(self, session_id: str, mod_dir: Path, api_key: str = "",
                 owner: str = "", game: str = "minecraft", loader: str = "",
                 version: str = "", model: str = "", base_url: str = "",
                 sandbox: str = "full-access", vision_enabled: bool = True,
                 vision_api_key: str = "", vision_base_url: str = "",
                 vision_model: str = "", auto_mode: bool = False,
                 search_api_key: str = "") -> None:
        """输入：身份 + 全部可配置项。返回：无。职责：字段赋值（全部见类注释）。"""
        self.id = session_id
        self.mod_dir = mod_dir
        self.api_key = api_key
        self.owner = owner
        self.game = game
        self.loader = loader
        self.version = version
        self.mode = "chat"  # 运行模式记忆（持久化于 mode.txt）
        self.model = model
        self.base_url = base_url
        self.sandbox = sandbox
        self.vision_enabled = vision_enabled
        self.vision_api_key = vision_api_key
        self.vision_base_url = vision_base_url
        self.vision_model = vision_model
        self.auto_mode = auto_mode
        self.search_api_key = search_api_key
        self.proc: Optional[subprocess.Popen] = None
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.result: Optional[str] = None
        self.log_path = mod_dir.parent / "run.log"
        self.event_cursor: Optional[str] = None
        self.daemon_prev_state: Optional[str] = None
        self.daemon_mode: Optional[str] = None

    # ---------- 配置持久化（v2：重启恢复不再丢配置） ----------

    def config_fields(self) -> dict:
        """输入：无。返回：应落盘的配置字段（不含密钥类）。"""
        return {"game": self.game, "loader": self.loader,
                "version": self.version, "model": self.model,
                "base_url": self.base_url, "sandbox": self.sandbox,
                "vision_enabled": self.vision_enabled,
                "vision_base_url": self.vision_base_url,
                "vision_model": self.vision_model,
                "auto_mode": self.auto_mode}

    def persist_config(self) -> None:
        """输入：无。返回：无。职责：把非敏感配置落盘 config.json（密钥类不落）。"""
        SessionDisk(self.mod_dir.parent).write_config(self.config_fields())

    def apply_overrides(self, req) -> None:
        """输入：带可选覆盖字段的请求对象。返回：无。职责：非空字段回写会话。"""
        if getattr(req, "api_key", None):
            self.api_key = req.api_key
        for field in ("model", "base_url"):
            val = getattr(req, field, "")
            if val:
                setattr(self, field, val)
        for field in ("vision_enabled", "vision_api_key", "vision_base_url",
                      "vision_model", "auto_mode", "search_api_key"):
            val = getattr(req, field, None)
            if val is not None:
                setattr(self, field, val)


#: 内存会话表（进程级唯一；启动时从磁盘恢复历史会话）。
sessions: dict[str, Session] = {}


def get_session(session_id: str) -> Session:
    """输入：会话 ID。返回：会话实体。Raises: KeyError（api 层转 404）。"""
    sess = sessions.get(session_id)
    if not sess:
        raise KeyError(session_id)
    return sess


def create_session(api_key: str, owner: str, **config) -> Session:
    """创建轻量会话：建目录 + 落 owner/api_key/config（不复制模板）。

    Args:
        api_key: 用户 API Key（落 .chat/api_key.txt，本地模式允许）。
        owner: 归属用户名。
        **config: game/loader/version/model 等配置项。
    Returns:
        已注册进内存表的新 Session。
    """
    session_id = uuid.uuid4().hex[:12]
    mod_dir = SESSIONS_DIR / session_id / "mod"
    mod_dir.mkdir(parents=True, exist_ok=True)
    disk = SessionDisk(mod_dir.parent)
    disk.write_owner(owner)
    disk.write_api_key(api_key)
    sess = Session(session_id, mod_dir, api_key=api_key, owner=owner, **config)
    disk.write_config(sess.config_fields())
    sessions[session_id] = sess
    return sess


def restore_sessions() -> None:
    """启动时扫描 data/sessions/*/，把历史会话重建进内存表。

    api_key 自 .chat/api_key.txt 读回；game/model 等自 config.json 读回
    （v2 修复：此前这些字段重启即丢，reset 会用错模板）。
    """
    if not SESSIONS_DIR.exists():
        return
    for child in sorted(SESSIONS_DIR.iterdir()):
        if not child.is_dir() or child.name in sessions:
            continue
        kill_stale_daemon(child)  # 防双进程抢队列
        disk = SessionDisk(child)
        cfg = disk.read_config()
        sess = Session(child.name, child / "mod", api_key=disk.read_api_key(),
                       owner=disk.read_owner(), **cfg)
        sessions[child.name] = sess
        _lock_restored_times(sess, child)


def _lock_restored_times(sess: Session, session_dir: Path) -> None:
    """输入：恢复的会话 + 目录。返回：无。职责：按产物 mtime 锁定历史时间戳。"""
    zip_file = session_dir / "mod.zip"
    run_log = session_dir / "run.log"
    if zip_file.exists():
        mtime = zip_file.stat().st_mtime
        sess.started_at = mtime - 60
        sess.finished_at = mtime
        sess.result = "（历史会话，产物已生成）"
    elif run_log.exists() and run_log.stat().st_size > 0:
        mtime = run_log.stat().st_mtime
        sess.started_at = mtime - 60
        sess.finished_at = mtime
        sess.result = "（历史会话，未生成 zip）"

# 生命周期操作再导出（拆分后调用方零改动）
from .session_lifecycle import (cleanup_orphan_sessions, kill_session_process,  # noqa: E402,F401
                                purge_session, purge_session_for_user,
                                reset_session_workspace)

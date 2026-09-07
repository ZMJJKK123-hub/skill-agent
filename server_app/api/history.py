# -*- coding: utf-8 -*-
"""历史与账号路由（server_app/api 层）。

登录/注册已废弃（v1.0.1 纯本地模式）——接口冻结保留；
history/会话列表是活跃功能（auth_store 的 history 部分）。
"""
from __future__ import annotations

import datetime
import json

from fastapi import APIRouter, Header, HTTPException

import auth_store  # 历史存取（文件存储；账号部分冻结保留）
from infrastructure.process_governor import is_safe_session_id
from services.session_manager import (SESSIONS_DIR, purge_session_for_user)
from services.stats import session_title
from .deps import auth_username, owned_session
from .dto import AuthRequest, HistoryBatchDelete, HistoryEntry

router = APIRouter(prefix="/api", tags=["history"])


@router.post("/register")
def register(req: AuthRequest):
    """注册（冻结保留；成功即发 token 免二次登录）。"""
    try:
        auth_store.register(req.username, req.password)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"username": req.username.strip(),
            "token": auth_store.create_token(req.username.strip())}


@router.post("/login")
def login(req: AuthRequest):
    """登录（冻结保留；校验密码发 token）。"""
    user = auth_store.check_credentials(req.username, req.password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    return {"username": user["username"],
            "token": auth_store.create_token(user["username"])}


@router.get("/me")
def me(authorization: str = Header(default="")):
    """当前用户（前端启动时免登检查）。"""
    return {"username": auth_username(authorization)}


@router.post("/logout")
def logout(authorization: str = Header(default="")):
    """注销（吊销 token；冻结保留）。"""
    token = authorization[len("Bearer "):].strip() if authorization.startswith("Bearer ") else ""
    auth_store.revoke_token(token)
    return {"ok": True}


def _history_with_jar(username: str) -> list:
    """给历史条目注入 has_jar（磁盘检测 dist/*.jar）。"""
    history = auth_store.load_history(username)
    for h in history:
        h["has_jar"] = False
        sid = h.get("sessionId")
        dist = SESSIONS_DIR / str(sid) / "mod" / "dist"
        if sid and dist.is_dir():
            try:
                h["has_jar"] = any(dist.glob("*.jar"))
            except OSError:
                h["has_jar"] = False
    return history


@router.get("/history")
def get_history(authorization: str = Header(default="")):
    """当前用户的历史记录（含 has_jar 打包状态）。"""
    return {"history": _history_with_jar(auth_username(authorization))}


@router.put("/history")
def put_history(entry: HistoryEntry, authorization: str = Header(default="")):
    """按 session_id 去重合并一条历史记录。"""
    username = auth_username(authorization)
    history = auth_store.upsert_history(username, entry.model_dump())
    return {"history": history}


@router.delete("/history")
def delete_history(session_id: str = "", authorization: str = Header(default="")):
    """删除历史（单条/全部），同步清理会话目录（含 kill 子进程）。"""
    username = auth_username(authorization)
    if session_id:
        if not is_safe_session_id(session_id):
            raise HTTPException(400, "非法 session_id")
        auth_store.remove_history(username, session_id)
        purge_session_for_user(session_id, username, safe_id=True)
        return {"history": _history_with_jar(username)}
    # 全部删除：owner.txt 是侧栏事实来源，按 owner 扫描逐个清理
    if SESSIONS_DIR.exists():
        for child in list(SESSIONS_DIR.iterdir()):
            owner_txt = child / "owner.txt"
            if not owner_txt.exists():
                continue
            try:
                if owner_txt.read_text(encoding="utf-8").strip() != username:
                    continue
            except OSError:
                continue
            purge_session_for_user(child.name, username, safe_id=True)
    auth_store.clear_history(username)
    return {"history": []}


@router.delete("/history/batch")
def delete_history_batch(req: HistoryBatchDelete,
                         authorization: str = Header(default="")):
    """批量删除历史：逐条清历史 + 清会话目录。"""
    username = auth_username(authorization)
    for sid in req.session_ids:
        if not is_safe_session_id(sid):
            raise HTTPException(400, "非法 session_id")
        auth_store.remove_history(username, sid)
        purge_session_for_user(sid, username, safe_id=True)
    return {"history": _history_with_jar(username)}


@router.get("/sessions")
def list_sessions(authorization: str = Header(default="")):
    """按 owner 派生会话列表（扫描 owner.txt，侧栏事实来源）。"""
    username = auth_username(authorization)
    out = []
    if SESSIONS_DIR.exists():
        for child in sorted(SESSIONS_DIR.iterdir()):
            if not child.is_dir() or not (child / "owner.txt").exists():
                continue
            try:
                owner = (child / "owner.txt").read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if owner != username:
                continue
            dist = child / "mod" / "dist"
            date = ""
            try:
                date = datetime.datetime.fromtimestamp(
                    child.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                pass
            out.append({"sessionId": child.name, "owner": owner,
                        "has_jar": dist.is_dir() and any(dist.glob("*.jar")),
                        "date": date, "title": session_title(child)})
    return {"sessions": out}


@router.get("/conversation")
def conversation(session_id: str, authorization: str = Header(default="")):
    """会话对话历史 + 模式推断（打开历史会话时恢复展示模式）。"""
    sess = owned_session(session_id, auth_username(authorization))
    messages = []
    conv = sess.mod_dir.parent / ".chat" / "conversation.jsonl"
    if conv.exists():
        try:
            for line in conv.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                    messages.append(msg)
        except OSError:
            pass
    from infrastructure.session_disk import SessionDisk
    mode = SessionDisk(sess.mod_dir.parent).read_mode()
    if mode is None:  # mode.txt 缺失时按目录/历史推断
        if sess.mod_dir.exists() and any(sess.mod_dir.iterdir()):
            mode = "mod"
        elif messages:
            mode = "chat"
    return {"session_id": session_id, "messages": messages, "mode": mode}

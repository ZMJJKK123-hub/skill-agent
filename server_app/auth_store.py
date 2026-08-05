"""认证与用户历史存储（纯文件，无数据库依赖）。

职责：
  1. 用户注册 / 登录：密码 PBKDF2-SHA256 加盐哈希，绝不落明文
  2. 登录 token 管理：secrets.token_hex(32)，7 天过期，持久化文件
  3. 每用户历史记录：data/history/{username}.json，按 session_id 去重合并

文件布局（都在项目 data/ 下）：
  data/users.json           用户表 {name: {salt, hash, created_at}}
  data/auth_sessions.json   token 表 {token: {username, expires_at}}
  data/history/{name}.json  每用户历史数组
"""

import hashlib
import json
import os
import secrets
import time
from pathlib import Path

# 项目 data 目录（server_app 的上上级）
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "auth_sessions.json"
HISTORY_DIR = DATA_DIR / "history"

TOKEN_TTL = 7 * 24 * 3600  # 7 天
PBKDF2_ITERATIONS = 100_000


# ---------- 文件读写工具 ----------

def _load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return default


def _save_json(path: Path, data) -> None:
    # 确保目标文件的父目录存在（data/、data/history/ 等首次写入时）
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- 密码哈希 ----------

def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    ).hex()


# ---------- 用户注册 / 登录 ----------

def register(username: str, password: str) -> dict:
    """注册新用户。成功返回用户信息，用户名已占用抛 ValueError。"""
    name = username.strip()
    if not name:
        raise ValueError("用户名不能为空")
    if len(name) > 32:
        raise ValueError("用户名过长（最多 32 字符）")
    if len(password) < 6:
        raise ValueError("密码至少 6 位")

    users = _load_json(USERS_FILE, {})
    if name in users:
        raise ValueError("用户名已存在")

    salt = secrets.token_bytes(16)
    users[name] = {
        "salt": salt.hex(),
        "hash": _hash_password(password, salt),
        "created_at": time.time(),
    }
    _save_json(USERS_FILE, users)
    return {"username": name}


def check_credentials(username: str, password: str) -> dict | None:
    """校验用户名密码，正确返回用户信息，否则返回 None。"""
    name = username.strip()
    users = _load_json(USERS_FILE, {})
    rec = users.get(name)
    if not rec:
        return None
    salt = bytes.fromhex(rec["salt"])
    if _hash_password(password, salt) != rec["hash"]:
        return None
    return {"username": name}


# ---------- token 管理 ----------

def create_token(username: str) -> str:
    token = secrets.token_hex(32)
    sessions = _load_json(SESSIONS_FILE, {})
    sessions[token] = {
        "username": username,
        "expires_at": time.time() + TOKEN_TTL,
    }
    _save_json(SESSIONS_FILE, sessions)
    return token


def validate_token(token: str) -> str | None:
    """校验 token，返回用户名；无效/过期返回 None。"""
    if not token:
        return None
    sessions = _load_json(SESSIONS_FILE, {})
    rec = sessions.get(token)
    if not rec:
        return None
    if rec.get("expires_at", 0) < time.time():
        # 过期清理
        sessions.pop(token, None)
        _save_json(SESSIONS_FILE, sessions)
        return None
    return rec.get("username")


def revoke_token(token: str) -> None:
    sessions = _load_json(SESSIONS_FILE, {})
    if token in sessions:
        sessions.pop(token, None)
        _save_json(SESSIONS_FILE, sessions)


def prune_expired() -> None:
    """清理已过期的登录 token（auth_sessions 不随会话删除，避免登录态丢失）。"""
    sessions = _load_json(SESSIONS_FILE, {})
    now = time.time()
    expired = [t for t, rec in sessions.items() if rec.get("expires_at", 0) < now]
    if expired:
        for t in expired:
            sessions.pop(t, None)
        _save_json(SESSIONS_FILE, sessions)


# ---------- 每用户历史记录 ----------

def _history_path(username: str) -> Path:
    return HISTORY_DIR / f"{username}.json"


def load_history(username: str) -> list:
    """返回该用户的历史数组（默认空列表）。"""
    return _load_json(_history_path(username), [])


def upsert_history(username: str, entry: dict) -> list:
    """按 session_id 去重合并：已存在仅更新耗时/文件数/时间，保留首次 prompt。"""
    history = load_history(username)
    idx = next((i for i, h in enumerate(history) if h.get("sessionId") == entry.get("sessionId")), -1)
    if idx >= 0:
        old = history[idx]
        history[idx] = {
            **old,
            "elapsed": entry.get("elapsed", old.get("elapsed")),
            "fileCount": entry.get("fileCount", old.get("fileCount")),
            "date": entry.get("date") or old.get("date"),
        }
    else:
        history.insert(0, {
            "sessionId": entry.get("sessionId"),
            "game": entry.get("game") or "minecraft",
            "prompt": entry.get("prompt") or "",
            "elapsed": entry.get("elapsed"),
            "fileCount": entry.get("fileCount"),
            "date": entry.get("date") or "",
        })
    trimmed = history[:20]
    _save_json(_history_path(username), trimmed)
    return trimmed


def remove_history(username: str, session_id: str) -> list:
    """从该用户历史中移除指定 session 的记录，返回剩余历史。

    session_id 不存在时静默返回原列表（幂等）。
    """
    history = load_history(username)
    filtered = [h for h in history if h.get("sessionId") != session_id]
    if len(filtered) != len(history):
        _save_json(_history_path(username), filtered)
    return filtered


def clear_history(username: str) -> None:
    _save_json(_history_path(username), [])

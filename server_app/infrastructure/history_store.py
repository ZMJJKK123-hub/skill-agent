# -*- coding: utf-8 -*-
"""每用户历史记录存储（server_app/infrastructure 层）。

v1.0.1 纯本地单用户后的唯一存活职责（原 auth_store.py 的 history 域
迁入；账号/密码/token 域随登录功能废弃删除）。

存储：data/history/{username}.json —— 数组，按 session_id 去重合并，
保留最近 20 条。
"""
from __future__ import annotations

import json
from pathlib import Path

#: 项目 data 目录（server_app 的上上级）。
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_DIR = DATA_DIR / "history"

#: 每用户历史上限（最早的被挤掉）。
MAX_HISTORY_ENTRIES = 20


def _load_json(path: Path, default):
    """输入：路径 + 默认值。返回：解析结果（缺失/损坏回退默认）。"""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return default


def _save_json(path: Path, data) -> None:
    """输入：路径 + 数据。返回：无。职责：落盘（自动建父目录）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _history_path(username: str) -> Path:
    """输入：用户名。返回：该用户的历史文件路径。"""
    return HISTORY_DIR / f"{username}.json"


def load_history(username: str) -> list:
    """输入：用户名。返回：历史数组（默认空）。"""
    return _load_json(_history_path(username), [])


def upsert_history(username: str, entry: dict) -> list:
    """按 session_id 去重合并：已存在仅更新耗时/文件数/时间，保留首 prompt。"""
    history = load_history(username)
    idx = next((i for i, h in enumerate(history)
                if h.get("sessionId") == entry.get("sessionId")), -1)
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
    trimmed = history[:MAX_HISTORY_ENTRIES]
    _save_json(_history_path(username), trimmed)
    return trimmed


def remove_history(username: str, session_id: str) -> list:
    """移除指定 session 的记录（幂等），返回剩余历史。"""
    history = load_history(username)
    filtered = [h for h in history if h.get("sessionId") != session_id]
    if len(filtered) != len(history):
        _save_json(_history_path(username), filtered)
    return filtered


def clear_history(username: str) -> None:
    """清空该用户历史。"""
    _save_json(_history_path(username), [])

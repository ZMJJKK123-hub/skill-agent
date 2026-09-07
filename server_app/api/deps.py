# -*- coding: utf-8 -*-
"""api 层公共依赖（server_app/api 层）。

认证与归属校验（纯本地模式：恒 local 用户）；会话获取与 404/403 转换。
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from services.session_manager import Session, sessions


def auth_username(authorization: str = Header(default="")) -> str:
    """纯本地模式：恒返回固定本地用户（登录前端已移除，v1.0.1）。

    恢复多用户时改回 token 校验即可（auth_store 接口保留）。
    """
    return "local"


def owned_session(session_id: str, username: str) -> Session:
    """输入：会话 ID + 用户名。返回：归属校验通过的会话。

    Raises:
        HTTPException: 404（不存在）/ 403（非本人或未绑定）。
    """
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")
    if not sess.owner or sess.owner != username:
        raise HTTPException(403, "无权访问该会话")
    return sess



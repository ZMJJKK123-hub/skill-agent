# -*- coding: utf-8 -*-
"""会话生命周期路由（server_app/api 层）。

只做协议转换与参数校验；业务在 services 层。
"""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse

from infrastructure.session_disk import SessionDisk
from services import templates
from services.session_manager import (create_session, purge_session,
                                        reset_session_workspace)
from services.stats import session_stats
from services.uploads import valid_upload_name
from .deps import auth_username, owned_session
from .dto import SessionRequest

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/session")
def create(req: SessionRequest, authorization: str = Header(default="")):
    """创建会话：轻量（建目录 + 绑用户 + 落配置），不复制模板。"""
    sess = create_session(req.api_key, auth_username(authorization),
                          game=req.game, loader=req.loader,
                          version=req.version, model=req.model,
                          base_url=req.base_url, sandbox=req.sandbox,
                          vision_enabled=req.vision_enabled,
                          vision_api_key=req.vision_api_key,
                          vision_base_url=req.vision_base_url,
                          vision_model=req.vision_model,
                          auto_mode=req.auto_mode,
                          search_api_key=req.search_api_key)
    return {"session_id": sess.id, "mod_dir": str(sess.mod_dir)}


@router.post("/session/mod")
def prepare_mod(session_id: str, authorization: str = Header(default=""),
                api_key: str = Header(default="", alias="X-API-Key"),
                game: str = "", loader: str = "", version: str = "",
                model: str = "", base_url: str = "", sandbox: str = ""):
    """为会话准备 mod 工作区：复制模板 + junction（幂等）+ git init。

    query 参数非空时同步覆盖会话配置（空 = 沿用创建时的值）。
    """
    sess = owned_session(session_id, auth_username(authorization))
    for field, val in (("game", game), ("loader", loader), ("version", version),
                       ("model", model), ("base_url", base_url),
                       ("sandbox", sandbox)):
        if val:
            setattr(sess, field, val)
    already = templates.has_template_content(sess.mod_dir)
    if not already:
        templates.copy_template(sess.game, sess.mod_dir, sess.loader,
                                sess.version)
        templates.init_session_git(sess.mod_dir)
    SessionDisk(sess.mod_dir.parent).write_config(sess.config_fields())
    return {"session_id": sess.id, "mod_ready": True, "already": already}


@router.delete("/session")
def delete(session_id: str, authorization: str = Header(default="")):
    """删除会话：kill 子进程 + 清游戏/Gradle 进程 + 删目录（幂等）。"""
    sess = owned_session(session_id, auth_username(authorization))
    purge_session(sess)
    return {"ok": True}


@router.post("/session/reset")
def reset(session_id: str, authorization: str = Header(default="")):
    """重置会话：保留 id/Key/配置，重建初始骨架。"""
    sess = owned_session(session_id, auth_username(authorization))
    reset_session_workspace(sess, templates.copy_template)
    return {"session_id": sess.id, "status": "reset"}


@router.get("/session")
def status(session_id: str, authorization: str = Header(default="")):
    """会话状态汇总：运行状态 / 耗时 / 产物统计。"""
    sess = owned_session(session_id, auth_username(authorization))
    return session_stats(sess)


@router.get("/session/image")
def image(session_id: str, name: str, authorization: str = Header(default="")):
    """返回会话上传图片附件（历史消息回显）。"""
    sess = owned_session(session_id, auth_username(authorization))
    if not valid_upload_name(name):
        raise HTTPException(400, "非法图片文件名")
    p = sess.mod_dir.parent / ".chat" / "uploads" / name
    if not p.is_file():
        raise HTTPException(404, "图片不存在")
    return FileResponse(p)

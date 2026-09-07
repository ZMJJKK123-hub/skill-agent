# -*- coding: utf-8 -*-
"""产物与观察路由（server_app/api 层）：下载/文件树/事件流/日志/模板列表。"""
from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import Response

import log_events  # 事件流/文件树解析（纯函数模块，server_app 同级）
from services.packaging import build_source_zip, find_built_jar
from services.session_manager import TEMPLATES_DIR
from .deps import auth_username, owned_session

router = APIRouter(prefix="/api", tags=["artifacts"])


@router.get("/download")
def download_zip(session_id: str, authorization: str = Header(default="")):
    """下载源码 zip（排除构建产物；mtime 缓存 + 原子替换）。"""
    sess = owned_session(session_id, auth_username(authorization))
    zip_path = build_source_zip(sess.mod_dir.parent, sess.mod_dir)
    # 一次性读内存返回：绕开 h11 大响应体 Content-Length bug
    return Response(content=zip_path.read_bytes(), media_type="application/zip",
                    headers={"Content-Disposition":
                             f'attachment; filename="mod-{session_id}-src.zip"'})


@router.get("/download/jar")
def download_jar(session_id: str, authorization: str = Header(default="")):
    """下载构建好的 mod jar（dist/ 首个；无则 400）。"""
    sess = owned_session(session_id, auth_username(authorization))
    jar = find_built_jar(sess.mod_dir)
    if jar is None:
        raise HTTPException(400, "该会话尚未打包 jar（未构建或构建失败）")
    return Response(content=jar.read_bytes(), media_type="application/java-archive",
                    headers={"Content-Disposition":
                             f'attachment; filename="mod-{session_id}.jar"'})


@router.get("/games")
def list_games():
    """动态枚举 mod_templates/ 下的可用游戏模板。"""
    games = []
    if TEMPLATES_DIR.exists():
        for p in sorted(TEMPLATES_DIR.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                desc = ""
                readme = p / "README.md"
                if readme.exists():
                    try:
                        first = readme.read_text(encoding="utf-8").strip().splitlines()
                        if first:
                            desc = first[0].lstrip("# ").strip()
                    except OSError:
                        pass
                games.append({"id": p.name, "name": p.name, "description": desc})
    if not games:
        games = [{"id": "minecraft", "name": "minecraft", "description": ""}]
    return {"games": games}


@router.get("/events")
def events(session_id: str, cursor: str = "",
           authorization: str = Header(default="")):
    """增量拉取 agent 事件流（cursor=JSON 字节偏移，前端回传续读）。"""
    sess = owned_session(session_id, auth_username(authorization))
    try:
        cur = json.loads(cursor) if cursor else None
    except json.JSONDecodeError:
        cur = None
    result = log_events.build_event_stream(sess.mod_dir.parent, cur)
    sess.event_cursor = result["cursor"]  # 前端可不传 cursor 直接续传
    return {"session_id": session_id, "events": result["events"],
            "cursor": result["cursor"]}


@router.get("/files")
def files(session_id: str, path: str = "",
          authorization: str = Header(default="")):
    """文件树 / 单文件预览（产物下载前检视）。"""
    sess = owned_session(session_id, auth_username(authorization))
    if not path:
        return {"session_id": session_id,
                "tree": log_events.build_file_tree(sess.mod_dir)}
    preview = log_events.read_file_preview(sess.mod_dir, path)
    if "error" in preview:
        raise HTTPException(400, preview["error"])
    return {"session_id": session_id, "path": path, **preview}


@router.get("/log")
def raw_log(session_id: str, offset: int = 0,
            authorization: str = Header(default="")):
    """原始 run.log 增量拉取（事件流的兜底通道）。"""
    sess = owned_session(session_id, auth_username(authorization))
    if not sess.log_path.exists():
        return {"content": "", "offset": 0}
    size = sess.log_path.stat().st_size
    with sess.log_path.open("r", encoding="utf-8", errors="replace") as f:
        if offset > 0:
            f.seek(offset)
        content = f.read()
    return {"content": content, "offset": size}

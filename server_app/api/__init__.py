# -*- coding: utf-8 -*-
"""api 层包入口：应用工厂（组装全部路由 + 静态托管 + 启动钩子）。

表现层只做协议转换；业务在 services、副作用在 infrastructure。
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.session_manager import cleanup_orphan_sessions, restore_sessions
from . import artifacts, history, sessions, tasks
from core.config import logger  # 统一日志：降级路径记录

#: 前端静态产物与 debug 游乐场目录。
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
DEBUG_DIR = Path(__file__).resolve().parent.parent / "debug"

#: 30 分钟一次的废弃会话清理周期。
ORPHAN_CLEANUP_INTERVAL_S = 30 * 60


def _mount_debug_routes(app: FastAPI) -> None:
    """输入：应用实例。返回：无。职责：挂载 /debug 维护页路由组。

    含入口页、静态文件（双保险防路径穿越）。
    Globals Used: DEBUG_DIR。
    """
    @app.get("/debug")
    @app.get("/debug/")
    async def debug_page():
        """debug 维护页入口。"""
        idx = DEBUG_DIR / "index.html"
        if idx.exists():
            return FileResponse(str(idx), headers={"Cache-Control": "no-cache"})
        return {"error": "debug page not found"}

    @app.get("/debug/{filepath:path}")
    async def debug_static(filepath: str):
        """debug 静态文件（双保险防路径穿越）。"""
        root = DEBUG_DIR.resolve()
        f = (root / filepath).resolve()
        if not f.is_relative_to(root) or not f.is_file():
            raise HTTPException(404, "Not found")
        return FileResponse(str(f), headers={"Cache-Control": "no-cache"})


def _mount_index_route(app: FastAPI) -> None:
    """输入：应用实例。返回：无。职责：挂载 / 首页与 /api/health。

    首页 no-cache 防旧 bundle；缺失时兜底 debug 维护页。
    Globals Used: WEB_DIR/DEBUG_DIR。
    """
    @app.get("/api/health")
    def health():
        """debug 页面探活。"""
        return {"status": "ok", "service": "skill-agent web", "port": 8000}

    @app.get("/")
    def index():
        """首页（no-cache 防旧 bundle；缺失时兜底 debug 维护页）。"""
        index_file = WEB_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), headers={"Cache-Control": "no-cache"})
        debug_idx = DEBUG_DIR / "index.html"
        if debug_idx.exists():
            return FileResponse(str(debug_idx), headers={"Cache-Control": "no-cache"})
        return {"error": "index.html not found", "web_dir": str(WEB_DIR)}


def create_app() -> FastAPI:
    """构建 FastAPI 应用（路由 + 兜底 + 静态托管 + startup 钩子）。

    Globals Used: 无（WEB_DIR/DEBUG_DIR 为本模块常量）。
    Returns:
        可直接交给 uvicorn 的应用实例。
    """
    app = FastAPI(title="MOD Agent 制作器", version="0.2.0")
    for router in (sessions.router, tasks.router, artifacts.router,
                   history.router):
        app.include_router(router)

    _mount_index_route(app)
    _mount_debug_routes(app)

    @app.exception_handler(StarletteHTTPException)
    async def fallback_404_to_debug(request: Request,
                                    exc: StarletteHTTPException):
        """未知页面 404 兜底到维护页（非 /api、/debug 路径）。"""
        if exc.status_code == 404 and not request.url.path.startswith(("/api", "/debug")):
            debug_idx = DEBUG_DIR / "index.html"
            if debug_idx.exists():
                return FileResponse(str(debug_idx))
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    WEB_DIR.mkdir(exist_ok=True)
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    _register_startup_hooks(app)
    return app


def _register_startup_hooks(app: FastAPI) -> None:
    """挂 startup 钩子：恢复历史会话 + 废弃会话定时清理。

    必须挂事件而非 __main__ 分支——文件头支持 uvicorn server:app 启动，
    那种方式不经过 __main__，历史会话永远进不了内存表。
    """
    done = {"flag": False}

    @app.on_event("startup")
    def _startup() -> None:
        if done["flag"]:
            return
        done["flag"] = True
        restore_sessions()
        cleanup_orphan_sessions()

        def _orphan_cleanup_loop():
            while True:
                time.sleep(ORPHAN_CLEANUP_INTERVAL_S)
                try:
                    cleanup_orphan_sessions()
                except Exception as e:
                    logger.debug("_orphan_cleanup_loop 降级忽略 | %s", e)

        threading.Thread(target=_orphan_cleanup_loop, daemon=True).start()

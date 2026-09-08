# -*- coding: utf-8 -*-
"""清小搭（Qingxiaoda）接入服务 —— OpenAI 兼容 HTTP API（薄入口）。

该服务把 skill-agent 引擎（core.services.loop 门面）包装成清小搭广场
要求的 OpenAI 兼容端点：
  GET  /v1/models
  POST /v1/chat/completions（非流式 JSON + 流式 SSE）
  GET  /files/{path}（agent 产物公网下载）
  GET  /health

运行方式（在项目根目录执行）：
  cd "tsinghua agent server"
  ..\\venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001

模块组成：config_env（环境/路径，最先导入）/ personas（人格）/
easter_eggs + replies（趣味与错误语料）/ openai_wire（SSE 帧构造）/
attachments（产物收集）/ normalize（消息规范化）/ daemon_api（引擎编排）。
"""
import atexit
import random

import config_env  # noqa: F401 — 必须最先导入（chdir/env 副作用）
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse

from chat_endpoint import router as chat_router
from chat_endpoint import check_auth
from config_env import WORKSPACE
from daemon_api import _DAEMONS
import logging  # 统一日志：降级路径记录

logger = logging.getLogger("tsinghua.main")

app = FastAPI(
    title="Tsinghua Agent Server",
    description="清小搭 OpenAI 兼容接入服务（skill-agent 核心引擎包装）",
    version="1.1.0",
)
app.include_router(chat_router)


def _cleanup_daemons() -> None:
    """服务退出时终止所有常驻 daemon 子进程，避免残留。"""
    for proc in list(_DAEMONS.values()):
        try:
            proc.terminate()
        except Exception as e:
            logger.warning("_cleanup_daemons 降级忽略 | %s", e)
    _DAEMONS.clear()


atexit.register(_cleanup_daemons)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志：定位清小搭实际请求的路径与返回状态码。"""
    method, path = request.method, request.url.path
    print(f"[req] {method} {path}", flush=True)
    try:
        response = await call_next(request)
    except Exception as e:
        print(f"[req] {method} {path} -> EXCEPTION {e}", flush=True)
        raise
    print(f"[req] {method} {path} -> {response.status_code}", flush=True)
    return response


@app.get("/v1/models")
@app.get("/models")
def list_models(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    """清小搭连通性/凭证校验端点（兼容 /models 和 /v1/models）。"""
    check_auth(authorization, x_api_key)
    return {
        "object": "list",
        "data": [{"id": "tsinghua-agent", "object": "model",
                  "owned_by": "skill-agent"}],
    }


@app.get("/files/{file_path:path}")
def serve_attachment(file_path: str):
    """agent 生成文件的公网下载（attachments 的 fileUrl 指向这里）。"""
    root = WORKSPACE.resolve()
    target = (root / file_path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(target))


@app.get("/")
def root():
    """根路径说明（随机趣味提示）。"""
    from replies import ROOT_IMPROVEMENT_NOTES
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "note": "这是给清小搭接入的 OpenAI 兼容服务，不是网页前端。",
        "message": random.choice(ROOT_IMPROVEMENT_NOTES),
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "请访问 http://<server>:8000/",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }


@app.get("/health")
def health():
    """健康检查（随机心情提示）。"""
    from replies import HEALTH_MOOD_NOTES
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "message": random.choice(HEALTH_MOOD_NOTES),
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "独立运行于 server_app/server.py（8000 端口）",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }

# -*- coding: utf-8 -*-
"""清小搭调试占位服务（Debug Mode）。

当真实 agent 服务关闭、你在本地/服务器调试代码时，
可以在 8001 端口启动本脚本，清小搭会收到固定的“正在调试”提示，
而不是连接失败/超时。

运行：
  cd "tsinghua agent server"
  ../venv/bin/python -m uvicorn debug_server:app --host 0.0.0.0 --port 8001
"""
import json
import os
import time
import uuid

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

VALID_KEY = os.environ.get("TSINGHUA_API_KEY", "sk-test-123")
DEBUG_MSG = os.environ.get(
    "DSH_DEBUG_MESSAGE",
    "服务正在调试中（Debug Mode），当前暂时无法处理对话。"
    "请稍后再试；如有 MOD 制作需求，可以稍后访问网页版或等待服务恢复。",
)

app = FastAPI(
    title="Tsinghua Agent Server (Debug Mode)",
    description="清小搭调试占位服务，返回固定调试提示",
    version="0.0.1-debug",
)


def _check_auth(authorization: str | None, x_api_key: str | None) -> None:
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    elif x_api_key:
        token = x_api_key.strip()
    if not token or token != VALID_KEY:
        raise HTTPException(status_code=401, detail="invalid credential")


def _new_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:12]}"


@app.get("/v1/models")
@app.get("/models")
def list_models(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    _check_auth(authorization, x_api_key)
    return {
        "object": "list",
        "data": [{"id": "tsinghua-agent", "object": "model", "owned_by": "skill-agent"}],
    }


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
@app.post("/v1/chat/completions/")
async def chat_completions(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    _check_auth(authorization, x_api_key)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON body")

    stream = body.get("stream") is True
    cid = _new_id()
    created = int(time.time())

    if not stream:
        return JSONResponse({
            "id": cid,
            "object": "chat.completion",
            "created": created,
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": DEBUG_MSG},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": len(DEBUG_MSG), "total_tokens": len(DEBUG_MSG)},
        })

    def frame(delta, finish=None, usage=None):
        choice = {"index": 0, "delta": delta, "finish_reason": finish}
        chunk = {"id": cid, "object": "chat.completion.chunk", "created": created,
                 "model": "tsinghua-agent", "choices": [choice]}
        if usage is not None:
            chunk["usage"] = usage
        return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    def gen():
        yield frame({"role": "assistant"})
        for i in range(0, len(DEBUG_MSG), 8):
            yield frame({"content": DEBUG_MSG[i:i + 8]})
        yield frame({}, finish="stop", usage={"prompt_tokens": 0, "completion_tokens": len(DEBUG_MSG), "total_tokens": len(DEBUG_MSG)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/")
def root():
    return {
        "service": "Tsinghua Agent Server",
        "status": "debug",
        "note": "当前为调试占位服务，不执行真实 agent。",
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "debug_message": DEBUG_MSG,
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }
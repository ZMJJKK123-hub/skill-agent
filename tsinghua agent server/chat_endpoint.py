# -*- coding: utf-8 -*-
"""对话端点：/v1/chat/completions 非流式与流式实现（由 main.py 迁出）。"""
import json
import os
import random
import time

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

import logging

from config_env import VALID_KEY
from daemon_api import (_DAEMONS, append_conversation,
                        collect_attachments, ensure_session_daemon,
                        run_agent, session_workdir, submit_daemon_request)
from easter_eggs import easter_egg_response
from normalize import last_user_content, normalize_messages
from openai_wire import (new_id, quick_chat_response, reasoning_delta,
                         sse_frame, usage_zero)
from personas import (PERSONA_DISPLAY, resolve_persona_key, set_persona,
                      session_persona_command)
from replies import (INVALID_JSON_MESSAGES, append_persona_guide,
                     friendly_agent_error)

log = logging.getLogger("tsinghua.chat")  # 统一日志：降级路径记录

router = APIRouter()


def check_auth(authorization, x_api_key):
    """Bearer / x-api-key 双鉴权，无效 401（由 main.py 迁出）。"""
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    elif x_api_key:
        token = x_api_key.strip()
    if not token:
        raise HTTPException(status_code=401, detail="missing credential")
    if token != VALID_KEY:
        raise HTTPException(status_code=401, detail="invalid credential")


def _persona_switch_response(persona_cmd, session_id: str, stream: bool):
    """人格切换确认（流式 SSE / 非流式 JSON），由 chat_completions 迁出。"""
    key, label = persona_cmd
    reply = f"🎭 人格已切换为：{label}！接下来我会用这个人格陪你聊天～"
    if not set_persona(session_id, key, session_workdir):
        reply = "⚠️ 人格切换失败，请稍后再试。"
    if stream:
        cid, created = new_id(), int(time.time())

        def gen():
            yield sse_frame(cid, created, {"role": "assistant"})
            for i in range(0, len(reply), 8):
                yield sse_frame(cid, created, {"content": reply[i:i + 8]})
            yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero())
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    return JSONResponse({
        "id": new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply},
            "finish_reason": "stop",
        }],
        "usage": usage_zero(),
    })


def _persona_query_reply(session_id: str) -> str:
    """当前人格查询回复文案（按人格差异化口吻）。"""
    key = resolve_persona_key(session_id, session_workdir)
    display = PERSONA_DISPLAY.get(key, key or "通用")
    if display == "喵娘":
        return "我是你的专属喵娘助手喵～当前人格：喵娘。想换人格跟我说“切换成高冷”就可以喵！"
    if display == "高冷技术助理":
        return "我是你的专属 AI 助手。当前人格：高冷技术助理。想换人格就说“切换成喵娘”。"
    return f"我是你的专属 AI 助手，当前人格：{display}。想换人格的话，跟我说“切换成喵娘”就好啦～"


def _status_reply(session_id: str) -> str:
    """服务状态快捷回复文案（由 chat_completions 迁出）。"""
    key = resolve_persona_key(session_id, session_workdir)
    display = PERSONA_DISPLAY.get(key, key or "通用")
    return f"✅ 服务运行中，AI 引擎在线，当前人格：{display}。我可以聊天、写代码、查资料～"


def _egg_response(egg: str, stream: bool):
    """彩蛋响应（流式 SSE / 非流式 JSON），由 chat_completions 迁出。"""
    if stream:
        cid, created = new_id(), int(time.time())

        def gen():
            yield sse_frame(cid, created, {"role": "assistant"})
            for i in range(0, len(egg), 8):
                yield sse_frame(cid, created, {"content": egg[i:i + 8]})
            yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero())
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    return JSONResponse({
        "id": new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": egg},
            "finish_reason": "stop",
        }],
        "usage": usage_zero(),
    })


@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    """OpenAI 兼容对话端点：非流式 JSON + 流式 SSE。"""
    check_auth(authorization, x_api_key)

    try:
        body = await request.json()
    except Exception:
        return quick_chat_response(random.choice(INVALID_JSON_MESSAGES), stream=False)

    # 严格按布尔解析 stream：不要把字符串 "false" 当真
    stream = body.get("stream") is True
    session_id = str(body.get("sessionId") or "")
    messages = normalize_messages(body.get("messages"), session_id)

    # 公网 URL 基址：附件 fileUrl 用它拼出（可用 DSH_PUBLIC_BASE_URL 覆盖）
    base_url = os.environ.get("DSH_PUBLIC_BASE_URL") or str(request.base_url).rstrip("/")

    # 人格切换命令：先于 agent 返回确认
    persona_cmd = session_persona_command(messages)
    if persona_cmd is not None:
        return _persona_switch_response(persona_cmd, session_id, stream)

    # 当前人格查询
    if last_user_content(messages) in {"你现在是什么人格", "当前人格", "你是什么人格", "你是谁", "你叫什么名字"}:
        reply = _persona_query_reply(session_id)
        return quick_chat_response(reply, stream)

    # 服务状态快捷回复
    if last_user_content(messages) in {"服务器状态", "服务状态", "系统状态"}:
        reply = _status_reply(session_id)
        return quick_chat_response(reply, stream)

    # 轻量彩蛋：先于 agent 返回，保证快速、有趣
    egg = easter_egg_response(messages)
    if egg is not None:
        return _egg_response(egg, stream)

    if stream:
        return StreamingResponse(
            stream_agent(messages, session_id, base_url),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 非流式：完整 Agent 跑完再返回（message.reasoning_content 带思考全文）
    try:
        final, attachments, reasoning = run_agent(messages, session_id, base_url)
    except Exception as e:  # noqa: BLE001
        err_msg = friendly_agent_error(e)
        return JSONResponse({
            "id": new_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": err_msg},
                "finish_reason": "stop",
            }],
            "usage": usage_zero(),
        })

    message = {"role": "assistant", "content": final}
    if reasoning:
        message["reasoning_content"] = reasoning
    payload = {
        "id": new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": "stop",
        }],
        "usage": usage_zero(),
    }
    if attachments:
        payload["x_soda"] = {"attachments": attachments}
    return JSONResponse(payload)


# 容错：兼容不带 /v1、或尾部带 / 的探测路径
@router.post("/chat/completions")
@router.post("/v1/chat/completions/")
async def chat_completions_alias(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    return await chat_completions(request, authorization, x_api_key)


# 流式生成器拆至 stream_endpoint（同路由模块，保持调用方零改动）
from stream_endpoint import stream_agent  # noqa: E402,F401

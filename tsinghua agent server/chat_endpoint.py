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
        key, label = persona_cmd
        reply = f"🎭 人格已切换为：{label}！接下来我会用这个人格陪你聊天～"
        if not set_persona(session_id, key, session_workdir):
            reply = "⚠️ 人格切换失败，请稍后再试。"
        if stream:
            cmd_cid = new_id()
            cmd_created = int(time.time())

            def cmd_gen():
                yield sse_frame(cmd_cid, cmd_created, {"role": "assistant"})
                for i in range(0, len(reply), 8):
                    yield sse_frame(cmd_cid, cmd_created, {"content": reply[i:i + 8]})
                yield sse_frame(cmd_cid, cmd_created, {}, finish_reason="stop", usage=usage_zero())
                yield "data: [DONE]\n\n"

            return StreamingResponse(cmd_gen(), media_type="text/event-stream")
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

    # 当前人格查询
    current_queries = {"你现在是什么人格", "当前人格", "你是什么人格", "你是谁", "你叫什么名字"}
    if last_user_content(messages) in current_queries:
        key = resolve_persona_key(session_id, session_workdir)
        display = PERSONA_DISPLAY.get(key, key or "通用")
        if display == "喵娘":
            reply = "我是你的专属喵娘助手喵～当前人格：喵娘。想换人格跟我说“切换成高冷”就可以喵！"
        elif display == "高冷技术助理":
            reply = "我是你的专属 AI 助手。当前人格：高冷技术助理。想换人格就说“切换成喵娘”。"
        else:
            reply = f"我是你的专属 AI 助手，当前人格：{display}。想换人格的话，跟我说“切换成喵娘”就好啦～"
        return quick_chat_response(reply, stream)

    # 服务状态快捷回复
    status_queries = {"服务器状态", "服务状态", "系统状态"}
    if last_user_content(messages) in status_queries:
        key = resolve_persona_key(session_id, session_workdir)
        display = PERSONA_DISPLAY.get(key, key or "通用")
        reply = f"✅ 服务运行中，AI 引擎在线，当前人格：{display}。我可以聊天、写代码、查资料～"
        return quick_chat_response(reply, stream)

    # 轻量彩蛋：先于 agent 返回，保证快速、有趣
    egg = easter_egg_response(messages)
    if egg is not None:
        if stream:
            egg_cid = new_id()
            egg_created = int(time.time())

            def egg_gen():
                yield sse_frame(egg_cid, egg_created, {"role": "assistant"})
                for i in range(0, len(egg), 8):
                    yield sse_frame(egg_cid, egg_created, {"content": egg[i:i + 8]})
                yield sse_frame(egg_cid, egg_created, {}, finish_reason="stop", usage=usage_zero())
                yield "data: [DONE]\n\n"

            return StreamingResponse(egg_gen(), media_type="text/event-stream")
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


def stream_agent(messages: list, session_id: str, base_url: str):
    """流式 Agent：常驻 daemon 处理请求，实时读推理文件转发 delta.reasoning。"""
    cid = new_id()
    created = int(time.time())

    yield sse_frame(cid, created, {"role": "assistant"})
    is_first_request = not any(
        isinstance(m, dict) and m.get("role") == "assistant"
        for m in messages
    )
    if is_first_request:
        yield sse_frame(cid, created, reasoning_delta("🔧 首次启动准备中，会稍微慢一点，请耐心等待～"))
    else:
        yield sse_frame(cid, created, reasoning_delta("正在调用自研 Agent 引擎…"))

    session_root = session_workdir(session_id)
    start_ts = time.time()
    ensure_session_daemon(session_root)
    rid = submit_daemon_request(session_root, messages)
    reasoning_file = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    result_file = session_root / "daemon" / "results" / f"{rid}.json"
    daemon_proc = _DAEMONS.get(str(session_root))
    final = None
    last_idx = 0
    deadline = time.time() + 900
    try:
        while time.time() < deadline:
            if reasoning_file.exists():
                try:
                    raw = reasoning_file.read_text(encoding="utf-8")
                    lines = raw.splitlines()
                    # daemon 可能写到一半（末行无换行符）：半行留到下次轮询再处理，
                    # 否则 json 解析失败 + last_idx 提前推进会丢思考文本
                    if raw and not raw.endswith("\n"):
                        lines = lines[:-1]
                    for line in lines[last_idx:]:
                        try:
                            obj = json.loads(line)
                            yield sse_frame(cid, created, reasoning_delta(obj.get("text", "")))
                        except Exception:  # noqa: BLE001
                            continue
                    last_idx = len(lines)
                except OSError as e:
                    log.debug("推理文件轮询读取失败（降级忽略） | %s", e)
            if result_file.exists():
                data = json.loads(result_file.read_text(encoding="utf-8-sig"))
                if data.get("error"):
                    raise RuntimeError(data["error"])
                final = data.get("text") or "(no response)"
                final = append_persona_guide(final, messages)
                append_conversation(session_id, messages, final)
                break
            if daemon_proc is not None and daemon_proc.poll() is not None:
                raise RuntimeError("AI 服务进程已退出，请检查服务配置")
            time.sleep(0.1)
        if final is None:
            raise RuntimeError("agent daemon timeout")
        attachments = collect_attachments(start_ts, base_url, scope=session_root)
    except Exception as e:  # noqa: BLE001
        err_msg = friendly_agent_error(e)
        err_step = 8
        for i in range(0, len(err_msg), err_step):
            yield sse_frame(cid, created, {"content": err_msg[i:i + err_step]})
        # 指南 §5.6：流式中途出错时，stop 帧附 error 字段（友好文案仍走 content 帧保证用户可见）
        yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(),
                         error={"type": "upstream_error", "message": str(e)[:200]})
        yield "data: [DONE]\n\n"
        return
    finally:
        for p in (reasoning_file, result_file):
            try:
                if p.exists():
                    p.unlink()
            except OSError as e:
                log.debug("清理 daemon 临时文件失败（降级忽略） | %s", p.name)

    step = 8
    for i in range(0, len(final or ""), step):
        yield sse_frame(cid, created, {"content": (final or "")[i:i + step]})

    extra = {}
    if attachments:
        extra["x_soda"] = {"attachments": attachments}
    yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(), extra=extra)
    yield "data: [DONE]\n\n"

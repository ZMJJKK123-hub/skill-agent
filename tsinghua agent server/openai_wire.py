# -*- coding: utf-8 -*-
"""OpenAI 兼容 wire 格式：id/usage/SSE 帧/快速回复构造（由 main.py 迁出）。"""
import json
import time
import uuid

from fastapi.responses import JSONResponse, StreamingResponse


def new_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:12]}"


def usage_zero() -> dict:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def quick_chat_response(content: str, stream: bool):
    """快速构造 OpenAI 完整回复（非流式 JSON 或流式 SSE）。"""
    if stream:
        cid = new_id()
        created = int(time.time())

        def gen():
            yield sse_frame(cid, created, {"role": "assistant"})
            for i in range(0, len(content), 8):
                yield sse_frame(cid, created, {"content": content[i:i + 8]})
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
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": usage_zero(),
    })


def sse_frame(cid: str, created: int, delta: dict, finish_reason=None, usage=None, error=None, extra=None) -> str:
    choice = {"index": 0, "delta": delta, "finish_reason": finish_reason}
    chunk = {
        "id": cid,
        "object": "chat.completion.chunk",
        "created": created,
        "model": "tsinghua-agent",
        "choices": [choice],
    }
    if usage is not None:
        chunk["usage"] = usage
    if error is not None:
        chunk["error"] = error
    if extra is not None:
        chunk.update(extra)
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"


def reasoning_delta(text: str) -> dict:
    """构造思考增量 delta：同时带 reasoning / reasoning_content 两个 key。

    清小搭侧约定读 delta.reasoning；DeepSeek/OpenAI 兼容客户端习惯读
    delta.reasoning_content。双 key 输出两边都能渲染，互不影响。
    """
    return {"reasoning": text, "reasoning_content": text}


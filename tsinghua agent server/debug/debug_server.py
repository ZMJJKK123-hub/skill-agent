# -*- coding: utf-8 -*-
"""清小搭调试占位服务（Debug Mode）。

当真实 agent 服务关闭、你在本地/服务器调试代码时，
可以在 8001 端口启动本脚本；每次聊天请求会从素材库随机返回一条
“正在调试”提示，而不是连接失败/超时。

运行：
  cd "tsinghua agent server/debug"
  ../venv/bin/python -m uvicorn debug_server:app --host 0.0.0.0 --port 8001
"""
import json
import os
import random
import time
import uuid

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

VALID_KEY = os.environ.get("TSINGHUA_API_KEY", "sk-test-123")

# 调试提示语素材库：每次请求随机抽一条，每条末尾附网页版地址
DEBUG_MESSAGES = [
    "🙈 哎呀，我被临时关进小黑屋调试啦！🔧✨ 现在暂时没法陪你聊天，抱歉呀～ 不过别担心，代码君正在努力修复中 💪 等我回来再继续聊哦！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🛠️ 蟹蟹你来找我玩～ 但我正在幕后做一次悄悄升级（Debug 模式）🔧⚙️ 暂时不能正常回复。放心，不是你的问题，是我在检查身体 😉 请稍后再来～\n\n🌐 网页版：http://49.232.37.238:8000/",
    "⏳ 系统正在调试中，AI 暂时抽空摸鱼去了 😴 你可以稍后再来，或者先去网页版逛逛～ 我们很快回来！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🧹 我正在给大脑打扫卫生，暂时不能见人～ 稍等一下下，马上就好！如果着急，可以先到网页版转转 ☕️✨\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🌈 我偷摸在后台升级新技能中，聊天功能先挂个“维修中”牌子～ 请过一阵子再回来找我玩哦 🐣🔧\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🎩 魔法师正在调整魔杖，不小心把我调成暂时无法说话模式了 🔮 稍后再来，我会带着更棒的能力回来！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "😅 抱歉抱歉，我刚刚把自己搞宕机了，正在重启大脑中… 你先去网页版喝杯茶，我马上回来 ☕️🚀\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🛠️ Debug 模式开启：我不是不在，是在偷偷变强！暂时不能正常对话，等我升级完再来找我哦 😎\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🐣 我正在偷偷孵化新功能，暂时不能说话～ 请稍后再来，或者先去网页版看看，很快就好！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "☕️ 程序员小哥哥正在给我灌咖啡调试中，先挂机一会～ 你可以先去网页版逛逛，我等会就回来！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🔮 占卜显示：你和我命中注定，但我现在正在 Debug… 稍等片刻，我们还会再见的！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "📦 我正在重新打包自己，暂时不能拆包裹聊天～ 稍后再来，或者先去网页版看看！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🎮 我先去打个补丁，暂时退出对话～ 你可以在网页版继续玩耍，等我回来！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "💤 我睡着被强行叫醒重构中，先别急着找我～ 去网页版逛逛，我马上就满血回归！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🐢 我正在慢速升级，暂时不能回复～ 别走开太久，网页版可以先逛逛！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🧩 我在拼装新模块，暂时没法跟你说话～ 稍后回来，我可以陪你聊更厉害的话题！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🚧 前方施工中，AI 暂时封闭入口～ 你可以绕道去网页版看看，我等修好再来！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🔗 我被焊住了，正在重新接线中 🛠️ 你先去网页版，我等会就能正常说话啦！\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🎉 我在准备一个大更新，暂时静音模式～ 稍后见！你也可以先去网页版体验一下～\n\n🌐 网页版：http://49.232.37.238:8000/",
    "🌱 我在重新生长自己，暂时不能对话～ 耐心等一下下，或者先去网页版逛逛，很快回来！\n\n🌐 网页版：http://49.232.37.238:8000/",
]

# 允许用环境变量强制固定一条提示语
_FIXED_MSG = os.environ.get("DSH_DEBUG_MESSAGE", "").strip()


def _pick_debug_message() -> str:
    if _FIXED_MSG:
        return _FIXED_MSG
    return random.choice(DEBUG_MESSAGES)


app = FastAPI(
    title="Tsinghua Agent Server (Debug Mode)",
    description="清小搭调试占位服务，返回随机调试提示",
    version="0.0.3-debug",
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
    msg = _pick_debug_message()

    if not stream:
        return JSONResponse({
            "id": cid,
            "object": "chat.completion",
            "created": created,
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": msg},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": len(msg), "total_tokens": len(msg)},
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
        for i in range(0, len(msg), 8):
            yield frame({"content": msg[i:i + 8]})
        yield frame({}, finish="stop", usage={"prompt_tokens": 0, "completion_tokens": len(msg), "total_tokens": len(msg)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/")
def root():
    return {
        "service": "Tsinghua Agent Server",
        "status": "debug",
        "note": "当前为调试占位服务，不执行真实 agent；每次回复会从素材库随机抽取提示语。",
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "debug_message_count": len(DEBUG_MESSAGES),
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }
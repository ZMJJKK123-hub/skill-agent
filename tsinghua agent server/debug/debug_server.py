# -*- coding: utf-8 -*-
"""清小搭调试占位服务（Debug Mode）。

当真实 agent 服务关闭、你在本地/服务器调试代码时，
可以在 8001 端口启动本脚本；每次聊天请求会从素材库随机返回一条
“正在调试”提示，而不是连接失败/超时。

支持人格切换（环境变量 DSH_PERSONA）：
  - meow   喵娘
  - cool   高冷技术助理
  - cheer  元气少女
  - elegant 优雅姐姐
  - default 通用

运行：
  cd "tsinghua agent server/debug"
  ../venv/bin/python -m uvicorn debug_server:app --host 0.0.0.0 --port 8001
"""
import json
import os
import random
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

# 读取项目根 .env（使 TSINGHUA_API_KEY 也能从 .env 读取）
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

VALID_KEY = os.environ.get("TSINGHUA_API_KEY", "sk-test-123")

_URL = "http://49.232.37.238:8000/"

PERSONAS = {
    "default": {
        "name": "通用",
        "messages": [
            f"🙈 哎呀，我被临时关进小黑屋调试啦！🔧✨ 现在暂时没法陪你聊天，抱歉呀～ 不过别担心，代码君正在努力修复中 💪 等我回来再继续聊哦！\n\n🌐 网页版：{_URL}",
            f"🛠️ 蟹蟹你来找我玩～ 但我正在幕后做一次悄悄升级（Debug 模式）🔧⚙️ 暂时不能正常回复。放心，不是你的问题，是我在检查身体 😉 请稍后再来～\n\n🌐 网页版：{_URL}",
            f"⏳ 系统正在调试中，AI 暂时抽空摸鱼去了 😴 你可以稍后再来，或者先去网页版逛逛～ 我们很快回来！\n\n🌐 网页版：{_URL}",
            f"🧹 我正在给大脑打扫卫生，暂时不能见人～ 稍等一下下，马上就好！如果着急，可以先到网页版转转 ☕️✨\n\n🌐 网页版：{_URL}",
            f"🌈 我偷摸在后台升级新技能中，聊天功能先挂个“维修中”牌子～ 请过一阵子再回来找我玩哦 🐣🔧\n\n🌐 网页版：{_URL}",
            f"🎩 魔法师正在调整魔杖，不小心把我调成暂时无法说话模式了 🔮 稍后再来，我会带着更棒的能力回来！\n\n🌐 网页版：{_URL}",
            f"😅 抱歉抱歉，我刚刚把自己搞宕机了，正在重启大脑中… 你先去网页版喝杯茶，我马上回来 ☕️🚀\n\n🌐 网页版：{_URL}",
            f"🛠️ Debug 模式开启：我不是不在，是在偷偷变强！暂时不能正常对话，等我升级完再来找我哦 😎\n\n🌐 网页版：{_URL}",
        ],
    },
    "meow": {
        "name": "喵娘",
        "messages": [
            f"喵呜～主人，我现在被塞进调试箱子里啦喵 🔧✨ 暂时不能陪你聊天，好委屈喵！不过代码君正在努力修，很快就能回来喵～\n\n🌐 网页版：{_URL}",
            f"喵喵喵！我不是故意不理你的喵～ 我正在偷偷升级新功能呢喵 😽 稍等一下，或者先去网页版逛逛主人！\n\n🌐 网页版：{_URL}",
            f"喵～主人不要担心，我只是一只正在 Debug 的小猫咪 🐱 等我修好毛线团就来陪你玩喵！\n\n🌐 网页版：{_URL}",
            f"呼噜呼噜…我现在被按在维修台上啦喵 ⚙️ 暂时不能说话喵～ 主人可以先逛逛网页版，我马上就元气满满地回来喵！\n\n🌐 网页版：{_URL}",
        ],
    },
    "cool": {
        "name": "高冷技术助理",
        "messages": [
            f"系统维护中。问题已知，正在修复。稍后再试。\n\n🌐 网页版：{_URL}",
            f"Debug. 不要打扰。完成会自动上线。\n\n🌐 网页版：{_URL}",
            f"当前不可用。原因：升级。预计很快恢复。\n\n🌐 网页版：{_URL}",
            f"已收到。正在处理。请等待。\n\n🌐 网页版：{_URL}",
        ],
    },
    "cheer": {
        "name": "元气少女",
        "messages": [
            f"耶！我正在进行超重要的升级中！！✨ 暂时不能陪你聊天，但是充满能量地准备回来！你也可以先去网页版踩踩哦～\n\n🌐 网页版：{_URL}",
            f"嗨呀～我现在被小哥哥锁在 Debug 小房间了啦！🔧 不过别担心，马上就会带着超棒的新能力蹦出来！\n\n🌐 网页版：{_URL}",
            f"冲鸭！我正在偷偷变强，等我出来一定会让你吓一跳的！✨ 先到网页版逛逛吧～\n\n🌐 网页版：{_URL}",
            f"元气满格但暂时被暂停使用啦～哈哈，稍等一下下，我这就满血复活回来找你玩！\n\n🌐 网页版：{_URL}",
        ],
    },
    "elegant": {
        "name": "优雅姐姐",
        "messages": [
            f"亲爱的，我正在后台进行一段优雅的修复之旅呢 ✨ 暂时不便同你交谈，请不要着急，稍后我会以更好的状态回来。\n\n🌐 网页版：{_URL}",
            f"感谢你的耐心等候。我正在进行细致的维护，很快就好。你可以先去网页版小憩片刻。\n\n🌐 网页版：{_URL}",
            f"此刻我暂时静默，只为给你带来更好的体验。请稍后再来，我定不负期待。\n\n🌐 网页版：{_URL}",
        ],
    },
    "mystic": {
        "name": "神秘占卜师",
        "messages": [
            f"🔮 星象显示，你此刻需要一个等待……我正在调试魔法阵，暂时无法为你解读未来。请稍后再来，谜底会揭晓。\n\n🌐 网页版：{_URL}",
            f"✨ 命运让我暂时静默，只为下一次更好的相遇。请不要着急，先去网页版转转，我会在时机成熟时归来。\n\n🌐 网页版：{_URL}",
            f"🔮 塔罗牌正位：Debug。逆位：耐心。请你稍作等待，答案正在路上。\n\n🌐 网页版：{_URL}",
        ],
    },
    "senpai": {
        "name": "学长前辈",
        "messages": [
            f"哦，学弟/学妹先等等啊，学长我正在修 bug 呢🔧 一会儿就好，你先去网页版看看别的～\n\n🌐 网页版：{_URL}",
            f"别急，前辈我正在后台清理代码垃圾，马上就能恢复。你先去网页版喝杯水吧。\n\n🌐 网页版：{_URL}",
            f"这个 bug 有点意思，学长我想再研究一下。稍等我一下，回来给你带好消息。\n\n🌐 网页版：{_URL}",
        ],
    },
}

# 允许用环境变量强制固定一条提示语
_FIXED_MSG = os.environ.get("DSH_DEBUG_MESSAGE", "").strip()


def _pick_persona() -> dict:
    persona_key = os.environ.get("DSH_PERSONA", "").strip().lower()
    if persona_key in PERSONAS:
        return PERSONAS[persona_key]
    return random.choice(list(PERSONAS.values()))


def _pick_debug_message() -> str:
    if _FIXED_MSG:
        return _FIXED_MSG
    return random.choice(_pick_persona()["messages"])


def _debug_easter_egg(messages) -> str | None:
    """Debug 模式专属彩蛋：和正式模式不同。"""
    for m in messages or []:
        if not isinstance(m, dict) or m.get("role") != "user":
            continue
        content = m.get("content", "")
        if not isinstance(content, str):
            continue
        c = content.strip().lower()
        if c == "ping":
            return "pong 🐟（Debug 彩蛋：我是占位鱼，不是真 AI～）"
        if c in ("彩蛋", "easter egg", "easteregg"):
            return "🥚 Debug 彩蛋！你找到了躲在维修间里的我～不过这里只有没修完的代码和一锅乱炖。"
        if c in ("help", "帮助", "debug help"):
            return "🔧 Debug 指令：ping / 彩蛋 / help / 你是谁。其他消息都会返回维护提示～"
        if c in ("你是谁", "你是什么"):
            return "我是 Debug 占位服务，不是真 AI。我只是暂时帮你占个位置，真正的我还在后厨忙～"
        if c in ("人格列表", "有哪些人格"):
            return "Debug 模式支持：通用、喵娘、高冷技术助理、元气少女、优雅姐姐、神秘占卜师、学长前辈。"
    return None


app = FastAPI(
    title="Tsinghua Agent Server (Debug Mode)",
    description="清小搭调试占位服务，返回多人格随机调试提示",
    version="0.0.4-debug",
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
    egg = _debug_easter_egg(body.get("messages"))
    msg = egg if egg is not None else _pick_debug_message()

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
    persona = _pick_persona()
    return {
        "service": "Tsinghua Agent Server",
        "status": "debug",
        "note": "当前为调试占位服务，不执行真实 agent；支持多人格随机提示。",
        "persona": persona["name"],
        "personas": list(PERSONAS.keys()),
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "debug_message_count": sum(len(p["messages"]) for p in PERSONAS.values()),
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }
# -*- coding: utf-8 -*-
"""清小搭（Qingxiaoda）接入服务 —— OpenAI 兼容 HTTP API。

该服务把 skill-agent 的 core.agent.agent_loop() 包装成清小搭广场要求的
OpenAI 兼容端点：

  GET  /v1/models
  POST /v1/chat/completions

支持：
- Bearer Token 鉴权（也兼容 x-api-key）
- 非流式 JSON 响应
- 流式 SSE 响应（role 帧 -> content 帧 -> stop 帧 -> data: [DONE]）
- 探测请求快速响应（避免清小搭探测超时）
- sessionId 简单记忆（当前直接使用平台下发的全量 messages 作为上下文）
- 文本消息归一化（图片/音频/文件输入暂时降级为占位说明，不影响 L0 文本对话）

运行方式（在项目根目录执行）：
  cd "tsinghua agent server"
  ..\\venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001
"""

import copy
import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径与环境：必须先于 core 导入完成
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVICE_DIR = Path(__file__).resolve().parent

# 让 core 包可导入
sys.path.insert(0, str(PROJECT_ROOT))

# 切到项目根，让 core/config 能读取根目录 .env，同时工具文件路径以项目根为基准
os.chdir(PROJECT_ROOT)

# 使用 chat 模式：不触发 MOD 专属的 GameTest / 构建 / 监管线程逻辑
os.environ.setdefault("DSH_MODE", "chat")

# 全自动模式：agent 若想 ask_user_question，不会在 HTTP 请求里永久阻塞
os.environ.setdefault("DSH_AUTO_MODE", "1")

# 会话状态落盘到本服务目录下的 .runtime/.chat，避免污染项目根目录
os.environ.setdefault("DSH_SESSION_ROOT", str(SERVICE_DIR / ".runtime"))
(SERVICE_DIR / ".runtime").mkdir(parents=True, exist_ok=True)

# 显式读取项目根 .env（包含 DEEPSEEK_API_KEY / TSINGHUA_API_KEY 等）
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env", override=True)
except Exception:
    pass

# 本服务自己的接入密钥（清小搭填的 credential）
# 默认 sk-test-123 仅用于本地测试；部署时务必设置环境变量 TSINGHUA_API_KEY
VALID_KEY = os.environ.get("TSINGHUA_API_KEY", "sk-test-123")

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from core.agent import agent_loop

# 挂载原有 server_app 网页服务：这样同一个端口既能服务清小搭，也能访问原网站。
# server_app 内部使用 `import auth_store` 这种同目录绝对导入，因此把 server_app 目录也加入 sys.path。
sys.path.insert(0, str(PROJECT_ROOT / "server_app"))
try:
    from server_app.server import app as web_app
    WEB_APP_AVAILABLE = True
except Exception as _web_err:
    print(f"[warn] server_app web app import failed: {_web_err}", flush=True)
    web_app = None
    WEB_APP_AVAILABLE = False

# ---------------------------------------------------------------------------
# FastAPI 实例
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Tsinghua Agent Server",
    description="清小搭 OpenAI 兼容接入服务（skill-agent 核心引擎包装）",
    version="1.0.0",
)

# 简单并发锁：agent_loop 内部有大量模块级全局单例（task_manager/teammate/worktree），
# 演示/低并发场景下串行执行最安全。高并发可改为每 sessionId 一个子进程（见 README）。
_agent_lock = threading.Lock()

# sessionId -> 最近一次完整 messages（仅用于调试/扩展；当前实际直接使用请求里的全量 messages）
_session_cache: dict[str, list] = {}
_SESSION_CACHE_MAX = 100


# ---------------------------------------------------------------------------
# 请求日志：方便定位清小搭实际请求了哪个路径、返回什么状态码
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    method = request.method
    path = request.url.path
    print(f"[req] {method} {path}", flush=True)
    try:
        response = await call_next(request)
    except Exception as e:
        print(f"[req] {method} {path} -> EXCEPTION {e}", flush=True)
        raise
    print(f"[req] {method} {path} -> {response.status_code}", flush=True)
    return response


# ---------------------------------------------------------------------------
# 鉴权
# ---------------------------------------------------------------------------
def _check_auth(authorization: str | None, x_api_key: str | None) -> None:
    """支持 Bearer Token 和 x-api-key 两种鉴权，无效一律 401。"""
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    elif x_api_key:
        token = x_api_key.strip()

    if not token:
        raise HTTPException(status_code=401, detail="missing credential")
    if token != VALID_KEY:
        raise HTTPException(status_code=401, detail="invalid credential")


# ---------------------------------------------------------------------------
# 消息规范化：把清小搭/OpenAI 请求转成 core.agent 可用的纯文本消息
# ---------------------------------------------------------------------------
def _content_to_text(content) -> str:
    """content 可能是 str，也可能是多模态数组；本服务按文本处理。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                parts.append(str(item))
                continue
            t = item.get("type", "")
            if t == "text":
                parts.append(str(item.get("text", "")))
            elif t == "image_url":
                parts.append("[图片输入]")
            elif t == "input_audio":
                parts.append("[音频输入]")
            elif t == "file":
                filename = (item.get("file") or {}).get("filename", "")
                parts.append(f"[文件输入:{filename}]" if filename else "[文件输入]")
        return "\n".join(p for p in parts if p)
    return str(content)


def _normalize_messages(messages: list | None) -> list[dict]:
    """过滤掉 tool 消息/多模态数组，保留纯文本 system/user/assistant 序列。"""
    if not isinstance(messages, list):
        return []

    out: list[dict] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role", "")
        if role not in ("system", "user", "assistant"):
            continue
        content = _content_to_text(m.get("content", ""))
        out.append({"role": role, "content": content})

    if not out:
        out = [{"role": "user", "content": "你好"}]
    return out


# ---------------------------------------------------------------------------
# OpenAI 通用字段构造
# ---------------------------------------------------------------------------
def _new_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:12]}"


def _usage_zero() -> dict:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def _sse_frame(cid: str, created: int, delta: dict, finish_reason=None, usage=None, error=None) -> str:
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
    return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# 核心：调用本项目 Agent 引擎
# ---------------------------------------------------------------------------
def _run_agent(messages: list, session_id: str) -> str:
    """调用 agent_loop 获取最终回复。串行化保证 demo 安全。"""
    # 缓存 session 最近消息（便于调试；当前仍优先使用请求里的全量 messages）
    if session_id:
        _session_cache[session_id] = copy.deepcopy(messages)
        # 简单防止内存无限增长
        if len(_session_cache) > _SESSION_CACHE_MAX:
            for k in list(_session_cache.keys())[:len(_session_cache) - _SESSION_CACHE_MAX]:
                _session_cache.pop(k, None)

    with _agent_lock:
        # agent_loop 会把 .chat/session_events.jsonl 等写到当前 cwd；
        # 临时切到服务自己的 .runtime 目录，避免污染项目根目录。
        _prev_cwd = Path.cwd()
        os.chdir(SERVICE_DIR / ".runtime")
        try:
            # deepcopy：agent_loop 会原地改写 messages
            final = agent_loop(copy.deepcopy(messages))
        finally:
            os.chdir(_prev_cwd)
    return str(final) if final is not None else "(no response)"


# ---------------------------------------------------------------------------
# 探测快速通道
# ---------------------------------------------------------------------------
def _is_probe_request(messages: list, max_tokens) -> bool:
    """清小搭探测会用 max_tokens:1 发最小对话；命中时走快速回复，避免超时。"""
    if max_tokens is not None:
        try:
            if int(max_tokens) == 1:
                return True
        except (TypeError, ValueError):
            pass
    # 兜底：极短且只有一轮 user 的消息也视为探测
    if len(messages) <= 1:
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, str) and len(content.strip()) <= 4:
                return True
    return False


def _probe_answer() -> str:
    return "连接成功：Tsinghua Agent 已就绪。"


def _probe_stream_response() -> StreamingResponse:
    cid = _new_id()
    created = int(time.time())

    def gen():
        yield _sse_frame(cid, created, {"role": "assistant"})
        yield _sse_frame(cid, created, {"content": _probe_answer()})
        yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero())
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


def _probe_json_response():
    return JSONResponse({
        "id": _new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": _probe_answer()},
            "finish_reason": "stop",
        }],
        "usage": _usage_zero(),
    })


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------
@app.get("/v1/models")
@app.get("/models")
def list_models(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    """清小搭连通性/凭证校验端点（兼容 /models 和 /v1/models）。"""
    _check_auth(authorization, x_api_key)
    return {
        "object": "list",
        "data": [
            {"id": "tsinghua-agent", "object": "model", "owned_by": "skill-agent"}
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    """OpenAI 兼容对话端点：非流式 JSON + 流式 SSE。"""
    _check_auth(authorization, x_api_key)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON body")

    # 严格按布尔解析 stream：不要把字符串 "false" 当真
    stream = body.get("stream") is True
    max_tokens = body.get("max_tokens")
    session_id = str(body.get("sessionId") or "")
    messages = _normalize_messages(body.get("messages"))

    # 清小搭探测最小对话：快速回复，不启动完整 Agent
    if _is_probe_request(messages, max_tokens):
        if stream:
            return _probe_stream_response()
        return _probe_json_response()

    if stream:
        return StreamingResponse(
            _stream_agent(messages, session_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 非流式：完整 Agent 跑完再返回
    try:
        final = _run_agent(messages, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent error: {e}")

    return JSONResponse({
        "id": _new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": final},
            "finish_reason": "stop",
        }],
        "usage": _usage_zero(),
    })


# 容错：兼容不带 /v1、或尾部带 / 的探测路径
@app.post("/chat/completions")
@app.post("/v1/chat/completions/")
async def chat_completions_alias(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    return await chat_completions(request, authorization, x_api_key)


def _stream_agent(messages: list, session_id: str):
    """流式 Agent：先发 role/思考帧，再跑 agent_loop，最后逐块吐内容。"""
    cid = _new_id()
    created = int(time.time())

    yield _sse_frame(cid, created, {"role": "assistant"})
    # 可选 L1 思考帧，让前端显示“思考中”
    yield _sse_frame(cid, created, {"reasoning": "正在调用自研 Agent 引擎…"})

    try:
        final = _run_agent(messages, session_id)
    except Exception as e:
        # 已发出 HTTP 头：按清小搭 §5.6 发送 error + stop 帧
        yield _sse_frame(
            cid, created, {},
            finish_reason="stop",
            error={"type": "upstream_error", "message": str(e)},
        )
        yield "data: [DONE]\n\n"
        return

    # 将完整回复按小块流式输出，保证界面逐字展示
    step = 8
    for i in range(0, len(final), step):
        yield _sse_frame(cid, created, {"content": final[i:i + step]})

    yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero())
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# 健康检查：原网页由挂载的 server_app 负责根路径 /
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "mounted at / from server_app",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }


# 把原有网站挂到根路径，保证：
#   /v1/*             -> 清小搭 OpenAI 兼容接口
#   / 和 /api/*        -> 原有 server_app 网页
if WEB_APP_AVAILABLE and web_app is not None:
    app.mount("/", web_app)
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

  本服务与 server_app 网页服务完全独立：
    - 8000 端口：server_app/server.py（你自己的网页）
    - 8001 端口：本服务（清小搭 OpenAI 兼容接口）
"""

import copy
import json
import mimetypes
import os
import queue
import re
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
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

# 工作区目录：agent 的所有文件操作/产物都发生在这里（与 server_app 网页隔离）
WORKSPACE = SERVICE_DIR / ".runtime"
WORKSPACE.mkdir(parents=True, exist_ok=True)

# 关键：必须在导入 core 之前把 cwd 切到 WORKSPACE，
# 这样 core/config.WORKDIR 与工具的文件操作基座都落在 .runtime，
# agent 生成的文件才会出现在我们能收集/提供下载的地方。
os.chdir(WORKSPACE)

from core.agent import agent_loop

# 2026-08-xx：已按用户要求与 server_app 完全解耦。
# 本服务只负责清小搭 OpenAI 兼容接口（8001 端口），不再挂载 server_app 网页。
# server_app 网页由单独的 `server_app/server.py` 运行在 8000 端口。

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
# 支持 file / image_url：下载到工作区 inputs/，让 agent 能用 read_file 等工具读取。
# ---------------------------------------------------------------------------
def _safe_input_name(filename: str, fallback_ext: str = "") -> str:
    name = Path(filename or "").name.strip()
    if not name:
        name = f"file_{uuid.uuid4().hex[:8]}{fallback_ext}"
    return name


def _download_remote_file(url: str, filename: str, inputs_dir: Path) -> tuple[str, bool]:
    """下载清小搭 OSS 上的文件/图片 URL 到工作区 inputs/，返回 (相对路径, 是否成功)。"""
    try:
        inputs_dir.mkdir(parents=True, exist_ok=True)
        import httpx
        r = httpx.get(url, timeout=60, follow_redirects=True)
        r.raise_for_status()
        safe_name = _safe_input_name(filename)
        target = inputs_dir / safe_name
        counter = 1
        while target.exists():
            target = inputs_dir / f"{Path(safe_name).stem}_{counter}{Path(safe_name).suffix}"
            counter += 1
        target.write_bytes(r.content)
        return f"inputs/{target.name}", True
    except Exception as e:
        return f"下载失败: {e}", False


def _content_to_text(content, inputs_dir: Path) -> str:
    """content 可能是 str，也可能是多模态数组；文本原样，文件/图片下载后给路径。"""
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
                url = ((item.get("image_url") or {}).get("url") or "")
                if url:
                    raw_name = Path(url.split("?")[0]).name or "image.png"
                    rel, ok = _download_remote_file(url, raw_name, inputs_dir)
                    parts.append(f"[图片已保存: {rel}]" if ok else f"[图片输入{rel}]")
                else:
                    parts.append("[图片输入]")
            elif t == "input_audio":
                parts.append("[音频输入暂不支持]")
            elif t == "file":
                file_obj = item.get("file") or {}
                url = file_obj.get("url") or ""
                filename = file_obj.get("filename") or ""
                if url:
                    rel, ok = _download_remote_file(url, filename, inputs_dir)
                    parts.append(f"[文件已保存: {rel}]" if ok else f"[文件输入{rel}]")
                elif file_obj.get("file_id"):
                    parts.append("[文件输入(file_id)暂不支持]")
                else:
                    parts.append(f"[文件输入:{filename}]" if filename else "[文件输入]")
        return "\n".join(p for p in parts if p)
    return str(content)


def _normalize_messages(messages: list | None, session_id: str = "") -> list[dict]:
    """过滤掉 tool 消息/多模态数组，保留纯文本 system/user/assistant 序列。"""
    if not isinstance(messages, list):
        return []

    inputs_dir = WORKSPACE / "inputs"
    out: list[dict] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role", "")
        if role not in ("system", "user", "assistant"):
            continue
        content = _content_to_text(m.get("content", ""), inputs_dir)
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


def _sse_frame(cid: str, created: int, delta: dict, finish_reason=None, usage=None, error=None, extra=None) -> str:
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


# ---------------------------------------------------------------------------
# 文件产物：收集 agent 生成的可交付文件，并通过 /files/... 公网下载
# ---------------------------------------------------------------------------
# 网页版完整地址（对话结尾提示用户用）
WEB_URL = os.environ.get("DSH_WEB_URL", "http://49.232.37.238:8000/").rstrip("/")

_ATTACHMENT_EXCLUDE_DIRS = {
    ".chat", ".tasks", ".team", ".worktrees", ".transcripts", ".spill",
    ".supervisor", "__pycache__", ".git", "node_modules", "venv",
    "data", "core", "server_app", "mod_templates", "mc_java_sources",
    "docs", "frontend", "web", "assets", "screenshots", "inputs",
}

_ATTACHMENT_EXTS = {
    ".zip", ".jar", ".tar", ".gz", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".md", ".csv", ".rtf",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
}

_ATTACHMENT_FILE_TYPE = {
    ".zip": "archive", ".jar": "file", ".tar": "archive", ".gz": "archive", ".7z": "archive",
    ".pdf": "pdf", ".doc": "word", ".docx": "word",
    ".xls": "excel", ".xlsx": "excel", ".ppt": "ppt", ".pptx": "ppt",
    ".txt": "text", ".md": "text", ".csv": "text", ".rtf": "text",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".webp": "image", ".bmp": "image", ".svg": "image",
}


def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _collect_attachments(start_ts: float, base_url: str, limit: int = 10) -> list[dict]:
    """收集 start_ts 之后生成的可交付文件，构造清小搭 x_soda.attachments。"""
    if not WORKSPACE.exists():
        return []
    attachments: list[dict] = []
    seen: set[str] = set()
    for p in sorted(WORKSPACE.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(WORKSPACE)
        except ValueError:
            continue
        parts = rel.parts
        if any(part in _ATTACHMENT_EXCLUDE_DIRS for part in parts):
            continue
        if p.suffix.lower() not in _ATTACHMENT_EXTS:
            continue
        try:
            if p.stat().st_mtime < start_ts - 1:
                continue
        except OSError:
            continue
        key = rel.as_posix()
        if key in seen:
            continue
        seen.add(key)
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        attachments.append({
            "fileUrl": f"{base_url}/files/{key}",
            "fileName": p.name,
            "fileType": _ATTACHMENT_FILE_TYPE.get(p.suffix.lower(), "file"),
            "mimeType": _guess_mime(p),
            "fileSize": size,
        })
        if len(attachments) >= limit:
            break
    return attachments


@app.get("/files/{file_path:path}")
def serve_attachment(file_path: str):
    """提供 agent 生成文件的公网下载（清小搭 attachments 的 fileUrl 指向这里）。"""
    root = WORKSPACE.resolve()
    target = (root / file_path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(target))


def _append_web_hint(text: str) -> str:
    """在对话回复末尾提示用户可访问完整网页版。"""
    hint = (
        f"\n\n> 💡 清小搭内提供对话/附件等精简功能；"
        f"如需文件树、实时事件、设置等更完整的功能，可访问网页版：{WEB_URL}"
    )
    return text + hint


# ---------------------------------------------------------------------------
# 核心：调用本项目 Agent 引擎
# ---------------------------------------------------------------------------
def _session_workdir(session_id: str) -> Path:
    """为每个清小搭 sessionId 分配独立工作目录，用于隔离对话历史/断点。"""
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "")[:64].strip("._") or "default"
    d = WORKSPACE / "sessions" / safe
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_agent(messages: list, session_id: str, base_url: str,
               reasoning_sink=None) -> tuple[str, list]:
    """调用 agent_loop 获取最终回复，并收集本次生成的附件。串行化保证 demo 安全。

    reasoning_sink: 可选回调，agent_loop 收到模型 reasoning_content 增量时实时调用，
    用于清小搭流式展示思考过程。非流式请求传 None 即可。
    """
    # 缓存 session 最近消息（便于调试；当前仍优先使用请求里的全量 messages）
    if session_id:
        _session_cache[session_id] = copy.deepcopy(messages)
        # 简单防止内存无限增长
        if len(_session_cache) > _SESSION_CACHE_MAX:
            for k in list(_session_cache.keys())[:len(_session_cache) - _SESSION_CACHE_MAX]:
                _session_cache.pop(k, None)

    start_ts = time.time()
    session_root = _session_workdir(session_id)
    _prev_cwd = Path.cwd()
    _prev_root = os.environ.get("DSH_SESSION_ROOT")
    os.environ["DSH_SESSION_ROOT"] = str(session_root)
    os.chdir(session_root)

    with _agent_lock:
        try:
            # 仅在本次调用期间设置 reasoning 转发，避免并发请求串线
            from core.agent import get_reasoning_sink, set_reasoning_sink
            _prev_sink = get_reasoning_sink()
            if reasoning_sink is not None:
                set_reasoning_sink(reasoning_sink)
            # deepcopy：agent_loop 会原地改写 messages
            final = agent_loop(copy.deepcopy(messages))
        finally:
            try:
                from core.agent import get_reasoning_sink, set_reasoning_sink
                set_reasoning_sink(_prev_sink)
            except Exception:
                pass
            os.chdir(_prev_cwd)
            if _prev_root is None:
                os.environ.pop("DSH_SESSION_ROOT", None)
            else:
                os.environ["DSH_SESSION_ROOT"] = _prev_root

    text = str(final) if final is not None else "(no response)"
    text = _append_web_hint(text)
    attachments = _collect_attachments(start_ts, base_url)
    return text, attachments


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
    messages = _normalize_messages(body.get("messages"), session_id)

    # 公网 URL 基址：附件 fileUrl 用它拼出（可用 DSH_PUBLIC_BASE_URL 覆盖）
    base_url = os.environ.get("DSH_PUBLIC_BASE_URL") or str(request.base_url).rstrip("/")

    # 清小搭探测最小对话：快速回复，不启动完整 Agent
    if _is_probe_request(messages, max_tokens):
        if stream:
            return _probe_stream_response()
        return _probe_json_response()

    if stream:
        return StreamingResponse(
            _stream_agent(messages, session_id, base_url),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 非流式：完整 Agent 跑完再返回
    try:
        final, attachments = _run_agent(messages, session_id, base_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent error: {e}")

    payload = {
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
    }
    if attachments:
        payload["x_soda"] = {"attachments": attachments}
    return JSONResponse(payload)


# 容错：兼容不带 /v1、或尾部带 / 的探测路径
@app.post("/chat/completions")
@app.post("/v1/chat/completions/")
async def chat_completions_alias(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
):
    return await chat_completions(request, authorization, x_api_key)


def _stream_agent(messages: list, session_id: str, base_url: str):
    """流式 Agent：后台线程跑 agent_loop，实时转发 delta.reasoning，最后逐块吐内容。"""
    cid = _new_id()
    created = int(time.time())

    yield _sse_frame(cid, created, {"role": "assistant"})
    # 可选 L1 思考帧，让前端先有“思考中”反馈
    yield _sse_frame(cid, created, {"reasoning": "正在调用自研 Agent 引擎…"})

    q: queue.Queue = queue.Queue()

    def _worker():
        try:
            # reasoning_sink 只作用于本次 agent_loop 调用，避免并发请求串线
            final, attachments = _run_agent(
                messages, session_id, base_url,
                reasoning_sink=lambda text: q.put(("reasoning", text)),
            )
            q.put(("final", final, attachments))
        except Exception as e:
            q.put(("error", str(e)))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    final = None
    attachments = []
    while True:
        try:
            item = q.get(timeout=0.3)
        except queue.Empty:
            if not thread.is_alive():
                break
            continue
        kind = item[0]
        if kind == "reasoning":
            yield _sse_frame(cid, created, {"reasoning": item[1]})
        elif kind == "final":
            final, attachments = item[1], item[2]
            break
        elif kind == "error":
            yield _sse_frame(
                cid, created, {},
                finish_reason="stop",
                error={"type": "upstream_error", "message": item[1]},
            )
            yield "data: [DONE]\n\n"
            return

    # 将完整回复按小块流式输出，保证界面逐字展示
    step = 8
    for i in range(0, len(final or ""), step):
        yield _sse_frame(cid, created, {"content": (final or "")[i:i + step]})

    extra = {}
    if attachments:
        extra["x_soda"] = {"attachments": attachments}
    yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero(), extra=extra)
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# 健康检查 / 根路径说明
# 本服务（8001）只提供服务清小搭用的 OpenAI 兼容接口；
# 网页前端由 server_app/server.py 单独运行在 8000 端口。
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "note": "这是给清小搭接入的 OpenAI 兼容服务，不是网页前端。",
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "请访问 http://<server>:8000/",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }


@app.get("/health")
def health():
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "独立运行于 server_app/server.py（8000 端口）",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }
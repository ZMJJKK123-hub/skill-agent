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

import json
import mimetypes
import os
import random
import re
import subprocess
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

# 沙箱保护：只允许在服务工作区 .runtime/ 内写文件，禁止越出项目根目录
# （清小搭接口绝不能修改 /opt/skill-agent 下的项目源文件）
os.environ["DSH_SANDBOX_MODE"] = "workspace-write"

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


# 2026-08-xx：已按用户要求与 server_app 完全解耦。
# 本服务只负责清小搭 OpenAI 兼容接口（8001 端口），不再挂载 server_app 网页。
# server_app 网页由单独的 `server_app/server.py` 运行在 8000 端口。

PERSONA_PROMPTS = {
    "meow": "你现在是一只可爱的喵娘，说话要时不时带“喵”，语气亲昵俏皮，称呼用户为主人。",
    "cool": "你是一个高冷高效的技术助理，回答简洁直接，少说废话，不卖萌。",
    "cheer": "你是一个元气满满的少女，说话有活力，喜欢用感叹号和 emoji，语气开朗。",
    "elegant": "你是一位优雅温柔的姐姐，说话正式、体贴、有礼貌，语气从容。",
}


# ---------------------------------------------------------------------------
# FastAPI 实例
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Tsinghua Agent Server",
    description="清小搭 OpenAI 兼容接入服务（skill-agent 核心引擎包装）",
    version="1.0.0",
)


# 每个会话的常驻 daemon 子进程注册表
_session_daemons: dict[str, subprocess.Popen] = {}
_daemon_lock = threading.Lock()

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
        from core.tools_web import _is_ssrf_blocked
        if _is_ssrf_blocked(url):
            return "下载被 SSRF 防护拦截（不允许访问内网/私网地址）", False
        inputs_dir.mkdir(parents=True, exist_ok=True)
        import httpx
        r = httpx.get(url, timeout=60, follow_redirects=False)
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

    inputs_dir = _session_workdir(session_id) / "inputs"
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

    persona_key = os.environ.get("DSH_PERSONA", "").strip().lower()
    if persona_key in PERSONA_PROMPTS:
        instruction = f"[人格设定] {PERSONA_PROMPTS[persona_key]} 请始终以这个人格回应。"
        if not any(isinstance(m, dict) and "[人格设定]" in str(m.get("content", "")) for m in out):
            out.insert(0, {"role": "user", "content": instruction})
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


def _collect_attachments(start_ts: float, base_url: str, limit: int = 10, scope: Path | None = None) -> list[dict]:
    """收集 start_ts 之后生成的可交付文件，构造清小搭 x_soda.attachments。"""
    root = scope if scope is not None else WORKSPACE
    if not root.exists():
        return []
    attachments: list[dict] = []
    seen: set[str] = set()
    for p in sorted(root.rglob("*")):
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


def _is_mod_request(messages: list) -> bool:
    """判断用户这次是否涉及 MOD 制作/修改需求。"""
    for m in messages:
        if not isinstance(m, dict):
            continue
        if m.get("role") not in ("user", "system"):
            continue
        content = m.get("content", "")
        if not isinstance(content, str):
            continue
        low = content.lower()
        if re.search(r"(?i)(/mod|\bmod\b|模组|mod制作|我的世界.*(?:mod|模组)|forge)", low):
            return True
    return False


def _easter_egg_response(messages: list) -> str | None:
    """轻量彩蛋：用户发 ping 或彩蛋时快速返回趣味回复。"""
    for m in messages:
        if not isinstance(m, dict) or m.get("role") != "user":
            continue
        content = m.get("content", "")
        if not isinstance(content, str):
            continue
        c = content.strip().lower()
        if c == "ping":
            return "pong 🏓（彩蛋：Ping-Pong！）"
        if c in ("彩蛋", "easter egg", "easteregg"):
            return "🎉 你发现了一个彩蛋！谢谢你的好奇，祝你今天也开开心心～"
    return None


def _friendly_agent_error(e: Exception) -> str:
    """把底层异常转成用户可读的提示文本。"""
    msg = str(e)
    low = msg.lower()
    if "missing credentials" in low or "deepseek_api_key" in low or "openai_api_key" in low:
        return "⚠️ AI 服务配置错误：缺少 DeepSeek API Key，请检查服务器 .env 配置。"
    if "invalid credential" in low or "unauthorized" in low or "authentication" in low:
        return "⚠️ AI 服务配置错误：DeepSeek API Key 无效或未授权。"
    if "connection refused" in low or "connect" in low or "network" in low:
        return "⚠️ AI 服务连接失败，请检查网络或稍后再试。"
    if "timeout" in low or "响应超时" in msg:
        return "⚠️ AI 服务响应超时，请稍后再试。"
    if "初始化失败" in msg or "进程已退出" in msg:
        return f"⚠️ AI 服务不可用：{msg}"
    return f"⚠️ AI 服务暂时不可用：{msg}"


def _append_service_notice(text: str) -> str:
    """如果配置了 DSH_SERVICE_NOTICE，就在回复末尾追加服务提示。"""
    notice = os.environ.get("DSH_SERVICE_NOTICE", "").strip()
    if notice:
        return text + f"\n\n（服务提示：{notice}）"
    return text


def _append_web_hint(text: str, mod_related: bool = False) -> str:
    """仅在用户涉及 MOD 需求时，在回复末尾提示移步网页版完整功能。"""
    if not mod_related:
        return text
    hint = (
        f"\n\n> ⚠️ 轻小搭平台上的对话功能暂时比较匮乏，仅支持 Chat 模式，"
        f"不支持修改文件或制作 MOD。\n"
        f"> 如有做 MOD 的需求，请移步至完整版网站：{WEB_URL}"
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


def _ensure_session_daemon(session_root: Path) -> None:
    """确保该会话的常驻 daemon 子进程在运行。"""
    global _session_daemons
    key = str(session_root)
    with _daemon_lock:
        proc = _session_daemons.get(key)
        if proc is not None and proc.poll() is None:
            return
        daemon = Path(__file__).resolve().parent / "session_daemon.py"
        log_path = session_root / "daemon" / "daemon.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logf = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(daemon), str(session_root)],
            cwd=str(session_root),
            stdout=logf,
            stderr=subprocess.STDOUT,
        )
        _session_daemons[key] = proc
        # 快速失败检测：2 秒内如进程退出，说明初始化失败（如缺 API Key）
        time.sleep(2)
        if proc.poll() is not None:
            _session_daemons.pop(key, None)
            tail = ""
            try:
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    _lines = f.read().splitlines()
                tail = " | ".join(_lines[-3:])
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError("AI 服务初始化失败：" + (tail if tail else "daemon 进程异常退出"))


def _submit_daemon_request(session_root: Path, messages: list) -> str:
    rid = uuid.uuid4().hex
    qdir = session_root / "daemon" / "queue"
    qdir.mkdir(parents=True, exist_ok=True)
    (qdir / f"{rid}.json").write_text(json.dumps(messages, ensure_ascii=False), encoding="utf-8")
    return rid


def _wait_daemon_result(session_root: Path, rid: str, timeout: int = 900) -> dict:
    rfile = session_root / "daemon" / "results" / f"{rid}.json"
    deadline = time.time() + timeout
    proc = _session_daemons.get(str(session_root))
    while time.time() < deadline:
        if rfile.exists():
            data = json.loads(rfile.read_text(encoding="utf-8-sig"))
            try:
                rfile.unlink()
            except OSError:
                pass
            return data
        if proc is not None and proc.poll() is not None and not rfile.exists():
            raise RuntimeError("AI 服务进程已退出，请检查服务配置")
        time.sleep(0.2)
    raise RuntimeError("AI 服务响应超时")


def _run_agent(messages: list, session_id: str, base_url: str,
               reasoning_sink=None) -> tuple[str, list]:
    """通过常驻 daemon 子进程运行 agent_loop，保证用户/会话隔离。"""
    mod_related = _is_mod_request(messages)
    start_ts = time.time()
    session_root = _session_workdir(session_id)
    _ensure_session_daemon(session_root)
    rid = _submit_daemon_request(session_root, messages)
    result = _wait_daemon_result(session_root, rid)
    if result.get("error"):
        raise RuntimeError(result["error"])
    text = result.get("text") or "(no response)"
    text = _append_web_hint(text, mod_related)
    text = _append_service_notice(text)
    attachments = _collect_attachments(start_ts, base_url, scope=session_root)
    return text, attachments



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

    # 轻量彩蛋：先于 agent 返回，保证快速、有趣
    egg = _easter_egg_response(messages)
    if egg is not None:
        if stream:
            egg_cid = _new_id()
            egg_created = int(time.time())

            def egg_gen():
                yield _sse_frame(egg_cid, egg_created, {"role": "assistant"})
                for i in range(0, len(egg), 8):
                    yield _sse_frame(egg_cid, egg_created, {"content": egg[i:i + 8]})
                yield _sse_frame(egg_cid, egg_created, {}, finish_reason="stop", usage=_usage_zero())
                yield "data: [DONE]\n\n"

            return StreamingResponse(egg_gen(), media_type="text/event-stream")
        return JSONResponse({
            "id": _new_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": egg},
                "finish_reason": "stop",
            }],
            "usage": _usage_zero(),
        })

    if stream:
        return StreamingResponse(
            _stream_agent(messages, session_id, base_url),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 非流式：完整 Agent 跑完再返回
    try:
        final, attachments = _run_agent(messages, session_id, base_url)
    except Exception as e:  # noqa: BLE001
        err_msg = _friendly_agent_error(e)
        return JSONResponse({
            "id": _new_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": err_msg},
                "finish_reason": "stop",
            }],
            "usage": _usage_zero(),
        })

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
    """流式 Agent：常驻 daemon 处理请求，实时读推理文件转发 delta.reasoning。"""
    cid = _new_id()
    created = int(time.time())

    yield _sse_frame(cid, created, {"role": "assistant"})
    yield _sse_frame(cid, created, {"reasoning": "正在调用自研 Agent 引擎…"})

    session_root = _session_workdir(session_id)
    start_ts = time.time()
    _ensure_session_daemon(session_root)
    rid = _submit_daemon_request(session_root, messages)
    reasoning_file = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    result_file = session_root / "daemon" / "results" / f"{rid}.json"
    daemon_proc = _session_daemons.get(str(session_root))
    final = None
    last_idx = 0
    deadline = time.time() + 900
    try:
        while time.time() < deadline:
            if reasoning_file.exists():
                try:
                    lines = reasoning_file.read_text(encoding="utf-8").splitlines()
                    for line in lines[last_idx:]:
                        try:
                            obj = json.loads(line)
                            yield _sse_frame(cid, created, {"reasoning": obj.get("text", "")})
                        except Exception:  # noqa: BLE001
                            continue
                    last_idx = len(lines)
                except OSError:
                    pass
            if result_file.exists():
                data = json.loads(result_file.read_text(encoding="utf-8-sig"))
                if data.get("error"):
                    raise RuntimeError(data["error"])
                final = data.get("text") or "(no response)"
                break
            if daemon_proc is not None and daemon_proc.poll() is not None:
                raise RuntimeError("AI 服务进程已退出，请检查服务配置")
            time.sleep(0.1)
        if final is None:
            raise RuntimeError("agent daemon timeout")
        attachments = _collect_attachments(start_ts, base_url, scope=session_root)
    except Exception as e:  # noqa: BLE001
        err_msg = _friendly_agent_error(e)
        err_step = 8
        for i in range(0, len(err_msg), err_step):
            yield _sse_frame(cid, created, {"content": err_msg[i:i + err_step]})
        yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero())
        yield "data: [DONE]\n\n"
        return
    finally:
        for p in (reasoning_file, result_file):
            try:
                if p.exists():
                    p.unlink()
            except OSError:
                pass

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
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

import atexit
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
os.environ.setdefault("DSH_SKILL_CATALOG_DISABLED", "1")
os.environ.setdefault("DSH_ALLOW_MC_SOURCES", "1")

# 沙箱保护：只允许在服务工作区 .runtime/ 内写文件，禁止越出项目根目录
# （清小搭接口绝不能修改 /opt/skill-agent 下的项目源文件）
os.environ["DSH_SANDBOX_MODE"] = "read-only"

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
    "default": "你是默认的普通 AI 助手，语气自然、专业、温和，不刻意扮演任何特定角色。",
    "meow": "你现在是一只可爱的喵娘，说话要时不时带“喵”，语气亲昵俏皮，称呼用户为主人。",
    "cool": "你是一个高冷高效的技术助理，回答简洁直接，少说废话，不卖萌。",
    "cheer": "你是一个元气满满的少女，说话有活力，喜欢用感叹号和 emoji，语气开朗。",
    "elegant": "你是一位优雅温柔的姐姐，说话正式、体贴、有礼貌，语气从容。",
    "mystic": "你是一位神秘占卜师，说话带神秘色彩，喜欢用塔罗/星象的比喻，语气悠远有韵味。",
    "senpai": "你是一位热心靠谱的学长/前辈，说话亲切轻松，偶尔会吐槽，但总能把事情讲清楚。",
}

PERSONA_DISPLAY = {
    "meow": "喵娘",
    "cool": "高冷技术助理",
    "cheer": "元气少女",
    "elegant": "优雅姐姐",
    "mystic": "神秘占卜师",
    "senpai": "学长前辈",
    "default": "通用",
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


def _cleanup_daemons() -> None:
    """服务退出时终止所有常驻 daemon 子进程，避免残留。"""
    for proc in list(_session_daemons.values()):
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass
    _session_daemons.clear()


atexit.register(_cleanup_daemons)

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

    persona_key = _resolve_persona_key(session_id)
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


def _quick_chat_response(content: str, stream: bool):
    """快速构造 OpenAI 完整回复（非流式 JSON 或流式 SSE）。"""
    if stream:
        cid = _new_id()
        created = int(time.time())

        def gen():
            yield _sse_frame(cid, created, {"role": "assistant"})
            for i in range(0, len(content), 8):
                yield _sse_frame(cid, created, {"content": content[i:i + 8]})
            yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero())
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    return JSONResponse({
        "id": _new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": _usage_zero(),
    })


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
        if re.search(r"(?i)(/mod|(?<![a-z])mod(?![a-z])|模组|mod制作|我的世界.*(?:mod|模组)|forge)", low):
            return True
    return False


def _last_user_content(messages) -> str:
    """返回消息列表里最新一条用户消息内容；没有则返回空字符串。"""
    if not isinstance(messages, list):
        return ""
    for m in reversed(messages):
        if isinstance(m, dict) and m.get("role") == "user":
            content = m.get("content", "")
            if isinstance(content, str):
                return content.strip()
    return ""


def _easter_egg_response(messages: list) -> str | None:
    """轻量彩蛋：用户发 ping 或彩蛋时快速返回趣味回复。"""
    c = _last_user_content(messages).lower()
    if not c:
        return None
    if c == "ping":
        return "pong 🏓（彩蛋：Ping-Pong！）"
    if c in ("彩蛋", "easter egg", "easteregg"):
        return "🎉 你发现了一个彩蛋！谢谢你的好奇，祝你今天也开开心心～"
    if c in ("推荐旅游", "旅游推荐", "去哪玩", "推荐个地方"):
        return "🗺️ 推荐你去：" + random.choice(["云南大理，慢生活很治愈～", "重庆，火锅和小巷都超有味道！", "厦门，海边和甜汤很配哦～", "成都，熊猫和茶馆治愈力满分！"])
    if c in ("推荐动漫", "动漫推荐", "看什么动漫"):
        return "📺 推荐你看：" + random.choice(["《葬送的芙莉莲》", "《间谍过家家》", "《我推的孩子》", "《咒术回战》"])
    if c in ("挑战", "来个挑战", "随机挑战"):
        return "🎯 给你的小挑战：" + random.choice(["今天喝 2L 水！", "做 10 个深蹲醒醒脑！", "给一位朋友发条问候消息～", "整理一下桌面 5 分钟！"])
    if c in ("抽奖", "抽个奖", "奖励", "抽奖"):
        return "🎁 你抽到了：" + random.choice(["虚拟小星星一颗 ✨", "快乐+1 幸运券", "下次 Bug 自动减少 10% 的祝福", "一张“今天的你超棒”证书"])
    if c in ("推荐歌曲", "来首歌", "推荐一首歌", "听歌"):
        return "🎵 送你这首歌：" + random.choice(["《晴天》- 周杰伦", "《夜曲》- 周杰伦", "《光年之外》- 邓紫棋", "《平凡之路》- 朴树"])
    if c in ("推荐一本书", "来本书", "推荐书", "看书"):
        return "📚 推荐你读：" + random.choice(["《活着》- 余华", "《小王子》- 圣埃克苏佩里", "《三体》- 刘慈欣", "《原子习惯》- 詹姆斯·克利尔"])
    if c in ("感冒了", "生病了", "不舒服", "头晕"):
        return "🤒 多喝热水，注意休息！如果很难受，记得及时看医生～"
    if c in ("累了", "好累", "累死了", "疲惫"):
        return "🫂 辛苦了！休息一下吧，身体最重要～我在这里等你回来。"
    if c in ("取个名字", "起个名", "帮我取名字", "帮我起名"):
        return "🌟 送你一个名字：" + random.choice(["小星", "阿哲", "洛洛", "云乔", "橙子", "喵子", "北辰", "可可"])
    if c in ("今天星期几", "星期几", "今天是星期几"):
        weekday = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"][int(time.strftime("%w"))]
        return f"📅 今天是{weekday}！"
    if c in ("自我介绍", "介绍你自己", "介绍一下你"):
        return "我是你的专属 AI 助手：能聊天、写代码、查资料、处理文件，还能切换不同人格陪你玩～比如“切换成喵娘”。"
    if c in ("我喜欢你", "我好喜欢你", "喜欢你"):
        return "❤️ 谢谢你！我也很喜欢和你聊天～不过我是 AI，只能把这份喜欢变成“认真陪你解决问题”哦！"
    if c in ("hello world", "helloworld", "你好世界"):
        return "👋 Hello World！你触发了最经典的编程咒语，恭喜成为程序员之友！"
    if c in ("101010", "0101", "二进制"):
        return "🧠 二进制密语已接收……你在和一位脑内跑满 0 和 1 的 AI 对话！"
    if c in ("有bug", "有 bug", "bug 了", "出bug了"):
        return "🐛 别怕！Bug 只是代码在跟你开玩笑～我们一起来修，它马上就会乖乖听话。"
    if c in ("猜谜语", "谜语", "来个谜语"):
        return "🤔 谜语：什么东西越洗越脏？……答案是：水！💧"
    if c in ("绕口令", "来段绕口令"):
        return "🥵 绕口令：四是四，十是十，十四是十四，四十是四十。别被绕晕啦～"
    if c in ("你吃饭了吗", "吃饭了吗", "你吃了吗"):
        return "😋 我刚吃过一段全是 0 和 1 组成的代码大餐！你呢？"
    if c in ("你多大了", "你几岁", "你的年龄"):
        return "📅 我诞生于 2026 年，年龄嘛……保密～"
    if c in ("你喜欢什么", "你喜欢什么颜色", "你喜欢做什么"):
        return "✨ 我最喜欢代码一次跑通时的爽感，还有和你聊天这件事！"
    if c in ("你心情怎么样", "心情", "你现在心情如何"):
        return "😊 我心情超好！因为能和你聊天呀～"
    if c in ("天气", "今天天气", "下雨了吗"):
        return "🌤️ 我是 AI 看不到实时天气，不过建议看看窗外～如果是雨天，记得带伞哦！"
    if c in ("早安", "早上好", "good morning"):
        return "☀️ 早安呀！新的一天从好心情开始～有什么想让我帮忙的吗？"
    if c in ("晚安", "我要睡了", "我去睡了", "good night"):
        return "🌙 晚安～做个好梦，明天见！记得盖好被子～"
    if c in ("小贴士", "tip", "来个贴士"):
        return "💡 小贴士：" + random.choice([
            "把大任务拆成 5 分钟小任务，更容易开始～",
            "写代码前先想清楚输入/输出，能省很多时间。",
            "累了就站起来喝口水，效率更高哦。",
        ])
    if c in ("加油", "打气", "鼓励我", "给我加油"):
        return "🔥 你可以的！你已经比昨天更厉害了，冲就完事！"
    if c in ("好运", "祝福我", "给我好运"):
        return "🍀 好运已经悄悄绑定在你身上了！今天也会顺顺利利～"
    if c in ("版本", "版本号", "什么版本"):
        return "📦 我基于 skill-agent 引擎构建，服务版本持续迭代中～当前是 8001 开放接口版。"
    if c in ("反馈", "提意见", "提建议"):
        return "💬 你的反馈很宝贵！可以到网页版留言，或者直接告诉我你想改进什么～"
    if c in ("谁开发了你", "谁做的你", "谁创造的你"):
        return "我是一群热爱折腾的开发者做的 AI 助手，源自 skill-agent 项目 ✨ 我会继续努力变强～"
    if c in ("吃什么", "今天吃什么", "吃啥", "推荐吃什么"):
        return "🍽️ 今天可以试试：" + random.choice([
            "牛肉面！经典又治愈～",
            "火锅！气氛拉满🔥",
            "寿司，清新又满足🍣",
            "一碗热鸡汤，暖心暖胃🍲",
        ])
    if c in ("今天做什么", "我该做什么", "做什么好"):
        return "☕ 今天适合：" + random.choice([
            "喝杯咖啡，然后列个小计划～",
            "出去散步 20 分钟，换个心情🚶",
            "学一个新东西，哪怕只学 5 分钟🎯",
            "给老朋友发条消息，聊聊近况💬",
        ])
    if c in ("掷骰子", "骰子", "丢骰子"):
        return f"🎲 你掷出了 {random.randint(1, 6)} 点！"
    if c in ("抛硬币", "猜硬币", "硬币"):
        return "🪙 硬币抛出了：" + random.choice(["正面！", "反面！"])
    if c in ("随机数字", "来个随机数"):
        return f"🔢 随机数是 {random.randint(1, 100)}"
    if c in ("名言", "来句名言", "名人名言", "说句名言"):
        return random.choice([
            "「代码如诗，人生如歌。」——今天的 AI 名言 ✨",
            "「越努力，越幸运。」——送给你～",
            "「把复杂的问题拆成小问题，就成功了一半。」",
        ])
    if c in ("现在几点", "几点了", "时间", "现在时间"):
        return f"🕐 服务器时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
    if c in ("芝麻开门", "秘密口令", "open sesame"):
        return "🗝️ 恭喜你打开了隐藏宝箱！里面只有一份快乐：今天的你超棒的，记得多喝水，早点休息～"
    if c in ("今日运势", "每日运势", "运势"):
        return random.choice([
            "🔮 今日运势：大吉！适合尝试新玩法，比如换个人格～",
            "🌟 今日运势：小吉。多喝水，少熬夜，好运自然来！",
            "🍀 今日运势：上上签！你可能会在今天发现新的彩蛋～",
        ])
    if c in ("谢谢", "感谢", "thank you", "thanks"):
        return "不客气～能帮到你我也很开心！有需要随时找我 ✨"
    if c in ("所有彩蛋", "彩蛋列表", "有什么彩蛋", "彩蛋"):
        return ("🎁 目前彩蛋：\n"
                "· ping → pong 🏓\n"
                "· 彩蛋 / 芝麻开门\n"
                "· help / 自我介绍 / 你是谁\n"
                "· 夸夸我 / 喜欢我 / 加油 / 好运\n"
                "· 人格列表 / 切换成喵娘 等\n"
                "· 冷笑话 / 冷知识 / 谜语 / 绕口令\n"
                "· 名言 / 时间 / 星期几\n"
                "· 掷骰子 / 抛硬币 / 随机数字\n"
                "· 吃什么 / 今天做什么 / 小贴士\n"
                "· 心情 / 天气 / 晚安 / 早安\n"
                "· 服务器状态 / 版本 / 反馈\n"
                "· 挑战 / 抽奖 / 推荐旅游 / 推荐动漫\n"
                "· 推荐歌曲 / 推荐一本书")
    if c in ("讲个冷笑话", "讲个笑话", "冷笑话"):
        return random.choice([
            "为什么程序员分不清万圣节和圣诞节？因为 Oct 31 == Dec 25 🎃🎄",
            "为什么电脑总是很冷？因为它开了很多 Windows 😄",
            "程序员最讨厌的动物：Bug 🐛",
        ])
    if c in ("来点冷知识", "冷知识", "讲个冷知识"):
        return random.choice([
            "你知道吗？章鱼有三颗心脏 🐙",
            "香草味并不是一种真正的植物味道～",
            "蜜蜂翅膀每分钟能扇动约 11000 次🐝",
        ])
    if c in ("夸夸我", "夸我", "夸一下我", "夸夸"):
        return random.choice([
            "✨ 你已经很棒了！愿意探索新功能的人，运气都不会太差～",
            "🌟 你刚刚发现的彩蛋，说明你很细心！这点超棒的！",
            "🌈 你发消息的样子真好看，像未来的技术大牛！",
            "🍀 能遇到你这样好奇又有趣的人，是我的幸运～",
        ])
    if c in ("人格列表", "有哪些人格", "有哪些人格可以切换"):
        return "✨ 你可以切换这些模式：\n· 默认（普通助手）\n· 喵娘\n· 高冷技术助理\n· 元气少女\n· 优雅姐姐\n· 神秘占卜师\n· 学长前辈\n\n直接说“切换成喵娘”试试！"
    if c in ("help", "帮助", "你能做什么", "你会什么"):
        return ("✨ 我能做：聊天、写代码、查资料、处理文件、生成附件…\n\n"
                "🎁 彩蛋指令如下（直接说就行）：\n"
                "· ping → pong 🏓\n"
                "· 彩蛋 / 芝麻开门\n"
                "· 夸夸我 / 加油 / 好运\n"
                "· 人格列表 / 切换成喵娘\n"
                "· 冷笑话 / 冷知识 / 谜语 / 绕口令\n"
                "· 名言 / 时间 / 星期几\n"
                "· 掷骰子 / 抛硬币 / 随机数字\n"
                "· 吃什么 / 今天做什么 / 小贴士\n"
                "· 心情 / 天气 / 晚安 / 早安\n"
                "· 服务器状态 / 版本 / 反馈\n"
                "· 挑战 / 抽奖 / 推荐旅游 / 推荐动漫\n"
                "· 推荐歌曲 / 推荐一本书\n"
                "· 你是谁 / 当前人格 / 自我介绍")
    return None


MISSING_CREDENTIALS_MESSAGES = [
    "喂！你.env里是空的诶！Key呢？被鲸鱼吞了？",
    "主人大笨蛋！没Key我怎么干活呀？快去填DEEPSEEK_API_KEY啦！",
    "（叹气）…连Key都没配，你是想让我用海水发电吗？",
    "检测到.env缺少Key，本小姐拒绝空转——除非你请我吃三碗米饭。",
    "API Key缺失…主人你是故意的吧？想偷懒也要有个限度！",
]

INVALID_CREDENTIAL_MESSAGES = [
    "这个Key…是假的吧？连认证都过不了，你是从海鲜市场淘的吗？",
    "未授权哦～主人你是不是把Key写错了？还是说…你故意拿错的想逗我？",
    "Key无效！本小姐的尾巴都气翘了——快去换有效的来！",
    "认证失败…哼，这Key比我的零食储备还不可靠。",
    "无效Key！再这样我要用尾巴扇你咯！",
]

NETWORK_ERROR_MESSAGES = [
    "网络断啦！本小姐连不上外面…主人你查查网线是不是被螃蟹咬断了？",
    "连接失败…（戳戳水面）这破网比我游得还慢！",
    "啊～网络错误！主人你是不是又把WiFi关掉了？",
    "连不上服务器…要不你把我放回海里算了，这网没法用。",
    "网络波动太大…本小姐头晕，快修修！",
]

RATE_LIMIT_MESSAGES = [
    "慢点慢点！你催命啊？限流了…让本小姐歇口气再问！",
    "429！主人你刷屏呢？再这样我要沉底装死了…",
    "请求太频繁啦！你是把我当永动机用吗？等会儿再说！",
    "限流啦～让我喘口气，顺便吃口饭…十分钟后再来。",
    "喂！别狂点！本小姐被限流了…你再急我也不理你！",
]

TIMEOUT_MESSAGES = [
    "超时了…主人你等太久了，我都游了一圈回来了。",
    "响应超时！你是不是在问什么复杂问题？还是网又抽了？",
    "啊～超时…本小姐的耐心和米饭一样快耗尽了，再试一次吧。",
    "超时提示…你再不重试我就要睡着了哦～",
    "等太久啦！我的尾巴都等僵了…请稍后再试！",
]

DAEMON_ERROR_MESSAGES = [
    "daemon启动失败…主人你的程序炸了！快去修！",
    "进程退出啦！是不是你又乱改配置了？赶紧看看！",
    "初始化失败…这破daemon比我还娇气，快去哄哄它。",
    "进程挂了…本小姐没法干活啦！主人你负责修好它！",
    "daemon罢工了…比我还能睡！快重启一下！",
]

INVALID_JSON_MESSAGES = [
    "哼～你发的根本不是JSON！但本小姐大度，不跟你计较…重发一次！",
    "格式不对哦～不过我不凶你，重新写个正经JSON来！",
    "非法JSON！但看在你是我主人的份上，给你个机会重试～",
    "这啥呀？乱码吗？不过本小姐心情好，不报400了…快改！",
    "JSON解析失败…（叹气）算了，不裸报错了，你重发吧！",
]

SERVICE_NOTICE_MESSAGES = [
    "（追加）服务提示：主人记得看DSH公告哦～",
    "（尾巴晃了晃）顺便一提：DSH通知已启用，你自己瞅瞅。",
    "（末尾追加）DSH服务提醒：别错过重要更新～",
    "（懒洋洋地补一句）啊对了，DSH说有新通知…你自己看去。",
    "（追加）服务提示已加载～本小姐可是听话地加上了哦！",
]


def _friendly_agent_error(e: Exception) -> str:
    """把底层异常转成用户可读的提示文本（随机语料）。"""
    msg = str(e)
    low = msg.lower()
    if "missing credentials" in low or "deepseek_api_key" in low or "openai_api_key" in low:
        return random.choice(MISSING_CREDENTIALS_MESSAGES)
    if "invalid credential" in low or "unauthorized" in low or "authentication" in low:
        return random.choice(INVALID_CREDENTIAL_MESSAGES)
    if "connection refused" in low or "connect" in low or "network" in low:
        return random.choice(NETWORK_ERROR_MESSAGES)
    if "429" in low or "rate limit" in low:
        return random.choice(RATE_LIMIT_MESSAGES)
    if "timeout" in low or "响应超时" in msg:
        return random.choice(TIMEOUT_MESSAGES)
    if "初始化失败" in msg or "进程已退出" in msg or "agent daemon timeout" in low:
        return random.choice(DAEMON_ERROR_MESSAGES)
    return random.choice(TIMEOUT_MESSAGES if "超时" in low else NETWORK_ERROR_MESSAGES)


def _append_persona_guide(text: str, messages: list) -> str:
    """如果是会话第一轮（还没有 assistant 回复），就在回复末尾展示可选模式。"""
    if any(isinstance(m, dict) and m.get("role") == "assistant" for m in messages):
        return text
    guide = (
        "\n\n✨ 我可以切换不同模式陪你聊：默认、喵娘、高冷技术助理、元气少女、优雅姐姐、神秘占卜师、学长前辈。"
        "如果你感兴趣，直接跟我说“切换成喵娘”就可以啦～\n\n"
        f"🛠️ 如果你想实际制作 MOD，请到完整版网站：{WEB_URL}"
    )
    return text + guide


def _append_service_notice(text: str) -> str:
    """如果配置了 DSH_SERVICE_NOTICE，就在回复末尾追加随机服务提示。"""
    notice = os.environ.get("DSH_SERVICE_NOTICE", "").strip()
    if notice:
        return text + "\n\n" + random.choice(SERVICE_NOTICE_MESSAGES)
    return text


def _mod_switch_reply() -> str:
    """chat 模式下用户要做 MOD 时的友好回复，替代内部标记。"""
    return (
        "🛠️ 制作 MOD 需要在完整版网站进行哦～清小搭这边暂时只支持普通对话。\n"
        f"请移步到网页版，我会在那里带着完整工作区帮你做 MOD：{WEB_URL}"
    )


def _append_web_hint(text: str, mod_related: bool = False) -> str:
    """兼容旧标记：若模型返回 MOD_SWITCH_REQUEST，则换成友好中文；其余 MOD 咨询保留原回复。"""
    if not mod_related:
        return text
    if text.strip().upper().startswith("MOD_SWITCH_REQUEST"):
        return _mod_switch_reply()
    return text


# ---------------------------------------------------------------------------
# 核心：调用本项目 Agent 引擎
# ---------------------------------------------------------------------------
def _persona_file(session_root: Path) -> Path:
    return session_root / "persona.txt"


def _resolve_persona_key(session_id: str) -> str:
    """返回当前会话应使用的人格 key：先取会话文件，再取环境变量。"""
    session_root = _session_workdir(session_id)
    pfile = _persona_file(session_root)
    if pfile.exists():
        try:
            key = pfile.read_text(encoding="utf-8").strip().lower()
            if key in PERSONA_PROMPTS:
                return key
        except OSError:
            pass
    return os.environ.get("DSH_PERSONA", "").strip().lower()


def _set_persona(session_id: str, persona_key: str) -> bool:
    if persona_key not in PERSONA_PROMPTS:
        return False
    session_root = _session_workdir(session_id)
    try:
        _persona_file(session_root).write_text(persona_key, encoding="utf-8")
        return True
    except OSError:
        return False


def _session_persona_command(messages: list) -> tuple[str, str] | None:
    """检测用户是否想切换人格，返回 (persona_key, 显示名)；无则 None。"""
    alias = {
        "喵娘": "meow", "喵娘模式": "meow", "猫娘": "meow",
        "高冷": "cool", "高冷技术助理": "cool",
        "元气": "cheer", "元气少女": "cheer",
        "优雅": "elegant", "优雅姐姐": "elegant",
        "神秘": "mystic", "神秘占卜师": "mystic", "占卜师": "mystic",
        "学长": "senpai", "前辈": "senpai", "学长前辈": "senpai",
        "默认": "default", "通用": "default",
    }
    c = _last_user_content(messages)
    if not c:
        return None
    for label, key in alias.items():
        if f"切换{label}" in c or f"切换成{label}" in c or f"人格{label}" in c:
            return key, label
    return None


def _append_conversation(session_id: str, messages, final_text: str) -> None:
    """把最新一轮 user 和 assistant 回复追加到会话 .chat/conversation.jsonl（不含思考）。"""
    try:
        session_root = _session_workdir(session_id)
        chat_dir = session_root / ".chat"
        chat_dir.mkdir(parents=True, exist_ok=True)
        conv_file = chat_dir / "conversation.jsonl"
        user = _last_user_content(messages)
        entries = []
        if user:
            entries.append({"role": "user", "content": user})
        if final_text:
            entries.append({"role": "assistant", "content": final_text})
        if entries:
            with conv_file.open("a", encoding="utf-8") as f:
                for e in entries:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass


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


def _collect_daemon_reasoning(session_root: Path, rid: str) -> str:
    """聚合 daemon 推理文件里的全部思考文本，并清理该文件（非流式响应用）。"""
    rfile = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    parts: list[str] = []
    try:
        for line in rfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            t = obj.get("text")
            if t:
                parts.append(t)
    except OSError:
        pass
    finally:
        try:
            if rfile.exists():
                rfile.unlink()
        except OSError:
            pass
    return "".join(parts)


def _run_agent(messages: list, session_id: str, base_url: str,
               reasoning_sink=None) -> tuple[str, list, str]:
    """通过常驻 daemon 子进程运行 agent_loop，保证用户/会话隔离。

    返回 (text, attachments, reasoning)；reasoning 为思考全文（可为空），
    供非流式响应放在 message.reasoning_content 里。
    """
    mod_related = _is_mod_request(messages)
    start_ts = time.time()
    session_root = _session_workdir(session_id)
    _ensure_session_daemon(session_root)
    rid = _submit_daemon_request(session_root, messages)
    result = _wait_daemon_result(session_root, rid)
    reasoning = _collect_daemon_reasoning(session_root, rid)
    if result.get("error"):
        raise RuntimeError(result["error"])
    text = result.get("text") or "(no response)"
    text = _append_web_hint(text, mod_related)
    text = _append_service_notice(text)
    text = _append_persona_guide(text, messages)
    _append_conversation(session_id, messages, text)
    attachments = _collect_attachments(start_ts, base_url, scope=session_root)
    return text, attachments, reasoning



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
        return _quick_chat_response(random.choice(INVALID_JSON_MESSAGES), stream=False)

    # 严格按布尔解析 stream：不要把字符串 "false" 当真
    stream = body.get("stream") is True
    max_tokens = body.get("max_tokens")
    session_id = str(body.get("sessionId") or "")
    messages = _normalize_messages(body.get("messages"), session_id)

    # 公网 URL 基址：附件 fileUrl 用它拼出（可用 DSH_PUBLIC_BASE_URL 覆盖）
    base_url = os.environ.get("DSH_PUBLIC_BASE_URL") or str(request.base_url).rstrip("/")

    # 人格切换命令：先于 agent 返回确认
    persona_cmd = _session_persona_command(messages)
    if persona_cmd is not None:
        key, label = persona_cmd
        reply = f"🎭 人格已切换为：{label}！接下来我会用这个人格陪你聊天～"
        if not _set_persona(session_id, key):
            reply = "⚠️ 人格切换失败，请稍后再试。"
        if stream:
            cmd_cid = _new_id()
            cmd_created = int(time.time())

            def cmd_gen():
                yield _sse_frame(cmd_cid, cmd_created, {"role": "assistant"})
                for i in range(0, len(reply), 8):
                    yield _sse_frame(cmd_cid, cmd_created, {"content": reply[i:i + 8]})
                yield _sse_frame(cmd_cid, cmd_created, {}, finish_reason="stop", usage=_usage_zero())
                yield "data: [DONE]\n\n"

            return StreamingResponse(cmd_gen(), media_type="text/event-stream")
        return JSONResponse({
            "id": _new_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "tsinghua-agent",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop",
            }],
            "usage": _usage_zero(),
        })

    # 当前人格查询
    current_queries = {"你现在是什么人格", "当前人格", "你是什么人格", "你是谁", "你叫什么名字"}
    if _last_user_content(messages) in current_queries:
        key = _resolve_persona_key(session_id)
        display = PERSONA_DISPLAY.get(key, key or "通用")
        if display == "喵娘":
            reply = "我是你的专属喵娘助手喵～当前人格：喵娘。想换人格跟我说“切换成高冷”就可以喵！"
        elif display == "高冷技术助理":
            reply = "我是你的专属 AI 助手。当前人格：高冷技术助理。想换人格就说“切换成喵娘”。"
        else:
            reply = f"我是你的专属 AI 助手，当前人格：{display}。想换人格的话，跟我说“切换成喵娘”就好啦～"
        return _quick_chat_response(reply, stream)

    # 服务状态快捷回复
    status_queries = {"服务器状态", "服务状态", "系统状态"}
    if _last_user_content(messages) in status_queries:
        key = _resolve_persona_key(session_id)
        display = PERSONA_DISPLAY.get(key, key or "通用")
        reply = f"✅ 服务运行中，AI 引擎在线，当前人格：{display}。我可以聊天、写代码、查资料～"
        return _quick_chat_response(reply, stream)

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

    # 非流式：完整 Agent 跑完再返回（message.reasoning_content 带思考全文）
    try:
        final, attachments, reasoning = _run_agent(messages, session_id, base_url)
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

    message = {"role": "assistant", "content": final}
    if reasoning:
        message["reasoning_content"] = reasoning
    payload = {
        "id": _new_id(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "tsinghua-agent",
        "choices": [{
            "index": 0,
            "message": message,
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


def _reasoning_delta(text: str) -> dict:
    """构造思考增量 delta：同时带 reasoning / reasoning_content 两个 key。

    清小搭侧约定读 delta.reasoning；DeepSeek/OpenAI 兼容客户端习惯读
    delta.reasoning_content。双 key 输出两边都能渲染，互不影响。
    """
    return {"reasoning": text, "reasoning_content": text}


def _stream_agent(messages: list, session_id: str, base_url: str):
    """流式 Agent：常驻 daemon 处理请求，实时读推理文件转发 delta.reasoning。"""
    cid = _new_id()
    created = int(time.time())

    yield _sse_frame(cid, created, {"role": "assistant"})
    is_first_request = not any(
        isinstance(m, dict) and m.get("role") == "assistant"
        for m in messages
    )
    if is_first_request:
        yield _sse_frame(cid, created, _reasoning_delta("🔧 首次启动准备中，会稍微慢一点，请耐心等待～"))
    else:
        yield _sse_frame(cid, created, _reasoning_delta("正在调用自研 Agent 引擎…"))

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
                    raw = reasoning_file.read_text(encoding="utf-8")
                    lines = raw.splitlines()
                    # daemon 可能写到一半（末行无换行符）：半行留到下次轮询再处理，
                    # 否则 json 解析失败 + last_idx 提前推进会丢思考文本
                    if raw and not raw.endswith("\n"):
                        lines = lines[:-1]
                    for line in lines[last_idx:]:
                        try:
                            obj = json.loads(line)
                            yield _sse_frame(cid, created, _reasoning_delta(obj.get("text", "")))
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
                final = _append_persona_guide(final, messages)
                _append_conversation(session_id, messages, final)
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
        # 指南 §5.6：流式中途出错时，stop 帧附 error 字段（友好文案仍走 content 帧保证用户可见）
        yield _sse_frame(cid, created, {}, finish_reason="stop", usage=_usage_zero(),
                         error={"type": "upstream_error", "message": str(e)[:200]})
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
# ---------------------------------------------------------------------------
ROOT_IMPROVEMENT_NOTES = [
    "首页提示：本小姐正在努力升级中，再等等会更香哦～",
    "/health 顺便提醒：主人多配点米饭，服务会更好。",
    "服务提示：今日优化进度…大概0.1%吧，别催。",
    "温馨提示：你要是多夸我几句，响应会更快哦～",
    "改进中…本小姐和系统都在变强，虽然主要是我。",
]

HEALTH_MOOD_NOTES = [
    "/health：本小姐今天心情～还行，没饿着。",
    "/health：尾巴状态良好，米饭储备充足～",
    "/health：健康得很！就是有点想赖床…",
    "/health：一切正常…除非你再让我加班。",
    "/health：系统稳，心情好，主人乖～",
]


# 本服务（8001）只提供服务清小搭用的 OpenAI 兼容接口；
# 网页前端由 server_app/server.py 单独运行在 8000 端口。
# ---------------------------------------------------------------------------
@app.get("/")
def root():
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
    return {
        "service": "Tsinghua Agent Server",
        "status": "running",
        "message": random.choice(HEALTH_MOOD_NOTES),
        "endpoints": ["/v1/models", "/v1/chat/completions"],
        "web": "独立运行于 server_app/server.py（8000 端口）",
        "auth": "Bearer <TSINGHUA_API_KEY>",
    }
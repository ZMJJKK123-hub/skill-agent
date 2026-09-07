# -*- coding: utf-8 -*-
"""识图包：截图 + 视觉 API 分析 + 焦点保护。
由单文件 vision.py 拆分；再导出保持兼容。
"""
# -*- coding: utf-8 -*-
"""Vision mode: screenshot + analyze_image implementations (moved from core/tools.py)."""
import os
import time
from pathlib import Path

from ....config import logger, safe_path
from ..runtime import worktree_manager

# ---------- 识图模式：截图 + 图片识别 ----------
# 视觉 API 使用独立 OpenAI 兼容客户端（DSH_VISION_*），与主模型 client 分离：
# DeepSeek 官方 API 图片输入不可靠，需由用户单独配置 GPT-4o / Qwen-VL / GLM-4V 等。
_vision_client = None
_vision_http_client = None

# 智谱 GLM-4.6V-Flash 免费视觉模型的本地配置目录（用户克隆的 glm4v-vision-mcp）。
# 如果设置面板没有填视觉 API，就自动读取该目录 server/.env 里的 ZHIPU_API_KEY。
_GLM4V_DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
_GLM4V_DEFAULT_MODEL = "glm-4.6v-flash"


def _vision_enabled() -> bool:
    # 默认开启（用户要求）。screenshot 只依赖 PIL，开启即可用；
    # analyze_image 在未配置视觉 API 时会返回明确的"未配置"提示。
    # 显式设置 DSH_VISION_ENABLED=0 仍可关闭。
    return os.environ.get("DSH_VISION_ENABLED", "1") != "0"


def _glm4v_env_path():
    """定位 glm4v-vision-mcp 的 server/.env（可用 DSH_GLM4V_ENV_FILE 覆盖）。"""
    override = os.environ.get("DSH_GLM4V_ENV_FILE", "").strip()
    if override:
        p = Path(override)
        if p.is_file():
            return p
    home = Path.home()
    candidates = [
        home / "Desktop" / "glm4v-vision-mcp" / "server" / ".env",
        home / "OneDrive" / "Desktop" / "glm4v-vision-mcp" / "server" / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _load_env_file(path: Path) -> dict:
    """极简 .env 解析（支持 KEY=VALUE、引号、# 注释）。"""
    data = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return data
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            data[key] = value
    return data


def _resolve_vision_config():
    """返回 (api_key, base_url, model)。

    优先使用用户显式配置的 DSH_VISION_*；没有配置时自动回退到桌面
    glm4v-vision-mcp 的免费 GLM-4.6V-Flash（读取 server/.env 的 ZHIPU_API_KEY）。
    """
    api_key = os.environ.get("DSH_VISION_API_KEY", "").strip()
    base_url = os.environ.get("DSH_VISION_BASE_URL", "").strip()
    model = os.environ.get("DSH_VISION_MODEL", "").strip()
    if api_key and base_url and model:
        return api_key, base_url, model
    env_path = _glm4v_env_path()
    if env_path:
        data = _load_env_file(env_path)
        zkey = (data.get("ZHIPU_API_KEY") or data.get("GLM_API_KEY") or "").strip()
        if zkey:
            return zkey, _GLM4V_DEFAULT_BASE_URL, _GLM4V_DEFAULT_MODEL
    return api_key, base_url, model


def _get_vision_client():
    """惰性创建视觉 API 的 OpenAI 客户端（进程内复用）。"""
    global _vision_client, _vision_http_client
    if _vision_client is None:
        import httpx as _httpx
        from openai import OpenAI
        api_key, base_url, _model = _resolve_vision_config()
        _vision_http_client = _httpx.Client(
            trust_env=False,
            verify=False,
            timeout=180.0,
        )
        _vision_client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=_vision_http_client,
        )
    return _vision_client


# ── 用户焦点保护：抢焦点前记录用户正在用的窗口，用完立刻归还 ──
# 客户端验证会反复把 MC 窗口置前（截图需要）+ 游戏捕获鼠标，用户的
# 光标被框在游戏里动弹不得直到验证结束（用户实测反馈）。协议：任何
# 抢焦点操作前 remember，操作完 restore——MC 失焦即自动释放鼠标捕获。
_user_fg = {"hwnd": None, "ts": 0.0}



def run_screenshot(region: dict = None) -> str:
    """截取当前屏幕；无 region 时自动聚焦 Minecraft 窗口并按其矩形裁剪。"""
    try:
        if not _vision_enabled():
            return "Error: 识图模式未开启（DSH_VISION_ENABLED=0）"
        from PIL import ImageGrab
        if region:
            try:
                left = int(region.get("left", 0))
                top = int(region.get("top", 0))
                width = int(region.get("width", 0))
                height = int(region.get("height", 0))
            except (TypeError, ValueError):
                return "Error: region must contain integer left/top/width/height"
            if width <= 0 or height <= 0:
                return "Error: region width/height must be positive"
            bbox = (left, top, left + width, top + height)
            img = ImageGrab.grab(bbox=bbox)
        else:
            box = _focus_minecraft_window()
            img = ImageGrab.grab(bbox=box)  # box=None 时回退全屏（原行为）
        base = worktree_manager.resolve_dir() if worktree_manager else Path.cwd()
        shot_dir = Path(base) / ".screenshots"
        shot_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = shot_dir / f"shot_{ts}.png"
        counter = 1
        while path.exists():
            path = shot_dir / f"shot_{ts}_{counter}.png"
            counter += 1
        img.save(path, "PNG")
        # 截完立刻把焦点还给用户正在用的窗口——MC 失焦自动暂停并释放
        # 鼠标捕获，用户的光标只在截图的约 1 秒内被游戏占用
        _restore_user_foreground()
        return f"Screenshot saved: {path.resolve()}"
    except Exception as e:
        return f"Error: screenshot failed: {e}"


def run_analyze_image(image_path: str, prompt: str = None) -> str:
    """读取图片并调用视觉 API 识别，返回模型描述文本（用于判断游戏/MOD 画面是否正常）。"""
    try:
        if not _vision_enabled():
            return "Error: 识图模式未开启（DSH_VISION_ENABLED=0）"
        api_key, base_url, model = _resolve_vision_config()
        if not api_key or not base_url or not model:
            return ("Error: 视觉 API 未配置（需要 DSH_VISION_API_KEY / "
                    "DSH_VISION_BASE_URL / DSH_VISION_MODEL，"
                    "或桌面 glm4v-vision-mcp/server/.env 里有 ZHIPU_API_KEY）")
        base = worktree_manager.resolve_dir() if worktree_manager else None
        p = safe_path(image_path, base)
        if not p.is_file():
            return f"Error: image not found: {image_path}"
        from PIL import Image
        import base64
        import io
        img = Image.open(p)
        # 缩放 + JPEG 压缩，降低 token/带宽消耗
        max_dim = 1280
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim))
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        text = prompt or (
            "Describe this image in detail. Focus on game/MOD UI state, "
            "errors, crash screens, or anomalies."
        )
        client = _get_vision_client()
        # 免费模型容易 429/5xx，做几次退避重试（与 glm4v-vision-mcp 行为一致）
        last_err = None
        for attempt in range(4):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text},
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                            }},
                        ],
                    }],
                    max_tokens=2000,
                )
                content = resp.choices[0].message.content
                return content or "(empty vision response)"
            except Exception as e:
                last_err = e
                status = getattr(e, "status_code", None)
                if status in (429, 500, 502, 503, 504):
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
        return f"Error: analyze_image failed after retries: {last_err}"
    except Exception as e:
        return f"Error: analyze_image failed: {e}"



# 焦点保护族再导出（game/input.py 引用）
from .focus import (focus_game_window, restore_user_window,  # noqa: E402,F401
                    _remember_user_foreground, _restore_user_foreground,
                    _focus_minecraft_window)

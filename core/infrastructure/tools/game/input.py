# -*- coding: utf-8 -*-
"""进程内 UI 自动化：AgentBridge 命令桥 + 键盘/焦点。
由 game.py 原样迁出。
"""
import ctypes
import json
import os
import re
import time
from pathlib import Path

from .rcon import _VK_MAP  # 键名→虚拟键码表（rcon 域持有）

from ....config import logger
from ..runtime import worktree_manager
from ..vision import run_analyze_image, run_screenshot
from .rcon import _base_dir
from ....config import logger  # 统一日志：降级路径记录


def _vk_code(key: str) -> int:
    k = key.strip().lower()
    if k in _VK_MAP:
        return _VK_MAP[k]
    if len(k) == 1 and k.isprintable():
        return ord(k.upper())
    raise ValueError(f"Unknown key: {key}")


def bridge_command(op: str, index: int = None, value: str = None,
                   text: str = None, name: str = None, timeout: int = 10,
                   x: int = None, y: int = None, z: int = None,
                   where: str = None, dir: str = None,
                   nearest: float = None, entity_type: str = None) -> str:
    """进程内 UI 自动化桥：直接调用按钮背后的 Java 函数（AgentBridge mod）。

    前置：starter/bridge/AgentBridge.java 已复制进 src/main，主 @Mod 构造器末尾
    以 FMLEnvironment.dist.isClient() 守卫实例化（缺守卫 GameTest 服务器会
    DISTXFORM 崩溃），客户端经 start_mc_client 启动。协议：写 run/bridge_cmd.json
    （含唯一 id），轮询 run/bridge_result.json 直到 id 匹配；screenshot 额外等图片落盘。
    """
    import json as _json
    from pathlib import Path as _P
    try:
        base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
        run_dir = _P(base) / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        cmd_id = f"{int(time.time() * 1000)}-{os.urandom(3).hex()}"
        payload = {"id": cmd_id, "op": op}
        if index is not None:
            payload["index"] = int(index)
        if value is not None:
            payload["value"] = str(value)
        if text is not None:
            payload["text"] = str(text)
        if name is not None:
            payload["name"] = str(name)
        if x is not None:
            payload["x"] = int(x)
        if y is not None:
            payload["y"] = int(y)
        if z is not None:
            payload["z"] = int(z)
        if where is not None:
            payload["where"] = str(where)
        if dir is not None:
            payload["dir"] = str(dir)
        if nearest is not None:
            payload["nearest"] = float(nearest)
        if entity_type is not None:
            payload["type"] = str(entity_type)
        result_path = run_dir / "bridge_result.json"
        result_path.unlink(missing_ok=True)  # 清掉旧结果，避免读到上条
        (run_dir / "bridge_cmd.json").write_text(
            _json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.2)
            try:
                data = _json.loads(result_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data.get("id") != cmd_id:
                continue
            if op == "screenshot" and data.get("ok"):
                # grab 写 <dir>/screenshots/<时间戳>.png（异步 ioPool）——按 mtime 等新文件
                shot_dir = _P(data.get("path", ""))
                if shot_dir.is_dir():
                    t0 = time.time()
                    newest = None
                    while time.time() - t0 < 4:
                        pngs = sorted(shot_dir.glob("*.png"), key=lambda p: p.stat().st_mtime)
                        if pngs and pngs[-1].stat().st_mtime >= t0 - 1:
                            newest = pngs[-1]
                            if pngs[-1].stat().st_mtime > t0:
                                break
                        time.sleep(0.3)
                    if newest:
                        data["path"] = str(newest)
                        data["file_ready"] = True
                    else:
                        data["file_ready"] = False
            return _json.dumps(data, ensure_ascii=False)
        return (f"Error: bridge_command timeout ({timeout}s) — op={op}。"
                "请确认：AgentBridge 已注册、客户端(run_test_client)仍在运行。")
    except Exception as e:
        return f"Error: bridge_command failed: {e}"


def _borrow_game_focus():
    """窗口级输入（keybd_event/SendInput 发给"当前焦点窗口"）前借用焦点：
    置前 MC 窗口，返回是否成功。焦点归还协议见 tools_vision——
    平时焦点保持在用户手里（截图/按键只在瞬间借用并立刻归还），
    不借用的话按键会打进用户正在用的窗口。"""
    try:
        from ..vision import focus_game_window
        return focus_game_window(wait=0.25, maximize=False)
    except Exception:
        return False


def _return_focus():
    try:
        from ..vision import restore_user_window
        restore_user_window()
    except Exception as e:
        logger.debug("_return_focus 降级忽略 | %s", e)


def game_input(action: str, key: str = None, text: str = None) -> str:
    """Generic game input: action='key' -> press_key(key), action='type' -> type_text(text)."""
    action = (action or "type").lower()
    if action in ("key", "press", "press_key"):
        if not key:
            return "Error: game_input key action requires 'key'"
        return press_key(key)
    if action in ("type", "text", "type_text"):
        if text is None:
            return "Error: game_input type action requires 'text'"
        return type_text(text)
    return "Error: game_input action must be 'key' or 'type'"


# ── Wait helpers ──────────────────────────────────────────────────────
def wait_for_log(pattern: str, timeout: int = 60, log_path: str = None) -> str:
    """Wait until a regex pattern appears in a log file (default run/logs/latest.log)."""
    base = _base_dir()
    base_resolved = Path(base).resolve()
    path = Path(log_path) if log_path else Path(base) / "run/logs/latest.log"
    if not path.is_absolute():
        path = Path(base) / path
    if not path.resolve().is_relative_to(base_resolved):
        return f"Error: log_path 越出工作区: {path}"
    deadline = time.time() + max(1, int(timeout))
    rx = re.compile(pattern, re.I)
    while time.time() < deadline:
        try:
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="replace")
                if rx.search(text):
                    return f"Found pattern '{pattern}' in {path}"
        except OSError as e:
            logger.warning("wait_for_log 降级忽略 | %s", e)
        time.sleep(1)
    return f"Timeout waiting for pattern '{pattern}' in {path}"


def wait_for_screen(duration: int = 5, prompt: str = None) -> str:
    """Wait N seconds, take a screenshot, and optionally analyze it with vision API."""
    time.sleep(max(0, int(duration)))
    shot = run_screenshot()
    lines = [f"Screenshot after {duration}s: {shot}"]
    if prompt:
        analysis = run_analyze_image(str(shot).replace("Screenshot saved: ", ""), prompt)
        lines.append(f"Analysis: {analysis}")
    return "\n".join(lines)


# ── Visual verify loop ────────────────────────────────────────────────


# 视觉验证循环拆至 verify（handlers 引用；再导出保持兼容）
from .verify import verify_visual_loop  # noqa: E402,F401

# 键盘输入域拆至 keys（handlers 引用；再导出保持兼容）
from .keys import press_key, press_keys, type_text  # noqa: E402,F401

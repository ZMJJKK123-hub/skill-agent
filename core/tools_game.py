# -*- coding: utf-8 -*-
"""Game interaction tools: RCON commands, Windows input, log/screen waiting, visual verify loop."""
import ctypes
import os
import re
import socket
import struct
import subprocess
import time
from pathlib import Path

from .config import logger
from .tools_runtime import worktree_manager
from .tools_vision import run_analyze_image, run_screenshot


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


# ── RCON ──────────────────────────────────────────────────────────────
def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("RCON connection closed")
        buf += chunk
    return buf


def _rcon_packet(sock: socket.socket, req_id: int, ptype: int, payload: str):
    body = struct.pack("<ii", req_id, ptype) + payload.encode("utf-8") + b"\x00\x00"
    sock.sendall(struct.pack("<i", len(body)) + body)
    length = struct.unpack("<i", _recv_exact(sock, 4))[0]
    resp_body = _recv_exact(sock, length)
    rid, rtype = struct.unpack("<ii", resp_body[:8])
    text = resp_body[8:-2].decode("utf-8", errors="replace")
    return rid, rtype, text


def send_game_command(command: str, host: str = "127.0.0.1", port: int = 25575,
                      password: str = None) -> str:
    """Send a Minecraft RCON command to a running server/client with RCON enabled."""
    password = password or os.environ.get("DSH_RCON_PASSWORD", "")
    if not password:
        return "Error: RCON password not provided (set password parameter or DSH_RCON_PASSWORD)"
    try:
        with socket.create_connection((host, int(port)), timeout=10) as sock:
            rid, rtype, _ = _rcon_packet(sock, 1, 3, password)
            if rid == -1:
                return "Error: RCON authentication failed"
            rid, rtype, text = _rcon_packet(sock, 2, 2, command)
            return text if text.strip() else "(empty RCON response)"
    except Exception as e:
        return f"Error: RCON failed: {e}"


# ── Windows input ─────────────────────────────────────────────────────
_VK_MAP = {
    "enter": 0x0D, "return": 0x0D, "esc": 0x1B, "escape": 0x1B,
    "tab": 0x09, "space": 0x20, "backspace": 0x08, "delete": 0x2E,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    # 鼠标键（webserv_heaven 实测：此前无右键，无法程序化"使用物品"如传送羽毛）
    "right_click": 0x02, "use": 0x02, "mouse_right": 0x02, "rbutton": 0x02,
    "left_click": 0x01, "attack": 0x01, "mouse_left": 0x01, "lbutton": 0x01,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "shift": 0x10, "ctrl": 0x11, "control": 0x11, "alt": 0x12,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45,
    "f": 0x46, "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A,
    "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F,
    "p": 0x50, "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54,
    "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58, "y": 0x59, "z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
}


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
        shot_path = None
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
        from .tools_vision import focus_game_window
        return focus_game_window(wait=0.25, maximize=False)
    except Exception:
        return False


def _return_focus():
    try:
        from .tools_vision import restore_user_window
        restore_user_window()
    except Exception:
        pass


def press_keys(sequence: list) -> str:
    """按脚本顺序在游戏窗口模拟按键（代码级 UI 导航，无需截图决策）。

    整个序列借用一次游戏焦点、结束后归还（避免逐键反复抢还抖动）。
    sequence 每项：
      - 单键名（同 press_key 规则）：tab / enter / esc / e / t ...
      - "wait:500"   等待 500ms（切屏/加载时用）
      - "type:文本"  输入文本（走 type_text，支持中文）
    返回逐步执行日志；任一步失败即中止并返回已执行步骤。
    """
    steps = []
    focused = _borrow_game_focus()
    try:
        for i, item in enumerate(sequence):
            s = str(item).strip()
            low = s.lower()
            if low.startswith("wait:"):
                ms = int(s.split(":", 1)[1])
                time.sleep(ms / 1000.0)
                steps.append(f"{i + 1}. wait {ms}ms")
            elif low.startswith("type:"):
                text = s.split(":", 1)[1]
                r = type_text(text, _focus_managed=True)
                steps.append(f"{i + 1}. type '{text}' -> {r}")
                time.sleep(0.15)
            else:
                steps.append(f"{i + 1}. press {s} -> {press_key(s, _focus_managed=True)}")
                time.sleep(0.15)
        return "Executed:\n" + "\n".join(steps)
    except Exception as e:
        return (f"Error: press_keys failed at step {len(steps) + 1}: {e}\n"
                "Executed:\n" + "\n".join(steps))
    finally:
        if focused:
            _return_focus()


def press_key(key: str, _focus_managed: bool = False) -> str:
    """Press and release a single key (Windows SendInput via keybd_event).

    _focus_managed=True 时认为调用方（press_keys）已借用游戏焦点，
    不再自行借还；单独调用时自借自还。
    """
    focused = False if _focus_managed else _borrow_game_focus()
    try:
        vk = _vk_code(key)
        user32 = ctypes.windll.user32
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(vk, 0, 2, 0)
        return f"Pressed {key}"
    except Exception as e:
        return f"Error: press_key failed: {e}"
    finally:
        if focused:
            _return_focus()


def type_text(text: str, _focus_managed: bool = False) -> str:
    """Type Unicode text into the game window (Windows SendInput).

    _focus_managed=True 时认为调用方（press_keys）已借用游戏焦点。
    """
    focused = False if _focus_managed else _borrow_game_focus()
    try:
        user32 = ctypes.windll.user32

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT), ("padding", ctypes.c_byte * 24)]
            _anonymous_ = ("_input",)
            _fields_ = [("type", ctypes.c_ulong), ("_input", _INPUT)]

        def send_unicode(char: str):
            inp = INPUT()
            inp.type = 1  # INPUT_KEYBOARD
            inp.ki.wVk = 0
            inp.ki.wScan = ord(char)
            inp.ki.dwFlags = 0x0004  # KEYEVENTF_UNICODE
            inp.ki.time = 0
            inp.ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
            inp.ki.dwFlags = 0x0004 | 0x0002  # KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

        for ch in text:
            send_unicode(ch)
            time.sleep(0.01)
        return f"Typed {len(text)} characters"
    except Exception as e:
        return f"Error: type_text failed: {e}"
    finally:
        if focused:
            _return_focus()


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
        except OSError:
            pass
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
def verify_visual_loop(prompt: str, max_attempts: int = 3, interval: int = 5,
                       command: str = None, rcon_password: str = None,
                       rcon_port: int = 25575) -> str:
    """Repeatedly send optional RCON command, screenshot, and analyze the screen."""
    max_attempts = max(1, int(max_attempts))
    interval = max(1, int(interval))
    out = [f"Visual verify loop: {max_attempts} attempts, interval {interval}s"]
    for i in range(1, max_attempts + 1):
        out.append(f"--- Attempt {i}/{max_attempts} ---")
        if command:
            out.append("RCON: " + send_game_command(command, port=rcon_port, password=rcon_password))
        time.sleep(interval)
        shot = run_screenshot()
        out.append(shot)
        if prompt:
            path = shot.replace("Screenshot saved: ", "").strip()
            out.append("Analysis: " + run_analyze_image(path, prompt))
    return "\n".join(out)

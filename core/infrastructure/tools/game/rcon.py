# -*- coding: utf-8 -*-
"""RCON 底座：Socket RCON 协议 + send_game_command。
由 game.py 原样迁出。
"""
import os  # 环境变量与进程级路径操作
import socket
import struct
import time
from pathlib import Path

from ....config import logger
from ..runtime import worktree_manager


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



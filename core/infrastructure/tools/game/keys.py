# -*- coding: utf-8 -*-
"""游戏键盘/文本输入（由 input.py 拆出）。

类职责：press_keys 序列按键 / press_key 单键 / type_text 逐字输入；
均带焦点保护（_focus_managed 由组合调用方管理）。
生命周期：handlers 注册与 game_input 分发调用。
"""
from ....config import logger  # 统一日志
from .input import _borrow_game_focus, _return_focus, _vk_code  # 焦点保护与键码表

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

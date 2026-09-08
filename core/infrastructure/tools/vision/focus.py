# -*- coding: utf-8 -*-
"""用户焦点保护：截图前借用前台、截后归还（防打扰用户桌面）。
由 vision.py 原样迁出。
"""
import os
import time

from ....config import logger


def _remember_user_foreground() -> None:
    from . import _user_fg  # 延迟导入：vision 包组合本模块，避免环
    """抢焦点前记录用户当前前台窗口（MC 自身与无标题窗口不记）。

    10 秒内的连续抢焦点（同一次验证的连续截图/按键）视为一批，
    不重复记录——避免第二次抢焦点时把 MC 当成"用户窗口"记下来。
    """
    now = time.time()
    if _user_fg["hwnd"] and now - _user_fg["ts"] < 10:
        _user_fg["ts"] = now
        return
    _user_fg["hwnd"] = None
    _user_fg["ts"] = now
    if os.name != "nt":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return
        length = user32.GetWindowTextLengthW(hwnd)
        if not length:
            return
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if buf.value and "minecraft" not in buf.value.lower():
            _user_fg["hwnd"] = hwnd
    except Exception as e:
        logger.debug("_remember_user_foreground 降级忽略 | %s", e)


def _restore_user_foreground() -> None:
    from . import _user_fg  # 延迟导入：同上
    """把焦点还给用户正在用的窗口（ALT 技巧绕过 Windows 前台锁定）。"""
    hwnd = _user_fg["hwnd"]
    if not hwnd or time.time() - _user_fg["ts"] > 60:
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        if not user32.IsWindow(hwnd):
            return
        user32.keybd_event(0x12, 0, 0, 0)   # ALT down
        user32.keybd_event(0x12, 0, 2, 0)   # ALT up
        user32.ShowWindow(hwnd, 9)          # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
    except Exception as e:
        logger.debug("_restore_user_foreground 降级忽略 | %s", e)


def focus_game_window(wait: float = 0.3, maximize: bool = False) -> bool:
    """置前 Minecraft 窗口（按键/输入类工具借用焦点）。返回是否找到窗口。"""
    return _focus_minecraft_window(wait=wait, maximize=maximize) is not None


def restore_user_window() -> None:
    """借用结束，归还焦点（与 focus_game_window 成对使用）。"""
    _restore_user_foreground()


def _visible_window_title(user32, hwnd) -> "str | None":
    """读可见且非空标题窗口的标题文本（不可见/无标题返回 None）。

    由 _focus_minecraft_window 的枚举回调拆出。
    """
    if not user32.IsWindowVisible(hwnd):
        return None
    length = user32.GetWindowTextLengthW(hwnd)
    if not length:
        return None
    import ctypes
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def _is_mc_window_title(title: str) -> bool:
    """窗口标题是否为 Minecraft（大小写不敏感），由 _focus_minecraft_window 拆出。"""
    return "minecraft" in title.lower()


def _focus_minecraft_window(wait: float = 0.8, maximize: bool = True):
    """把标题含 "Minecraft" 的窗口带到前台，返回其屏幕矩形 (l, t, r, b)。

    全屏截图（PIL ImageGrab）抓的是整个桌面——MC 窗口若不在前台，
    agent 拿到的是 IDE/桌面的图（webserv_stardust 实测）。截图前把
    MC 窗口置前并按其矩形裁剪，才能真正"看到"游戏画面。
    找不到窗口或非 Windows 时返回 None（回退原全屏行为）。
    """
    from . import _user_fg  # 延迟导入：同上
    _remember_user_foreground()
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        found = []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def _cb(hwnd, _lparam):
            try:
                title = _visible_window_title(user32, hwnd)
                if title is not None and _is_mc_window_title(title):
                    rect = wintypes.RECT()
                    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                        if (rect.right - rect.left) > 200 and (rect.bottom - rect.top) > 150:
                            found.append((hwnd, (rect.left, rect.top, rect.right, rect.bottom)))
            except Exception as e:
                logger.debug("_cb 降级忽略 | %s", e)
            return True

        user32.EnumWindows(_cb, 0)
        if not found:
            return None
        hwnd, rect = found[0]
        # Windows 禁止后台进程直接 SetForegroundWindow 抢前台（静默失败，
        # webserv_amber 实测截到的仍是 IDE）。标准规避：先模拟一次 ALT 键
        # 按放，使本进程满足前台锁定检查；若窗口最小化先还原。
        user32.keybd_event(0x12, 0, 0, 0)   # ALT down
        user32.keybd_event(0x12, 0, 2, 0)   # ALT up
        user32.ShowWindow(hwnd, 9)          # SW_RESTORE
        ok = user32.SetForegroundWindow(hwnd)
        if not ok:
            logger.warning("SetForegroundWindow 被系统拒绝，截图可能仍是桌面")
        if maximize:
            user32.ShowWindow(hwnd, 3)      # SW_MAXIMIZE：最大化游戏窗口，截图视野完整
        time.sleep(wait)  # 等窗口切换 + 渲染一帧
        return rect
    except Exception:
        return None



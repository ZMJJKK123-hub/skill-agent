# -*- coding: utf-8 -*-
"""游戏画面视觉验证循环（由 input.py 拆出）。

类职责：verify_visual_loop——截图→视觉分析→不满足重试的闭环；
焦点借用由 input 的 _borrow_game_focus 提供。
生命周期：handlers 注册为 verify_visual_loop 工具。
"""
from ..vision import run_analyze_image  # 视觉分析（tools.vision 包）
from .input import _borrow_game_focus  # 截图前焦点借用

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

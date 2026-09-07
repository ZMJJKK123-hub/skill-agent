# -*- coding: utf-8 -*-
"""游戏交互包：RCON 命令 + 进程内 UI 桥 + 键盘输入。
由单文件 game.py 拆分；再导出保持兼容。
"""
from .rcon import _base_dir, _recv_exact, _rcon_packet, send_game_command  # noqa: F401
from .input import (bridge_command, game_input, press_key, press_keys,  # noqa: F401
                    type_text, verify_visual_loop, wait_for_log,
                    wait_for_screen, _vk_code)

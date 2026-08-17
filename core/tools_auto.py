# -*- coding: utf-8 -*-
"""Auto-mode runtime toggle."""
from . import config


def set_auto_mode(enabled: bool) -> str:
    """Enable/disable auto mode for the current agent process."""
    config.AUTO_MODE = bool(enabled)
    return f"Auto mode {'enabled' if config.AUTO_MODE else 'disabled'} (current process)"

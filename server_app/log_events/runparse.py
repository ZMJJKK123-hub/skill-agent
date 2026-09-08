# -*- coding: utf-8 -*-
"""run.log 行协议解析：[reply]/[思考+]/[tool]/[tool-result]/[todo] → 事件。
由 log_events.py 原样迁出。
"""
import json
import re
import time
from typing import Optional

from .runparse_prims import _after, _ev, _split_tag  # 解析原语（machine 共用）


# ---------- run.log 事件解析 ----------

from .runparse_machine import _RunParser  # 行解析状态机（拆分模块）


# ---------- run.log 事件解析 ----------



def _parse_run_block(text: str, pending: dict | None = None, flush_at_eof: bool = True) -> tuple[list[dict], dict | None]:
    """把 run.log 的一段新增文本解析为事件列表（状态机类 _RunParser）。

    Args:
        text: 新增文本段。
        pending: 上次增量留下的未完回复（reply_buf 续接）。
        flush_at_eof: 全量读取 True（段末强制收尾回复）；增量 False。
    Returns:
        (事件列表, 续接 pending 或 None)。
    """
    from .runparse_machine import _RunParser  # 延迟导入（辅助原语在 machine 内，避免环）
    parser = _RunParser(pending)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        i += parser.feed(lines, i)
    if flush_at_eof:
        parser.flush_reply()
        return parser.events, None
    return parser.events, parser.to_pending()

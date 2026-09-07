# -*- coding: utf-8 -*-
"""超大工具结果的落盘外溢（infrastructure 层；dsh spill-policy 移植）。

超过阈值的纯文本工具结果写入 .spill/ 文件，模型只看到
前后预览 + 定位符，防止单条输出撑爆上下文。
"""
from __future__ import annotations

import os
from pathlib import Path

from .logging_.logger import get_logger

logger = get_logger("spill")

#: 豁免名单：这些工具的结果不得 spill——
#: read_file（防 读→spill→再读 死循环）；GameTest/构建类（出口闸依赖
#: 输出中的通过标记，预览截断会让闸失明、无限打回）；load_skill
#: （技能正文被截后 move_skills_to_end 会把残片当全文滚动）。
SPILL_EXEMPT = frozenset({
    "read_file", "load_skill", "run_test_gametest", "run_mod_test_cycle",
    "run_game_test_server", "parse_gametest_results",
    "read_game_test_log", "build_mod_jar_forge",
})


def maybe_spill(name: str, output: str, max_chars: int) -> str:
    """超大结果外溢到 .spill/，返回预览 + 文件定位符。

    Args:
        name: 工具名（豁免名单判定）。
        output: 原始输出文本。
        max_chars: 内联阈值（超过才外溢）。
    Returns:
        外溢时为预览文本；否则原样返回。写盘失败降级为原样返回（记日志）。
    """
    if name in SPILL_EXEMPT:
        return output
    if not isinstance(output, str) or len(output) <= max_chars:
        return output
    try:
        spill_dir = Path.cwd() / ".spill"
        spill_dir.mkdir(exist_ok=True)
        path = spill_dir / f"{name}-{os.urandom(4).hex()}.txt"
        path.write_text(output, encoding="utf-8")
        preview = output[:1200] + "\n...[truncated]...\n" + output[-1200:]
        return (f"[spilled] Full tool output ({len(output)} chars) saved to {path}.\n"
                f"Preview:\n{preview}")
    except OSError as e:
        logger.warning("spill 写盘失败，原样内联 | tool=%s | err=%s", name, e)
        return output

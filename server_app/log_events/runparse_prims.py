# -*- coding: utf-8 -*-
"""run.log 解析原语（由 runparse.py 拆出）：事件构造与前缀/标签切分。"""
import re
import time


def _ev(e_type: str, content: str, seq: int, **extra) -> dict:
    ev = {
        "id": f"ev-{seq}",
        "ts": time.time(),
        "type": e_type,
        "source": "run",
        # 调试需要：事件正文全量保留，不截断（便于使用者查看完整输出）
        "content": content,
    }
    ev.update(extra)
    return ev


def _after(text: str, prefix: str) -> str:
    return text[len(prefix):].strip()


def _split_tag(line: str) -> tuple[str, str]:
    """解析 '[teammate:bash] 输出...' → ('bash', '] 输出...')"""
    end = line.index("]")
    return line[len("["):end], line[end:]

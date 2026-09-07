# -*- coding: utf-8 -*-
"""运行时槽位（runtime slot）替换（services/loop 层）。

旧实现 _replace_runtime_slot 的类型化版本：临时上下文（监管提醒/
后台通知/队友汇报/完成闸提醒等）以固定标签前缀注入，新一轮注入
同标签时替换旧块，防止过期上下文累积干扰模型。
"""
from __future__ import annotations

from ...domain.messages import Message, UserMessage


def replace_runtime_slot(messages: list[Message], tag: str, content: str) -> None:
    """移除旧的 <tag> 前缀 user 消息后追加最新块（原地变更列表）。

    Args:
        messages: 当前消息列表（原地修改）。
        tag: 标签名（如 "supervisor-advice"；匹配规则为内容以 "<tag" 开头）。
        content: 最新注入文本（通常自带 <tag>...</tag> 包裹）。
    """
    prefix = f"<{tag}"
    kept = [m for m in messages
            if not (isinstance(m, UserMessage)
                    and m.content.lstrip().startswith(prefix))]
    messages[:] = kept
    messages.append(UserMessage(content=content))

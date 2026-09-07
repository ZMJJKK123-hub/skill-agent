# -*- coding: utf-8 -*-
"""会话存储抽象（interfaces 层）。

覆盖旧 core/conversation.py 的全部职责：对话历史、断点
（暂停/继续）、运行中插话队列。文件实现见
infrastructure/session_files.py；单测可注入内存实现。
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from ..domain.messages import Message, UserMessage


@runtime_checkable
class SessionStore(Protocol):
    """.chat/ 目录下三类文件的读写契约。

    类职责：唯一拥有会话文件格式知识的地方——
        conversation.jsonl  对话历史（user/assistant 对，供跨轮记忆）
        working.jsonl       当前轮完整断点（含工具中间态，暂停恢复用）
        pending.jsonl       运行中用户插话队列（daemon 每轮消费一条）
    方法调用逻辑：enqueue（server 侧进程外调用）→ drain_pending_one
    （agent 每轮开头）→ append_user/assistant（消费时落历史）→
    save_checkpoint（每轮开头）→ clear_checkpoint（正常完成后）。
    """

    # ---------- 对话历史 ----------

    def load_recent_history(self, max_rounds: int = 20) -> list[Message]:
        """读取最近 N 轮历史（user/assistant 消息对）。

        Returns:
            类型化消息列表；无历史返回空列表（绝不抛 IO 异常）。
        """
        ...

    def append_user(self, content: str, images: Optional[list[str]] = None) -> None:
        """追加用户消息（含图片附件名列表）。"""
        ...

    def append_assistant(self, content: str) -> None:
        """追加助手回复（只存文本，工具细节不进历史）。"""
        ...

    def reset_history(self) -> None:
        """清空对话历史（会话重置时调用）。"""
        ...

    # ---------- 断点 ----------

    def save_checkpoint(self, messages: list[Message]) -> None:
        """把当前完整消息列表落盘为断点（每轮循环开头调用）。"""
        ...

    def load_checkpoint(self) -> Optional[list[Message]]:
        """加载断点；无断点/文件损坏返回 None。"""
        ...

    def clear_checkpoint(self) -> None:
        """删除断点文件（正常完成一轮后调用）。"""
        ...

    # ---------- 插话队列 ----------

    def enqueue_pending(self, content: str,
                        images: Optional[list[str]] = None) -> None:
        """排入一条用户插话（只进队列，不写历史——历史由消费时落盘）。"""
        ...

    def drain_pending_one(self) -> list[UserMessage]:
        """出队最早一条插话（空列表表示无）；剩余留在队列。"""
        ...

    def drain_pending_all(self) -> list[UserMessage]:
        """一次性出队全部插话并清空队列（非 daemon 直跑模式的中途注入用）。"""
        ...

    def pending_count(self) -> int:
        """返回队列剩余条数（server 判断是否自动续跑）。"""
        ...

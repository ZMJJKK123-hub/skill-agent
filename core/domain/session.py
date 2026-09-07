# -*- coding: utf-8 -*-
"""会话域类型：运行模式 / 沙箱模式 / 会话上下文（domain 层，零 IO）。

按 agent.md Rule 2（强类型）：原先散落为裸字符串的 DSH_MODE /
DSH_SANDBOX_MODE 在引擎内部一律使用此处的枚举；裸字符串只允许在
infrastructure/config.py 读取环境变量时出现一次。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    """运行模式（对应环境变量 DSH_MODE）。

    MOD：MOD 制作模式——监管线程/GameTest 出口闸/收尾构建全部启用。
    CHAT：只读咨询模式——跳过一切 MOD 专属机制，纯文本回复即出口。
    """

    CHAT = "chat"
    MOD = "mod"

    @classmethod
    def parse(cls, raw: str | None) -> "Mode":
        """把环境变量字符串安全解析为 Mode。

        Args:
            raw: 环境变量原文（None/空 → CHAT 默认）。
        Returns:
            Mode 枚举值。
        Raises:
            ValueError: 值不是 chat/mod 时（fail loud，不静默回退）。
        """
        if not raw:
            return cls.CHAT
        try:
            return cls(raw.strip().lower())
        except ValueError as e:
            raise ValueError(f"未知运行模式 DSH_MODE={raw!r}（仅支持 chat/mod）") from e


class SandboxMode(str, Enum):
    """会话级沙箱模式（对应 DSH_SANDBOX_MODE）。"""

    FULL_ACCESS = "full-access"
    WORKSPACE_WRITE = "workspace-write"
    READ_ONLY = "read-only"


@dataclass
class SessionContext:
    """一次引擎运行的身份与环境的不可变快照。

    属性：
        session_root: str — 会话根目录（data/sessions/<id>/），
            .chat/ 断点与队列的所在处；空串表示无会话根（进程级使用）。
        mode: Mode — chat/mod 运行模式。
        sandbox: SandboxMode — 沙箱模式（写工具的放行/拒绝依据）。
        trace_id: str — 结构化日志贯穿标识（默认取 session_root 的名字），
            所有日志与异常上下文都携带它（Rule 2.5）。

    生命周期：bootstrap 从 Settings 一次性构建，整个 loop 期间只读。
    """

    session_root: str = ""
    mode: Mode = Mode.CHAT
    sandbox: SandboxMode = SandboxMode.FULL_ACCESS
    trace_id: str = ""

    def __post_init__(self) -> None:
        """派生默认 trace_id：未显式给定时取 session_root 尾名。"""
        if not self.trace_id:
            tail = self.session_root.rstrip("/\\").split("/")[-1].split("\\")[-1]
            self.trace_id = tail or "inline"

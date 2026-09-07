# -*- coding: utf-8 -*-
"""主循环的外围协作端口（services/loop 层）。

把监管线程 / 队友 / 后台任务 / 协议注入等外围系统抽象为窄接口，
runner 只依赖这些端口——旧单例（supervisor_manager 等）由
bootstrap 适配接入；单测用空实现。
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ...domain.messages import Message


@runtime_checkable
class SupervisorPort(Protocol):
    """监管线程端口（mod 模式启动；信箱每轮排空）。

    方法协作：start（循环启动）→ notify_round/drain_advice（每轮）→
    stop（收尾）；实现方保证线程安全。
    """

    def start(self) -> None:
        """启动监管线程（幂等）。"""
        ...

    def stop(self) -> None:
        """停止监管线程（收尾防泄漏）。"""
        ...

    def drain_advice(self) -> list[dict]:
        """取走信箱全部建议；返回 [{"type","content"}, ...]（读后即清）。"""
        ...

    def notify_round(self) -> None:
        """轮次计数；每 5 轮触发一次监管分析。"""
        ...


@runtime_checkable
class TeammatesPort(Protocol):
    """队友系统端口（leader 视角）。"""

    def read_leader_inbox(self) -> list[dict]:
        """取走 leader 收件箱；返回 [{"from","content"}, ...]（读后即清）。"""
        ...

    def working_names(self) -> list[str]:
        """仍在 working 状态的队友名（退出闸依据）。"""
        ...


@runtime_checkable
class BackgroundPort(Protocol):
    """后台任务通知端口。"""

    def drain_notifications(self) -> list:
        """取走全部已完成后台任务的通知（读后即清）。"""
        ...

    def format_results(self, notifications: list) -> str:
        """把通知列表渲染为 <background-results> 注入文本。"""
        ...


@runtime_checkable
class ProtocolPort(Protocol):
    """团队协议（审批/关机）注入端口。"""

    def inject_pending(self, agent_id: str, messages: list[Message]) -> None:
        """把 <pending-requests> 协议块注入消息列表（原地变更）。

        Args:
            agent_id: 协议视角身份（主循环恒 "leader"）。
            messages: 当前消息列表（实现负责替换旧块并追加新块）。
        """
        ...

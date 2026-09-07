# -*- coding: utf-8 -*-
"""Turn/Step 状态机（services/loop 层；dsh turn/step 边界的移植）。

一个 turn（一次用户请求）= 多个 step（模型请求 + 工具执行 + …）。
两条硬规则（dsh 观察）：
    1. concludesTurn —— 工具结果可以不经下一次模型调用直接结束 turn；
    2. max-tokens 粘滞 —— 一旦某 step 撞 max-tokens，后续正常 step
       不会把 turn 结局降级回 completed。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..session_log import SessionLog


@dataclass
class TurnEndReason:
    """turn 结局。

    属性：
        kind: str — completed | max-tokens | error | aborted | concluded。
        error: Optional[str] — error 结局时的原因文本。
    """

    kind: str
    error: Optional[str] = None


class TurnStepMachine:
    """跟踪当前 turn/step 并在边界处写事件日志。

    类职责：turn/step 计数与结局判定；所有转移都落到 SessionLog。
    实例属性：log（事件日志）、turn/step（计数）、turn_end（结局）、
    _finished（一次性守卫）。
    生命周期：每次 run() 创建；start_turn → (start_step/end_step)* →
    complete_turn / conclude_turn。
    """

    def __init__(self, log: SessionLog | None = None) -> None:
        """输入：事件日志（可空）。返回：无。职责：初始空闲态。"""
        self.log = log
        self.turn = 0
        self.step = 0
        self.turn_end: Optional[TurnEndReason] = None
        self._finished = False

    def start_turn(self, user_message: str | None = None) -> None:
        """开启新 turn（计数清零，写 turn/start 事件）。"""
        self.turn += 1
        self.step = 0
        self.turn_end = None
        self._finished = False
        if self.log:
            self.log.append("turn/start", {"turn": self.turn, "user": user_message})

    def start_step(self) -> None:
        """开启新 step（模型请求前调用）。"""
        self.step += 1
        if self.log:
            self.log.append("step/start", {"turn": self.turn, "step": self.step})

    def end_step(self, reason: str = "completed") -> None:
        """结束当前 step（工具批执行完/纯文本轮结束时调用）。"""
        if self.log:
            self.log.append("step/end",
                            {"turn": self.turn, "step": self.step, "reason": reason})

    def record_max_tokens(self) -> None:
        """登记 max-tokens 结局（粘滞：不因后续正常 step 降级）。"""
        if self.turn_end is None or self.turn_end.kind != "max-tokens":
            self.turn_end = TurnEndReason(kind="max-tokens")
            if self.log:
                self.log.append("turn/max-tokens",
                                {"turn": self.turn, "step": self.step})

    def conclude_turn(self, reason: str = "concluded") -> None:
        """工具直接结束 turn（不经下一次模型调用；一次性守卫）。"""
        if not self._finished:
            self.turn_end = TurnEndReason(kind=reason)
            self._finished = True
            if self.log:
                self.log.append("turn/end", {"turn": self.turn, "reason": reason})

    def complete_turn(self) -> None:
        """正常完成 turn（max-tokens 结局优先保留；一次性守卫）。"""
        if not self._finished:
            self.turn_end = self.turn_end or TurnEndReason(kind="completed")
            self._finished = True
            if self.log:
                self.log.append("turn/end",
                                {"turn": self.turn, "reason": self.turn_end.kind})

    @property
    def active(self) -> bool:
        """输入：无。返回：turn 是否仍在进行。"""
        return self.turn > 0 and not self._finished

    def __repr__(self) -> str:
        """输入：无。返回：调试摘要。"""
        return (f"<TurnStepMachine turn={self.turn} step={self.step} "
                f"finished={self._finished}>")

# -*- coding: utf-8 -*-
"""Turn/step state machine (port of dsh agent-loop turn/step boundaries).

DSH separates a *turn* (one user request) into *steps* (model request + tool
execution + model request ...). This module tracks boundaries, records them in
the SessionLog, and enforces the two important rules we observed in dsh:

- `concludesTurn`: a tool result can end the turn without another model call.
- `max-tokens` is sticky: once a step hits max-tokens, later normal steps do
  not downgrade the turn outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .session_log import SessionLog


@dataclass
class TurnEndReason:
    kind: str  # completed | max-tokens | error | aborted | concluded
    error: Optional[str] = None


class TurnStepMachine:
    """Tracks current turn/step and emits session log events at boundaries."""

    def __init__(self, log: SessionLog | None = None) -> None:
        self.log = log
        self.turn = 0
        self.step = 0
        self.turn_end: Optional[TurnEndReason] = None
        self._finished = False

    def start_turn(self, user_message: str | None = None) -> None:
        self.turn += 1
        self.step = 0
        self.turn_end = None
        self._finished = False
        if self.log:
            self.log.append("turn/start", {"turn": self.turn, "user": user_message})

    def start_step(self) -> None:
        self.step += 1
        if self.log:
            self.log.append("step/start", {"turn": self.turn, "step": self.step})

    def end_step(self, reason: str = "completed") -> None:
        if self.log:
            self.log.append("step/end", {"turn": self.turn, "step": self.step, "reason": reason})

    def record_max_tokens(self) -> None:
        # max-tokens is sticky: once set, later normal steps keep the
        # max-tokens outcome as the turn outcome.
        if self.turn_end is None or self.turn_end.kind != "max-tokens":
            self.turn_end = TurnEndReason(kind="max-tokens")
            if self.log:
                self.log.append("turn/max-tokens", {"turn": self.turn, "step": self.step})

    def conclude_turn(self, reason: str = "concluded") -> None:
        if not self._finished:
            self.turn_end = TurnEndReason(kind=reason)
            self._finished = True
            if self.log:
                self.log.append("turn/end", {"turn": self.turn, "reason": reason})

    def complete_turn(self) -> None:
        if not self._finished:
            self.turn_end = self.turn_end or TurnEndReason(kind="completed")
            self._finished = True
            if self.log:
                self.log.append("turn/end", {"turn": self.turn, "reason": self.turn_end.kind})

    @property
    def active(self) -> bool:
        return self.turn > 0 and not self._finished

    def __repr__(self) -> str:
        return f"<TurnStepMachine turn={self.turn} step={self.step} finished={self._finished}>"
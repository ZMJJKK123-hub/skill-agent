# -*- coding: utf-8 -*-
"""Event-sourced session log + deriveMessages (port of dsh-session core).

DSH keeps every interaction as an append-only event log and derives the
model-facing message list from those events each request. This module is the
first Python equivalent:

- `SessionLog.append(...)` records typed events.
- `SessionLog.derive_messages()` rebuilds the OpenAI messages list:
  user -> role user, assistant -> role assistant (content/tool_calls),
  tool -> role tool with matching tool_call_id.
- `repair_missing_tool_results(...)` fills a missing tool result so the
  assistant(tool_calls) -> tool sequence never breaks (the exact DSH invariant).

This is intentionally transport-independent (no API client). The agent loop can
use it as the durable source of truth while keeping `messages` as a derived view.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionEvent:
    """One immutable event in the session log."""
    seq: int
    type: str  # 'user' | 'assistant' | 'tool' | 'step/start' | 'step/end' | 'turn/start' | 'turn/end' | 'compaction'
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return {"seq": self.seq, "type": self.type, "payload": self.payload, "event_id": self.event_id}


class SessionLog:
    """Append-only session event log with derive_messages()."""

    def __init__(self) -> None:
        self.events: list[SessionEvent] = []
        self._seq = 0

    def append(self, type_: str, payload: dict[str, Any] | None = None) -> SessionEvent:
        self._seq += 1
        ev = SessionEvent(seq=self._seq, type=type_, payload=payload or {})
        self.events.append(ev)
        return ev

    # ---- event helpers -------------------------------------------------

    def add_user(self, content: str, source: str = "user") -> SessionEvent:
        return self.append("user", {"content": content, "source": source})

    def add_assistant(self, content: str | None = None,
                      tool_calls: list[dict[str, Any]] | None = None,
                      reasoning: str | None = None) -> SessionEvent:
        return self.append("assistant", {
            "content": content, "tool_calls": tool_calls, "reasoning": reasoning,
        })

    def add_tool_result(self, tool_call_id: str, content: str) -> SessionEvent:
        return self.append("tool", {"tool_call_id": tool_call_id, "content": content})

    def add_compaction(self, summary_content: str, start_seq: int, end_seq: int) -> SessionEvent:
        """Record a compaction checkpoint: events [start_seq, end_seq] are replaced
        by a summary user message in derived views (DSH surface replacement)."""
        ev = self.append("compaction", {
            "summary": summary_content,
            "start": int(start_seq),
            "end": int(end_seq),
        })
        return ev

    def _compaction_ranges(self) -> list[dict]:
        ranges = []
        for ev in self.events:
            if ev.type != "compaction":
                continue
            p = ev.payload
            if "start" in p and "end" in p and "summary" in p:
                ranges.append({
                    "start": int(p["start"]),
                    "end": int(p["end"]),
                    "summary": str(p["summary"]),
                })
        return sorted(ranges, key=lambda r: r["start"])

    # ---- derivation ----------------------------------------------------

    def derive_messages(self) -> list[dict[str, Any]]:
        """Rebuild OpenAI-format messages from events.

        - assistant events with tool_calls produce assistant messages.
        - tool events are attached with their tool_call_id (just like OpenAI).
        - compaction events replace a contiguous event range with one summary
          user message (DSH surface replacement), so derived history is compacted
          without losing the checkpoint.
        """
        ranges = self._compaction_ranges()
        ri = 0
        inside_range = False
        messages: list[dict[str, Any]] = []
        for ev in self.events:
            # Advance past ranges fully left of this event.
            while ri < len(ranges) and ev.seq > ranges[ri]["end"]:
                ri += 1
                inside_range = False
            if ri < len(ranges) and ranges[ri]["start"] <= ev.seq <= ranges[ri]["end"]:
                if not inside_range:
                    messages.append({"role": "user", "content": ranges[ri]["summary"]})
                    inside_range = True
                continue  # skip replaced original events
            inside_range = False

            if ev.type == "user":
                messages.append({"role": "user", "content": ev.payload.get("content", "")})
            elif ev.type == "assistant":
                msg: dict[str, Any] = {"role": "assistant"}
                content = ev.payload.get("content")
                tool_calls = ev.payload.get("tool_calls")
                if content is not None:
                    msg["content"] = content
                else:
                    msg["content"] = None if tool_calls else ""
                if tool_calls:
                    msg["tool_calls"] = tool_calls
                if ev.payload.get("reasoning"):
                    msg["reasoning_content"] = ev.payload["reasoning"]
                messages.append(msg)
            elif ev.type == "tool":
                messages.append({
                    "role": "tool",
                    "tool_call_id": ev.payload.get("tool_call_id", ""),
                    "content": ev.payload.get("content", ""),
                })
        return messages

    # ---- persistence ---------------------------------------------------

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(ev.to_dict(), ensure_ascii=False) for ev in self.events)

    @classmethod
    def from_jsonl(cls, text: str) -> "SessionLog":
        log = cls()
        for line in text.splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            log._seq = max(log._seq, int(data.get("seq", 0)))
            log.events.append(SessionEvent(
                seq=int(data["seq"]), type=data["type"],
                payload=data.get("payload", {}), event_id=data.get("event_id"),
            ))
        return log

    @classmethod
    def from_messages(cls, messages: list[dict[str, Any]]) -> "SessionLog":
        """Build a SessionLog from an existing OpenAI-format messages list."""
        log = cls()
        for m in messages:
            role = m.get("role")
            if role == "user":
                log.add_user(str(m.get("content", "")), source="messages")
            elif role == "assistant":
                log.add_assistant(
                    content=m.get("content"),
                    tool_calls=m.get("tool_calls"),
                    reasoning=m.get("reasoning_content"),
                )
            elif role == "tool":
                log.add_tool_result(str(m.get("tool_call_id", "")), str(m.get("content", "")))
        return log

    def __repr__(self) -> str:
        return f"<SessionLog events={len(self.events)} seq={self._seq}>"


def repair_missing_tool_results(log: SessionLog, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """DSH crash-recovery repair: ensure every assistant tool_call has a following tool result.

    If an assistant message declares tool_calls but the matching tool result is missing,
    insert a synthetic tool result so the OpenAI protocol stays valid.
    """
    tool_call_ids = set()
    for idx, msg in enumerate(messages):
        calls = msg.get("tool_calls") or []
        for tc in calls:
            tool_call_ids.add(tc.get("id", ""))
    present_ids = {
        m.get("tool_call_id", "") for m in messages if m.get("role") == "tool"
    }
    inserted = 0
    out: list[dict[str, Any]] = []
    for msg in messages:
        out.append(msg)
        calls = msg.get("tool_calls") or []
        if calls:
            for tc in calls:
                cid = tc.get("id", "")
                if cid in tool_call_ids and cid not in present_ids:
                    out.append({
                        "role": "tool",
                        "tool_call_id": cid,
                        "content": "[repaired] Missing tool result from crash/compaction. Check logs for actual output.",
                    })
                    log.add_tool_result(cid, "[repaired] Missing tool result from crash/compaction.")
                    inserted += 1
                    present_ids.add(cid)
    return out
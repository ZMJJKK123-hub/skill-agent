# -*- coding: utf-8 -*-
"""事件源会话日志（services 层；dsh session 核心的移植与类型化收编）。

事实源模型：一切交互先记为 append-only 事件（SessionEvent），
面向模型的消息列表只是事件的派生视图——崩溃后可重放、可修复。
payload dict 是磁盘 JSONL 的序列化格式（文件契约），不属于
"模块间裸字典"（Rule 2 禁令的豁免边界：落盘 wire format）。
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..domain.messages import (AssistantMessage, Message, ToolResultMessage,
                               UserMessage, transport_messages, typed_messages)
from ..infrastructure.logging_.logger import get_logger

logger = get_logger("session_log")

#: 事件日志落盘路径（相对进程 cwd，即会话工作区）。
EVENT_LOG_PATH = Path(".chat") / "session_events.jsonl"


@dataclass
class SessionEvent:
    """一条不可变事件。

    属性：
        seq: int — 单调递增序号（压缩区间锚点）。
        type: str — user/assistant/tool/turn/start/end/step/compaction。
        payload: dict — 序列化负载（磁盘 wire format）。
        event_id: str — 全局唯一 id（跨进程排障用）。
    """

    seq: int
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        """输入：无。返回：JSONL 行的 dict 形态。"""
        return {"seq": self.seq, "type": self.type,
                "payload": self.payload, "event_id": self.event_id}


class SessionLog:
    """append-only 事件日志 + 消息派生。

    类职责：记录事件；derive_messages() 重建模型消息列表；
    compaction 事件按区间替换为摘要（表面替换，不丢检查点）。
    实例属性：events（有序事件表）、_seq（序号分配器）。
    生命周期：每进程一个；restore() 从磁盘重建。
    """

    def __init__(self) -> None:
        """输入：无。返回：无。职责：初始化空事件表。"""
        self.events: list[SessionEvent] = []
        self._seq = 0

    def append(self, type_: str, payload: dict | None = None) -> SessionEvent:
        """输入：事件类型 + 负载。返回：新事件。职责：追加并分配序号。"""
        self._seq += 1
        ev = SessionEvent(seq=self._seq, type=type_, payload=payload or {})
        self.events.append(ev)
        return ev

    def add_user(self, content: str, source: str = "user") -> SessionEvent:
        """记 user 事件（source 标记来源：user/messages/...）。"""
        return self.append("user", {"content": content, "source": source})

    def add_assistant(self, content: str | None = None,
                      tool_calls: list[dict] | None = None,
                      reasoning: str | None = None) -> SessionEvent:
        """记 assistant 事件（content/tool_calls/reasoning 三元）。"""
        return self.append("assistant", {
            "content": content, "tool_calls": tool_calls, "reasoning": reasoning})

    def add_tool_result(self, tool_call_id: str, content: str) -> SessionEvent:
        """记 tool 结果事件（与 assistant.tool_calls 的 id 配对）。"""
        return self.append("tool", {"tool_call_id": tool_call_id, "content": content})

    def add_compaction(self, summary: str, start_seq: int, end_seq: int) -> SessionEvent:
        """记压缩检查点：区间 [start, end] 的事件在派生视图中被摘要替换。"""
        return self.append("compaction", {
            "summary": summary, "start": int(start_seq), "end": int(end_seq)})

    def _compaction_ranges(self) -> list[dict]:
        """输入：无。返回：有序压缩区间列表（start 升序）。"""
        ranges = []
        for ev in self.events:
            if ev.type != "compaction":
                continue
            p = ev.payload
            if {"start", "end", "summary"} <= p.keys():
                ranges.append({"start": int(p["start"]), "end": int(p["end"]),
                               "summary": str(p["summary"])})
        return sorted(ranges, key=lambda r: r["start"])

    def derive_messages(self) -> list[Message]:
        """从事件重建类型化消息列表（压缩区间→单条摘要 user 消息）。"""
        ranges = self._compaction_ranges()
        ri, inside = 0, False
        messages: list[Message] = []
        for ev in self.events:
            while ri < len(ranges) and ev.seq > ranges[ri]["end"]:
                ri += 1
                inside = False
            if ri < len(ranges) and ranges[ri]["start"] <= ev.seq <= ranges[ri]["end"]:
                if not inside:
                    messages.append(UserMessage(content=ranges[ri]["summary"]))
                    inside = True
                continue
            inside = False
            messages.extend(self._event_to_messages(ev))
        return messages

    @staticmethod
    def _event_to_messages(ev: SessionEvent) -> list[Message]:
        """输入：单条事件。返回：对应的消息列表（0 或 1 条）。"""
        if ev.type == "user":
            return [UserMessage(content=str(ev.payload.get("content", "")))]
        if ev.type == "assistant":
            calls = ev.payload.get("tool_calls")
            specs = None
            if calls:
                from ..domain.messages import ToolCallSpec
                specs = [ToolCallSpec.from_dict(tc) for tc in calls]
            return [AssistantMessage(content=ev.payload.get("content"),
                                     tool_calls=specs,
                                     reasoning=ev.payload.get("reasoning"))]
        if ev.type == "tool":
            return [ToolResultMessage(
                tool_call_id=str(ev.payload.get("tool_call_id", "")),
                content=str(ev.payload.get("content", "")))]
        return []

    # ---------- 持久化 ----------

    def to_jsonl(self) -> str:
        """输入：无。返回：全部事件的 JSONL 文本。"""
        return "\n".join(json.dumps(ev.to_dict(), ensure_ascii=False)
                         for ev in self.events)

    @classmethod
    def from_jsonl(cls, text: str) -> "SessionLog":
        """从 JSONL 文本重建（坏行抛 JSONDecodeError，由调用方降级）。"""
        log = cls()
        for line in text.splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            log._seq = max(log._seq, int(data.get("seq", 0)))
            log.events.append(SessionEvent(
                seq=int(data["seq"]), type=data["type"],
                payload=data.get("payload", {}), event_id=data.get("event_id") or uuid.uuid4().hex))
        return log

    def __repr__(self) -> str:
        """输入：无。返回：调试摘要。"""
        return f"<SessionLog events={len(self.events)} seq={self._seq}>"


def sync_messages(log: SessionLog, messages: list[Message],
                  synced_count: int) -> int:
    """把 messages[synced_count:] 增量同步进事件源；返回新的已同步数。"""
    try:
        for m in messages[synced_count:]:
            if isinstance(m, UserMessage):
                log.add_user(m.content, source="messages")
            elif isinstance(m, AssistantMessage):
                log.add_assistant(content=m.content,
                                  tool_calls=[tc.to_dict() for tc in m.tool_calls] if m.tool_calls else None,
                                  reasoning=m.reasoning)
            elif isinstance(m, ToolResultMessage):
                log.add_tool_result(m.tool_call_id, m.content)
            synced_count += 1
    except Exception as e:
        logger.warning("sync messages to log failed: %s", e)
    return synced_count


def repair_missing_tool_results(log: SessionLog,
                                messages: list[Message]) -> list[Message]:
    """崩溃恢复修复：每个 assistant tool_call 缺结果时补一条合成结果。

    保证 assistant(tool_calls) → tool 序列永远完整（OpenAI 协议硬约束）。
    """
    ids_with_calls = {tc.call_id for m in messages
                      if isinstance(m, AssistantMessage)
                      for tc in (m.tool_calls or [])}
    present = {m.tool_call_id for m in messages
               if isinstance(m, ToolResultMessage)}
    out: list[Message] = []
    inserted = 0
    for m in messages:
        out.append(m)
        if isinstance(m, AssistantMessage) and m.tool_calls:
            for tc in m.tool_calls:
                if tc.call_id in ids_with_calls and tc.call_id not in present:
                    out.append(ToolResultMessage(
                        tool_call_id=tc.call_id,
                        content=("[repaired] Missing tool result from "
                                 "crash/compaction.")))
                    log.add_tool_result(tc.call_id, "[repaired] Missing tool result from crash/compaction.")
                    inserted += 1
                    present.add(tc.call_id)
    if inserted:
        logger.info("repaired %d missing tool results", inserted)
    return out


def persist(log: SessionLog) -> None:
    """把事件日志覆写到 .chat/session_events.jsonl（重放/排障用）。"""
    try:
        EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        EVENT_LOG_PATH.write_text(log.to_jsonl(), encoding="utf-8")
        logger.info("SessionLog saved: %s events=%d", EVENT_LOG_PATH, len(log.events))
    except OSError as e:
        logger.warning("save session log failed: %s", e)


def restore() -> Optional[SessionLog]:
    """从磁盘恢复事件日志；不存在/损坏返回 None（调用方降级为空历史）。"""
    if not EVENT_LOG_PATH.exists():
        return None
    try:
        return SessionLog.from_jsonl(EVENT_LOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.warning("SessionLog 恢复失败: %s", e)
        return None

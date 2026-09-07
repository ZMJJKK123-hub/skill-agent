# -*- coding: utf-8 -*-
"""流式事件与轮报告 DTO（domain 层，零 IO）。

职责：定义模型流式输出的增量形状（ModelClient → 主循环）与
每轮调试快照（RoundReport，落盘 .chat/debug/round_messages.jsonl）。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StreamDelta:
    """模型流式输出的一个增量片段。

    属性：
        content: str — 回复文本增量（空串表示本片段无文本）。
        reasoning: str — 思考文本增量（空串同上）。
        tool_index: int | None — 工具调用片段的序号（同一调用分多片到达）。
        tool_call_id: str — 该工具调用的 id（首片携带，后续为空串）。
        tool_name: str — 工具名增量（通常首片完整给出）。
        tool_args: str — 参数 JSON 字符串增量。
        finish_reason: str | None — 结束原因（stop/tool_calls/length），
            只在最后一个片段携带。

    生命周期：由 ModelClient 适配器从 SDK chunk 归一化产出，
    model_call 服务负责聚合为完整 AssistantMessage。
    """

    content: str = ""
    reasoning: str = ""
    tool_index: int | None = None
    tool_call_id: str = ""
    tool_name: str = ""
    tool_args: str = ""
    finish_reason: str | None = None

    @property
    def has_payload(self) -> bool:
        """输入：无。返回：本片段是否携带任何有效载荷（过滤空 chunk）。"""
        return bool(self.content or self.reasoning or self.tool_index is not None
                    or self.finish_reason)


@dataclass
class RoundReport:
    """单轮调试快照（每轮循环末尾落盘，供事后排障）。

    属性：
        round_idx: int — 轮号（从 1 起）。
        message_count: int — 本轮结束时消息总数。
        tool_counts: dict[str, int] — 本轮各工具调用次数。
        notes: list[str] — 附注（触发的守卫/闸等关键事件）。
    """

    round_idx: int
    message_count: int = 0
    tool_counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """输入：无。返回：JSON 可序列化 dict（debug 快照落盘格式）。"""
        return {"round": self.round_idx, "messages": self.message_count,
                "tools": self.tool_counts, "notes": list(self.notes)}

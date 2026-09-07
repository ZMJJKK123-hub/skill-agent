# -*- coding: utf-8 -*-
"""消息 DTO：引擎内部唯一的对话消息类型（domain 层，零 IO）。

按 agent.md Rule 2（禁裸字典）：主循环/服务层之间只传本模块的类型；
OpenAI SDK 字典格式（"transport 格式"）只允许出现在两个边界——
infrastructure/openai_client.py（发给模型）与 SessionStore/SessionLog
（落盘序列化）。转换函数集中在此，保证单一事实来源。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass
class ToolCallSpec:
    """assistant 消息里的一次工具调用请求。

    属性：
        call_id: str — OpenAI 协议的 tool_call id（与 tool 结果配对）。
        name: str — 工具名。
        arguments: str — 原始 JSON 参数字符串（不解析，防 flash 半截 JSON）。
    """

    call_id: str
    name: str
    arguments: str

    def to_dict(self) -> dict:
        """输入：无。返回：OpenAI tool_calls 元素的 transport dict。"""
        return {
            "id": self.call_id,
            "type": "function",
            "function": {"name": self.name, "arguments": self.arguments},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ToolCallSpec":
        """输入：transport dict。返回：ToolCallSpec。职责：字段展平+容缺省。"""
        fn = d.get("function", {}) or {}
        return cls(call_id=str(d.get("id", "")), name=str(fn.get("name", "")),
                   arguments=str(fn.get("arguments", "") or ""))


@dataclass
class UserMessage:
    """用户消息。

    属性：
        content: str — 文本内容。
        images: list[str] | None — 图片附件文件名（.chat/uploads 下），
            仅在模型调用边界展开为多模态片段（见 openai_client）。
    """

    content: str
    images: list[str] | None = None

    @property
    def role(self) -> str:
        """消息角色名（序列化与判定统一入口）。"""
        return "user"

    def to_dict(self) -> dict:
        """输入：无。返回：transport dict（images 仅 user 携带）。"""
        d: dict = {"role": "user", "content": self.content}
        if self.images:
            d["images"] = list(self.images)
        return d


@dataclass
class AssistantMessage:
    """模型回复（可含思考与工具调用）。

    属性：
        content: str | None — 文本回复（纯工具调用轮可为 None）。
        tool_calls: list[ToolCallSpec] | None — 本轮请求的工具调用。
        reasoning: str | None — 思考过程（不进模型上下文，仅供日志/转发）。
    """

    content: str | None = None
    tool_calls: list[ToolCallSpec] | None = None
    reasoning: str | None = None

    @property
    def role(self) -> str:
        """消息角色名。"""
        return "assistant"

    def to_dict(self) -> dict:
        """输入：无。返回：transport dict（与 OpenAI 协议字段对齐）。"""
        d: dict = {"role": "assistant", "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.reasoning:
            d["reasoning_content"] = self.reasoning
        return d


@dataclass
class ToolResultMessage:
    """一次工具调用的执行结果（回填给模型）。"""

    tool_call_id: str
    content: str

    @property
    def role(self) -> str:
        """消息角色名。"""
        return "tool"

    def to_dict(self) -> dict:
        """输入：无。返回：transport dict。"""
        return {"role": "tool", "tool_call_id": self.tool_call_id,
                "content": self.content}


#: 三种消息的联合类型——"一条消息"在引擎内的唯一形态。
Message = Union[UserMessage, AssistantMessage, ToolResultMessage]


def from_transport(d: dict) -> Message:
    """transport dict → 类型化消息。

    Args:
        d: OpenAI/落盘格式的单条消息 dict。
    Returns:
        UserMessage / AssistantMessage / ToolResultMessage 之一。
    Raises:
        ValueError: role 缺失或未知（数据损坏必须 fail loud）。
    """
    role = d.get("role")
    if role == "user":
        return UserMessage(content=str(d.get("content", "")),
                           images=d.get("images"))
    if role == "assistant":
        calls = d.get("tool_calls")
        return AssistantMessage(
            content=d.get("content"),
            tool_calls=[ToolCallSpec.from_dict(tc) for tc in calls] if calls else None,
            reasoning=d.get("reasoning_content"),
        )
    if role == "tool":
        return ToolResultMessage(tool_call_id=str(d.get("tool_call_id", "")),
                                 content=str(d.get("content", "")))
    raise ValueError(f"未知消息 role={role!r}（transport 数据损坏）")


def typed_messages(items: list[dict]) -> list[Message]:
    """输入：transport dict 列表。返回：类型化消息列表（逐条 from_transport）。"""
    return [from_transport(d) for d in items]


def transport_messages(msgs: list[Message]) -> list[dict]:
    """输入：类型化消息列表。返回：transport dict 列表（逐条 to_dict）。"""
    return [m.to_dict() for m in msgs]

# -*- coding: utf-8 -*-
"""测试替身：FakeModelClient / FakeRegistry（引擎离线驱动的脚本化桩）。

设计：FakeModelClient 按轮次脚本（list[StreamDelta]）出流并记录每次
请求收到的消息快照；FakeRegistry 按工具名回放预置输出并记录执行。
两者让主循环的守卫/闸/出口逻辑可离线全路径驱动。
"""
from __future__ import annotations

from core.domain.events import StreamDelta
from core.domain.messages import Message


def text_round(*parts: str, finish: str = "stop") -> list[StreamDelta]:
    """输入：文本片段。返回：一个纯文本回复轮的增量脚本。"""
    deltas = [StreamDelta(content=p) for p in parts]
    deltas.append(StreamDelta(finish_reason=finish))
    return deltas


def empty_round() -> list[StreamDelta]:
    """输入：无。返回：空响应轮脚本（无内容无工具调用）。"""
    return [StreamDelta(finish_reason="stop")]


def tool_round(*calls: tuple[str, str, str], finish: str = "tool_calls") -> list[StreamDelta]:
    """输入：(call_id, name, arguments_json) 元组。返回：工具调用轮脚本。"""
    deltas = []
    for i, (cid, name, args) in enumerate(calls):
        deltas.append(StreamDelta(tool_index=i, tool_call_id=cid,
                                  tool_name=name, tool_args=args))
    deltas.append(StreamDelta(finish_reason=finish))
    return deltas


class FakeModelClient:
    """脚本化模型客户端。

    类职责：按 rounds 脚本逐轮出流；记录每次请求的消息快照（断言注入用）。
    实例属性：rounds（脚本表）、i（当前轮指针）、calls（每轮收到的消息副本）、
    complete_replies（complete_chat 的返回队列）。
    """

    def __init__(self, rounds: list[list[StreamDelta]],
                 complete_replies: list[str] | None = None) -> None:
        """输入：轮次脚本列表 + 非流式回复队列。返回：无。"""
        self.rounds = rounds
        self.i = 0
        self.calls: list[list[Message]] = []
        self.complete_replies = list(complete_replies or ["(summary)"])

    def stream_chat(self, system: str, messages: list[Message],
                    tools: list, max_tokens: int):
        """按脚本出流（脚本耗尽时重复最后一轮，防测试死循环外溢）。"""
        self.calls.append(list(messages))
        script = self.rounds[min(self.i, len(self.rounds) - 1)]
        self.i += 1
        yield from script

    def complete_chat(self, system: str, messages: list[Message],
                      max_tokens: int) -> str:
        """返回预置回复（队列耗尽复用最后一条）。"""
        reply = self.complete_replies[min(len(self.complete_replies) - 1, 0)] \
            if self.complete_replies else "(summary)"
        if len(self.complete_replies) > 1:
            self.complete_replies.pop(0)
        return reply


class FakeRegistry:
    """脚本化工具注册表（按名回放输出）。"""

    def __init__(self, outputs: dict[str, str] | None = None) -> None:
        """输入：工具名→输出文本表。返回：无。"""
        self.outputs = outputs or {}
        self.executed: list[tuple[str, dict]] = []

    def register(self, tool) -> None:
        """无操作（测试不注册真实工具）。"""

    def names(self) -> list[str]:
        """输入：无。返回：预置输出表的工具名。"""
        return sorted(self.outputs)

    def schemas(self, include=None, exclude=None) -> list:
        """输入：无。返回：空 schema 列表（tools_provider 已由测试接管）。"""
        return []

    def readonly_names(self) -> list[str]:
        """输入：无。返回：空列表。"""
        return []

    def execute(self, name: str, args: dict) -> str:
        """执行＝记录并回放预置输出（缺省 "ok"）。"""
        self.executed.append((name, args))
        return self.outputs.get(name, "ok")

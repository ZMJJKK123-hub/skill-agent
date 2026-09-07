# -*- coding: utf-8 -*-
"""模型客户端抽象（interfaces 层）。

业务侧（services/loop）只依赖本 Protocol；唯一实现是
infrastructure/openai_client.py（适配器）。单测注入 Fake 即可
无 API 驱动整个主循环。
"""
from __future__ import annotations

from typing import Iterator, Protocol, TypeAlias, runtime_checkable

from ..domain.events import StreamDelta
from ..domain.messages import Message

#: OpenAI function-calling 工具 schema 的 wire 格式。这是全引擎
#: 唯一被批准的"契约化字典"：形状由 OpenAI 官方规范固定，
#: 由 ToolRegistry.schemas() 产出，业务层不得手工构造。
ToolSchema: TypeAlias = dict


@runtime_checkable
class ModelClient(Protocol):
    """与 LLM 对话的抽象客户端。

    类职责：屏蔽具体 SDK；提供流式（主循环）与非流式（收尾总结）两种调用。
    方法调用逻辑：stream_chat 逐 delta 产出 StreamDelta（含图片多模态
    展开与 x-opencode-session 会话头，均为实现细节）；complete_chat
    一次性返回文本。
    """

    def stream_chat(
        self,
        system: str,
        messages: list[Message],
        tools: list[ToolSchema],
        max_tokens: int,
    ) -> Iterator[StreamDelta]:
        """流式对话（主循环每轮一次）。

        Args:
            system: 系统提示词（prompt 组装后的最终值）。
            messages: 类型化消息历史（实现内部负责多模态图片展开）。
            tools: 本轮可见工具 schema 列表（阶段门控后的子集）。
            max_tokens: 单轮最大输出 token。
        Returns:
            StreamDelta 迭代器；结束原因在最后一个片段的 finish_reason。
        Raises:
            ContextOverflowError: API 明确报上下文超限（调用方应压缩重试）。
            EngineError: 其余 API 故障（含上下文，供日志）。
        """
        ...

    def complete_chat(self, system: str, messages: list[Message],
                      max_tokens: int) -> str:
        """非流式对话（完成闸收尾总结等一次性调用）。

        Args:
            system: 系统提示词。
            messages: 类型化消息历史。
            max_tokens: 最大输出 token。
        Returns:
            模型回复文本（空串视为失败，由调用方回退）。
        """
        ...

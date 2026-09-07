# -*- coding: utf-8 -*-
"""模型调用子服务（services/loop 层）。

职责：一次流式模型请求的完整生命周期——流式增量实时落 run.log
协议通道（[reply]/[思考+] 逐 delta，前端流式渲染依赖）、聚合为
AssistantMessage、空响应熔断（5 次→压缩 / 8 次→强制收尾）、
上下文超限自动压缩重试。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from ...domain.errors import ContextOverflowError
from ...domain.events import StreamDelta
from ...domain.messages import AssistantMessage, ToolCallSpec, UserMessage
from ...domain.session import Mode
from ...infrastructure.logging_.logger import get_logger
from .deps import LoopDeps
from .state import LoopState

logger = get_logger("loop.model_call")

# 流式思考转发钩子：外部接入层（清小搭 8001）实时接收 reasoning delta。
# 全局单例与旧 core.agent.set_reasoning_sink 语义一致（P5 接入方切换引用）。
REASONING_SINK: Optional[Callable[[str], None]] = None


def set_reasoning_sink(fn: Optional[Callable[[str], None]]) -> None:
    """设置/清除 reasoning 实时回调（None 表示关闭）。"""
    global REASONING_SINK
    REASONING_SINK = fn


def get_reasoning_sink() -> Optional[Callable[[str], None]]:
    """输入：无。返回：当前 reasoning 回调（供调用方临时覆盖后恢复）。"""
    return REASONING_SINK


@dataclass
class CallOutcome:
    """一次模型调用的结果。

    属性：
        message: AssistantMessage | None — 聚合回复（ok 时非空）。
        finish_reason: str | None — 本轮结束原因（stop/tool_calls/length）。
        retry: bool — True 表示本轮作废，外层应直接进入下一轮。
    """

    message: Optional[AssistantMessage] = None
    finish_reason: Optional[str] = None
    retry: bool = False


class ModelCallService:
    """流式调用编排。

    类职责：聚合 StreamDelta → AssistantMessage；把增量实时写协议通道；
    空响应与超限两类故障就地自愈（返回 retry 让外层重进）。
    生命周期：bootstrap 构建一次，每轮调用 call()。
    """

    def call(self, state: LoopState, deps: LoopDeps) -> CallOutcome:
        """执行一轮流式模型调用（含全部故障自愈路径）。

        Args:
            state: 循环状态（读 messages，写 empty_strikes/force_final）。
            deps: 依赖容器。
        Returns:
            CallOutcome；retry=True 时 message 为空，外层直接 continue。
        """
        logger.info("=== 新一轮 | messages 长度=%d ===", len(state.messages))
        try:
            deltas = list(self._stream(state, deps))
        except ContextOverflowError as e:
            logger.warning("上下文超限，自动压缩后重试: %s", e)
            state.messages = deps.compaction.auto_compact(state.messages)
            state.synced_count = 0
            return CallOutcome(retry=True)
        message, finish = self._aggregate(deltas)
        if message is None:  # 空响应且无工具调用
            return self._handle_empty(state, deps)
        state.empty_strikes = 0
        if message.reasoning:
            logger.info("reasoning_content:\n%s", message.reasoning)
        return CallOutcome(message=message, finish_reason=finish or "stop")

    # ---------- 流式与聚合 ----------

    def _stream(self, state: LoopState, deps: LoopDeps) -> "list[StreamDelta]":
        """发起流式请求并逐增量转发（写协议通道 + 思考回调）。"""
        stream = deps.client.stream_chat(
            system=deps.system_provider(),
            messages=state.messages,
            tools=deps.tools_provider(),
            max_tokens=deps.settings.model.max_output_tokens,
        )
        out: list[StreamDelta] = []
        for delta in stream:
            out.append(delta)
            if delta.reasoning:
                deps.writer.thinking_delta(delta.reasoning)
                if REASONING_SINK is not None:
                    try:
                        REASONING_SINK(delta.reasoning)
                    except Exception as e:  # 回调方故障不得影响引擎
                        logger.warning("reasoning sink 回调失败: %s", e)
            if delta.content:
                deps.writer.reply_delta(delta.content)
        return out

    def _aggregate(self, deltas: list[StreamDelta]) -> "tuple[Optional[AssistantMessage], Optional[str]]":
        """把增量列表聚合为 AssistantMessage（或 None=空响应）。"""
        content = "".join(d.content for d in deltas)
        reasoning = "".join(d.reasoning for d in deltas)
        finish = next((d.finish_reason for d in reversed(deltas)
                       if d.finish_reason), None)
        calls: dict[int, dict] = {}
        for d in deltas:
            if d.tool_index is None:
                continue
            entry = calls.setdefault(
                d.tool_index, {"id": "", "name": "", "args": ""})
            entry["id"] += d.tool_call_id
            entry["name"] += d.tool_name
            entry["args"] += d.tool_args
        tool_calls = [ToolCallSpec(call_id=c["id"], name=c["name"],
                                   arguments=c["args"])
                      for _, c in sorted(calls.items())] or None
        if not content and not tool_calls:
            return None, finish
        return (AssistantMessage(content=content or None,
                                 tool_calls=tool_calls,
                                 reasoning=reasoning or None), finish)

    # ---------- 空响应熔断 ----------

    def _handle_empty(self, state: LoopState, deps: LoopDeps) -> CallOutcome:
        """空响应分级处置：1-4/6-7 警告重试，5 压缩，≥8 强制收尾。"""
        state.empty_strikes += 1
        logger.warning("模型返回空内容且无工具调用（连续第 %d 次）",
                       state.empty_strikes)
        if state.empty_strikes == 5:
            logger.warning("连续 5 次空响应，尝试 auto_compact 缩上下文")
            state.messages = deps.compaction.auto_compact(state.messages)
            state.synced_count = 0
            return CallOutcome(retry=True)
        if state.empty_strikes >= 8:
            state.force_final_msg = (
                "Model returned empty responses 8 times in a row "
                "(likely context overload). Partial progress is in run.log. "
                "建议：减少一次性加载的技能数量（≤3 个），或换用更稳定的模型。")
            logger.warning("%s", state.force_final_msg)
            return CallOutcome(retry=True)
        state.messages.append(UserMessage(content=self._empty_warning(deps)))
        return CallOutcome(retry=True)

    @staticmethod
    def _empty_warning(deps: LoopDeps) -> str:
        """输入：依赖。返回：按模式生成的空响应警告文本（逐字对齐旧实现）。"""
        if deps.ctx.mode == Mode.MOD:
            return ("<empty-response> 模型返回为空且没有工具调用。你必须调用一个工具继续任务，"
                    "禁止输出空文本或“No additional output”之类的话。</empty-response>")
        return ("<empty-response> 模型返回为空。请直接用自然语言回答用户最新的问题；"
                "只有确需查资料时才调用只读工具。</empty-response>")

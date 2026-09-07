# -*- coding: utf-8 -*-
"""工具批执行子服务（services/loop 层）。

一轮 assistant.tool_calls 的完整执行：预算计数（写前读/写后查）→
JSON 参数容错 → compact 延后 → 注册表统一管线 → [CONCLUDED] 检测 →
spill → 协议通道双行（[tool]/[tool-result]）→ 结果回填。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from ...domain.messages import AssistantMessage, ToolResultMessage
from ...infrastructure.logging_.logger import get_logger
from ...infrastructure.spill import maybe_spill
from .deps import LoopDeps
from .state import LoopState

logger = get_logger("loop.tool_batch")

#: 研究类工具（读/搜/查——写前与写后预算的计数对象）。
RESEARCH_TOOLS = frozenset({
    "read_file", "bash", "grep", "glob",
    "web_search", "web_fetch", "search_api", "load_skill",
})
#: 构建验证类工具（出现即重置写后研究预算）。
BUILD_VERIFY_TOOLS = frozenset({
    "build_mod_jar_forge", "run_test_gametest", "run_mod_test_cycle",
    "validate_resources", "parse_build_output", "read_game_test_log",
})
#: 工具结果内联阈值之外落盘 spill 的豁免名单见 infrastructure/spill.py。


@dataclass
class BatchResult:
    """一轮工具批的结果。

    属性：
        used_todo: bool — 本轮是否调用了 todo 工具（nag 计时清零依据）。
        compact_pending: bool — compact 工具被延后（守卫末尾统一执行）。
        concluded_output: str | None — 带 [CONCLUDED] 的工具输出（提前收尾）。
    """

    used_todo: bool = False
    compact_pending: bool = False
    concluded_output: Optional[str] = None


def _count_budget(state: LoopState, name: str, raw_args: str) -> None:
    """输入：工具名 + 原始参数串。返回：无。职责：写前/写后预算计数。"""
    writes_src = name in ("write_file", "edit_file") and (
        "src/main/java" in raw_args or "src/test/java" in raw_args)
    if writes_src:
        state.wrote_file = True
        state.existing_java = True
    elif not state.wrote_file and name in RESEARCH_TOOLS:
        state.pre_write_reads += 1
    elif state.wrote_file and name in BUILD_VERIFY_TOOLS:
        state.post_write_research = 0
    elif state.wrote_file and name in RESEARCH_TOOLS:
        state.post_write_research += 1


def _args_display(name: str, args: dict, raw: str) -> str:
    """输入：工具名 + 已解析参数 + 原始串。返回：协议行展示文本。"""
    if name == "bash":
        return str(args.get("command", raw))
    return json.dumps(args, ensure_ascii=False)


def execute_batch(state: LoopState, deps: LoopDeps,
                  message: AssistantMessage) -> BatchResult:
    """执行一轮工具调用批（结果逐条回填 state.messages）。

    Args:
        state: 循环状态（预算计数、消息列表、轮工具统计）。
        deps: 依赖容器（registry/writer/阈值）。
        message: 本轮 assistant 消息（tool_calls 来源）。
    Returns:
        BatchResult（used_todo/compact_pending/concluded_output）。
    """
    result = BatchResult()
    for tc in message.tool_calls or []:
        state.round_tool_counts[tc.name] = state.round_tool_counts.get(tc.name, 0) + 1
        _count_budget(state, tc.name, tc.arguments)
        if tc.name == "compact":
            # compact 延后：先跳过，等其他工具执行完由守卫统一压缩
            result.compact_pending = True
            logger.info("compact 工具被模型主动调用 | 先跳过，等其他工具执行完")
            continue
        outcome = _execute_one(state, deps, tc.name, tc.call_id, tc.arguments)
        if outcome is None:
            continue  # 参数 JSON 非法（错误文本已回填）
        if tc.name == "todo":
            result.used_todo = True
        if outcome.concluded:
            result.concluded_output = outcome.text
            logger.info("工具 %s 返回 [CONCLUDED]，本轮将立即收尾", tc.name)
        state.messages.append(ToolResultMessage(tool_call_id=tc.call_id,
                                                content=outcome.text))
    return result


@dataclass
class _OneOutcome:
    """单工具执行结果（concluded 标记 [CONCLUDED] 提前收尾）。"""

    text: str
    concluded: bool = False


def _execute_one(state: LoopState, deps: LoopDeps, name: str,
                 call_id: str, raw_args: str) -> Optional[_OneOutcome]:
    """执行单个工具调用并写协议通道。

    Returns:
        _OneOutcome；参数 JSON 非法时回填温和错误文本并返回 None。
    """
    try:
        args = json.loads(raw_args)
    except Exception as e:
        logger.warning("工具参数解析失败 | %s | %s | raw=%s",
                       name, e, raw_args[:300])
        state.messages.append(ToolResultMessage(
            tool_call_id=call_id,
            content=(f"Error: Invalid tool arguments JSON for {name}: {e}. "
                     f"Please call the tool again with valid JSON arguments.")))
        return None
    raw_output = deps.registry.execute(name, args)
    output = maybe_spill(name, str(raw_output),
                         deps.settings.loop.max_inline_tool_chars)
    ok = not output.lstrip().startswith("Error")
    logger.info("工具调用: %s | 参数=%s | output=%s",
                name, json.dumps(args, ensure_ascii=False), output)
    deps.writer.tool_call(name, _args_display(name, args, raw_args))
    deps.writer.tool_result(ok, output)
    if name == "todo":
        deps.writer.todo(output)
    return _OneOutcome(text=output, concluded="[CONCLUDED]" in output)

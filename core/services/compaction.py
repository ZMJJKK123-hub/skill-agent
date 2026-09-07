# -*- coding: utf-8 -*-
"""上下文压缩服务（services 层）：三层递进压缩的类型化重写。

移植自旧 core/compact.py（dsh compaction-basic），行为对齐：
    Layer 1 micro_compact —— 已禁用（旧实现即 no-op，防裁剪吞掉报错日志）
    Layer 2 auto_compact  —— token 超阈值：保存 transcript → 选边界 →
                             结构化摘要 → 替换旧区间保留尾部 + 初始锚点
    Layer 3 handle_compact —— 模型主动调用，复用 Layer 2
与旧版的唯一结构差异：摘要请求走注入的 ModelClient（不再读全局单例）。
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from ..domain.messages import Message, UserMessage, transport_messages
from ..infrastructure.config import ModelSettings
from ..infrastructure.logging_.logger import get_logger
from ..interfaces.model_client import ModelClient

logger = get_logger("compaction")

#: 大上下文模型的窗口映射（未列出的模型回退 DEFAULT_CONTEXT_WINDOW）。
MODEL_CONTEXT_WINDOWS = {
    "DeepSeek-V4-Flash-0731": 1_000_000,
    "DeepSeek-V4-Pro": 1_000_000,
}
DEFAULT_CONTEXT_WINDOW = 1_000_000
THRESHOLD_RATIO = 0.8   # 超过窗口 80% 触发自动压缩
RETAIN_RATIO = 0.16     # 尾部保留 16% 原样不压
MAX_SUMMARY_TOKENS = 4000

#: 结构化摘要指令（dsh summarizer 验证过的固定 8 节模板）。
COMPACTION_INSTRUCTION = (
    "You are now acting as a compaction engine for this AI coding assistant. "
    "Condense the conversation ABOVE into a structured checkpoint that lets another model "
    "resume the work with no loss of essential context.\n\n"
    "Output EXACTLY the Markdown structure below: keep every section, in order. "
    'Use terse bullets, not prose paragraphs. Write "(none)" for an empty section — never drop a section.\n\n'
    "## Primary Request and Intent\n"
    "- [the user's original and evolving goals; quote verbatim where the exact wording matters]\n\n"
    "## Key Technical Concepts\n"
    "- [technologies, frameworks, patterns, and conventions in play]\n\n"
    "## Files and Code\n"
    "- [exact path: why it matters, key changes or snippets]\n\n"
    "## Errors and Fixes\n"
    "- [error: how it was resolved, plus any related user feedback]\n\n"
    "## Pending Jobs\n"
    "- [explicitly requested work not yet completed]\n\n"
    "## Current Work\n"
    "- [precisely what was in progress at this checkpoint]\n\n"
    "## Next Step\n"
    '- [the single next action, directly in line with the most recent request, or "(none)"]\n\n'
    "## Critical Context\n"
    "- [decisions and their rationale, constraints, user preferences, open questions, data needed to continue]\n\n"
    "Rules:\n"
    "- Write concise English engineering prose. Preserve exact file paths, commands, error strings, "
    "identifiers, numeric values, function signatures, and syntax fragments.\n"
    "- Capture user feedback and explicit instructions faithfully, especially corrections.\n"
    "- Do NOT mention this summarization request or that the context was compacted.\n"
    "- Output only the checkpoint text: do not call any tool or take any other action.\n"
    "- If the conversation already contains a <compacted-summary> block, it is a PRIOR checkpoint. "
    "Do not copy it forward verbatim: preserve still-true facts, drop stale ones, and merge newer "
    "information into a single consolidated summary under the same structure."
)

CHECKPOINT_PREAMBLE = (
    "This is an automatically generated checkpoint condensing an earlier span of the conversation "
    "to free up context. Treat the captured context as established background and build on it "
    "without restating it. Continue the task directly from the messages that follow, without "
    "acknowledging this checkpoint."
)


def resolve_context_window(model: ModelSettings) -> int:
    """输入：模型配置。返回：生效的上下文窗口 token 数（显式配置优先）。"""
    if model.context_window > 0:
        return model.context_window
    return MODEL_CONTEXT_WINDOWS.get(model.model, DEFAULT_CONTEXT_WINDOW)


def estimate_tokens(messages: list[Message]) -> int:
    """粗估 token 数：chars / 3（兼顾中英文；对 transport dict 统计）。"""
    total_chars = 0
    for d in transport_messages(messages):
        total_chars += len(d.get("role", ""))
        content = d.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                text = json.dumps(block, ensure_ascii=False) if isinstance(block, dict) else str(block)
                total_chars += len(text)
        for tc in d.get("tool_calls") or []:
            total_chars += len(json.dumps(tc, ensure_ascii=False))
    return total_chars // 3


class CompactionService:
    """上下文压缩编排（依赖注入 ModelClient，可离线单测）。

    类职责：token 阈值判定 + 区间选择 + 结构化摘要 + 消息替换。
    类变量/实例属性：
        _client: ModelClient — 摘要请求通道。
        _system: Callable[[], str] — 摘要时携带的当前系统提示词。
        _window: int — 生效上下文窗口。
    生命周期：bootstrap 构建一次，随引擎存活。
    """

    def __init__(self, client: ModelClient, system_provider: Callable[[], str],
                 model: ModelSettings) -> None:
        """输入：模型客户端 + 系统提示词提供器 + 模型配置。返回：无。"""
        self._client = client
        self._system = system_provider
        self._window = resolve_context_window(model)

    @property
    def token_threshold(self) -> int:
        """输入：无。返回：自动压缩触发阈值（窗口 × 0.8）。"""
        return int(self._window * THRESHOLD_RATIO)

    # ---------- 边界选择 ----------

    def _select_cutoff(self, messages: list[Message]) -> int:
        """输入：消息列表。返回：保留尾部起始索引（不拆工具调用对）。"""
        retain = int(self._window * RETAIN_RATIO)
        items = transport_messages(messages)
        if not items:
            return 0
        accumulated, keep_from = 0, len(items)
        for i in range(len(items) - 1, -1, -1):
            accumulated += estimate_tokens([messages[i]])
            keep_from = i
            if accumulated >= retain:
                break
        while keep_from > 0:
            cur, prev = items[keep_from], items[keep_from - 1]
            if cur.get("role") == "tool" or prev.get("tool_calls"):
                keep_from -= 1
            else:
                break
        return keep_from

    # ---------- Layer 2 ----------

    def _save_transcript(self, messages: list[Message]) -> Path:
        """输入：消息列表。返回：transcript 快照路径（压缩前全量留底）。"""
        out_dir = Path(".transcripts")
        out_dir.mkdir(exist_ok=True)
        filepath = out_dir / f"conversation_{int(time.time())}.jsonl"
        with filepath.open("w", encoding="utf-8") as f:
            for d in transport_messages(messages):
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        logger.info("transcript.saved | messages=%d | path=%s", len(messages), filepath)
        return filepath

    def _summarize_region(self, region: list[Message]) -> str:
        """对压缩区间做结构化摘要（system + 区间 + 固定指令）。"""
        summary = self._client.complete_chat(
            self._system(), region, max_tokens=MAX_SUMMARY_TOKENS)
        return f"{CHECKPOINT_PREAMBLE}\n\n<compacted-summary>\n{summary}\n</compacted-summary>"

    def auto_compact(self, messages: list[Message]) -> list[Message]:
        """token 超阈值时的自动压缩（摘要必须更小，否则原样返回）。

        Args:
            messages: 当前完整消息列表。
        Returns:
            压缩后的新消息列表（锚点 + checkpoint + 保留尾部）。
        """
        pre_tokens = estimate_tokens(messages)
        filepath = self._save_transcript(messages)
        keep_from = self._select_cutoff(messages)
        region, keep = messages[:keep_from], messages[keep_from:]
        summary = self._summarize_region(region)
        region_tokens = estimate_tokens(region)
        if len(summary) // 3 >= region_tokens:
            logger.warning("auto_compact | 摘要未更小（%d >= %d），放弃压缩",
                           len(summary) // 3, region_tokens)
            return messages
        anchor = None
        if region and isinstance(region[0], UserMessage) and len(region[0].content) <= 1500:
            anchor = region[0]
        new_messages: list[Message] = []
        if anchor is not None:
            new_messages.append(anchor)
        new_messages.append(UserMessage(content=(
            f"[Context compacted. Full transcript: {filepath}]\n\n{summary}\n\n"
            "Continue from where we left off."
        )))
        new_messages.extend(keep)
        logger.info("auto_compact | messages %d→%d | tokens ≈%d→≈%d | cutoff=%d",
                    len(messages), len(new_messages), pre_tokens,
                    estimate_tokens(new_messages), keep_from)
        return new_messages

    def handle_compact(self, messages: list[Message]) -> tuple[list[Message], str]:
        """Layer 3：模型主动调用 compact 工具。返回 (新消息列表, 工具结果文本)。"""
        logger.info("handle_compact | 模型主动调用 compact 工具")
        return self.auto_compact(messages), "Context compacted successfully."

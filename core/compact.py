"""
三层递进上下文压缩（移植 dsh compaction-basic 的思路到 DeepSeek/OpenAI 消息格式）。

Layer 1: micro_compact  — 每轮自动，静默裁剪旧 tool_result（模型无关裁剪，对应 tool-result-pruner）
Layer 2: auto_compact   — token 超阈值，保留最近尾部，只摘要压缩更早的区间
Layer 3: compact 工具    — 模型主动触发，复用 Layer 2 流程

关键移植点（来自 dsh compaction-basic / summarizer.ts）：
- 结构化摘要 prompt：Primary Request / Key Concepts / Files / Errors / Pending /
  Current / Next Step / Critical Context（每节固定，空写 "(none)"）
- 摘要落成 checkpoint 消息：带 <compacted-summary> 标签 + preamble（说明是已建立的上下文）
- 保留最近 retainTokens 尾部原样，只压缩更早区间，且边界不拆开 assistant(tool_calls)
  与 tool 结果对（对应 dsh 的 toolPairingBalancedBefore）
- 摘要必须比被压缩内容更小，否则拒绝（对应 dsh 的 summary-is-smaller 校验）
"""

import json
import os
import time
from pathlib import Path

from .config import client, MODEL, logger

# ── 压缩预算（对应 dsh config：thresholdRatio=0.8 / retainRatio=0.16）──
# per-model context window map; env DSH_CONTEXT_WINDOW always wins.
MODEL_CONTEXT_WINDOWS = {
    "DeepSeek-V4-Flash-0731": 1000000,
    "DeepSeek-V4-Pro": 1000000,
}
CONTEXT_WINDOW = int(os.environ.get(
    "DSH_CONTEXT_WINDOW",
    str(MODEL_CONTEXT_WINDOWS.get(MODEL, 1000000)),
))
THRESHOLD_RATIO = 0.8
RETAIN_RATIO = 0.16
TOKEN_THRESHOLD = int(CONTEXT_WINDOW * THRESHOLD_RATIO)  # 触发阈值
RETAIN_TOKENS = int(CONTEXT_WINDOW * RETAIN_RATIO)        # 保留尾部预算
MAX_SUMMARY_TOKENS = 4000


# ── 结构化摘要指令（照搬 dsh summarizer.ts，已被验证）────────────
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


# ── Token 估算 ───────────────────────────────────────────
def estimate_tokens(messages: list) -> int:
    """粗估 token 数：chars / 3（兼顾中英文）。"""
    total_chars = 0
    for msg in messages:
        total_chars += len(msg.get("role", ""))
        content = msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    total_chars += len(json.dumps(block, ensure_ascii=False))
                else:
                    total_chars += len(str(block))
        for tc in msg.get("tool_calls", []) or []:
            total_chars += len(json.dumps(tc, ensure_ascii=False))
    return total_chars // 3


def _msg_tokens(msg: dict) -> int:
    return estimate_tokens([msg])


# ── 边界选择（对应 dsh selectCompactableRange）────────────
def select_cutoff(messages: list) -> int:
    """返回 keep_from 索引：该索引及其后的消息保留，之前的部分被压缩。

    从末尾向前累计 token 到 RETAIN_TOKENS，得到最近的保留尾部；
    再回退到「平衡边界」——不拆开 assistant(tool_calls) 与紧跟的 tool 结果对。
    """
    if not messages:
        return 0
    accumulated = 0
    keep_from = len(messages)
    for i in range(len(messages) - 1, -1, -1):
        accumulated += _msg_tokens(messages[i])
        keep_from = i
        if accumulated >= RETAIN_TOKENS:
            break
    if keep_from == 0:
        return 0
    while keep_from > 0:
        cur = messages[keep_from]
        prev = messages[keep_from - 1]
        if cur.get("role") == "tool" or prev.get("tool_calls"):
            keep_from -= 1
        else:
            break
    return keep_from


# ── Layer 1: micro_compact（模型无关裁剪，对应 tool-result-pruner）──
def _find_tool_name(messages: list, tool_call_id: str) -> str:
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []) or []:
            if tc.get("id") == tool_call_id:
                return tc.get("function", {}).get("name", "unknown")
    return "unknown"


def micro_compact(messages: list, keep_recent: int = 3) -> None:
    """保留最近 keep_recent 轮完整内容，更早的 tool_result 替换为占位符。"""
    assistant_indices = [
        i for i, m in enumerate(messages) if m.get("role") == "assistant"
    ]
    if len(assistant_indices) <= keep_recent:
        return
    cutoff_index = assistant_indices[-keep_recent]
    for i, msg in enumerate(messages):
        if i >= cutoff_index:
            break
        if msg.get("role") != "tool":
            continue
        content = msg.get("content", "")
        if not isinstance(content, str):
            continue
        tool_name = _find_tool_name(messages, msg.get("tool_call_id", ""))
        msg["content"] = f"[Previous: used {tool_name}]"


# ── Layer 2/3: 结构化摘要压缩 ─────────────────────────────
def save_transcript(messages: list) -> Path:
    """保存完整对话到 .transcripts/，压缩前的快照。"""
    transcript_dir = Path(".transcripts")
    transcript_dir.mkdir(exist_ok=True)
    filepath = transcript_dir / f"conversation_{int(time.time())}.jsonl"
    with open(filepath, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    logger.info(f"save_transcript | 保存 {len(messages)} 条消息到 {filepath}")
    return filepath


def summarize_region(region: list) -> str:
    """对要压缩的区间做一次结构化摘要（回放区间 + 追加压缩指令，对应 dsh summarizeWithLlm）。

    带上当前系统提示词，和 dsh summarizer 一样让摘要模型理解角色/规则，避免摘要跑偏。
    """
    from . import config as _config
    msgs = [{"role": "system", "content": _config.SYSTEM}]
    msgs += list(region)
    msgs.append({"role": "user", "content": COMPACTION_INSTRUCTION})
    response = client.chat.completions.create(
        model=MODEL,
        messages=msgs,
        max_tokens=MAX_SUMMARY_TOKENS,
    )
    summary = response.choices[0].message.content or ""
    return f"{CHECKPOINT_PREAMBLE}\n\n<compacted-summary>\n{summary}\n</compacted-summary>"


def auto_compact(messages: list) -> list:
    """Layer 2：保存 transcript → 选压缩区间 → 结构化摘要 → 替换旧区间，保留最近尾部。

    额外保留初始任务锚点（第一条短 user 消息），防止关键原始指令被摘要稀释。
    """
    pre_tokens = estimate_tokens(messages)
    filepath = save_transcript(messages)

    keep_from = select_cutoff(messages)
    region = messages[:keep_from]
    keep = messages[keep_from:]

    summary = summarize_region(region)

    # 摘要必须更小，否则保留原样（对应 dsh 的 summary-is-smaller 校验）
    region_tokens = estimate_tokens(region)
    summary_tokens = len(summary) // 3
    if summary_tokens >= region_tokens:
        logger.warning(
            f"auto_compact | 摘要未更小（{summary_tokens} >= {region_tokens}），放弃压缩"
        )
        return messages

    # 保留初始任务锚点：第一条 user 消息若较短，原样带到压缩后
    anchor = None
    if messages:
        first = messages[0]
        fc = first.get("content", "")
        if first.get("role") == "user" and isinstance(fc, str) and len(fc) <= 1500:
            anchor = first

    new_messages = []
    if anchor is not None:
        new_messages.append(anchor)
    new_messages.append({
        "role": "user",
        "content": (
            f"[Context compacted. Full transcript: {filepath}]\n\n{summary}\n\n"
            "Continue from where we left off."
        ),
    })
    new_messages += keep

    post_tokens = estimate_tokens(new_messages)
    logger.info(
        f"auto_compact | messages {len(messages)}→{len(new_messages)} | "
        f"tokens ≈{pre_tokens}→≈{post_tokens} | cutoff={keep_from}"
    )
    return new_messages


def handle_compact(messages: list) -> tuple:
    """Layer 3：模型主动调用 compact，复用 auto_compact。返回 (new_messages, output)。"""
    logger.info("handle_compact | 模型主动调用 compact 工具")
    new_messages = auto_compact(messages)
    return new_messages, "Context compacted successfully."

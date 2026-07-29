"""
三层递进上下文压缩系统（第 6 课）。

Layer 1: micro_compact  — 每轮自动，静默裁剪旧 tool_result
Layer 2: auto_compact   — token 超阈值，整段对话压缩为摘要
Layer 3: compact 工具    — 模型主动调用，复用 Layer 2 摘要流程

适配 DeepSeek/OpenAI 消息格式（role: tool 独立消息，非 Claude content list）。
"""

import json
import time
from pathlib import Path

from config import client, MODEL, logger

TOKEN_THRESHOLD = 100_000  # Layer 2 触发阈值


# ── Token 估算 ───────────────────────────────────────────
def estimate_tokens(messages: list) -> int:
    """粗估 token 数：chars / 3（兼顾中英文，中文 1 字 ≈ 1-2 token）。"""
    total_chars = 0
    for msg in messages:
        # role
        total_chars += len(msg.get("role", ""))
        # content
        content = msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    total_chars += len(json.dumps(block, ensure_ascii=False))
                else:
                    total_chars += len(str(block))
        # tool_calls
        for tc in msg.get("tool_calls", []) or []:
            total_chars += len(json.dumps(tc, ensure_ascii=False))
    estimated = total_chars // 3
    logger.info(f"estimate_tokens | messages={len(messages)} | chars={total_chars} | ≈{estimated} tokens")
    return estimated


# ── 辅助：根据 tool_call_id 反查工具名 ─────────────────
def _find_tool_name(messages: list, tool_call_id: str) -> str:
    """在 assistant 消息的 tool_calls 里按 ID 反查工具名。"""
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for tc in msg.get("tool_calls", []) or []:
            if tc.get("id") == tool_call_id:
                return tc.get("function", {}).get("name", "unknown")
    return "unknown"


# ── Layer 1: micro_compact ──────────────────────────────
def micro_compact(messages: list, keep_recent: int = 3) -> None:
    """保留最近 keep_recent 轮完整内容，更早的 tool_result 替换为占位符。

    DeepSeek 格式：tool result 是独立的 role=tool 消息（含 tool_call_id + content）。
    我们把 keep_recent 轮之前的 role=tool 消息的 content 替换为占位符。
    """
    # 找出所有 assistant 消息的索引（每轮的标志）
    assistant_indices = [
        i for i, m in enumerate(messages)
        if m.get("role") == "assistant"
    ]
    if len(assistant_indices) <= keep_recent:
        logger.info(f"micro_compact | assistant 轮数={len(assistant_indices)} <= {keep_recent}，跳过")
        return

    cutoff_index = assistant_indices[-keep_recent]
    replaced_count = 0
    saved_chars = 0

    for i, msg in enumerate(messages):
        if i >= cutoff_index:
            break
        if msg.get("role") != "tool":
            continue
        original_content = msg.get("content", "")
        if not isinstance(original_content, str):
            continue
        tool_name = _find_tool_name(messages, msg.get("tool_call_id", ""))
        saved_chars += len(original_content)
        msg["content"] = f"[Previous: used {tool_name}]"
        replaced_count += 1

    logger.info(
        f"micro_compact | 替换 {replaced_count} 个旧 tool_result | "
        f"省 ≈{saved_chars // 3} tokens | cutoff_index={cutoff_index}"
    )


# ── Layer 2: auto_compact ───────────────────────────────
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


def format_messages_for_summary(messages: list) -> str:
    """把 DeepSeek 消息列表转为可读文本，供 LLM 摘要。"""
    lines = []
    for msg in messages:
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if isinstance(content, list):
            content = json.dumps(content, ensure_ascii=False)
        lines.append(f"[{role}] {content}")
        # 附带 tool_calls 信息
        for tc in msg.get("tool_calls", []) or []:
            name = tc.get("function", {}).get("name", "?")
            args = tc.get("function", {}).get("arguments", "{}")
            lines.append(f"  -> tool_call: {name}({args})")
    return "\n".join(lines)


def summarize_conversation(messages: list) -> str:
    """让 DeepSeek 把完整对话压缩为结构化摘要。"""
    formatted = format_messages_for_summary(messages)
    pre_tokens = len(formatted) // 3

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": (
                    "把对话压缩为结构化摘要。保留：1) 用户原始目标 "
                    "2) 已完成步骤 3) 关键发现和决策 4) 当前待办。"
                    "丢弃：具体文件内容、命令输出、中间调试过程。"
                ),
            },
            {
                "role": "user",
                "content": formatted,
            },
        ],
    )
    summary = response.choices[0].message.content
    post_tokens = len(summary) // 3
    logger.info(
        f"summarize_conversation | 压缩前 ≈{pre_tokens} tokens → "
        f"压缩后 ≈{post_tokens} tokens | 压缩比 {pre_tokens / max(post_tokens, 1):.1f}:1"
    )
    return summary


def auto_compact(messages: list) -> list:
    """Layer 2：保存 transcript + 生成摘要 + 替换消息列表。"""
    pre_len = len(messages)
    pre_tokens = estimate_tokens(messages)

    filepath = save_transcript(messages)
    summary = summarize_conversation(messages)

    new_messages = [{
        "role": "user",
        "content": (
            f"[Context compacted. Full transcript: {filepath}]\n\n"
            f"## Conversation Summary\n\n{summary}\n\n"
            "Continue from where we left off."
        ),
    }]

    post_tokens = estimate_tokens(new_messages)
    logger.info(
        f"auto_compact | messages {pre_len} → {len(new_messages)} | "
        f"tokens ≈{pre_tokens} → ≈{post_tokens}"
    )
    return new_messages


# ── Layer 3: compact 工具 ───────────────────────────────
def handle_compact(messages: list) -> tuple:
    """模型主动触发，复用 auto_compact 的摘要流程。

    返回 (new_messages, output_string)。
    output_string 作为 tool_result 返回给模型（但实际 messages 已被替换）。
    """
    logger.info("handle_compact | 模型主动调用 compact 工具")
    new_messages = auto_compact(messages)
    return new_messages, "Context compacted successfully."
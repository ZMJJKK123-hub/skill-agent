# -*- coding: utf-8 -*-
"""agent.log（logging 输出）→ 事件。
由 log_events.py 原样迁出。
"""
import re


# ---------- agent.log 事件解析 ----------

def _strip_ts(line: str) -> str:
    """去掉开头的 '2024-08-04 01:23:45,678 [LEVEL] ' 前缀。"""
    idx = line.find(" [")
    if idx > 0:
        # 去掉 [LEVEL] 标记（如 [INFO]），只保留消息正文
        rest = line[idx + 1:].strip()
        if rest.startswith("[") and "]" in rest:
            rest = rest[rest.index("]") + 1:].strip()
        return rest
    return line.strip()


def _parse_agent_block(text: str) -> list[dict]:
    """把 agent.log 的一段新增文本解析为事件列表。

    提取高价值事件：工具调用、round、后台任务、团队/协议动作。
    """
    events: list[dict] = []
    seq = 0
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        if not line.strip():
            continue
        msg = _strip_ts(line)

        if msg.startswith("工具调用:"):
            events.append(_ev("tool_call", msg[len("工具调用:"):].strip(), seq,
                              source="agent")); seq += 1
        elif msg.startswith("=== 新一轮"):
            events.append(_ev("round", msg, seq, source="agent")); seq += 1
        elif msg.startswith("=== 队友 Agent 启动") or msg.startswith("=== 队友 Agent 结束"):
            events.append(_ev("system", msg, seq, source="agent")); seq += 1
        elif msg.startswith("=== Subagent 启动") or msg.startswith("=== Subagent 结束"):
            events.append(_ev("system", msg, seq, source="agent")); seq += 1
        elif msg.startswith("注入后台通知"):
            events.append(_ev("background", msg, seq, source="agent")); seq += 1
        elif msg.startswith("注入队友汇报"):
            events.append(_ev("teammate_report", msg, seq, source="agent")); seq += 1
        elif msg.startswith("TeamCoordinator.") or msg.startswith("ProtocolTracker."):
            events.append(_ev("protocol", msg, seq, source="agent")); seq += 1
        elif msg.startswith("WorktreeManager."):
            events.append(_ev("worktree", msg, seq, source="agent")); seq += 1
        # 其余 INFO 日志太多，不进入事件流（避免刷屏）
    return events



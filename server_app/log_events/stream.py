# -*- coding: utf-8 -*-
"""增量事件流：字节偏移游标 + 跨 poll 的 reply 续接缓存。
由 log_events.py 原样迁出。
"""
import itertools
import json
from pathlib import Path
from typing import Optional

from .agentparse import _parse_agent_block
from .runparse import _parse_run_block


# ---------- 增量流 ----------

_ID_COUNTER = itertools.count(1)

# 增量轮询时，如果 run.log 尾部停在一条未结束的 [reply] 流中间，
# 把已解析的回复片段暂存到这里，等下一次 poll 拿到后续字节后合并成一条完整 reply。
_PENDING_RUN_REPLY: dict[str, dict] = {}


def build_event_stream(session_dir: Path, cursor: Optional[dict] = None) -> dict:
    """读取两条日志的新增内容，合并为事件列表。

    cursor 结构：{"run": <int>, "agent": <int>}（字节偏移），None 表示从头读。
    返回：{"events": [...], "cursor": {...}}
    """
    run_log = session_dir / "run.log"
    agent_log = session_dir / "mod" / "agent.log"

    run_off = (cursor or {}).get("run", 0)
    agent_off = (cursor or {}).get("agent", 0)

    events: list[dict] = []
    next_cursor = {"run": run_off, "agent": agent_off}
    run_key = str(session_dir)

    # 全量读取时清掉历史 pending，从头部完整解析
    if cursor is None:
        _PENDING_RUN_REPLY.pop(run_key, None)
    pending_run_reply = _PENDING_RUN_REPLY.get(run_key)

    if run_log.exists():
        size = run_log.stat().st_size
        if size < run_off:
            run_off = 0  # 文件被截断/重建，游标重置
            _PENDING_RUN_REPLY.pop(run_key, None)
            pending_run_reply = None
        if size > run_off:
            with open(run_log, "r", encoding="utf-8", errors="replace") as f:
                f.seek(run_off)
                chunk = f.read(size - run_off)
            next_cursor["run"] = size
            incremental = cursor is not None
            evs, new_pending = _parse_run_block(chunk, pending_run_reply, flush_at_eof=not incremental)
            events.extend(evs)
            if incremental:
                if new_pending is None:
                    _PENDING_RUN_REPLY.pop(run_key, None)
                else:
                    _PENDING_RUN_REPLY[run_key] = new_pending
            else:
                _PENDING_RUN_REPLY.pop(run_key, None)
    else:
        next_cursor["run"] = 0
        _PENDING_RUN_REPLY.pop(run_key, None)

    if agent_log.exists():
        size = agent_log.stat().st_size
        if size < agent_off:
            agent_off = 0  # 文件被截断/重建，游标重置
        if size > agent_off:
            with open(agent_log, "r", encoding="utf-8", errors="replace") as f:
                f.seek(agent_off)
                chunk = f.read(size - agent_off)
            next_cursor["agent"] = size
            events.extend(_parse_agent_block(chunk))
    else:
        next_cursor["agent"] = 0

    # 统一重新编号，使用进程内单调计数器，保证 id 跨轮唯一
    for ev in events:
        ev["id"] = f"ev-{next(_ID_COUNTER)}"

    # peer 传播：[supervisor:xxx]/[subagent:xxx] 工具的 [tool-result] 行自身
    # 不带 peer 标记，前端按 peer 过滤内部工具时会漏掉这些红色失败行。
    # 把最近一个带 peer 的 tool_call 的 peer 传给紧随其后的 tool_result。
    last_peer = None
    for ev in events:
        if ev["type"] == "tool_call":
            last_peer = ev.get("peer")
        elif ev["type"] == "tool_result":
            if last_peer and not ev.get("peer"):
                ev["peer"] = last_peer
            if not ev.get("peer"):
                last_peer = None  # 主 agent 自己的工具结果，重置
        else:
            last_peer = None

    return {"events": events, "cursor": next_cursor}



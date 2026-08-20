"""日志事件流解析器。

把 agent 运行期间产生的两种日志解析成结构化事件：
  - run.log    子进程 stdout（run_task.py + core 里 print 的内容）
               含：[思考]、[todo]、[subagent/teammate 思考]、[subagent/teammate:工具]
  - mod/agent.log   logging 输出（core 里 logger.info 的内容）
               含：工具调用、round 开始、后台任务、团队动作、协议事件

设计原则：
  - 纯函数，无副作用；不依赖任何核心代码
  - 增量：调用方传入已读字节偏移，返回新事件 + 新偏移
  - 事件对象统一结构：{id, ts, type, source, content, ...extras}
"""

import itertools
import time
from pathlib import Path
from typing import Optional


# ---------- run.log 事件解析 ----------

def _ev(e_type: str, content: str, seq: int, **extra) -> dict:
    ev = {
        "id": f"ev-{seq}",
        "ts": time.time(),
        "type": e_type,
        "source": "run",
        # 调试需要：事件正文全量保留，不截断（便于使用者查看完整输出）
        "content": content,
    }
    ev.update(extra)
    return ev


def _after(text: str, prefix: str) -> str:
    return text[len(prefix):].strip()


def _split_tag(line: str) -> tuple[str, str]:
    """解析 '[teammate:bash] 输出...' → ('bash', '] 输出...')"""
    end = line.index("]")
    return line[len("["):end], line[end:]


def _parse_run_block(text: str) -> list[dict]:
    """把 run.log 的一段新增文本解析为事件列表。

    行级识别 + [todo] 块处理（todo 块 = 一行 [todo] 后跟若干缩进行）。
    """
    events: list[dict] = []
    lines = text.splitlines()
    i = 0
    seq = 0
    skip_final_reply = False
    while i < len(lines):
        line = lines[i].rstrip("\r")
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 跳过“完成，最终回复:”及其后的完整回复正文，避免事件流里重复显示最终回复
        if skip_final_reply:
            if stripped.startswith("["):
                skip_final_reply = False
            else:
                i += 1
                continue

        if stripped.startswith("[run_task]"):
            # 内部启动/收尾日志不展示给用户；若包含“最终回复”，则后续正文也跳过
            if "最终回复" in stripped:
                skip_final_reply = True
            i += 1
            continue
        elif stripped.startswith("[思考]"):
            events.append(_ev("thinking", _after(stripped, "[思考]"), seq)); seq += 1
        elif stripped.startswith("[teammate 思考]"):
            events.append(_ev("thinking", _after(stripped, "[teammate 思考]"), seq,
                              peer="teammate")); seq += 1
        elif stripped.startswith("[subagent 思考]"):
            events.append(_ev("thinking", _after(stripped, "[subagent 思考]"), seq,
                              peer="subagent")); seq += 1
        elif stripped.startswith("[supervisor 思考]"):
            events.append(_ev("thinking", _after(stripped, "[supervisor 思考]"), seq,
                              peer="supervisor")); seq += 1
        # ── 新结构化工具日志（core/agent.py 主 agent 输出，DSH 风格渲染用）──
        elif stripped.startswith("[reply]"):
            # 流式回复增量（每个 token 一行），不单独作为事件，避免刷屏
            i += 1
            continue
        elif stripped.startswith("[tool-result]"):
            # [tool-result] success|failed\n<输出> —— 多行块：收集后续行，
            # 遇到下一个 [标记行 或 空行 时停止（不能吞掉后续工具事件）
            rest = _after(stripped, "[tool-result]")
            block = [rest]
            j = i + 1
            while j < len(lines):
                nxt = lines[j].rstrip("\r")
                if not nxt.strip() or nxt.strip().startswith("["):
                    break
                block.append(nxt)
                j += 1
            status = "success" if rest.startswith("success") else "failed"
            content = "\n".join(block)
            events.append(_ev("tool_result", content, seq, status=status)); seq += 1
            i = j - 1
        elif stripped.startswith("[tool]"):
            # [tool] <工具名> <参数JSON/命令>
            rest = _after(stripped, "[tool]")
            parts = rest.split(" ", 1)
            tool_name = parts[0] if parts else "tool"
            detail = parts[1] if len(parts) > 1 else ""
            events.append(_ev("tool_call", detail, seq, tool=tool_name)); seq += 1
        elif stripped.startswith("[teammate:") and "]" in stripped:
            name, rest = _split_tag(stripped)
            events.append(_ev("tool_call", _after(rest, "]"), seq,
                              tool=name, peer="teammate")); seq += 1
        elif stripped.startswith("[subagent:") and "]" in stripped:
            name, rest = _split_tag(stripped)
            events.append(_ev("tool_call", _after(rest, "]"), seq,
                              tool=name, peer="subagent")); seq += 1
        elif stripped.startswith("[supervisor:") and "]" in stripped:
            name, rest = _split_tag(stripped)
            events.append(_ev("tool_call", _after(rest, "]"), seq,
                              tool=name, peer="supervisor")); seq += 1
        elif stripped == "[todo]":
            block = []
            j = i + 1
            # 只收集缩进的行（todo 列表项），遇到顶格行或空行停止
            while j < len(lines) and lines[j].startswith((" ", "\t")):
                block.append(lines[j].rstrip("\r"))
                j += 1
            events.append(_ev("todo", "\n".join(block), seq)); seq += 1
            i = j - 1
        else:
            events.append(_ev("log", stripped, seq)); seq += 1
        i += 1
    return events


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


# ---------- 增量流 ----------

_ID_COUNTER = itertools.count(1)


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

    if run_log.exists():
        size = run_log.stat().st_size
        if size < run_off:
            run_off = 0  # 文件被截断/重建，游标重置
        if size > run_off:
            with open(run_log, "r", encoding="utf-8", errors="replace") as f:
                f.seek(run_off)
                chunk = f.read(size - run_off)
            next_cursor["run"] = size
            events.extend(_parse_run_block(chunk))
    else:
        next_cursor["run"] = 0

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

    return {"events": events, "cursor": next_cursor}


# ---------- 文件树 ----------

def build_file_tree(root: Path, rel: str = "") -> dict:
    """递归构建文件树。返回 {name, path, type, size, children?}"""
    node = {
        "name": Path(rel).name if rel else root.name,
        "path": rel,
        "type": "dir",
        "children": [],
    }
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError:
        return node
    for p in entries:
        # 跳过运行时产物（mc_java_sources = MC+Forge 源码树，只对 agent 可见，
        # 不展示给前端，避免文件树渲染 8000+ 节点）
        if p.name in (".worktrees", ".team", ".tasks", ".transcripts",
                      "__pycache__", "agent.log", "run.log", ".git",
                      "mc_java_sources"):
            continue
        child_rel = f"{rel}/{p.name}" if rel else p.name
        if p.is_dir():
            node["children"].append(build_file_tree(p, child_rel))
        else:
            try:
                sz = p.stat().st_size
            except OSError:
                sz = 0
            node["children"].append({
                "name": p.name,
                "path": child_rel,
                "type": "file",
                "size": sz,
            })
    return node


MAX_PREVIEW = 100_000  # 预览上限 100KB


def read_file_preview(root: Path, rel_path: str) -> dict:
    """读取文件内容用于预览。返回 {content, truncated, size} 或错误 dict。"""
    target = (root / rel_path).resolve()
    # 防越界：必须位于 root 之下
    if not target.is_relative_to(root.resolve()):
        return {"error": "invalid path"}
    if not target.is_file():
        return {"error": "not a file"}
    size = target.stat().st_size
    data = target.read_text(encoding="utf-8", errors="replace")
    truncated = len(data) > MAX_PREVIEW
    return {
        "content": data[:MAX_PREVIEW],
        "truncated": truncated,
        "size": size,
    }

# -*- coding: utf-8 -*-
"""run.log 行协议解析：[reply]/[思考+]/[tool]/[tool-result]/[todo] → 事件。
由 log_events.py 原样迁出。
"""
import json
import re
import time
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


def _parse_run_block(text: str, pending: dict | None = None, flush_at_eof: bool = True) -> tuple[list[dict], dict | None]:
    """把 run.log 的一段新增文本解析为事件列表。

    行级识别 + [todo] 块处理（todo 块 = 一行 [todo] 后跟若干缩进行）。
    [reply] 流式增量（每 token 一行）聚合为一个 reply 事件：
    - print 固定输出 "[reply] {delta}"，去掉该固定分隔空格后原样保留 token；
    - 连续 [reply] 之间的空行视为回复内换行（不再把段落拆成多个 reply 事件）。
    - 增量读取时（flush_at_eof=False）若文本尾部仍是未结束的回复，不立即 flush，
      而是把 reply_buf 作为 pending 返回，交给下一次 poll 续接，避免一条回复被拆成多个事件。
    """
    events: list[dict] = []
    lines = text.splitlines()
    i = 0
    seq = 0
    skip_final_reply = False
    reply_buf: list[str] = list((pending or {}).get("reply_buf", []))
    pending_blanks = int((pending or {}).get("pending_blanks", 0))
    last_reply_json = bool((pending or {}).get("last_reply_json", False))  # 上一个 [reply] 行是否 JSON 编码（新格式）

    def _flush_reply() -> None:
        nonlocal seq, pending_blanks, last_reply_json
        if not reply_buf:
            pending_blanks = 0
            return
        joined = "".join(reply_buf).strip()
        reply_buf.clear()
        pending_blanks = 0
        last_reply_json = False
        if joined:
            events.append(_ev("reply", joined, seq)); seq += 1

    while i < len(lines):
        line = lines[i].rstrip("\r")
        stripped = line.strip()

        # 空行：如果当前正在聚合回复，先缓存为“回复内换行”，
        # 等下一行决定是继续 [reply]（插入换行）还是结束回复。
        if not stripped:
            if reply_buf:
                pending_blanks += 1
            i += 1
            continue

        # 旧格式回补：JSON 编码上线前，delta 内嵌换行会打出无 [reply] 前缀
        # 的裸行（如 markdown 的 "##"、"**加粗"）。回复聚合中遇到不以 "["
        # 开头的裸行视为回复续行（流式期间 stdout 只有本进程打印，真正的
        # 事件行都带 "[" 前缀）——否则一条回复被拆成多个事件，完成后尾部
        # 片段与磁盘历史前缀失配、残留成重复气泡（实测）。
        # 换行数 = 上一 [reply] 行自身行尾 1 个 + 中间空行 pending_blanks 个。
        if reply_buf and not stripped.startswith("["):
            reply_buf.append("\n" * (1 + pending_blanks))
            pending_blanks = 0
            reply_buf.append(line)
            i += 1
            continue

        # 非 [reply] 行：先收尾当前回复，再正常处理该行
        if not stripped.startswith("[reply]"):
            _flush_reply()

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
                _flush_reply()
                skip_final_reply = True
            i += 1
            continue
        elif stripped.startswith("[思考+]"):
            # 流式思考增量（agent.py 每个 reasoning delta 一行，JSON 编码
            # 防内嵌换行破坏行解析）。前端把相邻 thinking_delta 聚合为一段。
            _flush_reply()
            raw = _after(stripped, "[思考+]")
            if raw.startswith(" "):
                raw = raw[1:]
            try:
                frag = json.loads(raw)
                if not isinstance(frag, str):
                    frag = raw
            except ValueError:
                frag = raw
            events.append(_ev("thinking_delta", frag, seq)); seq += 1
        elif stripped.startswith("[思考]"):
            _flush_reply()
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
            # 流式回复增量（每个 token 一行）：连续行聚合，遇其他行收尾。
            # 新格式 JSON 编码（agent.py json.dumps，内嵌换行不破坏行结构）；
            # 旧格式裸文本兼容（空 token = 换行 token，delta 只有 \n 时
            # 打出 "[reply] "）。print 固定带一个分隔空格，去掉它。
            if pending_blanks > 0:
                # 旧格式：空行 = 回复内换行。上一 [reply] 行是 JSON 编码时，
                # 空行只是 print 自带行尾，丢弃（否则换行重复计数）
                if not last_reply_json:
                    reply_buf.append("\n" * pending_blanks)
                pending_blanks = 0
            # 必须用原始 line（而非 stripped）取内容：stripped 会去掉行尾空格，
            # 导致纯空格 token（如 "[reply]  "）被误判成换行 token。
            after_raw = line[line.index("[reply]") + len("[reply]"):]
            if after_raw.startswith(" "):
                after_raw = after_raw[1:]
            if after_raw == "":
                # 空token（旧格式换行 token）：不追加，print 自带换行形成
                # 后续空行，由 pending_blanks 统一换算成正确数量的 \n
                last_reply_json = False
            else:
                try:
                    frag = json.loads(after_raw)
                    last_reply_json = isinstance(frag, str)
                    if not isinstance(frag, str):
                        frag = after_raw
                except ValueError:
                    frag = after_raw
                    last_reply_json = False
                reply_buf.append(frag)
            i += 1
            continue
        elif stripped.startswith("[tool-result]"):
            _flush_reply()
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

    # 段末残留的流式回复：
    # - 全量读取（flush_at_eof=True）时直接 flush，保证完整回复能出事件；
    # - 增量读取时先缓存，交给下一次 poll 续接，避免一条回复被拆成多个事件。
    if flush_at_eof:
        _flush_reply()
        return events, None
    if reply_buf:
        return events, {
            "reply_buf": reply_buf,
            "pending_blanks": pending_blanks,
            "last_reply_json": last_reply_json,
        }
    return events, None



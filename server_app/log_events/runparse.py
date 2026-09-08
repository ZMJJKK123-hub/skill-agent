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


class _RunParser:
    """run.log 行解析状态机（由 _parse_run_block 巨函数拆出，逻辑逐字迁移）。

    类职责：逐行分发 [标记] 分支；维护流式回复聚合（reply_buf）、
    空行换行缓存、JSON 编码旗标、最终回复跳过与 todo/tool-result
    跨行块消费。
    类变量/实例属性：events/seq/reply_buf/pending_blanks/
    last_reply_json/skip_final_reply——见 __init__。
    生命周期：_parse_run_block 每段新建（pending 续接）。
    """

    def __init__(self, pending: dict | None):
        self.events: list[dict] = []
        self.seq = 0
        self.skip_final_reply = False
        self.reply_buf: list[str] = list((pending or {}).get("reply_buf", []))
        self.pending_blanks = int((pending or {}).get("pending_blanks", 0))
        self.last_reply_json = bool((pending or {}).get("last_reply_json", False))

    # ---------- 回复聚合 ----------

    def flush_reply(self) -> None:
        """收尾当前聚合中的回复为一个 reply 事件（空缓冲仅清计数）。"""
        if not self.reply_buf:
            self.pending_blanks = 0
            return
        joined = "".join(self.reply_buf).strip()
        self.reply_buf.clear()
        self.pending_blanks = 0
        self.last_reply_json = False
        if joined:
            self.events.append(_ev("reply", joined, self.seq)); self.seq += 1

    # ---------- 各标记分支（返回推进步数；默认 1）----------

    def on_blank(self) -> int:
        """空行：聚合中时缓存为回复内换行，由下一行决定去留。"""
        if self.reply_buf:
            self.pending_blanks += 1
        return 1

    def on_reply(self, line: str) -> int:
        """[reply] 流式增量：JSON 解析 + 空行换行折算。"""
        if self.pending_blanks > 0:
            # 旧格式：空行 = 回复内换行。上一行 JSON 编码时空行只是
            # print 自带行尾，丢弃（否则换行重复计数）
            if not self.last_reply_json:
                self.reply_buf.append("\n" * self.pending_blanks)
            self.pending_blanks = 0
        # 必须用原始 line（非 stripped）：纯空格 token 不能被误判成换行
        after_raw = line[line.index("[reply]") + len("[reply]"):]
        if after_raw.startswith(" "):
            after_raw = after_raw[1:]
        if after_raw == "":
            # 空 token（旧格式换行 token）：print 自带换行交由 pending_blanks 折算
            self.last_reply_json = False
        else:
            try:
                frag = json.loads(after_raw)
                self.last_reply_json = isinstance(frag, str)
                if not isinstance(frag, str):
                    frag = after_raw
            except ValueError:
                frag = after_raw
                self.last_reply_json = False
            self.reply_buf.append(frag)
        return 1

    def on_tool_result(self, stripped: str, lines: list[str], i: int) -> int:
        """[tool-result] 多行块：收集到下一个 [标记] 行或空行。"""
        self.flush_reply()
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
        self.events.append(_ev("tool_result", "\n".join(block), self.seq,
                               status=status)); self.seq += 1
        return j - i

    def on_todo(self, lines: list[str], i: int) -> int:
        """[todo] 块：收集后续缩进行（列表项）。"""
        block = []
        j = i + 1
        # 只收集缩进的行，遇到顶格行或空行停止
        while j < len(lines) and lines[j].startswith((" ", "\t")):
            block.append(lines[j].rstrip("\r"))
            j += 1
        self.events.append(_ev("todo", "\n".join(block), self.seq)); self.seq += 1
        return j - i

    def _feed_thinking(self, stripped: str) -> int | None:
        """思考标记族分发（[思考+]/[思考]/三类 peer 思考行）。

        Returns:
            推进步数；非思考标记返回 None（交回 feed 继续匹配）。
        """
        if stripped.startswith("[思考+]"):
            self.flush_reply()
            raw = _after(stripped, "[思考+]")
            if raw.startswith(" "):
                raw = raw[1:]
            try:
                frag = json.loads(raw)
                if not isinstance(frag, str):
                    frag = raw
            except ValueError:
                frag = raw
            self.events.append(_ev("thinking_delta", frag, self.seq)); self.seq += 1
            return 1
        if stripped.startswith("[思考]"):
            self.flush_reply()
            self.events.append(_ev("thinking", _after(stripped, "[思考]"), self.seq)); self.seq += 1
            return 1
        for peer in ("teammate", "subagent", "supervisor"):
            tag = f"[{peer} 思考]"
            if stripped.startswith(tag):
                self.events.append(_ev("thinking", _after(stripped, tag),
                                       self.seq, peer=peer)); self.seq += 1
                return 1
        return None

    def feed(self, lines: list[str], i: int) -> int:
        """处理一行，返回推进步数（跨行块可大于 1）。"""
        line = lines[i].rstrip("\r")
        stripped = line.strip()

        if not stripped:
            return self.on_blank()

        # 旧格式回补：回复聚合中的裸行（不以 [ 开头）视为回复续行——
        # 否则一条回复被拆多事件，尾部与磁盘历史前缀失配成重复气泡
        if self.reply_buf and not stripped.startswith("["):
            self.reply_buf.append("\n" * (1 + self.pending_blanks))
            self.pending_blanks = 0
            self.reply_buf.append(line)
            return 1

        # 非 [reply] 行：先收尾当前回复
        if not stripped.startswith("[reply]"):
            self.flush_reply()

        # 跳过"完成，最终回复:"及其后的正文（避免与流式重复显示）
        if self.skip_final_reply:
            if stripped.startswith("["):
                self.skip_final_reply = False
            else:
                return 1

        if stripped.startswith("[run_task]"):
            # 内部日志不展示；含"最终回复"则后续正文也跳过
            if "最终回复" in stripped:
                self.flush_reply()
                self.skip_final_reply = True
            return 1
        handled = self._feed_thinking(stripped)
        if handled is not None:
            return handled
        if stripped.startswith("[reply]"):
            return self.on_reply(line)
        if stripped.startswith("[tool-result]"):
            return self.on_tool_result(stripped, lines, i)
        if stripped.startswith("[tool]"):
            rest = _after(stripped, "[tool]")
            parts = rest.split(" ", 1)
            tool_name = parts[0] if parts else "tool"
            detail = parts[1] if len(parts) > 1 else ""
            self.events.append(_ev("tool_call", detail, self.seq, tool=tool_name)); self.seq += 1
            return 1
        for peer, tag in (("teammate", "[teammate:"), ("subagent", "[subagent:"),
                          ("supervisor", "[supervisor:")):
            if stripped.startswith(tag) and "]" in stripped:
                name, rest = _split_tag(stripped)
                self.events.append(_ev("tool_call", _after(rest, "]"), self.seq,
                                       tool=name, peer=peer)); self.seq += 1
                return 1
        if stripped == "[todo]":
            return self.on_todo(lines, i)
        self.events.append(_ev("log", stripped, self.seq)); self.seq += 1
        return 1

    def to_pending(self) -> dict | None:
        """段末残留的流式回复 → 下一次 poll 续接的 pending（无残留 None）。"""
        if self.reply_buf:
            return {
                "reply_buf": self.reply_buf,
                "pending_blanks": self.pending_blanks,
                "last_reply_json": self.last_reply_json,
            }
        return None


def _parse_run_block(text: str, pending: dict | None = None, flush_at_eof: bool = True) -> tuple[list[dict], dict | None]:
    """把 run.log 的一段新增文本解析为事件列表（状态机类 _RunParser）。

    Args:
        text: 新增文本段。
        pending: 上次增量留下的未完回复（reply_buf 续接）。
        flush_at_eof: 全量读取 True（段末强制收尾回复）；增量 False。
    Returns:
        (事件列表, 续接 pending 或 None)。
    """
    parser = _RunParser(pending)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        i += parser.feed(lines, i)
    if flush_at_eof:
        parser.flush_reply()
        return parser.events, None
    return parser.events, parser.to_pending()

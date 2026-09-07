# -*- coding: utf-8 -*-
"""run.log 协议写入器（infrastructure 层，EventWriter 的正式实现）。

行为契约（决策 1：协议保持）——输出行与旧 core/agent.py 的 print
逐字节一致，前端 log_events 解析零改动：
    reply_delta    → ``[reply] "<json>"``          （json 编码保证单行）
    thinking_delta → ``[思考+] "<json>"``          （同上）
    tool_call      → ``[tool] <名> <参数展示>``
    tool_result    → ``[tool-result] success|failed\\n<输出>``
    todo           → ``\\n[todo]\\n<清单>``        （历史行为：不 flush）
    notice         → ``[run_task] <文本>``
"""
from __future__ import annotations

import io
import json
import sys
from typing import TextIO

from ...interfaces.event_writer import EventWriter


class RunlogEventWriter(EventWriter):
    """把过程事件按 run.log 文本协议写到输出流。

    类职责：替代旧代码里散落的 print；流缺省动态解析 sys.stdout
    （run_task 子进程的 stdout 由 server 重定向到 run.log，构造期
    捕获会拿到错误的目标，必须每次调用时解析）。
    类变量/实例属性：
        _stream: TextIO | None — 显式注入的流（测试捕获用）；
        None 表示运行期动态取 sys.stdout。
    生命周期：bootstrap 每进程构建一个，随进程存活。
    """

    def __init__(self, stream: TextIO | None = None) -> None:
        """输入：可选注入流（测试）。返回：无。职责：仅记流引用，不打开资源。"""
        self._stream = stream

    def _out(self) -> TextIO:
        """输入：无。返回：当前应写入的流（显式注入优先，否则 sys.stdout）。"""
        return self._stream if self._stream is not None else sys.stdout

    def _emit(self, line: str, *, flush: bool = True) -> None:
        """输入：完整行内容 + 是否立即刷出。返回：无。职责：单点写行。"""
        out = self._out()
        try:
            out.write(line + "\n")
            if flush:
                out.flush()
        except (OSError, ValueError):
            # run.log 句柄被关闭（进程收尾竞态）——事件流是尽力而为的
            # 旁路通道，不因此打断引擎主流程；记录到 stderr 供排障。
            try:
                sys.stderr.write(f"[runlog] write failed: {line[:120]!r}\n")
            except (OSError, ValueError):
                pass

    def reply_delta(self, text: str) -> None:
        """写回复增量（json 编码：delta 内嵌换行不破坏行协议）。"""
        self._emit(f"[reply] {json.dumps(text, ensure_ascii=False)}")

    def thinking_delta(self, text: str) -> None:
        """写思考增量（前端聚合相邻 [思考+] 行为一段）。"""
        self._emit(f"[思考+] {json.dumps(text, ensure_ascii=False)}")

    def tool_call(self, name: str, args_display: str) -> None:
        """写工具调用行（args_display 已由调用方格式化，bash 为命令本身）。"""
        self._emit(f"[tool] {name} {args_display}")

    def tool_result(self, ok: bool, output: str) -> None:
        """写工具结果行（首行 success/failed，正文原样多行）。"""
        self._emit(f"[tool-result] {'success' if ok else 'failed'}\n{output}")

    def todo(self, output: str) -> None:
        """写完整 todo 清单（保持旧 print 的非 flush 行为）。"""
        self._emit(f"\n[todo]\n{output}", flush=False)

    def notice(self, text: str) -> None:
        """写系统提示行（构建进度/收尾信息等）。"""
        self._emit(f"[run_task] {text}")

    def debug_line(self, text: str) -> None:
        """原样写一行调试输出（[round] 快照等）。"""
        self._emit(text)


class MemoryEventWriter(EventWriter):
    """捕获全部事件到内存列表的测试替身（断言协议行用）。

    类变量/实例属性：lines: list[str] — 按序收集的输出行。
    生命周期：仅存在于单测，随用例丢弃。
    """

    def __init__(self) -> None:
        """输入：无。返回：无。职责：初始化行收集缓冲。"""
        self.lines: list[str] = []
        self._buf = io.StringIO()

    def _emit(self, line: str) -> None:
        """输入：完整行。返回：无。职责：同时记入缓冲与行列表。"""
        self._buf.write(line + "\n")
        self.lines.append(line)

    def reply_delta(self, text: str) -> None:
        """输入：回复增量。返回：无。职责：按协议格式记录。"""
        self._emit(f"[reply] {json.dumps(text, ensure_ascii=False)}")

    def thinking_delta(self, text: str) -> None:
        """输入：思考增量。返回：无。职责：按协议格式记录。"""
        self._emit(f"[思考+] {json.dumps(text, ensure_ascii=False)}")

    def tool_call(self, name: str, args_display: str) -> None:
        """输入：工具名 + 参数展示。返回：无。职责：按协议格式记录。"""
        self._emit(f"[tool] {name} {args_display}")

    def tool_result(self, ok: bool, output: str) -> None:
        """输入：成败 + 输出。返回：无。职责：按协议格式记录。"""
        self._emit(f"[tool-result] {'success' if ok else 'failed'}\n{output}")

    def todo(self, output: str) -> None:
        """输入：todo 清单。返回：无。职责：按协议格式记录。"""
        self._emit(f"\n[todo]\n{output}")

    def notice(self, text: str) -> None:
        """输入：提示文本。返回：无。职责：按协议格式记录。"""
        self._emit(f"[run_task] {text}")

    def debug_line(self, text: str) -> None:
        """输入：任意调试行。返回：无。职责：原样记录。"""
        self._emit(text)

    @property
    def text(self) -> str:
        """输入：无。返回：全部输出拼接的全文（对比快照用）。"""
        return self._buf.getvalue()

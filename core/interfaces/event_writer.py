# -*- coding: utf-8 -*-
"""run.log 事件写入抽象（interfaces 层）。

背景：agent 子进程的 stdout 被 run_task 重定向到 run.log，前端
/api/events 由 log_events 解析这些文本行——print 语句本身就是
跨进程协议。agent.md Rule 2 禁 print，因此把协议收敛为本接口；
实现 RunlogEventWriter 输出与旧格式逐字节一致的行（决策 1：
协议保持不变，前端零改动）。
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EventWriter(Protocol):
    """向 run.log 协议通道写入过程事件的抽象。

    类职责：替代散落各处的 print；协议行格式固定为——
        reply_delta   → ``[reply] <json字符串>``
        thinking_delta→ ``[思考+] <json字符串>``
        tool_call     → ``[tool] <名> <参数展示>``
        tool_result   → ``[tool-result] success|failed\\n<输出>``
        todo          → ``\\n[todo]\\n<清单>``
        notice        → ``[run_task] <文本>``
    方法调用逻辑：全部即时写入（todo 例外：保持旧实现的非 flush 行为）。
    """

    def reply_delta(self, text: str) -> None:
        """写入一个回复文本增量（json 编码保证单行）。"""
        ...

    def thinking_delta(self, text: str) -> None:
        """写入一个思考文本增量（流式思考，前端聚合成段）。"""
        ...

    def tool_call(self, name: str, args_display: str) -> None:
        """写入一次工具调用（bash 时 args_display 为命令本身）。"""
        ...

    def tool_result(self, ok: bool, output: str) -> None:
        """写入一次工具执行结果（ok=False 时行首为 failed）。"""
        ...

    def todo(self, output: str) -> None:
        """写入完整 todo 清单（终端正文的友好展示）。"""
        ...

    def notice(self, text: str) -> None:
        """写入系统提示行（构建进度/收尾信息等用户可见状态）。"""
        ...

    def debug_line(self, text: str) -> None:
        """原样写入一行调试输出（[round] 快照等；格式由调用方决定）。"""
        ...

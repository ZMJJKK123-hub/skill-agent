# -*- coding: utf-8 -*-
"""主循环状态：全部轮内可变量的显式收编（services/loop 层）。

旧 core/agent.py 把 20+ 个局部变量内联在 830 行巨函数里；
本类逐项收编（字段名与旧局部一一对应，注释标注旧名），
让守卫/闸的计数可单测、可观测。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from ...domain.messages import Message

if TYPE_CHECKING:  # 仅类型标注，避免运行期循环导入
    from .step_machine import TurnStepMachine


@dataclass
class LoopState:
    """一次 agent_loop 运行的全部可变状态。

    类职责：集中持有消息列表与所有守卫/闸计数器；只做存取不做逻辑。
    实例属性（旧名 → 字段）：
        messages — messages：类型化消息历史（循环内唯一事实源）
        round_idx — _round_idx：当前轮号（从 1 起）
        round_tool_counts — _round_tool_counts：本轮各工具调用次数
        known_issues_injected — _known_issues_injected：首轮注入旗标
        agents_injected — _agents_injected：AGENTS.md 首轮注入旗标
        wrote_file — _wrote_file：是否已写 src/main|test Java
        existing_java — _existing_java：启动时已存在自写 Java
        pre_write_reads — _pre_write_reads：写前研究计数
        pre_write_warned — _pre_write_warned：写前提醒去重旗标
        starter_auto_written — _starter_auto_written：starter 已自动写入
        skeleton_written — _skeleton_written：最小骨架已自动写入
        write_strikes — _write_strikes：写前预算违约次数
        post_write_research — _post_write_research：写后研究计数
        no_tool_strikes — _no_tool_strikes：出口闸空转次数
        empty_strikes — _empty_strikes：连续空响应计数（5→压缩/8→强制收尾）
        tool_rounds — _tool_rounds：工具调用轮计数（上限 200）
        gametest_rejects — _gametest_rejects：GameTest 闸连续打回计数
        rounds_since_todo — rounds_since_todo：距上次 todo 的轮数
        gate_round — _gate_round：完成闸首次触发轮号（宽限基准）
        force_final_msg — _force_final_msg：强制收尾文本（非空即收）
        compact_pending — compact_pending：compact 工具延后执行旗标
        synced_count — _synced_count：已同步进事件源的消息数
    生命周期：runner.run() 开头创建，退出即弃。
    """

    messages: list[Message] = field(default_factory=list)
    round_idx: int = 0
    round_tool_counts: dict[str, int] = field(default_factory=dict)
    known_issues_injected: bool = False
    agents_injected: bool = False
    wrote_file: bool = False
    existing_java: bool = False
    pre_write_reads: int = 0
    pre_write_warned: bool = False
    starter_auto_written: bool = False
    skeleton_written: bool = False
    write_strikes: int = 0
    post_write_research: int = 0
    no_tool_strikes: int = 0
    empty_strikes: int = 0
    tool_rounds: int = 0
    gametest_rejects: int = 0
    rounds_since_todo: int = 0
    gate_round: Optional[int] = None
    force_final_msg: Optional[str] = None
    compact_pending: bool = False
    synced_count: int = 0
    # 轮内局部量（旧实现为循环体局部变量；守卫/出口需要读，提升为字段）
    used_todo: bool = False
    concluded_output: Optional[str] = None
    step_machine: Optional["TurnStepMachine"] = None

    def begin_round(self) -> None:
        """输入：无。返回：无。职责：进入下一轮（轮号+1、轮内量清零）。"""
        self.round_idx += 1
        self.round_tool_counts = {}
        self.used_todo = False
        self.concluded_output = None
        self.compact_pending = False

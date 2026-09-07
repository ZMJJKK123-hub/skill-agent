# -*- coding: utf-8 -*-
"""主循环编排（services/loop 层）：AgentLoopEngine。

对应旧 core/agent.py 的 agent_loop 巨型函数，按五阶段重组：
    每轮：强制收尾检查 → 注入层 → 事件源同步 → 模型调用 →
    （非工具轮）出口层 /（工具轮）工具批 + 守卫瀑布。
行为以 main 分支旧实现为唯一平价基准（含 9 项 src/engine 教训项）。
"""
from __future__ import annotations

import json
from pathlib import Path

from ...domain.messages import Message
from ...infrastructure.logging_.logger import get_logger
from ..compaction import estimate_tokens
from ..session_log import (SessionLog, persist, repair_missing_tool_results, 
                           restore, sync_messages)
from .deps import LoopDeps
from .exits import finish_forced, no_tool_exit
from .guards import apply_repeat_tool_reminder
from .injections import INJECTORS, inject_runtime_context
from .model_call import ModelCallService
from .profiles import ModeProfile, profile_for
from .skills_rolling import move_skills_to_end
from .state import LoopState
from .step_machine import TurnStepMachine
from .tool_batch import execute_batch

logger = get_logger("loop.runner")

#: 每轮调试快照的落盘路径（相对 cwd）。
DEBUG_SNAPSHOT = Path(".chat") / "debug" / "round_messages.jsonl"


class AgentLoopEngine:
    """agent 主循环引擎。

    类职责：按 profile 驱动五阶段循环直至出口；不持有业务分支判断
    （全部下沉到 injections/guards/exits/profiles）。
    实例属性：
        _deps: LoopDeps — 全部依赖。
        _profile: ModeProfile — 模式行为声明。
        _calls: ModelCallService — 模型调用子服务。
    生命周期：bootstrap 构建；run() 一次一个 turn（daemon 模式下
    进程常驻、逐 turn 复用引擎实例）。
    """

    def __init__(self, deps: LoopDeps) -> None:
        """输入：依赖容器。返回：无。职责：装配子服务与模式策略。"""
        self._deps = deps
        self._profile: ModeProfile = profile_for(deps.ctx.mode)
        self._calls = ModelCallService()

    # ---------- 准备 ----------

    def _prepare(self, state: LoopState) -> None:
        """工作区自愈、监管启动、空历史重放、turn 开启（一次）。"""
        deps = self._deps
        deps.workspace_ensurer()
        if self._profile.is_mod:
            deps.supervisor.start()
        if not state.messages:
            restored = restore()
            if restored is not None:
                deps.session_log.events.extend(restored.events)
                deps.session_log._seq = restored._seq
                state.messages = restored.derive_messages()
                logger.info("从 SessionLog 恢复 %d 条消息", len(state.messages))
        state.step_machine = TurnStepMachine(deps.session_log)
        state.step_machine.start_turn()

    # ---------- 主循环 ----------

    def run(self, messages: list[Message]) -> str:
        """执行一个 turn（直到出口），返回面向用户的最终回复。

        Args:
            messages: 初始消息（空列表时从事件日志重放）。
        Returns:
            最终回复文本（与旧 agent_loop 返回值语义一致）。
        """
        state = LoopState(messages=messages)
        state.existing_java = self._has_custom_java()
        self._prepare(state)
        while True:
            state.begin_round()
            if state.force_final_msg is not None:
                return finish_forced(state, self._deps)
            self._inject(state)
            self._sync(state)
            state.step_machine.start_step()
            persist(self._deps.session_log)
            self._dump_round(state)
            move_skills_to_end(state.messages)
            outcome = self._calls.call(state, self._deps)
            if outcome.retry:
                continue
            message = outcome.message
            state.messages.append(message)
            if outcome.finish_reason == "length":
                state.step_machine.record_max_tokens()
            logger.info("finish_reason=%s", outcome.finish_reason)
            if outcome.finish_reason != "tool_calls":
                final = no_tool_exit(state, self._deps, message)
                if final is not None:
                    return final
                continue
            self._run_tools(state, message)
            if self._run_guards(state):
                continue

    @staticmethod
    def _has_custom_java() -> bool:
        """输入：无。返回：cwd 是否已有非模板自写 Java（预算守卫依据）。"""
        from ...infrastructure.autowrite import has_custom_java
        return has_custom_java()

    def _inject(self, state: LoopState) -> None:
        """输入：无。返回：无。职责：按序执行全部注入器 + 运行时快照。"""
        for injector in INJECTORS:
            injector(state, self._deps)
        inject_runtime_context(state, self._deps)

    def _sync(self, state: LoopState) -> None:
        """事件源同步 + 崩溃修复（DSH derive/repair 不变量）。"""
        log = self._deps.session_log
        state.synced_count = sync_messages(log, state.messages, state.synced_count)
        state.messages = repair_missing_tool_results(log, state.messages)
        state.synced_count = sync_messages(log, state.messages, state.synced_count)

    def _run_tools(self, state: LoopState, message) -> None:
        """工具批执行 + post-step 提醒 + step 收口。"""
        batch = execute_batch(state, self._deps, message)
        state.compact_pending = batch.compact_pending
        state.used_todo = batch.used_todo
        state.concluded_output = batch.concluded_output
        apply_repeat_tool_reminder(state, self._deps)
        state.step_machine.end_step(reason="completed")

    def _run_guards(self, state: LoopState) -> bool:
        """守卫瀑布；任一守卫触发即结束本轮（True=continue）。"""
        for guard in self._profile.guards:
            if guard(state, self._deps):
                return True
        return False

    # ---------- 调试快照 ----------

    def _dump_round(self, state: LoopState) -> None:
        """每轮调试快照：[round] 概览行 + 逐消息行 + JSONL 落盘。"""
        deps = self._deps
        try:
            tokens = estimate_tokens(state.messages)
            counts = ", ".join(f"{k}:{v}" for k, v in sorted(state.round_tool_counts.items()))
            deps.writer.debug_line(
                f"\n[round] #{state.round_idx} messages={len(state.messages)} "
                f"tokens≈{tokens} tools=[{counts}]")
            for i, m in enumerate(state.messages):
                content = m.content if isinstance(m.content, str) else ""
                preview = content[:180].replace("\n", "\\n")
                tc_note = f" tool_calls={len(m.tool_calls)}" if getattr(m, "tool_calls", None) else ""
                deps.writer.debug_line(
                    f"  [{i}] {m.role}{tc_note} len={len(content)} | {preview}")
            record = {"round": state.round_idx, "tokens": tokens,
                      "tool_counts": state.round_tool_counts,
                      "messages": [{"role": m.role,
                                    "content": (m.content if isinstance(m.content, str) else "")[:5000],
                                    "tool_call_ids": [tc.call_id for tc in (getattr(m, "tool_calls", None) or [])]}
                                   for m in state.messages]}
            DEBUG_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
            with DEBUG_SNAPSHOT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("round dump failed: %s", e)

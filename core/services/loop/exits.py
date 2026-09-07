# -*- coding: utf-8 -*-
"""出口层（services/loop 层）：非工具调用轮的处置与收尾。

覆盖旧 agent.py 的三段出口逻辑：
    1. 队友仍在工作 → 注入提醒继续等（不退出）；
    2. chat 模式 → 纯文本即出口，直接返回；
    3. mod 模式 → GameTest 强制核查（闸）→ 打回兜底 → 自然收尾
       （构建 jar + 预生成 zip + 停监管）。
另含强制收尾（force_final）的统一出口（补建产物）。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ...domain.messages import AssistantMessage, Message, ToolResultMessage, UserMessage
from ...domain.session import Mode
from ...infrastructure.logging_.logger import get_logger
from ..session_log import persist
from .deps import LoopDeps
from .slots import replace_runtime_slot
from .state import LoopState

logger = get_logger("loop.exits")

#: GameTest 自检工具（出现于 assistant.tool_calls 即视为"实际跑过"的证据来源）。
GT_TOOL_NAMES = {"run_test_gametest", "run_game_test_server", "run_mod_test_cycle"}


def no_tool_exit(state: LoopState, deps: LoopDeps,
                 message: AssistantMessage) -> Optional[str]:
    """模型不再调用工具时的出口处置。

    Args:
        state: 循环状态。
        deps: 依赖容器。
        message: 本轮 assistant 消息（最终回复载体）。
    Returns:
        最终回复字符串（引擎应立即返回）；None 表示打回继续循环。
    """
    state.step_machine.end_step(reason="completed")
    working = deps.teammates.working_names()
    if working:
        logger.info("模型想退出但队友仍在工作: %s | 注入提醒", working)
        replace_runtime_slot(state.messages, "reminder", (
            f"<reminder>Teammates still working: {', '.join(working)}. "
            f"Wait for their reports before finishing.</reminder>"))
        return None
    logger.info("循环结束，最终回复:\n%s", message.content)
    if deps.ctx.mode == Mode.CHAT:
        return finalize_chat(state, deps, message)
    ok, forced = _gametest_gate(state, deps, message)
    state.gametest_rejects += 1
    if not ok:
        if forced is not None:
            return forced  # 打回 ≥3 且 dist 有产物 → 强制收尾防无限循环
        return None
    return finalize_mod(state, deps, message)


# ---------- GameTest 出口闸 ----------

def _has_gametest_source() -> bool:
    """输入：无。返回：src/test/java 下是否存在 @GameTest 注解（只扫自写测试）。"""
    root = Path.cwd() / "src" / "test" / "java"
    if not root.exists():
        return False
    for fp in root.rglob("*.java"):
        try:
            if "@GameTest" in fp.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            continue
    return False


def _ran_gametest(state: LoopState) -> bool:
    """输入：无。返回：是否实际调用过 GameTest 工具且结果含通过/执行标记。"""
    call_ids = {tc.call_id for m in state.messages
                if isinstance(m, AssistantMessage)
                for tc in (m.tool_calls or []) if tc.name in GT_TOOL_NAMES}
    for m in state.messages:
        if (isinstance(m, ToolResultMessage) and m.tool_call_id in call_ids
                and isinstance(m.content, str)):
            c = m.content
            if (c.lstrip().startswith("[gametest]")
                    or "All required tests passed" in c
                    or "GAME TESTS COMPLETE" in c
                    or "RESULT: PASS" in c):
                return True
    return False


def _gametest_gate(state: LoopState, deps: LoopDeps,
                   message: AssistantMessage) -> tuple[bool, Optional[str]]:
    """GameTest 强制核查：未跑通不得宣布完成。

    Returns:
        (ok, forced)：ok=True 通过；ok=False 且 forced 非 None → 引擎
        应立即返回 forced（打回兜底）；ok=False 且 forced=None → 打回继续。
    """
    if _has_gametest_source() and _ran_gametest(state):
        return True, None
    state.messages.append(UserMessage(content=(
        "<gametest-check> FAILED: 你尚未完成 GameTest 自循环验证（需要：①在 src/test/java 编写至少一个 @GameTest 测试类；"
        "②调用 run_test_gametest 运行测试（扫描 src/test；禁止用 run_game_test_server 自检——它只扫 src/main）；"
        "③可用 read_game_test_log 查看日志）。"
        "按 skill-first 纪律，未跑通 GameTest 不得宣布 MOD 完成。请先补测试并运行，通过后再结束。")))
    state.messages.append(UserMessage(content=(
        "<tool-call-required> 任务未完成，禁止只输出纯文本。你必须立即调用一个工具："
        "write_file / edit_file / build_mod_jar_forge / run_test_gametest / run_mod_test_cycle / validate_resources。"
        "不要回复“No additional output”之类的话。</tool-call-required>")))
    state.no_tool_strikes += 1
    if state.no_tool_strikes >= 2:
        logger.warning("连续空转，自动调用 build_mod_jar_forge 推进")
        try:
            auto = deps.jar_builder()
        except Exception as e:  # 构建失败也回填文本，让模型看到错误继续修
            auto = f"Error: auto build failed: {e}"
        state.messages.append(ToolResultMessage(
            tool_call_id=f"auto-{os.urandom(4).hex()}", content=auto))
        state.no_tool_strikes = 0
    logger.info("gametest-check FAILED + tool-call-required 注入")
    if state.gametest_rejects + 1 >= 3:
        jars = _dist_jars()
        if jars:
            logger.warning("GameTest 打回 ≥3 次但 dist 已有产物，强制收尾防无限循环")
            _stop_turn(state, deps)
            deps.supervisor.stop()
            note = ((message.content or "")
                    + f"\n\n[system] GameTest 校验连续 {state.gametest_rejects + 1} 次未通过判定，"
                    f"但 dist/{jars[0]} 已生成（此前曾报告 GameTest 通过），已强制收尾，请人工复核。")
            return False, note
    return False, None


def _dist_jars() -> list[str]:
    """输入：无。返回：dist 下非模板 jar 文件名列表。"""
    try:
        dist = Path.cwd() / "dist"
        if dist.is_dir():
            return [f.name for f in dist.iterdir()
                    if f.name.endswith(".jar") and "examplemod" not in f.name]
    except OSError as e:
        logger.warning("dist 扫描失败: %s", e)
    return []


# ---------- 收尾 ----------

def _stop_turn(state: LoopState, deps: LoopDeps) -> None:
    """输入：无。返回：无。职责：统一停转（complete turn + 落盘事件日志）。"""
    state.step_machine.complete_turn()
    persist(deps.session_log)


def _build_artifacts(deps: LoopDeps) -> None:
    """收尾补建产物（jar + zip 预生成；非 Gradle 工程跳过并记日志）。"""
    gradlew = Path.cwd()
    has_gradle = ((gradlew / "gradlew.bat").exists()
                  or (gradlew / "gradlew").exists())
    if has_gradle and (gradlew / "build.gradle").exists():
        deps.writer.notice("开始构建 mod jar（首次构建需数分钟）...")
        try:
            deps.writer.notice(deps.jar_builder()[:3000])
        except Exception as e:
            logger.warning("收尾 jar 构建跳过: %s", e)
    else:
        logger.info("非 Gradle/Forge 工程，跳过 jar 构建")
    try:
        deps.writer.notice(deps.zip_builder())
    except Exception as e:
        logger.warning("收尾 zip 预生成跳过: %s", e)


def finalize_chat(state: LoopState, deps: LoopDeps,
                  message: AssistantMessage) -> str:
    """chat 出口：直接返回文本（不核查 GameTest、不构建产物）。"""
    _stop_turn(state, deps)
    return message.content or ""


def finalize_mod(state: LoopState, deps: LoopDeps,
                 message: AssistantMessage) -> str:
    """mod 自然收尾：构建 jar → 预生成 zip → 停监管 → 返回回复。"""
    _build_artifacts(deps)
    deps.supervisor.stop()
    _stop_turn(state, deps)
    return message.content or ""


def finish_forced(state: LoopState, deps: LoopDeps) -> str:
    """强制收尾（守卫触发）：补齐产物后返回 force_final 文本。"""
    logger.warning("%s", state.force_final_msg)
    _stop_turn(state, deps)
    if deps.ctx.mode == Mode.MOD:
        deps.supervisor.stop()
        _build_artifacts(deps)
    return state.force_final_msg or ""


def summarize_completion(deps: LoopDeps, messages: list[Message],
                         fallback: str) -> str:
    """让模型做一次无工具的最终总结（用户可见回复）。

    直接返回闸的系统文本会让"最终回复"变成内部指令串（718d315bec0b
    实测教训）；失败/空回复时回退 fallback。
    """
    instruction = UserMessage(content=(
        "[system] 任务完成判定已满足（dist jar 存在且 GameTest 通过）。"
        "请立即输出面向用户的最终总结，不要再调用任何工具。内容包含："
        "创建/修改了哪些文件、MOD 功能与关键数值、合成配方、"
        "如何安装使用、已完成的验证。"))
    try:
        text = deps.client.complete_chat(
            deps.system_provider(), messages + [instruction], max_tokens=4000)
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.warning("完成总结调用失败，回退闸文本: %s", e)
    return fallback

# -*- coding: utf-8 -*-
"""轮首注入层（services/loop 层）。

按旧 core/agent.py 循环头部的固定顺序，把 11 类上下文注入器
收编为 INJECTORS 序列（策略表替代 if-continue 瀑布，Rule 2.6.2）。
顺序即语义：监管信息先于后台通知/队友汇报进入上下文。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from ...domain.messages import AssistantMessage, Message, UserMessage
from ...domain.session import Mode
from ...infrastructure.logging_.logger import get_logger
from ..compaction import estimate_tokens
from .deps import LoopDeps
from .slots import replace_runtime_slot
from .state import LoopState

logger = get_logger("loop.injections")

Injector = Callable[[LoopState, LoopDeps], None]


def _messages_hint_mod(messages: list[Message]) -> bool:
    """输入：消息列表。返回：是否明显提及 MOD/模组/Forge（目录注入条件）。"""
    pattern = (r"(?i)(/mod|(?<![a-z])mod(?![a-z])|模组|mod制作"
               r"|我的世界.*(?:mod|模组)|forge)")
    for m in messages:
        if isinstance(m, UserMessage):
            if re.search(pattern, m.content):
                return True
    return False


def inject_supervisor(state: LoopState, deps: LoopDeps) -> None:
    """排空监管信箱（advice/alert 分级标签）并计轮（仅 mod）。"""
    if deps.ctx.mode != Mode.MOD:
        return
    advice = deps.supervisor.drain_advice()
    if advice:
        blocks = []
        for item in advice:
            tag = "supervisor-alert" if item.get("type") == "alert" else "supervisor-advice"
            blocks.append(f"<{tag}>\n{item.get('content', '')}\n</{tag}>")
        replace_runtime_slot(state.messages, "supervisor", "\n".join(blocks))
        logger.info("注入监管信息 type=%s", [a.get("type") for a in advice])
    deps.supervisor.notify_round()


def inject_checkpoint_and_interjections(state: LoopState, deps: LoopDeps) -> None:
    """断点落盘 + 运行中插话注入（daemon 模式 defer 旗标下跳过中途注入）。"""
    deps.store.save_checkpoint(state.messages)
    if deps.settings.loop.defer_drain:
        return  # daemon 逐条消费，一轮一条（问一条答一条）
    pending = deps.store.drain_pending_all()
    if not pending:
        return
    existing = {(m.role, m.content) for m in state.messages
                if isinstance(m, (UserMessage, AssistantMessage))}
    added = 0
    for msg in pending:
        key = ("user", msg.content)
        if key in existing:
            logger.info("跳过重复注入的排队消息: %s", msg.content[:40])
            continue
        content = f"[用户追加的排队消息] {msg.content}" if msg.content else msg.content
        state.messages.append(UserMessage(content=content, images=msg.images))
        existing.add(key)
        added += 1
    if added:
        logger.info("注入 %d 条运行中用户插入消息", added)


def inject_skill_catalog(state: LoopState, deps: LoopDeps) -> None:
    """技能目录 digest 注入（mod 恒注入；chat 仅在提及 MOD 时注入）。"""
    ws = deps.settings.workspace
    if ws.skill_catalog_disabled:
        return
    if deps.ctx.mode == Mode.MOD or _messages_hint_mod(state.messages):
        deps.skill_catalog_injector(state.messages)


def inject_background(state: LoopState, deps: LoopDeps) -> None:
    """排空后台任务通知（在 compact 之前注入，作为新数据参与估算）。"""
    notifications = deps.background.drain_notifications()
    if notifications:
        text = deps.background.format_results(notifications)
        replace_runtime_slot(state.messages, "background-results", text)
        logger.info("注入后台通知")


def inject_teammate_reports(state: LoopState, deps: LoopDeps) -> None:
    """排空 leader 收件箱（队友完成结果 → <teammate-reports>）。"""
    msgs = deps.teammates.read_leader_inbox()
    if msgs:
        parts = ["<teammate-reports>"]
        for m in msgs:
            parts.append(f"[from {m.get('from')}]\n{m.get('content')}")
        parts.append("</teammate-reports>")
        replace_runtime_slot(state.messages, "teammate-reports", "\n".join(parts))
        logger.info("注入队友汇报")


def _known_issues_text() -> str:
    """输入：无。返回：首轮强制注入的开工指令文本（含 CLIENT_VERIFY 路径）。"""
    repo_root = Path(__file__).resolve().parents[3]
    return (
        "<mandatory-first-step> 开工前必须先 run_read KNOWN_ISSUES.md "
        "（mod 工程根目录的事实来源，优先级高于技能描述）。读完按其中适用条目执行，"
        "尤其注意：GameTest 自检必须用 run_test_gametest（扫描 src/test/java），"
        "禁止用 run_game_test_server 做自检。未读取前不要写任何代码/资源。\n"
        "【写前查坑，强制】写任何 Java 文件之前，必须先用一次 grep 在 "
        "docs/agent/ERROR_LIST.md 里检索你即将用到的注册常量与关键 API 名"
        "（例如 BLOCK_ENTITY_TYPE、blit、makeMockPlayer、useWithoutItem、"
        "Registries 常量、MenuScreens 等），已有条目直接照修复写，不要等编译报错才查——"
        "c43424752e7d 实测：同族坑已入库仍被写出，三连 FAIL 才修完。\n"
        "如果本 MOD 涉及自定义实体、刷怪蛋或物品图标，你还必须 run_read "
        f"{repo_root / 'docs' / 'agent' / 'CLIENT_VERIFY.md'} "
        "（客户端验证指导，服务器/GameTest 发现不了客户端渲染与图标问题），"
        "并在完成前按其中固定流程执行客户端验证；未满足客户端验证不得宣布完成。</mandatory-first-step>"
    )


def inject_known_issues(state: LoopState, deps: LoopDeps) -> None:
    """首轮强制注入 KNOWN_ISSUES 开工指令（仅 mod；chat 无模板会绕圈）。"""
    if deps.ctx.mode == Mode.MOD and not state.known_issues_injected:
        state.known_issues_injected = True
        state.messages.append(UserMessage(content=_known_issues_text()))


def inject_agents_md(state: LoopState, deps: LoopDeps) -> None:
    """首轮注入工作区 AGENTS.md（模板带来的项目硬事实）。"""
    if deps.ctx.mode == Mode.MOD and not state.agents_injected:
        state.agents_injected = True
        path = Path.cwd() / "AGENTS.md"
        if path.exists():
            try:
                text = path.read_text(encoding="utf-8")
                replace_runtime_slot(
                    state.messages, "agents-instructions",
                    f"<agents-instructions>\n{text}\n</agents-instructions>")
                logger.info("已注入 AGENTS.md 工作区指令")
            except OSError as e:
                logger.warning("AGENTS.md 注入失败: %s", e)


def inject_protocol(state: LoopState, deps: LoopDeps) -> None:
    """注入 <pending-requests> 协议块（待审批计划/已决议结果）。"""
    deps.protocol.inject_pending("leader", state.messages)


def inject_auto_compact(state: LoopState, deps: LoopDeps) -> None:
    """token 超阈值自动压缩（事件源记 compaction；消息列表整体替换）。"""
    tokens = estimate_tokens(state.messages)
    if tokens <= deps.compaction.token_threshold:
        return
    logger.info("auto_compact 触发 | token=%d > 阈值 %d",
                tokens, deps.compaction.token_threshold)
    before_seq = max((e.seq for e in deps.session_log.events), default=0)
    state.messages = deps.compaction.auto_compact(state.messages)
    summary = next((m.content for m in state.messages
                    if isinstance(m, UserMessage)
                    and "[Context compacted" in m.content), "")
    deps.session_log.add_compaction(summary, 1, before_seq)
    state.synced_count = 0  # 新列表从头重新同步事件源


#: 固定注入顺序（与旧循环头部 Layer 0s→2 的次序一致）。
INJECTORS: tuple[Injector, ...] = (
    inject_supervisor,
    inject_checkpoint_and_interjections,
    inject_skill_catalog,
    inject_background,
    inject_teammate_reports,
    inject_known_issues,
    inject_agents_md,
    inject_protocol,
    inject_auto_compact,
)


def inject_runtime_context(state: LoopState, deps: LoopDeps) -> None:
    """pre-step 注入 <runtime-context> 快照（UTC 时间 + todo + 任务板）。

    替代旧 agent_hooks._inject_runtime_context_snapshot（全局 hook 注册表），
    文本格式与旧实现一致。
    """
    parts = []
    from datetime import datetime, timezone
    parts.append("Current time (UTC): "
                 + datetime.now(timezone.utc).isoformat(timespec="seconds"))
    snapshot = deps.runtime_snapshot()  # todo 进度 + 任务板（外围系统提供）
    if snapshot:
        parts.append(snapshot)
    if parts:
        replace_runtime_slot(
            state.messages, "runtime-context",
            "Current runtime context. This snapshot supersedes earlier "
            "runtime-context snapshots.\n\n" + "\n\n".join(parts))


def _append_skeleton_notice(state: LoopState, modid: str) -> None:
    """输入：modid。返回：无。职责：注入骨架已写入的推进指令（旧文逐字）。"""
    from ...domain.messages import UserMessage
    state.messages.append(UserMessage(content=(
        f"<auto-skeleton> 你已多次超预算未写码，系统已在 "
        f"src/main/java/com/{modid}/ 写入最小可编译主类骨架"
        f"（modid={modid}，1.21.11 注册写法已就位）。"
        f"立刻基于它继续：①按命名规则同步 mods.toml 的 modId、"
        f"build.gradle 的 group/archivesName、settings.gradle 的 "
        f"rootProject.name；②在其上扩展物品/方块/BlockEntity 等注册与逻辑。"
        f"本轮之后禁止再 read/grep starter 与 mc_java_sources，"
        f"下一轮必须是 write_file 或 edit_file。</auto-skeleton>")))


def _append_write_first_stop(state: LoopState) -> None:
    """输入：无。返回：无。职责：注入写前超预算软提醒（旧文逐字）。"""
    from ...domain.messages import UserMessage
    state.messages.append(UserMessage(content=(
        "<write-first-stop> 你已反复阅读 mc_java_sources/starter 但没有写文件。"
        "立即停止阅读源码。如果还没加载相关技能，先调用一次 load_skill 加载最相关技能"
        "（例如 forge-simple-min-mod）；然后立刻用 write_file 写出第一个最小 Java 文件，"
        "再 build/compile 根据报错处理。不要继续 read_file/grep mc_java_sources。</write-first-stop>")))

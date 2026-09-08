# -*- coding: utf-8 -*-
"""组装根的旧栈适配器（由 bootstrap.py 拆出）。

类职责：把旧模块（core.tools / supervisor / team / tasks 等）包成
loop 端口与闭包；全部惰性导入——单测 use_legacy=False 时零副作用。
生命周期：仅 bootstrap.build_engine 使用。
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable

from .domain.messages import Message, transport_messages, typed_messages
from .domain.session import Mode
from .infrastructure.config import Settings
from .infrastructure.logging_.logger import get_logger
from .interfaces.tool_registry import ToolRegistry
from .services.loop.ports import (BackgroundPort, ProtocolPort, SupervisorPort,
                                  TeammatesPort)

logger = get_logger("bootstrap")


# ---------- 旧模块适配器（P2b 工具包迁移后收编） ----------

def _legacy_tools() -> ToolRegistry:
    """输入：无。返回：旧 core.tools 的注册表（含 task handler 接线）。

    旧 tools.py 的 handler 注册为惰性查找（TOOL_HANDLERS.get(name)），
    因此这里补接 task → 子代理派发即可生效。
    """
    from .infrastructure import tools as legacy_tools  # 触发 85 工具注册（副作用包）
    from .subagent import run_subagent_async     # 子代理派发（task 工具 handler）

    legacy_tools.TOOL_HANDLERS["task"] = lambda **kw: run_subagent_async(
        kw["prompt"], persona=kw.get("persona"))
    return legacy_tools.tool_registry


def _legacy_system_provider() -> Callable[[], str]:
    """输入：无。返回：动态读取旧 config.SYSTEM 的提供器（解锁后重建生效）。"""
    def provider() -> str:
        from . import config as legacy_config
        return legacy_config.SYSTEM
    return provider


def _legacy_tools_provider() -> Callable[[], list[dict]]:
    """输入：无。返回：阶段门控后的工具 schema 提供器（chat 白名单/解锁全量）。"""
    def provider() -> list[dict]:
        from .tool_gate import leader_tools
        return leader_tools()
    return provider


class _LegacySupervisor(SupervisorPort):
    """监管线程适配器（mod 模式）。"""

    def start(self) -> None:
        """启动旧监管单例。"""
        from .supervisor import supervisor_manager
        supervisor_manager.start()

    def stop(self) -> None:
        """停止旧监管单例。"""
        from .supervisor import supervisor_manager
        supervisor_manager.stop()

    def drain_advice(self) -> list[dict]:
        """排空监管信箱。"""
        from .supervisor import supervisor_manager
        return supervisor_manager.drain_advice()

    def notify_round(self) -> None:
        """轮次计数（每 5 轮触发监管分析）。"""
        from .supervisor import supervisor_manager
        supervisor_manager.notify_round()


class _LegacyTeammates(TeammatesPort):
    """队友系统适配器（leader 视角）。"""

    def read_leader_inbox(self) -> list[dict]:
        """排空 leader 收件箱。"""
        from .infrastructure.tools.team import teammate_manager
        return teammate_manager.bus.read_inbox("leader")

    def working_names(self) -> list[str]:
        """返回仍在 working 的队友名。"""
        from .infrastructure.tools.team import teammate_manager
        return [name for name, cfg in teammate_manager.team.items()
                if cfg.status == "working"]


class _LegacyBackground(BackgroundPort):
    """后台任务通知适配器。"""

    def drain_notifications(self) -> list:
        """排空后台通知。"""
        from .infrastructure.tools.background import bg_manager
        return bg_manager.drain_notifications()

    def format_results(self, notifications: list) -> str:
        """渲染 <background-results> 注入文本。"""
        from .infrastructure.tools.background import format_background_results
        return format_background_results(notifications)


class _LegacyProtocol(ProtocolPort):
    """团队协议注入适配器（typed↔transport 往返调用旧 inject_pending_requests）。"""

    def inject_pending(self, agent_id: str, messages: list[Message]) -> None:
        """输入：身份 + 当前消息列表。返回：无。职责：原地注入协议块。"""
        from .protocol import inject_pending_requests
        dicts = transport_messages(messages)
        inject_pending_requests(dicts, agent_id)
        messages[:] = typed_messages(dicts)


def _legacy_skill_catalog_injector(messages: list[Message]) -> None:
    """技能目录 digest 注入适配器（digest 变化才追加；原地往返）。"""
    from .infrastructure.tools.skills import maybe_inject_skill_catalog
    dicts = transport_messages(messages)
    maybe_inject_skill_catalog(dicts)
    messages[:] = typed_messages(dicts)


def _legacy_runtime_snapshot() -> Callable[[], str]:
    """构造 pre-step 运行时快照提供器（todo 进度 + 任务板）。"""
    def snapshot() -> str:
        from .infrastructure.tools.tasks import task_manager, todo_manager
        parts = []
        if todo_manager.todos:
            parts.append("Todo progress:\n" + todo_manager.render())
        tasks = task_manager.list_tasks()
        if tasks:
            parts.append("Task board:\n" + "\n".join(
                f"- #{t.get('id')} [{t.get('status', '?')}] "
                f"{str(t.get('subject', ''))[:80]}" for t in tasks))
        return "\n\n".join(parts)
    return snapshot


def _workspace_ensurer(settings: Settings) -> Callable[[], None]:
    """构造工作区自愈闭包（mc_java_sources / docs/agent 的 junction 补建）。"""
    allowed = (settings.mode == Mode.MOD
               or settings.workspace.allow_mc_sources_in_chat)
    repo_root = Path(__file__).resolve().parent

    def ensure() -> None:
        if not allowed:
            return
        _ensure_junction(repo_root / "mc_java_sources_1.21.11",
                         Path.cwd() / "mc_java_sources")
        _ensure_junction(repo_root / "docs" / "agent",
                         Path.cwd() / "docs" / "agent")
    return ensure


def _ensure_junction(source: Path, target: Path) -> None:
    """输入：源目录 + 目标链接路径。返回：无。职责：缺失时补建目录链接。"""
    if target.exists() or not source.is_dir():
        return
    try:
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(source)],
                           check=True, capture_output=True)
        else:
            target.symlink_to(source, target_is_directory=True)
        logger.info("已补建 junction %s -> %s", target, source)
    except (OSError, subprocess.CalledProcessError) as e:
        logger.warning("补建 junction 失败 %s: %s", target, e)


def _legacy_jar_builder() -> Callable[[], str]:
    """输入：无。返回：jar 构建闭包（收尾/兜底自动构建）。"""
    def build() -> str:
        from .infrastructure.tools import _forge_build_jar
        return _forge_build_jar({})
    return build


def _legacy_zip_builder() -> Callable[[], str]:
    """输入：无。返回：源码 zip 预生成闭包。"""
    def build() -> str:
        from .infrastructure.tools import _build_source_zip
        return _build_source_zip()
    return build

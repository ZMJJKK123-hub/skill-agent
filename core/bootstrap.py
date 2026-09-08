# -*- coding: utf-8 -*-
"""组装根（composition root）：Settings → AgentEngine 的唯一装配点。

按 Rule 2.2（依赖注入）：全引擎的 concrete 实例只在此处创建；
业务层只见 interfaces。对旧模块（core.tools 等）的适配器全部
惰性导入——单测注入 Fake 时不触发任何旧代码/SDK 副作用。
"""
from __future__ import annotations

from typing import Optional

from .bootstrap_legacy import (_legacy_jar_builder, _legacy_runtime_snapshot,
                               _legacy_skill_catalog_injector,
                               _legacy_system_provider, _legacy_tools,
                               _legacy_tools_provider, _legacy_zip_builder,
                               _workspace_ensurer, _LegacyBackground,
                               _LegacyProtocol, _LegacySupervisor,
                               _LegacyTeammates)
from .domain.session import SessionContext
from .infrastructure.autowrite import write_skeleton, write_starter
from .infrastructure.config import Settings
from .infrastructure.logging_.runlog_writer import RunlogEventWriter
from .infrastructure.openai_client import OpenAIModelClient
from .infrastructure.session_files import FileSessionStore
from .interfaces.event_writer import EventWriter
from .interfaces.model_client import ModelClient
from .interfaces.tool_registry import ToolRegistry
from .services.compaction import CompactionService
from .services.loop.deps import (LoopDeps, NullBackground, NullProtocol,
                                 NullStore, NullSupervisor, NullTeammates)
from .services.loop.ports import (BackgroundPort, ProtocolPort, SupervisorPort,
                                  TeammatesPort)
from .services.loop.runner import AgentLoopEngine
from .services.session_log import SessionLog

def _assemble_ports(use_legacy: bool) -> dict:
    """输入：是否接旧工具栈。返回：五个外围端口的装配字典（Rule 2.2 DI）。"""
    if use_legacy:
        return {
            "supervisor": _LegacySupervisor(),
            "teammates": _LegacyTeammates(),
            "background": _LegacyBackground(),
            "protocol": _LegacyProtocol(),
            "skill_catalog": _legacy_skill_catalog_injector,
            "runtime_snapshot": _legacy_runtime_snapshot(),
        }
    return {
        "supervisor": NullSupervisor(),
        "teammates": NullTeammates(),
        "background": NullBackground(),
        "protocol": NullProtocol(),
        "skill_catalog": (lambda _: None),
        "runtime_snapshot": (lambda: ""),
    }

# ---------- 组装 ----------

def build_engine(
    settings: Optional[Settings] = None,
    *,
    client: Optional[ModelClient] = None,
    registry: Optional[ToolRegistry] = None,
    writer: Optional[EventWriter] = None,
    session_log: Optional[SessionLog] = None,
    use_legacy: bool = True,
) -> AgentLoopEngine:
    """构建 AgentLoopEngine（生产默认接旧工具栈；测试注入 Fake）。

    Args:
        settings: 配置（None = 从环境读取）。
        client / registry / writer / session_log: 覆盖注入（测试用）。
        use_legacy: False 时不触碰旧模块（纯 Fake 组装，测试隔离）。
    Returns:
        装配完成的引擎实例。
    """
    settings = settings or Settings.from_env()
    ctx = SessionContext(session_root=settings.session_root,
                         mode=settings.mode, sandbox=settings.sandbox)
    client = client or OpenAIModelClient(settings.model, settings.session_root)
    writer = writer or RunlogEventWriter()
    session_log = session_log or SessionLog()
    store = (FileSessionStore(settings.session_root)
             if settings.session_root else NullStore())
    system_provider = _legacy_system_provider() if use_legacy else (lambda: "")
    compaction = CompactionService(client, system_provider, settings.model)
    if use_legacy:
        registry = registry or _legacy_tools()
    ports = _assemble_ports(use_legacy)
    deps = LoopDeps(
        ctx=ctx, settings=settings, client=client, store=store, writer=writer,
        registry=registry, compaction=compaction,
        system_provider=system_provider,
        tools_provider=_legacy_tools_provider() if use_legacy else (lambda: []),
        supervisor=ports["supervisor"], teammates=ports["teammates"],
        background=ports["background"], protocol=ports["protocol"],
        skill_catalog_injector=ports["skill_catalog"],
        workspace_ensurer=_workspace_ensurer(settings),
        auto_starter=write_starter, auto_skeleton=write_skeleton,
        jar_builder=(_legacy_jar_builder() if use_legacy else (lambda: "skip")),
        zip_builder=(_legacy_zip_builder() if use_legacy else (lambda: "skip")),
        session_log=session_log,
        runtime_snapshot=ports["runtime_snapshot"],
    )
    return AgentLoopEngine(deps)

# -*- coding: utf-8 -*-
"""主循环依赖容器与空实现（services/loop 层）。

LoopDeps 是 runner 及各子服务的唯一入口对象（构造注入，Rule 2.2）：
业务模块不再 import 任何具体单例；bootstrap 负责把真实实现
（含过渡期的旧模块适配器）填进来，测试填 Null/Fake。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

from ...domain.session import SessionContext
from ...infrastructure.config import Settings
from ...interfaces.event_writer import EventWriter
from ...interfaces.model_client import ModelClient, ToolSchema
from ...interfaces.session_store import SessionStore
from ...interfaces.tool_registry import ToolRegistry
from ..compaction import CompactionService
from .ports import BackgroundPort, ProtocolPort, SupervisorPort, TeammatesPort

if TYPE_CHECKING:  # 仅类型标注用，避免运行期导入循环
    from ...session_log import SessionLog


@dataclass
class LoopDeps:
    """一次引擎运行的全部依赖（不可变装配结果）。

    类职责：依赖集合的显式声明；runner/guards/exits 只读这些字段。
    实例属性：
        ctx / settings — 会话身份与全量配置。
        client — 模型客户端（流式/非流式）。
        store — 会话存储（断点/插话/历史）；无会话根时为 NullStore。
        writer — run.log 协议写入器。
        registry — 工具注册表（execute/schemas）。
        compaction — 上下文压缩服务。
        system_provider — 当前系统提示词（解锁测试模式后重建，动态读取）。
        tools_provider — 本轮模型可见工具 schema（阶段门控后的子集）。
        supervisor / teammates / background / protocol — 外围系统端口。
        skill_catalog_injector — 技能目录 digest 注入（变更才追加）。
        workspace_ensurer — 工作区 junction 自愈（MC 源码/文档链接）。
        auto_starter / auto_skeleton — 写前预算兜底（starter 复制/骨架生成）。
        jar_builder / zip_builder — 收尾产物构建（mod 模式）。
        session_log — 事件源会话日志（崩溃恢复/重放的唯一事实源）。
        runtime_snapshot — pre-step 运行时快照（时间/todo/任务板）。
        trace_note — 附加日志前缀（结构化上下文）。
    生命周期：bootstrap 构建一次，整个 loop 只读。
    """

    ctx: SessionContext
    settings: Settings
    client: ModelClient
    store: SessionStore
    writer: EventWriter
    registry: ToolRegistry
    compaction: CompactionService
    system_provider: Callable[[], str]
    tools_provider: Callable[[], list[ToolSchema]]
    supervisor: SupervisorPort
    teammates: TeammatesPort
    background: BackgroundPort
    protocol: ProtocolPort
    skill_catalog_injector: Callable[[list], None]
    workspace_ensurer: Callable[[], None]
    auto_starter: Callable[[list], bool]
    auto_skeleton: Callable[[list], Optional[str]]
    jar_builder: Callable[[], str]
    zip_builder: Callable[[], str]
    session_log: "SessionLog"
    runtime_snapshot: Callable[[], str] = lambda: ""
    trace_note: str = ""


class NullSupervisor:
    """SupervisorPort 空实现（chat 模式/单测：监管线程不启动）。"""

    def start(self) -> None:
        """无操作。"""

    def stop(self) -> None:
        """无操作。"""

    def drain_advice(self) -> list[dict]:
        """输入：无。返回：空列表（无建议）。"""
        return []

    def notify_round(self) -> None:
        """无操作。"""


class NullTeammates:
    """TeammatesPort 空实现（无队友场景）。"""

    def read_leader_inbox(self) -> list[dict]:
        """输入：无。返回：空列表（无汇报）。"""
        return []

    def working_names(self) -> list[str]:
        """输入：无。返回：空列表（无人工作）。"""
        return []


class NullBackground:
    """BackgroundPort 空实现（无后台任务场景）。"""

    def drain_notifications(self) -> list:
        """输入：无。返回：空列表（无通知）。"""
        return []

    def format_results(self, notifications: list) -> str:
        """输入：通知列表（恒空）。返回：空串。"""
        return ""


class NullProtocol:
    """ProtocolPort 空实现（无协议请求场景）。"""

    def inject_pending(self, agent_id: str, append_slot: Callable) -> None:
        """无操作（无待审批请求）。"""


class NullStore:
    """SessionStore 空实现（无会话根：断点/插话/历史全部降级为无操作）。"""

    def load_recent_history(self, max_rounds: int = 20) -> list:
        """输入：无。返回：空列表（无历史）。"""
        return []

    def append_user(self, content: str, images: Optional[list] = None) -> None:
        """无操作。"""

    def append_assistant(self, content: str) -> None:
        """无操作。"""

    def reset_history(self) -> None:
        """无操作。"""

    def save_checkpoint(self, messages: list) -> None:
        """无操作。"""

    def load_checkpoint(self) -> Optional[list]:
        """输入：无。返回：None（无断点）。"""
        return None

    def clear_checkpoint(self) -> None:
        """无操作。"""

    def enqueue_pending(self, content: str, images: Optional[list] = None) -> None:
        """无操作。"""

    def drain_pending_one(self) -> list:
        """输入：无。返回：空列表。"""
        return []

    def drain_pending_all(self) -> list:
        """输入：无。返回：空列表。"""
        return []

    def pending_count(self) -> int:
        """输入：无。返回：0。"""
        return 0

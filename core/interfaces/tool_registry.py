# -*- coding: utf-8 -*-
"""工具注册表抽象（interfaces 层）。

与旧 core/toolkit.py 的 ToolDef/ToolRegistry 行为契约一致，
在此声明为 Protocol，供 services 层类型标注；具体实现（含执行
管线 pre→guard→handler→post）在 P2 迁移到
infrastructure/tools/registry.py。
"""
from __future__ import annotations

from typing import Callable, Optional, Protocol, Sequence, runtime_checkable

from .model_client import ToolSchema


@runtime_checkable
class ToolDefinition(Protocol):
    """一个已注册工具的契约视图。

    属性：
        name: str — 工具名（模型调用用的唯一标识）。
        description: str — 给模型看的用途说明。
        parameters: dict — OpenAI 参数 schema。
        handler: Callable — 执行体（**kwargs → str）。
        readonly: bool — 只读声明（supervisor 过滤依据）。
    """

    name: str
    description: str
    parameters: dict
    handler: Callable
    readonly: bool


@runtime_checkable
class ToolRegistry(Protocol):
    """工具注册与统一执行管线的契约。

    类职责：注册全部工具；提供声明式 schema 过滤（阶段门控）；
    execute 为 total 函数——任何异常都转温和错误文本，绝不向上抛。
    方法调用逻辑：register（启动期）→ schemas（每轮模型调用前）→
    execute（工具批执行期）。
    """

    def register(self, tool: ToolDefinition) -> None:
        """注册工具；重名必须 fail loud（ValueError）。"""
        ...

    def names(self) -> list[str]:
        """返回全部已注册工具名（排序稳定）。"""
        ...

    def schemas(
        self,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
    ) -> Sequence[ToolSchema]:
        """按 include/exclude 过滤出模型可见 schema（保持注册顺序）。"""
        ...

    def readonly_names(self) -> list[str]:
        """返回声明 readonly 的工具名（监管者可用集合）。"""
        ...

    def execute(self, name: str, args: dict) -> str:
        """执行一次工具调用。

        Args:
            name: 工具名。
            args: 已解析的参数 dict（解析失败在调用前已拦下）。
        Returns:
            文本结果；任何失败都形如 ``Error: ...`` 的温和文本。
        """
        ...

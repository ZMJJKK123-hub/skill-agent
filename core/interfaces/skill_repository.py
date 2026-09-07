# -*- coding: utf-8 -*-
"""技能库读取抽象（interfaces 层）。

技能 = core/skills/*/SKILL.md 知识文件。旧实现散在
tools_skills.py（加载正文）与 tools.py 的目录 digest 注入里；
P2 把两者收编为 services/skills.py + 本契约的文件实现。
"""
from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class SkillRepository(Protocol):
    """技能目录与正文的读取契约。

    类职责：扫描 SKILL.md（只读文件头部 8KB 提性能），
    提供目录 digest（变化才重新注入上下文）与按名加载正文。
    方法调用逻辑：catalog_digest（每轮注入前比对）→ load（模型
    主动 load_skill 时）→ list_names（调试/文档用）。
    """

    def catalog_digest(self) -> str:
        """返回技能目录摘要（name + 首行描述的稳定拼接）。

        Returns:
            摘要文本；目录不可用时返回空串（注入层据此跳过）。
        """
        ...

    def load(self, name: str) -> str:
        """加载一个技能的完整正文。

        Args:
            name: 技能目录名（如 forge-items）。
        Returns:
            SKILL.md 全文；不存在时返回带指引的错误文本（不抛异常，
            错误文本会回给模型让它自行纠正技能名）。
        """
        ...

    def list_names(self) -> Sequence[str]:
        """返回全部技能名（排序稳定，调试与 catalog 文档用）。"""
        ...

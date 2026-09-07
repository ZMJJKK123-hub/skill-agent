# -*- coding: utf-8 -*-
"""模式策略（services/loop 层）：chat / mod 两套行为声明的唯一出处。

消灭散布全循环的 `IS_MOD_MODE` 判断（策略模式，Rule 2.6.2）——
守卫链、监管启停、技能目录策略都由 profile 声明。
"""
from __future__ import annotations

from dataclasses import dataclass

from ...domain.session import Mode
from .guards import GUARDS_CHAT, GUARDS_MOD, GuardFn


@dataclass(frozen=True)
class ModeProfile:
    """一种运行模式的完整行为声明。

    类职责：把"模式差异"收敛为数据——新增模式只需增加 profile，
    不改 runner（开闭原则）。
    属性：
        mode: Mode — 对应枚举。
        guards: tuple[GuardFn, ...] — 工具批后守卫链（顺序即优先级）。
    生命周期：进程内常量，bootstrap 按模式取用。
    """

    mode: Mode
    guards: tuple[GuardFn, ...]

    @property
    def is_mod(self) -> bool:
        """输入：无。返回：是否 MOD 制作模式。"""
        return self.mode == Mode.MOD


#: mod 模式：全守卫链（完成闸/预算/上限/compact/nag）。
PROFILE_MOD = ModeProfile(mode=Mode.MOD, guards=GUARDS_MOD)

#: chat 模式：只读咨询——预算与完成闸不适用，仅保留上限与 compact。
PROFILE_CHAT = ModeProfile(mode=Mode.CHAT, guards=GUARDS_CHAT)


def profile_for(mode: Mode) -> ModeProfile:
    """输入：运行模式。返回：对应的 ModeProfile（未知模式 fail loud）。"""
    return PROFILE_MOD if mode == Mode.MOD else PROFILE_CHAT

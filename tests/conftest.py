# -*- coding: utf-8 -*-
"""pytest 共享夹具：离线引擎装配（use_legacy=False，不触碰旧模块/SDK 单例）。"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

# 仓库根入 sys.path（pytest 从任意 cwd 启动均可导入 core）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.bootstrap import build_engine  # noqa: E402
from core.domain.session import Mode  # noqa: E402
from core.infrastructure.config import LoopSettings, Settings  # noqa: E402
from core.infrastructure.logging_.runlog_writer import MemoryEventWriter  # noqa: E402
from core.services.session_log import SessionLog  # noqa: E402
from tests.fakes import FakeModelClient, FakeRegistry  # noqa: E402


def make_settings(mode: Mode = Mode.CHAT, session_root: str = "",
                  **loop_overrides) -> Settings:
    """输入：模式 + 会话根 + LoopSettings 覆盖项。返回：测试用 Settings。"""
    base = Settings.from_env({})
    loop = replace(LoopSettings(), **loop_overrides)
    return replace(base, mode=mode, session_root=session_root, loop=loop)


class EngineHarness:
    """一次测试的引擎装配集合（引擎 + 三替身 + 断言辅助）。"""

    def __init__(self, tmp: Path, mode: Mode = Mode.CHAT,
                 rounds=None, outputs=None, complete=None,
                 **loop_overrides) -> None:
        """输入：tmp 目录 + 模式 + 脚本。返回：无。职责：装配全部替身。"""
        self.tmp = tmp
        self.client = FakeModelClient(
            rounds if rounds is not None else [], complete_replies=complete)
        self.registry = FakeRegistry(outputs)
        self.writer = MemoryEventWriter()
        self.log = SessionLog()
        self.settings = make_settings(mode, str(tmp), **loop_overrides)
        self.engine = build_engine(
            self.settings, client=self.client, registry=self.registry,
            writer=self.writer, session_log=self.log, use_legacy=False)

    def last_model_messages(self):
        """输入：无。返回：最近一次模型请求收到的消息列表。"""
        return self.client.calls[-1]


@pytest.fixture
def tmp_cwd(tmp_path: Path, monkeypatch) -> Path:
    """每个用例独立的进程 cwd（守卫扫描 dist/src、debug 快照落盘都在此）。"""
    monkeypatch.chdir(tmp_path)
    return tmp_path

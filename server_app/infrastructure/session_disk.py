# -*- coding: utf-8 -*-
"""会话磁盘存取（server_app/infrastructure 层）。

会话根目录下全部"配置类"文件的读写契约（原 server.py 内联函数迁移）：
    .chat/api_key.txt   — API Key（本地模式允许落盘，重启恢复可续跑）
    owner.txt           — 归属用户（侧栏列表事实来源）
    mode.txt            — 会话运行模式记忆（chat|mod）
    config.json         — 会话全量配置（v2 新增：修复重启丢 game/model 等）
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from core.infrastructure.logging_.logger import get_logger

logger = get_logger("server.session_disk")


class SessionDisk:
    """一个会话根目录的配置文件读写器。

    类职责：集中全部会话配置落盘知识；写失败记日志不抛（旁路数据）。
    实例属性：root（会话根 Path）。
    生命周期：路由处理期内按需构建（无状态，可随时丢弃）。
    """

    def __init__(self, session_root: Path) -> None:
        """输入：会话根目录。返回：无。"""
        self.root = Path(session_root)

    # ---------- API Key ----------

    def read_api_key(self) -> str:
        """输入：无。返回：落盘的 API Key（无/读失败返回空串）。"""
        f = self.root / ".chat" / "api_key.txt"
        try:
            if f.is_file():
                return f.read_text(encoding="utf-8").strip()
        except OSError as e:
            logger.warning("api_key 读取失败: %s", e)
        return ""

    def write_api_key(self, api_key: str) -> None:
        """输入：API Key（空 = 删除文件）。返回：无。"""
        f = self.root / ".chat" / "api_key.txt"
        try:
            if not api_key:
                f.unlink(missing_ok=True)
                return
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(api_key, encoding="utf-8")
        except OSError as e:
            logger.warning("api_key 写入失败: %s", e)

    # ---------- 归属 ----------

    def read_owner(self) -> str:
        """输入：无。返回：owner.txt 内容（无则空串 = 未绑定）。"""
        try:
            f = self.root / "owner.txt"
            if f.exists():
                return f.read_text(encoding="utf-8").strip()
        except OSError as e:
            logger.debug("read_owner 降级忽略 | %s", e)
        return ""

    def write_owner(self, username: str) -> None:
        """输入：用户名。返回：无。职责：持久化归属（重启后仍归原用户）。"""
        try:
            (self.root / "owner.txt").write_text(username, encoding="utf-8")
        except OSError as e:
            logger.warning("owner 写入失败: %s", e)

    # ---------- 模式记忆 ----------

    def read_mode(self) -> Optional[str]:
        """输入：无。返回：mode.txt 的模式（chat|mod）；无/坏值返回 None。"""
        try:
            val = (self.root / "mode.txt").read_text(encoding="utf-8").strip()
            return val if val in ("chat", "mod") else None
        except OSError:
            return None

    def write_mode(self, mode: str) -> None:
        """输入：模式（chat|mod）。返回：无。"""
        try:
            (self.root / "mode.txt").write_text(mode, encoding="utf-8")
        except OSError as e:
            logger.warning("mode 写入失败: %s", e)

    # ---------- 全量配置（v2：修复重启丢配置） ----------

    def write_config(self, config: dict) -> None:
        """输入：会话配置 dict（game/model/vision/sandbox 等）。返回：无。"""
        try:
            (self.root / "config.json").write_text(
                json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as e:
            logger.warning("config 写入失败: %s", e)

    def read_config(self) -> dict:
        """输入：无。返回：会话配置 dict（旧会话无文件返回空 dict）。"""
        try:
            f = self.root / "config.json"
            if f.is_file():
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("config 读取失败: %s", e)
        return {}

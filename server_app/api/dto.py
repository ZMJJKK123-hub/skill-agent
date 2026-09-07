# -*- coding: utf-8 -*-
"""请求/响应 DTO（server_app/api 层）。

全部 Pydantic 请求模型的唯一定义点（原 server.py 内联模型迁移）。
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SessionRequest(BaseModel):
    """创建会话请求（轻量创建；模板在 /mod 触发时复制）。"""

    api_key: str
    game: str = "minecraft"     # 目标游戏（默认 Minecraft）
    loader: str = ""            # Mod Loader（如 forge）
    version: str = ""           # 游戏版本（如 1.21.11）
    model: str = ""             # 生成模型（v1.0.2 起无内置默认）
    base_url: str = ""          # OpenAI 兼容端点
    sandbox: str = "full-access"  # full-access | workspace-write | read-only
    vision_enabled: bool = True   # 识图模式开关
    vision_api_key: str = ""      # 视觉 API Key（独立于主模型）
    vision_base_url: str = ""
    vision_model: str = ""
    auto_mode: bool = False       # 全自动：ask 工具不阻塞
    search_api_key: str = ""      # 联网搜索 Key（Tavily 等）


class TaskRequest(BaseModel):
    """启动任务请求（chat/mod 双模式 + 排队/恢复 + 配置覆盖）。"""

    session_id: str
    prompt: str
    mode: str = "chat"             # chat（默认）| mod
    resume: bool = False           # 从断点恢复（暂停后继续）
    api_key: Optional[str] = None  # 覆盖会话 Key（改 key 后立即生效）
    model: str = ""
    base_url: str = ""
    vision_enabled: Optional[bool] = None
    vision_api_key: Optional[str] = None
    vision_base_url: Optional[str] = None
    vision_model: Optional[str] = None
    auto_mode: Optional[bool] = None
    search_api_key: Optional[str] = None
    images: list = []              # data URL 图片（≤4 张，落盘 .chat/uploads）
    force_mode: bool = False       # 显式模式覆盖（前端 /chat 拦截用）


class AuthRequest(BaseModel):
    """登录/注册请求（登录已废弃，接口冻结保留）。"""

    username: str
    password: str


class AnswerRequest(BaseModel):
    """回答 agent 提问（多题 answers 数组 / 单题 answer 兼容）。"""

    session_id: str
    answer: str = ""
    answers: Optional[list] = None


class HistoryEntry(BaseModel):
    """历史记录条目（upsert 用）。"""

    sessionId: str
    game: str = "minecraft"
    prompt: str = ""
    elapsed: Optional[int] = None
    fileCount: Optional[int] = None
    date: Optional[str] = None


class HistoryBatchDelete(BaseModel):
    """批量删除历史的 session_id 列表。"""

    session_ids: list[str]

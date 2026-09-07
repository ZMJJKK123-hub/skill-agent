# -*- coding: utf-8 -*-
"""配置对象：全部环境变量一次收敛为强类型 Settings（infrastructure 层）。

按 agent.md Rule 2.4（零硬编码）：网络地址/超时/凭证只在这里读取
环境变量并给出默认值，其余模块一律通过注入的 Settings 取值，
禁止再出现 os.environ.get 散读。旧 core/config.py 的模块级全局
（MODEL/CLIENT/SANDBOX_MODE…）由本类取代；系统提示词等文本资产
在 P2 迁移到 services/prompts.py。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from ..domain.session import Mode, SandboxMode


def _flag(name: str, default: str = "") -> bool:
    """输入：环境变量名 + 默认值。返回：是否等于 "1"（布尔旗标解析）。"""
    return os.environ.get(name, default) == "1"


@dataclass(frozen=True)
class ModelSettings:
    """主模型接入参数。

    属性：
        api_key: str — API 密钥（DEEPSEEK_API_KEY，历史名沿用）。
        base_url: str — OpenAI 兼容端点（DSH_BASE_URL）。
        model: str — 模型名（DSH_MODEL）。
        timeout_s: float — 单请求超时秒（长任务兜底）。
        session_header_id: str — x-opencode-session 稳定会话头种子
            （Zen 端点路由用；同会话保持一致以命中提示词缓存）。
    """

    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "GLM-4.5-Flash"
    timeout_s: float = 600.0
    session_header_id: str = ""
    context_window: int = 0        # 上下文窗口 token 数；0 = 按模型名映射/默认 1M
    max_output_tokens: int = 8000  # 单轮模型请求的 max_tokens


@dataclass(frozen=True)
class VisionSettings:
    """识图（视觉）模型接入参数（DSH_VISION_*）。"""

    enabled: bool = True          # 识图模式总开关（默认开启）
    api_key: str = ""             # 视觉 API 密钥
    base_url: str = ""            # 视觉端点（空 = 未配置）
    model: str = ""               # 视觉模型名


@dataclass(frozen=True)
class LoopSettings:
    """主循环防死循环参数（全部可用 env 覆盖，见 agent.md 零硬编码）。"""

    max_tool_rounds: int = 200       # 工具调用轮上限（DSH_MAX_TOOL_ROUNDS）
    max_total_rounds: int = 300      # 含纯文本轮的总上限（DSH_MAX_TOTAL_ROUNDS）
    completion_grace_rounds: int = 25  # 完成闸宽限轮（DSH_COMPLETION_GRACE_ROUNDS）
    max_inline_tool_chars: int = 3000  # 超长工具结果 spill 阈值（字符）
    repeat_tool_threshold: int = 5   # 同工具连续重复告警阈值
    defer_drain: bool = False        # daemon 模式下插话延迟消费旗标


@dataclass(frozen=True)
class WorkspaceSettings:
    """工作区与技能库定位参数。"""

    skills_dir: str = "core/skills"       # 默认技能库（相对仓库根）
    custom_skill_dirs: str = ""           # 附加技能目录（分号分隔）
    skill_catalog_disabled: bool = False  # 关闭技能目录注入（调试用）
    disable_client_tools: bool = False    # 低内存服务器：移除客户端/GUI 工具
    allow_mc_sources_in_chat: bool = False  # chat 模式允许读 MC 源码树
    mc_background: bool = True            # 游戏客户端后台化（默认开）


@dataclass(frozen=True)
class GameSettings:
    """游戏进程/RCON 参数（tools_gametest、tools_game 用）。"""

    rcon_port: int = 25575   # RCON 端口
    rcon_password: str = ""  # RCON 密码（空 = 未启用）


@dataclass(frozen=True)
class SearchSettings:
    """联网搜索参数（web_search 工具用）。"""

    tavily_api_key: str = ""   # Tavily 商用搜索（空则回退 DuckDuckGo）
    search_api_key: str = ""   # 兼容旧名的搜索 key


@dataclass(frozen=True)
class Settings:
    """引擎全量配置（组装根唯一持有的配置对象）。

    类变量/属性：mode / sandbox / session_root / web_chat /
    auto_mode / daemon_idle_timeout_s 及上述各分组。
    生命周期：bootstrap 启动时 Settings.from_env() 构建一次，
    之后只读（frozen），运行期不回读环境变量。
    """

    mode: Mode = Mode.CHAT
    sandbox: SandboxMode = SandboxMode.FULL_ACCESS
    session_root: str = ""
    web_chat: bool = False            # 本网站 chat 引导（否则引导 GitHub 自部署）
    auto_mode: bool = False           # 全自动：ask 工具不阻塞等用户
    daemon_idle_timeout_s: float = 600.0  # daemon 空闲自杀秒数
    model: ModelSettings = field(default_factory=ModelSettings)
    vision: VisionSettings = field(default_factory=VisionSettings)
    loop: LoopSettings = field(default_factory=LoopSettings)
    workspace: WorkspaceSettings = field(default_factory=WorkspaceSettings)
    game: GameSettings = field(default_factory=GameSettings)
    search: SearchSettings = field(default_factory=SearchSettings)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        """从环境变量构建 Settings（env 供测试注入，缺省读真实环境）。

        Globals Used:
            读全部 DSH_* / DEEPSEEK_API_KEY 环境变量（只读一次）。
        Args:
            env: 覆盖用的变量表（测试隔离用；None = os.environ）。
        Returns:
            完整 Settings 实例。
        """
        g = env if env is not None else dict(os.environ)
        sandbox_raw = g.get("DSH_SANDBOX_MODE", SandboxMode.FULL_ACCESS.value)
        groups = _env_groups(g)
        return cls(
            mode=Mode.parse(g.get("DSH_MODE")),
            sandbox=SandboxMode(sandbox_raw),
            session_root=g.get("DSH_SESSION_ROOT", ""),
            web_chat=g.get("DSH_WEB_CHAT", "") == "1",
            auto_mode=g.get("DSH_AUTO_MODE", "0") == "1",
            daemon_idle_timeout_s=float(g.get("DSH_DAEMON_IDLE_TIMEOUT", "600")),
            model=_env_model(g),
            vision=groups["vision"], loop=groups["loop"],
            workspace=groups["workspace"], game=groups["game"],
            search=groups["search"],
        )


def _env_model(g: dict) -> ModelSettings:
    """输入：环境变量表。返回：主模型配置组。"""
    return ModelSettings(
        api_key=g.get("DEEPSEEK_API_KEY", ""),
        base_url=g.get("DSH_BASE_URL", "https://api.deepseek.com"),
        model=g.get("DSH_MODEL", "GLM-4.5-Flash"),
        session_header_id=g.get("DSH_SESSION_ROOT", ""),
        context_window=int(g.get("DSH_CONTEXT_WINDOW", "0")),
        max_output_tokens=int(g.get("DSH_MAX_OUTPUT_TOKENS", "8000")),
    )


def _env_groups(g: dict) -> dict:
    """输入：环境变量表。返回：vision/loop/workspace/game/search 五个分组。"""
    return {
        "vision": VisionSettings(
            enabled=g.get("DSH_VISION_ENABLED", "1") == "1",
            api_key=g.get("DSH_VISION_API_KEY", ""),
            base_url=g.get("DSH_VISION_BASE_URL", ""),
            model=g.get("DSH_VISION_MODEL", "")),
        "loop": LoopSettings(
            max_tool_rounds=int(g.get("DSH_MAX_TOOL_ROUNDS", "200")),
            max_total_rounds=int(g.get("DSH_MAX_TOTAL_ROUNDS", "300")),
            completion_grace_rounds=int(g.get("DSH_COMPLETION_GRACE_ROUNDS", "25")),
            defer_drain=g.get("DSH_DEFER_DRAIN", "") == "1"),
        "workspace": WorkspaceSettings(
            skills_dir=g.get("DSH_SKILLS_DIR", "core/skills"),
            custom_skill_dirs=g.get("DSH_CUSTOM_SKILL_DIRS", ""),
            skill_catalog_disabled=g.get("DSH_SKILL_CATALOG_DISABLED", "") == "1",
            disable_client_tools=g.get("DSH_DISABLE_CLIENT_TOOLS", "") == "1",
            allow_mc_sources_in_chat=g.get("DSH_ALLOW_MC_SOURCES", "") == "1",
            mc_background=g.get("DSH_MC_BACKGROUND", "1") == "1"),
        "game": GameSettings(
            rcon_port=int(g.get("DSH_RCON_PORT", "25575")),
            rcon_password=g.get("DSH_RCON_PASSWORD", "")),
        "search": SearchSettings(
            tavily_api_key=g.get("DSH_TAVILY_API_KEY", ""),
            search_api_key=g.get("DSH_SEARCH_API_KEY", "")),
    }

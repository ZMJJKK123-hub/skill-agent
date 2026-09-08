import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ── 强制 stdout/stderr 走 UTF-8 ──────────────────────
# Windows 终端默认 GBK，print emoji/中文会崩。
# 在导入其他东西之前先 reconfigure，彻底解决 UnicodeEncodeError。
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# override 必须为 False：8000 网页版（run_task.py）在导入 core 前已把
# 「用户自己的 DEEPSEEK_API_KEY」和 server 注入的每会话 DSH_MODEL /
# DSH_BASE_URL 写进环境变量，若这里用 .env 覆盖，用户的 Key 与模型选择
# 会被仓库 .env（8001 清小搭配置）顶掉——实测曾导致正式服所有任务都走
# 服务器 owner 的 Key 计费。8001 侧不受影响：main.py / session_daemon.py
# 在导入 core 之前已显式 load_dotenv(..., override=True) 加载过 .env。
# DSH_NO_ENV_FILE=1（由 run_task.py 设置）：8000 用户会话进程完全不加载
# 仓库 .env——owner 的任何密钥/配置都不得进入用户进程。
if os.environ.get("DSH_NO_ENV_FILE") == "1":
    pass  # 8000 网页版：用户自备配置，跳过 .env 加载
else:
    load_dotenv(override=False)

# ---------- 日志系统 ----------
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("agent")

# ---------- 配置 ----------
# 模型与 API 地址由会话注入（DSH_MODEL / DSH_BASE_URL），未注入时回退 DeepSeek 官方默认。
MODEL = os.environ.get("DSH_MODEL", "GLM-4.5-Flash")

# 运行模式：chat（通用对话，不复制 mod 模板）| mod（MOD 制作，工作区已复制模板）
# 由 server 通过 run_task 的 DSH_MODE 环境变量注入。
MODE = os.environ.get("DSH_MODE", "chat")

# OpenAI 客户端：预置 http_client 避免每次子进程启动时 ssl 证书库加载
# 卡 15+ 秒（Windows 上 certifi cacert.pem 加载 + openai SDK 初始化，
# 实测 httpx.Client() 初始化 4-12s、OpenAI() 构造 15-17s —— 这是
# "发消息后进行中闪现、agent 迟迟不响应"的根因）。
# 方案：只禁用证书库文件加载（verify=False），请求仍走 HTTPS；
# 复用模块级单例避免重复构造。
import httpx as _httpx
_http_client = _httpx.Client(
    trust_env=False,        # 跳过系统代理探测（额外省 4-7s）
    verify=False,           # 跳过 CA 证书库加载（省 3-4s）
    timeout=600.0,          # 长超时：MOD 制作任务单轮可能很久
)
# Zen（opencode.ai Console Go）自 2026-09 起要求每个会话携带稳定的
# x-opencode-session 请求头（用于路由与提示词缓存），缺失时 deepseek-v4-flash
# 直接 400 MissingSessionID（实测：上一刻还能用，端点上线校验后全挂）。
# openai SDK 的 default_headers 随每个请求发送；非 Zen 端点忽略未知头，无副作用。
# ID 用每会话稳定的 uuid5（DSH_SESSION_ROOT 相同 → 重连/重启复用同一 ID，
# 提示词缓存收益最大化）；无会话根的部署回退进程内一次性随机 ID。
import uuid as _uuid
_session_seed = os.environ.get("DSH_SESSION_ROOT") or _uuid.uuid4().hex
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url=os.environ.get("DSH_BASE_URL", "https://api.deepseek.com"),
    http_client=_http_client,
    default_headers={"x-opencode-session": _uuid.uuid5(_uuid.NAMESPACE_URL, _session_seed).hex},
)

# 会话级沙箱模式：full-access | workspace-write | read-only（由 server 注入 DSH_SANDBOX_MODE）
SANDBOX_MODE = os.environ.get("DSH_SANDBOX_MODE", "full-access")

# 全自动模式：开启后 ask_user_question 不再阻塞等待用户，而是返回提示让 agent 用合理默认值继续。
# 由 server 通过 DSH_AUTO_MODE 注入（前端设置面板可切换）。
AUTO_MODE = os.environ.get("DSH_AUTO_MODE", "0") == "1"

# ---------- 路径安全沙箱 ----------
WORKDIR = Path.cwd()

def safe_path(p: str, base: str | None = None) -> Path:
    """把相对路径解析为绝对路径，并强制不越出工作区。

    第 12 课扩展：base 参数支持 worktree 根作为路径基座——
    worktree 位于 WORKDIR 之下，天然不会越界，但能实现
    "每个任务在自己目录里操作"的执行面隔离。
    base 为空时行为与 s11 一致（基座 = 项目根目录）。

    MOD 例外：mc_java_sources 常以 junction 形式挂在 mod 工作区内，
    真实路径在仓库根的 mc_java_sources_1.21.11。它是只读参考源码，
    允许 agent 读取完整文件，否则 search_api 只能给零散几行。
    """
    root = Path(base) if base else WORKDIR
    path = (root / p).resolve()
    if path.is_relative_to(WORKDIR):
        return path
    # 允许读取仓库根下的 MC/Forge 反编译源码参考树
    repo_root = Path(__file__).resolve().parent.parent
    mc_src = (repo_root / "mc_java_sources_1.21.11").resolve()
    if mc_src.exists() and path.is_relative_to(mc_src):
        return path
    # 允许读取 docs/agent 下的已知错误文档（只读参考）
    docs_agent = (repo_root / "docs" / "agent").resolve()
    if docs_agent.exists() and path.is_relative_to(docs_agent):
        return path
    raise ValueError(f"Path escapes workspace: {p}")


# 提示词常量域拆至 prompts（尾部再导出——全库 import 零改动）
from .prompts import (SYSTEM, CHAT_TOOL_GUIDE, SUBAGENT_SYSTEM,  # noqa: E402,F401
                      SUPERVISOR_SYSTEM, TEAMMATE_SYSTEM_PREFIX,
                      build_system_prompt, MAX_SUBAGENT_TURNS,
                      SUPERVISOR_MAX_TURNS)

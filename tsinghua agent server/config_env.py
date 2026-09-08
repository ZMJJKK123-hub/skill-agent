# -*- coding: utf-8 -*-
"""环境与路径准备（必须最先导入——副作用：chdir 与 DSH_* 环境变量）。

由 main.py 头部迁出。核心约束：
  1. 在任何 core 导入前把 cwd 切到 .runtime 工作区（工具文件基座）；
  2. chat 只读模式 + 沙箱 read-only（本服务绝不修改项目源文件）；
  3. 显式加载项目根 .env（含 DEEPSEEK/TSINGHUA 密钥）。
"""
import os
import sys
from pathlib import Path
import logging  # 统一日志：降级路径记录

logger = logging.getLogger("tsinghua.config")

#: 项目根 = 本目录的上上级
PROJECT_ROOT = Path(__file__).resolve().parent.parent
#: 本服务目录
SERVICE_DIR = Path(__file__).resolve().parent

# 让 core 包可导入
sys.path.insert(0, str(PROJECT_ROOT))

# 先切项目根读 .env，再切工作区（见下方 WORKSPACE）
os.chdir(PROJECT_ROOT)

# chat 模式：不触发 MOD 专属的 GameTest / 构建 / 监管线程逻辑
os.environ.setdefault("DSH_MODE", "chat")
os.environ.setdefault("DSH_SKILL_CATALOG_DISABLED", "1")
os.environ.setdefault("DSH_ALLOW_MC_SOURCES", "1")
# 沙箱保护：只允许读，禁止越出项目根写文件（防修改 /opt/skill-agent 源文件）
os.environ["DSH_SANDBOX_MODE"] = "read-only"
# 全自动模式：ask_user_question 不在 HTTP 请求里永久阻塞
os.environ.setdefault("DSH_AUTO_MODE", "1")
# 会话状态落盘到本服务目录下的 .runtime（避免污染项目根）
os.environ.setdefault("DSH_SESSION_ROOT", str(SERVICE_DIR / ".runtime"))

# 显式读取项目根 .env（DEEPSEEK_API_KEY / TSINGHUA_API_KEY 等）
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env", override=True)
except Exception as e:
    logger.debug("module 降级忽略 | %s", e)

#: 本服务的接入密钥（清小搭填的 credential；默认值仅本地测试用）
VALID_KEY = os.environ.get("TSINGHUA_API_KEY", "sk-test-123")

#: 工作区目录：agent 的所有文件操作/产物都在这里（与 server_app 网页隔离）
WORKSPACE = SERVICE_DIR / ".runtime"
WORKSPACE.mkdir(parents=True, exist_ok=True)

# 必须在导入 core 之前把 cwd 切到 WORKSPACE：core 的 WORKDIR 与工具
# 文件基座都落在 .runtime，产物才会出现在可收集/下载的位置
os.chdir(WORKSPACE)

#: 开源自部署地址（MOD 需求引导用户去本地部署完整版）
GITHUB_URL = os.environ.get(
    "DSH_GITHUB_URL", "https://github.com/ZMJJKK123-hub/skill-agent")

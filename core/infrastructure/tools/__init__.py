# -*- coding: utf-8 -*-
"""工具包入口：schema 拼装 + 元数据 + 注册循环 + 兼容再导出。

导入即完成全部 85 个工具的注册（保持旧 core/tools.py 的原序——
schemas 分片按原序切割，禁止重排；顺序即模型可见的工具列表顺序）。
"""
import os

from ...config import logger
from .registry import ToolDef, ToolRegistry, tool_registry  # noqa: F401 — 再导出
from . import handlers  # noqa: F401 — 导入期注册 prompt section / SYSTEM 重建

# 各分片 schema（原序拼接；分片内部见各文件头说明）
from .schemas_01_basic import TOOLS as _TOOLS_01
from .schemas_02_basic_team import TOOLS as _TOOLS_02
from .schemas_03_team import TOOLS as _TOOLS_03
from .schemas_04_build_team_vcs import TOOLS as _TOOLS_04
from .schemas_05_build_game import TOOLS as _TOOLS_05
from .schemas_06_basic_build_diag_game import TOOLS as _TOOLS_06
from .schemas_07_diag_game import TOOLS as _TOOLS_07
from .schemas_08_diag_game_vcs import TOOLS as _TOOLS_08
from .schemas_09_basic_build_vcs import TOOLS as _TOOLS_09

TOOLS = _TOOLS_01 + _TOOLS_02 + _TOOLS_03 + _TOOLS_04 + _TOOLS_05 + _TOOLS_06 + _TOOLS_07 + _TOOLS_08 + _TOOLS_09

#: 执行元数据（readonly/concurrency_safe/timeout；由旧 _TOOL_META 迁移）。
_TOOL_META = {'read_file': {'readonly': True, 'concurrency_safe': True}, 'grep': {'readonly': True, 'concurrency_safe': True}, 'search_api': {'readonly': True, 'concurrency_safe': True}, 'glob': {'readonly': True, 'concurrency_safe': True}, 'load_skill': {'readonly': True}, 'web_search': {'readonly': True, 'concurrency_safe': True}, 'search_minecraft_docs': {'readonly': True, 'concurrency_safe': True}, 'web_fetch': {'readonly': True, 'concurrency_safe': True}, 'task_list': {'readonly': True, 'concurrency_safe': True}, 'task_get': {'readonly': True, 'concurrency_safe': True}, 'team_status': {'readonly': True, 'concurrency_safe': True}, 'protocol_status': {'readonly': True}, 'worktree_list': {'readonly': True}, 'read_game_test_log': {'readonly': True}}

# 旧文件运行时补充的元数据（analyze_image 只读声明）
_TOOL_META["analyze_image"] = {"readonly": True}
# extra 循环补的只读标记（与旧 1657-1664 行一致）
for _schema in TOOLS:
    _name = _schema["function"]["name"]
    if _name in ("validate_resources", "parse_gametest_results", "read_crash_report", "analyze_crash",
                 "detect_environment", "verify_artifact", "wait_for_log", "wait_for_port",
                 "tail_log", "wait_for_mc_ready", "mc_status", "git_status", "git_diff",
                 "parse_build_output"):
        _TOOL_META.setdefault(_name, {"readonly": True, "concurrency_safe": True})

from .handlers import TOOL_HANDLERS  # noqa: E402 — 装配完成后引入


def _unknown_handler(**kw):
    """输入：任意参数。返回：未接线提示文本（handler 缺失 fail soft）。"""
    return "(handler not wired yet)"


# 低内存服务器模式：客户端/游戏 GUI 工具整组移除（防 OOM）
_CLIENT_TOOLS_BLOCKLIST = {
    "run_client", "run_server", "start_mc_server", "start_mc_client",
    "send_game_command", "game_input", "press_key", "type_text",
    "wait_for_screen", "verify_visual_loop", "server_console",
    "kill_game", "wait_for_mc_ready", "press_keys", "bridge_command",
    "run_test_client",
}
if os.environ.get("DSH_DISABLE_CLIENT_TOOLS") == "1":
    _before = len(TOOLS)
    TOOLS[:] = [t for t in TOOLS
                if t["function"]["name"] not in _CLIENT_TOOLS_BLOCKLIST]
    logger.info("低内存服务器模式：已禁用 %d 个客户端/游戏 GUI 工具（%d 个仍可用）",
                _before - len(TOOLS), len(TOOLS))

for _t in TOOLS:
    _name = _t["function"]["name"]
    _meta = _TOOL_META.get(_name, {})
    tool_registry.register(ToolDef(
        name=_name,
        description=_t["function"]["description"],
        parameters=_t["function"]["parameters"],
        handler=lambda _n=_name, **kw: (TOOL_HANDLERS.get(_n) or _unknown_handler)(**kw),
        timeout_ms=_meta.get("timeout_ms"),
        concurrency_safe=_meta.get("concurrency_safe", False),
        readonly=_meta.get("readonly", False),
        needs_approval=_meta.get("needs_approval"),
    ))

# 兼容再导出（bootstrap/旧引用方零改动切换）
from .background import bg_manager, format_background_results  # noqa: F401,E402
from .mod import _forge_build_jar, _build_source_zip  # noqa: F401,E402
from .skills import maybe_inject_skill_catalog, skill_loader  # noqa: F401,E402
from .tasks import task_manager, todo_manager  # noqa: F401,E402
from .team import teammate_manager  # noqa: F401,E402

logger.info("tool_registry 构建完成 | %d 个工具 | readonly=%s",
            len(tool_registry.names()), tool_registry.readonly_names())

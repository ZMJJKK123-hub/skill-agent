# -*- coding: utf-8 -*-
"""Stage-gated tool access for the agent.

Phase 1 (development): only BASE_TOOL_NAMES are visible.
Phase 2 (testing/verification): after activate_test_mode() is called, all tools
are visible for the remainder of the session and the extended prompt guide is
injected by rebuilding config.SYSTEM.
"""
import os

# Tools available without calling activate_test_mode.
BASE_TOOL_NAMES = {
    "activate_test_mode",
    "ask_user_question",
    "bash",
    "claim_task",
    "cleanup_workspace",
    "compact",
    "detect_environment",
    "download_file",
    "edit_file",
    "extract_archive",
    "glob",
    "grep",
    "load_skill",
    "protocol_status",
    "read_file",
    "request_shutdown",
    "respond_to_request",
    "run_in_background",
    "search_minecraft_docs",
    "search_api",
    "send_to_teammate",
    "set_auto_mode",
    "shutdown_teammate",
    "spawn_teammate",
    "submit_plan",
    "task",
    "task_clear",
    "task_create",
    "task_get",
    "task_list",
    "task_update",
    "team_status",
    "todo",
    "validate_resources",
    "web_fetch",
    "web_search",
    "worktree_create",
    "worktree_list",
    "worktree_recover",
    "worktree_remove",
    "worktree_run",
    "worktree_use",
    "write_file",
}

# These are never offered to the leader even after unlocking.
_LEADER_EXCLUDED = {"submit_plan"}

# chat（只读咨询）模式白名单：只开放读/搜/问 + 任务管理。
# 不含 write_file/edit_file/bash/构建/游戏/worktree/队友等任何写入或重型工具——
# 广告出写工具只会诱导模型尝试写入，然后被 read-only 沙箱拒绝（用户实测
# 因此看到"环境一直逼我写文件、每次写入又被拒绝"的内部抱怨文本）。
CHAT_TOOL_NAMES = {
    "read_file", "glob", "grep", "search_api", "search_minecraft_docs",
    "load_skill", "web_search", "web_fetch",
    "todo", "task", "task_create", "task_get", "task_list", "task_update",
    "ask_user_question", "compact",
}

TEST_MODE_UNLOCKED = False


def _is_chat_mode() -> bool:
    """chat（只读咨询）模式判定；config 延迟导入避免循环依赖。"""
    from . import config
    return getattr(config, "MODE", "chat") == "chat"


def is_unlocked() -> bool:
    """Whether the full toolset has been unlocked for this session."""
    return TEST_MODE_UNLOCKED


def get_gated_tool_names():
    """Return currently hidden tool names (all registrations minus base)."""
    from .tools import tool_registry
    all_names = set(tool_registry.names())
    return sorted(all_names - BASE_TOOL_NAMES)


def unlock_test_mode() -> str:
    """Unlock the full toolset for the rest of this session and rebuild prompt."""
    global TEST_MODE_UNLOCKED
    if _is_chat_mode():
        # chat 只读咨询没有"测试阶段"可言；解锁会引入构建类工具与只读声明冲突
        return "当前是只读咨询会话，无需解锁测试模式；可用工具已固定为只读集。"

    TEST_MODE_UNLOCKED = True

    from . import config
    config.SYSTEM = config.build_system_prompt()

    gated = get_gated_tool_names()
    lines = [
        "测试模式已解锁：本会话已开放全部工具，完整使用说明已注入系统提示词。",
        "",
        "新解锁工具（{} 个）：".format(len(gated)),
        ", ".join(gated),
        "",
        "下一步建议：",
        "1) 用 build_mod_jar_forge / run_test_gametest 验证；",
        "2) 一键闭环用 run_mod_test_cycle；",
        "3) 需要游戏内验证用 start_mc_client + verify_visual_loop；",
        "4) 通过后 git_commit / snapshot 打检查点。",
    ]
    return "\n".join(lines)


def leader_tools():
    """Return the OpenAI tools schema list for the main agent based on unlock state."""
    from .tools import tool_registry
    if _is_chat_mode():
        return tool_registry.schemas(include=CHAT_TOOL_NAMES, exclude=_LEADER_EXCLUDED)
    if TEST_MODE_UNLOCKED:
        return tool_registry.schemas(exclude=_LEADER_EXCLUDED)
    return tool_registry.schemas(include=BASE_TOOL_NAMES, exclude=_LEADER_EXCLUDED)
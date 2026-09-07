# -*- coding: utf-8 -*-
"""工具 handler 装配（由旧 core/tools.py 迁移）。

职责：① 工具名 → 执行函数 的映射表（TOOL_HANDLERS）；② 导入期注册
mod 纪律 prompt section 并重建 config.SYSTEM。schema 定义见 schemas_*.py，
注册循环见包 __init__.py。
"""
import json

from ... import config
from ...protocol import coordinator
from ...promptkit import PromptSection as _PS
from .ask import run_ask_user
from .artifact import verify_artifact
from .auto import set_auto_mode
from .background import bg_manager
from .cleanup import cleanup_workspace
from .crash import analyze_crash, read_crash_report
from .download import download_file, extract_archive
from .env import detect_environment
from .fs import run_edit, run_glob, run_grep, run_read, run_search_api, run_write
from .game import (
    bridge_command,
    game_input,
    press_key,
    press_keys,
    send_game_command,
    type_text,
    verify_visual_loop,
    wait_for_log,
    wait_for_screen,
)
from .git import git_commit, git_diff, git_status, restore_snapshot, snapshot
from .lifecycle import (
    kill_game,
    mc_status,
    server_console,
    start_mc_client,
    start_mc_server,
    start_mc_test_client,
    stop_mc_process,
)
from .loop import parse_build_output, run_mod_test_cycle
from .wait import tail_log, wait_for_mc_ready, wait_for_port
from ...tool_gate import unlock_test_mode
from .gametest import parse_gametest_results
from .mod import (
        _forge_build_jar,
    _gt_tool,
    _read_game_test_log,
    _run_game_test_server,
)
from .runtime import worktree_manager
from .shell import run_bash
from .skills import _load_skill_and_record
from .tasks import _claim_task, task_manager, todo_manager
from .team import _respond_to_request, _submit_plan, teammate_manager
from .validate import validate_resources
from .vision import run_analyze_image, run_screenshot
from .search import run_search_minecraft_docs, run_web_search
from .web import run_web_fetch
from .worktree_tools import _worktree_remove

# 第一层注入：MOD 纪律规则。
# M1/M2 重构：从"导入期 config.SYSTEM += 字符串拼接"改为注册有序 prompt section
# （移植 DSH system-prompt 设计）。技能目录（skill:catalog）在 M2 迁出 system
# prompt，改为 digest 驱动的会话消息注入（maybe_inject_skill_catalog）。
# 顺序约定：-100 身份 / 0 persona / 100-199 工具指引 / 200+ 规则。

# rules:core(150) —— 精简版核心规则；完整细节见 docs/agent/TOOL_GUIDE.md / ERROR_LIST.md / 技能
# 仅 mod 模式注册：这些是 MOD 制作纪律（写码/GameTest/dist jar），注入到 chat 只读
# 咨询会话会与 SYSTEM_CHAT 的只读声明冲突，导致模型输出"环境一直逼我写文件"类抱怨。
if config.MODE == "mod":
    config.prompt_assembler.section(_PS(
        "rules:core", 150,
        "CORE RULES (full detail in docs/agent/TOOL_GUIDE.md / ERROR_LIST.md / skills):\n"
        "- STRUCTURE: src/main/java = production code ONLY; ALL tests under src/test/java; NEVER put @GameTest in src/main.\n"
        "- SELF-TEST: use run_test_gametest (runTestGameTestServer, scans src/test). NEVER use run_game_test_server for self-verification.\n"
        "- RESOURCES (1.21.11): every item/block item needs assets/<modid>/items/<name>.json; model/texture refs are namespaced WITHOUT .json/.png; recipes use string ingredients + result {id,count}; lang item.<modid>.<name>/block.<modid>.<name> in BOTH en_us and zh_cn; pack.mcmeta uses the template form min_format/max_format (NOT supported_formats).\n"
        "- SOURCE: do NOT read/grep mc_java_sources before writing. Use search_api only after a compile/test error; source is backup only.\n"
        "- KNOWN ISSUES: read KNOWN_ISSUES.md before starting work (read-only; never edit/delete it).\n"
        "- COMPLETION: All required tests passed + dist/*.jar exists -> finish immediately; never loop on harmless WARNs.\n"
        "- ACTION: Before writing MOD code, load the most relevant skill first (load_skill). Then write code directly; do NOT pre-read mc_java_sources or starter docs. Source is backup only after errors.\n"
    ))

# 组装最终系统提示词并覆盖 config.SYSTEM。
# agent.py 在 tools.py 执行完之后才绑定 SYSTEM 引用——但 `from .config import SYSTEM`
# 是值绑定，此处必须用"模块属性动态读取"；agent.py 已改为 import config 后读 config.SYSTEM。
config.SYSTEM = config.build_system_prompt()

TOOL_HANDLERS = {
    "bash":         lambda **kw: run_bash(kw["command"]),
    "grep":         lambda **kw: run_grep(kw["pattern"], kw.get("path", "."),
                                          kw.get("glob_filter"), kw.get("max_results", 50),
                                          kw.get("context_lines", 0)),
    "search_api":   lambda **kw: run_search_api(kw["symbol"], kw.get("path", "mc_java_sources"),
                                                kw.get("max_results", 10),
                                                kw.get("context_lines", 0)),
    "glob":         lambda **kw: run_glob(kw["pattern"]),
    "web_search":   lambda **kw: run_web_search(kw["query"], kw.get("max_results", 5)),
    "search_minecraft_docs": lambda **kw: run_search_minecraft_docs(kw["query"], kw.get("max_results", 5)),
    "web_fetch":    lambda **kw: run_web_fetch(kw["url"], kw.get("max_chars", 100000)),
    "validate_resources": lambda **kw: validate_resources(kw.get("modid")),
    "parse_gametest_results": lambda **kw: parse_gametest_results(kw.get("lines", 200), kw.get("log_path")),
    "read_crash_report": lambda **kw: read_crash_report(kw.get("max_lines", 120)),
    "analyze_crash": lambda **kw: analyze_crash(kw.get("max_lines", 60)),
    "detect_environment": lambda **kw: detect_environment(),
    "verify_artifact": lambda **kw: verify_artifact(kw.get("jar_path")),
    "download_file": lambda **kw: download_file(kw["url"], kw["dest_path"]),
    "extract_archive": lambda **kw: extract_archive(kw["archive_path"], kw["dest_path"]),
    "cleanup_workspace": lambda **kw: cleanup_workspace(kw.get("mode", "cache")),
    "set_auto_mode": lambda **kw: set_auto_mode(kw.get("enabled", True)),
    "activate_test_mode": lambda **kw: unlock_test_mode(),
    "send_game_command": lambda **kw: send_game_command(
        kw["command"], kw.get("host", "127.0.0.1"), kw.get("port", 25575), kw.get("password")),
    "game_input": lambda **kw: game_input(kw.get("action", "type"), kw.get("key"), kw.get("text")),
    "press_key": lambda **kw: press_key(kw["key"]),
    "press_keys": lambda **kw: press_keys(kw.get("sequence") or []),
    "bridge_command": lambda **kw: bridge_command(
        kw.get("op", "screen_info"), kw.get("index"), kw.get("value"),
        kw.get("text"), kw.get("name"), kw.get("timeout", 10)),
    "type_text": lambda **kw: type_text(kw["text"]),
    "wait_for_log": lambda **kw: wait_for_log(kw["pattern"], kw.get("timeout", 60), kw.get("log_path")),
    "wait_for_screen": lambda **kw: wait_for_screen(kw.get("duration", 5), kw.get("prompt")),
    "verify_visual_loop": lambda **kw: verify_visual_loop(
        kw.get("prompt", ""), kw.get("max_attempts", 3), kw.get("interval", 5),
        kw.get("command"), kw.get("rcon_password"), kw.get("rcon_port", 25575)),
    "start_mc_server": lambda **kw: start_mc_server(
        kw.get("base"), kw.get("handle", "mc-server"), kw.get("rcon_port"), kw.get("rcon_password")),
    "start_mc_client": lambda **kw: start_mc_client(kw.get("base"), kw.get("handle", "mc-client")),
    "start_mc_test_client": lambda **kw: start_mc_test_client(kw.get("base"), kw.get("handle", "mc-client")),
    "mc_status": lambda **kw: mc_status(kw.get("handle")),
    "stop_mc_process": lambda **kw: stop_mc_process(kw.get("handle", "all"), kw.get("force", True)),
    "kill_game": lambda **kw: kill_game(kw.get("handle", "all")),
    "server_console": lambda **kw: server_console(
        handle=kw.get("handle", "mc-server"),
        command=kw.get("command"),
        text=kw.get("text"),
        rcon_password=kw.get("rcon_password"),
        rcon_port=kw.get("rcon_port", 25575)),
    "wait_for_port": lambda **kw: wait_for_port(
        kw["port"], kw.get("host", "127.0.0.1"), kw.get("timeout", 60)),
    "tail_log": lambda **kw: tail_log(kw.get("log_path"), kw.get("lines", 80), kw.get("base")),
    "wait_for_mc_ready": lambda **kw: wait_for_mc_ready(
        kw.get("handle", "mc-server"), kw.get("pattern", r"Done \("), kw.get("timeout", 120),
        kw.get("check_port", True), kw.get("port", 25565)),
    "git_status": lambda **kw: git_status(kw.get("workdir")),
    "git_diff": lambda **kw: git_diff(kw.get("workdir"), kw.get("stat", True)),
    "git_commit": lambda **kw: git_commit(
        kw["message"], kw.get("workdir"), kw.get("files"), kw.get("push", False)),
    "snapshot": lambda **kw: snapshot(kw.get("name", "checkpoint"), kw.get("workdir"), kw.get("message")),
    "restore_snapshot": lambda **kw: restore_snapshot(kw["ref"], kw.get("workdir")),
    "parse_build_output": lambda **kw: parse_build_output(
        kw.get("log_path"), kw.get("raw_text"), kw.get("base")),
    "run_mod_test_cycle": lambda **kw: run_mod_test_cycle(
        kw.get("modid"), kw.get("validate", True), kw.get("build", True), kw.get("run_tests", True),
        kw.get("build_timeout", 900), kw.get("test_timeout", 180), kw.get("base")),
    "ask_user_question": lambda **kw: run_ask_user(kw.get("questions") or kw.get("question", ""), kw.get("options", [])),
    "read_file":    lambda **kw: run_read(kw["path"], kw.get("limit"), kw.get("offset", 0)),
    "write_file":   lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":    lambda **kw: run_edit(kw["path"], kw["old_text"],
                                          kw["new_text"]),
    "todo":         lambda **kw: todo_manager.update(kw["items"]),
    "load_skill":   lambda **kw: _load_skill_and_record(kw),
    "task_create":  lambda **kw: json.dumps(task_manager.create(**kw), ensure_ascii=False),
    "task_update":  lambda **kw: json.dumps(task_manager.update(**kw), ensure_ascii=False),
    "task_list":    lambda **kw: json.dumps(task_manager.list_tasks(**kw), ensure_ascii=False),
    "task_get":     lambda **kw: json.dumps(task_manager.get_task(**kw), ensure_ascii=False),
    "task_clear":   lambda **kw: json.dumps(task_manager.clear(), ensure_ascii=False),
    "claim_task":   lambda **kw: _claim_task(kw),
    "run_in_background": lambda **kw: bg_manager.run(kw["command"]),
    "spawn_teammate":  lambda **kw: teammate_manager.spawn(kw["name"], kw["system_prompt"]),
    "send_to_teammate": lambda **kw: teammate_manager.send_task(kw["to_name"], kw["task"]),
    "team_status":     lambda **kw: teammate_manager.render_status(),
    "shutdown_teammate": lambda **kw: teammate_manager.shutdown(kw["name"]),
    # ── 第 10 课：协议工具 ──
    "request_shutdown": lambda **kw: coordinator.request_shutdown(
        kw["name"], kw.get("reason", "task_complete")),
    "submit_plan":      lambda **kw: _submit_plan(kw),
    "respond_to_request": lambda **kw: _respond_to_request(kw),
    "protocol_status":  lambda **kw: coordinator.render_status(),
    # ── 第 12 课：Worktree 终极隔离工具 ──
    "worktree_create":  lambda **kw: worktree_manager.worktree_create(
        kw["task_id"], kw.get("branch"), kw.get("repo")),
    "worktree_remove":  lambda **kw: _worktree_remove(kw),
    "worktree_run":     lambda **kw: worktree_manager.run_in_worktree(
        kw["task_id"], kw["command"]),
    "worktree_use":     lambda **kw: worktree_manager.worktree_use(
        kw.get("task_id")),
    "worktree_list":    lambda **kw: worktree_manager.render_list(),
    "worktree_recover": lambda **kw: json.dumps(worktree_manager.recover(),
                                                ensure_ascii=False),
    # ── Forge Mod 生成工具（MC 26.x / Forge 65.x）──
    "build_mod_jar_forge": lambda **kw: _forge_build_jar(kw),
    # ── GameTest 自循环调试（仅主 agent 可用）──
    "run_game_test_server": lambda **kw: _run_game_test_server(kw),
    "read_game_test_log": lambda **kw: _read_game_test_log(kw),
    "run_client": lambda **kw: _gt_tool("run_client", kw),
    "run_server": lambda **kw: _gt_tool("run_server", kw),
    "run_data_gen": lambda **kw: _gt_tool("run_data_gen", kw),
    "run_test_client": lambda **kw: _gt_tool("run_test_client", kw),
    "run_test_server": lambda **kw: _gt_tool("run_test_server", kw),
    "run_test_data": lambda **kw: _gt_tool("run_test_data", kw),
    "run_test_gametest": lambda **kw: _gt_tool("run_test_gametest", kw),
    # ── 识图工具（DSH_VISION_ENABLED 关闭时 handler 内部返回"未开启"提示）──
    "screenshot": lambda **kw: run_screenshot(kw.get("region")),
    "analyze_image": lambda **kw: run_analyze_image(kw["image_path"], kw.get("prompt")),
}

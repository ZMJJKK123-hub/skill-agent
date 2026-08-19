# -*- coding: utf-8 -*-
"""工具注册中心（重构后）。

本文件只保留：
- 工具 schema（TOOLS，发给大模型）
- 工具执行映射（TOOL_HANDLERS）
- 工具元数据与 tool_registry 构建
- 系统提示词 section 注册（发给大模型的机制）

所有函数实现已按功能拆分到 core/tools_*.py。
"""
import json

from . import config
from .config import logger
from .protocol import coordinator
from .promptkit import PromptSection as _PS
from .toolkit import ToolDef as _ToolDef, tool_registry
from .tools_ask import run_ask_user
from .tools_artifact import verify_artifact
from .tools_auto import set_auto_mode
from .tools_background import bg_manager, format_background_results
from .tools_cleanup import cleanup_workspace
from .tools_crash import analyze_crash, read_crash_report
from .tools_download import download_file, extract_archive
from .tools_env import detect_environment
from .tools_fs import run_edit, run_glob, run_grep, run_read, run_search_api, run_write
from .tools_game import (
    game_input,
    press_key,
    send_game_command,
    type_text,
    verify_visual_loop,
    wait_for_log,
    wait_for_screen,
)
from .tools_git import git_commit, git_diff, git_status, restore_snapshot, snapshot
from .tools_lifecycle import (
    kill_game,
    mc_status,
    server_console,
    start_mc_client,
    start_mc_server,
    stop_mc_process,
)
from .tools_loop import parse_build_output, run_mod_test_cycle
from .tools_wait import tail_log, wait_for_mc_ready, wait_for_port
from .tool_gate import unlock_test_mode
from .tools_gametest import parse_gametest_results
from .tools_mod import (
    _build_source_zip,
    _forge_build_jar,
    _gt_tool,
    _read_game_test_log,
    _run_game_test_server,
)
from .tools_runtime import worktree_manager
from .tools_shell import run_bash
from .tools_skills import _load_skill_and_record, maybe_inject_skill_catalog, skill_loader
from .tools_tasks import _claim_task, task_manager, todo_manager
from .tools_team import _respond_to_request, _submit_plan, teammate_manager
from .tools_validate import validate_resources
from .tools_vision import run_analyze_image, run_screenshot
from .tools_search import run_search_minecraft_docs, run_web_search
from .tools_web import run_web_fetch
from .tools_worktree import _worktree_remove

# 第一层注入：MOD 纪律规则。
# M1/M2 重构：从"导入期 config.SYSTEM += 字符串拼接"改为注册有序 prompt section
# （移植 DSH system-prompt 设计）。技能目录（skill:catalog）在 M2 迁出 system
# prompt，改为 digest 驱动的会话消息注入（maybe_inject_skill_catalog）。
# 顺序约定：-100 身份 / 0 persona / 100-199 工具指引 / 200+ 规则。

# rules:core(150) —— 精简版核心规则；完整细节见 docs/agent/TOOL_GUIDE.md / ERROR_LIST.md / 技能
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
                                          kw.get("glob_filter"), kw.get("max_results", 50)),
    "search_api":   lambda **kw: run_search_api(kw["symbol"], kw.get("path", "mc_java_sources"),
                                                kw.get("max_results", 10)),
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
    "type_text": lambda **kw: type_text(kw["text"]),
    "wait_for_log": lambda **kw: wait_for_log(kw["pattern"], kw.get("timeout", 60), kw.get("log_path")),
    "wait_for_screen": lambda **kw: wait_for_screen(kw.get("duration", 5), kw.get("prompt")),
    "verify_visual_loop": lambda **kw: verify_visual_loop(
        kw.get("prompt", ""), kw.get("max_attempts", 3), kw.get("interval", 5),
        kw.get("command"), kw.get("rcon_password"), kw.get("rcon_port", 25575)),
    "start_mc_server": lambda **kw: start_mc_server(
        kw.get("base"), kw.get("handle", "mc-server"), kw.get("rcon_port"), kw.get("rcon_password")),
    "start_mc_client": lambda **kw: start_mc_client(kw.get("base"), kw.get("handle", "mc-client")),
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
    "read_file":    lambda **kw: run_read(kw["path"], kw.get("limit")),
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
    "run_game_test_server": lambda **kw: _gt_tool("run_game_test_server", kw),
    "run_test_client": lambda **kw: _gt_tool("run_test_client", kw),
    "run_test_server": lambda **kw: _gt_tool("run_test_server", kw),
    "run_test_data": lambda **kw: _gt_tool("run_test_data", kw),
    "run_test_gametest": lambda **kw: _gt_tool("run_test_gametest", kw),
}

# ---------- 工具定义（DeepSeek / OpenAI 格式）----------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search file contents with a regex across the workspace (skips build/runtime dirs). Returns 'relative/path:line: content'. Useful for finding exact APIs/errors in mc_java_sources, skills, or generated code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex to search for"},
                    "path": {"type": "string", "description": "Directory or file to search (default workspace root)"},
                    "glob_filter": {"type": "string", "description": "Optional filename glob filter, e.g. *.java"},
                    "max_results": {"type": "integer", "description": "Max matches to return (default 50)"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_api",
            "description": "Focused API dictionary lookup: search MC/Forge source for a symbol and return up to 10 short match lines. USE THIS FIRST on compile errors instead of reading whole files. Do NOT call read_file on large source files to 'learn' APIs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Exact class/method/field name or error symbol, e.g. isClientSide or FMLClientSetupEvent.getBus"},
                    "path": {"type": "string", "description": "Directory to search (default mc_java_sources)"},
                    "max_results": {"type": "integer", "description": "Max match lines to return (default 10)"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files by glob pattern under the workspace (skips build/runtime dirs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern, e.g. **/*.java"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web (best-effort DuckDuckGo HTML). Returns a list of title + URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Max results (default 5)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_minecraft_docs",
            "description": "Search Minecraft/Forge-specific documentation sites (Minecraft Wiki, Forge Docs, NeoForged, GitHub) for exact APIs, versions, JSON formats, and mod development references.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, e.g. 'item model definition 1.21.11'"},
                    "max_results": {"type": "integer", "description": "Max results (default 5)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch a URL and return its text/HTML content (capped).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "max_chars": {"type": "integer", "description": "Max characters to return (default 100000)"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user_question",
            "description": "Ask the user one or more clarifying questions and wait for their answers. Use when the requirement is ambiguous and you need the user to choose or clarify. Pass 'questions' as an array to ask several at once (the user sees them all together, can answer each with a preset option or free text, and confirms once); each item has 'question' (string) and optional 'options' (list of preset choices). For a single question you may also use the legacy 'question' + 'options' form. The return value is a JSON array of {'question', 'answer'} pairs — one per question, in the order you asked them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string", "description": "The question to ask"},
                                "options": {"type": "array", "items": {"type": "string"}, "description": "Optional preset choices"},
                            },
                            "required": ["question"],
                        },
                        "description": "Multiple questions to ask at once (recommended)",
                    },
                    "question": {"type": "string", "description": "[legacy] Single question to ask"},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "[legacy] Optional preset choices for the single question"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace exact text in file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo",
            "description": "Update the task plan. Each item has 'content' (string) and 'status' (pending/in_progress/completed). Use this to track progress on multi-step tasks. Only ONE item should be in_progress at a time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["content", "status"],
                        },
                    },
                },
                "required": ["items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task",
            "description": "Run a subtask in an isolated context ASYNCHRONOUSLY (M4). Returns a task_id immediately without blocking the main loop; the subagent runs in the background and its final summary is injected into the next round as <background-results>. Use this for research, analysis, or any work whose intermediate output the parent does not need to see. IMPORTANT: after dispatching, continue working and check the next round's <background-results> for the summary — do not expect the result in this tool's return value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The task description for the subagent",
                    },
                    "persona": {
                        "type": "string",
                        "description": "Optional custom system prompt for the subagent (defaults to the standard research-agent persona)",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load domain-specific guidelines and best practices. Use this when the current task involves a specific domain like testing, git workflow, code review, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill to load",
                    }
                },
                "required": ["skill_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compact",
            "description": "Compress the conversation history into a summary. Use when the context is getting long and you want to clean up before continuing.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": "Create a new task with optional dependencies. Use this to break down complex work into a DAG of subtasks. Each task is persisted as a JSON file and can be tracked independently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "What the task is about",
                    },
                    "blocked_by": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "IDs of tasks that must complete before this one",
                    },
                },
                "required": ["subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Update a task's status. Set to in_progress when starting work, completed when done. Completing a task automatically unblocks downstream tasks that depend on it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                    "owner": {
                        "type": "string",
                        "description": "Which agent owns this task",
                    },
                },
                "required": ["task_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_list",
            "description": "List all tasks. Optionally filter by status. Use this to see the current state of the task graph.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_get",
            "description": "Get details of a specific task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_clear",
            "description": "Clear all tasks and reset the task ID counter. Use this after all tasks are completed to clean up for the next session.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_in_background",
            "description": "Run a shell command in the background. Returns immediately with a task ID. Use for long-running commands like npm install, pytest, docker build, pip install. Results delivered as background notifications in subsequent turns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_teammate",
            "description": "Create a persistent teammate agent that runs in its own thread with its own Agent Loop. The teammate has an independent context and can use all tools except team management tools (no recursion). Use this to delegate work to specialized agents (e.g., coder, tester, reviewer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Unique name for the teammate (e.g., 'coder', 'tester')",
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt defining the teammate's role and expertise",
                    },
                },
                "required": ["name", "system_prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_to_teammate",
            "description": "Send a task message to a teammate. The teammate will process it in its own Agent Loop and send the result back to your inbox. Results arrive as <teammate-reports> in subsequent turns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_name": {
                        "type": "string",
                        "description": "Name of the teammate to send the task to",
                    },
                    "task": {
                        "type": "string",
                        "description": "The task description to send",
                    },
                },
                "required": ["to_name", "task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "team_status",
            "description": "Show the current team roster with each teammate's status (idle/working/shutdown) and role. Use this to check on your team's progress.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_teammate",
            "description": "Shut down a teammate agent. The teammate's thread will exit on its next loop iteration. Use this when a teammate's work is done and you want to clean up resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_shutdown",
            "description": "Request a graceful shutdown of a teammate via the Shutdown Handshake Protocol. Sends a shutdown request; the teammate checks for uncommitted writes and either approves (safe exit after flushing buffers) or rejects (still has pending work). Use this instead of shutdown_teammate so the teammate gets a chance to finish/clean up. The result appears in <pending-requests> in a later turn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down gracefully",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why the teammate is being shut down",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_plan",
            "description": "Submit an implementation plan for leader approval (Plan Approval Protocol). High-risk changes MUST be approved before execution. If the plan is rejected, revise it and submit again. Wait for the approval result in <pending-requests> before executing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_summary": {
                        "type": "string",
                        "description": "What you plan to do",
                    },
                    "affected_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files you plan to modify/create",
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Risk level: high = refactor/delete API/database migration",
                    },
                    "estimated_changes": {
                        "type": "integer",
                        "description": "Estimated number of changes",
                    },
                },
                "required": ["plan_summary", "affected_files", "risk_level", "estimated_changes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "respond_to_request",
            "description": "Approve or reject a protocol request (Plan Approval Protocol). Called by the leader to respond to a teammate's plan submission. On reject, provide a reason; the teammate will revise and resubmit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "req_id": {
                        "type": "string",
                        "description": "The request ID shown in <pending-requests>",
                    },
                    "decision": {
                        "type": "string",
                        "enum": ["approve", "reject"],
                        "description": "approve = proceed with execution; reject = revise the plan",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the decision (especially on reject)",
                    },
                },
                "required": ["req_id", "decision"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_status",
            "description": "Show all protocol requests (shutdown handshakes and plan approvals) and their current status: pending/approved/rejected.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "claim_task",
            "description": "Atomically claim a task from the task board (.tasks/) so it becomes yours (in_progress + owner). Only pending, unowned, unblocked tasks can be claimed. If another agent already claimed it, this fails and you should try another task. Use task_list to see available tasks, then claim_task to grab one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to claim",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    # ── 第 12 课：Worktree 终极隔离工具 ──
    {
        "type": "function",
        "function": {
            "name": "worktree_create",
            "description": "Create a git worktree for a task and bind it: the task gets an isolated working directory under <repo>/.worktrees/task-<id> and auto-advances to in_progress. Work on the task inside that directory so parallel agents never overwrite each other. If the target repo is NOT the project root (e.g. a sub-repo like demo/demo-s12), pass repo explicitly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to isolate"},
                    "branch": {"type": "string", "description": "Optional branch name (default: task-<id>)"},
                    "repo": {"type": "string", "description": "Optional git repo root to create the worktree in (default: project root)"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_remove",
            "description": "Tear down a task's worktree: removes the directory, unregisters it, and cleans up the branch. complete_task=True also marks the task completed; merge=True first merges the worktree branch back to the main branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "complete_task": {"type": "boolean", "description": "Mark the task completed (default true)"},
                    "merge": {"type": "boolean", "description": "Merge the worktree branch back to main before removing (default false)"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_run",
            "description": "Run a shell command inside a task's worktree directory without switching your working base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "command": {"type": "string"},
                },
                "required": ["task_id", "command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_use",
            "description": "Switch THIS agent's working base to a task's worktree (thread-isolated). After switching, all your bash/read_file/write_file/edit_file operations are confined to that worktree. Pass task_id=0 or omit to switch back to the main directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task whose worktree to switch into; 0 or null switches back to main"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_list",
            "description": "Show the worktree registry: each worktree's task binding, branch, status and whether its directory exists.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_recover",
            "description": "Rebuild state after a crash by cross-checking the event stream, the worktree registry and the disk: roll back half-finished create ops, clean orphaned registry entries and flag orphaned directories.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    # ── Forge Mod 生成工具（MC 26.x / Forge 65.x）──
    {
        "type": "function",
        "function": {
            "name": "build_mod_jar_forge",
            "description": "Build the Forge mod project into an installable jar by running the Gradle wrapper (gradlew build). This takes several minutes on first build (downloads deps + remaps). On success, copies the jar(s) from build/libs/ into the project's dist/ folder so they can be placed directly in .minecraft/mods/. Parameters: gradle_task (default 'build').",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradle_task": {"type": "string"},
                },
            },
        },
    },
    # ── GameTest 自循环调试（仅主 agent 可用）──
    {
        "type": "function",
        "function": {
            "name": "run_game_test_server",
            "description": "Compile and run the Forge GameTestServer (gradlew runGameTestServer) to execute ALL @GameTest tests in the mod project. Run after writing your mod code + game tests, then call read_game_test_log to inspect run/logs/latest.log and fix failures. First run takes minutes (Gradle downloads + remap). Ensures run/eula.txt automatically. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradle_task": {
                        "type": "string",
                        "description": "Optional gradle task name (default 'runGameTestServer')",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_game_test_log",
            "description": "Read the tail of <mod working dir>/run/logs/latest.log (produced by run_game_test_server) to see GameTest results and errors. Use this after running GameTestServer: errors are almost always at the end of the log. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "integer",
                        "description": "Optional number of lines from the end to read (default 200, max 2000)",
                    },
                },
            },
        },
    },
    # ── Gradle verification tools group 1: src/main PRODUCTION code ONLY ──
    {
        "type": "function",
        "function": {
            "name": "run_client",
            "description": "Run 'gradlew runClient' in the BACKGROUND (non-blocking). Launches the GUI Minecraft client using ONLY src/main production code. Use mc_status / wait_for_screen to observe; stop with stop_mc_process(handle='mc-client'). Does not block the agent loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Kept for compatibility; ignored because startup is now background",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_server",
            "description": "Run 'gradlew runServer' in the BACKGROUND (non-blocking). Launches a headless dedicated server using ONLY src/main code. Use wait_for_log('Done (') / wait_for_port(25565) to check boot; stop with stop_mc_process(handle='mc-server'). Does not block the agent loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Kept for compatibility; ignored because startup is now background",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_data_gen",
            "description": "Run 'gradlew runData' - runs Data Generators against src/main to auto-generate model/recipe/loot/lang JSON assets from DataProvider code. Use after writing/updating DataProviders. Detect failure: 'BUILD SUCCESSFUL' absent in log means DataGen error; extract failing class+line. DIFFERENT from run_test_data: run_test_data also loads src/test and generates test-only placeholders without polluting shipped assets. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 120)",
                    },
                },
            },
        },
    },
    # ── Gradle verification tools group 2: src/main + src/test (isolated testing) ──
    {
        "type": "function",
        "function": {
            "name": "run_test_client",
            "description": "Run 'gradlew runTestClient' - launches GUI client loading BOTH src/main and src/test. Use when you need src/test helper tools (spawn/cheat command mods) for manual in-game debugging. DIFFERENT from run_client: run_client is production-only and never contains test helpers; run_test_client is the isolated-testing variant. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 90)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_server",
            "description": "Run 'gradlew runTestServer' - launches a headless dedicated server loading BOTH src/main and src/test. Use to exercise network sync / multi-player simulations that depend on isolated test code. DIFFERENT from run_server: run_server is production-only dedicated server; run_test_server loads src/test helpers. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 90)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_data",
            "description": "Run 'gradlew runTestData' - Data Generator loading BOTH src/main and src/test. Use when you wrote DataGen scripts inside src/test for test placeholders/temporary recipes; generates them WITHOUT polluting the shipped jar assets. DIFFERENT from run_data_gen: run_data_gen targets production assets only. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 120)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_gametest",
            "description": "RUN THIS FOR AGENT SELF-VERIFICATION: 'gradlew runTestGameTestServer' - GameTest automation server loading BOTH src/main and src/test, runs every @GameTest under src/test/java (isolated; never packaged into the final jar). THE core of the write->run->fix loop: write assertion tests in src/test, run this, parse Passed/Failed, fix src/main logic, re-run until pass. DIFFERENT from run_game_test_server: the latter only scans src/main @GameTest (shipped in jar as egg/getreward tests); for Agent validation you MUST use run_test_gametest. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 180)",
                    },
                },
            },
        },
    },
]

# ---------- M3: 工具注册表（toolkit.py）----------
# 由现有 TOOLS（模型 schema）+ TOOL_HANDLERS（执行）+ 元数据构建注册表。
# TOOLS / TOOL_HANDLERS 保留为兼容层（迁移期旧代码不受影响）；
# 新代码应使用 tool_registry.schemas(...) / tool_registry.execute(...)。
# handler 惰性解析：agent.py 在 tools.py 导入完成后才接线 TOOL_HANDLERS["task"]，
# 构建期快照会拿到占位 handler——闭包在 execute 时实时查 TOOL_HANDLERS。
from .toolkit import ToolDef as _ToolDef, tool_registry

# 工具元数据：readonly（只读声明）/ concurrency_safe（并行声明）/
# timeout_ms（超时钩子 opt-in）/ needs_approval（审批预留，M5+）
_TOOL_META: dict = {
    # 只读 + 并行安全（supervisor 与并行调度用）
    "read_file": {"readonly": True, "concurrency_safe": True},
    "grep": {"readonly": True, "concurrency_safe": True},
    "search_api": {"readonly": True, "concurrency_safe": True},
    "glob": {"readonly": True, "concurrency_safe": True},
    "load_skill": {"readonly": True},
    "web_search": {"readonly": True, "concurrency_safe": True},
    "search_minecraft_docs": {"readonly": True, "concurrency_safe": True},
    "web_fetch": {"readonly": True, "concurrency_safe": True},
    "task_list": {"readonly": True, "concurrency_safe": True},
    "task_get": {"readonly": True, "concurrency_safe": True},
    "team_status": {"readonly": True, "concurrency_safe": True},
    "protocol_status": {"readonly": True},
    "worktree_list": {"readonly": True},
    "read_game_test_log": {"readonly": True},
}

# 识图模式工具始终注册，保证模型能看到 screenshot / analyze_image。
# 是否允许实际调用由 DSH_VISION_ENABLED 控制：关闭时两个工具都返回“未开启”。
# 这样即使用户忘记打开开关，agent 也会知道存在识图工具，而不是自己写 OCR 脚本。
TOOL_HANDLERS["screenshot"] = lambda **kw: run_screenshot(kw.get("region"))
TOOL_HANDLERS["analyze_image"] = lambda **kw: run_analyze_image(
    kw["image_path"], kw.get("prompt"))

TOOLS.append({
    "type": "function",
    "function": {
        "name": "screenshot",
        "description": (
            "Capture the current screen (full screen by default, or a region) "
            "and save it under .screenshots/ in the workspace. Returns the image "
            "path. Use together with analyze_image to inspect game/MOD visuals."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "object",
                    "description": "Optional screen region to capture.",
                    "properties": {
                        "left": {"type": "integer", "description": "Left pixel coordinate"},
                        "top": {"type": "integer", "description": "Top pixel coordinate"},
                        "width": {"type": "integer", "description": "Region width in pixels"},
                        "height": {"type": "integer", "description": "Region height in pixels"},
                    },
                    "required": ["left", "top", "width", "height"],
                },
            },
            "required": [],
        },
    },
})
TOOLS.append({
    "type": "function",
    "function": {
        "name": "analyze_image",
        "description": (
            "Analyze an image file (e.g. a screenshot saved by the screenshot tool) "
            "using the separately configured vision API. Returns the model's textual "
            "description. Useful for checking whether a game/MOD screen looks normal, "
            "shows errors, or has rendered correctly."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Path to the image file (absolute or relative to workspace)"},
                "prompt": {"type": "string", "description": "Optional specific question/instruction about the image"},
            },
            "required": ["image_path"],
        },
    },
})
_TOOL_META["analyze_image"] = {"readonly": True}

# ── 新增自动流程工具：搜索 / 校验 / 解析 / 环境 / 产物 / 下载 / 清理 / 全自动 ──
_TOOL_SCHEMAS_EXTRA = [
    {
        "type": "function",
        "function": {
            "name": "validate_resources",
            "description": "Validate all MOD resource files (item model definitions, models, textures, blockstates, recipes, lang, pack.mcmeta) and report missing/invalid references. Use after writing assets to catch purple-missing-texture issues before running the game.",
            "parameters": {
                "type": "object",
                "properties": {
                    "modid": {"type": "string", "description": "Optional mod id; auto-detected from mods.toml/@Mod when omitted"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "parse_gametest_results",
            "description": "Parse the latest GameTest log and return a concise pass/fail summary with failed test names and error lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {"type": "integer", "description": "Tail lines to scan (default 200, max 2000)"},
                    "log_path": {"type": "string", "description": "Optional custom log path; default run/logs/latest.log"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_crash_report",
            "description": "Read the latest crash report from crash-reports/ and return the head of the report for debugging.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_lines": {"type": "integer", "description": "Lines to return (default 120)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_crash",
            "description": "Extract key facts from the latest crash report: description, exception, caused by, stack frames.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_lines": {"type": "integer", "description": "Max stack frames to include (default 60)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_environment",
            "description": "Detect current workspace environment: Java version, Gradle wrapper, mod loader, mod id, MC/Forge version, source layout, resource namespaces.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_artifact",
            "description": "Verify built jar(s) and source zip contain required metadata/resources and no forbidden runtime directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "jar_path": {"type": "string", "description": "Optional specific jar path; default uses latest dist/*.jar"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "download_file",
            "description": "Download a URL to a workspace path. Use for reference files, textures, or external resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to download"},
                    "dest_path": {"type": "string", "description": "Destination path inside workspace"},
                },
                "required": ["url", "dest_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_archive",
            "description": "Extract a zip/tar.gz/jar archive into a workspace directory (zip-slip safe).",
            "parameters": {
                "type": "object",
                "properties": {
                    "archive_path": {"type": "string", "description": "Archive path inside workspace"},
                    "dest_path": {"type": "string", "description": "Destination directory inside workspace"},
                },
                "required": ["archive_path", "dest_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cleanup_workspace",
            "description": "Clean build/runtime artifacts. mode='cache' removes build/.gradle/__pycache__/agent.log; mode='all' also removes run/run-data/.worktrees/.team/.tasks/.transcripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["cache", "all"], "description": "Cleanup mode (default cache)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_auto_mode",
            "description": "Toggle auto mode for the current agent process. When enabled, ask_user_question will not block and the agent uses reasonable defaults.",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "true to enable auto mode, false to disable"},
                },
                "required": ["enabled"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_game_command",
            "description": "Send a Minecraft RCON command to a running server/client (e.g. /give, /tp, /reload). Requires RCON enabled and password.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to send, e.g. 'give @p minecraft:diamond 1'"},
                    "host": {"type": "string", "description": "RCON host (default 127.0.0.1)"},
                    "port": {"type": "integer", "description": "RCON port (default 25575)"},
                    "password": {"type": "string", "description": "RCON password; if omitted uses DSH_RCON_PASSWORD"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "game_input",
            "description": "Generic game input. action='key' with key name, or action='type' with text. Sends input to the focused game window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["key", "type"], "description": "key=press single key, type=type text"},
                    "key": {"type": "string", "description": "Key name for key action (e.g. enter, e, esc)"},
                    "text": {"type": "string", "description": "Text to type for type action"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press and release a single key in the focused window (e.g. 'e' to open inventory, 'esc').",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key name (enter, esc, e, space, f1, etc.)"},
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type Unicode text into the focused window (useful for chat commands or search boxes).",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_log",
            "description": "Wait until a regex pattern appears in a log file (default run/logs/latest.log). Useful for waiting for server/client startup or test completion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern to search for"},
                    "timeout": {"type": "integer", "description": "Max seconds to wait (default 60)"},
                    "log_path": {"type": "string", "description": "Optional custom log path"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_screen",
            "description": "Wait a few seconds, take a screenshot, and optionally analyze it with the vision API. Use to let the game render before checking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "description": "Seconds to wait (default 5)"},
                    "prompt": {"type": "string", "description": "Optional vision analysis prompt"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_visual_loop",
            "description": "Run a visual verification loop: optionally send RCON commands, screenshot, analyze with vision, repeat. Returns all screenshot paths and analyses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Vision analysis prompt (e.g. 'is the item icon rendered correctly?')"},
                    "max_attempts": {"type": "integer", "description": "Number of attempts (default 3)"},
                    "interval": {"type": "integer", "description": "Seconds between attempts (default 5)"},
                    "command": {"type": "string", "description": "Optional RCON command to send before each screenshot"},
                    "rcon_password": {"type": "string", "description": "Optional RCON password"},
                    "rcon_port": {"type": "integer", "description": "Optional RCON port (default 25575)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_mc_server",
            "description": "Start the Forge dedicated server (gradlew runServer) in the background. Non-blocking; use mc_status / wait_for_log / wait_for_port to check readiness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {"type": "string", "description": "Optional MOD project dir (default current worktree)"},
                    "handle": {"type": "string", "description": "Process handle (default mc-server)"},
                    "rcon_port": {"type": "integer", "description": "If set, write enable-rcon/rcon.port to run/server.properties"},
                    "rcon_password": {"type": "string", "description": "If set, write rcon.password to run/server.properties and remember for RCON"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_mc_client",
            "description": "Start the Minecraft GUI client (gradlew runClient) in the background. Non-blocking; use mc_status / wait_for_screen to observe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {"type": "string", "description": "Optional MOD project dir (default current worktree)"},
                    "handle": {"type": "string", "description": "Process handle (default mc-client)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mc_status",
            "description": "Show tracked Minecraft server/client processes, open ports, and latest log readiness hints.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Optional handle filter (e.g. mc-server, mc-client)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "stop_mc_process",
            "description": "Stop a tracked Minecraft process by handle, or all with 'all' (default). Uses taskkill /T to kill the process tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "handle (mc-server/mc-client) or 'all' (default all)"},
                    "force": {"type": "boolean", "description": "Force kill (default true)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kill_game",
            "description": "Force kill all (or a named) Minecraft dev process. Alias for stop_mc_process(force=true).",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Optional handle; default 'all'"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "server_console",
            "description": "Send a console command to the local Minecraft server process via stdin if possible, otherwise fallback to RCON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Process handle (default mc-server)"},
                    "command": {"type": "string", "description": "Command to send (e.g. 'list', 'save-all')"},
                    "text": {"type": "string", "description": "Alias of command"},
                    "rcon_password": {"type": "string", "description": "Optional RCON password for fallback"},
                    "rcon_port": {"type": "integer", "description": "Optional RCON port (default 25575)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_port",
            "description": "Wait until a TCP port is open (e.g. 25565 server or 25575 RCON).",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "description": "TCP port to probe"},
                    "host": {"type": "string", "description": "Host (default 127.0.0.1)"},
                    "timeout": {"type": "integer", "description": "Max seconds (default 60)"},
                },
                "required": ["port"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tail_log",
            "description": "Read the tail of a log file (default run/logs/latest.log). Useful for quick diagnostics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_path": {"type": "string", "description": "Optional custom log path"},
                    "lines": {"type": "integer", "description": "Number of tail lines (default 80)"},
                    "base": {"type": "string", "description": "Optional project dir"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_mc_ready",
            "description": "Wait until a Minecraft server/client process is ready: log pattern matched or port open.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Process handle (default mc-server)"},
                    "pattern": {"type": "string", "description": "Regex readiness pattern (default 'Done (')"},
                    "timeout": {"type": "integer", "description": "Max seconds (default 120)"},
                    "check_port": {"type": "boolean", "description": "Also check server port (default true)"},
                    "port": {"type": "integer", "description": "Port to check (default 25565)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show git working tree status (git status --short).",
            "parameters": {
                "type": "object",
                "properties": {
                    "workdir": {"type": "string", "description": "Optional project dir"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show git diff (--stat by default) for the working tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workdir": {"type": "string", "description": "Optional project dir"},
                    "stat": {"type": "boolean", "description": "Use --stat (default true)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage all (or given files) and commit. Optionally push.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "workdir": {"type": "string", "description": "Optional project dir"},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "Optional specific files to commit; default -A"},
                    "push": {"type": "boolean", "description": "Also git push (default false)"},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "snapshot",
            "description": "Create a git checkpoint commit (snapshot). Returns short HEAD hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Snapshot name (default checkpoint)"},
                    "workdir": {"type": "string", "description": "Optional project dir"},
                    "message": {"type": "string", "description": "Optional commit message; default 'snapshot: <name>'"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restore_snapshot",
            "description": "Hard reset to a previous snapshot/commit. Destructive: discards uncommitted changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Commit hash/branch/tag to restore"},
                    "workdir": {"type": "string", "description": "Optional project dir"},
                },
                "required": ["ref"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "parse_build_output",
            "description": "Extract compile errors and FAILED Gradle tasks from build log or raw text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_path": {"type": "string", "description": "Optional path to build log"},
                    "raw_text": {"type": "string", "description": "Optional raw build output"},
                    "base": {"type": "string", "description": "Optional project dir for relative log_path"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_mod_test_cycle",
            "description": "One-call MOD test loop: validate_resources -> build jar -> run_test_gametest -> parse results. Returns full status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "modid": {"type": "string", "description": "Optional modid for resource validation"},
                    "validate": {"type": "boolean", "description": "Run validate_resources (default true)"},
                    "build": {"type": "boolean", "description": "Run gradlew build (default true)"},
                    "run_tests": {"type": "boolean", "description": "Run run_test_gametest (default true)"},
                    "build_timeout": {"type": "integer", "description": "Build timeout seconds (default 900)"},
                    "test_timeout": {"type": "integer", "description": "GameTest timeout seconds (default 180)"},
                    "base": {"type": "string", "description": "Optional project dir"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "activate_test_mode",
            "description": "Unlock the full toolset for this session. Call this when you need to build, run GameTest, start server/client, use game input/visual verification, or use Git snapshots. After calling, all remaining tools and their usage guide become visible for the rest of the session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

for _schema in _TOOL_SCHEMAS_EXTRA:
    TOOLS.append(_schema)
    _name = _schema["function"]["name"]
    if _name in ("validate_resources", "parse_gametest_results", "read_crash_report", "analyze_crash",
                 "detect_environment", "verify_artifact", "wait_for_log", "wait_for_port",
                 "tail_log", "wait_for_mc_ready", "mc_status", "git_status", "git_diff",
                 "parse_build_output"):
        _TOOL_META[_name] = {"readonly": True, "concurrency_safe": True}

def _unknown_handler(**kw):
    return "(handler not wired yet)"


for _t in TOOLS:
    _name = _t["function"]["name"]
    _meta = _TOOL_META.get(_name, {})
    tool_registry.register(_ToolDef(
        name=_name,
        description=_t["function"]["description"],
        parameters=_t["function"]["parameters"],
        handler=lambda _n=_name, **kw: (TOOL_HANDLERS.get(_n) or _unknown_handler)(**kw),
        timeout_ms=_meta.get("timeout_ms"),
        concurrency_safe=_meta.get("concurrency_safe", False),
        readonly=_meta.get("readonly", False),
        needs_approval=_meta.get("needs_approval"),
    ))


logger.info(
    f"M3 tool_registry 构建完成 | {len(tool_registry.names())} 个工具 | "
    f"readonly={tool_registry.readonly_names()}"
)

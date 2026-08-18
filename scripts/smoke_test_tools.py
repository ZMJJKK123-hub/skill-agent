# -*- coding: utf-8 -*-
"""Full-module safe smoke test: call every registered tool handler once.

Dangerous / blocking / long-running / network / GUI tools are marked SKIP.
The goal is to catch import errors, handler wiring errors, and obvious runtime
crashes without running a real Minecraft project.
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.tools import tool_registry  # noqa: E402

SKIP = {
    # build/gradle/server/client would run real project
    "build_mod_jar_forge", "run_data_gen", "run_test_data",
    "run_game_test_server", "run_test_gametest", "run_test_server",
    "run_test_client", "run_server", "run_client", "start_mc_server",
    "start_mc_client", "stop_mc_process", "kill_game", "server_console",
    "wait_for_mc_ready", "wait_for_port", "wait_for_log", "tail_log",  # tail safe, but file may missing; keep maybe
    # game input / vision need real display
    "game_input", "press_key", "type_text", "screenshot", "analyze_image",
    "verify_visual_loop", "wait_for_screen",
    # network / external side effects
    "web_search", "web_fetch", "search_minecraft_docs", "download_file",
    "extract_archive",
    # process / team / task side effects
    "run_in_background", "spawn_teammate", "send_to_teammate",
    "shutdown_teammate", "claim_task", "task_create", "task_update",
    "task_clear", "request_shutdown", "respond_to_request", "submit_plan",
    "task", "todo",
    # destructive / git mutations
    "cleanup_workspace", "git_commit", "snapshot", "restore_snapshot",
    "restore_snapshot",
    # interactive / user
    "ask_user_question", "set_auto_mode",
    # activate_test_mode changes session state (safe in a process, but skip in smoke)
    "activate_test_mode",
}

SAFE_ARGS = {
    "read_file": {"path": "core/config.py", "limit": 3},
    "write_file": {"path": "data/smoke_tmp.txt", "content": "smoke\n"},
    "edit_file": {"path": "data/smoke_tmp.txt", "old_text": "smoke", "new_text": "ok"},
    "glob": {"pattern": "core/*.py"},
    "grep": {"pattern": "def ", "path": "core/config.py"},
    "bash": {"command": "echo smoke-bash"},
    "detect_environment": {},
    "validate_resources": {"modid": "NONEXISTENT_SMOKE"},
    "parse_gametest_results": {"lines": 10, "log_path": "data/NO_SUCH_GAMETEST.log"},
    "read_game_test_log": {"lines": 10, "log_path": "data/NO_SUCH_GAMETEST.log"},
    "read_crash_report": {},
    "analyze_crash": {"path": "data/NO_SUCH_CRASH.txt"},
    "parse_build_output": {"raw_text": "line\nerror: something\n"},
    "verify_artifact": {},
    "mc_status": {},
    "tail_log": {"log_path": "data/NO_SUCH.log", "lines": 5},
    "wait_for_port": {"port": 59999, "timeout": 1},
    "git_status": {},
    "git_diff": {"stat": True},
    "send_game_command": {"command": "list", "host": "127.0.0.1", "port": 25575, "password": "x"},
    "run_mod_test_cycle": {"build": False, "run_tests": False, "validate": False},
    "protocol_status": {},
    "team_status": {},
    "task_list": {},
    "task_get": {"task_id": "NONEXISTENT_SMOKE"},
    "compact": {},
    "load_skill": {"name": "forge-simple-min-mod"},
}


def main():
    log_path = Path("smoke_test_tools.log")
    names = tool_registry.names()
    passed, skipped, failed = [], [], []
    lines = []
    for name in names:
        if name in SKIP:
            skipped.append(name)
            lines.append(f"SKIP  {name}")
            continue
        args = SAFE_ARGS.get(name, {})
        try:
            out = tool_registry.execute(name, args)
            text = str(out).replace("\n", " ")[:120]
            lines.append(f"PASS  {name} | args={args} | => {text}")
            passed.append(name)
        except Exception as e:  # execute is total, but guard anyway
            lines.append(f"FAIL  {name} | {e}\n{traceback.format_exc()}")
            failed.append(name)
    footer = [
        "",
        f"TOTAL={len(names)} PASS={len(passed)} SKIP={len(skipped)} FAIL={len(failed)}",
        "SKIPPED: " + ", ".join(skipped),
    ]
    lines.extend(footer)
    log_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(footer))
    if failed:
        print("FAILED:", ", ".join(failed))
    # cleanup temp file
    try:
        Path("data/smoke_tmp.txt").unlink(missing_ok=True)
    except Exception:
        pass


if __name__ == "__main__":
    main()
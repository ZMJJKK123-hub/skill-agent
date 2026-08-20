# -*- coding: utf-8 -*-
"""Lifecycle tools for Minecraft dev server/client: start/status/stop/console."""
import os
import re
import socket
import time
from pathlib import Path

from . import process_manager as pm
from .config import logger
from .gradletools import start_gradle_task
from .tools_game import send_game_command
from .tools_runtime import worktree_manager


def _base_dir():
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _ensure_rcon_props(base, port=None, password=None):
    """Enable RCON + offline mode in run/server.properties (if the file exists or can be created)."""
    target = Path(base) / "run" / "server.properties"
    if port is None:
        port = int(os.environ.get("DSH_RCON_PORT", "25575"))
    if password is None:
        password = os.environ.get("DSH_RCON_PASSWORD", "")
    if not password:
        password = "forge123"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        props = {}
        if target.exists():
            for line in target.read_text(encoding="utf-8", errors="replace").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, _, v = line.partition("=")
                    props[k.strip()] = v.strip()
        props["enable-rcon"] = "true"
        props["rcon.port"] = str(port)
        props["rcon.password"] = password
        props["online-mode"] = "false"
        lines = [f"{k}={v}\n" for k, v in props.items()]
        target.write_text("".join(lines), encoding="utf-8")
        return str(target)
    except Exception as e:
        return f"<failed to write rcon props: {e}>"


def start_mc_server(base=None, handle="mc-server", rcon_port=None, rcon_password=None):
    base = base or _base_dir()
    setup = ""
    if rcon_port or rcon_password:
        p = _ensure_rcon_props(base, rcon_port, rcon_password)
        setup = f"\nRCON props: {p}"
    res = start_gradle_task("runServer", base, handle)
    if not res["success"]:
        return f"[start_mc_server] {res['message']}"
    return (
        f"[start_mc_server] handle={res['handle']} pid={res['pid']}\n"
        f"log={res['log_path']}{setup}\n"
        "等待就绪：用 wait_for_log(pattern='Done (') 或 wait_for_port(port=25565)。"
    )


def start_mc_client(base=None, handle="mc-client"):
    base = base or _base_dir()
    res = start_gradle_task("runClient", base, handle)
    if not res["success"]:
        return f"[start_mc_client] {res['message']}"
    return (
        f"[start_mc_client] handle={res['handle']} pid={res['pid']}\n"
        f"log={res['log_path']}\n"
        "等待就绪：用 wait_for_log 或 wait_for_screen。"
    )


def mc_status(handle=None):
    base = _base_dir()
    info = pm.list_info(base)
    if handle and handle in info:
        info = {handle: info[handle]}
    lines = [f"mc_status | tracked processes under {base}:"]
    if not info:
        lines.append("  (none tracked)")
    for h, it in info.items():
        alive = it.get("alive", True)
        state = "alive" if alive else "exited"
        lines.append(f"  {h}: pid={it.get('pid')} [{state}] kind={it.get('kind')} log={it.get('log_path')}")
    # Probe common ports
    for port, name in [(25565, "server"), (25575, "rcon")]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                lines.append(f"  port {port} ({name}): OPEN")
        except Exception:
            pass
        finally:
            s.close()
    # Tail latest relevant logs for readiness hints
    hints = []
    for handle_hint, pat in [("mc-server", r"Done \("), ("mc-client", r"Sound engine initialized|Backend library")]:
        it = info.get(handle_hint)
        if it and it.get("log_path"):
            try:
                txt = Path(it["log_path"]).read_text(encoding="utf-8", errors="replace")
                if re.search(pat, txt):
                    hints.append(f"{handle_hint}: READY ({pat})")
                tail = txt.strip().splitlines()[-5:]
                if tail:
                    hints.append(f"{handle_hint} tail: {' | '.join(t[-1] for t in tail)}")
            except Exception:
                pass
    if hints:
        lines.append("  " + "\n  ".join(hints))
    return "\n".join(lines)


def stop_mc_process(handle="all", force=True):
    base = _base_dir()
    if str(handle).lower() == "all":
        return pm.stop_all(base, force=force)
    r = pm.stop(handle, force=force, base=base)
    return r["message"]


def kill_game(handle="all"):
    return stop_mc_process(handle, force=True)


def server_console(handle="mc-server", command=None, text=None, rcon_password=None, rcon_port=25575):
    command = command or text
    if not command:
        return "Error: server_console requires 'command'"
    ok = pm.write_stdin(handle, command)
    if ok:
        return f"[server_console] sent to '{handle}' stdin: {command}"
    # Fallback to RCON
    pw = rcon_password or os.environ.get("DSH_RCON_PASSWORD")
    if pw:
        res = send_game_command(command, port=rcon_port, password=pw)
        return f"[server_console] stdin unavailable -> RCON: {res}"
    return (
        f"Error: cannot write to '{handle}' stdin and no RCON password set. "
        "Use RCON (start_mc_server with rcon_password) or enable DSH_RCON_PASSWORD."
    )
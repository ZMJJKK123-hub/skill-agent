# -*- coding: utf-8 -*-
"""Wait/read helpers: ports, log tails, and Minecraft-ready checks."""
import os
import re
import socket
import time
from collections import deque
from pathlib import Path

from . import process_manager as pm
from .tools_runtime import worktree_manager


def _base_dir():
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def wait_for_port(port, host="127.0.0.1", timeout=60):
    port = int(port)
    timeout = max(1, int(timeout))
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            if s.connect_ex((host, port)) == 0:
                return f"Port {port} open on {host}"
            last = f"closed ({host}:{port})"
        except Exception as e:
            last = str(e)
        finally:
            s.close()
        time.sleep(1)
    return f"Timeout after {timeout}s: port {port} not open ({last})"


def tail_log(log_path=None, lines=80, base=None):
    base = base or _base_dir()
    path = Path(log_path) if log_path else Path(base) / "run/logs/latest.log"
    if not path.is_absolute():
        path = Path(base) / path
    if not path.exists():
        return f"Log not found: {path}"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            tail = deque(f, maxlen=max(1, int(lines)))
        return f"--- tail {path} ({len(tail)} lines) ---\n" + "".join(tail)
    except Exception as e:
        return f"Error reading {path}: {e}"


def wait_for_mc_ready(handle="mc-server", pattern=r"Done \(", timeout=120,
                      check_port=True, port=25565):
    timeout = max(1, int(timeout))
    deadline = time.time() + timeout
    rx = re.compile(pattern, re.I)
    while time.time() < deadline:
        info = pm.get(handle)
        if info:
            proc = info["proc"]
            if proc.poll() is not None:
                return f"[wait_for_mc_ready] '{handle}' exited early (code={proc.returncode}). Log: {info['log_path']}"
            try:
                txt = Path(info["log_path"]).read_text(encoding="utf-8", errors="replace")
                if rx.search(txt):
                    return f"[wait_for_mc_ready] '{handle}' READY (matched {pattern!r})"
            except OSError:
                pass
        if check_port:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                if s.connect_ex(("127.0.0.1", int(port))) == 0:
                    return f"[wait_for_mc_ready] port {port} open"
            except Exception:
                pass
            finally:
                s.close()
        time.sleep(1)
    return f"[wait_for_mc_ready] timeout after {timeout}s waiting for {handle} ready"
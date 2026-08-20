# -*- coding: utf-8 -*-
"""Background process registry for long-running Minecraft dev processes.

Each tracked process has a stable handle (e.g. mc-server / mc-client), a Popen,
a log path, and a persisted manifest under <base>/run/.agent_processes.json so
the agent can check status without keeping Python objects in memory.
"""
import json
import os
import subprocess
import time
from pathlib import Path

_PROCESSES = {}  # handle -> {"proc": Popen, "kind": str, "base": str, "log_path": Path, "started_at": float}
_MANIFEST = ".agent_processes.json"


def _manifest_path(base) -> Path:
    return Path(base) / "run" / _MANIFEST


def _popen_alive(proc) -> bool:
    return proc.poll() is None


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except Exception:
        return False


def kill_pid(pid: int, force: bool = True) -> bool:
    """Kill a PID tree. Returns True if the kill command was accepted."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F" if force else "", "/T", "/PID", str(pid)],
                capture_output=True, timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            try:
                os.killpg(os.getpgid(pid), 9 if force else 15)
            except Exception:
                os.kill(pid, 9 if force else 15)
        return True
    except Exception:
        return False


def _load_manifest(base: str):
    try:
        p = _manifest_path(base)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_manifest(base: str):
    try:
        data = {}
        for handle, info in _PROCESSES.items():
            proc = info["proc"]
            data[handle] = {
                "pid": proc.pid,
                "kind": info["kind"],
                "base": info["base"],
                "log_path": str(info["log_path"]),
                "started_at": info["started_at"],
            }
        p = _manifest_path(base)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def register(handle: str, proc, kind: str, base: str, log_path: Path):
    """Register a running Popen under a handle and persist manifest."""
    _PROCESSES[handle] = {
        "proc": proc,
        "kind": kind,
        "base": base,
        "log_path": Path(log_path),
        "started_at": time.time(),
    }
    _save_manifest(base)


def get(handle: str):
    return _PROCESSES.get(handle)


def handles() -> list:
    return list(_PROCESSES.keys())


def list_info(base: str = None):
    """Return current in-memory processes plus anything from manifest on disk."""
    items = {}
    for handle, info in _PROCESSES.items():
        proc = info["proc"]
        items[handle] = {
            "pid": proc.pid,
            "kind": info["kind"],
            "base": info["base"],
            "log_path": str(info["log_path"]),
            "started_at": info["started_at"],
            "alive": _popen_alive(proc),
        }
    # include orphaned manifest entries that are alive but not in memory
    if base:
        for handle, data in _load_manifest(base).items():
            if handle not in items and _pid_alive(int(data.get("pid", 0))):
                items[handle] = {
                    "pid": data.get("pid"),
                    "kind": data.get("kind"),
                    "base": data.get("base"),
                    "log_path": data.get("log_path"),
                    "started_at": data.get("started_at"),
                    "alive": True,
                    "restored_from_manifest": True,
                }
    return items


def write_stdin(handle: str, text: str) -> bool:
    info = _PROCESSES.get(handle)
    if not info or info["proc"].stdin is None or info["proc"].poll() is not None:
        return False
    try:
        info["proc"].stdin.write(text.rstrip("\n") + "\n")
        info["proc"].stdin.flush()
        return True
    except Exception:
        return False


def stop(handle: str, force: bool = True, base: str = None) -> dict:
    """Stop a tracked process (tree kill on Windows). Returns result dict."""
    info = _PROCESSES.get(handle)
    result = {"handle": handle, "ok": False, "message": f"No tracked process '{handle}'"}
    if not info and base is not None:
        manifest = _load_manifest(base)
        data = manifest.get(handle)
        if data:
            pid = int(data.get("pid", 0))
            if pid and _pid_alive(pid):
                kill_pid(pid, force=force)
                manifest.pop(handle, None)
                _save_manifest(base)
                result.update({"ok": True, "message": f"Stopped orphan '{handle}' (pid={pid})"})
                return result
    if not info:
        return result
    proc = info["proc"]
    pid = proc.pid
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F" if force else "", "/T", "/PID", str(pid)],
                capture_output=True, timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            try:
                os.killpg(os.getpgid(pid), 9 if force else 15)
            except Exception:
                proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            pass
        _PROCESSES.pop(handle, None)
        _save_manifest(info["base"])
        result.update({"ok": True, "message": f"Stopped '{handle}' (pid={pid})"})
    except Exception as e:
        result.update({"message": f"Failed to stop '{handle}': {e}"})
    return result


def stop_all(base: str = None, force: bool = True) -> str:
    lines = []
    for handle in list(_PROCESSES.keys()):
        r = stop(handle, force=force)
        lines.append(r["message"])
    if base:
        for handle, data in list_info(base).items():
            if handle not in _PROCESSES:
                pid = int(data.get("pid", 0))
                if pid and _pid_alive(pid):
                    ok = kill_pid(pid, force=force)
                    lines.append(f"Killed orphan '{handle}' pid={pid}: {'ok' if ok else 'failed'}")
    return "\n".join(lines) if lines else "No running game processes."
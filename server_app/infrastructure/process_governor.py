# -*- coding: utf-8 -*-
"""进程治理（server_app/infrastructure 层）。

与会话相关的全部进程清理职责（原 server.py 的三件套迁移）：
    1. kill_stale_daemon —— server 重启后清理遗留 daemon（防双进程抢队列）；
    2. kill_session_game_processes —— 按 run/.agent_processes.json 清单杀游戏进程树；
    3. kill_java_pids_for_dir —— 杀命令行引用会话目录的 Gradle 守护 JVM；
    4. purge 系列 —— 进程清理 + 目录删除（带重试，防句柄延迟释放残留）。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from core.infrastructure.logging_.logger import get_logger

logger = get_logger("server.process_governor")

#: session_id 合法字符（防路径穿越/目录删除攻击）。
SAFE_SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def is_safe_session_id(session_id: str) -> bool:
    """输入：session_id。返回：是否可安全用作目录名（防穿越）。"""
    if not isinstance(session_id, str) or not session_id:
        return False
    if session_id in (".", ".."):
        return False
    return bool(SAFE_SESSION_ID.fullmatch(session_id))


def kill_stale_daemon(session_dir: Path) -> None:
    """杀掉上一轮 server 进程遗留的 daemon（读 .chat/daemon.pid）。

    旧 daemon 若不清理，会与新建进程同时消费同一 pending 队列（竞态）。
    kill 失败（进程已死/pid 复用）忽略并清 pid 文件。
    """
    pid_file = session_dir / ".chat" / "daemon.pid"
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return
    try:
        os.kill(pid, 15)  # Windows 上 SIGTERM 即强制终止
    except OSError:
        pass
    try:
        pid_file.unlink(missing_ok=True)
    except OSError as e:
        logger.warning("pid 文件清理失败 | path=%s | err=%s", pid_file, e)


def _taskkill_tree(pid: int) -> None:
    """输入：进程号。返回：无。职责：Windows 按进程树强杀（客户端是 gradle 的子进程）。"""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                       capture_output=True, timeout=20,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def kill_session_game_processes(session_root: Path) -> None:
    """按 run/.agent_processes.json 清单杀会话的游戏进程（chat/mod 两处清单）。"""
    for manifest in (session_root / "run" / ".agent_processes.json",
                     session_root / "mod" / "run" / ".agent_processes.json"):
        try:
            if not manifest.is_file():
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for info in (data or {}).values():
                pid = int((info or {}).get("pid", 0))
                if pid > 0:
                    _taskkill_tree(pid)
            logger.info("已按清单清理会话游戏进程: %s", manifest.parent.parent.name)
        except Exception as e:
            logger.warning("清理游戏进程清单失败（忽略）: %s %s", manifest, e)


def kill_java_pids_for_dir(dir_path: Path) -> list[int]:
    """杀命令行引用了指定目录的 java 进程（Gradle 守护；删除会话防目录锁）。"""
    killed: list[int] = []
    if os.name != "nt":
        return killed
    marker = str(dir_path).replace("/", "\\").lower()
    ps_script = (
        "Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" | "
        "ForEach-Object { \"$($_.ProcessId)|$($_.CommandLine)\" }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, text=True, timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        for line in (r.stdout or "").splitlines():
            pid_s, _, cmdline = line.strip().partition("|")
            if marker not in (cmdline or "").replace("/", "\\").lower():
                continue
            try:
                pid = int(pid_s)
            except ValueError:
                continue
            kr = subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                                capture_output=True, timeout=20,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if kr.returncode == 0:
                killed.append(pid)
    except Exception as e:
        logger.warning("枚举/杀 java 进程失败（忽略）: %s", e)
    return killed


def rmtree_with_retry(path: Path, retries: int = 3) -> None:
    """带重试的目录删除（进程刚被杀时句柄释放有延迟，立即删可能失败）。"""
    for _ in range(retries):
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        time.sleep(1.0)
    if path.exists():
        logger.warning("会话目录删除后仍有残留（文件被占用）: %s", path)


def purge_session_dir(session_dir: Path) -> None:
    """输入：会话根目录。返回：无。职责：杀清单游戏进程 + Gradle 守护 + 重试删目录。"""
    if not session_dir.exists():
        return
    kill_session_game_processes(session_dir)
    kill_java_pids_for_dir(session_dir)
    rmtree_with_retry(session_dir)

# -*- coding: utf-8 -*-
"""Shell execution tool implementation (moved from core/tools.py)."""
import os
import re
import subprocess

from . import config
from .config import logger

_MUTATING_TOKENS = [
    "del ", "rd ", "rmdir", "mkdir", "copy ", "xcopy", "move ", "ren ", "rename ",
    ">", ">>", "git add", "git commit", "pip install", "npm install", "npm i ",
    "python -m pip", "pip3 install", "conda install",
]


def _sandbox_mode() -> str:
    return getattr(config, "SANDBOX_MODE", "full-access")


def _is_mutating(command: str) -> bool:
    c = command.lower()
    return any(t in c for t in _MUTATING_TOKENS)


def _escapes_workspace(command: str) -> bool:
    """检测 cd / pushd 到工作区之外（..、根目录、盘符）。"""
    return bool(re.search(r"\b(?:cd|pushd)\s+(?:\.\.|[/\\]|[a-z]:)", command.lower()))


def run_bash(command: str) -> str:
    """执行命令并返回 stdout/stderr，含基本安全防护（Windows）。

    用 Popen + 手动 taskkill /f /t /pid 杀进程树，避免 subprocess.run 在
    shell=True 下 timeout 死锁（cmd.exe 被杀但孙子进程 node.exe 持有管道
    导致 communicate 永不返回）。
    """
    dangerous = [
        "format",
        "diskpart", "reg delete", "shutdown",
        # 致命：taskkill /im 会杀掉 Agent 自身进程（python.exe）
        "taskkill /f /im python.exe",
        "taskkill /f /im node.exe",
        "taskkill /f /im cmd.exe",
    ]
    if any(d in command.lower() for d in dangerous):
        return "Error: Dangerous command blocked"
    # 沙箱：路径级加固（full-access 不限制）
    mode = _sandbox_mode()
    if mode != "full-access":
        if _escapes_workspace(command):
            return "Error: 沙箱模式禁止越出工作区（cd .. / cd 绝对路径）"
        if mode == "read-only" and _is_mutating(command):
            return "Error: read-only 模式禁止修改性操作（del/rd/mkdir/copy/重定向/安装等）"
    # 第 12 课：cwd 跟随线程 session 基座（worktree_use 后落在 worktree 内）
    from .tools_runtime import worktree_manager
    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
    proc = subprocess.Popen(
        command, shell=True, cwd=base,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )
    try:
        out, _ = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        subprocess.run(
            f"taskkill /f /t /pid {proc.pid}",
            shell=True, capture_output=True,
        )
        try:
            out, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            out = ""
        return ("Error: Timeout (30s) — 进程树已被强杀。\n"
                "如果你在启动服务器（node server.js / npm start / python -m http.server），"
                "禁止单独执行启动命令。必须用一条组合命令完成"
                "「后台启动 → 等待 → 测试 → 杀进程」：\n"
                "  start /b cmd /c \"node server.js > server.log 2>&1\" & "
                "timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & "
                "for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a\n"
                "注意：禁止用 taskkill /f /im python.exe，会杀掉 Agent 自身。")
    out = (out or "").strip()
    return out[:50000] if out else "(no output)"

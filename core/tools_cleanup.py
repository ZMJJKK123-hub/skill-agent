# -*- coding: utf-8 -*-
"""cleanup_workspace: safe cleanup of build/runtime artifacts."""
import os
import shutil
import subprocess
from pathlib import Path

from .config import logger
from .tools_runtime import worktree_manager


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _rmtree(path: Path) -> None:
    """Delete a directory robustly (handles long Windows paths)."""
    if not path.exists():
        return
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
    if path.exists():
        full = "\\\\?\\" + str(path.resolve())
        subprocess.run(f'cmd /c rd /s /q "{full}"', shell=True, capture_output=True)


def cleanup_workspace(mode: str = "cache") -> str:
    """Remove build/runtime artifacts.

    mode:
      cache (default): build/, .gradle/, __pycache__/, agent.log
      all: cache + run/, run-data/, .worktrees/, .team/, .tasks/, .transcripts/
    """
    base = Path(_base_dir())
    removed = []

    cache_dirs = ["build", ".gradle", "__pycache__", ".pytest_cache", ".mypy_cache"]
    all_dirs = ["run", "run-data", ".worktrees", ".team", ".tasks", ".transcripts"]

    dirs_to_remove = list(cache_dirs)
    if mode == "all":
        dirs_to_remove += all_dirs

    for name in dirs_to_remove:
        p = base / name
        if p.is_dir():
            _rmtree(p)
            removed.append(name)

    file_names = ["agent.log", "hs_err_pid*.log"]
    if mode == "all":
        file_names += [".todo.json"]
    for name in file_names:
        for p in base.glob(name) if "*" in name else [base / name]:
            if p.is_file():
                try:
                    p.unlink()
                    removed.append(str(p.relative_to(base)))
                except OSError:
                    pass

    if not removed:
        return "Nothing to clean."
    return "Removed: " + ", ".join(removed)

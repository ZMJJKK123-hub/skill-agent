# -*- coding: utf-8 -*-
"""Crash report reading and analysis."""
import os
import re
from pathlib import Path

from .tools_runtime import worktree_manager


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _find_latest_crash(base: str) -> Path | None:
    candidates = []
    for root in (Path(base) / "crash-reports", Path(base) / "run" / "crash-reports"):
        if root.is_dir():
            candidates.extend(root.glob("crash-*.txt"))
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def _read_crash(max_lines: int = 120) -> str:
    base = _base_dir()
    path = _find_latest_crash(base)
    if path is None:
        return "Error: no crash report found (looked in crash-reports/ and run/crash-reports/)"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"Error: cannot read crash report {path}: {e}"
    lines = text.splitlines()
    if max_lines <= 0:
        max_lines = 120
    head = lines[:max_lines]
    return f"Crash report: {path}\n\n" + "\n".join(head)


def read_crash_report(max_lines: int = 120) -> str:
    """Read the latest crash report (first N lines)."""
    return _read_crash(max_lines)


def analyze_crash(max_lines: int = 60) -> str:
    """Extract key facts from the latest crash report."""
    base = _base_dir()
    path = _find_latest_crash(base)
    if path is None:
        return "Error: no crash report found"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return f"Error: cannot read crash report {path}: {e}"

    lines = text.splitlines()
    facts = [f"Crash report: {path}"]
    for line in lines:
        low = line.lower()
        if re.match(r"^---- minecraft crash report ----", low):
            facts.append("Header: " + line.strip())
        elif re.match(r"^// ", line):
            facts.append("Description: " + line.strip())
        elif line.startswith("Description:"):
            facts.append(line.strip())
        elif line.startswith("Exception:"):
            facts.append(line.strip())
        elif line.startswith("Caused by:"):
            facts.append(line.strip())
        elif re.match(r"^at [\w$.]+", line):
            facts.append(line.strip())
            if len([f for f in facts if f.startswith("at ")]) >= max_lines:
                break
    if len(facts) <= 1:
        facts.append("(could not extract structured facts; showing raw head)")
        facts.extend(lines[:max_lines])
    return "\n".join(facts)

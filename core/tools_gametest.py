# -*- coding: utf-8 -*-
"""parse_gametest_results: extract pass/fail summary from Forge GameTest latest.log."""
import os
import re
from pathlib import Path

from .config import logger
from .tools_runtime import worktree_manager

DEFAULT_LOG = "run/logs/latest.log"


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def _tail(path: Path, max_chars: int = 400_000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            size = f.tell()
            read_size = min(size, max_chars)
            f.seek(size - read_size)
            return f.read()
    except OSError as e:
        return f"(log read failed: {e})"


def parse_gametest_results(lines: int = 200, log_path: str = None) -> str:
    """Parse the tail of the GameTest log and return a concise pass/fail summary."""
    base = _base_dir()
    path = Path(log_path) if log_path else Path(base) / DEFAULT_LOG
    if not path.is_absolute():
        path = Path(base) / path
    if not path.exists():
        return f"Error: GameTest log not found: {path}"

    text = _tail(path)
    log_lines = text.splitlines()[-max(1, min(int(lines), 2000)):]

    passed = []
    failed = []
    errors = []
    for line in log_lines:
        low = line.lower()
        if re.search(r"\b(passed|pass)\b", low) and re.search(r"\b(test|gametest)\b", low):
            passed.append(line.strip())
        elif re.search(r"\b(failed|fail)\b", low) and re.search(r"\b(test|gametest)\b", low):
            failed.append(line.strip())
        elif re.search(r"\b(error|exception|fatal)\b", low):
            errors.append(line.strip())

    # Also try structured lines like "Test #N: ... PASSED!" / "FAILED!"
    structured_pass = [l for l in log_lines if "PASSED!" in l or "PASSED" in l]
    structured_fail = [l for l in log_lines if "FAILED!" in l or "FAILED" in l]
    if structured_pass:
        passed = structured_pass
    if structured_fail:
        failed = structured_fail

    out = [
        f"GameTest log: {path}",
        f"Tail lines scanned: {len(log_lines)}",
        f"Passed entries: {len(passed)}",
        f"Failed entries: {len(failed)}",
        f"Error/exception lines: {len(errors)}",
    ]
    if failed:
        out.append("")
        out.append("FAILED TESTS:")
        for f_ in failed[-20:]:
            out.append(f"  - {f_[:300]}")
    if passed:
        out.append("")
        out.append("PASSED TESTS (last 20):")
        for p_ in passed[-20:]:
            out.append(f"  - {p_[:300]}")
    if errors:
        out.append("")
        out.append("ERROR/EXCEPTION LINES (last 20):")
        for e_ in errors[-20:]:
            out.append(f"  - {e_[:300]}")

    # Determine overall verdict
    if failed or errors:
        out.append("")
        out.append("RESULT: FAIL")
    elif passed:
        out.append("")
        out.append("RESULT: PASS")
    else:
        out.append("")
        out.append("RESULT: UNKNOWN (no clear pass/fail markers found; check full log)")
    return "\n".join(out)

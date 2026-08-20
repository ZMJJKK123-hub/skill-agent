# -*- coding: utf-8 -*-
"""Self-loop orchestration helpers: build diagnostics + one-call MOD test cycle."""
import os
import re
from pathlib import Path

from .gradletools import GRADLE_TOOLS
from .tools_gametest import parse_gametest_results
from .tools_mod import _forge_build_jar
from .tools_runtime import worktree_manager
from .tools_validate import validate_resources


def _base_dir():
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def parse_build_output(log_path=None, raw_text=None, base=None):
    """Extract compile errors and FAILED tasks from Gradle build output."""
    base = base or _base_dir()
    text = raw_text or ""
    if not text and log_path:
        path = Path(log_path)
        if not path.is_absolute():
            path = Path(base) / path
        if not path.resolve().is_relative_to(Path(base).resolve()):
            return f"Error: log_path 越出工作区: {path}"
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
    if not text:
        return "Error: parse_build_output needs log_path or raw_text"
    lines = text.splitlines()
    errors = []
    failed_tasks = []
    for line in lines:
        if re.search(r"(?i)\berror:\s*[^\n]+", line) or re.search(r"\.java:\d+:\s*error", line) or "错误:" in line or "找不到符号" in line or "无法解析" in line or "does not exist" in line or "cannot find symbol" in line:
            errors.append(line.strip())
        elif re.search(r">\s*Task\s+:.*\bFAILED\b", line):
            failed_tasks.append(line.strip())
        elif re.search(r"BUILD FAILED", line):
            failed_tasks.append(line.strip())
    out = [f"Build errors: {len(errors)}", f"Failed tasks: {len(failed_tasks)}"]
    if errors:
        out.append("")
        out.append("ERRORS (first 30):")
        for e in errors[:30]:
            out.append(f"  {e[:400]}")
    if failed_tasks:
        out.append("")
        out.append("FAILED TASKS:")
        for t in failed_tasks[-20:]:
            out.append(f"  {t[:400]}")
    if not errors and not failed_tasks:
        out.append("  (no obvious compile/FAILED markers; check full output)")
    return "\n".join(out)


def run_mod_test_cycle(modid=None, validate=True, build=True, run_tests=True,
                       build_timeout=900, test_timeout=180, base=None):
    """One-call verifier: validate resources -> build jar -> run GameTest -> parse results."""
    base = base or _base_dir()
    out = [f"=== MOD TEST CYCLE === base={base}"]
    result_ok = True

    if validate:
        out.append("")
        out.append("--- [1/3] validate_resources ---")
        v = validate_resources(modid)
        out.append(v)
        if "RESULT: FAIL" in v:
            result_ok = False

    if build:
        out.append("")
        out.append("--- [2/3] build_mod_jar_forge ---")
        b = _forge_build_jar({"gradle_task": "build"})
        out.append(b)
        if "[build] Gradle 构建失败" in b or "BUILD FAILED" in b:
            result_ok = False
            diag = parse_build_output(raw_text=b)
            out.append("")
            out.append("Build diagnosis:")
            out.append(diag)

    if run_tests:
        out.append("")
        out.append("--- [3/3] run_test_gametest ---")
        t = GRADLE_TOOLS["run_test_gametest"](base, timeout=test_timeout)
        summary = t.get("summary", "")
        out.append(summary)
        parsed = parse_gametest_results()
        out.append(parsed)
        if not t.get("success") or "RESULT: FAIL" in parsed:
            result_ok = False

    out.append("")
    out.append("RESULT: PASS" if result_ok else "RESULT: FAIL")
    return "\n".join(out)
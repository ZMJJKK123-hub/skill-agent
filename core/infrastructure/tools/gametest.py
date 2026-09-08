# -*- coding: utf-8 -*-
"""parse_gametest_results: extract pass/fail summary from Forge GameTest latest.log."""
import os
import re
from pathlib import Path

from .runtime import worktree_manager

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


def _classify_log_lines(log_lines: list) -> tuple[list, list, list]:
    """输入：日志行列表。返回：(passed, failed, errors) 三组行。

    职责：按关键词分类 + 结构化 PASSED!/FAILED! 行优先覆盖。
    """
    passed, failed, errors = [], [], []
    for line in log_lines:
        low = line.lower()
        if re.search(r"\b(passed|pass)\b", low) and re.search(r"\b(test|gametest)\b", low):
            passed.append(line.strip())
        elif re.search(r"\b(failed|fail)\b", low) and re.search(r"\b(test|gametest)\b", low):
            failed.append(line.strip())
        elif re.search(r"\b(error|exception|fatal)\b", low):
            errors.append(line.strip())
    # 结构化行（"Test #N: ... PASSED!"）优先于关键词模糊匹配
    structured_pass = [l for l in log_lines if "PASSED!" in l or "PASSED" in l]
    structured_fail = [l for l in log_lines if "FAILED!" in l or "FAILED" in l]
    if structured_pass:
        passed = structured_pass
    if structured_fail:
        failed = structured_fail
    return passed, failed, errors


def _render_gametest_summary(path, log_lines, passed, failed, errors) -> str:
    """输入：路径与三组分类行。返回：渲染好的汇总文本（含 RESULT 判定）。

    判定规则：只有失败条目才 FAIL；passed 与 error 并存按 PASS 算
    （数据包解析 ERROR 噪音不掩盖绿灯，红宝石剑会话实测误报）。
    """
    out = [
        f"GameTest log: {path}",
        f"Tail lines scanned: {len(log_lines)}",
        f"Passed entries: {len(passed)}",
        f"Failed entries: {len(failed)}",
        f"Error/exception lines: {len(errors)}",
    ]
    for title, group in (("FAILED TESTS:", failed),
                         ("PASSED TESTS (last 20):", passed),
                         ("ERROR/EXCEPTION LINES (last 20):", errors)):
        if group:
            out.append("")
            out.append(title)
            for l in group[-20:]:
                out.append(f"  - {l[:300]}")
    if failed:
        verdict = "FAIL"
    elif passed:
        verdict = "PASS"
    elif errors:
        verdict = "FAIL"
    else:
        verdict = "UNKNOWN (no clear pass/fail markers found; check full log)"
    out += ["", f"RESULT: {verdict}"]
    return "\n".join(out)


def _resolve_log_path(log_path) -> tuple[Path, str | None]:
    """解析日志路径（默认 run/logs/latest.log；相对挂基座；沙箱校验）。

    Returns:
        (路径, 错误消息或 None)。
    """
    base = _base_dir()
    path = Path(log_path) if log_path else Path(base) / DEFAULT_LOG
    if not path.is_absolute():
        path = Path(base) / path
    if not path.resolve().is_relative_to(Path(base).resolve()):
        return path, f"Error: log_path 越出工作区: {path}"
    if not path.exists():
        return path, f"Error: GameTest log not found: {path}"
    return path, None


def parse_gametest_results(lines: int = 200, log_path: str = None) -> str:
    """Parse the tail of the GameTest log and return a concise pass/fail summary.

    Calls: _resolve_log_path / _classify_log_lines / _render_gametest_summary。
    """
    path, err = _resolve_log_path(log_path)
    if err:
        return err

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

    # Determine overall verdict: 显式通过优先。只有失败条目才判 FAIL；
    # passed 与 error 并存时（数据包解析 ERROR + 测试全过）按 PASS 算，
    # 否则配方格式类噪音会把绿灯判成红灯（红宝石剑会话实测误报）。
    if failed:
        out.append("")
        out.append("RESULT: FAIL")
    elif passed:
        out.append("")
        out.append("RESULT: PASS")
    elif errors:
        out.append("")
        out.append("RESULT: FAIL")
    else:
        out.append("")
        out.append("RESULT: UNKNOWN (no clear pass/fail markers found; check full log)")
    return "\n".join(out)

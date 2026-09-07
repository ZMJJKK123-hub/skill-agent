# -*- coding: utf-8 -*-
"""会话收尾知识沉淀（server_app/services 层）。

两个"自动沉淀"职责（原 run_task.py 内的 finalize_* 函数迁移）：
    1. finalize_known_issues —— 把本次 run.log 的错误信号聚类去重后
       追加进会话的 mod/KNOWN_ISSUES.md（agent 只读，新坑由系统落账）；
    2. finalize_error_list —— 把 NEW_ERROR: 结构化行/常规错误信号追加进
       共享 docs/agent/ERROR_LIST.md。
两者都只追加、绝不覆盖旧条目。
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from core.infrastructure.logging_.logger import get_logger

logger = get_logger("finalizers")

#: 错误信号行特征（KNOWN_ISSUES 收集用）。
_SIGNAL_PATTERN = re.compile(
    r"(?:ERROR|Error|Exception|BUILD FAILED|Failed|失败|超时|Timeout|"
    r"Crash|错误|PKIX|SSLHandshake|NoClassDefFound|ClassCastException)", re.I)

#: 根因聚类优先特征（构建工具名/异常类型，防时间戳把同类错误拆散）。
_CLUSTER_PRIMARY = re.compile(
    r"\b(Gradle|Maven|PKIX|SSLHandshake|forgeGradle|compileJava|"
    r"Cannot find symbol|NoClassDefFound|ClassCastException)\b", re.I)

#: ERROR_LIST 兜底收集的常规错误特征。
_ERROR_LIST_PATTERN = re.compile(
    r"(?i)(:\s*error:|exception|build failed|failed to|cannot find symbol|"
    r"not found|invalid mod|missing language|supported_formats|mandatory=true)")


def _read_safe(path: Path) -> str | None:
    """输入：文件路径。返回：全文（缺失/IO 错误返回 None 并记日志）。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        logger.warning("读取失败 | path=%s | err=%s", path, e)
        return None


def _normalize_signal(raw: str) -> str:
    """输入：原始日志行。返回：去时间戳/地址/行号后的归一化信号。"""
    s = re.sub(r"0x[0-9a-fA-F]+", "<addr>", raw)
    s = re.sub(r"\b\d{1,2}:\d{2}:\d{2}(?:[.,]\d+)?\b", "", s)
    s = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _cluster_key(s: str) -> str:
    """输入：归一化信号。返回：聚类键（根因特征词；泛关键词无区分度）。"""
    m = _CLUSTER_PRIMARY.search(s)
    if m:
        return m.group(1).lower()
    m = re.search(r"([A-Za-z_][\w.]*Exception|[A-Za-z_][\w.]*Error)", s)
    if m:
        return m.group(1)
    # 注意：此 pattern 必须带捕获组——旧版无组调 group(1) 抛 IndexError
    # 导致整个收尾静默失败（d70b3f408f53 实测每轮收尾都崩）。
    m = re.match(r"([A-Za-z_][\w.]*)", s)
    return m.group(1) if m else "other"


def finalize_known_issues(session_dir: Path, project_root: Path) -> None:
    """把 run.log 错误信号聚类去重后追加进 mod/KNOWN_ISSUES.md。

    Args:
        session_dir: 会话根目录（run.log 与 mod/ 的父目录）。
        project_root: 仓库根（日志上下文用）。
    Globals Used: 无。
    Calls: _read_safe / _normalize_signal / _cluster_key。
    """
    issues_path = session_dir / "mod" / "KNOWN_ISSUES.md"
    log_path = session_dir / "run.log"
    if not issues_path.exists() or not log_path.exists():
        return
    existing = _read_safe(issues_path)
    log_text = _read_safe(log_path)
    if existing is None or log_text is None:
        return
    signals = [s for s in (_normalize_signal(l) for l in log_text.splitlines()
                           if _SIGNAL_PATTERN.search(l)) if len(s) >= 25][:40]
    clusters: dict[str, list[str]] = {}
    for s in signals:
        clusters.setdefault(_cluster_key(s), []).append(s)
    for g in ("error", "failed", "exception", "other"):  # 泛键无区分度
        clusters.pop(g, None)
    existing_lower = existing.lower()
    today = datetime.now().strftime("%Y-%m-%d")
    added = []
    for key, samples in clusters.items():
        if key.lower() in existing_lower:
            continue
        added.append(
            f"## [{today}] {key}（自动记录，来自本次 run.log）\n"
            f"- 症状: {samples[0][:200]}\n"
            f"- 根因: 自动记录待确认（见会话 run.log，同类信号 {len(samples)} 条）\n"
            f"- 规避: 优先参考本文件既有条目与已加载的 skills；若是本会话新问题，"
            f"需下次会话在相同场景下验证后补充确认。\n")
    if not added:
        return
    sep = "" if existing.endswith("\n\n") else "\n\n"
    try:
        issues_path.write_text(existing + sep + "\n".join(added), encoding="utf-8")
    except OSError as e:
        logger.error("KNOWN_ISSUES 写回失败 | err=%s", e)
        return
    logger.info("已追加 %d 条错误记录到 mod/KNOWN_ISSUES.md", len(added))


def finalize_error_list(session_dir: Path, project_root: Path) -> None:
    """把本次运行新错误追加到 docs/agent/ERROR_LIST.md（共享知识库）。

    优先 NEW_ERROR: 结构化行；无则退化为常规错误信号（上限 10 条）。

    Args:
        session_dir: 会话根目录（run.log 所在）。
        project_root: 仓库根（ERROR_LIST.md 所在）。
    """
    log_path = session_dir / "run.log"
    target = project_root / "docs" / "agent" / "ERROR_LIST.md"
    log_text = _read_safe(log_path)
    if log_text is None:
        return
    existing = _read_safe(target) or ""
    existing_lower = existing.lower()
    new_entries: list[str] = []
    seen: set[str] = set()

    for raw in log_text.splitlines():  # 1) 结构化 NEW_ERROR: 行
        m = re.search(r"NEW_ERROR:\s*(.+)", raw, re.I)
        if not m:
            continue
        body = m.group(1).strip()
        if body and body.lower() not in existing_lower and body not in seen:
            seen.add(body)
            new_entries.append(f"- **Auto-recorded:** {body}")

    if not new_entries:  # 2) 兜底：常规错误信号
        for raw in log_text.splitlines():
            if len(new_entries) >= 10:
                break
            if not _ERROR_LIST_PATTERN.search(raw):
                continue
            sample = re.sub(r"\s+", " ", raw).strip()[:220]
            if len(sample) < 20 or sample.lower() in existing_lower or sample in seen:
                continue
            seen.add(sample)
            new_entries.append(f"- **Auto-recorded:** {sample}")

    if not new_entries:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    section = (f"\n## {today} Auto-recorded from runtime\n\n"
               + "\n".join(new_entries) + "\n")
    try:
        if not existing.endswith("\n"):
            existing += "\n"
        with target.open("a", encoding="utf-8") as f:
            f.write(section)
        logger.info("已追加 %d 条到 docs/agent/ERROR_LIST.md", len(new_entries))
    except OSError as e:
        logger.error("ERROR_LIST 写回失败 | err=%s", e)

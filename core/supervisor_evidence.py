# -*- coding: utf-8 -*-
"""监管证据采集（由 supervisor.py 拆出）。

类职责：定位最新 run.log / 读尾部 / 任务板快照 / transcript 尾部；
全部只读、无 self 状态，纯函数便于单测。
生命周期：仅 SupervisorManager._analyze_once 调用。
"""
from pathlib import Path

from .config import logger  # 统一日志
from .infrastructure.tools import task_manager  # 任务板快照

#: transcript 取尾部行数（原 supervisor 模块常量迁出）
SUPERVISOR_TRANSCRIPT_TAIL = 30


def _project_root() -> Path:
    """项目根（基于 __file__，抗 cwd chdir——同 supervisor 修复注释）。"""
    return Path(__file__).resolve().parents[1]


    # ── 证据采集 ──
def resolve_run_log() -> Path | None:
    """定位最新会话的 run.log（基于项目根，抗 cwd chdir）。

    run_task.py 会把 cwd chdir 到 <session>/mod，因此不能用相对路径。
    优先取 <项目根>/data/sessions/*/run.log 里最新修改的那个；
    回退到 <项目根>/run.log。
    """
    base = _project_root() / "data" / "sessions"
    if base.exists():
        cands = sorted(base.glob("*/run.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands:
            return cands[0]
    root = _project_root() / "run.log"
    return root if root.exists() else None

def tail(path: Path, chars: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        text = "\n".join(lines[-200:])
        return text[-chars:]
    except OSError as e:
        return f"(run.log 读取失败: {e})"

def tasks_summary() -> str:
    try:
        tasks = task_manager.list_tasks()
        if not tasks:
            return "(task board empty)"
        lines = [f"- #{t.get('id')} [{t.get('status', '?')}] {t.get('subject', '')[:80]}" for t in tasks]
        return "\n".join(lines)
    except Exception:
        return "(task board unavailable)"

def transcript_tail() -> str | None:
    base = _project_root() / ".transcripts"
    if not base.exists():
        return None
    files = sorted(base.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None
    try:
        lines = files[0].read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-SUPERVISOR_TRANSCRIPT_TAIL:])
    except OSError:
        return None

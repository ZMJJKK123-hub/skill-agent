# -*- coding: utf-8 -*-
"""WorktreeManager 的运行与恢复方法族（由 manager.py 拆出，Mixin 模式）。

类职责：run_in_worktree 命令执行 / worktree_use 切换 / resolve_dir
基座解析 / _find_incomplete_ops + recover 崩溃恢复 / 列表渲染。
生命周期：WorktreeManager(manager.py) 继承组合；单例构建在
infrastructure/tools/runtime.py。
"""
import json
import subprocess
from pathlib import Path  # 命令/路径类型

from ..config import logger


class WorktreeRunMixin:
    """运行/切换/恢复/列表方法族（self 依赖 manager.py 的注册基座）。"""

    def run_in_worktree(self, task_id: int, command: str) -> str:
        """显式在任务的 worktree 目录中执行命令（不改变 session 基座）。

        沿用 run_bash 的 Windows Popen + taskkill 模式：
        timeout 时杀整棵进程树，避免 cmd.exe 死锁。
        """
        wt_path = self._get_worktree_path(task_id)
        if not wt_path or not wt_path.exists():
            raise ValueError(f"No active worktree for task {task_id}")
        proc = subprocess.Popen(
            command, shell=True, cwd=str(wt_path),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env={**__import__("os").environ,
                 "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        try:
            out, _ = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            from ..process_manager import kill_pid
            kill_pid(proc.pid)
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"kill 后 5s 仍未退出（放弃回收） | pid={proc.pid}")
            return "Error: run_in_worktree timeout (120s), process tree killed"
        out = (out or "").strip()
        logger.info(
            f"WorktreeManager.run_in_worktree | task #{task_id} | cmd={command[:100]} | "
            f"out_len={len(out)}"
        )
        return out[:50000] if out else "(no output)"

    def worktree_use(self, task_id: int | None) -> str:
        """切换当前线程的 session 工作基座（线程隔离）。

        task_id=None 或 0 → 切回项目根目录（主平面）。
        切换后，bash 的 cwd、read_file/write_file/edit_file 的路径基座
        都指向该 worktree——当前线程的所有文件操作都隔离在 worktree 内。
        用 threading.local 存放，Leader / 每个 teammate 线程互不影响。
        """
        if task_id is None or task_id == 0:
            self._local.base = None
            logger.info(f"WorktreeManager.worktree_use | 切回主目录 {self.project_root}")
            return f"已切换到主目录（工具基座 = {self.project_root}）"
        wt_path = self._get_worktree_path(task_id)
        if not wt_path or not wt_path.exists():
            return (
                f"Error: No active worktree for task {task_id}. "
                f"请先用 worktree_create(task_id={task_id}) 创建。"
            )
        self._local.base = str(wt_path)
        logger.info(f"WorktreeManager.worktree_use | task #{task_id} → 基座 {wt_path}")
        return (
            f"已切换到 worktree: {wt_path}\n"
            f"后续 bash / read_file / write_file / edit_file 均作用于该目录（线程隔离）。"
        )

    def resolve_dir(self) -> str:
        """返回当前线程的工具操作基座目录。

        tools.py 的 run_bash(cwd)、run_read/write/edit(safe_path base) 都调用它：
        worktree_use 切到 worktree → 所有操作落在 worktree 内；
        否则落在项目根目录（与 s11 行为一致）。
        """
        base = getattr(self._local, "base", None)
        return base if base else str(self.project_root)

    # ── 崩溃恢复 ──────────────────────────────────────────


    def _find_incomplete_ops(self) -> list:
        """扫描事件流，找未闭合的 before 事件（before 无 after/failed 配对）。

        这是"崩溃到一半"的证据：操作已开始但没完成。
        """
        events_path = self._events_path()
        if not events_path.exists():
            return []
        before_events = {}
        with open(events_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                etype = event.get("type", "")
                tid = event.get("task_id", "")
                if etype.endswith(".before"):
                    before_events[f"{etype}:{tid}"] = event
                elif etype.endswith(".after") or etype.endswith(".failed"):
                    base = etype.rsplit(".", 1)[0]
                    before_events.pop(f"{base}.before:{tid}", None)
        return list(before_events.values())

    def recover(self) -> dict:
        """从 .tasks/ + index.json + 磁盘重建现场。两个数据源交叉比对。

        返回 issues 汇总：
          incomplete_ops   事件流有 before 无 after/failed（半完成操作）
          orphaned_worktrees  注册表↔磁盘不一致的记录
          recovered       注册表 + 磁盘都完好的 worktree
        """
        issues = {"orphaned_worktrees": [], "incomplete_ops": [], "recovered": []}
        # 1. 事件流：未闭合的 before 事件
        pending_ops = self._find_incomplete_ops()
        for op in pending_ops:
            issues["incomplete_ops"].append(op)
            if op.get("type") == "worktree.create.before":
                # 创建到一半崩溃 → 清理残留目录 + 注销
                tid = op.get("task_id")
                partial_path = self.worktrees_dir / f"task-{tid}"
                if partial_path.exists():
                    subprocess.run(
                        ["git", "worktree", "remove", str(partial_path), "--force"],
                        cwd=str(self.project_root), capture_output=True, text=True,
                    )
                    logger.info(f"WorktreeManager.recover | 清理半创建 worktree {partial_path}")
                self._unregister_worktree(tid)
                logger.info(
                    f"WorktreeManager.recover | 已回滚半完成创建 | task #{tid}"
                )
        # 2. index.json 有，磁盘没有 → 孤儿记录，注销
        index = self._load_index()
        for wt_id, wt_info in list(index.items()):
            wt_path = Path(wt_info["path"])
            if not wt_path.exists():
                self._unregister_worktree(wt_info["task_id"])
                issues["orphaned_worktrees"].append(wt_id)
                logger.info(f"WorktreeManager.recover | 孤儿注册记录已注销: {wt_id}")
            else:
                issues["recovered"].append(wt_id)
        # 3. 磁盘有，index.json 没有 → 孤儿目录，标记
        if self.worktrees_dir.exists():
            for dir_path in self.worktrees_dir.iterdir():
                if dir_path.is_dir() and dir_path.name not in index:
                    issues["orphaned_worktrees"].append(dir_path.name)
                    logger.info(f"WorktreeManager.recover | 发现孤儿目录: {dir_path.name}")
        logger.info(
            f"WorktreeManager.recover 完成 | incomplete={len(issues['incomplete_ops'])} | "
            f"orphaned={len(issues['orphaned_worktrees'])} | "
            f"recovered={len(issues['recovered'])}"
        )
        return issues

    # ── 查询 ─────────────────────────────────────────────
    def list_active(self) -> list:
        """返回所有 active 状态的 worktree。"""
        return [
            info for info in self._load_index().values()
            if info.get("status") == "active"
        ]

    def render_list(self) -> str:
        """渲染注册表全景，供模型查看隔离状态。"""
        index = self._load_index()
        if not index:
            return "(no worktrees)"
        lines = ["🌲 Worktree Registry:"]
        for wt_id, info in index.items():
            exists = "✓" if Path(info["path"]).exists() else "✗(missing)"
            lines.append(
                f"  {wt_id} | task #{info['task_id']} | {info['branch']} | "
                f"{info['status']} | {exists} | repo={info.get('repo', '?')} | "
                f"{info.get('created_at', '')[:19]}"
            )
        return "\n".join(lines)

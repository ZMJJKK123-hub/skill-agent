# -*- coding: utf-8 -*-
"""WorktreeManager：git worktree 隔离 + Task 双状态机联动 + 崩溃恢复。
由 worktree.py 原样迁出。
"""
import json
import logging
import subprocess
import threading

from .index_ops import WorktreeIndexMixin  # 索引/注册基座（拆分模块）
from .runtime_ops import WorktreeRunMixin  # 运行/恢复域（拆分模块）
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("agent")


class WorktreeManager(WorktreeIndexMixin, WorktreeRunMixin):
    """管理 git worktree 生命周期，与 TaskManager 联动（控制面 ↔ 执行面）。"""

    def __init__(self, project_root: str, task_manager):
        # 统一解析为绝对路径：git worktree add 的相对路径是相对 cwd 解析的，
        # 若 project_root 是相对路径会与调用方的路径基准不一致（双重嵌套）。
        # 绝对路径保证 worktree_create 传给 git 的路径 = 注册表/检查用的路径。
        self.project_root = Path(project_root).resolve()
        self.worktrees_dir = self.project_root / ".worktrees"
        self.tasks_dir = self.project_root / ".tasks"
        self.task_manager = task_manager
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        # 注册表 / 事件流的并发写锁（teammate 多线程同时 create/remove）
        self._io_lock = threading.Lock()
        # 线程本地 session 基座：worktree_use 只影响当前线程
        # （Leader 主线程、每个 teammate 线程各有自己的工作目录，互不覆盖）
        self._local = threading.local()
        logger.info(
            f"WorktreeManager 初始化 | project_root={self.project_root} | "
            f"worktrees_dir={self.worktrees_dir} | tasks_dir={self.tasks_dir}"
        )

    # ── 注册表（.worktrees/index.json）──────────────────────────
    def worktree_create(self, task_id: int, branch: str | None = None,
                        repo: str | None = None) -> str:
        """创建 worktree 并绑定到任务，自动推进任务到 in_progress。

        Bug B 修复：新增 repo 参数——指定在哪个 git 仓库下建 worktree
        （例如 demo/demo-s12 子仓库），worktree 目录落在 <repo>/.worktrees/。
        不传则与课文一致，建在 project_root/.worktrees/。

        一个方法做三件事（双状态机联动）：
          1. git worktree add 创建独立工作目录（执行面）
          2. 注册到 index.json（控制面，记录实际 repo 根）
          3. 任务 pending → in_progress（控制面）
        调用方只需要一行代码。
        """
        repo_root = self._resolve_repo(repo)
        branch = branch or f"task-{task_id}"
        wt_path = repo_root / ".worktrees" / f"task-{task_id}"
        self._emit("worktree.create.before", task_id=task_id, branch=branch,
                   repo=str(repo_root))
        try:
            subprocess.run(
                ["git", "worktree", "add", str(wt_path), "-b", branch],
                cwd=str(repo_root),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self._register_worktree(task_id, branch, str(wt_path), repo_root)
            # 双状态机联动点①：绑定 worktree → 任务自动 in_progress
            self.task_manager.update_status(task_id, "in_progress")
            self._emit("worktree.create.after", task_id=task_id, path=str(wt_path),
                       repo=str(repo_root))
            logger.info(
                f"WorktreeManager.worktree_create 成功 | task #{task_id} → {wt_path} "
                f"(branch={branch}, repo={repo_root}) | 任务状态 → in_progress"
            )
            return str(wt_path)
        except subprocess.CalledProcessError as e:
            self._emit(
                "worktree.create.failed", task_id=task_id,
                error=(e.stderr or str(e)).strip(),
                repo=str(repo_root),
            )
            logger.exception(
                f"WorktreeManager.worktree_create 失败 | task #{task_id} | "
                f"{(e.stderr or str(e)).strip()}"
            )
            raise

    def _merge_branch(self, task_id: int, branch: str) -> None:
        """把 worktree 分支合并回其所属仓库的主分支（先提交 worktree 改动）。

        Bug B 修复：merge 的目标是 worktree 所属的仓库（repo），
        而不是 project_root——否则子仓库场景会 merge 到错误的仓库。
        """
        info = self._get_worktree_info(task_id)
        repo_root = self._repo_of(info)
        self._emit("worktree.merge.before", task_id=task_id, branch=branch,
                   repo=str(repo_root))
        wt_path = self._get_worktree_path(task_id)
        if wt_path and wt_path.exists():
            # 1. 提交 worktree 内的全部改动（若无改动，git commit 报错，忽略即可）
            subprocess.run(
                ["git", "add", "-A"], cwd=str(wt_path),
                capture_output=True, text=True,
            )
            commit = subprocess.run(
                ["git", "commit", "-m", f"task-{task_id}: work from worktree"],
                cwd=str(wt_path), capture_output=True, text=True,
            )
            if commit.returncode == 0:
                logger.info(f"WorktreeManager._merge_branch | {branch} 已提交改动")
            else:
                logger.info(
                    f"WorktreeManager._merge_branch | {branch} 无改动可提交"
                    f"（{commit.stderr.strip()[:100]}）"
                )
        # 2. 在所属仓库把该分支 merge 回来（--no-ff 保留合并记录）
        merge = subprocess.run(
            ["git", "merge", "--no-ff", branch, "-m", f"Merge {branch} (task #{task_id})"],
            cwd=str(repo_root), capture_output=True, text=True,
        )
        if merge.returncode != 0:
            self._emit("worktree.merge.failed", task_id=task_id,
                       error=(merge.stderr or str(merge)).strip())
            raise RuntimeError(
                f"Merge branch {branch} failed: {(merge.stderr or merge.stdout).strip()}"
            )
        self._emit("worktree.merge.after", task_id=task_id, branch=branch,
                   repo=str(repo_root))
        logger.info(f"WorktreeManager._merge_branch | {branch} 已合并回 {repo_root}")

    def worktree_remove(self, task_id: int,
                        complete_task: bool = True, merge: bool = False) -> None:
        """拆除 worktree（双状态机联动点②）。

        complete_task=True → 任务 in_progress → completed
        merge=True         → 先把 worktree 分支合并回所属仓库主分支，再拆除
        Bug B 修复：git 命令在 worktree 所属仓库（repo）上执行，
        而不是 project_root——子仓库场景下拆错仓库会失败。
        一个调用搞定四件事：完成任务(可选) + 拆目录 + 注销注册 + 清理分支。
        """
        info = self._get_worktree_info(task_id)
        repo_root = self._repo_of(info)
        self._emit("worktree.remove.before", task_id=task_id,
                   complete_task=complete_task, merge=merge, repo=str(repo_root))
        # 1. 可选：合并 worktree 分支回所属仓库主分支
        if merge and info:
            self._merge_branch(task_id, info["branch"])
        # 2. 可选：完成任务
        if complete_task:
            self.task_manager.update_status(task_id, "completed")
            self._emit("task.completed", task_id=task_id)
        # 3. 移除 git worktree 目录（--force：即使有未提交改动也删）
        wt_path = self._get_worktree_path(task_id)
        if wt_path and wt_path.exists():
            subprocess.run(
                ["git", "worktree", "remove", str(wt_path), "--force"],
                cwd=str(repo_root), capture_output=True, text=True,
            )
            logger.info(f"WorktreeManager.worktree_remove | 已移除目录 {wt_path}")
        # 4. 清理分支（-d 只删已合并分支；未合并失败则忽略，分支留着无碍）
        subprocess.run(
            ["git", "branch", "-d", f"task-{task_id}"],
            cwd=str(repo_root), capture_output=True, text=True,
        )
        # 5. 从注册表注销
        self._unregister_worktree(task_id)
        self._emit("worktree.remove.after", task_id=task_id, repo=str(repo_root))
        logger.info(f"WorktreeManager.worktree_remove 完成 | task #{task_id}")

    # ── 执行（在 worktree 内跑命令 / 切换 session 基座）──────────

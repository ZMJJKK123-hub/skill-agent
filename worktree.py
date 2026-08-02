"""s12 — Worktree + Task Isolation：终极隔离

双平面架构（控制面与执行面分离）：
  控制面  .tasks/     任务状态 + 事件流（调度与审计）
  执行面  .worktrees/ git worktree 独立工作目录（并行干活）

双状态机（各自独立生命周期，通过绑定关系联动）：
  Task       pending → in_progress → completed（s07 沿用，绑定 worktree 时联动推进）
  Worktree   absent  → active        → removed / kept（新增）

绑定联动：
  worktree_create(task_id)                 → 创建目录 + 注册 + Task→in_progress
  worktree_remove(task_id, complete_task=True)
                                           → Task→completed + 拆目录 + 注销 + 清分支（可选 merge 回主分支）

线程隔离（s12 对 s9-11 并发队友的关键适配）：
  worktree_use 用 threading.local 存 session 基座——每个 teammate 线程
  各有自己的工作目录，Leader / 队友 / 队友之间互不覆盖。
  这正是第 12 课的核心：文件系统级隔离，杜绝共享目录静默覆盖。

崩溃恢复：
  .tasks/events.jsonl 记录每个操作的 before/after 事件对。重启时交叉比对
  事件流 + 注册表(index.json) + 磁盘实际状态，重建现场：
    - 事件流有 before 无 after → 半完成操作 → 回滚
    - 注册表有但磁盘无 → 孤儿记录 → 清理
    - 磁盘有但注册表无 → 孤儿目录 → 标记

设计约束：本模块不 import tools.py（TaskManager 由构造参数注入），
因此 can 被 tools.py 直接 import，无循环依赖。
"""

import json
import logging
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("agent")


class WorktreeManager:
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
    def _index_path(self) -> Path:
        return self.worktrees_dir / "index.json"

    def _load_index(self) -> dict:
        """读取注册表。返回 {worktree_id: info}。文件不存在返回空 dict。"""
        path = self._index_path()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.loads(f.read()).get("worktrees", {})
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"WorktreeManager._load_index 读取失败({e})，按空注册表处理")
                return {}
        return {}

    def _save_index(self, worktrees: dict) -> None:
        """原子写注册表（先写临时文件再替换，避免崩溃留下半截 JSON）。"""
        tmp = self._index_path().with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"worktrees": worktrees}, f, indent=2, ensure_ascii=False)
        tmp.replace(self._index_path())
        logger.info(
            f"WorktreeManager._save_index | 已保存 {len(worktrees)} 条注册记录"
        )

    def _register_worktree(self, task_id: int, branch: str, path: str) -> None:
        """登记 worktree 元信息（status=active）。"""
        with self._io_lock:
            index = self._load_index()
            index[f"task-{task_id}"] = {
                "task_id": task_id,
                "branch": branch,
                "path": path,
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_index(index)
        logger.info(f"WorktreeManager._register_worktree | task #{task_id} | branch={branch}")

    def _unregister_worktree(self, task_id: int | str) -> None:
        """从注册表移除 worktree 记录。"""
        key = f"task-{task_id}" if not str(task_id).startswith("task-") else str(task_id)
        with self._io_lock:
            index = self._load_index()
            if key in index:
                del index[key]
                logger.info(f"WorktreeManager._unregister_worktree | 注销 {key}")
            self._save_index(index)

    def _get_worktree_path(self, task_id: int) -> Path | None:
        """按 task_id 查 worktree 路径；没有返回 None。"""
        info = self._load_index().get(f"task-{task_id}")
        return Path(info["path"]) if info else None

    def _get_worktree_info(self, task_id: int) -> dict | None:
        return self._load_index().get(f"task-{task_id}")

    # ── 事件流（.tasks/events.jsonl，append-only）────────────────
    def _events_path(self) -> Path:
        return self.tasks_dir / "events.jsonl"

    def _emit(self, event_type: str, **data) -> None:
        """追加一条事件。JSONL 一行一事件，永不覆盖。"""
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            **data,
        }
        with self._io_lock:
            with open(self._events_path(), "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        logger.info(
            f"WorktreeManager._emit | {event_type} | "
            f"{json.dumps(data, ensure_ascii=False)}"
        )

    # ── Worktree 生命周期 ────────────────────────────────────
    def worktree_create(self, task_id: int, branch: str | None = None) -> str:
        """创建 worktree 并绑定到任务，自动推进任务到 in_progress。

        一个方法做三件事（双状态机联动）：
          1. git worktree add 创建独立工作目录（执行面）
          2. 注册到 index.json（控制面）
          3. 任务 pending → in_progress（控制面）
        调用方只需要一行代码。
        """
        branch = branch or f"task-{task_id}"
        wt_path = self.worktrees_dir / f"task-{task_id}"
        self._emit("worktree.create.before", task_id=task_id, branch=branch)
        try:
            subprocess.run(
                ["git", "worktree", "add", str(wt_path), "-b", branch],
                cwd=str(self.project_root),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self._register_worktree(task_id, branch, str(wt_path))
            # 双状态机联动点①：绑定 worktree → 任务自动 in_progress
            self.task_manager.update_status(task_id, "in_progress")
            self._emit("worktree.create.after", task_id=task_id, path=str(wt_path))
            logger.info(
                f"WorktreeManager.worktree_create 成功 | task #{task_id} → {wt_path} "
                f"(branch={branch}) | 任务状态 → in_progress"
            )
            return str(wt_path)
        except subprocess.CalledProcessError as e:
            self._emit(
                "worktree.create.failed", task_id=task_id,
                error=(e.stderr or str(e)).strip(),
            )
            logger.exception(
                f"WorktreeManager.worktree_create 失败 | task #{task_id} | "
                f"{(e.stderr or str(e)).strip()}"
            )
            raise

    def _merge_branch(self, task_id: int, branch: str) -> None:
        """把 worktree 分支合并回主分支（先提交 worktree 里的改动）。"""
        self._emit("worktree.merge.before", task_id=task_id, branch=branch)
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
        # 2. 在主仓库把该分支 merge 回来（--no-ff 保留合并记录）
        merge = subprocess.run(
            ["git", "merge", "--no-ff", branch, "-m", f"Merge {branch} (task #{task_id})"],
            cwd=str(self.project_root), capture_output=True, text=True,
        )
        if merge.returncode != 0:
            self._emit("worktree.merge.failed", task_id=task_id,
                       error=(merge.stderr or str(merge)).strip())
            raise RuntimeError(
                f"Merge branch {branch} failed: {(merge.stderr or merge.stdout).strip()}"
            )
        self._emit("worktree.merge.after", task_id=task_id, branch=branch)
        logger.info(f"WorktreeManager._merge_branch | {branch} 已合并回主分支")

    def worktree_remove(self, task_id: int,
                        complete_task: bool = True, merge: bool = False) -> None:
        """拆除 worktree（双状态机联动点②）。

        complete_task=True → 任务 in_progress → completed
        merge=True         → 先把 worktree 分支合并回主分支，再拆除
        一个调用搞定四件事：完成任务(可选) + 拆目录 + 注销注册 + 清理分支。
        """
        self._emit("worktree.remove.before", task_id=task_id,
                   complete_task=complete_task, merge=merge)
        info = self._get_worktree_info(task_id)
        # 1. 可选：合并 worktree 分支回主分支
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
                cwd=str(self.project_root), capture_output=True, text=True,
            )
            logger.info(f"WorktreeManager.worktree_remove | 已移除目录 {wt_path}")
        # 4. 清理分支（-d 只删已合并分支；未合并失败则忽略，分支留着无碍）
        subprocess.run(
            ["git", "branch", "-d", f"task-{task_id}"],
            cwd=str(self.project_root), capture_output=True, text=True,
        )
        # 5. 从注册表注销
        self._unregister_worktree(task_id)
        self._emit("worktree.remove.after", task_id=task_id)
        logger.info(f"WorktreeManager.worktree_remove 完成 | task #{task_id}")

    # ── 执行（在 worktree 内跑命令 / 切换 session 基座）──────────
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
            subprocess.run(
                f"taskkill /f /t /pid {proc.pid}",
                shell=True, capture_output=True,
            )
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                pass
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
                f"{info['status']} | {exists} | {info.get('created_at', '')[:19]}"
            )
        return "\n".join(lines)

# -*- coding: utf-8 -*-
"""WorktreeManager 的索引与注册基座（由 manager.py 拆出，Mixin 模式）。

类职责：索引文件读写 / worktree 注册注销 / 路径与信息查询 /
事件日志 emit / 仓库根解析——文件即状态源。
生命周期：WorktreeManager(manager.py) 继承组合。
"""
import json
from datetime import datetime, timezone  # 注册时间戳
from pathlib import Path  # 索引/注册路径类型
from ..config import logger


class WorktreeIndexMixin:
    """索引/注册/查询方法族（self 依赖 manager.py 的 __init__ 状态）。"""

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

    def _register_worktree(self, task_id: int, branch: str, path: str,
                           repo_root: Path | None = None) -> None:
        """登记 worktree 元信息（status=active）。

        Bug B 修复：记录实际 worktree 所属的 git 仓库根目录（repo_root），
        默认取 worktree 路径的父父目录（<repo>/.worktrees/task-N）。
        remove/recover 用它定位正确的 git 仓库执行 git 命令。
        """
        repo_root = repo_root or Path(path).resolve().parent.parent
        with self._io_lock:
            index = self._load_index()
            index[f"task-{task_id}"] = {
                "task_id": task_id,
                "branch": branch,
                "path": path,
                "status": "active",
                "repo": str(repo_root),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._save_index(index)
        logger.info(
            f"WorktreeManager._register_worktree | task #{task_id} | "
            f"branch={branch} | repo={repo_root}"
        )

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

    def _repo_of(self, info: dict | None) -> Path:
        """从注册信息反推 worktree 所属的 git 仓库根目录。"""
        if info and info.get("repo"):
            return Path(info["repo"])
        if info:
            return Path(info["path"]).resolve().parent.parent
        return self.project_root

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
    def _resolve_repo(self, repo: str | None) -> Path:
        """解析目标 git 仓库根目录。

        Bug B 修复：worktree 不一定建在 project_root——任务可能要求
        "在 demo/demo-s12 这个子仓库里建 worktree 做隔离测试"。
        repo 为空时回退到 project_root（与课文/selftest 行为一致）。
        """
        if repo:
            return Path(repo).resolve()
        return self.project_root

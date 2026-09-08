# -*- coding: utf-8 -*-
"""任务板文件存储基座（由 board.py 拆出，函数化）。

类职责：任务 JSON 文件路径 / 读写 / 自增 ID / 全 ID 扫描——
文件即数据库的原子操作层。
生命周期：TaskManager 委托调用。
"""
import json
import os

from ....config import logger


def _task_path(task_dir: str, task_id: int) -> str:
    return os.path.join(task_dir, f"task_{task_id}.json")

def _read_task(task_dir: str, task_id: int) -> dict | None:
    path = _task_path(task_dir, task_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_task(task_dir: str, task: dict):
    path = _task_path(task_dir, task["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2, ensure_ascii=False)

def _compute_next_id(task_dir: str) -> int:
    existing = _all_task_ids(task_dir)
    return max(existing, default=0) + 1

def _all_task_ids(task_dir: str) -> list[int]:
    # Bug A 修复：Agent 收尾阶段可能用 bash 物理删除 .tasks 目录
    # （任务清理指令里就要求删掉 .tasks）。目录不存在时按"空任务列表"
    # 处理，避免 all_completed() 在 os.listdir() 处抛 FileNotFoundError
    # 导致主循环收尾崩溃。
    if not os.path.isdir(task_dir):
        logger.info(
            f"TaskManager._all_task_ids | 目录 {task_dir} 不存在，"
            f"按空任务列表处理"
        )
        return []
    ids = []
    for fname in os.listdir(task_dir):
        if fname.startswith("task_") and fname.endswith(".json"):
            try:
                ids.append(int(fname[5:-5]))
            except ValueError:
                continue
    return sorted(ids)

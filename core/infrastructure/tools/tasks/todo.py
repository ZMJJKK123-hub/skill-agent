# -*- coding: utf-8 -*-
"""TodoManager：叠加式规划清单（不改动 Agent Loop 核心）。
由 tasks.py 原样迁出。
"""
import json
import os
import threading

from ....config import logger


# ---------- TodoManager（叠加的规划系统，不改动 Agent Loop 核心）----------
# 持久化：进程重启后恢复 todo（用户中断 / MOD 自我循环结束后继续对话也能记住进度）。
TODO_STATE_FILE = ".todo.json"


class TodoManager:
    def __init__(self):
        self.todos: list[dict] = []
        self.state_file = TODO_STATE_FILE
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.todos = data
                    logger.info(f"TodoManager._load | 已恢复 {len(self.todos)} 条 todo")
        except Exception as e:
            logger.warning(f"TodoManager._load 失败: {e}")

    def _save(self) -> None:
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"TodoManager._save 失败: {e}")

    def update(self, items: list[dict]) -> str:
        """更新待办列表。核心约束：同一时间只允许一个 in_progress。"""
        logger.info(f"TodoManager.update 被调用，items={json.dumps(items, ensure_ascii=False)}")
        in_progress = [i for i in items if i["status"] == "in_progress"]
        if len(in_progress) > 1:
            return "Error: Only one item can be in_progress at a time."
        self.todos = items
        self._save()
        return self.render()

    def render(self) -> str:
        """渲染待办清单，让模型在每次调用后看到全局进度。"""
        if not self.todos:
            return "(no todos)"
        icons = {"pending": "☐", "in_progress": "▶", "completed": "✓"}
        done = sum(1 for i in self.todos if i["status"] == "completed")
        total = len(self.todos)
        header = f"📋 Todo List ({done}/{total} completed)"
        lines = [header]
        for idx, item in enumerate(self.todos, 1):
            icon = icons.get(item["status"], "?")
            lines.append(f"  [{idx}] {icon} {item['content']}")
        rendered = "\n".join(lines)
        logger.info(f"TodoManager.render:\n{rendered}")
        return rendered

todo_manager = TodoManager()


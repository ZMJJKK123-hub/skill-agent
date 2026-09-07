# -*- coding: utf-8 -*-
"""MessageBus：JSONL 收件箱（drain-on-read）。
由 team.py 原样迁出。
"""
import json
import os
import threading
from pathlib import Path

from ....config import logger


# ---------- MessageBus（第 9 课：JSONL 收件箱，drain-on-read）----------
class MessageBus:
    """append-only 的 JSONL 收件箱系统。

    每个队友一个 .jsonl 文件，send 追加一行，read_inbox 读取全部并清空。
    drain-on-read：消息只需处理一次，读完就清，不需要已读标记。
    线程安全：用 threading.Lock 保护文件操作（队友在同进程线程中）。
    """

    def __init__(self, inbox_dir: str = ".team/inbox"):
        self.inbox_dir = inbox_dir
        os.makedirs(inbox_dir, exist_ok=True)
        self._lock = threading.Lock()
        # 每次启动清空残留的 inbox 文件——上一次 session 的消息已无意义
        # （队友线程随进程退出而死亡，无人再读取这些孤儿消息）
        self._clean_stale_inbox()
        logger.info(f"MessageBus 初始化 | inbox_dir={inbox_dir} | 已清空残留消息")

    def _clean_stale_inbox(self):
        """清空 inbox 目录下所有 .jsonl 文件的残留内容。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时跳过，避免 os.listdir 抛 FileNotFoundError。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        for fname in os.listdir(self.inbox_dir):
            if fname.endswith(".jsonl"):
                path = os.path.join(self.inbox_dir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    pass  # truncate to empty

    def send(self, from_name: str, to_name: str, content: str):
        """往目标队友的收件箱追加一条消息。"""
        if not _is_safe_agent_name(to_name):
            logger.warning(f"MessageBus.send | 非法 to_name={to_name!r}，已忽略")
            return
        msg = {
            "from": from_name,
            "to": to_name,
            "content": content,
            "timestamp": time.time(),
        }
        path = os.path.join(self.inbox_dir, f"{to_name}.jsonl")
        with self._lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        logger.info(f"MessageBus.send | {from_name} → {to_name} | content={content[:100]}")

    def broadcast(self, from_name: str, content: str, team: dict):
        """群发给所有队友（除自己外）。"""
        for name in team:
            if name != from_name:
                self.send(from_name, name, content)

    def read_inbox(self, name: str) -> list:
        """读取并清空收件箱（drain-on-read）。"""
        path = os.path.join(self.inbox_dir, f"{name}.jsonl")
        if not os.path.exists(path):
            return []
        with self._lock:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # 读完即清
            with open(path, "w", encoding="utf-8") as f:
                pass  # truncate to empty
        msgs = []
        for l in lines:
            if not l.strip():
                continue
            try:
                msgs.append(json.loads(l))
            except json.JSONDecodeError:
                logger.warning(f"MessageBus.read_inbox | {name} | 跳过损坏消息行")
                continue
        logger.info(f"MessageBus.read_inbox | {name} | 读取 {len(msgs)} 条消息")
        return msgs

    def clear_all(self):
        """第 11 课：清空所有收件箱文件（session 收尾时调用）。

        只清空 .jsonl 文件内容，保留目录本身。

        Bug D 修复：Agent 收尾可能物理删除 .team 目录，inbox 可能不存在。
        目录不存在时直接跳过，避免 os.listdir 抛 FileNotFoundError 使主循环崩溃。
        """
        if not os.path.isdir(self.inbox_dir):
            return
        with self._lock:
            for fname in os.listdir(self.inbox_dir):
                if fname.endswith(".jsonl"):
                    path = os.path.join(self.inbox_dir, fname)
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            pass  # truncate to empty
                    except OSError:
                        pass
        logger.info(f"MessageBus.clear_all | 已清空 {self.inbox_dir} 下所有收件箱文件")


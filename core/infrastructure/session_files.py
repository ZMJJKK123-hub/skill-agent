# -*- coding: utf-8 -*-
"""会话文件存储：SessionStore 的文件实现（infrastructure 层）。

存储布局（与旧 core/conversation.py 完全同构，server 侧无需任何改动）：
    <session_root>/.chat/conversation.jsonl  对话历史（user/assistant 对）
    <session_root>/.chat/working.jsonl       当前轮断点（暂停/继续）
    <session_root>/.chat/pending.jsonl       运行中插话队列
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..domain.messages import Message, UserMessage, transport_messages, typed_messages
from ..interfaces.session_store import SessionStore
from .logging_.logger import get_logger

#: 恢复时最多回放的对话轮数（防上下文无限膨胀，旧默认 20 轮）。
MAX_HISTORY_ROUNDS = 20

logger = get_logger("session_files")


class FileSessionStore(SessionStore):
    """.chat/ 三类文件的类型化读写（SessionStore 实现）。

    类职责：唯一拥有会话文件格式知识；写入失败记 WARNING 不抛出
    （旁路数据不得打断引擎主流程——但绝不静默，均有日志）。
    类变量/实例属性：
        root: Path — 会话根目录；chat: Path — .chat 子目录。
    生命周期：bootstrap 每进程构建；文件随写入惰性创建。
    """

    def __init__(self, session_root: str) -> None:
        """输入：会话根目录路径字符串。返回：无。职责：推导 .chat 目录。"""
        self.root = Path(session_root)
        self.chat = self.root / ".chat"

    # ---------- 基础读写 ----------

    def _read_jsonl(self, path: Path) -> list[dict]:
        """输入：jsonl 文件路径。返回：dict 列表（坏行跳过并记日志）。"""
        records: list[dict] = []
        if not path.exists():
            return records
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("jsonl 坏行已跳过 | path=%s", path)
        except OSError as e:
            logger.warning("jsonl 读取失败 | path=%s | err=%s", path, e)
        return records

    def _append_jsonl(self, path: Path, record: dict) -> None:
        """输入：路径 + 单条记录。返回：无。职责：追加一行 JSON（建目录）。"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.error("jsonl 追加失败 | path=%s | err=%s", path, e)

    # ---------- 对话历史 ----------

    def load_recent_history(self, max_rounds: int = MAX_HISTORY_ROUNDS) -> list[Message]:
        """读取最近 N 轮历史（一轮 = user+assistant 各一条，取尾部）。"""
        path = self.chat / "conversation.jsonl"
        msgs = [d for d in self._read_jsonl(path)
                if d.get("role") in ("user", "assistant")]
        tail = msgs[-max_rounds * 2:]
        return typed_messages(tail)

    def append_user(self, content: str, images: Optional[list[str]] = None) -> None:
        """追加用户消息（含图片附件名；供前端回显与多模态重建）。"""
        entry: dict = {"role": "user", "content": content}
        if images:
            entry["images"] = [str(n) for n in images]
        self._append_jsonl(self.chat / "conversation.jsonl", entry)
        logger.info("conversation.append | role=user | len=%d | images=%d",
                    len(content), len(images or []))

    def append_assistant(self, content: str) -> None:
        """追加助手回复（只存文本——工具细节不进磁盘历史）。"""
        self._append_jsonl(self.chat / "conversation.jsonl",
                           {"role": "assistant", "content": content})
        logger.info("conversation.append | role=assistant | len=%d", len(content))

    def reset_history(self) -> None:
        """清空对话历史文件（会话重置时调用）。"""
        path = self.chat / "conversation.jsonl"
        try:
            path.unlink(missing_ok=True)
            logger.info("conversation.reset | 已清空 %s", path)
        except OSError as e:
            logger.warning("conversation.reset 失败 | err=%s", e)

    # ---------- 断点 ----------

    def save_checkpoint(self, messages: list[Message]) -> None:
        """把当前完整消息列表覆写为断点（每轮循环开头调用）。"""
        path = self.chat / "working.jsonl"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                for d in transport_messages(messages):
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
            logger.info("checkpoint.saved | messages=%d", len(messages))
        except OSError as e:
            logger.error("checkpoint.save 失败 | err=%s", e)

    def load_checkpoint(self) -> Optional[list[Message]]:
        """加载断点；无断点/空文件返回 None（恢复模式入口）。"""
        records = self._read_jsonl(self.chat / "working.jsonl")
        return typed_messages(records) if records else None

    def clear_checkpoint(self) -> None:
        """删除断点文件（正常完成一轮后调用）。"""
        try:
            (self.chat / "working.jsonl").unlink(missing_ok=True)
        except OSError as e:
            logger.warning("checkpoint.clear 失败 | err=%s", e)

    # ---------- 插话队列 ----------

    def enqueue_pending(self, content: str,
                        images: Optional[list[str]] = None) -> None:
        """排入一条用户插话（只进队列；历史由消费时落盘，保证处理顺序）。"""
        entry: dict = {"role": "user", "content": content}
        if images:
            entry["images"] = [str(n) for n in images]
        self._append_jsonl(self.chat / "pending.jsonl", entry)
        logger.info("pending.enqueued | len=%d", len(content))

    def _rewrite_pending(self, lines: list[str]) -> None:
        """输入：应保留的原始行。返回：无。职责：覆写插话队列文件。"""
        try:
            path = self.chat / "pending.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")
        except OSError as e:
            logger.warning("pending.rewrite 失败 | err=%s", e)

    def drain_pending_one(self) -> list[UserMessage]:
        """出队最早一条插话（严格问一条答一条；其余留在队列）。

        按原始行处理（而非解析后记录）：坏 JSON/非 user 行同样被移除，
        与旧实现一致——否则坏行会永远卡在队头。
        """
        path = self.chat / "pending.jsonl"
        lines = [l for l in self._read_lines(path) if l.strip()]
        if not lines:
            return []
        self._rewrite_pending(lines[1:])
        try:
            first = json.loads(lines[0])
        except json.JSONDecodeError:
            logger.warning("pending.drain_one | 队首坏行已丢弃")
            return []
        if isinstance(first, dict) and first.get("role") == "user":
            logger.info("pending.drain_one | 剩余 %d", len(lines) - 1)
            return [UserMessage(content=str(first.get("content", "")),
                                images=first.get("images"))]
        return []

    def _read_lines(self, path: Path) -> list[str]:
        """输入：文本文件路径。返回：原始行列表（文件缺失/IO 错误返回空）。"""
        try:
            return path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        except OSError as e:
            logger.warning("读取失败 | path=%s | err=%s", path, e)
            return []

    def drain_pending_all(self) -> list[UserMessage]:
        """一次性出队全部插话并清空文件（非 daemon 模式的中途注入）。"""
        records = self._read_jsonl(self.chat / "pending.jsonl")
        if not records:
            return []
        self._rewrite_pending([])
        out = [UserMessage(content=str(r.get("content", "")), images=r.get("images"))
               for r in records if r.get("role") == "user"]
        if out:
            logger.info("pending.drain_all | 取出 %d 条", len(out))
        return out

    def pending_count(self) -> int:
        """返回队列剩余条数（server 判断是否自动续跑）。"""
        return len(self._read_jsonl(self.chat / "pending.jsonl"))

    def pending_entries(self) -> list[dict]:
        """返回队列全部原始条目（不消费；daemon 组装上下文时过滤用）。"""
        return self._read_jsonl(self.chat / "pending.jsonl")

"""对话历史持久化组件（多轮对话支持）。

设计目标：把 agent 从"一轮输入一轮输出、跑完即清"升级为
"可恢复的多轮对话"——模拟 DSH 平台的对话形式，让 agent 能记住
用户之前说过的需求，逐步把 mod 要求完善。

存储位置：<session_root>/.chat/conversation.jsonl
- session_root = 会话根目录（data/sessions/<id>/），由 run_task.py
  通过 DSH_SESSION_ROOT 环境变量注入；不在 mod/ 里面，
  agent 的收尾清理（删 .tasks/.team 等）永远不会碰到它。
- 只存 user / assistant 两条角色的对话对；tool 调用细节、
  system 注入、后台通知等运行时噪音不落盘——恢复时只重建
  "用户说了什么 + agent 回了什么"的骨架，供下一轮继续。

线程安全：append 用独占写（a 模式 + 单行 JSON），load 用读；
子进程每轮独立（一轮 = 一个子进程），不存在同进程并发写。
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("agent")

CHAT_DIR_NAME = ".chat"
CONVERSATION_FILE = "conversation.jsonl"
WORKING_FILE = "working.jsonl"    # 当前轮完整断点（含工具中间状态，暂停/继续用）
PENDING_FILE = "pending.jsonl"    # 运行中用户插入的消息队列（排队等当前轮跑完）

# 恢复时最多回放多少轮历史（防止无限膨胀：旧轮次被压缩为摘要）
MAX_HISTORY_ROUNDS = 20


def chat_dir(session_root: str | os.PathLike) -> Path:
    """返回会话的 .chat 目录（不存在则创建）。"""
    d = Path(session_root) / CHAT_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def conversation_path(session_root: str | os.PathLike) -> Path:
    return chat_dir(session_root) / CONVERSATION_FILE


def load_history(session_root: str | os.PathLike) -> list[dict]:
    """读取会话的全部历史对话（user/assistant 消息对）。

    返回形如 [{"role": "user", "content": "..."}, ...] 的列表；
    文件不存在或损坏时返回空列表。
    """
    path = conversation_path(session_root)
    if not path.exists():
        return []
    messages: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                    messages.append(msg)
    except OSError as e:
        logger.warning(f"conversation.load_history 读取失败: {e}")
        return []
    return messages


def load_recent_history(session_root: str | os.PathLike, max_rounds: int = MAX_HISTORY_ROUNDS) -> list[dict]:
    """读取最近 N 轮对话历史。

    一轮 = 一条 user + 一条 assistant（可能 user 后没有 assistant，比如
    当前这一轮还没回复）。取最后 max_rounds 轮，防止上下文无限膨胀。
    """
    messages = load_history(session_root)
    if not messages:
        return []
    # 从尾部向前数轮：assistant 消息算一轮的终点，user 算起点
    # 简化实现：直接取末尾 max_rounds*2 条消息（user+assistant 各一）
    tail = messages[-max_rounds * 2:]
    return tail


def append_message(session_root: str | os.PathLike, role: str, content: str) -> None:
    """追加一条对话消息（role: user | assistant）。"""
    if role not in ("user", "assistant"):
        raise ValueError(f"conversation.append_message: invalid role {role!r}")
    path = conversation_path(session_root)
    entry = {
        "role": role,
        "content": content,
        "ts": None,  # 占位：需要时间戳时由调用方覆盖（保持简单）
    }
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"role": role, "content": content}, ensure_ascii=False) + "\n")
        logger.info(f"conversation.append_message | role={role} | len={len(content)}")
    except OSError as e:
        logger.error(f"conversation.append_message 写入失败: {e}")


def append_user(session_root: str | os.PathLike, content: str) -> None:
    append_message(session_root, "user", content)


def append_assistant(session_root: str | os.PathLike, content: str) -> None:
    append_message(session_root, "assistant", content)


def reset(session_root: str | os.PathLike) -> None:
    """清空会话历史（重置会话时调用）。"""
    path = conversation_path(session_root)
    try:
        if path.exists():
            path.unlink()
        logger.info(f"conversation.reset | 已清空 {path}")
    except OSError as e:
        logger.warning(f"conversation.reset 失败: {e}")


# ---------- 断点存储（暂停/继续：完整上下文含工具中间状态） ----------

def working_path(session_root: str | os.PathLike) -> Path:
    return chat_dir(session_root) / WORKING_FILE


def save_working(session_root: str | os.PathLike, messages: list) -> None:
    """把当前轮的完整 messages 持久化为断点（每轮循环开头调用）。

    暂停（杀子进程）后，断点文件仍在磁盘；继续时新子进程
    原样加载此文件恢复上下文，像没停过一样继续跑。
    """
    path = working_path(session_root)
    try:
        with open(path, "w", encoding="utf-8") as f:
            for m in messages:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        logger.info(f"conversation.save_working | 已保存断点 {len(messages)} 条消息")
    except OSError as e:
        logger.error(f"conversation.save_working 写入失败: {e}")


def load_working(session_root: str | os.PathLike) -> list:
    """加载断点 messages（恢复模式用）；文件不存在返回 None 表示无断点。"""
    path = working_path(session_root)
    if not path.exists():
        return None
    messages = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError as e:
        logger.warning(f"conversation.load_working 读取失败: {e}")
        return None
    return messages if messages else None


def clear_working(session_root: str | os.PathLike) -> None:
    """清空断点（正常完成一轮后调用）。"""
    path = working_path(session_root)
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


# ---------- 运行中插话排队（queue：等当前轮跑完后自动处理） ----------

def pending_path(session_root: str | os.PathLike) -> Path:
    return chat_dir(session_root) / PENDING_FILE


def enqueue_pending(session_root: str | os.PathLike, content: str) -> None:
    """把运行中用户发来的消息排入队列（当前轮跑完后由前端自动续跑处理）。"""
    path = pending_path(session_root)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"role": "user", "content": content}, ensure_ascii=False) + "\n")
        logger.info(f"conversation.enqueue_pending | 已排队用户消息")
    except OSError as e:
        logger.error(f"conversation.enqueue_pending 写入失败: {e}")


def drain_pending(session_root: str | os.PathLike) -> list:
    """读取并清空 pending 队列（agent 每轮开头调用，注入为 user 消息）。"""
    path = pending_path(session_root)
    if not path.exists():
        return []
    msgs = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    m = json.loads(line)
                    if isinstance(m, dict) and m.get("role") == "user":
                        msgs.append(m)
                except json.JSONDecodeError:
                    continue
        # 读完即清
        with open(path, "w", encoding="utf-8") as f:
            pass
    except OSError as e:
        logger.warning(f"conversation.drain_pending 失败: {e}")
    if msgs:
        logger.info(f"conversation.drain_pending | 取出 {len(msgs)} 条排队消息")
    return msgs


def pending_count(session_root: str | os.PathLike) -> int:
    """返回 pending 队列剩余条数（前端轮询判断是否自动续跑）。"""
    path = pending_path(session_root)
    if not path.exists():
        return 0
    count = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
    except OSError:
        return 0
    return count

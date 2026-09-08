# -*- coding: utf-8 -*-
"""单轮执行生命周期（server_app/services 层）。

职责：一轮 agent 循环的完整闭环——跑引擎 → 清断点 → 回复落历史 →
stdout 预览 → 知识沉淀收尾；含排队消息过滤与轮次崩溃的用户可见
错误回复。全部函数由 run_task（首轮）与 daemon_runner（后续轮）调用。
"""
from __future__ import annotations

import traceback
from pathlib import Path

from core.domain.messages import Message
from core.infrastructure.logging_.logger import get_logger
from core.infrastructure.session_files import FileSessionStore
from core.interfaces.event_writer import EventWriter
from core.services.loop.runner import AgentLoopEngine

from .finalizers import finalize_error_list, finalize_known_issues

logger = get_logger("round_runner")


def run_one_round(engine: AgentLoopEngine, messages: list[Message],
                  session_dir: Path, store: FileSessionStore,
                  writer: EventWriter, project_root: Path) -> str:
    """跑一轮引擎循环并完成全部收尾（断点/历史/预览/沉淀）。

    Args:
        engine: 引擎实例（daemon 模式跨轮复用）。
        messages: 本轮消息（typed）。
        session_dir: 会话根目录。
        store: 会话文件存储。
        writer: run.log 协议写入器。
        project_root: 仓库根（沉淀目标定位用）。
    Returns:
        引擎最终回复文本。
    """
    try:
        final = engine.run(messages)
    except Exception as e:
        # 统一失败标记行：前端据此显示"运行异常"而不是绿色"完成"
        writer.notice(f"任务异常终止: {type(e).__name__}: {e}")
        raise
    store.clear_checkpoint()
    # 先落历史再打印（stdout 大段写入偶发冻结——数据安全优先）
    store.append_assistant(final or "")
    _print_final_preview(writer, final)
    try:
        finalize_known_issues(session_dir, project_root)
    except Exception as e:
        logger.warning("finalize_known_issues 失败: %s", e)
    try:
        finalize_error_list(session_dir, project_root)
    except Exception as e:
        logger.warning("finalize_error_list 失败: %s", e)
    return final


def _print_final_preview(writer: EventWriter, final: str) -> None:
    """输入：最终回复。返回：无。职责：打印前 600 字预览（防 stdout 冻结）。"""
    preview = (final or "")[:600]
    try:
        writer.notice(f"完成，最终回复:\n{preview}")
    except OSError:
        try:
            for ln in preview.splitlines()[:10]:
                writer.notice(ln[:120])
        except OSError as e:
            logger.debug("_print_final_preview 降级忽略 | %s", e)


def strip_pending_messages(messages: list[Message],
                           store: FileSessionStore) -> list[Message]:
    """把仍在排队（pending 文件里）的消息移出本轮上下文。

    排队消息属于"之后的轮次"（daemon 一轮只消费一条）；不滤掉的话
    本轮模型会看到多条待答需求，常合并处理只答最后一条（实测）。
    """
    pending = store.pending_entries()
    if not pending:
        return messages
    pset = {(str(p.get("role")), str(p.get("content"))) for p in pending}
    kept = [m for m in messages
            if (m.role, getattr(m, "content", None)) not in pset]
    if len(kept) != len(messages):
        logger.info("已把 %d 条排队消息移出本轮（等 daemon 逐条处理）",
                    len(messages) - len(kept))
    return kept


def notify_round_error(store: FileSessionStore, e: Exception) -> None:
    """轮次崩溃时向对话历史追加用户可见的错误回复。

    此前异常只打 traceback：用户消息已入历史却永远没有回复，界面显示
    "完成"但消息被静默吞掉。落一条 assistant 错误回复保持 u/a 交替。
    """
    text = (f"⚠️ 本轮调用失败：{str(e)[:300]}\n\n"
            f"请检查模型配置 / API Key / 网络后重试；若持续失败可在设置里更换模型提供方。")
    try:
        store.append_assistant(text)
    except Exception as e2:
        logger.error("错误回复写入历史失败: %s", e2)


def print_round_trace(e: Exception) -> None:
    """输入：轮次异常。返回：无。职责：打 traceback 进日志（stderr 通道）。"""
    traceback.print_exc()

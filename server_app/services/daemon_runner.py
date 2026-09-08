# -*- coding: utf-8 -*-
"""会话常驻循环（server_app/services 层）。

chat / mod 模式共享的 daemon：首轮跑完后不退出进程，每 0.5s 轮询
.chat/pending.jsonl，有新消息就（消费一条 → 组装历史 → 引擎一轮 →
收尾），回到等待。第二轮起零 import / 零技能扫描开销。

daemon 状态文件（server 侧的判定契约）：
    .chat/daemon.state — waiting（空闲）| working（跑轮中）
    .chat/daemon.pid   — pid 文件（server 重启清理遗留 daemon）
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from core.domain.messages import Message
from core.infrastructure.logging_.logger import get_logger
from core.infrastructure.session_files import FileSessionStore
from core.interfaces.event_writer import EventWriter
from core.services.loop.runner import AgentLoopEngine

from .round_runner import notify_round_error, print_round_trace, run_one_round

logger = get_logger("daemon_runner")

#: 轮询间隔（秒）——新消息到达的最大感知延迟。
POLL_INTERVAL_S = 0.5


class DaemonFiles:
    """daemon 状态文件的读写（server 识别空闲/工作的契约通道）。

    类职责：集中 state/pid 两个文件的写入与清理；写失败记日志不抛出。
    实例属性：state_path / pid_path（.chat/ 下两个文件）。
    生命周期：daemon 进程一生一对；finally 阶段 cleanup()。
    """

    def __init__(self, session_root: Path) -> None:
        """输入：会话根目录。返回：无。职责：推导 .chat 下两个路径。"""
        chat = session_root / ".chat"
        chat.mkdir(parents=True, exist_ok=True)
        self.state_path = chat / "daemon.state"
        self.pid_path = chat / "daemon.pid"

    def write_pid_and_working(self) -> None:
        """输入：无。返回：无。职责：进程启动即写 pid + working。"""
        self._write(self.pid_path, _pid())
        self.set_state("working")

    def set_state(self, state: str) -> None:
        """输入：waiting|working。返回：无。职责：写状态文件。"""
        self._write(self.state_path, state)

    def read_mode_hint(self, fallback: str) -> str:
        """输入：缺省模式。返回：mode.txt 内容（缺失回退）。"""
        try:
            return (self.state_path.parent / "mode.txt").read_text(
                encoding="utf-8").strip()
        except OSError:
            return fallback

    def cleanup(self) -> None:
        """输入：无。返回：无。职责：退出时删 pid/state 文件。"""
        for p in (self.pid_path, self.state_path):
            try:
                p.unlink(missing_ok=True)
            except OSError as e:
                logger.warning("daemon 文件清理失败 | path=%s | err=%s", p, e)

    @staticmethod
    def _write(path: Path, text: str) -> None:
        """输入：路径 + 文本。返回：无。职责：单点写文件（失败记日志）。"""
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as e:
            logger.warning("daemon 状态写入失败 | path=%s | err=%s", path, e)


def _pid() -> str:
    """输入：无。返回：当前进程 id 字符串。"""
    return str(os.getpid())


def _stop_game_processes(session_dir: Path, note: str) -> None:
    """空闲收尾：关掉 agent 启动的游戏客户端/服务器（防窗口残留）。"""
    try:
        from core.process_manager import stop_all
        stopped = stop_all(str(session_dir), force=True)
        if stopped and stopped != "No running game processes.":
            logger.info("空闲收尾%s，已关闭游戏进程: %s", note, stopped)
    except Exception as e:
        logger.warning("游戏进程收尾清理失败: %s", e)


def _run_pending_round(engine: AgentLoopEngine, store: FileSessionStore,
                       writer: EventWriter, session_dir: Path,
                       project_root: Path, files: DaemonFiles) -> None:
    """消费一条排队消息并执行一轮（异常转通知，结束回 waiting）。

    Args:
        engine/store/writer: 引擎三元组。
        session_dir: 会话工作目录。
        project_root: 仓库根。
        files: daemon 状态文件组。
    """
    if not _consume_one(store):
        files.set_state("waiting")
        return
    messages = _assemble_round_context(store)
    if messages is None:
        files.set_state("waiting")
        return
    try:
        run_one_round(engine, messages, session_dir, store,
                      writer, project_root)
    except Exception as e:
        writer.notice(f"daemon 轮异常（继续等待）: {e}")
        print_round_trace(e)
        notify_round_error(store, e)
        files.set_state("waiting")
        return
    if store.pending_count() == 0:  # 有排队则保留进程（下轮即用）
        _stop_game_processes(session_dir, "")
    files.set_state("waiting")


def daemon_loop(engine: AgentLoopEngine, store: FileSessionStore,
                writer: EventWriter, session_dir: Path,
                session_root: Path, mode: str,
                idle_timeout_s: float, project_root: Path) -> None:
    """daemon 主循环（首轮完成后进入；空闲超时自动退出）。

    Args:
        engine: 引擎实例（跨轮复用，长对话状态保留）。
        store: 会话文件存储（队列消费/历史组装）。
        writer: run.log 协议写入器。
        session_dir: 会话工作目录（chat=会话根，mod=mod/ 子目录）。
        session_root: 会话根（.chat/ 所在）。
        mode: 本进程固化的运行模式（chat|mod）。
        idle_timeout_s: 空闲退出秒数。
        project_root: 仓库根（知识沉淀用）。
    """
    files = DaemonFiles(session_root)
    last_activity = time.time()
    _stop_game_processes(session_dir, "（启动即执行）")
    files.set_state("waiting")
    try:
        while True:
            time.sleep(POLL_INTERVAL_S)
            if not _has_pending(store):
                if time.time() - last_activity > idle_timeout_s:
                    writer.notice("daemon idle exit")
                    return
                continue
            if _mode_switched(files, mode):
                writer.notice(f"检测到模式切换（{mode}→{files.read_mode_hint(mode)}），"
                              f"daemon 退出待重拉")
                files.set_state("waiting")
                return
            last_activity = time.time()
            files.set_state("working")
            _run_pending_round(engine, store, writer, session_dir,
                               project_root, files)
    except KeyboardInterrupt:
        # server 被 Ctrl+C 停止时中断广播到同控制台 daemon → 优雅退出
        writer.notice("daemon stopped (interrupt)")
    finally:
        _stop_game_processes(session_dir, "（退出兜底）")
        files.cleanup()


def _has_pending(store: FileSessionStore) -> bool:
    """输入：存储。返回：队列是否有消息（IO 异常按无处理）。"""
    try:
        return store.pending_count() > 0
    except Exception as e:
        logger.warning("pending 计数失败（按无处理）: %s", e)
        return False


def _mode_switched(files: DaemonFiles, mode: str) -> bool:
    """输入：状态文件 + 本进程模式。返回：mode.txt 是否切到了另一模式。"""
    cur = files.read_mode_hint(mode)
    return cur in ("chat", "mod") and cur != mode


def _consume_one(store: FileSessionStore) -> bool:
    """消费最早一条排队消息并落历史（严格问一条答一条）。

    Returns:
        True=成功消费；False=本轮跳过（回等待）。
    """
    try:
        for msg in store.drain_pending_one():
            store.append_user(msg.content, images=msg.images)
        return True
    except Exception as e:
        logger.warning("drain_pending_one 失败: %s", e)
        return False


def _assemble_round_context(store: FileSessionStore) -> "list[Message] | None":
    """组装本轮上下文：近期历史 + 滤掉仍在排队的消息。

    Returns:
        消息列表；空历史/读取失败返回 None（跳过本轮）。
    """
    from .round_runner import strip_pending_messages
    try:
        messages = store.load_recent_history()
    except Exception as e:
        logger.warning("加载对话历史失败（跳过本轮）: %s", e)
        return None
    messages = strip_pending_messages(messages, store)
    if not messages:
        logger.info("daemon 轮无历史消息，跳过")
        return None
    return messages

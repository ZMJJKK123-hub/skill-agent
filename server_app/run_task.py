# -*- coding: utf-8 -*-
"""会话子进程入口：server.py 为每个生成任务 spawn 的独立进程。

进程边界即隔离边界：每会话一个子进程 = 独立 cwd + 独立引擎单例
（任务/队友/工具注册表互不串扰）。本文件只做装配与编排：
    解析参数/env → 切 cwd → 写 daemon pid/state → 提前落历史 →
    构建引擎（重导入在此刻发生）→ 组装消息 → 首轮 → daemon 常驻。

用法（由 server.py 调用）：
    python run_task.py <session_dir> <api_key> [task_prompt]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# 仓库根入 sys.path（core 包与服务子包可导入，与 cwd 无关）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SERVER_APP_DIR))


def _reconfigure_stdout() -> None:
    """输入：无。返回：无。职责：stdout 行缓冲 + UTF-8（run.log 实时性根基）。"""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True, write_through=True,
                                   encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def _load_prompt(argv: list[str]) -> "tuple[str | None, str]":
    """输入：argv。返回：(任务提示词或 None=失败, 失败说明)。"""
    prompt_file = os.environ.get("DSH_PROMPT_FILE", "")
    if prompt_file:  # UTF-8 临时文件优先（绕开 Windows argv GBK 损坏中文）
        try:
            text = Path(prompt_file).read_text(encoding="utf-8")
            try:
                Path(prompt_file).unlink()  # 读完即删（server 不再管）
            except OSError:
                pass
            return text, ""
        except OSError as e:
            return None, f"读取提示词文件失败: {e}"
    return (argv[3] if len(argv) >= 4 else ""), ""


def _parse_prompt_images() -> list[str]:
    """输入：无。返回：DSH_PROMPT_IMAGES 里的附件文件名列表（坏值忽略）。"""
    raw = os.environ.get("DSH_PROMPT_IMAGES", "")
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(n) for n in parsed if isinstance(n, str) and n]
    except ValueError:
        print("[run_task] DSH_PROMPT_IMAGES 解析失败，忽略图片附件", flush=True)
    return []


def _early_write_user_prompt(store, mode: str, user_prompt: str,
                             images: list[str], is_resume: bool) -> None:
    """把用户消息提前写入历史（必须在重导入 core.tools 之前）。

    引擎构建要数秒（openai SDK）；不提前写，用户发完消息立刻翻历史
    会读到空记录。resume 一律不写（带消息的 resume 已入队，避免双写）。
    """
    if mode not in ("chat", "mod") or not user_prompt or is_resume:
        return
    try:
        store.append_user(user_prompt, images=images or None)
    except Exception as e:
        print(f"[run_task] 提前写入历史失败: {e}", flush=True)


def _assemble_first_round(store, task_prompt: str,
                          images: list[str]) -> "list | None":
    """组装首轮消息：断点恢复优先，其次历史 + 当前 prompt（含查重挂图）。

    Returns:
        消息列表；无 prompt 且无历史时 None（进程应退出）。
    """
    from core.domain.messages import UserMessage
    from services.round_runner import strip_pending_messages

    if os.environ.get("DSH_RESUME", "") == "1":
        loaded = store.load_checkpoint()
        if loaded:
            print(f"[run_task] 恢复模式 | 已从断点加载 {len(loaded)} 条消息",
                  flush=True)
            return list(loaded)
        print("[run_task] 恢复模式但无断点，回退到普通启动", flush=True)
    messages = list(store.load_recent_history())
    if not task_prompt:
        if not messages:
            print("[run_task] 无 prompt 且无历史可续，退出", flush=True)
            return None
        return messages
    messages = strip_pending_messages(messages, store)  # 排队的属后续轮次
    for m in reversed(messages):  # 查重扫全列表（只看末条会重复 append）
        if isinstance(m, UserMessage) and m.content == task_prompt:
            print("[run_task] 历史已包含当前 prompt，跳过重复追加", flush=True)
            if images:
                m.images = images  # 图片挂到历史那条上
            return messages
    if images and messages and isinstance(messages[-1], UserMessage):
        messages[-1].images = None  # 同轮裸 prompt 不带图
    messages.append(UserMessage(content=task_prompt,
                                images=images or None))
    return messages


def main() -> int:
    """进程入口：装配 → 首轮 → daemon 常驻。Returns: 进程退出码。"""
    from core.bootstrap import build_engine
    from core.infrastructure.config import Settings
    from core.infrastructure.logging_.runlog_writer import RunlogEventWriter
    from core.infrastructure.session_files import FileSessionStore
    from services.daemon_runner import DaemonFiles, daemon_loop
    from services.round_runner import (notify_round_error, print_round_trace,
                                       run_one_round)

    _reconfigure_stdout()
    if len(sys.argv) < 3:
        print("Usage: python run_task.py <session_dir> <api_key> [task_prompt]")
        return 1
    session_dir = Path(sys.argv[1]).resolve()
    api_key = sys.argv[2]
    task_prompt, err = _load_prompt(sys.argv)
    if task_prompt is None:
        print(f"[run_task] {err}", flush=True)
        return 1

    mode = os.environ.get("DSH_MODE", "chat")
    session_root = Path(os.environ.get("DSH_SESSION_ROOT",
                                       str(session_dir.parent))).resolve()
    store = FileSessionStore(str(session_root))
    writer = RunlogEventWriter()

    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))  # cwd 决定引擎工作区
    writer.notice(f"模式={mode} | 工作目录 => {session_dir}")

    # 启动即写 pid + working：首轮进行中不能被 server 误判成空闲
    #（模式切换 kill 分支据此避免杀掉正在跑的首轮，实测 1e1b540ece82）
    DaemonFiles(session_root).write_pid_and_working()

    # 用户自备 Key；禁载仓库 .env（owner 密钥不得进入用户进程）
    os.environ["DSH_NO_ENV_FILE"] = "1"
    os.environ["DEEPSEEK_API_KEY"] = api_key

    _early_write_user_prompt(store, mode,
                             os.environ.get("DSH_USER_PROMPT", "") or task_prompt,
                             _parse_prompt_images(),
                             is_resume=os.environ.get("DSH_RESUME", "") == "1")

    try:  # 重导入在此刻（cwd 已切好）；禁止轮中途 drain（daemon 逐条消费）
        os.environ["DSH_DEFER_DRAIN"] = "1"
        settings = Settings.from_env()
        engine = build_engine(settings)
    except Exception as e:
        print(f"[run_task] 引擎构建失败: {e}", flush=True)
        return 1

    messages = _assemble_first_round(store, task_prompt, _parse_prompt_images())
    if messages is None:
        return 1
    try:
        run_one_round(engine, messages, session_dir, store, writer, PROJECT_ROOT)
    except Exception as e:
        print_round_trace(e)
        notify_round_error(store, e)

    daemon_loop(engine, store, writer, session_dir, session_root, mode,
                settings.daemon_idle_timeout_s, PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""任务派发（server_app/services 层；原 start_task/pause_task 业务迁移）。

职责：模式解析三层推断（mode.txt 记忆 / /mod /chat 前缀 / 工作区沿用）、
运行中插话排队、断点恢复、daemon 模式切换重拉、子进程环境组装与 spawn。
模式推断在此唯一实现（原 server.py 与 run_task.py 两处重复已收敛）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from fastapi import HTTPException

from core.infrastructure.logging_.logger import get_logger

from infrastructure.daemon_protocol import (clear_daemon_files,
                                              enqueue_pending,
                                              read_daemon_state)
from infrastructure.process_governor import kill_session_game_processes
from infrastructure.session_disk import SessionDisk
from .session_manager import BASE_DIR, Session, kill_session_process
from .templates import has_template_content

logger = get_logger("server.task_dispatcher")

#: 子进程入口脚本。
RUN_TASK = Path(__file__).resolve().parent.parent / "run_task.py"


def resolve_mode(sess: Session, req) -> "tuple[str, str | None]":
    """解析本轮实际运行模式（三层推断 + /chat 裸切回）。

    Args:
        sess: 目标会话。
        req: TaskRequest（prompt/mode/force_mode 字段）。
    Returns:
        (mode, switched)：switched 非 None 表示仅切模式不启动任务。
    """
    mode = req.mode if req.mode in ("chat", "mod") else "chat"
    disk = SessionDisk(sess.mod_dir.parent)
    persisted = disk.read_mode()
    if persisted:
        sess.mode = persisted
    if req.prompt.strip().lower().startswith("/chat"):
        # /chat 显式切回对话；裸 "/chat" 只切模式不启动任务
        sess.mode = mode = "chat"
        stripped = req.prompt.strip()[len("/chat"):].strip()
        if not stripped:
            disk.write_mode("chat")
            return mode, "chat"
        req.prompt = stripped
    elif req.prompt.strip().lower().startswith("/mod"):
        mode = sess.mode = "mod"
    elif (sess.mode == "mod" and mode == "chat" and not req.force_mode
            and has_template_content(sess.mod_dir)):
        # mod 会话的裸消息默认沿用 mod（迭代修改）；force_mode 尊重显式 chat
        mode = "mod"
    sess.mode = mode
    disk.write_mode(mode)
    return mode, None


def queue_or_spawn(sess: Session, req, mode: str,
                   upload_names: list[str]) -> dict:
    """运行中排队 / 断点恢复 / 直接 spawn 的三分支派发。

    Args:
        sess: 目标会话。
        req: TaskRequest。
        mode: 已解析的运行模式。
        upload_names: 已落盘的图片附件名。
    Returns:
        响应 dict（queued / mode-switched / started）。
    """
    if sess.proc is not None and sess.proc.poll() is None:
        daemon_st = read_daemon_state(sess.mod_dir.parent)
        if req.resume and daemon_st != "waiting":
            raise HTTPException(409, "Task already running；请先暂停再继续")
        if _should_respawn_for_mode(sess, daemon_st, mode, req, upload_names):
            _kill_daemon_for_mode_switch(sess)
        else:
            if req.prompt.strip() or upload_names:
                try:
                    enqueue_pending(sess.mod_dir.parent,
                                    req.prompt.strip() or "（图片）",
                                    images=upload_names or None)
                except Exception as e:
                    raise HTTPException(500, "排队消息写入失败") from e
            return {"session_id": sess.id, "status": "queued", "mode": mode}
    if req.resume and (req.prompt.strip() or upload_names):
        # 带 prompt 的恢复 = 断点续跑 + 强注入新消息（先入队，恢复轮会 drain）
        try:
            enqueue_pending(sess.mod_dir.parent, req.prompt.strip() or "（图片）",
                            images=upload_names or None)
        except Exception as e:
            raise HTTPException(500, "排队消息写入失败") from e
    _spawn_task_process(sess, req, mode, upload_names)
    return {"session_id": sess.id, "status": "started", "mode": mode,
            "resume": req.resume}


def _should_respawn_for_mode(sess: Session, daemon_st: str | None,
                             mode: str, req, upload_names: list[str]) -> bool:
    """输入：daemon 状态 + 目标模式。返回：空闲 daemon 模式不同是否应杀掉重拉。

    daemon 的 cwd/工具集/系统提示词在 spawn 时固化；模式切换必须重拉，
    否则消息被旧模式 daemon 消费（实测 1e1b540ece82：/mod 后仍答只读）。
    """
    return (daemon_st == "waiting" and sess.daemon_mode
            and sess.daemon_mode != mode
            and bool(req.prompt.strip() or upload_names))


def _kill_daemon_for_mode_switch(sess: Session) -> None:
    """输入：会话。返回：无。职责：杀空闲旧模式 daemon（落到 respawn 分支）。"""
    kill_session_process(sess)
    sess.proc = None


def _spawn_task_process(sess: Session, req, mode: str,
                        upload_names: list[str]) -> None:
    """spawn run_task 子进程（cwd=BASE_DIR；stdout 追加 run.log）。

    Args:
        sess: 目标会话。
        req: TaskRequest（resume/prompt）。
        mode: 运行模式。
        upload_names: 图片附件名。
    Globals Used: os.environ —— 继承并覆盖注入（DSH_* 全套）。
    Raises:
        HTTPException: 提示词临时文件写失败（500）。
    """
    work_dir = sess.mod_dir if mode == "mod" else sess.mod_dir.parent
    prompt = _build_prompt(sess, req, mode)
    env_extra = _write_prompt_file(prompt)
    sess.apply_overrides(req)
    try:
        proc = subprocess.Popen(
            [sys.executable, str(RUN_TASK), str(work_dir), sess.api_key],
            cwd=str(BASE_DIR),
            # 追加而非截断：重拉 daemon/暂停恢复不能抹掉之前轮次的事件
            stdout=open(sess.log_path, "a", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            env=_child_env(sess, req, mode, upload_names, env_extra),
        )
    except Exception:
        if env_extra.get("DSH_PROMPT_FILE"):
            _safe_unlink(env_extra["DSH_PROMPT_FILE"])
        raise
    sess.proc = proc
    sess.started_at = time.time()
    sess.finished_at = None
    sess.result = None
    sess.event_cursor = None
    sess.daemon_mode = mode
    # 清上一轮 daemon.state：防切换后首轮被误判 waiting/finished
    clear_daemon_files(sess.mod_dir.parent)


def _build_prompt(sess: Session, req, mode: str) -> str:
    """输入：请求 + 模式。返回：实际下发的提示词（mod 首轮加工作区上下文）。"""
    if mode == "mod" and not req.resume:
        return (
            f"你是一个 MOD 制作器。请在当前工作目录（{sess.mod_dir}）下"
            f"为游戏生成一个满足以下需求的 MOD。\n"
            f"要求：\n{req.prompt.strip() or '（需求见用户上传的图片）'}\n\n"
            f"请直接创建/修改需要的所有文件，完成后汇总你创建了哪些文件。"
        )
    return req.prompt


def _write_prompt_file(prompt: str) -> dict:
    """输入：提示词。返回：含 DSH_PROMPT_FILE 的 env 附加项（绕开 argv GBK）。"""
    if not prompt:
        return {}
    try:
        fd, path = tempfile.mkstemp(suffix=".prompt.txt", prefix="dsh_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(prompt)
        return {"DSH_PROMPT_FILE": path}
    except OSError as e:
        raise HTTPException(500, f"提示词临时文件写入失败: {e}") from e


def _safe_unlink(path: str) -> None:
    """输入：路径。返回：无。职责：尽力删除临时文件（失败记日志）。"""
    try:
        os.unlink(path)
    except OSError as e:
        logger.warning("临时文件删除失败: %s", e)


def _child_env(sess: Session, req, mode: str, upload_names: list[str],
               env_extra: dict) -> dict:
    """组装子进程环境变量（模型/沙箱/模式/视觉/全自动全量注入）。"""
    env = {**os.environ,
           "DEEPSEEK_API_KEY": sess.api_key,
           "DSH_NO_ENV_FILE": "1",
           "PYTHONUNBUFFERED": "1",
           "DSH_MODEL": sess.model, "DSH_BASE_URL": sess.base_url,
           "DSH_SANDBOX_MODE": sess.sandbox,
           "DSH_MODE": mode,
           "DSH_SESSION_ROOT": str(sess.mod_dir.parent),
           "DSH_RESUME": "1" if req.resume else "0",
           # 用户原始输入优先写历史（包装版会污染侧栏标题/泄漏路径）
           "DSH_USER_PROMPT": ("" if req.resume else
                               (req.prompt.strip() or ("（图片）" if upload_names else ""))),
           # 本网站标记：chat 提示词引导 /mod 而非外站
           "DSH_WEB_CHAT": "1",
           "DSH_DISABLE_CLIENT_TOOLS": os.environ.get("DSH_DISABLE_CLIENT_TOOLS", "0"),
           "DSH_VISION_ENABLED": "1" if sess.vision_enabled else "0",
           "DSH_VISION_API_KEY": sess.vision_api_key or "",
           "DSH_VISION_BASE_URL": sess.vision_base_url or "",
           "DSH_VISION_MODEL": sess.vision_model or "",
           "DSH_AUTO_MODE": "1" if sess.auto_mode else "0",
           "DSH_TAVILY_API_KEY": sess.search_api_key or "",
           **env_extra}
    if upload_names:
        env["DSH_PROMPT_IMAGES"] = json.dumps(upload_names, ensure_ascii=False)
    return env


def pause_task(sess: Session) -> str:
    """暂停会话：kill 子进程（断点保留在 .chat/working.jsonl）。

    Returns:
        状态文本：not-running（本就没跑）| paused。
    """
    if sess.proc is None or sess.proc.poll() is not None:
        return "not-running"
    kill_session_process(sess)
    sess.proc = None
    # daemon 被强杀 finally 不执行：按清单杀游戏进程 + 清状态文件
    kill_session_game_processes(sess.mod_dir.parent)
    clear_daemon_files(sess.mod_dir.parent)
    return "paused"

# -*- coding: utf-8 -*-
"""任务执行路由（server_app/api 层）：启动/暂停/状态/结果/问答。"""
from __future__ import annotations

import json
import time

from fastapi import APIRouter, Header, HTTPException

from infrastructure.daemon_protocol import (has_working_checkpoint,
                                              pending_count)
from services.session_manager import Session
from services.stats import read_log_tail, session_stats
from services.task_dispatcher import pause_task, queue_or_spawn, resolve_mode
from services.uploads import save_upload_images
from .deps import auth_username, owned_session
from .dto import AnswerRequest, TaskRequest

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/task")
def start(req: TaskRequest, authorization: str = Header(default="")):
    """启动/排队/续跑 agent 子进程（每会话一进程隔离）。"""
    sess = owned_session(req.session_id, auth_username(authorization))
    _backfill_key(sess, req)
    if not (sess.api_key and sess.api_key.strip()):
        raise HTTPException(400, "API Key 为空，无法启动任务（请在设置中填写 API Key）")
    if not req.prompt.strip() and not req.images and not req.resume:
        raise HTTPException(400, "提示词为空，请填写内容")
    upload_names = save_upload_images(sess.mod_dir.parent, req.images)
    mode, switched = resolve_mode(sess, req)
    if switched:
        return {"session_id": sess.id, "status": "mode-switched", "mode": mode}
    if mode == "mod" and not (sess.mod_dir.exists() and any(sess.mod_dir.iterdir())):
        raise HTTPException(400, "MOD 工作区尚未准备：请先通过 /mod 触发模板复制")
    return queue_or_spawn(sess, req, mode, upload_names)


def _backfill_key(sess: Session, req: TaskRequest) -> None:
    """输入：会话 + 请求。返回：无。职责：带 key 的请求回填内存并落盘。"""
    if req.api_key:
        sess.api_key = req.api_key
        from infrastructure.session_disk import SessionDisk
        SessionDisk(sess.mod_dir.parent).write_api_key(req.api_key)


@router.post("/task/pause")
def pause(session_id: str, authorization: str = Header(default="")):
    """暂停运行中的 agent（断点保留，继续时可恢复）。"""
    sess = owned_session(session_id, auth_username(authorization))
    return {"session_id": session_id, "status": pause_task(sess)}


@router.get("/status")
def status(session_id: str, api_key: str = "",
           authorization: str = Header(default="")):
    """会话运行状态 + 日志尾部（顺带回填调用方携带的 key）。"""
    sess = owned_session(session_id, auth_username(authorization))
    if api_key and not sess.api_key:
        sess.api_key = api_key
    stats = session_stats(sess)
    log_tail = read_log_tail(sess.log_path)
    if stats["finished"] and sess.result is None:
        sess.result = log_tail  # 日志尾部即结果（历史行为保持）
        sess.finished_at = time.time()
    return {
        "session_id": session_id,
        "running": stats["running"],
        "finished": stats["finished"],
        "paused": sess.proc is None and has_working_checkpoint(sess.mod_dir.parent),
        "pending": pending_count(sess.mod_dir.parent),
        "started_at": sess.started_at,
        "finished_at": sess.finished_at,
        "log_tail": log_tail,
        **stats,
    }


@router.get("/result")
def result(session_id: str, authorization: str = Header(default="")):
    """最终结果文本（未完成时 status=running）。"""
    sess = owned_session(session_id, auth_username(authorization))
    if not session_stats(sess)["finished"]:
        return {"status": "running", "result": None}
    return {"status": "finished", "result": sess.result or ""}


@router.get("/question")
def question(session_id: str, authorization: str = Header(default="")):
    """读取 agent 待回答的问题（ask_user_question 写入的 question.json）。"""
    sess = owned_session(session_id, auth_username(authorization))
    qpath = sess.mod_dir.parent / "question.json"
    if not qpath.exists():
        return {"status": "none"}
    try:
        data = json.loads(qpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "none"}
    if isinstance(data.get("questions"), list) and data["questions"]:
        return {"status": "pending", "questions": data["questions"]}
    if data.get("question"):  # 旧单题格式归一化
        return {"status": "pending",
                "questions": [{"question": data["question"],
                               "options": data.get("options") or []}]}
    return {"status": "none"}


@router.post("/answer")
def answer(req: AnswerRequest, authorization: str = Header(default="")):
    """写入用户回答（answer.json；agent 的 ask 工具轮询到后继续）。"""
    sess = owned_session(req.session_id, auth_username(authorization))
    payload = ({"answers": req.answers} if req.answers is not None
               else {"answer": req.answer})
    (sess.mod_dir.parent / "answer.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}

# -*- coding: utf-8 -*-
"""流式 SSE 生成器（由 chat_endpoint.py 拆出）。

类职责：daemon 推理文件实时转发（delta.reasoning）+ 结果帧分片
输出 + 中途出错友好降级；与 chat_endpoint 的路由层解耦。
生命周期：仅 chat_endpoint.stream 分支调用。
"""
import json  # daemon 推理/结果文件解析
import logging  # 降级记录
import time  # 轮询节流

from daemon_api import (_DAEMONS, append_conversation,
                        ensure_session_daemon, session_workdir,
                        submit_daemon_request)
from openai_wire import new_id, reasoning_delta, sse_frame, usage_zero
from replies import append_persona_guide, friendly_agent_error

logger = logging.getLogger("tsinghua.stream")

def _opening_frames(messages: list, cid: str, created: int):
    """开场帧：role 帧 + 首次启动/常规调用的思考提示帧（SSE 生成器）。"""
    yield sse_frame(cid, created, {"role": "assistant"})
    is_first = not any(isinstance(m, dict) and m.get("role") == "assistant"
                       for m in messages)
    tip = "🔧 首次启动准备中，会稍微慢一点，请耐心等待～" if is_first else "正在调用自研 Agent 引擎…"
    yield sse_frame(cid, created, reasoning_delta(tip))


def _read_new_reasoning_lines(reasoning_file, last_idx: int) -> tuple[list, int]:
    """读取推理文件的新增完整行。

    daemon 可能写到一半（末行无换行符）：半行留到下次轮询，否则
    json 解析失败 + 游标提前推进会丢思考文本。
    Args:
        reasoning_file: 推理 jsonl 路径。last_idx: 已消费行数。
    Returns:
        (新增行列表, 新游标)。
    """
    raw = reasoning_file.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if raw and not raw.endswith("\n"):
        lines = lines[:-1]
    return lines[last_idx:], len(lines)


def _content_frames(final: str, cid: str, created: int):
    """最终正文按 8 字符分片成 content 帧（SSE 生成器）。"""
    step = 8
    for i in range(0, len(final), step):
        yield sse_frame(cid, created, {"content": final[i:i + step]})


def _cleanup_daemon_files(*files) -> None:
    """清理 daemon 临时文件（推理/结果，失败降级忽略）。"""
    for p in files:
        try:
            if p.exists():
                p.unlink()
        except OSError as e:
            logger.debug("清理 daemon 临时文件失败（降级忽略） | %s", p.name)


def _reasoning_frames(lines: list, cid: str, created: int):
    """推理行列表 → SSE 思考帧（坏行跳过，SSE 生成器）。"""
    for line in lines:
        try:
            obj = json.loads(line)
            yield sse_frame(cid, created, reasoning_delta(obj.get("text", "")))
        except Exception:  # noqa: BLE001
            continue


def _submit_and_paths(session_id: str, messages: list):
    """提交 daemon 请求并返回轮询所需的文件路径与进程句柄。

    Returns:
        (会话根, 起始时间戳, 推理文件, 结果文件, daemon 进程或 None)。
    """
    session_root = session_workdir(session_id)
    start_ts = time.time()
    ensure_session_daemon(session_root)
    rid = submit_daemon_request(session_root, messages)
    reasoning_file = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    result_file = session_root / "daemon" / "results" / f"{rid}.json"
    daemon_proc = _DAEMONS.get(str(session_root))
    return session_root, start_ts, reasoning_file, result_file, daemon_proc


def _error_frames(e: Exception, cid: str, created: int):
    """流式中途出错的降级帧序列（SSE 生成器）。

    指南 §5.6：stop 帧附 error 字段；友好文案仍走 content 帧保证用户可见。
    """
    err_msg = friendly_agent_error(e)
    for i in range(0, len(err_msg), 8):
        yield sse_frame(cid, created, {"content": err_msg[i:i + 8]})
    yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(),
                    error={"type": "upstream_error", "message": str(e)[:200]})
    yield "data: [DONE]\n\n"


def _read_daemon_result(result_file, messages: list, session_id: str) -> str:
    """读 daemon 结果文件（错误转 RuntimeError；正文过人格指南后落历史）。"""
    data = json.loads(result_file.read_text(encoding="utf-8-sig"))
    if data.get("error"):
        raise RuntimeError(data["error"])
    final = data.get("text") or "(no response)"
    final = append_persona_guide(final, messages)
    append_conversation(session_id, messages, final)
    return final


def stream_agent(messages: list, session_id: str, base_url: str):
    """流式 Agent：常驻 daemon 处理请求，实时读推理文件转发 delta.reasoning。"""
    cid = new_id()
    created = int(time.time())
    yield from _opening_frames(messages, cid, created)

    session_root, start_ts, reasoning_file, result_file, daemon_proc = (
        _submit_and_paths(session_id, messages))
    final = None
    last_idx = 0
    deadline = time.time() + 900
    try:
        while time.time() < deadline:
            if reasoning_file.exists():
                try:
                    new_lines, last_idx = _read_new_reasoning_lines(
                        reasoning_file, last_idx)
                    yield from _reasoning_frames(new_lines, cid, created)
                except OSError as e:
                    logger.debug("推理文件轮询读取失败（降级忽略） | %s", e)
            if result_file.exists():
                final = _read_daemon_result(result_file, messages, session_id)
                break
            if daemon_proc is not None and daemon_proc.poll() is not None:
                raise RuntimeError("AI 服务进程已退出，请检查服务配置")
            time.sleep(0.1)
        if final is None:
            raise RuntimeError("agent daemon timeout")
        attachments = collect_attachments(start_ts, base_url, scope=session_root)
    except Exception as e:  # noqa: BLE001
        yield from _error_frames(e, cid, created)
        return
    finally:
        _cleanup_daemon_files(reasoning_file, result_file)

    yield from _content_frames(final or "", cid, created)

    extra = {}
    if attachments:
        extra["x_soda"] = {"attachments": attachments}
    yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(), extra=extra)
    yield "data: [DONE]\n\n"

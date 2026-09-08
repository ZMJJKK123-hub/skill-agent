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

def stream_agent(messages: list, session_id: str, base_url: str):
    """流式 Agent：常驻 daemon 处理请求，实时读推理文件转发 delta.reasoning。"""
    cid = new_id()
    created = int(time.time())

    yield sse_frame(cid, created, {"role": "assistant"})
    is_first_request = not any(
        isinstance(m, dict) and m.get("role") == "assistant"
        for m in messages
    )
    if is_first_request:
        yield sse_frame(cid, created, reasoning_delta("🔧 首次启动准备中，会稍微慢一点，请耐心等待～"))
    else:
        yield sse_frame(cid, created, reasoning_delta("正在调用自研 Agent 引擎…"))

    session_root = session_workdir(session_id)
    start_ts = time.time()
    ensure_session_daemon(session_root)
    rid = submit_daemon_request(session_root, messages)
    reasoning_file = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    result_file = session_root / "daemon" / "results" / f"{rid}.json"
    daemon_proc = _DAEMONS.get(str(session_root))
    final = None
    last_idx = 0
    deadline = time.time() + 900
    try:
        while time.time() < deadline:
            if reasoning_file.exists():
                try:
                    raw = reasoning_file.read_text(encoding="utf-8")
                    lines = raw.splitlines()
                    # daemon 可能写到一半（末行无换行符）：半行留到下次轮询再处理，
                    # 否则 json 解析失败 + last_idx 提前推进会丢思考文本
                    if raw and not raw.endswith("\n"):
                        lines = lines[:-1]
                    for line in lines[last_idx:]:
                        try:
                            obj = json.loads(line)
                            yield sse_frame(cid, created, reasoning_delta(obj.get("text", "")))
                        except Exception:  # noqa: BLE001
                            continue
                    last_idx = len(lines)
                except OSError as e:
                    logger.debug("推理文件轮询读取失败（降级忽略） | %s", e)
            if result_file.exists():
                data = json.loads(result_file.read_text(encoding="utf-8-sig"))
                if data.get("error"):
                    raise RuntimeError(data["error"])
                final = data.get("text") or "(no response)"
                final = append_persona_guide(final, messages)
                append_conversation(session_id, messages, final)
                break
            if daemon_proc is not None and daemon_proc.poll() is not None:
                raise RuntimeError("AI 服务进程已退出，请检查服务配置")
            time.sleep(0.1)
        if final is None:
            raise RuntimeError("agent daemon timeout")
        attachments = collect_attachments(start_ts, base_url, scope=session_root)
    except Exception as e:  # noqa: BLE001
        err_msg = friendly_agent_error(e)
        err_step = 8
        for i in range(0, len(err_msg), err_step):
            yield sse_frame(cid, created, {"content": err_msg[i:i + err_step]})
        # 指南 §5.6：流式中途出错时，stop 帧附 error 字段（友好文案仍走 content 帧保证用户可见）
        yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(),
                         error={"type": "upstream_error", "message": str(e)[:200]})
        yield "data: [DONE]\n\n"
        return
    finally:
        for p in (reasoning_file, result_file):
            try:
                if p.exists():
                    p.unlink()
            except OSError as e:
                logger.debug("清理 daemon 临时文件失败（降级忽略） | %s", p.name)

    step = 8
    for i in range(0, len(final or ""), step):
        yield sse_frame(cid, created, {"content": (final or "")[i:i + step]})

    extra = {}
    if attachments:
        extra["x_soda"] = {"attachments": attachments}
    yield sse_frame(cid, created, {}, finish_reason="stop", usage=usage_zero(), extra=extra)
    yield "data: [DONE]\n\n"

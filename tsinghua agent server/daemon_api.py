# -*- coding: utf-8 -*-
"""Agent 引擎调用编排：会话 daemon 子进程 / 请求队列 / 结果轮询（由 main.py 迁出）。"""
import json
import re
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from config_env import WORKSPACE

from attachments import collect_attachments
from normalize import is_mod_request, last_user_content
from replies import append_service_notice, append_persona_guide, append_web_hint


# 每个会话的常驻 daemon 子进程注册表
_DAEMONS: dict[str, subprocess.Popen] = {}
_DAEMON_LOCK = threading.Lock()


def cleanup_daemons() -> None:
    """服务退出时终止所有常驻 daemon 子进程，避免残留。"""
    for proc in list(_DAEMONS.values()):
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass
    _DAEMONS.clear()










def append_conversation(session_id: str, messages, final_text: str) -> None:
    """把最新一轮 user 和 assistant 回复追加到会话 conversation.jsonl（不含思考）。"""
    try:
        session_root = session_workdir(session_id)
        chat_dir = session_root / ".chat"
        chat_dir.mkdir(parents=True, exist_ok=True)
        conv_file = chat_dir / "conversation.jsonl"
        user = last_user_content(messages)
        entries = []
        if user:
            entries.append({"role": "user", "content": user})
        if final_text:
            entries.append({"role": "assistant", "content": final_text})
        if entries:
            with conv_file.open("a", encoding="utf-8") as f:
                for e in entries:
                    f.write(json.dumps(e, ensure_ascii=False) + chr(10))
    except Exception:
        pass  # 会话历史是旁路数据，失败不阻断响应


def session_workdir(session_id: str) -> Path:
    """为每个清小搭 sessionId 分配独立工作目录，用于隔离对话历史/断点。"""
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "")[:64].strip("._") or "default"
    d = WORKSPACE / "sessions" / safe
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_session_daemon(session_root: Path) -> None:
    """确保该会话的常驻 daemon 子进程在运行。"""
    key = str(session_root)
    with _DAEMON_LOCK:
        proc = _DAEMONS.get(key)
        if proc is not None and proc.poll() is None:
            return
        daemon = Path(__file__).resolve().parent / "session_daemon.py"
        log_path = session_root / "daemon" / "daemon.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logf = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(daemon), str(session_root)],
            cwd=str(session_root),
            stdout=logf,
            stderr=subprocess.STDOUT,
        )
        _DAEMONS[key] = proc
        # 快速失败检测：2 秒内如进程退出，说明初始化失败（如缺 API Key）
        time.sleep(2)
        if proc.poll() is not None:
            _DAEMONS.pop(key, None)
            tail = ""
            try:
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    _lines = f.read().splitlines()
                tail = " | ".join(_lines[-3:])
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError("AI 服务初始化失败：" + (tail if tail else "daemon 进程异常退出"))


def submit_daemon_request(session_root: Path, messages: list) -> str:
    rid = uuid.uuid4().hex
    qdir = session_root / "daemon" / "queue"
    qdir.mkdir(parents=True, exist_ok=True)
    (qdir / f"{rid}.json").write_text(json.dumps(messages, ensure_ascii=False), encoding="utf-8")
    return rid


def wait_daemon_result(session_root: Path, rid: str, timeout: int = 900) -> dict:
    rfile = session_root / "daemon" / "results" / f"{rid}.json"
    deadline = time.time() + timeout
    proc = _DAEMONS.get(str(session_root))
    while time.time() < deadline:
        if rfile.exists():
            data = json.loads(rfile.read_text(encoding="utf-8-sig"))
            try:
                rfile.unlink()
            except OSError:
                pass
            return data
        if proc is not None and proc.poll() is not None and not rfile.exists():
            raise RuntimeError("AI 服务进程已退出，请检查服务配置")
        time.sleep(0.2)
    raise RuntimeError("AI 服务响应超时")


def collect_daemon_reasoning(session_root: Path, rid: str) -> str:
    """聚合 daemon 推理文件里的全部思考文本，并清理该文件（非流式响应用）。"""
    rfile = session_root / "daemon" / "reasoning" / f"{rid}.jsonl"
    parts: list[str] = []
    try:
        for line in rfile.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            t = obj.get("text")
            if t:
                parts.append(t)
    except OSError:
        pass
    finally:
        try:
            if rfile.exists():
                rfile.unlink()
        except OSError:
            pass
    return "".join(parts)


def run_agent(messages: list, session_id: str, base_url: str,
               reasoning_sink=None) -> tuple[str, list, str]:
    """通过常驻 daemon 子进程运行 agent_loop，保证用户/会话隔离。

    返回 (text, attachments, reasoning)；reasoning 为思考全文（可为空），
    供非流式响应放在 message.reasoning_content 里。
    """
    mod_related = is_mod_request(messages)
    start_ts = time.time()
    session_root = session_workdir(session_id)
    ensure_session_daemon(session_root)
    rid = submit_daemon_request(session_root, messages)
    result = wait_daemon_result(session_root, rid)
    reasoning = collect_daemon_reasoning(session_root, rid)
    if result.get("error"):
        raise RuntimeError(result["error"])
    text = result.get("text") or "(no response)"
    text = append_web_hint(text, mod_related)
    text = append_service_notice(text)
    text = append_persona_guide(text, messages)
    append_conversation(session_id, messages, text)
    attachments = collect_attachments(start_ts, base_url, scope=session_root)
    return text, attachments, reasoning


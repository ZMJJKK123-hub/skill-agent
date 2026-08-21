# -*- coding: utf-8 -*-
"""清小搭每会话常驻 daemon worker。

用法：
  session_daemon.py <session_dir>

在 session_dir 的 daemon 子目录下监听请求队列：
  daemon/queue/<req_id>.json      请求（内容为 messages 列表）
  daemon/results/<req_id>.json    结果 {"text":..., "error":...}
  daemon/reasoning/<req_id>.jsonl 实时思考行 {"text":...}

常驻后仅首次加载 core；同一会话后续请求走队列，无冷启动。
"""
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

session_dir = Path(sys.argv[1]).resolve()
session_dir.mkdir(parents=True, exist_ok=True)

os.environ["DSH_SESSION_ROOT"] = str(session_dir)
os.environ.setdefault("DSH_MODE", "chat")
os.environ["DSH_AUTO_MODE"] = "1"
os.environ.setdefault("DSH_SANDBOX_MODE", "workspace-write")
os.environ["DSH_SESSION_ROOT"] = str(session_dir)
os.chdir(session_dir)

queue_dir = session_dir / "daemon" / "queue"
results_dir = session_dir / "daemon" / "results"
reasoning_dir = session_dir / "daemon" / "reasoning"
for d in (queue_dir, results_dir, reasoning_dir):
    d.mkdir(parents=True, exist_ok=True)

IDLE_TIMEOUT = float(os.environ.get("DSH_DAEMON_IDLE_TIMEOUT", "600"))
last_activity = time.time()

from core.agent import agent_loop, set_reasoning_sink  # noqa: E402


def _write_json(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _process_request(req_path: Path) -> None:
    global last_activity
    last_activity = time.time()
    rid = req_path.stem
    reasoning_file = reasoning_dir / f"{rid}.jsonl"
    result_file = results_dir / f"{rid}.json"
    # 清空旧的推理文件
    try:
        reasoning_file.write_text("", encoding="utf-8")
    except Exception:
        pass

    def _sink(text: str) -> None:
        try:
            with reasoning_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
        except Exception:
            pass

    try:
        messages = json.loads(req_path.read_text(encoding="utf-8-sig"))
        set_reasoning_sink(_sink)
        final = agent_loop(messages)
        text = str(final) if final is not None else "(no response)"
        _write_json(result_file, {"text": text, "error": None})
    except Exception as e:  # noqa: BLE001
        _write_json(result_file, {"text": "", "error": str(e)})
    finally:
        set_reasoning_sink(None)
        try:
            req_path.unlink()
        except Exception:
            pass


def main() -> None:
    print(f"[session_daemon] started for {session_dir}", flush=True)
    while True:
        try:
            for req_path in sorted(queue_dir.glob("*.json")):
                _process_request(req_path)
        except Exception as e:  # noqa: BLE001
            print(f"[session_daemon] loop error: {e}", flush=True)
        if time.time() - last_activity > IDLE_TIMEOUT:
            print(f"[session_daemon] idle timeout ({IDLE_TIMEOUT}s), exit", flush=True)
            break
        time.sleep(0.2)


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""P7 真实 /mod 冒烟驱动：起临时 server → 建会话 → 模板 → 任务 → 轮询 → 验收。

用法（仓库根）：
    python tests/p7_smoke.py
依赖 .env 的 DEEPSEEK_API_KEY / DSH_MODEL / DSH_BASE_URL（owner 配置）。
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = 8902
BASE = f"http://127.0.0.1:{PORT}"
PROMPT = ("/mod 做一个蓝宝石剑（sapphiresword），攻击力 9，"
          "合成配方：1 个蓝宝石 + 2 根木棍（竖排：上宝石、中棍、下棍）")


def load_env() -> dict:
    """输入：无。返回：.env 的键值表（简单解析，无 dotenv 依赖）。"""
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


def req(method: str, path: str, payload: dict | None = None,
        timeout: int = 120) -> tuple[int, dict | bytes]:
    """输入：方法/路径/负载。返回：(状态码, JSON dict 或原始字节)。"""
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            body = resp.read()
            try:
                return resp.status, json.loads(body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]


def main() -> int:
    env = load_env()
    assert env.get("DEEPSEEK_API_KEY"), ".env 缺 DEEPSEEK_API_KEY"
    server_env = {**os.environ, "DSH_NO_ENV_FILE": "1",
                  "DSH_DISABLE_CLIENT_TOOLS": "1"}
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app",
         "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"],
        cwd=str(ROOT / "server_app"), env=server_env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[p7] server pid={server.pid} port={PORT}", flush=True)
    try:
        for _ in range(30):  # 等服务就绪
            time.sleep(1)
            try:
                code, body = req("GET", "/api/health", timeout=5)
                if code == 200:
                    break
            except OSError:
                continue
        else:
            print("[p7] FAIL: server 未就绪");  return 1

        code, body = req("POST", "/api/session", {
            "api_key": env["DEEPSEEK_API_KEY"],
            "model": env.get("DSH_MODEL", ""),
            "base_url": env.get("DSH_BASE_URL", "")})
        assert code == 200, body
        sid = body["session_id"]
        print(f"[p7] session={sid}", flush=True)

        code, body = req("POST", f"/api/session/mod?session_id={sid}"
                                   "&loader=forge&version=1.21.11")
        print(f"[p7] prepare_mod: {code} {body}", flush=True)
        assert code == 200

        code, body = req("POST", "/api/task", {
            "session_id": sid, "prompt": PROMPT, "mode": "mod"})
        print(f"[p7] task: {code} {body}", flush=True)
        assert code == 200, body

        deadline = time.time() + 35 * 60
        last_state = ""
        while time.time() < deadline:
            time.sleep(15)
            code, st = req("GET", f"/api/status?session_id={sid}")
            assert code == 200, st
            state = st.get("state")
            if state != last_state:
                print(f"[p7] {time.strftime('%H:%M:%S')} state={state} "
                      f"elapsed={st.get('elapsed')}s pending={st.get('pending')}",
                      flush=True)
                last_state = state
            if state == "finished" and st.get("pending", 0) == 0:
                break
            if state == "pending" and st.get("elapsed") is None:
                print("[p7] WARN: 任务未真正启动（pending）", flush=True)
        else:
            print("[p7] FAIL: 35 分钟超时未完成", flush=True)
            return 1

        code, result = req("GET", f"/api/result?session_id={sid}")
        summary = str(result.get("result") or "")[:600]
        print(f"[p7] result(head): {summary!r}", flush=True)

        code, jar = req("GET", f"/api/download/jar?session_id={sid}")
        jar_ok = code == 200 and isinstance(jar, bytes) and len(jar) > 1000
        print(f"[p7] jar: http={code} bytes={len(jar) if isinstance(jar, bytes) else jar}",
              flush=True)
        code, events = req("GET", f"/api/events?session_id={sid}")
        ev = events.get("events", []) if isinstance(events, dict) else []
        kinds: dict = {}
        for e in ev:
            kinds[e.get("type")] = kinds.get(e.get("type"), 0) + 1
        print(f"[p7] events: {len(ev)} 条，类型分布={kinds}", flush=True)
        code, zipb = req("GET", f"/api/download?session_id={sid}")
        zip_ok = code == 200 and isinstance(zipb, bytes) and len(zipb) > 10000
        print(f"[p7] zip: http={code} bytes={len(zipb) if isinstance(zipb, bytes) else zipb}",
              flush=True)

        ok = jar_ok and zip_ok and len(ev) > 5
        print(f"[p7] {'SMOKE_PASS' if ok else 'SMOKE_FAIL'}", flush=True)
        if not ok:  # 失败时保留 run.log 供诊断（成功才清理会话）
            log_path = ROOT / "data" / "sessions" / sid / "run.log"
            if log_path.exists():
                keep = ROOT / "tests" / f"p7_fail_{sid}_run.log"
                keep.write_text(log_path.read_text(encoding="utf-8", errors="replace"),
                                encoding="utf-8")
                print(f"[p7] run.log 已保留: {keep}", flush=True)
            return 1
        req("DELETE", f"/api/session?session_id={sid}")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    sys.exit(main())

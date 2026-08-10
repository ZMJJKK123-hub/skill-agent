"""gradletools: 8 个 Gradle 验证工具（Agent 写码-运行-解析-修正闭环）。
目录隔离硬规则: main 仅业务代码(禁@GameTest); test 唯一测试位置; 自测核心=runTestGameTestServer。
统一返回 {"success","exit_code","summary","error_details","raw_logs_snippet"}。
"""
import json, os, re, subprocess
from pathlib import Path


def _run_gradle(task, timeout, base):
    if not os.path.exists(os.path.join(base, "build.gradle")):
        return {"exit_code": -1, "raw": "", "tail": ""}
    if os.name == "nt":
        g = "gradlew.bat" if os.path.exists(os.path.join(base, "gradlew.bat")) else "gradle"
        cmd = ["cmd", "/c", g, task, "--console=plain"]
    else:
        g = "./gradlew" if os.path.exists(os.path.join(base, "gradlew")) else "gradle"
        cmd = [g, task, "--console=plain"]
    try:
        p = subprocess.Popen(cmd, cwd=base, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace",
                             env={**os.environ, "PYTHONUTF8": "1"})
    except Exception as e:
        return {"exit_code": -1, "raw": str(e), "tail": str(e)}
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            if os.name == "nt":
                subprocess.run(f"taskkill /f /t /pid {p.pid}", shell=True, capture_output=True)
            else:
                os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            pass
        try:
            p.communicate(timeout=5)
        except Exception:
            pass
        return {"exit_code": -1, "raw": (out or "") + "\n[TIMEOUT]",
                "tail": (out or "")[-4000:]}
    txt = out or ""
    return {"exit_code": p.returncode, "raw": txt, "tail": txt[-4000:]}


def _ok(res, summary):
    return {"success": True, "exit_code": 0, "summary": summary,
            "error_details": None, "raw_logs_snippet": res["tail"][-1500:]}


def _fail(res, summary, etype=None, emsg=None, loc=""):
    return {"success": False, "exit_code": res["exit_code"], "summary": summary,
            "error_details": {"type": etype, "message": emsg, "file_location": loc},
            "raw_logs_snippet": res["tail"][-1500:]}


def _dev_err(res):
    txt = res.get("raw", "")
    m = re.search(r"(error:\s*[^\n]+|> Task :[^\n]*(?:FAILED|failed))", txt)
    lm = re.search(r"([A-Za-z0-9_/.\\<>]+\.java:\d+)", txt)
    return ("compile_error", m.group(1) if m else "BUILD FAILED", lm.group(1) if lm else "")


# ---------- 8 个工具 ----------
def run_data_gen(base, timeout=120):
    res = _run_gradle("runData", timeout, base)
    if res["exit_code"] != 0 and "BUILD SUCCESSFUL" not in res.get("raw", ""):
        t, m, l = _dev_err(res)
        return _fail(res, "DataGen FAILED", t, m, l)
    return _ok(res, "DataGen SUCCESSFUL")


def run_game_test_server(base, timeout=180):
    res = _run_gradle("runGameTestServer", timeout, base)
    if res["exit_code"] != 0 and "BUILD SUCCESSFUL" not in res.get("raw", ""):
        t, m, l = _dev_err(res)
        return _fail(res, "GameTestServer FAILED", t, m, l)
    return _ok(res, "GameTestServer finished (use read_game_test_log for details)")


def run_server(base, timeout=60):
    res = _run_gradle("runServer", timeout, base)
    txt = res.get("raw", "")
    if "Done (" in txt:
        return _ok(res, "Server booted: Done. Dedicated-server compatible.")
    cr = Path(base) / "crash-reports"
    crash = ""
    if cr.is_dir():
        fs = sorted(cr.glob("crash-*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        if fs:
            crash = fs[0].read_text(encoding="utf-8", errors="replace")[:2000]
    mt = re.search(r"(NoClassDefFoundError|ClassCastException|NullPointerException|FATAL)", txt + crash)
    return _fail(res, "Server did not reach Done", mt.group(1) if mt else "server_crash",
                 crash[:300], "")


def run_client(base, timeout=90):
    res = _run_gradle("runClient", timeout, base)
    txt = res.get("raw", "")
    if "BUILD FAILED" in txt or "Exception" in txt:
        t, m, l = _dev_err(res)
        return _fail(res, "Client crash/fail", t, m, l)
    return _ok(res, "Client launched without visible crash")


def _run_test_task(task, base, timeout):
    res = _run_gradle(task, timeout, base)
    if res["exit_code"] != 0 and "BUILD SUCCESSFUL" not in res.get("raw", "") and "Done (" not in res.get("raw", ""):
        t, m, l = _dev_err(res)
        return _fail(res, f"{task} FAILED", t, m, l)
    return _ok(res, f"{task} finished OK")


def run_test_client(base, timeout=90):
    return _run_test_task("runTestClient", base, timeout)


def run_test_server(base, timeout=90):
    return _run_test_task("runTestServer", base, timeout)


def run_test_data(base, timeout=120):
    return _run_test_task("runTestData", base, timeout)


def run_test_gametest(base, timeout=180):
    res = _run_gradle("runTestGameTestServer", timeout, base)
    txt = res.get("raw", "")
    if res["exit_code"] != 0 and "BUILD SUCCESSFUL" not in txt and "Done (" not in txt:
        t, m, l = _dev_err(res)
        return _fail(res, "TestGameTestServer FAILED", t, m, l)
    if re.search(r"FAILED|Failed to|Exception", txt):
        return _fail(res, "TestGameTestServer: some tests failed", "GameTestFailure", txt[-800:], "")
    return _ok(res, "TestGameTestServer OK (src/test gametests passed)")


GRADLE_TOOLS = {
    "run_client": run_client,
    "run_server": run_server,
    "run_data_gen": run_data_gen,
    "run_game_test_server": run_game_test_server,
    "run_test_client": run_test_client,
    "run_test_server": run_test_server,
    "run_test_data": run_test_data,
    "run_test_gametest": run_test_gametest,
}
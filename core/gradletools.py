"""gradletools: 8 个 Gradle 验证工具（Agent 写码-运行-解析-修正闭环）。
目录隔离硬规则: main 仅业务代码(禁@GameTest); test 唯一测试位置; 自测核心=runTestGameTestServer。
统一返回 {"success","exit_code","summary","error_details","raw_logs_snippet"}。
"""
import json, os, re, subprocess
from pathlib import Path

from . import process_manager as pm


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
    out = ""
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as _te:
        # 超时后进程可能已死，二次 communicate 也可能抛异常——此前 out 未初始化
        # 直接 UnboundLocalError（ERROR_LIST 记录的历史工具 bug，此处根治）
        partial = _te.stdout if isinstance(getattr(_te, "stdout", None), str) else ""
        if partial:
            out += partial
        try:
            if os.name == "nt":
                subprocess.run(f"taskkill /f /t /pid {p.pid}", shell=True, capture_output=True)
            else:
                os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            pass
        try:
            more, _ = p.communicate(timeout=5)
            out += more or ""
        except Exception:
            pass
        return {"exit_code": -1, "raw": out + "\n[TIMEOUT]",
                "tail": out[-4000:]}
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
    m = re.search(r"(error:\s*[^\n]+|错误:\s*[^\n]+|> Task :[^\n]*(?:FAILED|failed))", txt)
    lm = re.search(r"([A-Za-z0-9_/.\\<>]+\.java:\d+)", txt)
    return ("compile_error", m.group(1) if m else "BUILD FAILED", lm.group(1) if lm else "")


def _is_long_running_run(task: str) -> bool:
    """runClient/runTestClient/runServer 等"游戏进程型"任务：阻塞到游戏退出。"""
    import re
    return bool(re.match(r"^run(Test)?(Client|Server|GameTestServer|TestGameTestServer)$", task))


def _kill_workspace_clients(base: str) -> None:
    """启动新客户端前，杀掉本工作区残留的游戏 java 进程（防双客户端/目录锁）。

    webserv_lapisamulet 实测：超时只杀掉 gradle 包装进程，游戏是 daemon 的
    子进程得以幸存 → 僵尸客户端 + 第二个客户端共用 run/ 目录锁死崩溃。
    """
    if os.name != "nt":
        return
    try:
        import subprocess as _sp
        marker = os.path.abspath(base).replace("\\", "\\\\").lower()
        q = (f"Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
             f"Where-Object {{ $_.CommandLine -match 'run(Client|TestClient)' -and "
             f"$_.CommandLine -match [regex]::Escape('{marker}') }} | "
             f"ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}")
        _sp.run(["powershell", "-NoProfile", "-Command", q],
                capture_output=True, timeout=20)
    except Exception:
        pass


def _gradle_cmd(task, base):
    """Return the command to run a Gradle task in the given mod base dir."""
    if not os.path.exists(os.path.join(base, "build.gradle")):
        return None
    extra = ["--no-daemon"] if _is_long_running_run(task) else []
    if os.name == "nt":
        g = "gradlew.bat" if os.path.exists(os.path.join(base, "gradlew.bat")) else "gradle"
        return ["cmd", "/c", g, task, "--console=plain", *extra]
    g = "./gradlew" if os.path.exists(os.path.join(base, "gradlew")) else "gradle"
    return [g, task, "--console=plain", *extra]


def start_gradle_task(task, base, handle="mc"):
    """Start a Gradle task in background; returns immediately with handle/pid/log_path."""
    cmd = _gradle_cmd(task, base)
    if cmd is None:
        return {"success": False, "message": f"No build.gradle in {base}"}
    if _is_long_running_run(task):
        _kill_workspace_clients(base)
    log_path = Path(base) / "run" / f"{handle}.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8", errors="replace")
        proc = subprocess.Popen(
            cmd, cwd=base,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
        pm.register(handle, proc, task, base, log_path)
        return {
            "success": True,
            "handle": handle,
            "pid": proc.pid,
            "log_path": str(log_path),
            "message": f"Started '{task}' in background (handle={handle}, pid={proc.pid})",
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to start {task}: {e}"}


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
    """Run 'gradlew runServer' in background (non-blocking).

    Use mc_status / wait_for_log / wait_for_port to check when it reaches 'Done'.
    The previous blocking behavior moved to start_gradle_task; this keeps the
    same tool name for compatibility but no longer blocks the agent loop.
    """
    res = start_gradle_task("runServer", base, "mc-server")
    if not res["success"]:
        return {"success": False, "exit_code": -1, "summary": res["message"],
                "error_details": None, "raw_logs_snippet": res["message"]}
    return {"success": True, "exit_code": 0, "summary": res["message"],
            "error_details": None, "raw_logs_snippet": f"Server starting in background. Log: {res['log_path']}\nUse mc_status or wait_for_log to check readiness."}


def run_client(base, timeout=90):
    """Run 'gradlew runClient' in background (non-blocking).

    Use mc_status / wait_for_log / wait_for_screen to observe the GUI client.
    The previous blocking behavior moved to start_gradle_task.
    """
    res = start_gradle_task("runClient", base, "mc-client")
    if not res["success"]:
        return {"success": False, "exit_code": -1, "summary": res["message"],
                "error_details": None, "raw_logs_snippet": res["message"]}
    return {"success": True, "exit_code": 0, "summary": res["message"],
            "error_details": None, "raw_logs_snippet": f"Client starting in background. Log: {res['log_path']}\nUse mc_status or wait_for_log to check readiness."}


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
    # 判定顺序：显式通过标记最优先。数据包解析错误（如配方旧格式
    # "Failed to parse"）或 DISTXFORM 等 ERROR 行不是 GameTest 失败，
    # 不能盖过 "All N required tests passed"（红宝石剑会话曾因此连续
    # 误报 FAIL，白跑多轮 build+GameTest）。
    if re.search(r"All [1-9]\d* required tests passed", txt):
        return _ok(res, "TestGameTestServer OK (all required tests passed)")
    if res["exit_code"] != 0 and "BUILD SUCCESSFUL" not in txt and "Done (" not in txt:
        t, m, l = _dev_err(res)
        return _fail(res, "TestGameTestServer FAILED", t, m, l)
    # 只认 GameTest 自己报告的失败；裸 "Failed to"/"Exception" 会命中
    # 非测试噪音（数据包解析、dist 清理器日志），造成假阴性。
    if re.search(r"required tests failed|tests failed|FAILED!", txt):
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
# -*- coding: utf-8 -*-
"""完整 MOD 会话启动器：走 server_app 的真实建会话流程 + run_task.py。

用法：
  python server_app/run_full_mod_task.py <session_id> <api_key> <prompt_file>

它会：
1. 创建 data/sessions/<session_id>/mod
2. 调用 server._copy_template(...)（自动复制模板 + mc_java_sources + docs/agent）
3. 通过 server_app/run_task.py 启动完整 agent 循环，日志写入 run.log
"""
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from server_app.server import _copy_template  # noqa: E402


def _load_env_file(path: Path) -> dict:
    """读取 .env 的 KEY=VALUE（不打印值）。"""
    result = {}
    if not path.exists():
        return result
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python run_full_mod_task.py <session_id> <api_key|auto> <prompt_file>")
        return 1

    session_id = sys.argv[1]
    api_key = sys.argv[2]
    prompt_file = Path(sys.argv[3]).resolve()
    if not prompt_file.exists():
        print(f"[run_full] prompt file not found: {prompt_file}")
        return 1

    env_file = PROJECT_ROOT / ".env"
    env_extra = _load_env_file(env_file)
    if api_key == "auto":
        api_key = env_extra.get("DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            print("[run_full] auto mode requested but no DEEPSEEK_API_KEY found in .env")
            return 1

    sessions_dir = PROJECT_ROOT / "data" / "sessions"
    session_dir = sessions_dir / session_id
    mod_dir = session_dir / "mod"

    if mod_dir.exists():
        import shutil
        shutil.rmtree(session_dir, ignore_errors=True)
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[run_full] 使用完整 server._copy_template 创建会话: {mod_dir}")
    _copy_template("minecraft", mod_dir, "forge", "1.21.11")

    env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "DSH_MODE": "mod",
        "DSH_SESSION_ROOT": str(session_dir),
        "DSH_AUTO_MODE": "1",
        "DSH_PROMPT_FILE": str(prompt_file),
        "DEEPSEEK_API_KEY": api_key,
    }

    run_task = PROJECT_ROOT / "server_app" / "run_task.py"
    log_path = session_dir / "run.log"
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            [sys.executable, str(run_task), str(mod_dir), api_key],
            cwd=str(PROJECT_ROOT),
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
        )
    print(f"[run_full] started pid={proc.pid} | log={log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
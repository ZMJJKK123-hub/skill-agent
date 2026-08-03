"""MOD 制作器后端 —— FastAPI 服务。

架构（会话隔离 = 每会话一个子进程）：
  POST /api/session    {api_key, game}     → 复制 mod 骨架到独立会话目录
  POST /api/task       {session_id, prompt} → 启动 run_task.py 子进程跑 agent
  GET  /api/status     ?session_id         → 会话状态 / 运行日志尾部
  GET  /api/result     ?session_id         → 最终结果（agent 收尾文本）
  GET  /api/download   ?session_id         → 下载生成好的 mod.zip

用户自己的 API Key 只通过命令行参数传入子进程环境，不落盘、不共享。

运行：python server.py  （或 uvicorn server:app --host 0.0.0.0 --port 8000）
"""

import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 项目根 = 本文件的上上级；会话/模板/前端目录基于项目根 & 本文件同目录组织
# 注意：run_task.py 与 server.py 同目录（server_app/），不要用 PROJECT_ROOT 拼
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_TASK = Path(__file__).resolve().parent / "run_task.py"
sys.path.insert(0, str(PROJECT_ROOT))

# ---------- 目录布局（都在服务器项目根下） ----------
# 会话/模板/前端目录都基于项目根组织（core 在 core/，server_app 只管服务本身）
BASE_DIR = PROJECT_ROOT
SESSIONS_DIR = BASE_DIR / "data" / "sessions"     # 每个用户独立工作区
TEMPLATES_DIR = BASE_DIR / "mod_templates"         # 每个游戏一份骨架
WEB_DIR = Path(__file__).resolve().parent / "web"   # 前端静态文件（server_app/web/）

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


class Session:
    """一个用户的生成会话：独立 mod 工作目录 + 子进程状态。"""

    def __init__(self, session_id: str, mod_dir: Path, api_key: str):
        self.id = session_id
        self.mod_dir = mod_dir
        self.api_key = api_key
        self.proc: Optional[subprocess.Popen] = None
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.result: Optional[str] = None
        self.log_path = mod_dir.parent / "run.log"


# 内存会话表（试水规模够用；坚持到需要持久化时再换数据库）
sessions: dict[str, Session] = {}

app = FastAPI(title="MOD Agent 制作器", version="0.1.0")


# ---------- 模型 ----------
class SessionRequest(BaseModel):
    api_key: str
    game: str = "minecraft"   # 默认 Minecraft


class TaskRequest(BaseModel):
    session_id: str
    prompt: str


# ---------- 会话生命周期 ----------
def _copy_template(game: str, dest: Path) -> Path:
    """把 mod_templates/<game>/ 复制到会话目录，作为 agent 的起点。"""
    src = TEMPLATES_DIR / game
    dest.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    # 模板不存在也不报错：给 agent 一个空目录自由发挥
    return dest


@app.post("/api/session")
def create_session(req: SessionRequest):
    """创建会话：复制游戏骨架 → 生成独立 mod 工作区。"""
    session_id = uuid.uuid4().hex[:12]
    mod_dir = SESSIONS_DIR / session_id / "mod"
    _copy_template(req.game, mod_dir)
    sessions[session_id] = Session(session_id, mod_dir, req.api_key)
    return {"session_id": session_id, "mod_dir": str(mod_dir)}


@app.post("/api/task")
def start_task(req: TaskRequest):
    """为会话启动 agent 子进程（每会话一进程，天然隔离）。"""
    sess = sessions.get(req.session_id)
    if not sess:
        raise HTTPException(404, f"Session {req.session_id} not found")
    if not (sess.api_key and sess.api_key.strip()):
        raise HTTPException(400, "API Key 为空，无法启动任务（用户需填写自己的 DeepSeek API Key）")
    if not req.prompt.strip():
        raise HTTPException(400, "提示词为空，请填写 MOD 需求")
    if sess.proc is not None and sess.proc.poll() is None:
        raise HTTPException(409, "Task already running for this session")

    # 提示词里补充 mod 制作上下文（agent 在哪、产出物要求）
    prompt = (
        f"你是一个 MOD 制作器。请在当前工作目录（{sess.mod_dir}）下"
        f"为游戏生成一个满足以下需求的 MOD。\n"
        f"要求：\n{req.prompt}\n\n"
        f"请直接创建/修改需要的所有文件，完成后汇总你创建了哪些文件。"
    )
    # 启动隔离子进程：cwd 切到该会话的 mod 目录（run_task.py 内部 os.chdir）。
    # 注意：run_task.py 与 server.py 同目录（server_app/），用 RUN_TASK 而非 BASE_DIR
    proc = subprocess.Popen(
        [sys.executable, str(RUN_TASK),
         str(sess.mod_dir), sess.api_key, prompt],
        cwd=str(BASE_DIR),
        stdout=open(sess.log_path, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
    )
    sess.proc = proc
    sess.started_at = time.time()
    sess.finished_at = None
    sess.result = None
    return {"session_id": sess.id, "status": "started"}


@app.get("/api/status")
def get_status(session_id: str):
    """返回会话是否运行中 + 日志尾部（前端轮询展示进度）。"""
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")
    running = sess.proc is not None and sess.proc.poll() is None
    finished = sess.proc is not None and sess.proc.poll() is not None
    log_tail = ""
    if sess.log_path.exists():
        # 只取末尾 2000 字符给前端，避免并发读大文件
        log_tail = sess.log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
        if sess.proc is not None and finished and sess.result is None:
            sess.result = log_tail  # 简单起见：日志尾部即结果（可优化）
            sess.finished_at = time.time()
    return {
        "session_id": session_id,
        "running": running,
        "finished": finished,
        "started_at": sess.started_at,
        "finished_at": sess.finished_at,
        "log_tail": log_tail,
    }


@app.get("/api/result")
def get_result(session_id: str):
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")
    if sess.proc is None or sess.proc.poll() is None:
        return {"status": "running", "result": None}
    return {"status": "finished", "result": sess.result or ""}


@app.get("/api/download")
def download_mod(session_id: str):
    """把会话生成的 mod 目录打包成 zip 供用户下载。"""
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")
    zip_path = SESSIONS_DIR / session_id / "mod.zip"
    shutil.make_archive(str(zip_path)[:-4], "zip", root_dir=str(sess.mod_dir))
    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"mod-{session_id}.zip",
    )


# ---------- 前端静态资源 ----------
WEB_DIR.mkdir(exist_ok=True)


@app.get("/")
def index():
    """根路由显式返回首页，避免任何 mount 歧义导致 404。"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "index.html not found", "web_dir": str(WEB_DIR)}


# 兜底：web 目录里其余静态资源（html 默认返回 index）
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


if __name__ == "__main__":
    import uvicorn

    print("MOD Agent 制作器已启动: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
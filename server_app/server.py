"""MOD 制作器后端 —— FastAPI 服务。

架构（会话隔离 = 每会话一个子进程）：
  POST /api/session    {api_key, game}     → 复制 mod 骨架到独立会话目录
  POST /api/task       {session_id, prompt} → 启动 run_task.py 子进程跑 agent
  GET  /api/session    ?session_id         → 会话状态汇总
  GET  /api/status     ?session_id         → 会话状态 / 运行日志尾部
  GET  /api/result     ?session_id         → 最终结果（agent 收尾文本）
  GET  /api/download   ?session_id         → 下载生成好的 mod.zip
  GET  /api/games                        → 可用游戏模板列表
  GET  /api/events     ?session_id&cursor  → agent 事件流（思考/工具/待办）
  GET  /api/files      ?session_id&path    → 文件树 / 单文件预览
  GET  /api/log        ?session_id&offset  → 原始日志增量拉取

用户自己的 API Key 只通过命令行参数传入子进程环境，不落盘、不共享。

运行：python server.py  （或 uvicorn server:app --host 0.0.0.0 --port 8000）
"""

import os
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

import log_events  # 事件流 / 文件树解析（server_app 同级模块）

# 项目根 = 本文件的上上级；会话/模板/前端目录基于项目根 & 本文件同目录组织
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUN_TASK = Path(__file__).resolve().parent / "run_task.py"
sys.path.insert(0, str(PROJECT_ROOT))

# ---------- 目录布局（都在服务器项目根下） ----------
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
        self.event_cursor = None  # 事件流游标（由 /api/events 维护）


# 会话表：新会话进内存；服务启动时从磁盘恢复历史会话（供下载/预览/事件）
# 注意：恢复的会话 api_key 为空（key 不落盘），只能查看产物，不能重新跑任务
sessions: dict[str, Session] = {}


def _restore_sessions() -> None:
    """启动时扫描 data/sessions/*/，把历史会话重建进内存表。

    这样服务重启后，之前的 mod.zip / 产物树 / 事件日志依然可访问（下载、
    文件预览、事件回放），解决“历史记录点下载提示会话不存在”的问题。
    api_key 不落盘 → 恢复的会话置空，下载/回放不受影响。
    """
    if not SESSIONS_DIR.exists():
        return
    for child in sorted(SESSIONS_DIR.iterdir()):
        if not child.is_dir():
            continue
        mod_dir = child / "mod"
        if not mod_dir.exists():
            continue
        session_id = child.name
        if session_id in sessions:
            continue
        sess = Session(session_id, mod_dir, api_key="")
        sessions[session_id] = sess

        # 有 run.log 说明跑过任务；有 mod.zip 说明已打包完成
        run_log = child / "run.log"
        zip_file = child / "mod.zip"
        if zip_file.exists():
            # 已完成：锁定结束时间（用 zip 文件 mtime，幂等）
            sess.proc = None
            sess.started_at = zip_file.stat().st_mtime - 60  # 粗略估算开始时间(留 60s 余量)
            sess.finished_at = zip_file.stat().st_mtime
            sess.result = "（历史会话，产物已生成）"
        elif run_log.exists() and run_log.stat().st_size > 0:
            # 有日志但未打包：视为历史中已结束（进程已不在）但未打包
            sess.started_at = run_log.stat().st_mtime - 60
            sess.finished_at = run_log.stat().st_mtime
            sess.result = "（历史会话，未生成 zip）"
        # 无日志：纯骨架会话，保持 pending

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


def _get_session(session_id: str) -> Session:
    """按 ID 查会话，不存在抛 404。"""
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(404, f"Session {session_id} not found")
    return sess


def _session_stats(sess: Session) -> dict:
    """汇总会话状态：运行状态 / 耗时 / 产物统计。

    finished 判定：进程已退出（proc 非 None 且 poll 非 None），
    或恢复的历史会话（proc=None 但 finished_at 已锁定，如已打包 zip）。
    否则新建未跑任务的会话（proc=None 且 finished_at=None）保持 pending。
    """
    running = sess.proc is not None and sess.proc.poll() is None
    finished = (sess.proc is not None and sess.proc.poll() is not None) or (
        sess.proc is None and sess.finished_at is not None
    )
    state = "running" if running else ("finished" if finished else "pending")

    # 统计产物文件数量与总大小
    file_count = 0
    total_bytes = 0
    try:
        for p in sess.mod_dir.rglob("*"):
            if p.is_file() and not any(
                part in (".worktrees", ".team", ".tasks", ".transcripts",
                         "__pycache__", ".git")
                for part in p.relative_to(sess.mod_dir).parts
            ):
                file_count += 1
                total_bytes += p.stat().st_size
    except OSError:
        pass

    elapsed = None
    if sess.started_at:
        # 进程已结束但 finished_at 未锁定时，幂等锁定一次。
        # 否则每次轮询都用 time.time()，已完成任务的耗时仍在增长。
        if (sess.finished_at is None
                and sess.proc is not None
                and not running
                and finished):
            sess.finished_at = time.time()
        end = sess.finished_at if sess.finished_at else time.time()
        elapsed = int(end - sess.started_at)

    return {
        "session_id": sess.id,
        "state": state,
        "running": running,
        "finished": finished,
        "started_at": sess.started_at,
        "finished_at": sess.finished_at,
        "elapsed": elapsed,
        "file_count": file_count,
        "total_bytes": total_bytes,
    }


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
    sess = _get_session(req.session_id)
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
    # PYTHONUNBUFFERED=1：强制子进程 stdout 无缓冲，否则 print 会积压到
    # ~8KB 才写盘（前端要等 20 秒才能看到思考过程）。这是实时日志的关键。
    proc = subprocess.Popen(
        [sys.executable, str(RUN_TASK),
         str(sess.mod_dir), sess.api_key, prompt],
        cwd=str(BASE_DIR),
        stdout=open(sess.log_path, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    sess.proc = proc
    sess.started_at = time.time()
    sess.finished_at = None
    sess.result = None
    sess.event_cursor = None
    return {"session_id": sess.id, "status": "started"}


@app.get("/api/session")
def get_session(session_id: str):
    """会话状态汇总：运行状态 / 耗时 / 产物统计。"""
    sess = _get_session(session_id)
    return _session_stats(sess)


@app.get("/api/status")
def get_status(session_id: str):
    """返回会话是否运行中 + 日志尾部（前端轮询展示进度）。"""
    sess = _get_session(session_id)
    running = sess.proc is not None and sess.proc.poll() is None
    finished = sess.proc is not None and sess.proc.poll() is not None
    log_tail = ""
    if sess.log_path.exists():
        # 只取末尾 2000 字符给前端，避免并发读大文件
        log_tail = sess.log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
        if sess.proc is not None and finished and sess.result is None:
            sess.result = log_tail  # 简单起见：日志尾部即结果（可优化）
            sess.finished_at = time.time()
    stats = _session_stats(sess)
    return {
        "session_id": session_id,
        "running": running,
        "finished": finished,
        "started_at": sess.started_at,
        "finished_at": sess.finished_at,
        "log_tail": log_tail,
        **stats,
    }


@app.get("/api/result")
def get_result(session_id: str):
    sess = _get_session(session_id)
    if sess.proc is None or sess.proc.poll() is None:
        return {"status": "running", "result": None}
    return {"status": "finished", "result": sess.result or ""}


@app.get("/api/download")
def download_mod(session_id: str):
    """把会话生成的 mod 目录打包成 zip 供用户下载。"""
    sess = _get_session(session_id)
    zip_path = SESSIONS_DIR / session_id / "mod.zip"
    shutil.make_archive(str(zip_path)[:-4], "zip", root_dir=str(sess.mod_dir))
    return FileResponse(
        str(zip_path),
        media_type="application/zip",
        filename=f"mod-{session_id}.zip",
    )


# ---------- 观察与分析接口（server 层独立，不依赖 core） ----------

@app.get("/api/games")
def list_games():
    """动态枚举 mod_templates/ 下的可用游戏模板。"""
    games = []
    if TEMPLATES_DIR.exists():
        for p in sorted(TEMPLATES_DIR.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                # 读取模板描述（README.md 的首行）
                desc = ""
                readme = p / "README.md"
                if readme.exists():
                    try:
                        first = readme.read_text(encoding="utf-8").strip().splitlines()
                        if first:
                            desc = first[0].lstrip("# ").strip()
                    except OSError:
                        pass
                games.append({"id": p.name, "name": p.name, "description": desc})
    if not games:
        games = [{"id": "minecraft", "name": "minecraft", "description": ""}]
    return {"games": games}


@app.get("/api/events")
def get_events(session_id: str, cursor: str = ""):
    """增量拉取 agent 事件流（思考 / 工具调用 / 待办 / 系统）。

    cursor 参数用 JSON 字符串传回（前台捕获上次返回的 cursor 再传入）。
    """
    sess = _get_session(session_id)
    if not sess.proc or sess.proc.poll() is None:
        # 未启动：允许读历史日志
        pass
    import json as _json
    try:
        cur = _json.loads(cursor) if cursor else None
    except Exception:
        cur = None
    result = log_events.build_event_stream(sess.mod_dir.parent, cur)
    # 记录游标，前台可不传 cursor 就直接续传
    sess.event_cursor = result["cursor"]
    return {
        "session_id": session_id,
        "events": result["events"],
        "cursor": result["cursor"],
    }


@app.get("/api/files")
def get_files(session_id: str, path: str = ""):
    """文件树 / 单文件预览（产物下载前可检视）。"""
    sess = _get_session(session_id)
    if not path:
        tree = log_events.build_file_tree(sess.mod_dir)
        return {"session_id": session_id, "tree": tree}
    preview = log_events.read_file_preview(sess.mod_dir, path)
    if "error" in preview:
        raise HTTPException(400, preview["error"])
    return {"session_id": session_id, "path": path, **preview}


@app.get("/api/log")
def get_log(session_id: str, offset: int = 0):
    """原始日志增量拉取（事件流的兜底方案，展示完整 stdio）。"""
    sess = _get_session(session_id)
    if not sess.log_path.exists():
        return {"content": "", "offset": 0}
    size = sess.log_path.stat().st_size
    with open(sess.log_path, "r", encoding="utf-8", errors="replace") as f:
        if offset > 0:
            f.seek(offset)
        content = f.read()
    return {"content": content, "offset": size}


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

    # 启动时恢复历史会话（供下载/预览/事件回放），服务重启不丢失
    _restore_sessions()
    print(f"MOD Agent 制作器已启动: http://localhost:8000（恢复 {len(sessions)} 个历史会话）")
    uvicorn.run(app, host="0.0.0.0", port=8000)

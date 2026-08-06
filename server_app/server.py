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
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import auth_store  # 用户注册/登录/token/历史（文件存储）
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

    def __init__(self, session_id: str, mod_dir: Path, api_key: str, owner: str = "",
                 game: str = "minecraft", loader: str = "", version: str = ""):
        self.id = session_id
        self.mod_dir = mod_dir
        self.api_key = api_key
        self.owner = owner  # 归属用户名（空 = 未绑定/历史遗留会话，不可访问）
        self.game = game          # 目标游戏（重置时重建骨架用）
        self.loader = loader      # 加载器（如 forge）
        self.version = version    # 版本（如 1.21.1）
        self.proc: Optional[subprocess.Popen] = None
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.result: Optional[str] = None
        self.log_path = mod_dir.parent / "run.log"
        self.event_cursor = None  # 事件流游标（由 /api/events 维护）


# 会话表：新会话进内存；服务启动时从磁盘恢复历史会话（供下载/预览/事件）
# 注意：恢复的会话 api_key 为空（key 不落盘），只能查看产物，不能重新跑任务
sessions: dict[str, Session] = {}

# 下载互斥锁：防止并发请求同时写同一个 mod.zip（zipfile 非原子写，
# 并发写半个文件会让读取方拿到 Content-Length 不匹配 → 浏览器 Failed to fetch）
_download_lock = threading.Lock()


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
        # 恢复的历史会话：owner 从 owner.txt 读（重启后仍归原用户）
        owner_txt = child / "owner.txt"
        owner = owner_txt.read_text(encoding="utf-8").strip() if owner_txt.exists() else ""
        sess = Session(session_id, mod_dir, api_key="", owner=owner)
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
    loader: str = ""          # 可选：Mod Loader（如 forge / fabric）
    version: str = ""         # 可选：游戏版本（如 1.21.1）


class TaskRequest(BaseModel):
    session_id: str
    prompt: str


class AuthRequest(BaseModel):
    username: str
    password: str


class HistoryEntry(BaseModel):
    sessionId: str
    game: str = "minecraft"
    prompt: str = ""
    elapsed: Optional[int] = None
    fileCount: Optional[int] = None
    date: Optional[str] = None


# ---------- 会话生命周期 ----------
def _copy_template(game: str, dest: Path, loader: str = "", version: str = "") -> Path:
    """把对应模板复制到会话目录，作为 agent 的起点。

    优先定位子目录 mod_templates/<game>/<loader>-<version>/；
    子目录不存在或未传 loader/version 时回退到 <game>/ 根目录。
    """
    src = TEMPLATES_DIR / game
    if loader and version:
        sub = TEMPLATES_DIR / game / f"{loader}-{version}"
        if sub.exists():
            src = sub
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


def _purge_session(sess: Session) -> None:
    """彻底清理一个会话：kill 子进程 + 删目录 + 移除内存记录（幂等）。

    供删除会话 / 删除历史 / 批量删除 / 全部删除复用。
    """
    if sess.proc is not None and sess.proc.poll() is None:
        # 强行终止生成子进程
        try:
            sess.proc.kill()
            sess.proc.wait(timeout=5)
        except Exception:
            pass
    sessions.pop(sess.id, None)
    shutil.rmtree(sess.mod_dir.parent, ignore_errors=True)
    auth_store.prune_expired()


def _purge_session_dir(session_id: str) -> None:
    """按 ID 清理会话目录（会话不在内存时用，如历史遗留脏目录）。"""
    sess_dir = SESSIONS_DIR / session_id
    if sess_dir.exists():
        shutil.rmtree(sess_dir, ignore_errors=True)


# 废弃会话清理：用户创建会话但从未开始生成（无 run.log / mod.zip），
# 且超时未再被访问的目录视为垃圾，由后端兜底清除（弥补前端关页/刷新丢失定时器）。
ORPHAN_TTL = 60 * 60  # 1 小时


def _cleanup_orphan_sessions() -> None:
    """启动时与后台定时清理从未生成过的废弃会话目录。

    判定"废弃"：目录下既无 run.log 也无 mod.zip（即从未启动过任务），
    且目录 mtime（镜像创建时间）距今超过 ORPHAN_TTL。
    正在生成 / 已完成的会话不受影响，前端 10 分钟超时也已先删正常会话。
    """
    if not SESSIONS_DIR.exists():
        return
    now = time.time()
    for child in SESSIONS_DIR.iterdir():
        if not child.is_dir():
            continue
        if (child / "run.log").exists() or (child / "mod.zip").exists():
            continue
        try:
            if now - child.stat().st_mtime < ORPHAN_TTL:
                continue
        except OSError:
            continue
        sid = child.name
        sess = sessions.get(sid)
        if sess:
            _purge_session(sess)
        else:
            _purge_session_dir(sid)
        print(f"[cleanup] 清除废弃会话 {sid}")


def _auth_username(authorization: str) -> str:
    """从 Authorization: Bearer <token> 取用户名；无效抛 401。"""
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    username = auth_store.validate_token(token)
    if not username:
        raise HTTPException(401, "登录已失效，请重新登录")
    return username


def _assert_owner(sess: Session, username: str) -> None:
    """校验会话归属；非本人或未绑定会话一律 403，保证用户间隔离。"""
    if not sess.owner or sess.owner != username:
        raise HTTPException(403, "无权访问该会话")


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

    # jar 打包状态：mod/dist/ 下是否存在 jar（agent 收尾构建成功后写入）
    has_jar = False
    try:
        if sess.mod_dir.exists():
            dist_dir = sess.mod_dir / "dist"
            if dist_dir.is_dir():
                has_jar = any(dist_dir.glob("*.jar"))
    except OSError:
        pass

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
        "has_jar": has_jar,
    }


@app.post("/api/session")
def create_session(req: SessionRequest, authorization: str = Header(default="")):
    """创建会话：复制游戏骨架 → 生成独立 mod 工作区，并绑定当前登录用户。"""
    username = _auth_username(authorization)
    session_id = uuid.uuid4().hex[:12]
    mod_dir = SESSIONS_DIR / session_id / "mod"
    _copy_template(req.game, mod_dir, req.loader, req.version)
    # 持久化归属：重启后恢复会话仍能返回原用户（owner.txt）
    try:
        (mod_dir.parent / "owner.txt").write_text(username, encoding="utf-8")
    except OSError:
        pass
    sessions[session_id] = Session(session_id, mod_dir, req.api_key, owner=username,
                                  game=req.game, loader=req.loader, version=req.version)
    return {"session_id": session_id, "mod_dir": str(mod_dir)}


@app.delete("/api/session")
def delete_session(session_id: str, authorization: str = Header(default="")):
    """删除会话：先中断后台子进程，再删除会话目录与记录。

    用于「用户从 MOD 需求页返回 API 配置页」时彻底清理本次会话。
    运行中的任务也会被强制终止（kill），确保能删掉。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    _purge_session(sess)
    return {"ok": True}


@app.post("/api/session/reset")
def reset_session(session_id: str, authorization: str = Header(default="")):
    """重置会话：保留 session_id 与 API Key，清空产物/日志并恢复初始骨架。

    用于「重新生成」——先中断后台子进程（若还在跑），
    再把 mod/ 文件夹重置为最初的骨架占位（如仅 README），
    方便用户在同一个 session 下重新生成。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    # 中断生成中的子进程（若存在）
    if sess.proc is not None and sess.proc.poll() is None:
        try:
            sess.proc.kill()
            sess.proc.wait(timeout=5)
        except Exception:
            pass
    # 重置运行态
    sess.proc = None
    sess.started_at = None
    sess.finished_at = None
    sess.result = None
    sess.event_cursor = None
    # 清空 mod/ 与 run.log，重建初始骨架（保留记录的 game/loader/version）
    shutil.rmtree(sess.mod_dir, ignore_errors=True)
    if sess.log_path.exists():
        try:
            sess.log_path.unlink()
        except OSError:
            pass
    _copy_template(sess.game, sess.mod_dir, sess.loader, sess.version)
    return {"session_id": sess.id, "status": "reset"}


@app.post("/api/task")
def start_task(req: TaskRequest, authorization: str = Header(default="")):
    """为会话启动 agent 子进程（每会话一进程，天然隔离）。"""
    username = _auth_username(authorization)
    sess = _get_session(req.session_id)
    _assert_owner(sess, username)
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
def get_session(session_id: str, authorization: str = Header(default="")):
    """会话状态汇总：运行状态 / 耗时 / 产物统计。"""
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    return _session_stats(sess)


@app.get("/api/status")
def get_status(session_id: str, authorization: str = Header(default="")):
    """返回会话是否运行中 + 日志尾部（前端轮询展示进度）。"""
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    running = sess.proc is not None and sess.proc.poll() is None
    finished = sess.proc is not None and sess.proc.poll() is not None
    log_tail = ""
    if sess.log_path.exists():
        # 尾部预览取末尾 20000 字符（调试需要更完整上下文）
        log_tail = sess.log_path.read_text(encoding="utf-8", errors="replace")[-20000:]
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
def get_result(session_id: str, authorization: str = Header(default="")):
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    if sess.proc is None or sess.proc.poll() is None:
        return {"status": "running", "result": None}
    return {"status": "finished", "result": sess.result or ""}


@app.get("/api/download")
def download_mod(session_id: str, authorization: str = Header(default="")):
    """下载源码 zip：只打包源码工程（源码 + Gradle 配置 + README）。

    排除 build/（Gradle 中间产物）与 dist/（jar 由 /api/download/jar 单独提供），
    保证源码 zip 不含可安装 jar，源码与产物分离。

    用 zipfile 手动遍历打包（make_archive 的 ignore 参数需 Python 3.14+，
    3.13 会抛 TypeError）。zipfile 为标准库，Python 3.10+ 均兼容。
    """
    import zipfile

    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    zip_path = SESSIONS_DIR / session_id / "mod.zip"
    skip = {"build", "dist", ".worktrees", ".team", ".tasks",
            ".transcripts", "__pycache__", ".git"}

    with _download_lock:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if sess.mod_dir.exists():
                for p in sorted(sess.mod_dir.rglob("*")):
                    try:
                        rel = p.relative_to(sess.mod_dir)
                    except ValueError:
                        continue
                    if any(part in skip for part in rel.parts):
                        continue
                    if p.is_file():
                        zf.write(p, rel.as_posix())
        # 一次性读入内存返回：绕开 FileResponse 流式发送在 h11 下的大文件
        # Content-Length bug（uvicorn 默认 h11 对超大响应体会抛
        # "Too little data for declared Content-Length" → 前端 Failed to fetch）
        data = zip_path.read_bytes()
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="mod-{session_id}-src.zip"'},
    )


@app.get("/api/download/jar")
def download_jar(session_id: str, authorization: str = Header(default="")):
    """下载打包好的 mod jar（dist/ 下的 jar）。

    jar 由 agent 收尾调用 build_mod_jar_forge 构建后复制到 mod/dist/。
    多个 jar 时取第一个；没有 jar 返回 400。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    dist_dir = sess.mod_dir / "dist"
    if not dist_dir.is_dir():
        raise HTTPException(400, "该会话尚未打包 jar（未构建或构建失败）")
    jars = sorted(dist_dir.glob("*.jar"))
    if not jars:
        raise HTTPException(400, "该会话尚未打包 jar（未构建或构建失败）")
    data = jars[0].read_bytes()
    return Response(
        content=data,
        media_type="application/java-archive",
        headers={"Content-Disposition": f'attachment; filename="mod-{session_id}.jar"'},
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
def get_events(session_id: str, cursor: str = "", authorization: str = Header(default="")):
    """增量拉取 agent 事件流（思考 / 工具调用 / 待办 / 系统）。

    cursor 参数用 JSON 字符串传回（前台捕获上次返回的 cursor 再传入）。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
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
def get_files(session_id: str, path: str = "", authorization: str = Header(default="")):
    """文件树 / 单文件预览（产物下载前可检视）。"""
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    if not path:
        tree = log_events.build_file_tree(sess.mod_dir)
        return {"session_id": session_id, "tree": tree}
    preview = log_events.read_file_preview(sess.mod_dir, path)
    if "error" in preview:
        raise HTTPException(400, preview["error"])
    return {"session_id": session_id, "path": path, **preview}


@app.get("/api/log")
def get_log(session_id: str, offset: int = 0, authorization: str = Header(default="")):
    """原始日志增量拉取（事件流的兜底方案，展示完整 stdio）。"""
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    if not sess.log_path.exists():
        return {"content": "", "offset": 0}
    size = sess.log_path.stat().st_size
    with open(sess.log_path, "r", encoding="utf-8", errors="replace") as f:
        if offset > 0:
            f.seek(offset)
        content = f.read()
    return {"content": content, "offset": size}


# ---------- 认证与用户历史 ----------

@app.post("/api/register")
def register_user(req: AuthRequest):
    """注册新用户，成功后直接返回登录 token（免二次登录）。"""
    try:
        auth_store.register(req.username, req.password)
    except ValueError as e:
        raise HTTPException(400, str(e))
    token = auth_store.create_token(req.username.strip())
    return {"username": req.username.strip(), "token": token}


@app.post("/api/login")
def login_user(req: AuthRequest):
    """登录：校验密码，返回 token。"""
    user = auth_store.check_credentials(req.username, req.password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    token = auth_store.create_token(user["username"])
    return {"username": user["username"], "token": token}


@app.get("/api/me")
def me(authorization: str = Header(default="")):
    """校验 token 有效性，返回当前用户（前端启动时免登检查用）。"""
    username = _auth_username(authorization)
    return {"username": username}


@app.post("/api/logout")
def logout(authorization: str = Header(default="")):
    """注销：吊销 token。"""
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    auth_store.revoke_token(token)
    return {"ok": True}


def _history_with_jar(username: str) -> list:
    """给历史条目注入 has_jar（磁盘检测 dist/*.jar 是否存在）。"""
    history = auth_store.load_history(username)
    for h in history:
        sid = h.get("sessionId")
        h["has_jar"] = False
        if sid:
            dist_dir = SESSIONS_DIR / sid / "mod" / "dist"
            if dist_dir.is_dir():
                try:
                    h["has_jar"] = any(dist_dir.glob("*.jar"))
                except OSError:
                    h["has_jar"] = False
    return history


@app.get("/api/history")
def get_history(authorization: str = Header(default="")):
    """当前登录用户的历史记录（按用户隔离，含 has_jar 打包状态）。"""
    username = _auth_username(authorization)
    return {"history": _history_with_jar(username)}


@app.put("/api/history")
def put_history(entry: HistoryEntry, authorization: str = Header(default="")):
    """按 session_id 去重合并一条历史记录。"""
    username = _auth_username(authorization)
    history = auth_store.upsert_history(username, entry.model_dump())
    return {"history": history}


class HistoryBatchDelete(BaseModel):
    session_ids: list[str]


@app.delete("/api/history")
def delete_history(session_id: str = "", authorization: str = Header(default="")):
    """删除历史记录（单条指定 session_id；不传则清空全部）。

    同步删除 data/sessions/{session_id}/ 目录（含 kill 运行中的子进程），
    确保历史删除后产物文件不再残留磁盘。全部删除 = 遍历该用户历史逐条清理。
    """
    username = _auth_username(authorization)
    if session_id:
        # 单条删除：清历史 + 清会话目录（校验归属后彻底清理）
        auth_store.remove_history(username, session_id)
        sess = sessions.get(session_id)
        if sess and sess.owner == username:
            _purge_session(sess)
        else:
            _purge_session_dir(session_id)
        return {"history": _history_with_jar(username)}

    # 全部删除：先删除每个历史会话的磁盘目录，再清历史表
    for h in auth_store.load_history(username):
        sid = h.get("sessionId")
        if not sid:
            continue
        sess = sessions.get(sid)
        if sess and sess.owner == username:
            _purge_session(sess)
        else:
            _purge_session_dir(sid)
    auth_store.clear_history(username)
    return {"history": []}


@app.delete("/api/history/batch")
def delete_history_batch(req: HistoryBatchDelete, authorization: str = Header(default="")):
    """批量删除历史：每个 session_id 清历史 + 同步清会话目录。"""
    username = _auth_username(authorization)
    for sid in req.session_ids:
        auth_store.remove_history(username, sid)
        sess = sessions.get(sid)
        if sess and sess.owner == username:
            _purge_session(sess)
        else:
            _purge_session_dir(sid)
    return {"history": _history_with_jar(username)}


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
    _cleanup_orphan_sessions()

    # 后台守护线程：每 30 分钟清理一次废弃会话（前端关页/刷新丢失定时器时兜底）
    def _orphan_cleanup_loop():
        while True:
            time.sleep(30 * 60)
            try:
                _cleanup_orphan_sessions()
            except Exception:
                pass

    threading.Thread(target=_orphan_cleanup_loop, daemon=True).start()

    print(f"MOD Agent 制作器已启动: http://localhost:8000（恢复 {len(sessions)} 个历史会话）")
    try:
        # httptools：C 语言 HTTP 解析器，根治 h11 在超大响应体上的 Content-Length bug
        uvicorn.run(app, host="0.0.0.0", port=8000, http="httptools")
    except Exception:
        # 未安装 httptools 时回退默认 h11（内存读方案已绕开大文件流式问题）
        uvicorn.run(app, host="0.0.0.0", port=8000)

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
import re
import json
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request, Response
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
                 game: str = "minecraft", loader: str = "", version: str = "",
                 model: str = "DeepSeek-V4-Flash-0731", base_url: str = "https://llmapi.paratera.com",
                 sandbox: str = "full-access",
                 vision_enabled: bool = False, vision_api_key: str = "",
                 vision_base_url: str = "", vision_model: str = "",
                 auto_mode: bool = False, search_api_key: str = ""):
        self.id = session_id
        self.mod_dir = mod_dir
        self.api_key = api_key
        self.owner = owner  # 归属用户名（空 = 未绑定/历史遗留会话，不可访问）
        self.game = game          # 目标游戏（重置时重建骨架用）
        self.loader = loader      # 加载器（如 forge）
        self.version = version    # 版本（如 1.21.1）
        self.model = model        # 生成用的模型名（如 DeepSeek-V4-Flash-0731 / 自定义 provider 的模型）
        self.base_url = base_url  # 生成用的 API base_url（OpenAI 兼容）
        self.sandbox = sandbox    # 会话沙箱模式：full-access | workspace-write | read-only
        self.vision_enabled = vision_enabled    # 识图模式：True 时注册 screenshot/analyze_image 工具
        self.vision_api_key = vision_api_key    # 视觉 API Key（独立于主模型，不落盘）
        self.vision_base_url = vision_base_url  # 视觉 API Base URL（OpenAI 兼容）
        self.vision_model = vision_model        # 视觉模型名（如 gpt-4o / qwen-vl-plus / glm-4v）
        self.auto_mode = auto_mode              # 全自动模式：True 时 ask_user_question 不阻塞等待用户
        self.search_api_key = search_api_key    # 联网搜索 API Key（Tavily 等）
        self.proc: Optional[subprocess.Popen] = None
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.result: Optional[str] = None
        self.log_path = mod_dir.parent / "run.log"
        self.event_cursor = None  # 事件流游标（由 /api/events 维护）
        self.daemon_prev_state: Optional[str] = None  # daemon 状态机记忆（waiting/working/None）


# 会话表：新会话进内存；服务启动时从磁盘恢复历史会话（供下载/预览/事件）
# 注意：恢复的会话 api_key 为空（key 不落盘），只能查看产物，不能重新跑任务
sessions: dict[str, Session] = {}

# 下载互斥锁：防止并发请求同时写同一个 mod.zip（zipfile 非原子写，
# 并发写半个文件会让读取方拿到 Content-Length 不匹配 → 浏览器 Failed to fetch）
_download_lock = threading.Lock()


def _kill_stale_daemon(session_dir: Path) -> None:
    """杀掉上一轮 server 进程遗留的 chat daemon（读 .chat/daemon.pid）。

    server 重启后旧 daemon 进程仍存活（孤儿），若不清理，用户发新消息时
    会与新建进程同时消费同一 pending 队列 → 双进程跑同一会话（竞态污染）。
    按 pid 文件 kill，失败（进程已死/pid 被复用）则忽略。
    """
    pid_file = session_dir / ".chat" / "daemon.pid"
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return
    try:
        # Windows 上 os.kill(pid, signal.SIGTERM) 即强制终止；
        # 仅终止自己之前启动的子进程（pid 复用概率极低，接受）
        os.kill(pid, 15)  # SIGTERM
    except OSError:
        pass
    try:
        pid_file.unlink(missing_ok=True)
    except OSError:
        pass


def _restore_sessions() -> None:
    """启动时扫描 data/sessions/*/，把历史会话重建进内存表。

    这样服务重启后，之前的 mod.zip / 产物树 / 事件日志依然可访问（下载、
    文件预览、事件回放），解决“历史记录点下载提示会话不存在”的问题。
    api_key 不落盘 → 恢复的会话置空，下载/回放不受影响。

    兼容普通会话（纯聊天，无 mod/ 子目录）：不再要求 mod 目录存在。
    """
    if not SESSIONS_DIR.exists():
        return
    for child in sorted(SESSIONS_DIR.iterdir()):
        if not child.is_dir():
            continue
        session_id = child.name
        if session_id in sessions:
            continue
        # 重启时清理遗留 daemon（防双进程抢队列）
        _kill_stale_daemon(child)
        mod_dir = child / "mod"
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
        # 无日志：纯骨架/纯聊天会话，保持 pending

app = FastAPI(title="MOD Agent 制作器", version="0.1.0")


# ---------- 模型 ----------
class SessionRequest(BaseModel):
    api_key: str
    game: str = "minecraft"   # 默认 Minecraft
    loader: str = ""          # 可选：Mod Loader（如 forge / fabric）
    version: str = ""         # 可选：游戏版本（如 1.21.1）
    model: str = "DeepSeek-V4-Flash-0731"          # 生成模型
    base_url: str = "https://llmapi.paratera.com"  # OpenAI 兼容 API 地址
    sandbox: str = "full-access"              # 沙箱模式：full-access | workspace-write | read-only
    vision_enabled: bool = False              # 识图模式开关
    vision_api_key: str = ""                  # 视觉 API Key（独立于主模型）
    vision_base_url: str = ""                 # 视觉 API Base URL
    vision_model: str = ""                    # 视觉模型名
    auto_mode: bool = False                   # 全自动模式：不阻塞 ask_user_question
    search_api_key: str = ""                  # 联网搜索 API Key（Tavily 等）


class TaskRequest(BaseModel):
    session_id: str
    prompt: str
    mode: str = "chat"   # chat（通用对话，默认）| mod（MOD 制作）
    resume: bool = False  # True=从断点恢复继续（暂停后点继续按钮）
    model: str = ""       # 可选：覆盖会话模型（前端切换 flash/pro 后立即生效）
    base_url: str = ""    # 可选：覆盖会话 base_url（自定义 provider）
    vision_enabled: Optional[bool] = None  # 可选：覆盖会话识图模式开关
    vision_api_key: Optional[str] = None   # 可选：覆盖会话视觉 API Key
    vision_base_url: Optional[str] = None  # 可选：覆盖会话视觉 API Base URL
    vision_model: Optional[str] = None     # 可选：覆盖会话视觉模型名
    auto_mode: Optional[bool] = None       # 可选：覆盖会话全自动模式开关
    search_api_key: Optional[str] = None   # 可选：覆盖会话搜索 API Key


class AuthRequest(BaseModel):
    username: str
    password: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str = ""   # 单题回答（legacy）
    answers: Optional[list] = None  # 多题回答：[{"question": "...", "answer": "..."}, ...]


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
    src_is_sub = False
    if loader and version:
        sub = TEMPLATES_DIR / game / f"{loader}-{version}"
        if sub.exists():
            src = sub
            src_is_sub = True
    dest.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copytree(src, dest, dirs_exist_ok=True)

    # KNOWN_ISSUES.md：各版本独立。
    # - 若实际使用的是 <loader>-<version>/ 子目录：该子目录自带的 KNOWN_ISSUES.md
    #   已随 copytree 复制进会话（优先保留，不覆盖）——各版本各自积累经验。
    # - 若回退到 <game>/ 根目录（未传 loader/version，或子目录不存在）：才无条件
    #   复制根级 KNOWN_ISSUES.md（作为默认占位；收尾阶段 finalize_known_issues()
    #   更新模板里的这份文件）。
    if not src_is_sub:
        issues_src = TEMPLATES_DIR / game / "KNOWN_ISSUES.md"
        if issues_src.exists():
            shutil.copy2(issues_src, dest / "KNOWN_ISSUES.md")

    # 不再复制 mc_java_sources 和 docs/agent（每会话几百 MB 太重）。
    # 改为创建 symlink 指向仓库根目录，零存储成本；
    # safe_path 已放行这两个只读参考路径。
    if version.startswith("26.2"):
        mc_sources = PROJECT_ROOT / "mc_java_sources_26.2"
    else:
        mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
    mc_link = dest / "mc_java_sources"
    if mc_sources.is_dir() and not mc_link.exists():
        try:
            if os.name == "nt":
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(mc_link), str(mc_sources)],
                    check=True, capture_output=True,
                )
            else:
                mc_link.symlink_to(mc_sources, target_is_directory=True)
            print(f"[server] linked mc_java_sources -> {mc_sources}")
        except Exception as e:
            print(f"[server] link mc_java_sources 失败: {e}")

    docs_link = dest / "docs" / "agent"
    docs_src = PROJECT_ROOT / "docs" / "agent"
    if docs_src.is_dir() and not docs_link.exists():
        try:
            docs_link.parent.mkdir(parents=True, exist_ok=True)
            if os.name == "nt":
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(docs_link), str(docs_src)],
                    check=True, capture_output=True,
                )
            else:
                docs_link.symlink_to(docs_src, target_is_directory=True)
            print(f"[server] linked docs/agent -> {docs_src}")
        except Exception as e:
            print(f"[server] link docs/agent 失败: {e}")

    # 模板不存在也不报错：给 agent 一个一个空目录自由发挥
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


def _is_safe_session_id(session_id: str) -> bool:
    """校验 session_id 是否可作为目录名，防止路径穿越/目录删除。"""
    if not isinstance(session_id, str) or not session_id:
        return False
    if session_id in (".", ".."):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", session_id))


def _purge_session_dir(session_id: str) -> None:
    """按 ID 清理会话目录（会话不在内存时用，如历史遗留脏目录）。"""
    if not _is_safe_session_id(session_id):
        return
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


def _daemon_state(sess: Session) -> Optional[str]:
    """读取 chat 常驻 daemon 的状态文件：waiting | working | None。

    daemon 进程在 .chat/daemon.state 写入当前状态：
      - waiting：空闲等待新消息（上一轮已完成）→ 会话应显示"完成"
      - working：正在跑一轮 → 会话应显示"运行中"
    - None：非 daemon（进程未存活 / mod 模式 / 状态文件不存在）。

    仅在进程存活时才有意义；进程退出后由 poll() 判定 finished。
    """
    if sess.proc is None or sess.proc.poll() is not None:
        return None
    state_file = sess.mod_dir.parent / ".chat" / "daemon.state"
    try:
        val = state_file.read_text(encoding="utf-8").strip()
        return val if val in ("waiting", "working") else None
    except OSError:
        return None


def _session_stats(sess: Session) -> dict:
    """汇总会话状态：运行状态 / 耗时 / 产物统计。

    finished 判定：进程已退出（proc 非 None 且 poll 非 None），
    或恢复的历史会话（proc=None 但 finished_at 已锁定，如已打包 zip），
    或 daemon 空闲等待（进程存活但 daemon.state == waiting）。
    否则新建未跑任务的会话（proc=None 且 finished_at=None）保持 pending。

    daemon 状态机（chat 常驻）：
      - waiting：上一轮完成、进程待命 → finished=True、running=False；
        前端显示"完成"；elapsed 锁定到上一轮结束时刻。
      - working：正在跑新一轮 → running=True、finished=False；
        elapsed 从上一轮结束时刻重新起算。
    """
    daemon_st = _daemon_state(sess)
    proc_alive = sess.proc is not None and sess.proc.poll() is None
    daemon_idle = daemon_st == "waiting" and proc_alive
    daemon_working = daemon_st == "working" and proc_alive

    # daemon 空闲但队列里有消息（用户刚发、daemon 尚未消费）：
    # 不能算 finished——否则前端会在 finished+pending>0 时把上一轮的
    # log_tail 误提取为本次回复（实测：发新消息秒回旧回复后停住）。
    if daemon_idle:
        try:
            from core.conversation import pending_count
            if pending_count(sess.mod_dir.parent) > 0:
                daemon_idle = False
        except Exception:
            pass

    running = proc_alive and not daemon_idle
    finished = (sess.proc is not None and not proc_alive) or (
        sess.proc is None and sess.finished_at is not None
    ) or daemon_idle
    state = "running" if running else ("finished" if finished else "pending")

    # daemon 状态机：working（新轮开始）时清掉上一轮锁定的 finished_at，
    # 让 elapsed 从新一轮开始计时；回到 waiting 时锁定一次。
    if daemon_working and sess.daemon_prev_state == "waiting":
        sess.finished_at = None
        sess.started_at = time.time()  # 新轮开始：elapsed 重新起算
    sess.daemon_prev_state = daemon_st
    if daemon_idle and sess.finished_at is None:
        sess.finished_at = time.time()  # 幂等：锁定到本轮结束时刻

    # 统计产物文件数量与总大小
    file_count = 0
    total_bytes = 0
    try:
        _skip_dirs = {".worktrees", ".team", ".tasks", ".transcripts",
                      "__pycache__", ".git", "mc_java_sources"}
        for _root, _dirs, _files in os.walk(sess.mod_dir):
            _dirs[:] = [d for d in _dirs if d not in _skip_dirs]
            for _fn in _files:
                file_count += 1
                total_bytes += (Path(_root) / _fn).stat().st_size
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
    """创建会话：轻量创建（不复制模板/源码），仅建目录并绑定当前登录用户。

    mod 模板与 MC 源码在用户输入 /mod 触发时由 POST /api/session/mod 复制。
    """
    username = _auth_username(authorization)
    session_id = uuid.uuid4().hex[:12]
    mod_dir = SESSIONS_DIR / session_id / "mod"
    mod_dir.mkdir(parents=True, exist_ok=True)
    # 持久化归属：重启后恢复会话仍能返回原用户（owner.txt）
    try:
        (mod_dir.parent / "owner.txt").write_text(username, encoding="utf-8")
    except OSError:
        pass
    sessions[session_id] = Session(session_id, mod_dir, req.api_key, owner=username,
                                  game=req.game, loader=req.loader, version=req.version,
                                  model=req.model, base_url=req.base_url, sandbox=req.sandbox,
                                  vision_enabled=req.vision_enabled,
                                  vision_api_key=req.vision_api_key,
                                  vision_base_url=req.vision_base_url,
                                  vision_model=req.vision_model,
                                  auto_mode=req.auto_mode,
                                  search_api_key=req.search_api_key)
    return {"session_id": session_id, "mod_dir": str(mod_dir)}


@app.post("/api/session/mod")
def prepare_mod_session(
    session_id: str,
    authorization: str = Header(default=""),
    api_key: str = Header(default="", alias="X-API-Key"),
    game: str = "minecraft",
    loader: str = "forge",
    version: str = "1.21.11",
    model: str = "DeepSeek-V4-Flash-0731",
    base_url: str = "https://llmapi.paratera.com",
    sandbox: str = "full-access",
):
    """为会话准备 mod 工作区：把模板 + MC 源码复制到 <session>/mod/（幂等）。

    由前端在用户输入 /mod 并确认后调用；复制过（mod/ 有内容）则跳过。
    api_key/game/loader/version 走 query/header，与会话已存参数一致。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)

    # 幂等：mod/ 已存在模板内容则跳过（防止重复 /mod 重复复制）
    already = False
    try:
        if sess.mod_dir.exists() and any(sess.mod_dir.iterdir()):
            already = True
    except OSError:
        pass
    if not already:
        _copy_template(sess.game, sess.mod_dir, sess.loader, sess.version)
    return {"session_id": sess.id, "mod_ready": True, "already": already}


# ============================================================================
# 【导入文件夹功能 - 已临时禁用】
# 说明：导入后 bug 较多，暂时注释停用；代码保留，后续扩展时恢复。
# 恢复方法：取消本段注释即可（前端 workspace.tsx 同步恢复）。
# ============================================================================
# @app.post("/api/import")
# async def import_session(
#     request: Request,
#     authorization: str = Header(default=""),
#     api_key: str = Header(default="", alias="X-API-Key"),
#     game: str = "minecraft",
#     loader: str = "forge",
#     version: str = "1.21.11",
#     model: str = "DeepSeek-V4-Flash-0731",
#     base_url: str = "https://llmapi.paratera.com",
#     sandbox: str = "full-access",
# ):
#     """导入已有 mod 文件夹：前端选目录打成 zip 上传，解压成新会话工作区。
#
#     请求体 = 原始 zip 字节（Content-Type: application/zip）；
#     api_key 走 X-API-Key 头，game/loader/version/model/base_url 走 query 参数。
#     不依赖 python-multipart，后端零新增依赖。
#     """
#     import io
#     import zipfile
#
#     username = _auth_username(authorization)
#     session_id = uuid.uuid4().hex[:12]
#     mod_dir = SESSIONS_DIR / session_id / "mod"
#     mod_dir.mkdir(parents=True, exist_ok=True)
#
#     data = await request.body()
#     if not data:
#         raise HTTPException(400, "上传文件为空")
#     try:
#         with zipfile.ZipFile(io.BytesIO(data)) as zf:
#             for member in zf.infolist():
#                 # 防 zip-slip：拒绝绝对路径与越界（..）路径
#                 member_path = Path(member.filename)
#                 if member_path.is_absolute() or ".." in member_path.parts:
#                     raise HTTPException(400, f"zip 内含非法路径: {member.filename}")
#                 target = (mod_dir / member_path).resolve()
#                 if not target.is_relative_to(mod_dir.resolve()):
#                     raise HTTPException(400, f"zip 内含非法路径: {member.filename}")
#                 if member.is_dir():
#                     target.mkdir(parents=True, exist_ok=True)
#                 else:
#                     target.parent.mkdir(parents=True, exist_ok=True)
#                     with zf.open(member) as src, open(target, "wb") as dst:
#                         shutil.copyfileobj(src, dst)
#     except zipfile.BadZipFile:
#         raise HTTPException(400, "无效的 zip 文件")
#
#     # 供 agent 查阅 MC+Forge 源码（与 _copy_template 一致）
#     # 按会话版本选择对应的 MC+Forge 源码树（会话内目录名保持 mc_java_sources 不变）
#     if version.startswith("26.2"):
#         mc_sources = PROJECT_ROOT / "mc_java_sources_26.2"
#     else:
#         mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
#     if mc_sources.is_dir():
#         try:
#             shutil.copytree(mc_sources, mod_dir / "mc_java_sources", dirs_exist_ok=True)
#         except OSError as e:
#             print(f"[server] 复制 mc_java_sources 失败: {e}")
#
#     try:
#         (mod_dir.parent / "owner.txt").write_text(username, encoding="utf-8")
#     except OSError:
#         pass
#     sessions[session_id] = Session(session_id, mod_dir, api_key, owner=username,
#                                   game=game, loader=loader, version=version,
#                                   model=model, base_url=base_url, sandbox=sandbox)
#     return {"session_id": session_id, "mod_dir": str(mod_dir)}
# ============================================================================


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
    """为会话启动 agent 子进程（每会话一进程，天然隔离）。

    mode=chat：cwd=会话根目录，通用对话（不要求 mod 模板）；
    mode=mod：cwd=<session>/mod/，MOD 制作（要求 mod 模板已复制）。

    运行中重入（sess.proc 活着）：
      - resume=True：忽略（调用方应先 pause 再 resume）
      - resume=False：不抛 409，而是把消息排入 pending 队列，
        当前轮跑完后由前端自动续跑处理（运行中插话支持）。
    """
    username = _auth_username(authorization)
    sess = _get_session(req.session_id)
    _assert_owner(sess, username)
    if not (sess.api_key and sess.api_key.strip()):
        raise HTTPException(400, "API Key 为空，无法启动任务（用户需填写自己的 DeepSeek API Key）")
    if not req.prompt.strip() and not req.resume:
        raise HTTPException(400, "提示词为空，请填写内容")

    mode = req.mode if req.mode in ("chat", "mod") else "chat"
    # mod 模式要求 mod/ 已复制模板（/api/session/mod 调用过）
    if mode == "mod" and not (sess.mod_dir.exists() and any(sess.mod_dir.iterdir())):
        raise HTTPException(400, "MOD 工作区尚未准备：请先通过 /mod 触发模板复制")

    # ── 运行中重入：排队（不 409）──
    if sess.proc is not None and sess.proc.poll() is None:
        daemon_st = _daemon_state(sess)
        if req.resume and daemon_st != "waiting":
            # resume 仅两种合法场景：
            #   1) 进程已死（走下面恢复分支）
            #   2) daemon 空闲等待（chat 常驻）——前端"自动续跑"（finished+pending>0）
            #      会以 resume=True 重入；daemon 自己能消费 pending，直接确认即可。
            # 其他进程存活时的 resume（如运行中）维持原 409 防御。
            raise HTTPException(409, "Task already running；请先暂停再继续")
        try:
            if req.prompt.strip():
                from core.conversation import enqueue_pending
                enqueue_pending(sess.mod_dir.parent, req.prompt)
        except Exception:
            raise HTTPException(500, "排队消息写入失败")
        return {"session_id": sess.id, "status": "queued", "mode": mode}

    # ── 恢复模式：从断点继续（暂停后点继续按钮）──
    if req.resume:
        # 带 prompt 的恢复 = 暂停后强注入新消息：先写入 pending（同时落历史），
        # 恢复的 run_task 从断点加载后，agent 第一轮会 drain 到该消息作为 user 注入。
        if req.prompt.strip():
            try:
                from core.conversation import enqueue_pending
                enqueue_pending(sess.mod_dir.parent, req.prompt)
            except Exception:
                raise HTTPException(500, "排队消息写入失败")
        # 校验断点存在（没有断点则回退普通启动，由 run_task 决定）
        pass

    # 工作目录：chat 模式 = 会话根目录；mod 模式 = mod/ 子目录
    work_dir = sess.mod_dir if mode == "mod" else sess.mod_dir.parent

    # 提示词里补充上下文（agent 在哪、产出物要求）——仅 mod 模式加 mod 制作上下文
    if mode == "mod" and not req.resume:
        prompt = (
            f"你是一个 MOD 制作器。请在当前工作目录（{sess.mod_dir}）下"
            f"为游戏生成一个满足以下需求的 MOD。\n"
            f"要求：\n{req.prompt}\n\n"
            f"请直接创建/修改需要的所有文件，完成后汇总你创建了哪些文件。"
        )
    else:
        prompt = req.prompt

    # prompt 写入 UTF-8 临时文件（绕开 Windows 子进程 argv 的 GBK 编码损坏中文）
    prompt_file = None
    env_extra = {}
    if prompt:
        import tempfile as _tempfile
        try:
            fd, prompt_file = _tempfile.mkstemp(suffix=".prompt.txt", prefix="dsh_")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(prompt)
            env_extra["DSH_PROMPT_FILE"] = prompt_file
        except OSError as e:
            raise HTTPException(500, f"提示词临时文件写入失败: {e}")

    # 模型/地址：请求里带了就用最新的（前端切换 flash/pro 或自定义 provider
    # 后立即生效），否则用会话创建时存储的值；同时回写会话，保持后续一致。
    if req.model:
        sess.model = req.model
    if req.base_url:
        sess.base_url = req.base_url
    if req.vision_enabled is not None:
        sess.vision_enabled = req.vision_enabled
    if req.vision_api_key is not None:
        sess.vision_api_key = req.vision_api_key
    if req.vision_base_url is not None:
        sess.vision_base_url = req.vision_base_url
    if req.vision_model is not None:
        sess.vision_model = req.vision_model
    if req.auto_mode is not None:
        sess.auto_mode = req.auto_mode
    if req.search_api_key is not None:
        sess.search_api_key = req.search_api_key

    # 启动隔离子进程：cwd 切到工作目录（run_task.py 内部 os.chdir）。
    # PYTHONUNBUFFERED=1：强制子进程 stdout 无缓冲，否则 print 会积压到
    # ~8KB 才写盘（前端要等 20 秒才能看到思考过程）。这是实时日志的关键。
    try:
        proc = subprocess.Popen(
            [sys.executable, str(RUN_TASK),
             str(work_dir), sess.api_key],
            cwd=str(BASE_DIR),
            stdout=open(sess.log_path, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1",
                 "DSH_MODEL": sess.model, "DSH_BASE_URL": sess.base_url,
                 "DSH_SANDBOX_MODE": sess.sandbox,
                 "DSH_MODE": mode,
                 "DSH_SESSION_ROOT": str(sess.mod_dir.parent),
                 "DSH_RESUME": "1" if req.resume else "0",
                 "DSH_VISION_ENABLED": "1" if sess.vision_enabled else "0",
                 "DSH_VISION_API_KEY": sess.vision_api_key or "",
                 "DSH_VISION_BASE_URL": sess.vision_base_url or "",
                 "DSH_VISION_MODEL": sess.vision_model or "",
                 "DSH_AUTO_MODE": "1" if sess.auto_mode else "0",
                 "DSH_TAVILY_API_KEY": sess.search_api_key or "",
                 **env_extra},
        )
    except Exception:
        if prompt_file:
            try:
                os.unlink(prompt_file)
            except OSError:
                pass
        raise
    sess.proc = proc
    sess.started_at = time.time()
    sess.finished_at = None
    sess.result = None
    sess.event_cursor = None
    # 注意：prompt 临时文件由 run_task.py 读取后自行删除。
    # 这里绝不能提前 unlink——Windows 上子进程启动有延迟，
    # 立即删除会导致 run_task 读取失败（实测：agent 直接退出，
    # 前端表现为"进行中"闪现后消失、输入无反应）。
    return {"session_id": sess.id, "status": "started", "mode": mode, "resume": req.resume}


@app.post("/api/task/pause")
def pause_task(session_id: str, authorization: str = Header(default="")):
    """暂停当前运行的 agent（类似 sleep，不是杀掉整个 agent）。

    子进程被 kill，但断点已由 agent 每轮写入 .chat/working.jsonl；
    用户点"继续"时 start_task(resume=True) 从断点原样恢复继续跑。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    if sess.proc is None or sess.proc.poll() is not None:
        return {"session_id": session_id, "status": "not-running"}
    try:
        sess.proc.kill()
        sess.proc.wait(timeout=5)
    except Exception:
        pass
    sess.proc = None
    # 清理 daemon 状态文件（daemon 被强杀，finally 不执行）
    try:
        (sess.mod_dir.parent / ".chat" / "daemon.pid").unlink(missing_ok=True)
        (sess.mod_dir.parent / ".chat" / "daemon.state").unlink(missing_ok=True)
    except OSError:
        pass
    # finished_at 保持 None：暂停 ≠ 完成，前端据此显示"已终止/继续"状态
    return {"session_id": session_id, "status": "paused"}


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
    stats = _session_stats(sess)
    running = stats["running"]
    finished = stats["finished"]
    log_tail = ""
    if sess.log_path.exists():
        # 尾部预览取末尾 20000 字符（只读尾部，避免全量读大日志）
        log_size = sess.log_path.stat().st_size
        with open(sess.log_path, "r", encoding="utf-8", errors="replace") as _f:
            if log_size > 20000:
                _f.seek(log_size - 20000)
            log_tail = _f.read()
        if finished and sess.result is None:
            sess.result = log_tail  # 简单起见：日志尾部即结果（可优化）
            sess.finished_at = time.time()
    # 暂停状态：进程被 pause 杀掉但断点仍在 → 前端显示"已终止，可继续"
    paused = sess.proc is None and (sess.mod_dir.parent / ".chat" / "working.jsonl").exists()
    # 排队消息数：运行中用户插入、待当前轮跑完后自动续跑处理
    pending = 0
    try:
        from core.conversation import pending_count
        pending = pending_count(sess.mod_dir.parent)
    except Exception:
        pass
    return {
        "session_id": session_id,
        "running": running,
        "finished": finished,
        "paused": paused,
        "pending": pending,
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
    stats = _session_stats(sess)
    if not stats["finished"]:
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
            ".transcripts", "__pycache__", ".git", "mc_java_sources"}

    with _download_lock:
        # 缓存逻辑：若已存在 mod.zip 且比所有源码文件都新，则直接复用，
        # 避免每次点击都重新打包 11MB → 前端长时间无反馈 + 重复点击堆积。
        need_build = True
        if zip_path.exists() and sess.mod_dir.exists():
            zip_mtime = zip_path.stat().st_mtime
            newest_src = max(
                (p.stat().st_mtime
                 for p in sess.mod_dir.rglob("*")
                 if p.is_file() and "mc_java_sources" not in p.parts),
                default=0,
            )
            if zip_mtime >= newest_src:
                need_build = False
        if need_build:
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


@app.get("/api/conversation")
def get_conversation(session_id: str, authorization: str = Header(default="")):
    """返回会话的对话历史（多轮聊天的 user/assistant 消息对）+ 模式推断。

    历史存于 <session_root>/.chat/conversation.jsonl，由 core/conversation.py
    维护（chat 模式每一轮追加 user + assistant）。
    mode 推断：mod/ 已复制模板 → 'mod'；有 .chat 历史 → 'chat'；否则 None。
    前端打开历史会话时据此恢复正确的展示模式。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    history_path = sess.mod_dir.parent / ".chat" / "conversation.jsonl"
    messages = []
    if history_path.exists():
        import json as _json
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = _json.loads(line)
                    except _json.JSONDecodeError:
                        continue
                    if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
                        messages.append(msg)
        except OSError:
            pass
    # 模式推断：mod 模板已复制 → mod；有对话历史 → chat
    mode = None
    try:
        if sess.mod_dir.exists() and any(sess.mod_dir.iterdir()):
            mode = "mod"
    except OSError:
        pass
    if mode is None and messages:
        mode = "chat"
    return {"session_id": session_id, "messages": messages, "mode": mode}


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


@app.get("/api/sessions")
def list_sessions(authorization: str = Header(default="")):
    """按 owner 派生当前用户的会话列表（扫描 data/sessions/*/owner.txt）。

    不再依赖单独的 history 存储：会话目录 + owner.txt 是唯一事实来源，
    历史与会话双向一致（删除会话即从列表消失）。
    """
    import datetime

    username = _auth_username(authorization)
    out = []
    if SESSIONS_DIR.exists():
        for child in sorted(SESSIONS_DIR.iterdir()):
            if not child.is_dir():
                continue
            owner_txt = child / "owner.txt"
            if not owner_txt.exists():
                continue
            try:
                owner = owner_txt.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if owner != username:
                continue
            has_jar = False
            dist_dir = child / "mod" / "dist"
            if dist_dir.is_dir():
                has_jar = any(dist_dir.glob("*.jar"))
            date = ""
            try:
                date = datetime.datetime.fromtimestamp(child.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                pass
            # 标题：优先 .chat/conversation.jsonl 的首条 user 消息（截断 24 字），
            # 无对话记录时回退为会话 ID 前 8 位（保持可识别）。
            title = _session_title(child)
            out.append({"sessionId": child.name, "owner": owner, "has_jar": has_jar, "date": date, "title": title})
    return {"sessions": out}


def _session_title(child: Path) -> str:
    """从会话目录推导展示标题：首条 user 消息截断，无则用 ID 前缀。"""
    conv_path = child / ".chat" / "conversation.jsonl"
    if conv_path.exists():
        try:
            with open(conv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        text = str(msg.get("content", "")).strip()
                        if text:
                            return text if len(text) <= 24 else text[:24] + "…"
        except OSError:
            pass
    return child.name[:8]


@app.get("/api/question")
def get_question(session_id: str, authorization: str = Header(default="")):
    """返回 agent 当前待回答的问题（agent 调 ask_user_question 时写入 question.json）。

    新格式：{"questions": [{"question": "...", "options": [...]}, ...]}（多问题）；
    兼容旧格式 {"question": "...", "options": [...]} → 归一化为 questions 数组。
    """
    username = _auth_username(authorization)
    sess = _get_session(session_id)
    _assert_owner(sess, username)
    qpath = sess.mod_dir.parent / "question.json"
    if not qpath.exists():
        return {"status": "none"}
    try:
        data = json.loads(qpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "none"}
    # 归一化：新格式 questions 数组 / 旧格式单 question
    if isinstance(data.get("questions"), list) and data["questions"]:
        return {"status": "pending", "questions": data["questions"]}
    if data.get("question"):
        return {"status": "pending", "questions": [{"question": data["question"], "options": data.get("options") or []}]}
    return {"status": "none"}


@app.post("/api/answer")
def post_answer(req: AnswerRequest, authorization: str = Header(default="")):
    """用户回答 agent 的问题：写 answer.json，agent 的 ask_user_question 轮询到后继续。

    支持两种 body：
      - 多题：{"session_id": ..., "answers": [{"question": "...", "answer": "..."}, ...]}
      - 单题（legacy）：{"session_id": ..., "answer": "..."}
    """
    username = _auth_username(authorization)
    sess = _get_session(req.session_id)
    _assert_owner(sess, username)
    apath = sess.mod_dir.parent / "answer.json"
    payload = {"answers": req.answers} if req.answers is not None else {"answer": req.answer}
    apath.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}


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
        if not _is_safe_session_id(session_id):
            raise HTTPException(status_code=400, detail="非法 session_id")
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
        if not _is_safe_session_id(sid):
            raise HTTPException(status_code=400, detail="非法 session_id")
        auth_store.remove_history(username, sid)
        sess = sessions.get(sid)
        if sess and sess.owner == username:
            _purge_session(sess)
        else:
            _purge_session_dir(sid)
    return {"history": _history_with_jar(username)}


# ---------- 健康检查（debug 页面探活用）----------
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "skill-agent web", "port": 8000}


# ---------- 前端静态资源 ----------
WEB_DIR.mkdir(exist_ok=True)


@app.get("/")
def index():
    """根路由显式返回首页，避免任何 mount 歧义导致 404。"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "index.html not found", "web_dir": str(WEB_DIR)}


# Debug 维护占位页（8000 挂了时用 Nginx 跳转，或直接访问 /debug/）
DEBUG_DIR = Path(__file__).resolve().parent / "debug"

@app.get("/debug")
@app.get("/debug/")
async def debug_page():
    idx = DEBUG_DIR / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return {"error": "debug page not found"}

@app.get("/debug/{filepath:path}")
async def debug_static(filepath: str):
    f = DEBUG_DIR / filepath
    if f.is_file():
        return FileResponse(str(f))
    raise HTTPException(404, "Not found")

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

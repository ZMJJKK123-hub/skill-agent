# -*- coding: utf-8 -*-
"""一次性修复：P3 拆分引入的 97 处 undefined name（用后即删）。

每处按 agent.md Rule 1 补「逐条注释导入」；循环依赖处用函数内
延迟导入并注释时序原因。
"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

R = Path.cwd()


def patch(rel, pairs):
    p = R / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, "NOT-UNIQUE/MISSING", old[:70])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"fixed {rel}")


# ── 1) run_task.py：三个提取函数的依赖归位（延迟导入保持重导入时序语义）──
patch("server_app/run_task.py", [
    # _prepare_workspace：DaemonFiles + EventWriter 标注改字符串
    ('''def _prepare_workspace(session_dir: Path, session_root: Path, mode: str,
                       writer: EventWriter) -> None:''',
     '''def _prepare_workspace(session_dir: Path, session_root: Path, mode: str,
                       writer: "EventWriter") -> None:'''),
    ('''    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))  # cwd 决定引擎工作区
    writer.notice(f"模式={mode} | 工作目录 => {session_dir}")
    DaemonFiles(session_root).write_pid_and_working()''',
     '''    from services.daemon_runner import DaemonFiles  # 延迟导入：保持 main 原有重导入时序（cwd 已切好）
    session_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(str(session_dir))  # cwd 决定引擎工作区
    writer.notice(f"模式={mode} | 工作目录 => {session_dir}")
    DaemonFiles(session_root).write_pid_and_working()'''),
    # _build_engine_or_exit
    ('''    try:
        os.environ["DSH_DEFER_DRAIN"] = "1"
        settings = Settings.from_env()
        return build_engine(settings), settings''',
     '''    from core.bootstrap import build_engine  # 延迟导入：构建必须发生在 cwd 切换后
    from core.infrastructure.config import Settings  # 同上：from_env 读工作区相关环境

    try:
        os.environ["DSH_DEFER_DRAIN"] = "1"
        settings = Settings.from_env()
        return build_engine(settings), settings'''),
    # _run_first_round_safely
    ('''    try:
        run_one_round(engine, messages, session_dir, store, writer, PROJECT_ROOT)
    except Exception as e:
        print_round_trace(e)
        notify_round_error(store, e)''',
     '''    from services.round_runner import (notify_round_error,  # 首轮执行三件套（延迟导入同 main 时序）
                                        print_round_trace,
                                        run_one_round)

    try:
        run_one_round(engine, messages, session_dir, store, writer, PROJECT_ROOT)
    except Exception as e:
        print_round_trace(e)
        notify_round_error(store, e)'''),
    # main 里 daemon_loop 调用点在 main 体内（有局部导入）→ 无需改；
    # 但 main 用的 EventWriter 标注已字符串化，模块级的 EventWriter 导入是否仍被引用？
    # 检查：保留（模块级导入供标注解析与潜在复用），pyflakes unused 会在终扫确认。
])

# ── 2) game/keys.py：stdlib 补导入 ──
patch("core/infrastructure/tools/game/keys.py", [
    ('''from ....config import logger  # 统一日志
from .input import _borrow_game_focus, _return_focus, _vk_code  # 焦点保护与键码表''',
     '''import ctypes  # Windows 键码发送（user32.keybd_event）
import time  # 按键间隔节流

from ....config import logger  # 统一日志
from .input import _borrow_game_focus, _return_focus, _vk_code  # 焦点保护与键码表'''),
])

# ── 3) game/rcon.py：os ──
s = (R / "core/infrastructure/tools/game/rcon.py").read_text(encoding="utf-8")
if "\nimport os" not in s and not s.startswith("import os"):
    first_import = s.index("import")
    s = s[:first_import] + "import os  # 环境变量与进程级路径操作\n" + s[first_import:]
    (R / "core/infrastructure/tools/game/rcon.py").write_text(s, encoding="utf-8")
print("fixed game/rcon.py")

# ── 4) game/input.py：_VK_MAP 从 rcon 导入 ──
patch("core/infrastructure/tools/game/input.py", [
    ("from ....config import logger",
     "from ....config import logger  # 统一日志\nfrom .rcon import _VK_MAP  # 键名→虚拟键码表（rcon 域持有）"),
])

# ── 5) game/verify.py：time + 两个跨域函数 ──
p = R / "core/infrastructure/tools/game/verify.py"
s = p.read_text(encoding="utf-8")
print("verify head:")
print("\n".join(s.splitlines()[:14]))

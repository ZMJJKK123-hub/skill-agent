# -*- coding: utf-8 -*-
"""GameTest 自测工具（由 mod.py 拆出）。

类职责：EULA 预写 / runTestGameTestServer 进程拉起与收割 /
latest.log 尾读；全部带路径沙箱与超时治理。
生命周期：handlers 注册为 run_game_test_server / read_game_test_log。
"""
import os
import subprocess
from pathlib import Path  # 日志路径类型

from ...config import logger, safe_path
from .mod import GAME_TEST_TIMEOUT  # GameTest 超时常量（build 域持有）
from .runtime import worktree_manager

#: GameTest 运行日志相对路径（与 build.gradle workingDir=run 一致）
GAME_TEST_LOG_PATH = "run/logs/latest.log"


def _ensure_game_test_eula(base: os.PathLike | str) -> None:
    """确保 run/eula.txt 存在且 eula=true（MC 服务端首次启动硬性要求）。

    不存在或内容不含 eula=true 时写入 eula=true；已正确则跳过。
    """
    try:
        run_dir = Path(base) / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        eula = run_dir / "eula.txt"
        if eula.exists() and "eula=true" in eula.read_text(encoding="utf-8", errors="replace"):
            return
        eula.write_text("eula=true\n", encoding="utf-8")
        logger.info(f"_ensure_game_test_eula | 已写入 {eula}")
    except Exception as e:
        logger.info(f"_ensure_game_test_eula 失败: {e}")


def _render_game_test_report(returncode: int, out: str) -> str:
    """输入：进程退出码 + 完整输出。返回：给模型的结果报告（截断 + 下一步提示）。

    职责：异常退出识别、read_game_test_log 引导、命名空间检查提示。
    """
    tail = out[-50000:]
    summary = "[gametest] runGameTestServer 已完成"
    if returncode != 0 and "GameTest" not in out:
        summary = "[gametest] runGameTestServer 进程异常退出（可能编译/运行错误）"
    hint = (
        "\n→ 请接着调用 read_game_test_log 读取 run/logs/latest.log 的最新日志，"
        "根据错误修复后重新调用本工具即可实现自循环调试。"
    )
    if "forge.enabledGameTestNamespaces" not in out and "tutorial_mod" not in out:
        hint += (
            "\n提示：若你的 GameTest 没有运行，检查 build.gradle 的 "
            "forge.enabledGameTestNamespaces 是否与你 mods.toml 的 modId 一致。"
        )
    return f"{summary}\n{tail}\n{hint}"


def _run_game_test_server(kw: dict) -> str:
    """run_game_test_server 工具：编译并运行 Forge GameTestServer。

    - 在 mod 工作目录执行 gradlew.bat/gradlew runGameTestServer（对应 build.gradle
      已配置的 register('gameTestServer')）。
    - 运行前自动确保 run/eula.txt（服务端首次启动必须接受 EULA）。
    - Popen + taskkill 进程树，超时 GAME_TEST_TIMEOUT 秒（首次构建可能数分钟）。
    - 输出截断返回给模型；模型再调用 read_game_test_log 读日志修复。
    """
    task = kw.get("gradle_task", "runGameTestServer")
    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
    _ensure_game_test_eula(base)

    from .mod import _gradle_cmd  # 命令构造与 build 工具共用一份
    cmd = _gradle_cmd(base, task)

    try:
        proc = subprocess.Popen(
            cmd, cwd=base,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
    except Exception as e:
        return f"[gametest] 无法启动 Gradle: {e}"

    try:
        out, _ = proc.communicate(timeout=GAME_TEST_TIMEOUT)
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(f"taskkill /f /t /pid {proc.pid}", shell=True, capture_output=True)
        except Exception as e:
            logger.debug("_run_game_test_server 降级忽略 | %s", e)
        try:
            proc.communicate(timeout=5)
        except Exception as e:
            logger.debug("_run_game_test_server 降级忽略 | %s", e)
        return (
            f"[gametest] runGameTestServer 超时（>{GAME_TEST_TIMEOUT}s），进程已终止。\n"
            f"注意：GameTestServer 运行完测试后可能不会自动退出（若有测试通过则等待全部完成）。\n"
            f"请用 read_game_test_log 读取 run/logs/latest.log 查看测试结果与错误。"
        )

    return _render_game_test_report(proc.returncode, out or "")


GAME_TEST_LOG_PATH = "run/logs/latest.log"  # 相对 mod 工作目录


def _read_game_test_log(kw: dict) -> str:
    """read_game_test_log 工具：读取 GameTestServer 运行日志尾部（默认 200 行）。

    路径：<mod工作目录>/run/logs/latest.log（与 build.gradle workingDir=run 一致）。
    只读、路径沙箱、从文件末尾取 lines 行（错误几乎都在末尾）。
    """
    lines_count = kw.get("lines", 200)
    try:
        lines_count = int(lines_count)
        if not (1 <= lines_count <= 2000):
            return "Error: read_game_test_log lines must be between 1 and 2000"
    except (TypeError, ValueError):
        return f"Error: read_game_test_log lines must be an integer, got '{kw.get('lines')}'"

    base = worktree_manager.resolve_dir() if worktree_manager else None
    try:
        log_path = safe_path(GAME_TEST_LOG_PATH, base)
    except Exception as e:
        return f"Error: {e}"
    if not log_path.exists():
        return (
            f"Error: {GAME_TEST_LOG_PATH} 不存在。"
            f"请先在 mod 工作目录调用 run_game_test_server 运行 GameTestServer，"
            f"之后再读取日志检查测试结果。"
        )

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            # 快速定位尾部：seek 到末尾往回读一个块，避免 10MB+ 日志整读
            f.seek(0, 2)
            size = f.tell()
            read_size = min(size, 200_000)  # 读最后约 200KB 足够覆盖 2000 行
            f.seek(size - read_size)
            tail_text = f.read()
        lines = tail_text.splitlines()
        data = lines[-lines_count:] if len(lines) > lines_count else lines
        return "\n".join(data)
    except Exception as e:
        return f"Error: 读取日志失败: {e}"

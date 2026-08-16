# -*- coding: utf-8 -*-
"""Forge MOD build + GameTest tool implementations (moved from core/tools.py)."""
import os
import subprocess
import sys
from pathlib import Path

from .config import logger, safe_path
from .gradletools import GRADLE_TOOLS as _GT
from .tools_runtime import worktree_manager

_GT_BASE = None


def _gt_base():
    global _GT_BASE
    if _GT_BASE is None:
        import core.config as _c
        _GT_BASE = worktree_manager.resolve_dir() if worktree_manager else str(_c.WORKDIR)
    return _GT_BASE

# ========== Forge Mod 生成工具（MC 26.x / Forge 65.x，2026-08） ==========
# 纯模板生成：输入参数 → 生成文件内容 → 用 run_write 写入当前 mod 工作目录。
# 所有 handler 都是工具函数增量，不依赖也不修改 agent 主循环。

def _build_source_zip() -> str:
    """源码 zip 预生成：在 agent 收尾阶段把当前 mod 工程打包为 mod.zip。

    与 server 的 download_mod 采用相同规则（跳过 build/dist/.git 等运行时目录），
    这样用户第一次点击下载时后端直接命中缓存返回，无需现场打包 11MB。
    """
    import zipfile

    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
    zip_path = base.parent / "mod.zip"  # <session>/mod.zip（与 server SESSIONS_DIR 布局一致）
    skip = {"build", "dist", ".worktrees", ".team", ".tasks",
            ".transcripts", "__pycache__", ".git", "mc_java_sources"}
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(base):
                for p in sorted(Path(base).rglob("*")):
                    try:
                        rel = p.relative_to(Path(base))
                    except ValueError:
                        continue
                    if any(part in skip for part in rel.parts):
                        continue
                    if p.is_file():
                        zf.write(p, rel.as_posix())
        return f"[build] 源码 zip 已预生成: {zip_path}"
    except Exception as e:
        return f"[build] 源码 zip 预生成失败: {e}"


def _forge_build_jar(kw: dict) -> str:
    """build_mod_jar_forge：构建 Forge mod 项目为可安装 jar（gradlew build）。

    与 run_bash 的 30s 超时不同，这里用同步长超时（900s）等待 Forge Gradle
    首次构建完成（下载依赖 + 反混淆通常需要数分钟）。构建成功后把
    build/libs/*.jar 复制到工程根的 dist/ 目录便于识别/下载。
    """
    task = kw.get("gradle_task", "build")
    base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()

    if os.name == "nt" or sys.platform == "win32":
        if os.path.exists(os.path.join(base, "gradlew.bat")):
            cmd = ["cmd", "/c", "gradlew.bat", task]
        else:
            cmd = ["cmd", "/c", "gradle", task, "--console=plain"]
    else:
        if os.path.exists(os.path.join(base, "gradlew")):
            cmd = ["./gradlew", task, "--console=plain"]
        else:
            cmd = ["gradle", task, "--console=plain"]

    try:
        proc = subprocess.Popen(
            cmd, cwd=base,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        )
    except Exception as e:
        return f"[build] 无法启动 Gradle: {e}"

    try:
        out, _ = proc.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(f"taskkill /f /t /pid {proc.pid}", shell=True, capture_output=True)
        except Exception:
            pass
        return f"[build] Gradle 构建超时（>900s）。\n日志尾部:\n{(out or '')[-3000:]}"

    ok = proc.returncode == 0
    tail = (out or "")[-3000:]

    if not ok:
        hint = ""
        if "Failed to find JDK for version 8" in (out or "") and "JavaProvisionerException" in (out or ""):
            hint = (
                "原因：ForgeGradle 的 Mavenizer 在配置阶段需要自动下载其内部使用的 JDK"
                "（含 Java 8），但服务器 SSL/证书校验失败（PKIX path building failed）"
                "导致下载被拦截。\n"
                "注意：不需要手动安装或切换 JAVA_HOME 到 JDK 8——Gradle 本身要求 JVM 17 或更高，"
                "系统主 JDK 保持 25（或 21）即可。\n"
                "解决：修复服务器 SSL 证书/网络代理（放行 github.com 与 adoptium 下载）后重新生成。"
            )
        elif "SSLHandshakeException" in (out or "") or "PKIX path building failed" in (out or ""):
            hint = (
                "原因：Gradle 下载依赖时 SSL 证书校验失败"
                "（多为代理/公司网络拦截或系统根证书不全）。\n"
                "解决：修复证书/代理后重新生成。"
            )
        else:
            hint = "原因：构建过程出错（详见日志尾部）。"
        return (
            f"[build] Gradle 构建失败 (exit={proc.returncode})。\n"
            f"{hint}\n日志尾部:\n{tail}"
        )

    libs_dir = os.path.join(base, "build", "libs")
    jars = []
    if os.path.isdir(libs_dir):
        for fname in sorted(os.listdir(libs_dir)):
            if fname.endswith(".jar"):
                jars.append(fname)
                try:
                    ddist = os.path.join(base, "dist")
                    os.makedirs(ddist, exist_ok=True)
                    import shutil as _sh
                    _sh.copy2(os.path.join(libs_dir, fname), os.path.join(ddist, fname))
                except Exception as e:
                    return f"[build] 构建成功但复制 jar 失败: {e}"

    if not jars:
        return f"[build] 构建完成但未在 build/libs 找到 jar。\n日志尾部:\n{tail}"

    sizes = []
    for j in jars:
        try:
            sizes.append(f"{j} ({os.path.getsize(os.path.join(base,'dist',j))} B)")
        except OSError:
            sizes.append(j)
    return (
        f"[build] 构建成功 ✓ 产出 jar：\n  " + "\n  ".join(sizes) +
        "\n已复制到工程根的 dist/ 目录，可直接放入 .minecraft/mods/。"
    )


# ========== GameTest 自循环调试工具（仅主 agent 可用） ==========
# run_game_test_server: 调 gradlew runGameTestServer 编译并运行全部 GameTest。
# read_game_test_log:    读 <mod>/run/logs/latest.log 尾部日志，把错误喂给模型修复。
# 两者都通过 leader 侧（主 agent）使用；teammate / subagent 的过滤集合已排除。

GAME_TEST_TIMEOUT = 900  # 首次 runGameTestServer 需下载依赖/反混淆，给足 900s


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

    if os.name == "nt" or sys.platform == "win32":
        if os.path.exists(os.path.join(base, "gradlew.bat")):
            cmd = ["cmd", "/c", "gradlew.bat", task]
        else:
            cmd = ["cmd", "/c", "gradle", task, "--console=plain"]
    else:
        if os.path.exists(os.path.join(base, "gradlew")):
            cmd = ["./gradlew", task, "--console=plain"]
        else:
            cmd = ["gradle", task, "--console=plain"]

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
        except Exception:
            pass
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        return (
            f"[gametest] runGameTestServer 超时（>{GAME_TEST_TIMEOUT}s），进程已终止。\n"
            f"注意：GameTestServer 运行完测试后可能不会自动退出（若有测试通过则等待全部完成）。\n"
            f"请用 read_game_test_log 读取 run/logs/latest.log 查看测试结果与错误。"
        )

    ok = proc.returncode == 0
    tail = (out or "")[-50000:]
    summary = "[gametest] runGameTestServer 已完成"
    if not ok and "GameTest" not in (out or ""):
        summary = "[gametest] runGameTestServer 进程异常退出（可能编译/运行错误）"
    hint = (
        f"\n→ 请接着调用 read_game_test_log 读取 run/logs/latest.log 的最新日志，"
        f"根据错误修复后重新调用本工具即可实现自循环调试。"
    )
    if "forge.enabledGameTestNamespaces" not in (out or "") and "tutorial_mod" not in (out or ""):
        hint += (
            "\n提示：若你的 GameTest 没有运行，检查 build.gradle 的 "
            "forge.enabledGameTestNamespaces 是否与你 mods.toml 的 modId 一致。"
        )
    return f"{summary}\n{tail}\n{hint}"


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




def _gt_tool(name, kw):
    """gradle 工具公共入口：懒定位工作目录，调用 gradletools 并序列化结果。"""
    import json as _json
    base = worktree_manager.resolve_dir() if worktree_manager else None
    if not base:
        import core.config as _c
        base = str(_c.WORKDIR)
    fn = _GT[name]
    r = fn(base)
    return _json.dumps(r, ensure_ascii=False)

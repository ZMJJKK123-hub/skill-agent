# -*- coding: utf-8 -*-
"""Forge MOD build + GameTest tool implementations (moved from core/tools.py)."""
import os
import subprocess
import sys
from pathlib import Path

from ...config import logger, safe_path
from ...gradletools import GRADLE_TOOLS as _GT
from .runtime import worktree_manager

_GT_BASE = None



def _build_source_zip() -> str:
    """源码 zip 预生成：在 agent 收尾阶段把当前 mod 工程打包为 mod.zip。

    与 server 的 download_mod 采用相同规则（跳过 build/dist/.git 等运行时目录），
    这样用户第一次点击下载时后端直接命中缓存返回，无需现场打包 11MB。
    """
    import zipfile

    # base 必须是 Path：resolve_dir()/os.getcwd() 都返回 str，
    # 直接 .parent 会抛 'str' object has no attribute 'parent'
    # （此前 zip 预生成一直在收尾时静默失败，mod.zip 从未预生成）
    from pathlib import Path as _Path
    base = _Path(worktree_manager.resolve_dir() if worktree_manager else os.getcwd())
    zip_path = base.parent / "mod.zip"  # <session>/mod.zip（与 server SESSIONS_DIR 布局一致）
    skip = {"build", "dist", ".worktrees", ".team", ".tasks",
            ".transcripts", "__pycache__", ".git", "mc_java_sources",
            # run/ 是游戏运行目录（存档/日志/缓存，几十 MB 且非源码），不打进 zip
            "run", "run-data", ".gradle", ".chat", ".screenshots", ".spill"}
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
        except Exception as e:
            logger.debug("_forge_build_jar 降级忽略 | %s", e)
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

# GameTest 域拆至 mod_gametest（handlers 引用；此处再导出保持兼容）
from .mod_gametest import _ensure_game_test_eula, _read_game_test_log, _run_game_test_server  # noqa: E402,F401

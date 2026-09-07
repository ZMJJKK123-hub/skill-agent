# -*- coding: utf-8 -*-
"""MOD 模板装配（server_app/services 层；原 server.py _copy_template 迁移）。

把 mod_templates/<game>[/<loader>-<version>] 复制为会话工作区起点，
并建立 mc_java_sources / docs/agent 的 junction（零存储成本的只读参考）。
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from core.infrastructure.logging_.logger import get_logger

logger = get_logger("server.templates")

#: 仓库根（mc_java_sources_* 与 docs/agent 的真实位置）。
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _link_junction(link: Path, source: Path) -> None:
    """输入：链接路径 + 源目录。返回：无。职责：缺失时建目录 junction（跨平台）。"""
    if link.exists() or not source.is_dir():
        return
    try:
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(source)],
                           check=True, capture_output=True)
        else:
            link.symlink_to(source, target_is_directory=True)
        logger.info("linked %s -> %s", link.name, source)
    except (OSError, subprocess.CalledProcessError) as e:
        logger.warning("link %s 失败: %s", link, e)


def copy_template(game: str, dest: Path, loader: str = "",
                  version: str = "") -> Path:
    """把对应模板复制到会话目录（作为 agent 起点），并挂只读参考 junction。

    Args:
        game: 游戏名（mod_templates 一级目录）。
        dest: 会话 mod/ 目标目录。
        loader: 加载器（如 forge；与 version 联合定位子目录）。
        version: 版本（如 1.21.11 / 26.2）。
    Returns:
        目标目录（模板不存在时为空目录——agent 自由发挥）。
    Globals Used: 无（PROJECT_ROOT 为本模块常量）。
    Calls: shutil.copytree / _link_junction。
    """
    templates = PROJECT_ROOT / "mod_templates"
    src = templates / game
    src_is_sub = False
    if loader and version:
        sub = templates / game / f"{loader}-{version}"
        if sub.exists():
            src, src_is_sub = sub, True
    dest.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    # 子目录模板自带 KNOWN_ISSUES.md 已随 copytree 复制；只有回退到
    # <game>/ 根时才无条件复制根级 KNOWN_ISSUES.md（默认占位）。
    if not src_is_sub:
        issues = templates / game / "KNOWN_ISSUES.md"
        if issues.exists():
            shutil.copy2(issues, dest / "KNOWN_ISSUES.md")
    # 只读参考 junction：按版本选源码树（26.2 独立树）
    mc_sources = (PROJECT_ROOT / "mc_java_sources_26.2" if version.startswith("26.2")
                  else PROJECT_ROOT / "mc_java_sources_1.21.11")
    _link_junction(dest / "mc_java_sources", mc_sources)
    _link_junction(dest / "docs" / "agent", PROJECT_ROOT / "docs" / "agent")
    return dest


def init_session_git(mod_dir: Path) -> None:
    """输入：会话 mod 目录。返回：无。职责：git init 独立仓库（防检查点命中主仓库）。

    无本地 .git 时 git_commit 会向上命中主仓库 .git，把整个主仓库的
    未提交改动一起提交（实测 juice 会话检查点扫走仓库根源码改动）。
    """
    if (mod_dir / ".git").exists():
        return
    try:
        subprocess.run(["git", "init"], cwd=str(mod_dir),
                       capture_output=True, text=True, timeout=30)
    except Exception as e:  # git 不可用不影响工作区准备，仅检查点会向上命中
        logger.warning("git init 失败（忽略）: %s", e)


def has_template_content(mod_dir: Path) -> bool:
    """输入：会话 mod 目录。返回：是否已复制过模板（幂等判定）。"""
    try:
        return mod_dir.exists() and any(mod_dir.iterdir())
    except OSError:
        return False

# -*- coding: utf-8 -*-
"""产物打包（server_app/services 层；原 /api/download 内联逻辑迁移）。

源码 zip 的缓存 + 原子替换打包：mtime 缓存避免重复压 11MB；临时文件
成功后 os.replace——中途失败不留下半截 zip（半截 zip 的 mtime 最新会让
缓存判断跳过重建，用户永远下载到坏档）。
"""
from __future__ import annotations

import os
import threading
import zipfile
from pathlib import Path

from core.infrastructure.logging_.logger import get_logger

logger = get_logger("server.packaging")

#: 下载互斥锁：zipfile 非原子写，并发写同一文件会拿到 Content-Length 不匹配。
_download_lock = threading.Lock()

#: 源码 zip 排除目录/文件（构建产物、运行时、只读参考都不是源码）。
ZIP_SKIP = {"build", "dist", ".gradle", ".chat", "agent.log", "run.log",
            ".worktrees", ".team", ".tasks", ".transcripts", "__pycache__",
            ".git", "mc_java_sources",
            "run", "run-data", ".screenshots", ".spill"}


def _zip_is_fresh(zip_path: Path, mod_dir: Path) -> bool:
    """输入：zip 路径 + 源目录。返回：缓存是否仍新（比所有入包文件 mtime 新）。"""
    if not zip_path.exists() or not mod_dir.exists():
        return False
    zip_mtime = zip_path.stat().st_mtime
    newest_src = 0
    for p in mod_dir.rglob("*"):
        try:
            if not p.is_file():
                continue
            if any(part in ZIP_SKIP for part in p.relative_to(mod_dir).parts):
                continue
            newest_src = max(newest_src, p.stat().st_mtime)
        except OSError:
            continue  # 句柄未释放的瞬时错误不触发重打包
    return zip_mtime >= newest_src


def _write_zip_atomic(zip_path: Path, mod_dir: Path) -> None:
    """输入：目标 zip + 源目录。返回：无。职责：临时文件打包后原子替换。"""
    tmp_path = zip_path.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if mod_dir.exists():
                for p in sorted(mod_dir.rglob("*")):
                    try:
                        rel = p.relative_to(mod_dir)
                    except ValueError:
                        continue
                    if any(part in ZIP_SKIP for part in rel.parts):
                        continue
                    if p.is_file():
                        try:
                            zf.write(p, rel.as_posix())
                        except OSError:
                            continue  # 单文件被锁：跳过，不毁掉整个包
        os.replace(tmp_path, zip_path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def build_source_zip(session_dir: Path, mod_dir: Path) -> Path:
    """生成（或复用缓存的）源码 zip，返回路径。

    Args:
        session_dir: 会话根（zip 落 <session>/mod.zip）。
        mod_dir: 源码目录。
    Returns:
        zip 文件路径（调用方读字节返回——绕开 h11 大响应体 bug）。
    """
    zip_path = session_dir / "mod.zip"
    with _download_lock:
        if not _zip_is_fresh(zip_path, mod_dir):
            _write_zip_atomic(zip_path, mod_dir)
        return zip_path


def find_built_jar(mod_dir: Path) -> Path | None:
    """输入：mod 目录。返回：dist 下首个 jar（无则 None）。"""
    dist = mod_dir / "dist"
    try:
        if dist.is_dir():
            jars = sorted(dist.glob("*.jar"))
            if jars:
                return jars[0]
    except OSError as e:
        logger.warning("jar 定位失败: %s", e)
    return None

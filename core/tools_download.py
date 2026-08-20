# -*- coding: utf-8 -*-
"""download_file / extract_archive: safe external file download and archive extraction."""
import os
import tarfile
import zipfile
from pathlib import Path

from .config import safe_path
from .tools_runtime import worktree_manager


def _base_dir() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def download_file(url: str, dest_path: str) -> str:
    """Download a URL to a workspace path (UTF-8 binary safe)."""
    try:
        import httpx
        from .tools_web import _is_ssrf_blocked
        if _is_ssrf_blocked(url):
            return "Error: URL 被 SSRF 防护拦截（不允许访问内网/私网地址）"
        base = _base_dir()
        dest = safe_path(dest_path, base)
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = httpx.get(url, timeout=60, follow_redirects=False)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return f"Downloaded {len(r.content)} bytes to {dest}"
    except Exception as e:
        return f"Error: download failed: {e}"


def extract_archive(archive_path: str, dest_path: str) -> str:
    """Extract a zip/tar.gz archive into a workspace directory (zip-slip safe)."""
    try:
        base = _base_dir()
        archive = safe_path(archive_path, base)
        dest = safe_path(dest_path, base)
        dest.mkdir(parents=True, exist_ok=True)
        if not archive.is_file():
            return f"Error: archive not found: {archive}"
        if archive.suffix.lower() == ".zip" or archive.name.lower().endswith(".jar"):
            with zipfile.ZipFile(archive) as zf:
                for member in zf.infolist():
                    target = (dest / member.filename).resolve()
                    if not target.is_relative_to(dest.resolve()):
                        return f"Error: archive contains illegal path: {member.filename}"
                    if member.is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target, "wb") as dst:
                            dst.write(src.read())
        elif archive.name.endswith((".tar.gz", ".tgz", ".tar")):
            with tarfile.open(archive, "r:*") as tf:
                for member in tf.getmembers():
                    target = (dest / member.name).resolve()
                    if not target.is_relative_to(dest.resolve()):
                        return f"Error: archive contains illegal path: {member.name}"
                    if member.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    elif member.isfile():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tf.extractfile(member) as src, open(target, "wb") as dst:
                            dst.write(src.read())
        else:
            return f"Error: unsupported archive type: {archive.suffix}"
        return f"Extracted {archive.name} to {dest}"
    except Exception as e:
        return f"Error: extract failed: {e}"

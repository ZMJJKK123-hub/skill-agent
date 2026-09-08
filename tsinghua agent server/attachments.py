# -*- coding: utf-8 -*-
"""文件产物收集：扫描工作区可交付文件构造 x_soda.attachments（由 main.py 迁出）。"""
import mimetypes
from pathlib import Path

from config_env import WORKSPACE


_ATTACHMENT_EXCLUDE_DIRS = {
    ".chat", ".tasks", ".team", ".worktrees", ".transcripts", ".spill",
    ".supervisor", "__pycache__", ".git", "node_modules", "venv",
    "data", "core", "server_app", "mod_templates", "mc_java_sources",
    "docs", "frontend", "web", "assets", "screenshots", "inputs",
}

_ATTACHMENT_EXTS = {
    ".zip", ".jar", ".tar", ".gz", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".md", ".csv", ".rtf",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
}

_ATTACHMENT_FILE_TYPE = {
    ".zip": "archive", ".jar": "file", ".tar": "archive", ".gz": "archive", ".7z": "archive",
    ".pdf": "pdf", ".doc": "word", ".docx": "word",
    ".xls": "excel", ".xlsx": "excel", ".ppt": "ppt", ".pptx": "ppt",
    ".txt": "text", ".md": "text", ".csv": "text", ".rtf": "text",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".webp": "image", ".bmp": "image", ".svg": "image",
}


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _deliverable(rel: Path, p: Path, start_ts: float) -> bool:
    """是否可交付：白名单扩展 + 排除目录 + 时间窗（由 collect_attachments 拆出）。"""
    if any(part in _ATTACHMENT_EXCLUDE_DIRS for part in rel.parts):
        return False
    if p.suffix.lower() not in _ATTACHMENT_EXTS:
        return False
    try:
        return p.stat().st_mtime >= start_ts - 1
    except OSError:
        return False


def collect_attachments(start_ts: float, base_url: str, limit: int = 10, scope: Path | None = None) -> list[dict]:
    """收集 start_ts 之后生成的可交付文件，构造清小搭 x_soda.attachments。"""
    root = scope if scope is not None else WORKSPACE
    if not root.exists():
        return []
    attachments: list[dict] = []
    seen: set[str] = set()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(WORKSPACE)
        except ValueError:
            continue
        if not _deliverable(rel, p, start_ts):
            continue
            continue
        key = rel.as_posix()
        if key in seen:
            continue
        seen.add(key)
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        attachments.append({
            "fileUrl": f"{base_url}/files/{key}",
            "fileName": p.name,
            "fileType": _ATTACHMENT_FILE_TYPE.get(p.suffix.lower(), "file"),
            "mimeType": guess_mime(p),
            "fileSize": size,
        })
        if len(attachments) >= limit:
            break
    return attachments

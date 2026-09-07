# -*- coding: utf-8 -*-
"""文件树构建与单文件预览（防路径越界 + 100KB 上限）。
由 log_events.py 原样迁出。
"""
from pathlib import Path


# ---------- 文件树 ----------

def build_file_tree(root: Path, rel: str = "") -> dict:
    """递归构建文件树。返回 {name, path, type, size, children?}"""
    node = {
        "name": Path(rel).name if rel else root.name,
        "path": rel,
        "type": "dir",
        "children": [],
    }
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError:
        return node
    for p in entries:
        # 跳过运行时产物（mc_java_sources = MC+Forge 源码树，只对 agent 可见，
        # 不展示给前端，避免文件树渲染 8000+ 节点）
        if p.name in (".worktrees", ".team", ".tasks", ".transcripts",
                      "__pycache__", "agent.log", "run.log", ".git",
                      "mc_java_sources"):
            continue
        child_rel = f"{rel}/{p.name}" if rel else p.name
        if p.is_dir():
            node["children"].append(build_file_tree(p, child_rel))
        else:
            try:
                sz = p.stat().st_size
            except OSError:
                sz = 0
            node["children"].append({
                "name": p.name,
                "path": child_rel,
                "type": "file",
                "size": sz,
            })
    return node


MAX_PREVIEW = 100_000  # 预览上限 100KB


def read_file_preview(root: Path, rel_path: str) -> dict:
    """读取文件内容用于预览。返回 {content, truncated, size} 或错误 dict。"""
    target = (root / rel_path).resolve()
    # 防越界：必须位于 root 之下
    if not target.is_relative_to(root.resolve()):
        return {"error": "invalid path"}
    if not target.is_file():
        return {"error": "not a file"}
    size = target.stat().st_size
    data = target.read_text(encoding="utf-8", errors="replace")
    truncated = len(data) > MAX_PREVIEW
    return {
        "content": data[:MAX_PREVIEW],
        "truncated": truncated,
        "size": size,
    }

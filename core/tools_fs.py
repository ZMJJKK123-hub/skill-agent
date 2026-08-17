# -*- coding: utf-8 -*-
"""File read/write/edit/search tool implementations (moved from core/tools.py)."""
import fnmatch
import os
import re
from pathlib import Path

from . import config
from .config import logger, safe_path
from .skillcheck import any_loaded
from .tools_runtime import worktree_manager
from .tools_shell import _sandbox_mode


def run_read(path: str, limit: int = None) -> str:
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        text = safe_path(path, base).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"

def _is_mod_file(path: str) -> bool:
    """判断路径是否属 MOD 工程文件（需先 load_skill 才能写）。
    覆盖 src/main、src/test、Gradle 构建脚本、mods.toml 元数据等。"""
    p = path.replace("\\", "/").strip("/")
    frags = ("src/main", "src/test", "src/api/java",
             "build.gradle", "settings.gradle", "gradle.properties",
             "mods.toml", "neoforge.mods.toml", "META-INF/mods.toml")
    return any(f in p for f in frags)


def run_write(path: str, content: str) -> str:
    if _sandbox_mode() == "read-only":
        return "Error: read-only 模式禁止写入文件"
    # 已按用户要求关闭“必须先 load_skill 才能写 MOD 文件”的限制，允许先写后验证
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    if _sandbox_mode() == "read-only":
        return "Error: read-only 模式禁止修改文件"
    # 已按用户要求关闭“必须先 load_skill 才能改 MOD 文件”的限制，允许先写后验证
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        content = fp.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"

# ---------- 文件搜索 / 网络工具（移植 dsh 的 tool-fs-search / tool-web）----------
# grep/glob：直接搜工作区文件（含 mc_java_sources、skills、生成代码），
# 不再依赖 bash findstr 的脆弱转义；web_search/web_fetch：联网查资料/抓取网页。
_SEARCH_SKIP_DIRS = {
    ".gradle", "build", "dist", ".git", ".idea", ".vscode",
    "node_modules", ".worktrees", ".team", ".tasks", ".transcripts",
    "__pycache__", "run", "bin", "venv", "mc_java_sources",
}


def _search_base() -> str:
    return worktree_manager.resolve_dir() if worktree_manager else os.getcwd()


def run_glob(pattern: str) -> str:
    """按 glob 模式查找文件，返回相对工作区的路径列表（跳过运行时目录）。"""
    try:
        base = Path(_search_base()).resolve()
        matches = []
        for p in base.rglob(pattern):
            if not p.is_file():
                continue
            try:
                parts = p.relative_to(base).parts
            except ValueError:
                continue
            if any(part in _SEARCH_SKIP_DIRS for part in parts):
                continue
            matches.append(str(p.relative_to(base)))
        matches = matches[:200]
        if not matches:
            return "(no files matched)"
        if len(matches) == 200:
            return "\n".join(matches) + "\n... (仅显示前 200 条)"
        return "\n".join(matches)
    except Exception as e:
        return f"Error: {e}"


def run_grep(pattern: str, path: str = ".", glob_filter: str = None,
             max_results: int = 50) -> str:
    """正则搜索文件内容，返回 '相对路径:行号: 行内容'（跳过运行时目录）。"""
    try:
        base = Path(_search_base()).resolve()
        root = (base / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        # 沙箱：非 full-access 禁止搜工作区之外
        if _sandbox_mode() != "full-access" and not str(root).startswith(str(base)):
            return "Error: grep 路径越出工作区"
        rx = re.compile(pattern)
        results = []

        def _walk(directory: Path):
            for dirpath, dirnames, filenames in os.walk(str(directory)):
                dirnames[:] = [d for d in dirnames if d not in _SEARCH_SKIP_DIRS]
                for fname in filenames:
                    if glob_filter and not fnmatch.fnmatch(fname, glob_filter):
                        continue
                    fp = Path(dirpath) / fname
                    try:
                        text = fp.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        continue
                    for i, line in enumerate(text.splitlines(), 1):
                        if rx.search(line):
                            try:
                                rel = str(fp.relative_to(base))
                            except ValueError:
                                rel = str(fp)
                            results.append(f"{rel}:{i}: {line[:300]}")
                            if len(results) >= max_results:
                                return

        if root.is_dir():
            _walk(root)
        elif root.is_file():
            try:
                text = root.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return "(no matches)"
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    results.append(f"{path}:{i}: {line[:300]}")
                    if len(results) >= max_results:
                        break
        out = "\n".join(results) if results else "(no matches)"
        if len(results) >= max_results:
            out += f"\n... (截断，共显示 {max_results} 条)"
        return out
    except Exception as e:
        return f"Error: {e}"


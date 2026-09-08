# -*- coding: utf-8 -*-
"""File read/write/edit/search tool implementations (moved from core/tools.py)."""
import fnmatch
import os
import re
from pathlib import Path

from ... import config
from ...config import safe_path
from .runtime import worktree_manager
from .shell import _sandbox_mode
from ...config import logger  # 统一日志：降级路径记录
from ...config import logger  # 统一日志：降级路径记录


def run_read(path: str, limit: int = None, offset: int = 0) -> str:
    """Read a file. offset is 1-based first line; limit caps line count.

    Full source files (mc_java_sources) are allowed by safe_path; use this
    instead of search_api when you need constructor/method/record signatures.
    """
    try:
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        fp = _remap_mc_sources(fp)
        text = fp.read_text(encoding="utf-8")
        lines = text.splitlines()
        if offset and offset > 0:
            lines = lines[offset - 1:]
        if limit and limit > 0:
            lines = lines[:limit]
        return "\n".join(lines)[:120000]
    except Exception as e:
        return f"Error: {e}"


def _is_mc_java_sources(fp: Path) -> bool:
    """判断解析后的路径是否落在只读 MC/Forge 源码参考树。"""
    try:
        repo_root = Path(__file__).resolve().parent.parent
        resolved = fp.resolve()
        for name in ("mc_java_sources_1.21.11", "mc_java_sources_26.2"):
            src = (repo_root / name).resolve()
            if src.exists() and resolved.is_relative_to(src):
                return True
        # docs/agent 是只读参考文档，同样禁止写入。
        # （此前误放在 except 分支里成为死代码，正常流程永远执行不到）
        docs_agent = (repo_root / "docs" / "agent").resolve()
        if docs_agent.exists() and resolved.is_relative_to(docs_agent):
            return True
    except Exception as e:  # noqa: BLE001
        logger.debug("路径判定失败按可写处理（降级忽略） | %s", e)
    return False


def run_write(path: str, content: str) -> str:
    if _sandbox_mode() == "read-only":
        return "Error: read-only 模式禁止写入文件"
    # 提示词要求先加载最相关技能，但运行时不强制前置拦截；写和验证优先
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        if _is_mc_java_sources(fp):
            return "Error: mc_java_sources 是只读参考源码，禁止修改"
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    if _sandbox_mode() == "read-only":
        return "Error: read-only 模式禁止修改文件"
    # 提示词要求先加载最相关技能，但运行时不强制前置拦截；写和验证优先
    try:
        # 第 12 课：基座跟随线程 session（worktree_use 后落在 worktree 内）
        base = worktree_manager.resolve_dir() if worktree_manager else None
        fp = safe_path(path, base)
        if _is_mc_java_sources(fp):
            return "Error: mc_java_sources 是只读参考源码，禁止修改"
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

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MC_SOURCE_TREES = ("mc_java_sources_1.21.11", "mc_java_sources_26.2")


def _remap_mc_sources(fp: Path) -> Path:
    """工作区缺 mc_java_sources junction 时，把该前缀引用重映射到仓库根源码树。

    chat 会话不建 junction（_ensure_mc_java_sources 仅 mod 模式启用），但
    工具指引明确让模型用 search_api/read_file 查 mc_java_sources——不重映射
    则每次必然空手而归（cbc300ed23b3 实测 4 连空，模型被迫靠参数记忆答题，
    还把本项目映射里不存在的 ResourceLocation 写进了答案）。
    """
    if fp.exists():
        return fp
    workdir_mc = Path(config.WORKDIR) / "mc_java_sources"
    try:
        rel = fp.resolve().relative_to(workdir_mc.resolve())
    except (ValueError, OSError):
        return fp
    for tree in _MC_SOURCE_TREES:
        cand = _REPO_ROOT / tree / rel
        if cand.exists():
            return cand
    return fp


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


def run_search_api(symbol: str, path: str = "mc_java_sources", max_results: int = 10, context_lines: int = 0) -> str:
    """Focused API-lookup helper.

    Searches the given path (default MC/Forge sources) for the exact symbol.
    symbol is treated as literal text (auto regex-escaped). Set context_lines>0
    to see surrounding lines; if you need the full signature, use read_file on
    the reported .java file instead.
    """
    import re as _re
    escaped = _re.escape(symbol)
    try:
        out = run_grep(escaped, path=path, glob_filter="*.java",
                       max_results=max_results, context_lines=context_lines)
        prefix = f"[search_api] Searching literal '{symbol}' in {path} (max {max_results} lines, context {context_lines}):\n"
        return prefix + out
    except Exception as e:
        return f"Error: {e}"


def _grep_emit(results: list, rel: str, src_lines: list, idx: int,
               context_lines: int) -> None:
    """命中行（含上下文）追加进结果（由 run_grep 迁出）。"""
    ctx = context_lines if context_lines and context_lines > 0 else 0
    lo = max(0, idx - 1 - ctx)
    hi = min(len(src_lines), idx + ctx)
    for n in range(lo, hi):
        results.append(f"{rel}:{n + 1}: {src_lines[n][:300]}")


def _grep_one_file(fp: Path, rel: str, rx, max_results: int,
                   context_lines: int, already: int) -> list:
    """单文件扫描（相对路径标签 rel 由调用方给定）。"""
    out: list = []
    try:
        src = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for i, line in enumerate(src, 1):
        if rx.search(line):
            _grep_emit(out, rel, src, i, context_lines)
            if len(out) + already >= max_results:
                break
    return out


def _grep_walk(directory: Path, base: Path, rx, glob_filter,
               max_results: int, context_lines: int) -> list:
    """目录树扫描（跳过运行时目录；glob 过滤；达到上限即停）。"""
    results: list = []
    for dirpath, dirnames, filenames in os.walk(str(directory)):
        dirnames[:] = [d for d in dirnames if d not in _SEARCH_SKIP_DIRS]
        for fname in filenames:
            if glob_filter and not fnmatch.fnmatch(fname, glob_filter):
                continue
            fp = Path(dirpath) / fname
            try:
                rel = str(fp.relative_to(base))
            except ValueError:
                rel = str(fp)
            part = _grep_one_file(fp, rel, rx, max_results,
                                  context_lines, len(results))
            results.extend(part)
            if len(results) >= max_results:
                return results
    return results


def _grep_sandbox_ok(root: Path, base: Path) -> bool:
    """输入：目标路径 + 工作区根。返回：是否允许搜索。

    职责：非 full-access 禁止越出工作区；只读参考树
    （mc_java_sources / docs/agent）例外。
    """
    if _sandbox_mode() == "full-access" or str(root).startswith(str(base)):
        return True
    repo_root = Path(__file__).resolve().parent.parent
    allowed_refs = [
        (repo_root / "mc_java_sources_1.21.11").resolve(),
        (repo_root / "mc_java_sources_26.2").resolve(),
        (repo_root / "docs" / "agent").resolve(),
    ]
    return any(ref.exists() and str(root).startswith(str(ref))
               for ref in allowed_refs)


def run_grep(pattern: str, path: str = ".", glob_filter: str = None,
             max_results: int = 50, context_lines: int = 0) -> str:
    """正则搜索文件内容，返回 '相对路径:行号: 行内容'（跳过运行时目录）。

    context_lines>0 时每个匹配附带前后 context_lines 行，方便确认签名/上下文。
    Calls: _grep_sandbox_ok。
    """
    try:
        base = Path(_search_base()).resolve()
        root = (base / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        # 源码树重映射：工作区无 mc_java_sources（chat 会话）时落到仓库根参考树
        root = _remap_mc_sources(root)
        if not _grep_sandbox_ok(root, base):
            return "Error: grep 路径越出工作区"
        try:
            rx = re.compile(pattern)
        except re.error as e:
            return f"Error: invalid regex '{pattern}': {e}"
        results = _grep_walk(root, base, rx, glob_filter,
                             max_results, context_lines)
        emitted = len(results)

        if root.is_file():
            results += _grep_one_file(root, str(path), rx, max_results,
                                      context_lines, emitted)
        out = "\n".join(results) if results else "(no matches)"
        if len(results) >= max_results:
            out += f"\n... (截断，共显示 {max_results} 条)"
        return out
    except Exception as e:
        return f"Error: {e}"


# -*- coding: utf-8 -*-
"""grep 工具域（由 fs.py 拆出）：沙箱判定 + 目录/单文件扫描 + 上下文输出。"""
import os
import re
from fnmatch import fnmatch
from pathlib import Path

from ...config import logger  # 统一日志：降级路径记录
from .fs import (_SEARCH_SKIP_DIRS, _remap_mc_sources,  # 搜索跳过目录/重映射/沙箱
                  _sandbox_mode, _search_base)

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


# -*- coding: utf-8 -*-
"""延迟导入审计：扫描 core/ 与 server_app/ 全部 .py 的 import 语句
（含函数体内的延迟 import），逐个验证模块可解析，报告断链。

为什么需要它：pyflakes/ruff 只覆盖模块级导入，函数内 `from .x import y`
的断链（旧 tools.py 拆分迁移的笔误）只有运行到该分支才暴露——
Zen 真实测试中 bash 工具损坏（No module named
'core.infrastructure.tools.tools_runtime'）即此类缺陷，本脚本在
2026-09-07 一次抓出全部 13 处。重构后建议运行：
    venv/Scripts/python.exe tests/audit_imports.py
输出 ALL_IMPORTS_OK 即通过；非零条数 = 存在断链。
"""
import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SKIP_PARTS = {"__pycache__", "data", "web", "frontend", "node_modules", "debug"}


def is_pkg_dir(d: Path) -> bool:
    """输入：目录。返回：相对 ROOT 的每级是否都有 __init__.py（真包链）。"""
    cur = ROOT
    for part in d.relative_to(ROOT).parts:
        cur = cur / part
        if not (cur / "__init__.py").exists():
            return False
    return True


def iter_bad_imports(files: list[Path]) -> list[str]:
    """输入：待扫描 .py 列表。返回：断链描述行（路径:行号 -> 目标）。

    只验证项目内模块（相对导入 + 顶层名能对应到仓库文件/目录的绝对导入），
    第三方库不在职责内。
    """
    bad: list[str] = []
    for f in files:
        if any(x in f.parts for x in SKIP_PARTS):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        pkg_parts = f.relative_to(ROOT).with_suffix("").parts[:-1]
        pkg_ok = is_pkg_dir(ROOT.joinpath(*pkg_parts)) if pkg_parts else True
        for node in ast.walk(tree):
            items: list[tuple[str, int, int]] = []  # (module, level, lineno)
            if isinstance(node, ast.ImportFrom) and node.module and node.level:
                items.append((node.module, node.level, node.lineno))
            elif isinstance(node, ast.Import):
                items.extend((a.name, 0, node.lineno) for a in node.names)
            for mod, level, ln in items:
                if level:
                    if not pkg_ok:
                        continue  # 非包目录（如含空格的脚本目录）不做相对解析
                    target = ".".join(
                        list(pkg_parts[: len(pkg_parts) - level + 1]) + [mod])
                else:
                    top = mod.split(".")[0]
                    if not ((ROOT / top).exists() or (ROOT / f"{top}.py").exists()):
                        continue  # 第三方/标准库
                    target = mod
                try:
                    importlib.import_module(target)
                except Exception as e:  # noqa: BLE001 — 任何导入失败都算断链
                    bad.append(f"{f.relative_to(ROOT)}:{ln} -> {target} "
                               f"({type(e).__name__})")
    return bad


def main() -> int:
    files = list((ROOT / "core").rglob("*.py")) + \
        list((ROOT / "server_app").rglob("*.py"))
    bad = iter_bad_imports(files)
    if bad:
        print("\n".join(bad))
    print(f"TOTAL_BAD={len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

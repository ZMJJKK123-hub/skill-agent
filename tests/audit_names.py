# -*- coding: utf-8 -*-
"""未定义名审计：pyflakes undefined-name 全量扫描（防拆分类回归）。

背景：2026-09-08 真实测试发现函数拆分提取后，被提取函数引用的
符号仍留在原函数的局部 import 里（run_task.DaemonFiles 等），
97 处 undefined name 静态全部漏网——模块级导入审计与 Fake 平价
测试都不覆盖此场景。本工具固化为标准回归项：
    venv/Scripts/python.exe tests/audit_names.py
输出 UNDEFINED_NAMES_OK 即通过。
"""
import subprocess  # 调用 pyflakes（第三方工具，避免重复造轮子）
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    """输入：无。返回：进程退出码（0=通过，1=存在未定义名）。"""
    proc = subprocess.run(
        [sys.executable, "-m", "pyflakes", "core/", "server_app/",
         "tsinghua agent server/"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    undefined = [l for l in (proc.stdout + proc.stderr).splitlines()
                 if "undefined name" in l]
    if undefined:
        print("\n".join(undefined))
    print(f"UNDEFINED_COUNT={len(undefined)}")
    return 1 if undefined else 0


if __name__ == "__main__":
    sys.exit(main())

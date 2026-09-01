# -*- coding: utf-8 -*-
"""新代码生效核验 + 健康监视（只读，不干预）。"""
import io
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BASE = r"C:\Users\59639\Desktop\skill-agent\data\sessions\powerforge_test"
LOG = (sys.argv[1] if len(sys.argv) > 1 else BASE + r"\run.log")

try:
    text = open(LOG, encoding="utf-8", errors="replace").read()
except FileNotFoundError:
    print("LOG_NOT_FOUND:", LOG)
    sys.exit(0)

lines = text.splitlines()
rounds = re.findall(r"\[round\] #(\d+) messages=(\d+) tokens≈(\d+)", text)

# ── 新代码信号 ──
signals = {}
# 1) runtime-context 轮次播报（新代码：Round budget 每轮出现）
ctx_lines = [l for l in lines if "Current runtime context" in l]
budget_lines = [l for l in lines if "Round budget:" in l]
signals["runtime_context_lines"] = len(ctx_lines)
signals["round_budget_report_lines"] = len(budget_lines)
# 2) bash 自估超时
bash_calls = re.findall(r"^\[tool\] bash (\{.*\})", text, re.M)
bash_with_timeout = [b for b in bash_calls if "timeout_seconds" in b]
signals["bash_calls"] = len(bash_calls)
signals["bash_with_timeout"] = len(bash_with_timeout)
if bash_with_timeout:
    vals = re.findall(r'"timeout_seconds":\s*(\d+)', " ".join(bash_with_timeout))
    signals["bash_timeout_values"] = Counter(vals).most_common(6)
# 3) 后台/构建/GameTest 自估超时
bg_calls = [l for l in lines if l.startswith("[tool] run_in_background")]
signals["bg_calls"] = len(bg_calls)
signals["bg_with_timeout"] = sum(1 for l in bg_calls if "timeout_seconds" in l)
build_calls = re.findall(r"^\[tool\] build_mod_jar_forge (\{.*\})", text, re.M)
signals["build_calls"] = len(build_calls)
signals["build_with_timeout"] = sum(1 for l in build_calls if '"timeout"' in l)
gt_calls = re.findall(r"^\[tool\] run_test_gametest (\{.*\})", text, re.M)
signals["gametest_calls"] = len(gt_calls)
signals["gametest_with_timeout"] = sum(1 for l in gt_calls if '"timeout"' in l)
# 4) extend_round_limit
signals["extend_calls"] = text.count("[tool] extend_round_limit")
extend_results = [l for l in lines if "Round budget extended" in l]
signals["extend_results"] = len(extend_results)
# 5) 旧病灶复发检测
signals["dangerous_blocked"] = sum(1 for l in lines if "Error: Dangerous command blocked" in l)
signals["bash30s_timeout"] = sum(1 for l in lines if "Timeout (30s)" in l)
signals["bg600s_timeout"] = sum(1 for l in lines if "timed out (600s)" in l or "timed out (600s)" in l)
signals["unbound_err"] = text.count("UnboundLocalError")
signals["build_timeout_hits"] = re.findall(r"Gradle 构建超时（>(\d+)s）", text)
signals["empty_response_nags"] = sum(1 for l in lines if re.match(r"\s+\[\d+\] user len=\d+ \| <empty-response>", l))
# 6) 预警注入
signals["low_budget_warnings"] = sum(1 for l in lines if "Round budget low" in l)

# ── 进度健康 ──
tools = re.findall(r"^\[tool\] (\S+)", text, re.M)
signals["rounds"] = len(rounds)
signals["last_round"] = rounds[-1] if rounds else None
signals["tool_calls"] = len(tools)
signals["tool_dist"] = Counter(tools).most_common(12)
for m, n in [("BUILD SUCCESSFUL", "build_ok"), ("All 1 required tests passed", "gametest_pass_1"),
             ("All required tests passed", "gametest_pass"), ("RESULT: PASS", "result_pass"),
             ("完成，最终回复", "finished")]:
    if m in text:
        signals[n] = text.count(m)
dist = None
import os
d = BASE + r"\mod\dist"
if os.path.isdir(d):
    dist = os.listdir(d)
signals["dist"] = dist

for k, v in signals.items():
    print(f"{k}: {v}")
print("--- tail 6 ---")
for l in lines[-6:]:
    print(l[:170])

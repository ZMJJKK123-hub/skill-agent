# -*- coding: utf-8 -*-
"""skyrealm 会话监视。"""
import io, sys, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
text = open(r"data\sessions\skyrealm_test\run.log", encoding="utf-8", errors="replace").read()
lines = text.splitlines()
rounds = re.findall(r"\[round\] #(\d+) messages=(\d+) tokens≈(\d+)", text)
tools = re.findall(r"^\[tool\] (\S+)", text, re.M)
print("rounds:", len(rounds), "tools:", len(tools), Counter(tools).most_common(10))
print("budget_broadcast:", sum(1 for l in lines if "Round budget:" in l))
m = re.findall(r"Round budget: (\d+)/(\d+)", text)
print("latest_budget:", m[-1] if m else None)
print("empty_nags:", sum(1 for l in lines if re.match(r"\s+\[\d+\] user len=\d+ \| <empty-response>", l)))
print("extend_calls:", text.count("[tool] extend_round_limit"))
print("low_budget_warn:", text.count("Round budget low"))
print("bg_build:", sum(1 for l in lines if l.startswith("[tool] build_mod_jar_forge") and "background" in l))
bt = re.findall(r'"timeout_seconds":\s*(\d+)', text)
print("bash_timeouts_used:", Counter(bt).most_common(6))
bto = re.findall(r"^\[tool\] build_mod_jar_forge (\{.*\})", text, re.M)
for b in bto[-3:]:
    print("build_call:", b[:120])
gto = re.findall(r"^\[tool\] run_test_gametest (\{.*\})", text, re.M)
print("gametest_calls:", len(gto), "with_timeout:", sum(1 for g in gto if '"timeout"' in g))
for pat in ["BUILD SUCCESSFUL", "RESULT: PASS", "RESULT: FAIL", "完成，最终回复",
            "Round budget low", "强制收尾", "Max total", "All 1 required tests passed",
            "All 8 required tests passed", "All 9 required tests passed"]:
    n = text.count(pat)
    if n: print(f"MARKER {pat}: {n}")
import os
d = r"data\sessions\skyrealm_test\mod\dist"
print("dist:", os.listdir(d) if os.path.isdir(d) else None)
print("--- tail ---")
for l in lines[-5:]:
    print(l[:175])

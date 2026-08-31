# -*- coding: utf-8 -*-
"""精简轮询：只输出轮次统计、最新工具调用、关键里程碑。"""
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LOG = r"C:\Users\59639\Desktop\skill-agent\data\sessions\gemcraft_glm53_test\run.log"

text = open(LOG, "r", encoding="utf-8", errors="replace").read()
lines = text.splitlines()

rounds = re.findall(r"\[round\] #(\d+) messages=(\d+) tokens≈(\d+)", text)
tools = re.findall(r"^\[tool\] (\S+)", text, re.M)
fails = [l for l in lines if l.startswith("[tool-result] failed")]

print(f"rounds={len(rounds)} last={rounds[-1] if rounds else None} tool_calls={len(tools)} failed={len(fails)}")

from collections import Counter
print("tool usage:", dict(Counter(tools).most_common(12)))

for marker in ["BUILD SUCCESSFUL", "构建成功", "All required tests passed", "RESULT: PASS",
               "dist/", "MOD jar exists", "gametest-check FAILED", "write-first-stop",
               "build-now-stop", "auto_compact", "[CONCLUDED]", "GameTest 打回", "强制收尾"]:
    n = text.count(marker)
    if n:
        print(f"MARKER x{n}: {marker}")

print("--- last 12 [reply]/[tool]/[gametest]/[build] lines ---")
shown = 0
for l in reversed(lines):
    if any(l.startswith(p) for p in ("[reply]", "[tool]", "[gametest]", "[build]", "[run_task]", "MARKER")) or "[build]" in l[:40]:
        print(l[:200])
        shown += 1
        if shown >= 12:
            break

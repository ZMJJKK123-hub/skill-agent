# -*- coding: utf-8 -*-
"""一次性拆分：最后 3 个函数收尾（用后即删）。"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def patch(f, pairs):
    p = Path(f)
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (f, old[:60])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print(f"patched {f}")


# 1) validate：blockstates 分支提取
patch("core/infrastructure/tools/validate.py", [
    ('''    # Blockstate JSON: assets/<modid>/blockstates/<name>.json
    if "assets" in parts and "blockstates" in parts and len(parts) >= 4 and parts[parts.index("assets") + 1] == modid:
        variants = (data or {}).get("variants")
        if isinstance(variants, dict):
            for state, v in variants.items():
                if isinstance(v, dict) and isinstance(v.get("model"), str):
                    _check_model_ref(base, v["model"], modid, errors, rel)
                elif isinstance(v, list):
                    for entry in v:''',
     '''    _validate_blockstate_json(base, rel, parts, modid, data, errors)'''),
])
# 该分支剩余体（list entry 内层）需要一并看——先读文件确认替换边界完整
s = Path("core/infrastructure/tools/validate.py").read_text(encoding="utf-8")
print(s[s.index("_validate_blockstate_json(base, rel"):s.index("_validate_blockstate_json(base, rel")+400])

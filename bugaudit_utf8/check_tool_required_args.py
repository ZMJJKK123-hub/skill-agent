"""妫�鏌� handler 涓�閫氳繃 kw["x"] 寮哄埗鍙栧�肩殑鍙傛暟锛屾槸鍚﹂兘鍦� schema 鐨� required 閲屻��

鍙�璇绘��鏌ワ紝涓嶄慨鏀圭幇鏈夋簮鐮併��
"""
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import tools


def get_schema(name):
    for t in tools.TOOLS:
        if t["function"]["name"] == name:
            return t["function"]["parameters"]
    return None


def extract_strict_keys(src):
    keys = set()
    keys.update(re.findall(r'kw\["([^"]+)"\]', src))
    keys.update(re.findall(r"kw\['([^']+)'\]", src))
    return keys


def main():
    issues = []
    for name, handler in sorted(tools.TOOL_HANDLERS.items()):
        if name == "task":
            continue
        try:
            src = inspect.getsource(handler)
        except Exception:
            continue
        strict = extract_strict_keys(src)
        if not strict:
            continue
        schema = get_schema(name)
        if schema is None:
            continue
        required = set(schema.get("required", []))
        non_required = strict - required
        if non_required:
            issues.append((name, sorted(non_required), sorted(required)))

    if not issues:
        print("No handler uses kw[...] on non-required schema args.")
    else:
        for name, non_required, required in issues:
            print(f"[STRICT-NOT-REQUIRED] tool={name}")
            print(f"  strict keys: {non_required}")
            print(f"  schema required: {required}")


if __name__ == "__main__":
    main()
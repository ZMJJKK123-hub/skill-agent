"""妫�鏌� core/tools.py 涓� TOOL_HANDLERS 瀹為檯璇诲彇鐨� kw 鍙傛暟鏄�鍚﹂兘鍖呭惈鍦� TOOLS schema 涓�銆�

鍙�璇绘��鏌ワ紝涓嶄慨鏀逛换浣曠幇鏈夋簮鐮併��
"""
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import tools


def get_schema_props(name):
    for t in tools.TOOLS:
        if t["function"]["name"] == name:
            props = t["function"]["parameters"].get("properties", {})
            required = t["function"]["parameters"].get("required", [])
            return set(props.keys()), set(required)
    return set(), set()


def extract_kw_keys(src):
    keys = set()
    keys.update(re.findall(r'kw\["([^"]+)"\]', src))
    keys.update(re.findall(r"kw\['([^']+)'\]", src))
    keys.update(re.findall(r'kw\.get\("([^"]+)"', src))
    keys.update(re.findall(r"kw\.get\('([^']+)'", src))
    return keys


def main():
    # task 鍦� agent.py 閲屾帴绾匡紝妫�鏌ユ椂鍙�鑳藉瓨鍦�锛涜繖閲岀壒娈婂�勭悊
    issues = []
    for name, handler in sorted(tools.TOOL_HANDLERS.items()):
        if name == "task":
            continue
        try:
            src = inspect.getsource(handler)
        except Exception as e:
            print(f"[skip] {name}: cannot get source: {e}")
            continue
        keys = extract_kw_keys(src)
        if not keys:
            continue
        props, required = get_schema_props(name)
        missing = keys - props
        if missing:
            issues.append((name, sorted(missing), sorted(keys), sorted(props)))

    if not issues:
        print("No missing schema props found in TOOL_HANDLERS kw access.")
    else:
        for name, missing, keys, props in issues:
            print(f"[MISMATCH] tool={name}")
            print(f"  handler uses: {keys}")
            print(f"  schema props: {props}")
            print(f"  missing in schema: {missing}")


if __name__ == "__main__":
    main()
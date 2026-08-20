"""楠岃瘉 log_events._parse_run_block 鏄�鍚﹀湪 [tool-result] 鍚庝涪澶辩揣閭讳簨浠惰�屻��

鍙�璇婚獙璇侊紝涓嶄慨鏀逛换浣曟枃浠躲��
"""
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "server_app"))

from log_events import _parse_run_block


def main():
    text = """[tool] bash echo hi
[tool-result] success
output line
[鎬濊�僝 next thought
"""
    events = _parse_run_block(text)
    for ev in events:
        print(ev["type"], "|", ev["content"][:40])
    types = [ev["type"] for ev in events]
    if "thinking" not in types:
        print("RESULT: THINKING EVENT LOST (bug confirmed)")
    else:
        print("RESULT: no loss")


if __name__ == "__main__":
    main()
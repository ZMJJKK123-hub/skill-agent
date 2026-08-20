"""楠岃瘉 auth_store.register 鏄�鍚﹀厑璁哥敤鎴峰悕閫犳垚鍘嗗彶鏂囦欢璺�寰勭┛瓒娿��

鍙�璇婚獙璇侊細鎶� auth_store 鐨� DATA_DIR 鎸囧悜涓存椂鐩�褰曪紝涓嶈Е纰扮湡瀹� data銆�
"""
import os
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "server_app"))

import auth_store


def main():
    tmp = Path(tempfile.mkdtemp(prefix="auth_race_"))
    # 閲嶅畾鍚戝埌涓存椂鐩�褰�
    auth_store.DATA_DIR = tmp
    auth_store.HISTORY_DIR = tmp / "history"
    auth_store.USERS_FILE = tmp / "users.json"
    auth_store.SESSIONS_FILE = tmp / "auth_sessions.json"
    auth_store.HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    name = "../evil"
    try:
        auth_store.register(name, "password123")
        auth_store.upsert_history(name, {"sessionId": "s1", "prompt": "x"})
    except Exception as e:
        print("register raised:", type(e).__name__, e)
        print("RESULT: blocked")
        return

    outside = tmp / "evil.json"          # 棰勬湡瓒婄晫浣嶇疆
    print("tmp:", tmp)
    print("history dir:", auth_store.HISTORY_DIR)
    print("outside exists:", outside.exists())
    if outside.exists():
        print("RESULT: PATH TRAVERSAL CONFIRMED")
    else:
        print("RESULT: no traversal observed")


if __name__ == "__main__":
    main()
"""楠岃瘉 server.py _purge_session_dir 瀵� session_id 鏈�鍋氳矾寰勬牎楠岀殑闂�棰樸��

浣跨敤涓存椂鐩�褰曪紝涓嶈Е纰扮湡瀹� data銆�
"""
import os
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "server_app"))

import server


def main():
    tmp = Path(tempfile.mkdtemp(prefix="srv_path_"))
    sessions = tmp / "sessions"
    sessions.mkdir()
    marker = tmp / "marker.txt"
    marker.write_text("do-not-delete", encoding="utf-8")

    # 妯℃嫙 _purge_session_dir("..")锛氫細璇濅笉瀛樺湪鏃惰皟鐢ㄦ柟浼氳蛋鍒拌繖閲�
    server.SESSIONS_DIR = sessions
    server._purge_session_dir("..")

    print("tmp exists:", tmp.exists())
    print("sessions exists:", sessions.exists())
    print("marker exists:", marker.exists())
    if not tmp.exists() or not marker.exists():
        print("RESULT: PATH TRAVERSAL / ARBITRARY DELETE CONFIRMED")
    else:
        print("RESULT: no deletion observed")


if __name__ == "__main__":
    main()
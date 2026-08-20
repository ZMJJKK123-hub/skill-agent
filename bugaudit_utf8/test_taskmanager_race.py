"""楠岃瘉 TaskManager.create() 鍦ㄥ�氱嚎绋嬪苟鍙戜笅鏄�鍚︿細浜х敓閲嶅�� task_id銆�

鍙�鍋氶獙璇侊紝涓嶄慨鏀逛换浣曠幇鏈夋簮鐮併��
"""
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools_tasks import TaskManager


def main():
    tmp = tempfile.mkdtemp(prefix="task_race_")
    tm = TaskManager(task_dir=tmp)
    results = []
    barrier = threading.Barrier(2)

    def worker(tag):
        barrier.wait()
        ids = []
        for i in range(50):
            t = tm.create(f"{tag}-{i}")
            ids.append(t.get("id"))
        results.append(ids)

    threads = [threading.Thread(target=worker, args=(f"t{i}",)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    a, b = results
    dup = sorted(set(a) & set(b))
    all_ids = a + b
    dup_within = len(all_ids) - len(set(all_ids))
    print("thread0 ids:", a[:5], "...")
    print("thread1 ids:", b[:5], "...")
    print("dup across threads:", dup[:10], "count=", len(dup))
    print("total duplicate ids in combined:", dup_within)
    if dup:
        print("RESULT: RACE CONFIRMED")
    else:
        print("RESULT: no race observed this run")


if __name__ == "__main__":
    main()
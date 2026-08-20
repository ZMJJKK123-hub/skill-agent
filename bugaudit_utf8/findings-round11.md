# Bug Audit Round 11

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 22锛堜腑锛夛細`MessageBus.read_inbox` 閬囨崯鍧� JSON 琛屼細鐩存帴宕╂簝

鏂囦欢锛歚core/tools_team.py`

```python
def read_inbox(self, name: str) -> list:
    ...
    lines = f.readlines()
    ...
    msgs = [json.loads(l) for l in lines if l.strip()]
```

娌℃湁瀵瑰崟琛� JSON 鍋� try/except銆傚�傛灉 `.team/inbox/<name>.jsonl` 鏌愪竴琛屽啓鍏ヤ腑鏂�/鎹熷潖锛宍json.loads` 鎶涘紓甯革紝鏁翠釜闃熷弸绾跨▼浼氬穿銆�

褰卞搷锛�
- 闃熷弸 Agent 鍥犱竴灏佸潖娑堟伅閫�鍑�
- 鍚庣画浠诲姟鏃犳硶缁х画

---

## 鍙戠幇 23锛堜腑锛夛細`TodoManager` 娌℃湁閿侊紝澶氶槦鍙嬪苟鍙戞洿鏂� todo 鍙�鑳戒簰鐩歌�嗙洊

鏂囦欢锛歚core/tools_tasks.py`

- `TodoManager.update()` 鐩存帴 `self.todos = items` + `_save()`
- 娌℃湁 `threading.Lock`

鍦ㄥ�氫釜 teammate 绾跨▼骞惰�屽伐浣滄椂锛屼袱涓�绾跨▼鍚屾椂璋冪敤 `todo` 宸ュ叿鍙�鑳戒簰鐩歌�嗙洊瀵规柟鍒楄〃锛屾垨鍐欏潖 `.todo.json`銆�

---

## 璇存槑

- 鍚庣��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round11.md`
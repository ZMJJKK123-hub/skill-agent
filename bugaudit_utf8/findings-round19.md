# Bug Audit Round 19

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 33锛堜綆锛夛細`run_bash` 鐨勫嵄闄╁懡浠よ繃婊ゆ妸鏅�閫氬崟璇� `format` 涔熸嫤鎴�

鏂囦欢锛歚core/tools_shell.py`

```python
dangerous = ["format", "diskpart", "reg delete", "shutdown", ...]
if any(d in command.lower() for d in dangerous):
    return "Error: Dangerous command blocked"
```

闂�棰橈細
- 浣跨敤瀛愪覆鍖归厤 `"format" in command.lower()`
- 鍛戒护濡� `echo format string`銆乣python format.py`銆乣grep format` 閮戒細琚�璇�鍒や负鍗遍櫓鍛戒护骞舵嫤鎴�
- 鍚屾牱 `shutdown` 瀛愪覆浼氳��浼� `shutdown_teammate`? 閭ｆ槸宸ュ叿鍚嶏紝涓嶆槸 shell 鍛戒护锛涗絾 shell 閲� `echo shutdown` 涔熶細琚�鎷�

褰卞搷锛�
- 姝ｅ父鍛戒护琚�璇�鎷︽埅
- 灞炰簬璇�鎶�/鍔熻兘鍙楅檺闂�棰橈紝涓嶆槸瀹夊叏婕忔礊

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round19.md`
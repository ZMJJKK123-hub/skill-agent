# Bug Audit Round 15

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 30锛堜腑锛夛細閲嶅�� spawn 涓�涓� idle 闃熷弸浼氬惎鍔ㄩ噸澶嶇嚎绋嬶紝鏃х嚎绋嬫湭鍋滄��

鏂囦欢锛歚core/tools_team.py` 鈫� `TeammateManager.spawn()`

```python
if name in self.team:
    if self.team[name].status == "shutdown":
        ...
    elif self.team[name].status == "idle":
        self.team[name].system_prompt = system_prompt
        self._save_team_config()
        logger.info(f"Teammate {name} 宸插瓨鍦�(idle)锛岄噸鍚�绾跨▼")
    else:
        return error
thread = threading.Thread(target=self._teammate_loop, args=(name,), daemon=True)
self.threads[name] = thread
thread.start()
```

褰撻槦鍙嬬姸鎬佷负 `idle` 鏃讹細
- 鏃х嚎绋嬪叾瀹炶繕鍦� `_teammate_loop` 閲岃疆璇㈡敹浠剁��/鐪嬫澘锛坕dle 绾跨▼瀛樻椿鏈�闀� 60 绉掞級
- 杩欓噷娌℃湁鍋滄�㈡棫绾跨▼锛屽張鐩存帴 `start()` 涓�涓�鏂扮嚎绋�

缁撴灉锛�
- 鍚屼竴涓�闃熷弸鍚嶅悓鏃跺瓨鍦ㄤ袱涓�绾跨▼
- 涓や釜绾跨▼閮戒細璇诲悓涓�涓�鏀朵欢绠便�佽�ら�嗗悓涓�涓�浠诲姟鏉匡紝鍙�鑳介噸澶嶅�勭悊浠诲姟

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- spawn idle 鏃跺厛 `shutdown(name)` 骞� `join` 鏃х嚎绋嬶紝鎴栬�剧疆鍋滄��浜嬩欢锛屽啀鍚�鍔ㄦ柊绾跨▼銆�

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round15.md`
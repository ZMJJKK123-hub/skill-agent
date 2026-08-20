# Bug Audit Round 26

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 40锛堜腑锛夛細`cleanup_workspace` 涓嶉伒瀹� read-only 娌欑�憋紝浠嶅彲鍒犻櫎鏂囦欢

鏂囦欢锛歚core/tools_cleanup.py`

```python
def cleanup_workspace(mode="cache"):
    ...
    for name in dirs_to_remove:
        if p.is_dir():
            _rmtree(p)
    ...
```

- 娌℃湁妫�鏌� `_sandbox_mode()`
- 鍗充娇娌欑�辫�句负 `read-only`锛宍cleanup_workspace` 浠嶈兘鍒犻櫎 `build/`銆乣.gradle/`銆佺敋鑷� `run/`銆乣.tasks/` 绛夌洰褰�

褰卞搷锛�
- 涓庘�滃彧璇绘矙绠扁�濊��涔夊啿绐�
- 濡傛灉鏈�鏉� 8001 鍒囨垚 read-only 妯″紡锛宎gent 浠嶅彲閫氳繃璇ュ伐鍏峰垹闄ゆ枃浠�
- 褰撳墠 8001 鏄� workspace-write锛屽奖鍝嶆湁闄愶紝浣嗗睘浜庢矙绠变竴鑷存�� bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round26.md`
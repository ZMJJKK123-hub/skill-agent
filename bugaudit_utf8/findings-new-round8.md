# New Bug Audit Round 8

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 53锛堥珮锛夛細`run_bash` 鐨勮秺鐣屾��娴嬪彲鐢ㄥ紩鍙风粫杩囷紝`cd ".."` 閫冨嚭宸ヤ綔鍖�

鏂囦欢锛歚core/tools_shell.py` 鈫� `_escapes_workspace()`

```python
def _escapes_workspace(command: str) -> bool:
    return bool(re.search(r"\b(?:cd|pushd)\s+(?:\.\.|[/\\]|[a-z]:)", command.lower()))
```

妫�娴嬭�佹眰 `cd` 鍚庣揣璺� `..` 鎴栫粷瀵硅矾寰�/鐩樼�︼紝浣嗭細
- `cd ".."`锛歚cd` 鍚庢槸寮曞彿锛屾�ｅ垯涓嶅尮閰�
- `cd '..'`锛氬悓鏍蜂笉鍖归厤
- `cd .. &&` 浼氳��鎷︼紝浣嗗姞寮曞彿灏辩粫杩�

褰卞搷锛�
- `workspace-write` 娌欑�变笅 agent 鍙�鎵ц�� `cd ".."` 杩涘叆宸ヤ綔鍖哄�栫洰褰�
- 鍐嶉厤鍚� `write_file`/`bash` 閲嶅畾鍚戝嵆鍙�淇�鏀归」鐩�鏍规垨鍏朵粬鐩�褰�
- 涓� `run_in_background` 缁曡繃绫讳技锛屾槸娌欑�辫竟鐣屽け鏁�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
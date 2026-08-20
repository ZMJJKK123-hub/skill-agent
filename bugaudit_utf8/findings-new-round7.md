# New Bug Audit Round 7

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 52锛堥珮锛夛細澶氫釜宸ュ叿鍙�閫氳繃 `log_path` 鍙傛暟璇诲彇宸ヤ綔鍖哄�栦换鎰忔枃浠讹紝缁曡繃娌欑��

娑夊強鏂囦欢/鍑芥暟锛�
- `core/tools_gametest.py` 鈫� `parse_gametest_results(log_path=...)`
- `core/tools_wait.py` 鈫� `tail_log(log_path=...)`銆乣wait_for_log(log_path=...)`
- `core/tools_loop.py` 鈫� `parse_build_output(log_path=...)`

杩欎簺鍑芥暟澶ч兘锛�
```python
path = Path(log_path) if log_path else Path(base) / "run/logs/latest.log"
if not path.is_absolute():
    path = Path(base) / path
...
path.read_text(...)
```

娌℃湁浣跨敤 `safe_path`锛屼篃娌℃湁鏍￠獙鐩�鏍囧繀椤诲湪宸ヤ綔鍖哄唴銆�

褰卞搷锛�
- 鍦� `workspace-write` 娌欑�变笅锛宎gent 浠嶅彲閫氳繃 `tail_log(log_path="/etc/passwd")` 璇诲彇浠绘剰鏂囦欢鍐呭��
- 鎴栬�诲叾浠栭」鐩�鐩�褰�/绯荤粺鏂囦欢
- 灞炰簬娌欑�卞彧璇婚�冮�� + 淇℃伅娉勯湶椋庨櫓

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 瀵� `log_path` 缁熶竴璧� `safe_path()` 骞堕檺鍒跺湪宸ヤ綔鍖哄唴

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
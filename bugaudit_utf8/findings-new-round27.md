# New Bug Audit Round 27

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 73锛堜綆锛夛細`read_crash_report` 鍏ㄩ噺璇绘枃浠跺悗鍐嶅彇澶撮儴

鏂囦欢锛歚core/tools_crash.py`

```python
text = path.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
head = lines[:max_lines]
```

- 鍗充娇鍙�瑕佸墠 120 琛岋紝涔熶細鍏堟暣涓�璇诲叆鏂囦欢
- 瓒呭ぇ crash report 鏃舵氮璐瑰唴瀛�

褰卞搷锛氫綆锛屼笌 `parse_build_output` 鍚岀被銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
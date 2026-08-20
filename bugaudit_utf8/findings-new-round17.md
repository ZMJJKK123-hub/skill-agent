# New Bug Audit Round 17

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 63锛堜綆锛夛細`run_mod_test_cycle` 鐨� `build_timeout` 鍙傛暟鏈�鐢熸晥

鏂囦欢锛歚core/tools_loop.py` 鈫� `run_mod_test_cycle()`

```python
def run_mod_test_cycle(..., build_timeout=900, test_timeout=180, ...):
    ...
    if build:
        b = _forge_build_jar({"gradle_task": "build"})
```

- `build_timeout` 琚�鎺ユ敹浣嗕粠鏈�浼犵粰 `_forge_build_jar`
- `_forge_build_jar` 鍐呴儴鍥哄畾 900 绉掕秴鏃�
- `test_timeout` 鍊掓槸浼犵粰浜� GameTest

褰卞搷锛�
- 璋冪敤鏂规棤娉曡皟鏁存瀯寤鸿秴鏃�
- 鍙傛暟鏃犳晥/璇�瀵�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
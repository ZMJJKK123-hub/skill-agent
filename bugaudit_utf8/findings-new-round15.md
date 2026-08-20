# New Bug Audit Round 15

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 61锛堜綆锛夛細`run_mod_test_cycle` 瀵规瀯寤哄け璐ヨ瘑鍒�涓嶅畬鏁�

鏂囦欢锛歚core/tools_loop.py`

```python
if "[build] Gradle 鏋勫缓澶辫触" in b or "BUILD FAILED" in b:
    result_ok = False
```

- 鍙�璇嗗埆杩欎袱绉嶅け璐ユ爣璁�
- 濡傛灉 `_forge_build_jar` 杩斿洖鍏朵粬澶辫触鏂囨湰锛堝�傝秴鏃躲�佹壘涓嶅埌 gradlew銆佸�嶅埗 jar 澶辫触锛夛紝`result_ok` 涓嶄細鍙� False
- 鍙�鑳借��鎶� PASS

褰卞搷锛氭祴璇曞惊鐜�瀵归儴鍒嗘瀯寤哄け璐ユ紡鎶ャ��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
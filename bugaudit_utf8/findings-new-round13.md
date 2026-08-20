# New Bug Audit Round 13

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 59锛堜腑锛夛細`run_mod_test_cycle` 鏈�璇嗗埆 `validate_resources` 鐨勯敊璇�杩斿洖锛屽彲鑳借��鎶� PASS

鏂囦欢锛歚core/tools_loop.py`

```python
v = validate_resources(modid)
out.append(v)
if "RESULT: FAIL" in v:
    result_ok = False
```

- `validate_resources` 鍦ㄦ棤娉曡嚜鍔ㄨ瘑鍒� modid 绛夐敊璇�鏃惰繑鍥� `"Error: cannot auto-detect modid..."`锛屽叾涓�涓嶅寘鍚� `"RESULT: FAIL"`
- 鍥犳�� `result_ok` 涓嶄細鍙� False
- 鍚庣画 build/test 鍗充娇鎴愬姛锛屾渶缁堜粛鍙�鑳借緭鍑� `RESULT: PASS`

褰卞搷锛�
- 璧勬簮鏍￠獙澶辫触浣嗘暣浣撴祴璇曞惊鐜�鏄剧ず閫氳繃
- 婕忔姤闂�棰�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 璇嗗埆 `v.startswith("Error")` 鎴� `"RESULT: FAIL"` / `"ERRORS:"` 绛夊け璐ヤ俊鍙�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
# New Bug Audit Round 1

> 鏂颁竴杞�鎸佺画宸℃煡锛屽彧璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 43锛堜腑锛夛細`_SEARCH_SKIP_DIRS` 鍖呭惈 `mc_java_sources`锛屼笌娉ㄩ噴鈥滃惈 mc_java_sources鈥濈煕鐩�

鏂囦欢锛歚core/tools_fs.py` 73-80

```python
# grep/glob锛氱洿鎺ユ悳宸ヤ綔鍖烘枃浠讹紙鍚� mc_java_sources銆乻kills銆佺敓鎴愪唬鐮侊級锛�
_SEARCH_SKIP_DIRS = {
    ...
    "mc_java_sources",
}
```

闂�棰橈細
- 娉ㄩ噴鏄庣‘璇� grep/glob 浼氭悳 `mc_java_sources`
- 浣� `_SEARCH_SKIP_DIRS` 鎶� `mc_java_sources` 鍔犲叆璺宠繃鐩�褰�
- `run_glob` 璺�寰勪腑鍑虹幇 `mc_java_sources` 鏃朵細琚�璺宠繃锛屾棤娉� glob MC 婧愮爜
- `run_grep` 浠ユ暣涓�宸ヤ綔鍖轰负鏍规椂锛宍mc_java_sources` 瀛愮洰褰曚細琚� `os.walk` 鍓�鏋濓紝鎼滀笉鍒伴噷闈㈠唴瀹�
- 鍙�鏈夋樉寮忎紶 `path="mc_java_sources"`锛堜緥濡� `search_api`锛夋椂鏍圭洰褰曟湰韬�涓嶈��鍓�鏋濓紝鎵嶈兘鎼滃埌

褰卞搷锛�
- 閫氱敤 `grep`/`glob` 琛屼负涓庢敞閲婁笉绗�
- 鐢ㄦ埛/妯″瀷浠ヤ负鑳芥悳 MC 婧愮爜锛屽疄闄呭ぇ閮ㄥ垎鎯呭喌鎼滀笉鍒�
- 灞炰簬鈥滄敞閲婃壙璇鸿兘鍔涗笌瀹為檯瀹炵幇涓嶄竴鑷粹�濈殑 bug

---

## 璇存槑

- 杩欐槸鏂颁竴杞�鐩�鏍囩殑绗�涓�浠芥姤鍛�
- 鍚庣画鍙戠幇缁х画鏀惧湪 `bugaudit/` 涓�
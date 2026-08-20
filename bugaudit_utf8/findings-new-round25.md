# New Bug Audit Round 25

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 71锛堜綆锛夛細`mc_status` / `wait_for_mc_ready` 瀵� manifest 鎭㈠�嶇殑瀛ゅ効杩涚▼涓嶅畬鏁存劅鐭�

鏂囦欢锛歚core/tools_lifecycle.py`銆乣core/tools_wait.py`

- `mc_status` 浣跨敤 `process_manager.list_info(base)`锛岃兘鐪嬪埌 manifest 瀛ゅ効
- 浣� `wait_for_mc_ready(handle)` 浣跨敤 `process_manager.get(handle)`锛堝彧鏌ュ唴瀛� `_PROCESSES`锛夛紝鐪嬩笉鍒� manifest 瀛ゅ効
- 鏈嶅姟閲嶅惎鍚庯紝`wait_for_mc_ready("mc-server")` 鍙�鑳戒竴鐩寸瓑鍒拌秴鏃讹紝灏界�¤繘绋嬪疄闄呮椿鐫�

褰卞搷锛氶噸鍚�鍚庡�瑰�ゅ効杩涚▼鐨勭瓑寰�/鐘舵�佸垽鏂�涓嶅畬鏁淬��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
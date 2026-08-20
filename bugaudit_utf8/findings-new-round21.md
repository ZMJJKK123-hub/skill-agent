# New Bug Audit Round 21

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 67锛堜綆锛夛細`start_mc_server` 浣跨敤鍥哄畾榛樿�� RCON 瀵嗙爜 `forge123`

鏂囦欢锛歚core/tools_lifecycle.py` 鈫� `_ensure_rcon_props()`

```python
if not password:
    password = "forge123"
```

- 鏈�鎻愪緵 RCON 瀵嗙爜鏃跺啓鍏ュ浐瀹氶粯璁ゅ瘑鐮�
- 鑻ユ湇鍔″櫒鏆撮湶鍏�缃戯紝RCON 绔�鍙ｅ彲鑳借��鐚滄祴瀵嗙爜

褰卞搷锛�
- 瀹夊叏榛樿�ゅ�艰杽寮�
- 寮�鍙戝満鏅�褰卞搷浣庯紝浣嗗叕缃戦儴缃叉湁椋庨櫓

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
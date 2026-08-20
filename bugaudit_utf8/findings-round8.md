# Bug Audit Round 8

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 19锛堥珮锛屽凡楠岃瘉锛夛細娉ㄥ唽鐢ㄦ埛鍚嶆湭鍋氳矾寰勫畨鍏ㄦ牎楠岋紝鍙�瀵艰嚧鍘嗗彶鏂囦欢璺�寰勭┛瓒�

鏂囦欢锛歚server_app/auth_store.py`

`register()` 鍙�鏍￠獙锛�
```python
if not name: raise ...
if len(name) > 32: raise ...
if len(password) < 6: raise ...
```

娌℃湁闄愬埗 `/`銆乣\`銆乣..` 绛夊瓧绗︺��

鑰屽巻鍙叉枃浠跺悕鐩存帴鎷兼帴鐢ㄦ埛鍚嶏細
```python
def _history_path(username: str) -> Path:
    return HISTORY_DIR / f"{username}.json"
```

濡傛灉鐢ㄦ埛娉ㄥ唽鍚嶄负锛�
```
../evil
```
閭ｄ箞鍘嗗彶鏂囦欢浼氬啓鍒帮細
```
data/history/../evil.json
```
鍗� `data/evil.json`锛岃秺鍑轰簡鐢ㄦ埛鍘嗗彶鐩�褰曘��

褰卞搷锛�
- 璺�寰勭┛瓒婇�庨櫓
- 澶氱敤鎴峰満鏅�涓嬪彲浠ヨ�诲啓鍒伴�勬湡涔嬪�栫殑鏂囦欢
- 缃戦〉绔�鏄�鍏�寮�鏈嶅姟锛岃繖鏄�鐪熷疄瀹夊叏闂�棰�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 娉ㄥ唽鏃堕檺鍒剁敤鎴峰悕涓� `[A-Za-z0-9_-]+`锛堟垨鑷冲皯绂佹�� `/`銆乣\`銆乣..`锛�
- 鎴栧巻鍙叉枃浠跺悕浣跨敤 sessionId/鍝堝笇锛岃�屼笉鏄�鐩存帴鎷兼帴鐢ㄦ埛鍚�

楠岃瘉锛�
- 鏂板�� `bugaudit/test_auth_store_path_traversal.py`
- 瀹炴祴娉ㄥ唽 `../evil` 鍚庯紝`evil.json` 鍑虹幇鍦ㄩ�勬湡鍘嗗彶鐩�褰�**涔嬪��**锛岀‘璁よ矾寰勭┛瓒婃垚绔嬨��

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round8.md`
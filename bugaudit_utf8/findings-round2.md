# Bug Audit Round 2

> 鏈�杞�鍙�璇诲贰鏌� + 鏂板�為獙璇佹祴璇曪紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 5锛堥珮锛屽凡楠岃瘉锛夛細TaskManager.create() 骞跺彂浼氬垱寤洪噸澶� task_id

鏂囦欢锛歚core/tools_tasks.py`

`TaskManager.create()` 娌℃湁浣跨敤 `self._lock`锛�
```python
def create(self, subject, blocked_by=None):
    ...
    task = {"id": self._next_id, ...}
    ...
    self._write_task(task)
    self._next_id += 1
```

楠岃瘉鏂瑰紡锛氭柊澧� `bugaudit/test_taskmanager_race.py`锛岀敤 2 涓�绾跨▼鍚勫垱寤� 50 涓�浠诲姟銆�

缁撴灉锛�
- 涓や釜绾跨▼鍑虹幇閲嶅�� task_id锛歚[1, 3, 11, 20, 22, 34, 58, 65]`
- 鍚堣�￠噸澶� 8 涓� ID

褰卞搷锛�
- agent 澶氫釜 teammate / 澶氱嚎绋嬪苟鍙戝垱寤轰换鍔℃椂锛屼换鍔� ID 浼氬啿绐侊紝瀵艰嚧浠诲姟浜掔浉瑕嗙洊鎴栫姸鎬侀敊涔便��
- 杩欐槸鐪熷疄鐨勫苟鍙� bug锛屼笉鏄�鐞嗚�洪棶棰樸��

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦� `create()` 鍐呭姞 `with self._lock:`锛屾妸璇诲彇 `_next_id`銆佸啓鏂囦欢銆佽嚜澧炴斁鍒伴攣鍐呫��

---

## 鍙戠幇 6锛堜腑锛夛細妯℃澘鐗堟湰涓� MC 婧愮爜鐗堟湰涓嶅尮閰�

鏂囦欢锛歚server_app/server.py` 鈫� `_copy_template()`

```python
if version.startswith("26.2"):
    mc_sources = PROJECT_ROOT / "mc_java_sources_26.2"
else:
    mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
```

浣嗗�傛灉鐢ㄦ埛閫夋嫨 `forge-1.21.9` 鎴� `forge-1.21.10`锛屼唬鐮佷粛鐒跺�嶅埗 `mc_java_sources_1.21.11` 浣滀负鍙傝�冩簮鐮併��

褰卞搷锛�
- agent 鍦� 1.21.9/1.21.10 浼氳瘽涓�鏌ュ埌鐨� API/绫诲悕鍙�鑳芥潵鑷� 1.21.11锛屽�艰嚧閿欒��鍐欐硶銆�
- 椤圭洰鐩�鍓嶄篃缂哄皯 `mc_java_sources_1.21.9` / `mc_java_sources_1.21.10` 鐩�褰曘��

---

## 鍙戠幇 7锛堜腑锛夛細auth_store JSON 鍐欐枃浠舵棤閿�

鏂囦欢锛歚server_app/auth_store.py`

`_save_json()` 鐩存帴 `write_text`锛屾病鏈夋枃浠堕攣/鍘熷瓙鍐欍�傚�氫釜璇锋眰鍚屾椂娉ㄥ唽/鐧诲綍/鏇存柊鍘嗗彶鏃讹紝鍙�鑳藉彂鐢燂細
- 涓㈠け鏇存柊
- 璇诲埌鍗婃埅 JSON锛堣櫧鐒舵�傜巼浣庯級

褰卞搷锛氬�氱敤鎴峰苟鍙戜笅璁よ瘉/鍘嗗彶鏁版嵁鍙�鑳戒笉涓�鑷淬��

---

## 璇存槑

- 绗�涓�杞�鎶ュ憡瑙� `bugaudit/findings-round1.md`
- 娴嬭瘯鏂囦欢 `bugaudit/test_taskmanager_race.py` 淇濈暀浣滀负楠岃瘉鍑�璇�
# New Bug Audit Round 6

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 50锛堜綆锛夛細`TodoManager._save` 闈炲師瀛愬啓锛屽穿婧冨彲鑳芥崯鍧� `.todo.json`

鏂囦欢锛歚core/tools_tasks.py`

```python
def _save(self):
    with open(self.state_file, "w", encoding="utf-8") as f:
        json.dump(self.todos, f, ...)
```

- 鐩存帴瑕嗙洊鍐欙紝娌℃湁涓存椂鏂囦欢 + rename
- 鍐欎竴鍗婂穿婧冨彲鑳界暀涓嬫崯鍧� JSON锛屼笅娆″姞杞藉け璐�

褰卞搷锛氫綆锛屼絾灞炰簬瀛樺偍鍙�闈犳�ч棶棰樸��

---

## 鍙戠幇 51锛堜綆锛夛細鎶�鑳芥弿杩伴�栬�屼负绌烘椂锛岀洰褰曟潯鐩�鎻忚堪涓虹┖

鏂囦欢锛歚core/tools_skills.py` 鈫� `_shorten_description()`

```python
first = next((l.strip() for l in desc.splitlines() if l.strip()), "")
```

- 濡傛灉 `description` 浠ョ┖琛屽紑澶达紝棣栬�屼細鍙栧埌绗�浜岃�岋紵鍏跺疄 `if l.strip()` 浼氳烦杩囩┖琛岋紝鎵�浠ヤ笉浼氫负绌�
- 鑻� desc 鍏ㄩ儴涓虹┖锛屽垯 first=""锛岀洰褰曟潯鐩�鏃犳弿杩�
- 褰卞搷灏�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
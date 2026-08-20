# New Bug Audit Round 19

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 65锛堜綆锛夛細`run_in_background` 鐨勫嵄闄╁懡浠よ繃婊ゅ悓鏍锋槸瀛愪覆鍖归厤锛屼細璇�鎷︽櫘閫氬懡浠�

鏂囦欢锛歚core/tools_background.py`

```python
dangerous = ["format", "diskpart", "reg delete", "shutdown", ...]
if any(d in command.lower() for d in dangerous):
    return "Error: Dangerous command blocked"
```

- 涓� `run_bash` 鐩稿悓鐨勫瓙涓插尮閰嶉棶棰�
- 渚嬪�� `echo shutdown`銆乣python format.py` 浼氳��璇�鎷�

褰卞搷锛氭�ｅ父鍚庡彴鍛戒护琚�璇�鎷︽埅銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
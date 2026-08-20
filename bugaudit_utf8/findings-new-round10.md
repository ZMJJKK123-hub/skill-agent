# New Bug Audit Round 10

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 55锛堜腑锛夛細`verify_artifact` 鐨� `jar_path` 鍙�璇诲彇宸ヤ綔鍖哄�栦换鎰� jar

鏂囦欢锛歚core/tools_artifact.py`

```python
if jar_path:
    p = Path(jar_path)
    if p.is_absolute() and p.exists():
        jars = [p]
```

- `jar_path` 鏈�鏍￠獙蹇呴』鍦ㄥ伐浣滃尯鍐�
- 濡傛灉妯″瀷浼� `/etc/passwd` 鎴栦换鎰忔枃浠惰矾寰勶紙铏界劧鍚嶄箟涓婃槸 jar锛夛紝宸ュ叿浼氬皾璇曚互 zip 鎵撳紑骞惰繑鍥炲唴瀹规憳瑕�
- 灞炰簬娌欑�卞彧璇婚�冮�稿悓绫婚棶棰�

褰卞搷锛�
- 鍙�璇诲彇宸ヤ綔鍖哄�栨枃浠讹紙鑻ヨ兘琚� zipfile 瑙ｆ瀽鍒欐硠闇插唴瀹癸紱涓嶈兘瑙ｆ瀽鍒欐姤閿欙級
- 浣�/涓�鍗�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
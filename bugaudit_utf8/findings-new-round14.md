# New Bug Audit Round 14

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 60锛堜綆锛夛細`detect_environment` 璇讳笉鍒� Java 鐗堟湰锛屽洜涓� `java -version` 杈撳嚭鍒� stderr

鏂囦欢锛歚core/tools_env.py` 鈫� `_run()`

```python
p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, ...)
out = (p.stdout or "").strip()
return out[:500] or f"(exit {p.returncode})"
```

- `java -version` 瀹為檯杈撳嚭鍦� stderr
- `_run` 鍙�鍙� stdout
- 缁撴灉鏄� Java 鐗堟湰鏄剧ず涓� `(exit 0)` 鑰屼笉鏄�瀹為檯鐗堟湰

褰卞搷锛�
- `detect_environment` 涓� Java 鐗堟湰淇℃伅缂哄け
- 褰卞搷寰堜綆锛屼絾灞炰簬瀹炵幇 bug

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
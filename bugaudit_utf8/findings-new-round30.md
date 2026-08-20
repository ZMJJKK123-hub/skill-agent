# New Bug Audit Round 30

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 76锛堜綆锛夛細`_find_modid` 鍦ㄦ棤娉曚粠 mods.toml 璇嗗埆鏃讹紝浼氶�掑綊鎵�鎻忓叏閮� Java 鏂囦欢

鏂囦欢锛歚core/tools_validate.py` 鈫� `_find_modid()`

```python
java_root = Path(base) / "src" / "main" / "java"
if java_root.is_dir():
    for f in java_root.rglob("*.java"):
        ...
```

- 濡傛灉 `mods.toml` 涓嶅瓨鍦ㄦ垨鏈�鍖归厤锛屼細閬嶅巻鏁翠釜 `src/main/java`
- 澶ч」鐩�鎴栨簮鐮佹爲杈冨ぇ鏃跺彲鑳借緝鎱�
- `validate_resources` / `detect_environment` 閮戒細璋冪敤瀹�

褰卞搷锛氫綆锛屾�ц兘闂�棰樸��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
# New Bug Audit Round 26

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 72锛堜綆锛夛細`_build_source_zip` 鍦ㄦ竻灏忔惌宸ヤ綔鍖轰笅鎶� mod.zip 鍐欏埌 `.runtime` 鐨勭埗鐩�褰曪紝闄勪欢鎵�鎻忓彲鑳芥壂涓嶅埌

鏂囦欢锛歚core/tools_mod.py` 鈫� `_build_source_zip()`

```python
base = worktree_manager.resolve_dir() if worktree_manager else os.getcwd()
zip_path = base.parent / "mod.zip"  # <session>/mod.zip
```

- 鍦� server_app 涓� base 鏄�浼氳瘽 `mod/` 鐩�褰曪紝`base.parent` 鏄�浼氳瘽鐩�褰曪紝zip 浣嶇疆姝ｇ‘
- 鍦ㄦ竻灏忔惌 8001 涓� `worktree_manager.resolve_dir()` 杩斿洖 `.runtime`锛宍base.parent` 鏄� `tsinghua agent server`锛宍mod.zip` 鍐欏埌鏈嶅姟鐩�褰�
- 闄勪欢鏀堕泦 `_collect_attachments` 鍙�鎵� `.runtime`锛屽彲鑳芥壂涓嶅埌杩欎釜 zip

褰卞搷锛氭竻灏忔惌鍦烘櫙涓嬫簮鐮� zip 闄勪欢鍙�鑳戒涪澶�/璺�寰勪笉涓�鑷淬��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
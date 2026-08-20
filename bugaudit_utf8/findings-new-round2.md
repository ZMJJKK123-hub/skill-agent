# New Bug Audit Round 2

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 44锛堜綆锛夛細`run_grep` 鐨� `context_lines` 鍦ㄥ�氫釜鍖归厤鐩搁偦鏃朵細杈撳嚭閲嶅�嶈��

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_grep()` / `_emit()`

```python
def _emit(rel, src_lines, idx):
    ctx = context_lines if context_lines and context_lines > 0 else 0
    lo = max(0, idx - 1 - ctx)
    hi = min(len(src_lines), idx + ctx)
    for n in range(lo, hi):
        results.append(f"{rel}:{n + 1}: {src_lines[n][:300]}")
```

- 姣忎釜鍖归厤閮界嫭绔嬭緭鍑� `[idx-1-ctx, idx+ctx)` 鍖洪棿
- 濡傛灉涓や釜鍖归厤琛岃窛绂诲皬浜庣瓑浜� 2*ctx锛屽畠浠�鐨勪笂涓嬫枃绐楀彛浼氶噸鍙狅紝鍚屼竴琛屼細琚�閲嶅�嶈拷鍔�

褰卞搷锛�
- `grep` 缁撴灉鍑虹幇閲嶅�嶈��
- 缁撴灉鏉℃暟鍙�鑳借秴杩� `max_results`锛堝洜涓哄厛杩藉姞鍚庡垽鏂�鎴�鏂�锛�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
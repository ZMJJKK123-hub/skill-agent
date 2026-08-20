# Bug Audit Round 27

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 41锛堜綆锛夛細`glob` 宸ュ叿浼氬叏閲忛亶鍘嗗伐浣滃尯鍚庢墠鎴�鏂�鍒� 200 鏉�

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_glob()`

```python
for p in base.rglob(pattern):
    ...
    matches.append(...)
matches = matches[:200]
```

- 浣跨敤 `rglob` 鍏ㄩ噺閬嶅巻鍚庢墠鎴�鏂�
- 瀵逛簬鍖呭惈涓婁竾鏂囦欢锛堝�� `mc_java_sources`銆乣node_modules` 绛夛級鐨勫伐浣滃尯锛岃櫧鐒朵細璺宠繃閮ㄥ垎鐩�褰曪紝浣嗕粛鍙�鑳借緝鎱�
- 缁撴灉铏界劧闄愬埗 200 鏉★紝浣嗛亶鍘嗘垚鏈�涓嶅彈闄愬埗

褰卞搷锛氭�ц兘闂�棰橈紝灏ゅ叾鍦ㄥぇ宸ヤ綔鍖�/浣庨厤鏈嶅姟鍣ㄤ笂銆�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round27.md`
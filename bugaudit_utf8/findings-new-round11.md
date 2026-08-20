# New Bug Audit Round 11

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 56锛堜腑锛夛細`worktree_run` 鍛戒护涓嶅�楁矙绠憋紝鍙�鐢� `cd ..` 閫冨嚭 worktree

鏂囦欢锛歚core/worktree.py` 鈫� `run_in_worktree()`

```python
proc = subprocess.Popen(command, shell=True, cwd=str(wt_path), ...)
```

- 鐩存帴浠� shell 鎵ц�屼换鎰忓懡浠�
- 娌℃湁澶嶇敤 `run_bash` 鐨勮秺鐣�/娌欑�辨��鏌�
- 鍛戒护閲� `cd ..` 鍙�杩涘叆 worktree 澶栧眰鐩�褰�

褰卞搷锛�
- 涓� `run_in_background` 绫讳技锛屽睘浜庢矙绠�/鎵ц�岄潰闅旂�荤粫杩�

---

## 鍙戠幇 57锛堜綆锛夛細鎶�鑳藉垪琛ㄥ湪杩涚▼鍚�鍔ㄦ椂鎵�鎻忥紝鏂板�炴妧鑳介渶閲嶅惎鎵嶇敓鏁�

鏂囦欢锛歚core/tools_skills.py`

- `SkillLoader.__init__` 鍙�鎵�鎻忎竴娆�
- `reload()` 瀛樺湪浣嗘湭鏆撮湶涓哄伐鍏�/鎺ュ彛
- 杩愯�屼腑鏂板��/淇�鏀规妧鑳界洰褰曪紝agent 鐪嬩笉鍒版柊鎶�鑳�

褰卞搷锛氬姛鑳藉彈闄愶紝闇�閲嶅惎杩涚▼銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
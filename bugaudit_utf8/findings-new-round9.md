# New Bug Audit Round 9

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 54锛堜腑锛夛細git 宸ュ叿鍏佽�镐紶浠绘剰 `workdir`锛屽彲鎿嶄綔宸ヤ綔鍖哄�栦粨搴�

鏂囦欢锛歚core/tools_git.py`

- `git_status(workdir=None)` / `git_diff(workdir=None)` / `git_commit(message, workdir=None)` / `snapshot(workdir=None)` / `restore_snapshot(ref, workdir=None)`
- 閮界洿鎺ヤ娇鐢� `workdir or _base_dir()`锛屾湭鐢� `safe_path` 鏍￠獙
- schema 閲� `workdir` 鏄�鍙�閫夊弬鏁帮紝妯″瀷鍙�浠ヤ紶 `/opt/skill-agent`銆乣/etc` 绛夌粷瀵硅矾寰�

褰卞搷锛�
- 鍦� workspace-write 娌欑�变笅锛宎gent 鍙�閫氳繃 git 宸ュ叿璇诲彇/淇�鏀瑰伐浣滃尯澶栫殑 git 浠撳簱
- 渚嬪�� `snapshot(workdir="/opt/skill-agent")` 鍙�浠ュ湪椤圭洰鏍逛粨搴撳仛 `git add -A` / commit锛屽奖鍝嶉」鐩�婧愮爜
- 灞炰簬娌欑�辫竟鐣岀粫杩囷紙鍙�璇�/鍐欓�冮�革級

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 瀵� `workdir` 鍙傛暟缁熶竴璧� `safe_path()` 骞堕檺鍒跺湪宸ヤ綔鍖哄唴

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
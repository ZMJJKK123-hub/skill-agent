# Bug Audit Round 3

> 鏈�杞�鍙�璇绘��鏌� + 涓や釜闈欐�侀獙璇佽剼鏈�锛屾湭淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 8锛堜腑锛夛細grep 宸ュ叿 schema 缂哄皯 `context_lines`锛屼絾 handler 宸叉敮鎸�

鏂囦欢锛歚core/tools.py`

- `TOOL_HANDLERS["grep"]` 宸茬粡璋冪敤锛�
  ```python
  run_grep(kw["pattern"], kw.get("path", "."), kw.get("glob_filter"),
           kw.get("max_results", 50), kw.get("context_lines", 0))
  ```
- 浣� `grep` 鐨� OpenAI schema 鍙�澹版槑浜嗭細
  ```json
  ["pattern", "path", "glob_filter", "max_results"]
  ```
- `search_api` 鐨� schema 鏈� `context_lines`锛宍grep` 娌℃湁銆�

褰卞搷锛�
- 妯″瀷涓嶇煡閬� `grep` 鑳藉甫涓婁笅鏂囪�屾暟锛屼笉浼氫富鍔ㄤ娇鐢�锛�
- 濡傛灉鏌愪簺瀹㈡埛绔�涓ユ牸鏍￠獙锛屼紶 `context_lines` 鍙�鑳借��鎷掔粷鎴栧拷鐣ャ��

楠岃瘉鑴氭湰锛歚bugaudit/check_tool_args.py`

---

## 鍙戠幇 9锛堥珮锛夛細`run_in_background` 缁曡繃 workspace-write 娌欑�憋紝鍙�鑳戒慨鏀归」鐩�鏍圭洰褰�

鏂囦欢锛歚core/tools_background.py`

`BackgroundManager.run()` 鍙�杩囨护浜嗗嚑涓�鍗遍櫓鍛戒护锛�
```python
dangerous = ["format", "diskpart", "reg delete", "shutdown",
             "taskkill /f /im python.exe", ...]
```

瀹�**娌℃湁**锛�
- 妫�鏌� `cd ..` / 缁濆�硅矾寰勮秺鍑哄伐浣滃尯
- 鍦� `read-only` 涓嬫嫤鎴�鍐欐搷浣�
- 娌℃湁澶嶇敤 `tools_shell._sandbox_mode()` / `_escapes_workspace()`

鑰� `bash` 宸ュ叿鍦� `workspace-write` 妯″紡涓嬩細鎷︽埅瓒婂嚭宸ヤ綔鍖猴紝`run_in_background` 鍗翠笉浼氥��

褰卞搷锛�
- 鍦� 8001 娓呭皬鎼�鎺ュ彛閲岋紝鍗充娇 `DSH_SANDBOX_MODE=workspace-write` 淇濇姢浜嗛」鐩�鏍癸紝agent 浠嶅彲鑳介�氳繃 `run_in_background` 鎵ц�岋細
  ```bash
  cd .. && echo x > /opt/skill-agent/pwned.txt
  ```
  浠庤�岀粫杩囨矙绠变慨鏀归」鐩�婧愮爜/鏍圭洰褰曟枃浠躲��

杩欐�ｆ槸鐢ㄦ埛鎷呭績鐨勨�滄竻灏忔惌鐢ㄦ埛瀵硅瘽鍚庨」鐩�鏍圭洰褰曞嚭鐜版枃浠垛�濈殑娼滃湪閫斿緞涔嬩竴銆�

---

## 鏂板�為獙璇佽剼鏈�

```
bugaudit/check_tool_args.py
bugaudit/check_tool_required_args.py
bugaudit/test_taskmanager_race.py
```

## 璇存槑

- `check_tool_required_args.py` 缁撴灉涓烘棤闂�棰橈紙handler 寮哄埗鍙栧�奸兘鍦� required 閲岋級
- 鍓嶄袱杞�鎶ュ憡瑙� `bugaudit/findings-round1.md`銆乣findings-round2.md`
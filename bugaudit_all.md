===== findings-new-round1.md =====
# New Bug Audit Round 1

> 鏂颁竴杞�鎸佺画宸℃煡锛屽彧璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 43锛堜腑锛夛細`_SEARCH_SKIP_DIRS` 鍖呭惈 `mc_java_sources`锛屼笌娉ㄩ噴鈥滃惈 mc_java_sources鈥濈煕鐩�

鏂囦欢锛歚core/tools_fs.py` 73-80

```python
# grep/glob锛氱洿鎺ユ悳宸ヤ綔鍖烘枃浠讹紙鍚� mc_java_sources銆乻kills銆佺敓鎴愪唬鐮侊級锛�
_SEARCH_SKIP_DIRS = {
    ...
    "mc_java_sources",
}
```

闂�棰橈細
- 娉ㄩ噴鏄庣‘璇� grep/glob 浼氭悳 `mc_java_sources`
- 浣� `_SEARCH_SKIP_DIRS` 鎶� `mc_java_sources` 鍔犲叆璺宠繃鐩�褰�
- `run_glob` 璺�寰勪腑鍑虹幇 `mc_java_sources` 鏃朵細琚�璺宠繃锛屾棤娉� glob MC 婧愮爜
- `run_grep` 浠ユ暣涓�宸ヤ綔鍖轰负鏍规椂锛宍mc_java_sources` 瀛愮洰褰曚細琚� `os.walk` 鍓�鏋濓紝鎼滀笉鍒伴噷闈㈠唴瀹�
- 鍙�鏈夋樉寮忎紶 `path="mc_java_sources"`锛堜緥濡� `search_api`锛夋椂鏍圭洰褰曟湰韬�涓嶈��鍓�鏋濓紝鎵嶈兘鎼滃埌

褰卞搷锛�
- 閫氱敤 `grep`/`glob` 琛屼负涓庢敞閲婁笉绗�
- 鐢ㄦ埛/妯″瀷浠ヤ负鑳芥悳 MC 婧愮爜锛屽疄闄呭ぇ閮ㄥ垎鎯呭喌鎼滀笉鍒�
- 灞炰簬鈥滄敞閲婃壙璇鸿兘鍔涗笌瀹為檯瀹炵幇涓嶄竴鑷粹�濈殑 bug

---

## 璇存槑

- 杩欐槸鏂颁竴杞�鐩�鏍囩殑绗�涓�浠芥姤鍛�
- 鍚庣画鍙戠幇缁х画鏀惧湪 `bugaudit/` 涓�

===== findings-new-round10.md =====
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

===== findings-new-round11.md =====
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

===== findings-new-round12.md =====
# New Bug Audit Round 12

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 58锛堥珮/Linux 涓ラ噸锛夛細澶氬�勮秴鏃舵竻鐞嗗啓姝� `taskkill`锛屽湪 Linux 涓婃棤娉曠粓姝㈣秴鏃惰繘绋�

娑夊強锛�
- `core/tools_shell.py` `run_bash()` 瓒呮椂鍒嗘敮
- `core/tools_background.py` `_execute()` 瓒呮椂鍒嗘敮
- `core/worktree.py` `run_in_worktree()` 瓒呮椂鍒嗘敮

浠ｇ爜绀轰緥锛�
```python
except subprocess.TimeoutExpired:
    subprocess.run(f"taskkill /f /t /pid {proc.pid}", shell=True, capture_output=True)
```

- `taskkill` 鏄� Windows 鍛戒护
- 8001/鏈嶅姟璺戝湪 Linux 涓婏紝`taskkill` 涓嶅瓨鍦�
- 瓒呮椂鍚庤繘绋嬫爲涓嶄細琚�鏉�姝伙紝鍙�鑳芥畫鐣欏悗鍙拌繘绋嬬户缁�杩愯��

褰卞搷锛�
- 瓒呮椂鍛戒护鏃犳硶娓呯悊
- 闀挎湡杩愯�屽彲鑳藉爢绉�鍍靛案/娈嬬暀杩涚▼
- 灏ゅ叾瀵� Linux 閮ㄧ讲闈炲父鍏抽敭

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鎸� `os.name` 鍖哄垎锛歐indows 鐢� `taskkill /T /F`锛孡inux 鐢� `os.killpg(proc.pid, SIGKILL)`

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round13.md =====
# New Bug Audit Round 13

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 59锛堜腑锛夛細`run_mod_test_cycle` 鏈�璇嗗埆 `validate_resources` 鐨勯敊璇�杩斿洖锛屽彲鑳借��鎶� PASS

鏂囦欢锛歚core/tools_loop.py`

```python
v = validate_resources(modid)
out.append(v)
if "RESULT: FAIL" in v:
    result_ok = False
```

- `validate_resources` 鍦ㄦ棤娉曡嚜鍔ㄨ瘑鍒� modid 绛夐敊璇�鏃惰繑鍥� `"Error: cannot auto-detect modid..."`锛屽叾涓�涓嶅寘鍚� `"RESULT: FAIL"`
- 鍥犳�� `result_ok` 涓嶄細鍙� False
- 鍚庣画 build/test 鍗充娇鎴愬姛锛屾渶缁堜粛鍙�鑳借緭鍑� `RESULT: PASS`

褰卞搷锛�
- 璧勬簮鏍￠獙澶辫触浣嗘暣浣撴祴璇曞惊鐜�鏄剧ず閫氳繃
- 婕忔姤闂�棰�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 璇嗗埆 `v.startswith("Error")` 鎴� `"RESULT: FAIL"` / `"ERRORS:"` 绛夊け璐ヤ俊鍙�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round14.md =====
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

===== findings-new-round15.md =====
# New Bug Audit Round 15

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 61锛堜綆锛夛細`run_mod_test_cycle` 瀵规瀯寤哄け璐ヨ瘑鍒�涓嶅畬鏁�

鏂囦欢锛歚core/tools_loop.py`

```python
if "[build] Gradle 鏋勫缓澶辫触" in b or "BUILD FAILED" in b:
    result_ok = False
```

- 鍙�璇嗗埆杩欎袱绉嶅け璐ユ爣璁�
- 濡傛灉 `_forge_build_jar` 杩斿洖鍏朵粬澶辫触鏂囨湰锛堝�傝秴鏃躲�佹壘涓嶅埌 gradlew銆佸�嶅埗 jar 澶辫触锛夛紝`result_ok` 涓嶄細鍙� False
- 鍙�鑳借��鎶� PASS

褰卞搷锛氭祴璇曞惊鐜�瀵归儴鍒嗘瀯寤哄け璐ユ紡鎶ャ��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round16.md =====
# New Bug Audit Round 16

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 62锛堜綆锛夛細澶氫釜宸ュ叿瀵规暟鍊煎弬鏁扮己灏戠被鍨嬭浆鎹�锛屾ā鍨嬩紶瀛楃�︿覆鏃跺彲鑳藉穿婧�

渚嬪瓙锛�
- `core/tools_web.py` `run_web_fetch(url, max_chars)`锛氳嫢 `max_chars` 鏄�瀛楃�︿覆锛宍text[:max_chars]` 鎶� `TypeError`
- `core/tools_search.py` `run_web_search(query, max_results)`锛氳嫢 `max_results` 鏄�瀛楃�︿覆锛宍range`/鎴�鏂�鍙�鑳芥姏閿�
- `core/tools_gametest.py` `parse_gametest_results(lines)`锛氳櫧鐒跺仛浜� `int()`锛屼絾鍏朵粬宸ュ叿涓嶆槸閮藉仛

澶氭暟鍑芥暟璋冪敤鍙傛暟浼氱敱妯″瀷鎸� JSON number 鍙戦�侊紝浣嗕笉鍚� provider 鍙�鑳戒紶瀛楃�︿覆/鏁板瓧娣风敤锛涙暣浣撶己灏戠粺涓�闃插尽銆�

褰卞搷锛氫綆姒傜巼杩愯�屾椂閿欒��銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round17.md =====
# New Bug Audit Round 17

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 63锛堜綆锛夛細`run_mod_test_cycle` 鐨� `build_timeout` 鍙傛暟鏈�鐢熸晥

鏂囦欢锛歚core/tools_loop.py` 鈫� `run_mod_test_cycle()`

```python
def run_mod_test_cycle(..., build_timeout=900, test_timeout=180, ...):
    ...
    if build:
        b = _forge_build_jar({"gradle_task": "build"})
```

- `build_timeout` 琚�鎺ユ敹浣嗕粠鏈�浼犵粰 `_forge_build_jar`
- `_forge_build_jar` 鍐呴儴鍥哄畾 900 绉掕秴鏃�
- `test_timeout` 鍊掓槸浼犵粰浜� GameTest

褰卞搷锛�
- 璋冪敤鏂规棤娉曡皟鏁存瀯寤鸿秴鏃�
- 鍙傛暟鏃犳晥/璇�瀵�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round18.md =====
# New Bug Audit Round 18

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 64锛堜綆锛夛細`glob`/`grep` 鍦� Windows 涓婅繑鍥炲弽鏂滄潬璺�寰勶紝涓庢彁绀鸿瘝/宸ュ叿绾﹀畾涓嶄竴鑷�

鏂囦欢锛歚core/tools_fs.py`

- `run_glob` 浣跨敤 `str(p.relative_to(base))`锛學indows 涓嬫槸 `\` 鍒嗛殧
- `run_grep` 鍚屾牱浣跨敤 `str(fp.relative_to(base))`
- 浣嗙郴缁熸彁绀鸿瘝鍜屾枃妗ｉ噷绀轰緥鏅�閬嶄娇鐢� `/` 璺�寰�

褰卞搷锛�
- agent 鎷垮埌鍙嶆枩鏉犺矾寰勶紝鍚庣画浼犵粰 `read_file` 铏界劧鍦� Windows 涔熻兘鐢�锛屼絾璺ㄥ钩鍙拌�屼负涓嶄竴鑷�
- 鍦� Linux 涓婂垯鏄� `/`锛屾墍浠ュ悓涓�宸ュ叿鍦ㄤ笉鍚屽钩鍙拌繑鍥炴牸寮忎笉鍚�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round19.md =====
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

===== findings-new-round2.md =====
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

===== findings-new-round20.md =====
# New Bug Audit Round 20

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 66锛堜綆锛夛細`parse_build_output` 瀵瑰ぇ鏃ュ織鏃犱笂闄愪繚鎶�

鏂囦欢锛歚core/tools_loop.py`

- `text = path.read_text(encoding="utf-8", errors="replace")` 涓�娆℃�ц�诲叆鏁翠釜鏂囦欢
- 娌℃湁琛屾暟/澶у皬涓婇檺
- 瓒呭ぇ鏋勫缓鏃ュ織鍙�鑳藉崰鐢ㄥぇ閲忓唴瀛�

瀵规瘮锛歚parse_gametest_results` 鏈夊熬璇讳笂闄愶紝`read_game_test_log` 鏈� 200KB 涓婇檺銆�

褰卞搷锛氫綆閰嶆湇鍔″櫒涓婂�勭悊瓒呭ぇ鏃ュ織鏃跺彲鑳藉唴瀛樺帇鍔涘ぇ銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round21.md =====
# New Bug Audit Round 21

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 67锛堜綆锛夛細`start_mc_server` 浣跨敤鍥哄畾榛樿�� RCON 瀵嗙爜 `forge123`

鏂囦欢锛歚core/tools_lifecycle.py` 鈫� `_ensure_rcon_props()`

```python
if not password:
    password = "forge123"
```

- 鏈�鎻愪緵 RCON 瀵嗙爜鏃跺啓鍏ュ浐瀹氶粯璁ゅ瘑鐮�
- 鑻ユ湇鍔″櫒鏆撮湶鍏�缃戯紝RCON 绔�鍙ｅ彲鑳借��鐚滄祴瀵嗙爜

褰卞搷锛�
- 瀹夊叏榛樿�ゅ�艰杽寮�
- 寮�鍙戝満鏅�褰卞搷浣庯紝浣嗗叕缃戦儴缃叉湁椋庨櫓

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round22.md =====
# New Bug Audit Round 22

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 68锛堜腑锛夛細`move_skills_to_end` 姣忚疆鍔犺浇鏂版妧鑳介兘浼氳拷鍔犳柊鐨� `<active-skills>`锛屾棫鍧椾笉娓呯悊

鏂囦欢锛歚core/skillcheck.py` 鈫� `move_skills_to_end()`

- 姣忔�″彂鐜版柊鐨� `load_skill` 宸ュ叿缁撴灉锛屼細鎶婃妧鑳藉叏鏂囦互 `<active-skills>` user 娑堟伅杩藉姞鍒版湯灏�
- 涓嶄細绉婚櫎鏃х殑 `<active-skills>` 娑堟伅
- 澶氭�″姞杞戒笉鍚屾妧鑳藉悗锛屼笂涓嬫枃閲屼細绱�绉�澶氫唤鎶�鑳藉叏鏂囧潡

褰卞搷锛�
- 涓婁笅鏂囪啫鑳�
- 鏃ф妧鑳藉叏鏂囧崰鐢� token
- 涓庘�滄粴鍔ㄥ埌鏈�鏂般�佷笉绱�绉�鈥濈殑璁捐�℃剰鍥句笉绗︼紙鏃� tool 娑堟伅琚�鍗犱綅锛屼絾鏃� active-skills user 娑堟伅娌¤��娓呯悊锛�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round23.md =====
# New Bug Audit Round 23

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 69锛堜綆锛夛細鎶�鑳芥�ｆ枃鑻ュ寘鍚� `</skill>` 瀛楁牱锛屼細琚� `load_skill` 鐨勬�ｅ垯鎻愬墠鎴�鏂�

鏂囦欢锛歚core/tools_skills.py` / `core/skillcheck.py`

- `SkillLoader.get_content()` 杩斿洖 `<skill name="...">\n{body}\n</skill>`
- `skillcheck` 鐨� `_SKILL_BLOCK_RE` 浣跨敤闈炶椽濠� `(.*?)</skill>`
- 濡傛灉鎶�鑳芥�ｆ枃閲屽嚭鐜� `</skill>` 鏂囨湰锛堜緥濡� Markdown 浠ｇ爜鍧楃ず渚嬶級锛岃В鏋愪細鎻愬墠缁撴潫锛屾妧鑳藉叏鏂囪��鎴�鏂�

褰卞搷锛�
- 鎶�鑳藉唴瀹逛涪澶�
- 姝ｇ‘鎬�/涓婁笅鏂囦笉瀹屾暣

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round24.md =====
# New Bug Audit Round 24

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 70锛堜腑锛夛細闃熷弸澶勭悊鈥滅洿鎺ユ敹浠剁�变换鍔♀�濆悗涓嶉噸缃� IDLE 瓒呮椂锛岄暱浠诲姟瀹屾垚鍙�鑳界珛鍗宠嚜鍔ㄥ叧鏈�

鏂囦欢锛歚core/tools_team.py` 鈫� `_teammate_loop()`

- `idle_deadline = time.time() + 60` 鍦ㄧ嚎绋嬪紑濮嬫椂璁剧疆涓�娆�
- 鍙�鏈夆�滀粠鐪嬫澘璁ら�嗕换鍔♀�濇椂浼氶噸缃� `idle_deadline`
- 浠庢敹浠剁�辨敹鍒扮洿鎺ユ寚娲句换鍔℃椂锛屼笉閲嶇疆

濡傛灉鐩存帴浠诲姟鑰楁椂瓒呰繃鍓╀綑 idle 鏃堕棿锛�
- 澶勭悊瀹屽洖鍒� IDLE 鏃� `time.time() >= idle_deadline`
- 鐞冮槦琚�鍒ゅ畾鈥滅┖闂茶秴鏃垛�濆苟鑷�鍔� shutdown

褰卞搷锛�
- 闃熷弸鍒氬畬鎴愪竴涓�閲嶈�佷换鍔″氨琚�鑷�鍔ㄥ叧闂�
- 闀垮�硅瘽/澶嶆潅浠诲姟鍦烘櫙涓嬩笉鍙�闈�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦ㄨ繘鍏� WORK 澶勭悊浠讳綍娑堟伅锛堝寘鎷�鏀朵欢绠憋級鏃堕兘閲嶇疆 `idle_deadline`

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round25.md =====
# New Bug Audit Round 25

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 71锛堜綆锛夛細`mc_status` / `wait_for_mc_ready` 瀵� manifest 鎭㈠�嶇殑瀛ゅ効杩涚▼涓嶅畬鏁存劅鐭�

鏂囦欢锛歚core/tools_lifecycle.py`銆乣core/tools_wait.py`

- `mc_status` 浣跨敤 `process_manager.list_info(base)`锛岃兘鐪嬪埌 manifest 瀛ゅ効
- 浣� `wait_for_mc_ready(handle)` 浣跨敤 `process_manager.get(handle)`锛堝彧鏌ュ唴瀛� `_PROCESSES`锛夛紝鐪嬩笉鍒� manifest 瀛ゅ効
- 鏈嶅姟閲嶅惎鍚庯紝`wait_for_mc_ready("mc-server")` 鍙�鑳戒竴鐩寸瓑鍒拌秴鏃讹紝灏界�¤繘绋嬪疄闄呮椿鐫�

褰卞搷锛氶噸鍚�鍚庡�瑰�ゅ効杩涚▼鐨勭瓑寰�/鐘舵�佸垽鏂�涓嶅畬鏁淬��

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round26.md =====
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

===== findings-new-round27.md =====
# New Bug Audit Round 27

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 73锛堜綆锛夛細`read_crash_report` 鍏ㄩ噺璇绘枃浠跺悗鍐嶅彇澶撮儴

鏂囦欢锛歚core/tools_crash.py`

```python
text = path.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
head = lines[:max_lines]
```

- 鍗充娇鍙�瑕佸墠 120 琛岋紝涔熶細鍏堟暣涓�璇诲叆鏂囦欢
- 瓒呭ぇ crash report 鏃舵氮璐瑰唴瀛�

褰卞搷锛氫綆锛屼笌 `parse_build_output` 鍚岀被銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round28.md =====
# New Bug Audit Round 28

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 74锛堜綆锛夛細`_SEARCH_SKIP_DIRS` 鍖呭惈瀹芥硾鐨� `bin`銆乣run`锛屽彲鑳借��鎺掗櫎鍚堟硶鐩�褰�

鏂囦欢锛歚core/tools_fs.py`

```python
_SEARCH_SKIP_DIRS = { ..., "run", "bin", "venv", ...}
```

- 宸ヤ綔鍖洪噷濡傛灉鏈夊悕涓� `bin/`銆乣run/` 鐨勪笟鍔＄洰褰曪紙渚嬪�� `src/main/resources/bin/`锛夛紝`run_grep`/`run_glob` 浼氳烦杩�
- 杩欎簺鍚嶅瓧澶�閫氱敤锛屽�规槗璇�浼ゅ悎娉曞唴瀹�

褰卞搷锛氭悳绱㈢粨鏋滀笉瀹屾暣銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round29.md =====
# New Bug Audit Round 29

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 75锛堜綆锛夛細鎶�鑳芥枃浠跺甫 UTF-8 BOM 鏃� frontmatter 瑙ｆ瀽鍙�鑳藉け璐�

鏂囦欢锛歚core/tools_skills.py`

- `_read_head` 璇� bytes 鍚� `decode("utf-8", errors="replace")`
- 濡傛灉鏂囦欢甯� BOM锛坄EF BB BF`锛夛紝寮�澶翠細鍙樻垚 `\ufeff---`
- `raw.startswith("---")` 涓� False锛屽綋鍓嶄唬鐮佷細鎶婂畠褰撯�滄棤 frontmatter鈥濆�勭悊锛孻AML 鍏冩暟鎹�涓㈠け

褰卞搷锛�
- 甯� BOM 鐨� SKILL.md 浼氫涪澶� name/description 绛夊厓鏁版嵁
- 鍘嗗彶涓婃浘鍥犳�ゅ嚭杩囬棶棰橈紙YAML 鍏煎�癸級

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round3.md =====
# New Bug Audit Round 3

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 45锛堜綆锛夛細鎶�鑳界洰褰� digest 鍙樺寲鏃跺彧杩藉姞鏂扮洰褰曟秷鎭�锛屼笉娓呯悊鏃ф秷鎭�

鏂囦欢锛歚core/tools_skills.py` 鈫� `maybe_inject_skill_catalog()`

- 褰撴妧鑳藉垪琛ㄥ彉鍖栵紙digest 鏀瑰彉锛夋椂锛屼細寰� messages 杩藉姞涓�鏉℃柊鐨� `<available-skills>`
- 涓嶄細绉婚櫎鏃х殑鐩�褰曟秷鎭�
- 濡傛灉鎶�鑳芥枃浠跺�氭�″�炲垹锛屼笂涓嬫枃閲屼細绉�绱�澶氭潯鐩�褰�

褰卞搷锛氫笂涓嬫枃鑶ㄨ儉/鏃х洰褰曡��瀵笺��

---

## 鍙戠幇 46锛堜綆锛夛細`_find_modid` 鍙�璇嗗埆鍙屽紩鍙� `modId="..."`

鏂囦欢锛歚core/tools_validate.py`

```python
m = re.search(r'modId\s*=\s*"([^"]+)"', text)
```

- 鑻� `mods.toml` 鐢ㄥ崟寮曞彿锛岃瘑鍒�涓嶅埌
- 澶氭暟妯℃澘鐢ㄥ弻寮曞彿锛屽奖鍝嶅皬

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round30.md =====
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

===== findings-new-round4.md =====
# New Bug Audit Round 4

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 47锛堜綆锛夛細`ask_user_question` 浼犲叆绌烘暟缁勬椂浼氱敓鎴� `"[]"` 浣滀负闂�棰�

鏂囦欢锛歚core/tools_ask.py`

```python
if isinstance(questions, list) and questions:
    ...
else:
    qs = [{"question": str(questions or ""), "options": options}]
```

- 濡傛灉妯″瀷浼� `questions: []`锛宍questions` 涓� falsy锛岃繘鍏� else
- `str([])` = `"[]"`锛屼簬鏄�闂�棰樺彉鎴� `"[]"`
- 搴旇�嗕负鈥滄棤闂�棰樷�濆苟杩斿洖閿欒��/鎻愮ず

---

## 鍙戠幇 48锛堜綆锛夛細鍚庡彴浠诲姟缁撴灉鎴�鏂�鍒� 2000 瀛楃�︿絾鏃犳埅鏂�鏍囪��

鏂囦欢锛歚core/tools_background.py` 鈫� `format_background_results()`

```python
f"Result: {n['result'][:2000]}"
```

- 瓒呰繃 2000 瀛楃�︾洿鎺ユ埅鏂�
- 娌℃湁鎻愮ず鈥滃凡鎴�鏂�鈥濓紝agent 鍙�鑳借��浠ヤ负缁撴灉瀹屾暣

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round5.md =====
# New Bug Audit Round 5

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 49锛堜腑锛夛細闃熷弸浠庣湅鏉胯嚜涓昏�ら�嗕换鍔″悗锛岀粨鏋滃彂缁� `board` 鏀朵欢绠辫�屼笉鏄� `leader`锛宭eader 鐪嬩笉鍒�

鏂囦欢锛歚core/tools_team.py` 鈫� `_teammate_loop()`

```python
claimed = self._try_claim_from_board(name)
...
messages = [{
    "from": "board",
    "content": f"浣犱粠浠诲姟鐪嬫澘璁ら�嗕簡浠诲姟 #{claimed['id']}锛歿claimed['subject']} ..."
}]
...
self.bus.send(name, msg["from"], f"[{name} 瀹屾垚] {result}")
```

- 鐪嬫澘鑷�涓昏�ら�嗙殑浠诲姟锛屾秷鎭� `from` 鏄� `"board"`
- 瀹屾垚鍚庣粨鏋滃彂缁� `"board"` 鏀朵欢绠�
- 浣嗕富 agent 鍦� `agent_loop` 閲屽彧浼� `read_inbox("leader")`
- `board` 鏀朵欢绠辨棤浜鸿�诲彇锛屽畬鎴愮粨鏋滀涪澶�

褰卞搷锛�
- 闃熷弸鑷�涓昏�ら�嗙殑浠诲姟铏界劧瀹屾垚锛屼絾 leader 姘歌繙鏀朵笉鍒版眹鎶�
- 鑷�娌讳换鍔￠棴鐜�鏂�瑁�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鐪嬫澘璁ら�嗕换鍔＄殑鍥炴姤涔熷簲鍙戠粰 `"leader"`锛岃�屼笉鏄� `"board"`

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round6.md =====
# New Bug Audit Round 6

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 50锛堜綆锛夛細`TodoManager._save` 闈炲師瀛愬啓锛屽穿婧冨彲鑳芥崯鍧� `.todo.json`

鏂囦欢锛歚core/tools_tasks.py`

```python
def _save(self):
    with open(self.state_file, "w", encoding="utf-8") as f:
        json.dump(self.todos, f, ...)
```

- 鐩存帴瑕嗙洊鍐欙紝娌℃湁涓存椂鏂囦欢 + rename
- 鍐欎竴鍗婂穿婧冨彲鑳界暀涓嬫崯鍧� JSON锛屼笅娆″姞杞藉け璐�

褰卞搷锛氫綆锛屼絾灞炰簬瀛樺偍鍙�闈犳�ч棶棰樸��

---

## 鍙戠幇 51锛堜綆锛夛細鎶�鑳芥弿杩伴�栬�屼负绌烘椂锛岀洰褰曟潯鐩�鎻忚堪涓虹┖

鏂囦欢锛歚core/tools_skills.py` 鈫� `_shorten_description()`

```python
first = next((l.strip() for l in desc.splitlines() if l.strip()), "")
```

- 濡傛灉 `description` 浠ョ┖琛屽紑澶达紝棣栬�屼細鍙栧埌绗�浜岃�岋紵鍏跺疄 `if l.strip()` 浼氳烦杩囩┖琛岋紝鎵�浠ヤ笉浼氫负绌�
- 鑻� desc 鍏ㄩ儴涓虹┖锛屽垯 first=""锛岀洰褰曟潯鐩�鏃犳弿杩�
- 褰卞搷灏�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round7.md =====
# New Bug Audit Round 7

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 52锛堥珮锛夛細澶氫釜宸ュ叿鍙�閫氳繃 `log_path` 鍙傛暟璇诲彇宸ヤ綔鍖哄�栦换鎰忔枃浠讹紝缁曡繃娌欑��

娑夊強鏂囦欢/鍑芥暟锛�
- `core/tools_gametest.py` 鈫� `parse_gametest_results(log_path=...)`
- `core/tools_wait.py` 鈫� `tail_log(log_path=...)`銆乣wait_for_log(log_path=...)`
- `core/tools_loop.py` 鈫� `parse_build_output(log_path=...)`

杩欎簺鍑芥暟澶ч兘锛�
```python
path = Path(log_path) if log_path else Path(base) / "run/logs/latest.log"
if not path.is_absolute():
    path = Path(base) / path
...
path.read_text(...)
```

娌℃湁浣跨敤 `safe_path`锛屼篃娌℃湁鏍￠獙鐩�鏍囧繀椤诲湪宸ヤ綔鍖哄唴銆�

褰卞搷锛�
- 鍦� `workspace-write` 娌欑�变笅锛宎gent 浠嶅彲閫氳繃 `tail_log(log_path="/etc/passwd")` 璇诲彇浠绘剰鏂囦欢鍐呭��
- 鎴栬�诲叾浠栭」鐩�鐩�褰�/绯荤粺鏂囦欢
- 灞炰簬娌欑�卞彧璇婚�冮�� + 淇℃伅娉勯湶椋庨櫓

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 瀵� `log_path` 缁熶竴璧� `safe_path()` 骞堕檺鍒跺湪宸ヤ綔鍖哄唴

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round8.md =====
# New Bug Audit Round 8

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 53锛堥珮锛夛細`run_bash` 鐨勮秺鐣屾��娴嬪彲鐢ㄥ紩鍙风粫杩囷紝`cd ".."` 閫冨嚭宸ヤ綔鍖�

鏂囦欢锛歚core/tools_shell.py` 鈫� `_escapes_workspace()`

```python
def _escapes_workspace(command: str) -> bool:
    return bool(re.search(r"\b(?:cd|pushd)\s+(?:\.\.|[/\\]|[a-z]:)", command.lower()))
```

妫�娴嬭�佹眰 `cd` 鍚庣揣璺� `..` 鎴栫粷瀵硅矾寰�/鐩樼�︼紝浣嗭細
- `cd ".."`锛歚cd` 鍚庢槸寮曞彿锛屾�ｅ垯涓嶅尮閰�
- `cd '..'`锛氬悓鏍蜂笉鍖归厤
- `cd .. &&` 浼氳��鎷︼紝浣嗗姞寮曞彿灏辩粫杩�

褰卞搷锛�
- `workspace-write` 娌欑�变笅 agent 鍙�鎵ц�� `cd ".."` 杩涘叆宸ヤ綔鍖哄�栫洰褰�
- 鍐嶉厤鍚� `write_file`/`bash` 閲嶅畾鍚戝嵆鍙�淇�鏀归」鐩�鏍规垨鍏朵粬鐩�褰�
- 涓� `run_in_background` 缁曡繃绫讳技锛屾槸娌欑�辫竟鐣屽け鏁�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍

===== findings-new-round9.md =====
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

===== findings-round1.md =====
# Bug Audit Round 1

> 鏈�杞�鍙�璇诲贰鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併�傛柊澧炴湰鏂囦欢鐢ㄤ簬璁板綍鍙戠幇銆�

## 鍙戠幇 1锛堥珮锛夛細8001 浼氳瘽鐩�褰曞垏鎹㈠湪閿佸�栨墽琛岋紝骞跺彂浼氫覆浼氳瘽

鏂囦欢锛歚tsinghua agent server/main.py` 鈫� `_run_agent()`

闂�棰橈細
```python
session_root = _session_workdir(session_id)
_prev_cwd = Path.cwd()
...
os.environ["DSH_SESSION_ROOT"] = str(session_root)
os.chdir(session_root)

with _agent_lock:
    ...
    final = agent_loop(...)
```

`os.chdir()` 鍜� `os.environ["DSH_SESSION_ROOT"]` 鏄�**杩涚▼绾у叏灞�鐘舵��**锛屼絾瀹冧滑琚�鏀惧湪 `_agent_lock` **澶栭潰**銆�

濡傛灉涓や釜娓呭皬鎼�璇锋眰鍚屾椂鍒拌揪锛�
- 璇锋眰 A 鎶� cwd/env 鍒囧埌 A 浼氳瘽
- 璇锋眰 B 鎶� cwd/env 鍒囧埌 B 浼氳瘽
- 璇锋眰 A 杩涘叆閿佹墽琛� `agent_loop` 鏃讹紝cwd/env 鍙�鑳藉凡缁忚�� B 鏀规帀

缁撴灉锛欰 鐨勫�硅瘽鍘嗗彶/鏂�鐐瑰彲鑳藉啓鍒� B 鐨勭洰褰曪紝鎴栬�� B 鍐欏埌 A 鐨勭洰褰曘��

淇�澶嶅缓璁�锛堜粎寤鸿��锛屼笉鏀癸級锛�
- 鎶� `os.chdir(session_root)` 鍜� `DSH_SESSION_ROOT` 鐨勮�剧疆/鎭㈠��**鍏ㄩ儴绉诲叆 `with _agent_lock:` 鍐呴儴**銆�
- 骞跺湪 `agent_loop` 璋冪敤鍓嶅悗淇濇寔 cwd/env 涓�鑷淬��

## 鍙戠幇 2锛堜腑锛夛細鏂囦欢宸ュ叿鍩哄骇浠嶆槸鍏ㄥ眬 `.runtime`锛屼笉鏄�浼氳瘽鐩�褰�

鏂囦欢锛歚tsinghua agent server/main.py` + `core/tools_runtime.py`

闂�棰橈細
- `WORKSPACE = .runtime` 鍦ㄥ�煎叆 core 鏃惰��鍥哄畾涓� `config.WORKDIR`
- `worktree_manager` 鐨勬牴鐩�褰曚篃鍥犳�ゅ浐瀹氫负 `.runtime`
- 铏界劧瀵硅瘽鍘嗗彶宸叉寜浼氳瘽闅旂�诲埌 `.runtime/sessions/<sessionId>/`锛屼絾 agent 鐢� `write_file` 绛夊伐鍏峰啓鏂囦欢鏃讹紝瀹為檯鍐欑殑鏄� `.runtime/` 鏍圭洰褰曪紝涓嶆槸 `sessions/<sessionId>/`

缁撴灉锛�
- 澶氫釜浼氳瘽濡傛灉閮藉啓 `output/hello.py`锛屼細浜掔浉瑕嗙洊
- 闄勪欢鏀堕泦鏄�鎵�鏁翠釜 `.runtime`锛屼篃浼氭妸鍒�鐨勪細璇濇枃浠朵竴璧峰甫涓�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 璁╂枃浠跺伐鍏峰熀搴т篃闅� `sessionId` 鍒囨崲鍒� `sessions/<sessionId>/`
- 鎴栨瘡涓�浼氳瘽浣跨敤鐙�绔嬪瓙杩涚▼锛堝儚 server_app 閭ｆ牱锛�

## 鍙戠幇 3锛堜綆锛夛細MOD 鍏抽敭璇嶈��鍒�

鏂囦欢锛歚tsinghua agent server/main.py` 鈫� `_is_mod_request()`

褰撳墠鍒ゆ柇锛�
```python
if any(k in low for k in ("mod", "/mod", "妯＄粍", "鎴戠殑涓栫晫", "forge")):
```

`"mod"` 鏄�瀛愪覆鍖归厤锛屽洜姝ょ敤鎴疯�� `model`銆乣modern`銆乣module`銆乣modification` 閮戒細瑙﹀彂 MOD 缃戦〉寮曞�硷紝鍙�鑳介�犳垚涓嶅繀瑕佹彁绀恒��

## 鍙戠幇 4锛堜綆锛夛細鍓嶇��妯″瀷鍒楄〃閲嶅��

鏂囦欢锛歚server_app/frontend/src/plugins/conversation.tsx`

```ts
const models = ['DeepSeek-V4-Flash-0731', 'DeepSeek-V4-Flash-0731', ...]
```

鍚屼竴涓�妯″瀷鍑虹幇涓ゆ�★紝涓� `store.ts` 鐨� `resolveModelConfig` 涔熸湁涓や釜瀹屽叏鐩稿悓鐨勫垽鏂�鍒嗘敮銆備笉鏄�鍔熻兘鎬ч敊璇�锛屼絾灞炰簬鍐椾綑銆�

## 璇存槑

- 浠ヤ笂鏄�棣栬疆蹇�閫熷贰鏌ョ粨鏋�
- 鍚庣画杞�娆′細缁х画妫�鏌ュ伐鍏� schema/handler 涓�鑷存�с�佸瓨鍌ㄨ矾寰勩�佸苟鍙戙�佸墠绔�鐘舵�佹満绛�

===== findings-round10.md =====
# Bug Audit Round 10

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 21锛堥珮锛夛細Agent 绯荤粺鎻愮ず璇嶆槸 Windows 鍛戒护瑙勫垯锛屼絾 8001 閮ㄧ讲鍦� Linux

鏂囦欢锛歚core/config.py`

- `SYSTEM_CHAT` 涓�鏄庣‘鍐欙細
  > "You are running on Windows cmd. You MUST use Windows command syntax."
  > 鐢� `dir` / `type` / `copy` / `del` / `rd` / `taskkill` / `netstat`

- `TEAMMATE_SYSTEM_PREFIX` 鍚屾牱鏄� Windows 瑙勫垯

- `docs/agent/TOOL_GUIDE.md` 涔熸槸 Windows 璇�娉�

浣嗕綘鐨� 8001 娓呭皬鎼�鏈嶅姟璺戝湪 **Ubuntu Linux** 鏈嶅姟鍣ㄤ笂锛宍core/tools_shell.run_bash()` 瀹為檯浣跨敤 `/bin/sh` 鎵ц�屽懡浠わ細
```python
subprocess.Popen(command, shell=True, ...)
```

褰卞搷锛�
- agent 鍦� Linux 涓婅��瑕佹眰浣跨敤 Windows 鍛戒护锛屼緥濡� `dir`銆乣type`銆乣del`銆乣taskkill`锛岃繖浜涘湪 Linux 涓婁笉瀛樺湪鎴栬�屼负涓嶅悓
- 鎵ц�� shell 宸ュ叿寰堝彲鑳介�戠箒澶辫触锛歚dir: command not found`銆乣taskkill: command not found`
- 杩欐槸褰撳墠 Linux 閮ㄧ讲涓嬬殑**涓ラ噸骞冲彴鐭涚浘**锛屾瘮鍗曠偣宸ュ叿 bug 褰卞搷闈㈡洿澶�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鏍规嵁杩愯�屽钩鍙板姩鎬侀�夋嫨绯荤粺鎻愮ず璇嶏紙Windows/Linux锛�
- 鎴栧湪 Linux 閮ㄧ讲鏃舵敞鍏� Linux 鐗堝懡浠よ�勫垯锛坄ls` / `cat` / `rm -rf` 绛夛紝骞跺悓姝ュ畨鍏ㄩ檺鍒讹級

---

## 璇存槑

- 鍚庣��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round10.md`

===== findings-round11.md =====
# Bug Audit Round 11

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 22锛堜腑锛夛細`MessageBus.read_inbox` 閬囨崯鍧� JSON 琛屼細鐩存帴宕╂簝

鏂囦欢锛歚core/tools_team.py`

```python
def read_inbox(self, name: str) -> list:
    ...
    lines = f.readlines()
    ...
    msgs = [json.loads(l) for l in lines if l.strip()]
```

娌℃湁瀵瑰崟琛� JSON 鍋� try/except銆傚�傛灉 `.team/inbox/<name>.jsonl` 鏌愪竴琛屽啓鍏ヤ腑鏂�/鎹熷潖锛宍json.loads` 鎶涘紓甯革紝鏁翠釜闃熷弸绾跨▼浼氬穿銆�

褰卞搷锛�
- 闃熷弸 Agent 鍥犱竴灏佸潖娑堟伅閫�鍑�
- 鍚庣画浠诲姟鏃犳硶缁х画

---

## 鍙戠幇 23锛堜腑锛夛細`TodoManager` 娌℃湁閿侊紝澶氶槦鍙嬪苟鍙戞洿鏂� todo 鍙�鑳戒簰鐩歌�嗙洊

鏂囦欢锛歚core/tools_tasks.py`

- `TodoManager.update()` 鐩存帴 `self.todos = items` + `_save()`
- 娌℃湁 `threading.Lock`

鍦ㄥ�氫釜 teammate 绾跨▼骞惰�屽伐浣滄椂锛屼袱涓�绾跨▼鍚屾椂璋冪敤 `todo` 宸ュ叿鍙�鑳戒簰鐩歌�嗙洊瀵规柟鍒楄〃锛屾垨鍐欏潖 `.todo.json`銆�

---

## 璇存槑

- 鍚庣��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round11.md`

===== findings-round12.md =====
# Bug Audit Round 12

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 24锛堜綆锛夛細`start_gradle_task` 鎵撳紑鐨勬棩蹇楁枃浠跺彞鏌勬湭鏄惧紡鍏抽棴

鏂囦欢锛歚core/gradletools.py`

```python
log_file = open(log_path, "a", encoding="utf-8", errors="replace")
proc = subprocess.Popen(..., stdout=log_file, ...)
```
`log_file` 娌℃湁 close锛屼緷璧� GC/杩涚▼閫�鍑哄悗鍥炴敹銆傝繘绋嬮暱鏃堕棿杩愯�屾椂鍙ユ焺浼氫繚鎸佹墦寮�锛涜櫧鐒跺奖鍝嶅皬锛屼絾灞炰簬璧勬簮绠＄悊闂�棰樸��

---

## 鍙戠幇 25锛堜綆锛夛細鍓嶇�� `api()` 瀵圭┖ JSON 鍝嶅簲澶勭悊涓嶇ǔ

鏂囦欢锛歚server_app/frontend/src/lib/api.ts`

```ts
if (ct.includes('application/json')) return (await res.json()) as T
```

濡傛灉鍚庣��杩斿洖 `200` + `Content-Type: application/json` 浣� body 涓虹┖锛宍res.json()` 浼氭姏寮傚父銆傜洰鍓嶆帴鍙ｅ熀鏈�閮戒細杩斿洖 JSON 瀵硅薄锛屽奖鍝嶅皬銆�

---

## 璇存槑

- 鍚庣��瀛愪唬鐞嗕粛鍦ㄨ繍琛�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round12.md`

===== findings-round13.md =====
# Bug Audit Round 13

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 26锛堜腑锛夛細`_session_stats` 姣忔�¤疆璇㈤兘浼氶亶鍘嗘暣涓� `mc_java_sources` 婧愮爜鏍�

鏂囦欢锛歚server_app/server.py` 鈫� `_session_stats()`

```python
for p in sess.mod_dir.rglob("*"):
    if p.is_file() and not any(
        part in (".worktrees", ".team", ".tasks", ".transcripts",
                 "__pycache__", ".git", "mc_java_sources")
        for part in p.relative_to(sess.mod_dir).parts
    ):
        file_count += 1
```

铏界劧鏈�缁堜細璺宠繃 `mc_java_sources`锛屼絾 `rglob("*")` **浠嶇劧浼氬厛閬嶅巻**鏁翠釜婧愮爜鏍戯紙涓婁竾鏂囦欢锛夛紝鐒跺悗鍐嶈繃婊ゃ�傚墠绔�姣� 2 绉掕疆璇� `/api/session` 鎴� `/api/status` 鏃堕兘浼氳Е鍙戜竴娆°��

褰卞搷锛�
- 澶ч噺鏃犺皳 IO/閬嶅巻
- 2G 灏忔湇鍔″櫒涓婂彲鑳芥嫋鎱㈡帴鍙ｅ搷搴�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 閬嶅巻鏃剁洿鎺� `rglob` 鎺掗櫎 `mc_java_sources`锛堝�備娇鐢� `os.walk` 鍓�鏋濓級锛屾垨缂撳瓨缁熻�＄粨鏋溿��

---

## 鍙戠幇 27锛堜腑锛夛細`get_status` 姣忔�¤�绘暣涓� run.log 鍐嶅彇灏� 20000 瀛楃��

鏂囦欢锛歚server_app/server.py` 鈫� `get_status()`

```python
log_tail = sess.log_path.read_text(encoding="utf-8", errors="replace")[-20000:]
```

濡傛灉 run.log 澧為暱鍒板嚑 MB/鍑犲崄 MB锛屾瘡娆¤疆璇㈤兘浼氬畬鏁磋�诲叆鍐呭瓨锛屽啀鎴�鍙栧熬閮ㄣ��

褰卞搷锛�
- 鍐呭瓨/IO 娴�璐�
- 鏃ュ織瓒婂ぇ瓒婃槑鏄�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鐢� seek 鍒版枃浠舵湯灏惧線鍓嶈�诲浐瀹氬瓧鑺傦紝鍙�璇诲熬閮ㄣ��

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round13.md`

===== findings-round14.md =====
# Bug Audit Round 14

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 28锛堜綆锛夛細`_save_session_log` 浣跨敤 cwd 鐩稿�硅矾寰勶紝mod 妯″紡涓嬩簨浠舵棩蹇椾笌浼氳瘽鏍逛笉涓�鑷�

鏂囦欢锛歚core/agent.py`

```python
path = os.path.join(".chat", "session_events.jsonl")
```

鍦� server_app mod 妯″紡涓嬶紝`agent_loop` 鐨� cwd 鏄� `<session>/mod/`锛岃�屽�硅瘽鍘嗗彶/鏂�鐐瑰瓨鍦� `<session>/.chat/`锛堢敱 `DSH_SESSION_ROOT` 鍐冲畾锛夈��

缁撴灉锛�
- 浜嬩欢鏃ュ織鍐欏湪 `mod/.chat/session_events.jsonl`
- 瀵硅瘽鍘嗗彶鍐欏湪 `<session>/.chat/conversation.jsonl`
- 涓よ�呬笉鍦ㄥ悓涓�涓� `.chat` 鐩�褰曪紝鍥炴斁/鏌ョ湅鏃朵笉缁熶竴

褰卞搷锛氳緝浣庯紝浣嗙洰褰曡��涔変笉涓�鑷达紝鏄撴贩娣嗐��

---

## 鍙戠幇 29锛堜綆锛夛細`run_web_fetch` 绂佺敤閲嶅畾鍚戯紝閬囧埌璺宠浆 URL 鍙�鑳藉け璐�

鏂囦欢锛歚core/tools_web.py`

```python
r = httpx.get(url, timeout=20, follow_redirects=False)
```

寰堝�氱綉椤典細 301/302 璺宠浆锛涘叧闂�閲嶅畾鍚戝悗鍙�鑳芥嬁鍒� 3xx 鑰屼笉鏄�姝ｆ枃銆�

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round14.md`

===== findings-round15.md =====
# Bug Audit Round 15

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 30锛堜腑锛夛細閲嶅�� spawn 涓�涓� idle 闃熷弸浼氬惎鍔ㄩ噸澶嶇嚎绋嬶紝鏃х嚎绋嬫湭鍋滄��

鏂囦欢锛歚core/tools_team.py` 鈫� `TeammateManager.spawn()`

```python
if name in self.team:
    if self.team[name].status == "shutdown":
        ...
    elif self.team[name].status == "idle":
        self.team[name].system_prompt = system_prompt
        self._save_team_config()
        logger.info(f"Teammate {name} 宸插瓨鍦�(idle)锛岄噸鍚�绾跨▼")
    else:
        return error
thread = threading.Thread(target=self._teammate_loop, args=(name,), daemon=True)
self.threads[name] = thread
thread.start()
```

褰撻槦鍙嬬姸鎬佷负 `idle` 鏃讹細
- 鏃х嚎绋嬪叾瀹炶繕鍦� `_teammate_loop` 閲岃疆璇㈡敹浠剁��/鐪嬫澘锛坕dle 绾跨▼瀛樻椿鏈�闀� 60 绉掞級
- 杩欓噷娌℃湁鍋滄�㈡棫绾跨▼锛屽張鐩存帴 `start()` 涓�涓�鏂扮嚎绋�

缁撴灉锛�
- 鍚屼竴涓�闃熷弸鍚嶅悓鏃跺瓨鍦ㄤ袱涓�绾跨▼
- 涓や釜绾跨▼閮戒細璇诲悓涓�涓�鏀朵欢绠便�佽�ら�嗗悓涓�涓�浠诲姟鏉匡紝鍙�鑳介噸澶嶅�勭悊浠诲姟

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- spawn idle 鏃跺厛 `shutdown(name)` 骞� `join` 鏃х嚎绋嬶紝鎴栬�剧疆鍋滄��浜嬩欢锛屽啀鍚�鍔ㄦ柊绾跨▼銆�

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round15.md`

===== findings-round16-backend.md =====
# Bug Audit Round 16 鈥斺�� 鍚庣��瀛愪唬鐞嗗�¤�＄粨鏋�

> 鏉ユ簮锛氬悗绔�瀹¤�″瓙浠ｇ悊 444328cc 杩斿洖缁撴灉銆�
> 鍙�璇诲�¤�★紝鏈�淇�鏀逛换浣曟枃浠躲��

## 楂樹弗閲嶅害

### 1. 璺�寰勭┛瓒� / 浠绘剰鐩�褰曞垹闄わ紙鍚�璺ㄧ敤鎴峰垹闄わ級銆愬凡楠岃瘉銆�
- 鏂囦欢锛歚server.py` 鐨� `_purge_session_dir`锛�301-305锛夈�乣delete_history`锛�1283-1291锛夈�乣delete_history_batch`锛�1307-1318锛�
- `session_id` 鏉ヨ嚜瀹㈡埛绔�锛屾棤鏍煎紡/褰掑睘鏍￠獙锛岀洿鎺ユ嫾 `SESSIONS_DIR / session_id` 鍚� `shutil.rmtree`
- 渚嬪�� `DELETE /api/history?session_id=..` 鍙�鍒犻櫎 `data/` 鐩�褰�
- 璺ㄧ敤鎴凤細session 瀛樺湪浣嗕笉灞炰簬褰撳墠鐢ㄦ埛鏃讹紝`else` 鍒嗘敮浠嶄細 `_purge_session_dir` 鍒犻櫎璇ョ洰褰�
- 楠岃瘉锛歚bugaudit/test_server_purge_path_traversal.py` 瀹炴祴 `_purge_session_dir("..")` 鍒犻櫎涓存椂鐖剁洰褰曪紝纭�璁ゆ垚绔�

## 涓�涓ラ噸搴�

### 2. `get_result` 鐘舵�佹満閿欒��锛歱roc=None 涓�寰嬫姤 running
### 3. 浜嬩欢娴佹父鏍囧湪鏃ュ織鎴�鏂�鍚庡崱姝伙紝浜嬩欢姘镐笉鏇存柊
### 4. 浜嬩欢娴佸�為噺璇荤殑绔炴�侊細鏂囦欢澧為暱鏃堕噸澶嶄簨浠�
### 5. 浜嬩欢 id 璺ㄨ疆涓嶅敮涓�锛堟瘡鎵归兘浠� ev-0 缂栧彿锛�
### 6. `[tool-result]` / `[todo]` 鍧楀悗绱ч偦鐨勪簨浠惰�岃��鍚炴帀
### 7. `get_events` 鏈�瀹炵幇鈥滀笉浼� cursor 鐩存帴缁�浼犫�濓紝浼氫粠澶撮噸鏀�
### 8. `get_status` 鐢� time.time() 瑕嗙洊 daemon 浼氳瘽 finished_at

## 浣庝弗閲嶅害

### 9. 鍏ㄥ眬涓嬭浇閿佽法浼氳瘽涓茶��
### 10. 瀛愯繘绋嬫棩蹇楁枃浠跺彞鏌勬湭鏄惧紡鍏抽棴
### 11. finalize_known_issues 鍒嗛殧绗︽�讳唬鐮�
### 12. finalize_error_list 鏃� try 璇诲彇鐩�鏍囨枃浠�

## 琛ュ厖

- sessions 瀛楀吀/瀛楁�靛湪澶氱嚎绋� worker 涓�璇诲啓鏃犻攣锛屽瓨鍦ㄦ暟鎹�绔炰簤椋庨櫓

===== findings-round17-logevent.md =====
# Bug Audit Round 17 鈥斺�� log_events 浜嬩欢瑙ｆ瀽楠岃瘉

> 鏈�杞�鍙�璇� + 鏂板�為獙璇佹祴璇曪紝鏈�淇�鏀逛换浣曟枃浠躲��

## 鍙戠幇 31锛堜腑锛屽凡楠岃瘉锛夛細`[tool-result]` 鍧椾細鍚炴帀绱ч殢鍏跺悗鐨勪簨浠惰��

鏂囦欢锛歚core/../server_app/log_events.py` 鈫� `_parse_run_block`

鍘熷洜锛�
- `[tool-result]` 鍒嗘敮鏀堕泦鍒颁笅涓�涓� `[` 寮�澶磋�屽墠鍋滄��锛宍i = j`
- 寰�鐜�鏈�灏鹃�氱敤鐨� `i += 1` 浼氭妸 `j` 鎸囧悜鐨勯偅涓�琛岀洿鎺ヨ烦杩�

楠岃瘉锛歚bugaudit/test_log_events_tool_result_skip.py`

杈撳叆锛�
```
[tool] bash echo hi
[tool-result] success
output line
[鎬濊�僝 next thought
```

瀹為檯杈撳嚭浜嬩欢鍙�鏈夛細
```
tool_call | echo hi
tool_result | success ...
```

`[鎬濊�僝 next thought` 涓㈠け銆�

褰卞搷锛�
- 浜嬩欢娴佷笉瀹屾暣锛屽墠绔�鐪嬩笉鍒� tool-result 鍚庣殑绗�涓�鏉℃�濊��/浜嬩欢
- 鏃ュ織/浜嬩欢灞曠ず涓嶇ǔ瀹�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round17-logevent.md`
- 楠岃瘉鑴氭湰鏂板�烇細`test_log_events_tool_result_skip.py`

===== findings-round18.md =====
# Bug Audit Round 18

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 32锛堜腑锛夛細`search_api` 鐨� `context_lines` 鍙傛暟琚�蹇界暐锛屽疄闄呬笉鐢熸晥

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_search_api()`

```python
def run_search_api(symbol, path="mc_java_sources", max_results=10, context_lines=0):
    ...
    out = run_grep(symbol, path=path, glob_filter="*.java", max_results=max_results)
```

- `run_search_api` 鎺ユ敹 `context_lines`锛屼絾璋冪敤 `run_grep` 鏃�**娌℃湁浼� `context_lines`**
- 鑰� `run_grep` 鏈�韬�鏄�鏀�鎸� `context_lines` 鐨�
- `search_api` 鐨� OpenAI schema 涔熷叕寮�浜� `context_lines`

缁撴灉锛�
- 妯″瀷/鐢ㄦ埛浠ヤ负浼犱簡 `context_lines` 鑳界湅鍒颁笂涓嬫枃锛屽疄闄呮案杩滅湅涓嶅埌
- 灞炰簬鈥滃嚱鏁板弬鏁版毚闇蹭絾瀹炵幇澶辨晥鈥濈殑 bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round18.md`

===== findings-round19.md =====
# Bug Audit Round 19

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 33锛堜綆锛夛細`run_bash` 鐨勫嵄闄╁懡浠よ繃婊ゆ妸鏅�閫氬崟璇� `format` 涔熸嫤鎴�

鏂囦欢锛歚core/tools_shell.py`

```python
dangerous = ["format", "diskpart", "reg delete", "shutdown", ...]
if any(d in command.lower() for d in dangerous):
    return "Error: Dangerous command blocked"
```

闂�棰橈細
- 浣跨敤瀛愪覆鍖归厤 `"format" in command.lower()`
- 鍛戒护濡� `echo format string`銆乣python format.py`銆乣grep format` 閮戒細琚�璇�鍒や负鍗遍櫓鍛戒护骞舵嫤鎴�
- 鍚屾牱 `shutdown` 瀛愪覆浼氳��浼� `shutdown_teammate`? 閭ｆ槸宸ュ叿鍚嶏紝涓嶆槸 shell 鍛戒护锛涗絾 shell 閲� `echo shutdown` 涔熶細琚�鎷�

褰卞搷锛�
- 姝ｅ父鍛戒护琚�璇�鎷︽埅
- 灞炰簬璇�鎶�/鍔熻兘鍙楅檺闂�棰橈紝涓嶆槸瀹夊叏婕忔礊

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round19.md`

===== findings-round2.md =====
# Bug Audit Round 2

> 鏈�杞�鍙�璇诲贰鏌� + 鏂板�為獙璇佹祴璇曪紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 5锛堥珮锛屽凡楠岃瘉锛夛細TaskManager.create() 骞跺彂浼氬垱寤洪噸澶� task_id

鏂囦欢锛歚core/tools_tasks.py`

`TaskManager.create()` 娌℃湁浣跨敤 `self._lock`锛�
```python
def create(self, subject, blocked_by=None):
    ...
    task = {"id": self._next_id, ...}
    ...
    self._write_task(task)
    self._next_id += 1
```

楠岃瘉鏂瑰紡锛氭柊澧� `bugaudit/test_taskmanager_race.py`锛岀敤 2 涓�绾跨▼鍚勫垱寤� 50 涓�浠诲姟銆�

缁撴灉锛�
- 涓や釜绾跨▼鍑虹幇閲嶅�� task_id锛歚[1, 3, 11, 20, 22, 34, 58, 65]`
- 鍚堣�￠噸澶� 8 涓� ID

褰卞搷锛�
- agent 澶氫釜 teammate / 澶氱嚎绋嬪苟鍙戝垱寤轰换鍔℃椂锛屼换鍔� ID 浼氬啿绐侊紝瀵艰嚧浠诲姟浜掔浉瑕嗙洊鎴栫姸鎬侀敊涔便��
- 杩欐槸鐪熷疄鐨勫苟鍙� bug锛屼笉鏄�鐞嗚�洪棶棰樸��

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦� `create()` 鍐呭姞 `with self._lock:`锛屾妸璇诲彇 `_next_id`銆佸啓鏂囦欢銆佽嚜澧炴斁鍒伴攣鍐呫��

---

## 鍙戠幇 6锛堜腑锛夛細妯℃澘鐗堟湰涓� MC 婧愮爜鐗堟湰涓嶅尮閰�

鏂囦欢锛歚server_app/server.py` 鈫� `_copy_template()`

```python
if version.startswith("26.2"):
    mc_sources = PROJECT_ROOT / "mc_java_sources_26.2"
else:
    mc_sources = PROJECT_ROOT / "mc_java_sources_1.21.11"
```

浣嗗�傛灉鐢ㄦ埛閫夋嫨 `forge-1.21.9` 鎴� `forge-1.21.10`锛屼唬鐮佷粛鐒跺�嶅埗 `mc_java_sources_1.21.11` 浣滀负鍙傝�冩簮鐮併��

褰卞搷锛�
- agent 鍦� 1.21.9/1.21.10 浼氳瘽涓�鏌ュ埌鐨� API/绫诲悕鍙�鑳芥潵鑷� 1.21.11锛屽�艰嚧閿欒��鍐欐硶銆�
- 椤圭洰鐩�鍓嶄篃缂哄皯 `mc_java_sources_1.21.9` / `mc_java_sources_1.21.10` 鐩�褰曘��

---

## 鍙戠幇 7锛堜腑锛夛細auth_store JSON 鍐欐枃浠舵棤閿�

鏂囦欢锛歚server_app/auth_store.py`

`_save_json()` 鐩存帴 `write_text`锛屾病鏈夋枃浠堕攣/鍘熷瓙鍐欍�傚�氫釜璇锋眰鍚屾椂娉ㄥ唽/鐧诲綍/鏇存柊鍘嗗彶鏃讹紝鍙�鑳藉彂鐢燂細
- 涓㈠け鏇存柊
- 璇诲埌鍗婃埅 JSON锛堣櫧鐒舵�傜巼浣庯級

褰卞搷锛氬�氱敤鎴峰苟鍙戜笅璁よ瘉/鍘嗗彶鏁版嵁鍙�鑳戒笉涓�鑷淬��

---

## 璇存槑

- 绗�涓�杞�鎶ュ憡瑙� `bugaudit/findings-round1.md`
- 娴嬭瘯鏂囦欢 `bugaudit/test_taskmanager_race.py` 淇濈暀浣滀负楠岃瘉鍑�璇�

===== findings-round20.md =====
# Bug Audit Round 20

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 34锛堜腑锛夛細闃熷弸璋冪敤 `claim_task` 鏃惰韩浠芥湭娉ㄥ叆锛岃�ら�嗕汉鍙樻垚 `unknown`

鏂囦欢锛歚core/tools_team.py` 鈫� `_run_teammate_agent()`

```python
# 鍙�瀵� submit_plan 娉ㄥ叆韬�浠�
if tc.function.name == "submit_plan":
    args["_agent_id"] = agent_id
handler = TOOL_HANDLERS.get(tc.function.name)
```

`claim_task` 娌℃湁鍍� `submit_plan` 閭ｆ牱娉ㄥ叆 `_agent_id`銆�

鑰� `core/tools_tasks.py` 鐨� `_claim_task`锛�
```python
agent = kw.get("_agent_id", "unknown")
ok = task_manager.claim(kw["task_id"], agent)
```

缁撴灉锛�
- 闃熷弸浠庝换鍔＄湅鏉� `claim_task` 鍚庯紝浠诲姟 owner 琚�鍐欐垚 `"unknown"`
- 澶氫釜闃熷弸鍚屾椂鎵�鐪嬫澘鏃舵棤娉曞尯鍒嗚皝璁ら�嗕簡浠诲姟锛岃嚜娌昏�ら�嗘満鍒跺悕瀛樺疄浜�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦� `_run_teammate_agent` 鎵ц�� `claim_task` 鏃跺悓鏍锋敞鍏� `args["_agent_id"] = agent_id`

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round20.md`

===== findings-round21.md =====
# Bug Audit Round 21

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 35锛堜綆锛夛細SkillLoader 鎵�鎻忓彧璇绘枃浠跺ご 8KB锛岃秴澶� frontmatter 浼氳��鎴�鏂�

鏂囦欢锛歚core/tools_skills.py` 鈫� `SkillLoader._read_head()`

```python
def _read_head(path: str, max_bytes: int = 8192) -> str:
    ...
```

- 鍙�璇诲墠 8KB 鏉ヨВ鏋� YAML frontmatter
- 濡傛灉鏌愪釜 `SKILL.md` 鐨� frontmatter锛坄---` 鍐咃級瓒呰繃 8KB锛岃В鏋愪細寰楀埌涓嶅畬鏁� YAML
- `yaml.safe_load` 鍙�鑳芥姤閿欐垨瑙ｆ瀽鍑洪敊璇� meta锛屾妧鑳借��涓㈠純/琛屼负寮傚父

褰卞搷锛�
- 鐩�鍓嶆妧鑳� frontmatter 閮借緝灏忥紝褰卞搷浣�
- 浣嗗睘浜庢綔鍦ㄨВ鏋愯竟鐣� bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round21.md`

===== findings-round22.md =====
# Bug Audit Round 22

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 36锛堜腑锛夛細`process_manager.stop(handle)` 鏃犳硶鍋滄�� manifest 閲岀殑瀛ゅ効杩涚▼

鏂囦欢锛歚core/process_manager.py`

```python
def stop(handle, force=True):
    info = _PROCESSES.get(handle)
    if not info:
        return {"handle": handle, "ok": False, "message": f"No tracked process '{handle}'"}
    ...
```

- `_PROCESSES` 鏄�鍐呭瓨娉ㄥ唽琛�
- `list_info(base)` 浼氫粠 manifest 鎭㈠�嶅�ゅ効杩涚▼骞舵爣璁� `restored_from_manifest=True`
- 浣� `stop(handle)` 鍙�鏌ュ唴瀛� `_PROCESSES`锛屼笉鏌� manifest

缁撴灉锛�
- 鏈嶅姟閲嶅惎鍚庯紝涔嬪墠 `run/` 涓� manifest 閲岀殑 mc 杩涚▼浠嶆椿鐫�
- `mc_status` 鑳界湅鍒板畠锛屼絾 `stop_mc_process(handle='mc-server')` 浼氭姤 鈥淣o tracked process鈥濓紝鏃犳硶鍋滄��
- 鍙�鏈� `stop_all(base)` 鎵嶄細澶勭悊瀛ゅ効

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- `stop(handle)` 鍦ㄥ唴瀛樻壘涓嶅埌鏃讹紝涔熷幓 `_load_manifest(base)` 涓�鏌ユ壘 pid 骞� kill

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round22.md`

===== findings-round23.md =====
# Bug Audit Round 23

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 37锛堜腑锛夛細`MessageBus.send` 闃熷弸鍚嶆湭鏍￠獙锛屽彲鑳借矾寰勭┛瓒婂啓鍏�

鏂囦欢锛歚core/tools_team.py` 鈫� `MessageBus.send()`

```python
path = os.path.join(self.inbox_dir, f"{to_name}.jsonl")
with open(path, "a", encoding="utf-8") as f:
    f.write(...)
```

- `to_name` 鏉ヨ嚜 `send_to_teammate` / `spawn_teammate` 鐨勬ā鍨�/鐢ㄦ埛杈撳叆
- 娌℃湁闄愬埗 `..`銆乣/`銆乣\` 绛夊瓧绗�
- 濡傛灉 `to_name` 涓� `../evil`锛屾秷鎭�鏂囦欢浼氬啓鍒� `.team/inbox/../evil.jsonl`锛堝嵆 `.team/evil.jsonl`锛夌敋鑷虫洿涓婂眰

褰卞搷锛�
- 璺�寰勭┛瓒婂啓鍏�
- 鍦ㄩ槦鍙嬪悕鍙�鎺х殑鍦烘櫙涓嬪彲鍚戦�勬湡澶栫洰褰曞啓鏂囦欢
- 涓ラ噸绋嬪害涓�锛堝洜涓烘槸 agent 鍐呴儴宸ュ叿锛屼笉鏄�澶栭儴鐩存帴杈撳叆锛屼絾妯″瀷鍙�鑳借��璇卞�兼瀯閫犳伓鎰忓悕瀛楋級

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 瀵� `name` / `to_name` 鍋氬畨鍏ㄥ瓧绗︽牎楠岋紙濡� `[A-Za-z0-9_-]+`锛�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round23.md`

===== findings-round24.md =====
# Bug Audit Round 24

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 38锛堜腑锛夛細`web_fetch` / `download_file` 鏃� SSRF 闃叉姢

鏂囦欢锛歚core/tools_web.py`銆乣core/tools_download.py`

- `run_web_fetch(url)` 鐩存帴 `httpx.get(url, ...)`锛屼笉鏍￠獙鍩熷悕/IP
- `download_file(url, dest)` 鍚屾牱鐩存帴涓嬭浇浠绘剰 URL

褰卞搷锛�
- agent 鍙�琚�璇卞�艰�锋眰鍐呯綉鍦板潃锛屼緥濡� `http://169.254.169.254/latest/meta-data/`锛堜簯鍏冩暟鎹�锛�
- 澶氱敤鎴风綉椤�/娓呭皬鎼�鍦烘櫙涓嬶紝妯″瀷鍙�鑳借�� prompt 娉ㄥ叆鍘昏�块棶鍐呯綉闈為�勬湡璧勬簮
- 灞炰簬 SSRF 椋庨櫓

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 澧炲姞鍩熷悕/IP 鐧藉悕鍗曟垨鑷冲皯灞忚斀鍐呯綉/淇濈暀鍦板潃/浜戝厓鏁版嵁缃戞��
- 鎴栧�� `web_fetch` 鍋� URL scheme 鏍￠獙锛堜粎 http/https锛夊拰閲嶅畾鍚戠洰鏍囨牎楠�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round24.md`

===== findings-round25.md =====
# Bug Audit Round 25

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 39锛堜綆锛夛細`run_read` 杈撳嚭瓒呰繃 50000 瀛楃�︽椂闈欓粯鎴�鏂�锛屾棤鏍囪��

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_read()`

```python
return "\n".join(lines)[:50000]
```

- 瓒呰繃 50000 瀛楃�︾洿鎺ユ埅鏂�
- 娌℃湁杩藉姞 `... (truncated)` 涔嬬被鐨勬彁绀�

褰卞搷锛�
- agent 涓嶇煡閬撴枃浠惰��鎴�鏂�锛屽彲鑳借��浠ヤ负璇诲埌浜嗗畬鏁村唴瀹�
- 灞炰簬淇℃伅涓㈠け/璇�瀵肩被闂�棰�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round25.md`

===== findings-round26.md =====
# Bug Audit Round 26

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 40锛堜腑锛夛細`cleanup_workspace` 涓嶉伒瀹� read-only 娌欑�憋紝浠嶅彲鍒犻櫎鏂囦欢

鏂囦欢锛歚core/tools_cleanup.py`

```python
def cleanup_workspace(mode="cache"):
    ...
    for name in dirs_to_remove:
        if p.is_dir():
            _rmtree(p)
    ...
```

- 娌℃湁妫�鏌� `_sandbox_mode()`
- 鍗充娇娌欑�辫�句负 `read-only`锛宍cleanup_workspace` 浠嶈兘鍒犻櫎 `build/`銆乣.gradle/`銆佺敋鑷� `run/`銆乣.tasks/` 绛夌洰褰�

褰卞搷锛�
- 涓庘�滃彧璇绘矙绠扁�濊��涔夊啿绐�
- 濡傛灉鏈�鏉� 8001 鍒囨垚 read-only 妯″紡锛宎gent 浠嶅彲閫氳繃璇ュ伐鍏峰垹闄ゆ枃浠�
- 褰撳墠 8001 鏄� workspace-write锛屽奖鍝嶆湁闄愶紝浣嗗睘浜庢矙绠变竴鑷存�� bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round26.md`

===== findings-round27.md =====
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

===== findings-round29.md =====
# Bug Audit Round 29

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 42锛堜腑锛夛細agent 鍙�鍏抽棴 AUTO_MODE锛屼箣鍚� `ask_user_question` 浼氬湪娓呭皬鎼�/鏃� UI 鐜�澧冮樆濉�

鏂囦欢锛歚core/tools_auto.py`銆乣core/tools_ask.py`

- `set_auto_mode(enabled)` 鍏佽�告ā鍨嬪叧闂�鑷�鍔ㄦā寮�
- 娓呭皬鎼� 8001 鏈嶅姟娌℃湁鈥滈棶绛斿崱鐗団�濋�氶亾
- 鑻� agent 璋冪敤 `set_auto_mode(false)` 鍚庡啀璋冪敤 `ask_user_question`锛屼細杞�璇� `answer.json` 鏈�澶� 5 鍒嗛挓锛屾湡闂磋�锋眰闀挎椂闂存寕璧�

褰卞搷锛�
- 涓�娆￠敊璇�鐨� `set_auto_mode(false)` 鍙�鑳藉�艰嚧瀵硅瘽鍗′綇
- 灞炰簬杩愯�岄�庨櫓/婊ョ敤闈�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦ㄦ竻灏忔惌鍏ュ彛寮哄埗 `AUTO_MODE=True` 涓嶅彲琚�妯″瀷鍏抽棴
- 鎴栧湪 `set_auto_mode` 涓�绂佹�㈠湪鏃犻棶绛� UI 鐜�澧冨叧闂�

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round29.md`
- 鎬绘姤鍛婏細`SUMMARY.md`锛�42 椤癸級

===== findings-round3.md =====
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

===== findings-round4.md =====
# Bug Audit Round 4

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 10锛堜腑锛夛細`inject_pending_requests` 姣忚疆閲嶅�嶈拷鍔狅紝涓嶅幓閲�

鏂囦欢锛歚core/protocol.py`

```python
def inject_pending_requests(messages: list, agent_id: str) -> None:
    ...
    if not parts:
        return
    messages.append({"role": "user", "content": "\n".join(["<pending-requests>"] + parts + ["</pending-requests>"])})
```

`agent_loop` 姣忚疆閮戒細璋冪敤 `inject_pending_requests(messages, "leader")`銆�

濡傛灉鏌愭潯璁″垝瀹℃壒璇锋眰涓�鐩� pending锛堟瘮濡傛ā鍨嬭繛缁�澶氳疆璋冪敤宸ュ叿娌″幓瀹℃壒锛夛紝姣忎竴杞�閮戒細寰�娑堟伅鍒楄〃閲�**鍐嶈拷鍔犱竴浠�** `<pending-requests>` 鍧楋紝鏃х殑涓嶄細琚�鏇挎崲/娓呯悊銆�

褰卞搷锛�
- 涓婁笅鏂囪��閲嶅�嶅崗璁�鍧楁拺澶�
- 妯″瀷鍙�鑳借��閲嶅�嶄俊鎭�骞叉壈
- 闀挎椂闂翠换鍔″�规槗鑶ㄨ儉

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 绫讳技 `<pending-requests>` 浣跨敤 `_replace_runtime_slot` 閫昏緫锛氬厛绉婚櫎鏃у潡鍐嶈拷鍔犳柊鍧椼��

---

## 鍙戠幇 11锛堜腑锛夛細鍓嶇�� `poll()` 鏃犱覆琛屽寲锛屼簨浠跺彲鑳介噸澶嶈拷鍔�

鏂囦欢锛歚server_app/frontend/src/lib/session.ts`

`poll()` 鏄� async锛屼絾璋冪敤鏂瑰彲鑳藉悓鏃惰Е鍙戯細
- `sendPrompt` 閲� `void poll()`
- `startPolling` 鐨勫畾鏃跺櫒

涓や釜 `poll()` 骞跺彂鎵ц�屾椂锛屽彲鑳芥嬁鍒板悓涓�涓� `cursor`锛岄兘鍘绘媺鍚屼竴鎵� events锛岀劧鍚庡垎鍒� `setState({ events: [...state.events, ...ev.events] })`銆�

褰卞搷锛�
- 浜嬩欢娴侀噸澶嶆樉绀�
- 鐘舵�佹洿鏂颁簰鐩歌�嗙洊锛坙ast-write-wins锛夊彲鑳戒涪浜嬩欢

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍔犱竴涓� `pollingInFlight` 鏍囧織鎴栫敤涓�涓�涓茶�� Promise 閾撅紝閬垮厤骞跺彂 poll銆�

---

## 鍙戠幇 12锛堜綆锛夛細閮ㄥ垎宸ュ叿鍦� Linux 鏈嶅姟鍣ㄤ笂涓嶅彲鐢�锛圵indows-only锛�

鏂囦欢锛歚core/tools_game.py`銆乣core/tools_vision.py`

- `press_key` / `type_text` / `game_input` 浣跨敤 `ctypes.windll.user32`锛屽彧鏀�鎸� Windows
- `run_screenshot` 浣跨敤 `PIL.ImageGrab.grab()`锛屽湪鏃犳�岄潰 Linux 鏈嶅姟鍣ㄤ笂閫氬父涓嶅彲鐢�

褰卞搷锛�
- 娓呭皬鎼� 8001 閮ㄧ讲鍦� Linux 鏃讹紝濡傛灉 agent 璋冪敤杩欎簺宸ュ叿浼氳繑鍥為敊璇�
- 涓嶅奖鍝嶄富娴佺▼锛屼絾鑳藉姏涓庡钩鍙颁笉鍖归厤

---

## 璇存槑

- 鍓嶅嚑杞�鎶ュ憡瑙� `bugaudit/findings-round{1,2,3}.md`
- 鍓嶇��瀛愪唬鐞嗗�¤�＄粨鏋滃緟杩斿洖锛屽洖鏉ュ悗鎴戜細骞跺叆涓嬩竴杞�鎶ュ憡

===== findings-round5.md =====
# Bug Audit Round 5

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 13锛堥珮锛夛細MOD 鎶�鑳藉姞杞借�勫垯鑷�鐩哥煕鐩�

鏂囦欢瀵规瘮锛�

- `core/config.py` SYSTEM_MOD锛�
  > "Before writing ANY MOD Java/resource, load the most relevant skill with load_skill"
  > HARD RULES: "SKILLS FIRST (MOD) ... Skills are the PRIMARY reference"
  > "Before starting any task: `load_skill` the most relevant skill first"

- `docs/agent/TOOL_GUIDE.md` Appendix F锛�
  > "Skills are reference material, not gatekeepers. There is NO mandatory skill load."
  > "There is NO mandatory `<skill-source>` citation after changes."

杩欎袱浠芥枃妗ｉ兘浼氳繘鍏� agent 鐨勫伐浣滃尯/涓婁笅鏂囷細
- SYSTEM_MOD 鍦ㄤ富寰�鐜� system prompt 閲�
- TOOL_GUIDE.md 鐢� `server.py` 澶嶅埗杩涗細璇濆伐浣滃尯锛宎gent 鍙� `read_file` 璇诲埌

褰卞搷锛�
- agent 浼氭敹鍒颁簰鐩哥煕鐩剧殑鎸囦护锛氣�滃繀椤� load_skill鈥� vs 鈥滀笉鏄�寮哄埗鈥�
- 鍙�鑳藉�艰嚧 agent 琛屼负涓嶇ǔ瀹氾細鏈夌殑浼氳瘽涓ユ牸鍔犺浇鎶�鑳斤紝鏈夌殑浼氳瘽鐩存帴鍐欎唬鐮�
- 瀵光�渟kill-first 绾�寰嬧�濊繖涓�鏍稿績璁捐�℃潵璇达紝杩欐槸鏄庣‘鐭涚浘

---

## 鍙戠幇 14锛堜綆锛夛細compact 鍙�鑳芥妸鍒濆�嬩换鍔￠敋鐐归噸澶嶅甫鍏�

鏂囦欢锛歚core/compact.py` 鈫� `auto_compact()`

```python
region = messages[:keep_from]   # 鍖呭惈绗�涓�鏉� user 娑堟伅锛坅nchor锛�
summary = summarize_region(region)
...
if anchor is not None:
    new_messages.append(anchor)   # 鍘熷�� anchor
new_messages.append({"role": "user", "content": "..." + summary + "..."})
```

鍘熷�� anchor 鏃㈣��鎽樿�佽繘 summary锛屽張琚�鍘熸牱淇濈暀锛屽彲鑳藉嚭鐜颁俊鎭�閲嶅�嶃�傚奖鍝嶈緝灏忋��

---

## 鍙戠幇 15锛堜綆锛夛細WorktreeManager `_load_index` 閮ㄥ垎璺�寰勬棤閿�

鏂囦欢锛歚core/worktree.py`

`_load_index()` 鐩存帴璇绘枃浠讹紝娌℃湁缁熶竴鍔� `_io_lock`锛沗_save_index` 鏈夐攣銆傚苟鍙戣��+鍐欐椂鍙�鑳借�诲埌鍗婃埅 JSON锛堣櫧鐒舵�傜巼浣庯級銆�

---

## 璇存槑

- 鍓嶇��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round5.md`

===== findings-round6.md =====
# Bug Audit Round 6

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 16锛堜腑锛夛細`search_api` 鍦ㄦ病鏈夊姞杞戒换浣曟妧鑳芥椂浼氱洿鎺ユ嫆缁濇墽琛�

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_search_api()`

```python
if not any_loaded():
    return "Hint: You have not loaded any skill yet. Please load_skill first ..."
```

闂�棰橈細
- 杩欐槸涓� MOD鈥渟kill-first鈥濊�捐�＄殑
- 浣嗗湪娓呭皬鎼� Chat 妯″紡涓嬶紝agent 鍙�鑳藉彧鏄�鏅�閫氶棶绛旓紝杩樻病鍔犺浇鎶�鑳藉氨鎯虫悳绱� MC 婧愮爜锛屼細琚�杩欎釜 gate 鎸′綇
- 瀵艰嚧 `search_api` 鍦ㄦ煇浜涙�ｅ父鍦烘櫙涓嬩笉鍙�鐢�

褰卞搷锛�
- Chat 妯″紡涓嬬殑婧愮爜妫�绱㈣兘鍔涜��閿欒��闄愬埗
- 涓嶆槸宕╂簝锛屼絾灞炰簬鈥滃嚱鏁拌皟鐢ㄤ笉鍙�鐢ㄢ�濈被闂�棰�

---

## 鍙戠幇 17锛堜綆锛夛細鍓嶇�� `models` 鍙橀噺琚�瀹氫箟浣嗘湭浣跨敤

鏂囦欢锛歚server_app/frontend/src/plugins/conversation.tsx`

```ts
const models = ['DeepSeek-V4-Flash-0731', 'DeepSeek-V4-Flash-0731', ...providers.map((p) => p.model)]
```

瀹為檯娓叉煋鏃朵娇鐢ㄧ殑鏄�纭�缂栫爜閫夐」 + `providers` 閫愪釜鎷嗗垎锛宍models` 娌℃湁琚�浣跨敤锛屽睘浜庢�讳唬鐮�/鍐椾綑銆�

---

## 鍙戠幇 18锛堜綆锛夛細`cleanup_workspace` 鐨� Windows 闀胯矾寰勫厹搴曞湪 Linux 鏃犳晥

鏂囦欢锛歚core/tools_cleanup.py`

```python
if path.exists():
    full = "\\\\?\\" + str(path.resolve())
    subprocess.run(f'cmd /c rd /s /q "{full}"', ...)
```

- 濡傛灉 `shutil.rmtree` 澶辫触锛屼細灏濊瘯 Windows `cmd /c rd`
- 鍦� Linux 鏈嶅姟鍣ㄤ笂杩欐潯鍛戒护涓嶅瓨鍦�锛屽厹搴曟棤鏁�
- 褰卞搷寰堝皬锛屽洜涓� `rmtree` 涓�鑸�鑳芥垚鍔�

---

## 璇存槑

- 鍓嶇��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round6.md`

===== findings-round7-frontend.md =====
# Bug Audit Round 7 鈥斺�� 鍓嶇��瀛愪唬鐞嗗�¤�＄粨鏋�

> 鏉ユ簮锛氬墠绔�瀹¤�″瓙浠ｇ悊 7dc3a5a9 杩斿洖缁撴灉銆�
> 鍙�璇诲�¤�★紝鏈�淇�鏀逛换浣曟枃浠躲��

## 楂樹弗閲嶅害

### 1. `poll()` 璺ㄤ細璇濈珵鎬侊紝鏃т細璇濇暟鎹�鍙�鑳借�嗙洊鏂颁細璇�
- 鏂囦欢锛歚server_app/frontend/src/lib/session.ts` 217-265 琛�
- `poll()` 鍏堝彇 `sid = state.sessionId`锛宎wait 鏈熼棿鐢ㄦ埛鍒囦細璇�/鏂板缓浼氳瘽鍚庯紝鏃� in-flight 鍝嶅簲浠嶄細 `setState` 瑕嗙洊褰撳墠鏂颁細璇濈姸鎬併��
- 褰卞搷锛氬垏鎹㈠巻鍙�/鏂板缓瀵硅瘽鏃舵棫浼氳瘽浜嬩欢銆佺姸鎬併�乧ursor 娣峰叆鏂颁細璇濓紝鐣岄潰閿欎贡銆�

### 2. 鑷�鍔ㄧ画璺戝け璐ヤ細姘镐箙鍗″湪 running 涓� pending 褰掗浂
- 鏂囦欢锛歚server_app/frontend/src/lib/session.ts` 245-250 琛�
- `st.finished && pending>0` 鏃跺厛缃� `phase:'running', pending:0`锛屽啀 `await api.startTask`锛涜嫢 startTask 鎶涢敊琚� catch 鍚炴帀锛岀姸鎬佹案涔� running銆乸ending 娓呴浂锛屾帓闃熸秷鎭�姘歌繙涓嶇画璺戙��

## 涓�涓ラ噸搴�

### 3. Composer 鍚庣画娑堟伅纭�缂栫爜 mode='chat'锛屼笌缁�璺�/鎭㈠�嶄娇鐢ㄧ殑 state.mode 涓嶄竴鑷�
- `plugins/conversation.tsx` 421 琛� vs `lib/session.ts` 124/209/248 琛�
- MOD 浼氳瘽涓�缁х画鍙戞秷鎭�浼氭寜 chat 妯″紡鍙戦�侊紝鍙�鑳戒笉璧� MOD 閫昏緫銆�

### 4. `openHistorySession`/`loadConversation` 鍦ㄩ�炲洖璋冨彲鑳借�嗙洊鏂颁細璇�
- `lib/session.ts` 353-359銆�288-295 琛�
- 蹇�閫熻繛缁�鍒囨崲鍘嗗彶浼氳瘽鏃讹紝鏃у搷搴旇�嗙洊鏂颁細璇濇皵娉°��

### 5. API Key 瀹為檯鎸佷箙鍖栧埌 localStorage锛屼笌鏂囨�堚�滀笉钀界洏鈥濈煕鐩�
- `lib/store.ts` persist() 鍐欏叆 apiKey/visionApiKey/searchApiKey
- `lib/i18n.ts` 鏂囨�堣�粹�滀粎瀛樺綋鍓嶄細璇濓紝涓嶈惤鐩� / never persisted鈥�
- 瀹夊叏/闅愮�佺煕鐩俱��

## 浣庝弗閲嶅害

### 6. 缂� i18n 璇嶆潯锛歚auth.logout`銆乣toast.newChat`
### 7. `resolveModelConfig` 閲嶅�嶄笖鎭掔湡鏉′欢
### 8. DeepSeek 閫夐」閲嶅�嶏紙models 鏁扮粍 + optgroup锛�
### 9. `resumeTask` 鏈�浼� model/baseUrl 绛夐厤缃�锛岄潬鍚庣��榛樿�ゅ��
### 10. 鏆傚仠鎬佸彂閫佸け璐ュ悗涔愯�傛坊鍔犵殑 chatMessage 鏈�鍥炴粴

## 瀛愪唬鐞嗚�や负姝ｅ父鐨勬柟闈�

- `api.ts` 閴存潈/Content-Type/璺�寰勫熀鏈�姝ｇ‘
- `store.ts` 蹇�鐓�/璁㈤槄/鎸佷箙鍖栨満鍒舵�ｅ父
- `registry.tsx` 妲戒綅绯荤粺銆乣AppShell.tsx` 甯冨眬姝ｅ父
- 绫诲瀷瀹氫箟涓庝娇鐢ㄦ柟鍩烘湰涓�鑷�

===== findings-round8.md =====
# Bug Audit Round 8

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 19锛堥珮锛屽凡楠岃瘉锛夛細娉ㄥ唽鐢ㄦ埛鍚嶆湭鍋氳矾寰勫畨鍏ㄦ牎楠岋紝鍙�瀵艰嚧鍘嗗彶鏂囦欢璺�寰勭┛瓒�

鏂囦欢锛歚server_app/auth_store.py`

`register()` 鍙�鏍￠獙锛�
```python
if not name: raise ...
if len(name) > 32: raise ...
if len(password) < 6: raise ...
```

娌℃湁闄愬埗 `/`銆乣\`銆乣..` 绛夊瓧绗︺��

鑰屽巻鍙叉枃浠跺悕鐩存帴鎷兼帴鐢ㄦ埛鍚嶏細
```python
def _history_path(username: str) -> Path:
    return HISTORY_DIR / f"{username}.json"
```

濡傛灉鐢ㄦ埛娉ㄥ唽鍚嶄负锛�
```
../evil
```
閭ｄ箞鍘嗗彶鏂囦欢浼氬啓鍒帮細
```
data/history/../evil.json
```
鍗� `data/evil.json`锛岃秺鍑轰簡鐢ㄦ埛鍘嗗彶鐩�褰曘��

褰卞搷锛�
- 璺�寰勭┛瓒婇�庨櫓
- 澶氱敤鎴峰満鏅�涓嬪彲浠ヨ�诲啓鍒伴�勬湡涔嬪�栫殑鏂囦欢
- 缃戦〉绔�鏄�鍏�寮�鏈嶅姟锛岃繖鏄�鐪熷疄瀹夊叏闂�棰�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 娉ㄥ唽鏃堕檺鍒剁敤鎴峰悕涓� `[A-Za-z0-9_-]+`锛堟垨鑷冲皯绂佹�� `/`銆乣\`銆乣..`锛�
- 鎴栧巻鍙叉枃浠跺悕浣跨敤 sessionId/鍝堝笇锛岃�屼笉鏄�鐩存帴鎷兼帴鐢ㄦ埛鍚�

楠岃瘉锛�
- 鏂板�� `bugaudit/test_auth_store_path_traversal.py`
- 瀹炴祴娉ㄥ唽 `../evil` 鍚庯紝`evil.json` 鍑虹幇鍦ㄩ�勬湡鍘嗗彶鐩�褰�**涔嬪��**锛岀‘璁よ矾寰勭┛瓒婃垚绔嬨��

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round8.md`

===== findings-round9.md =====
# Bug Audit Round 9

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 20锛堜腑锛夛細`compact` 宸ュ叿瀵瑰瓙浠ｇ悊/闃熷弸鍙�瑙侊紝浣嗘墽琛屾椂鏃� handler

鏂囦欢锛�
- `core/subagent.py`锛氬瓙浠ｇ悊宸ュ叿闆� = `tool_registry.schemas(exclude=SUBAGENT_EXCLUDED)`锛宍SUBAGENT_EXCLUDED` 娌℃湁鎺掗櫎 `compact`
- `core/tools_team.py`锛氶槦鍙嬪伐鍏烽泦 = `TOOLS` 鎺掗櫎鑻ュ共宸ュ叿锛屼篃娌℃湁鎺掗櫎 `compact`
- `core/tools.py`锛歚TOOL_HANDLERS` 娌℃湁 `compact`
- `core/agent.py`锛氬彧鍦ㄤ富 agent 寰�鐜�閲屽�� `compact` 鍋氫簡鐗规畩澶勭悊锛屽瓙浠ｇ悊/闃熷弸寰�鐜�娌℃湁

鍥犳�わ細
- 瀛愪唬鐞� / 闃熷弸鐨� OpenAI schema 閲岃兘鐪嬪埌 `compact`
- 浣嗗畠浠�鎵ц�� `compact` 鏃讹細
  - 瀛愪唬鐞嗚蛋 `tool_registry.execute("compact", {})` 鈫� 杩斿洖 `"(handler not wired yet)"`
  - 闃熷弸璧� `TOOL_HANDLERS.get("compact")` 鈫� 杩斿洖 `"Unknown tool: compact"`

褰卞搷锛�
- 瀛愪唬鐞�/闃熷弸濡傛灉灏濊瘯鍘嬬缉涓婁笅鏂囷紝浼氭嬁鍒颁竴涓�鏃犳剰涔夐敊璇�锛屾棤娉曠湡姝ｅ帇缂�
- 琛屼负涓庘�滃伐鍏峰彲鐢ㄢ�濈殑澹版槑涓嶄竴鑷�

淇�澶嶆柟鍚戯紙寤鸿��锛夛細
- 鍦ㄥ瓙浠ｇ悊/闃熷弸宸ュ叿鍒楄〃涓�鎺掗櫎 `compact`
- 鎴栫粰瀹冧滑鐨勫惊鐜�涔熷疄鐜� `compact` 鐗规畩澶勭悊

---

## 璇存槑

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round9.md`

===== SUMMARY.md =====
# skill-agent Bug Audit Summary

> 鐘舵�侊細鍙�璇诲贰鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��
> 鍙戠幇鏃堕棿锛氭寔缁�杞�娆°��

## 楂樺嵄

| # | 闂�棰� | 浣嶇疆 | 鐘舵�� |
|---|------|------|------|
| 1 | 8001 `_run_agent` 鍦ㄩ攣澶栧垏鎹� cwd/env锛屽苟鍙戜覆浼氳瘽 | `tsinghua agent server/main.py` | 寰呬慨 |
| 5 | `TaskManager.create()` 骞跺彂閲嶅�� task_id | `core/tools_tasks.py` | 宸查獙璇� |
| 9 | `run_in_background` 缁曡繃 workspace-write 娌欑�� | `core/tools_background.py` | 寰呬慨 |
| 19 | `auth_store` 鐢ㄦ埛鍚嶆棤璺�寰勬牎楠岋紝鍘嗗彶鏂囦欢璺�寰勭┛瓒� | `server_app/auth_store.py` | 宸查獙璇� |
| 21 | Agent 鎻愮ず璇� Windows 鍛戒护瑙勫垯锛屼絾 8001 鍦� Linux | `core/config.py` | 寰呬慨 |
| 鍚庣��楂樺嵄 | `server.py` `delete_history` / `_purge_session_dir` 浠绘剰鐩�褰曞垹闄� | `server_app/server.py` | 宸查獙璇� |

## 涓�鍗�

| # | 闂�棰� | 浣嶇疆 |
|---|------|------|
| 2 | 鏂囦欢宸ュ叿鍩哄骇浠嶆槸鍏ㄥ眬 `.runtime`锛屼笉鏄�浼氳瘽鐩�褰� | `core/tools_runtime.py` / `main.py` |
| 6 | 1.21.9/1.21.10 澶嶅埗 1.21.11 婧愮爜 | `server_app/server.py` |
| 7 | auth_store JSON 鍐欐枃浠舵棤閿� | `server_app/auth_store.py` |
| 8 | grep schema 缂� `context_lines` | `core/tools.py` |
| 10 | inject_pending_requests 姣忚疆閲嶅�嶈拷鍔� | `core/protocol.py` |
| 11 | 鍓嶇�� poll 骞跺彂閲嶅�嶄簨浠� | `frontend/src/lib/session.ts` |
| 13 | MOD 鎶�鑳藉姞杞借�勫垯鑷�鐩哥煕鐩� | `core/config.py` vs `docs/agent/TOOL_GUIDE.md` |
| 16 | search_api 鏃犳妧鑳藉姞杞芥椂鎷掔粷鎵ц�� | `core/tools_fs.py` |
| 20 | compact 瀵瑰瓙浠ｇ悊/闃熷弸鍙�瑙佷絾鎵ц�屾棤 handler | `core/subagent.py` / `tools_team.py` |
| 22 | MessageBus.read_inbox 鎹熷潖 JSON 宕╂簝 | `core/tools_team.py` |
| 23 | TodoManager 鏃犻攣 | `core/tools_tasks.py` |
| 26 | `_session_stats` 姣忔�￠亶鍘� mc_java_sources | `server_app/server.py` |
| 27 | `get_status` 鍏ㄩ噺璇� run.log | `server_app/server.py` |
| 30 | 閲嶅�� spawn idle 闃熷弸鍚�鍔ㄩ噸澶嶇嚎绋� | `core/tools_team.py` |
| 鍚庣��涓�鍗� | get_result / 浜嬩欢娓告爣 / 浜嬩欢閲嶅�� / 浜嬩欢 id / 浜嬩欢琛屽悶 / cursor 缁�浼� / finished_at 瑕嗙洊 | `server_app/server.py`銆乣log_events.py` |

## 浣庡嵄

| # | 闂�棰� | 浣嶇疆 |
|---|------|------|
| 3 | MOD 鍏抽敭璇嶅瓙涓茶��鍒� | `main.py` |
| 4 | 鍓嶇��妯″瀷鍒楄〃鍐椾綑 | `frontend/src/plugins/conversation.tsx` |
| 12 | Linux 涓� Windows-only 宸ュ叿涓嶅彲鐢� | `core/tools_game.py` / `tools_vision.py` |
| 14 | compact 鍒濆�嬮敋鐐归噸澶� | `core/compact.py` |
| 15 | WorktreeManager `_load_index` 鏃犻攣 | `core/worktree.py` |
| 17 | 鍓嶇�� `models` 鍙橀噺鏈�浣跨敤 | `conversation.tsx` |
| 18 | cleanup_workspace Windows 鍏滃簳鍦� Linux 鏃犳晥 | `core/tools_cleanup.py` |
| 24 | start_gradle_task 鏃ュ織鍙ユ焺鏈�鍏抽棴 | `core/gradletools.py` |
| 25 | 鍓嶇�� api() 绌� JSON 鍝嶅簲鎶涘紓甯� | `frontend/src/lib/api.ts` |
| 28 | `_save_session_log` cwd 鐩稿�硅矾寰� | `core/agent.py` |
| 29 | run_web_fetch 鍏抽棴閲嶅畾鍚� | `core/tools_web.py` |
| 鍓嶇��浣庡嵄 | i18n 缂鸿瘝鏉� / resolveModelConfig 鍐椾綑 / resumeTask 鏈�浼犻厤缃� / 涔愯�傛秷鎭�鏈�鍥炴粴 | `frontend/src/*` |
| 鍚庣��浣庡嵄 | 鍏ㄥ眬涓嬭浇閿� / fd 娉勬紡 / 姝讳唬鐮� / finalize 鏃� try | `server.py`銆乣run_task.py` |

## 楠岃瘉鑴氭湰

```
bugaudit/test_taskmanager_race.py
bugaudit/test_auth_store_path_traversal.py
bugaudit/test_server_purge_path_traversal.py
bugaudit/check_tool_args.py
bugaudit/check_tool_required_args.py
```

## 璇存槑

- 鎵�鏈夐棶棰樺潎鏈�淇�鏀圭幇鏈変唬鐮�
- 璇︾粏鍒嗚疆鎶ュ憡瑙� `findings-round*.md`
- 鎴�鑷� round 28锛岀疮璁� 42 椤瑰彂鐜帮紙鍚�澶氭�￠獙璇佽剼鏈�纭�璁わ級

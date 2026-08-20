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
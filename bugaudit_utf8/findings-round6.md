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
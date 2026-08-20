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
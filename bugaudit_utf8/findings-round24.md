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
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
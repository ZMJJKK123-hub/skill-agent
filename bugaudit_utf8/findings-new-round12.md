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
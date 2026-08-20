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
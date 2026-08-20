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
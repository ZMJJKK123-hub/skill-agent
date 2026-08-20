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
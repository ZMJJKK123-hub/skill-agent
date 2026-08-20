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
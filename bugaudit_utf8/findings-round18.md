# Bug Audit Round 18

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 32锛堜腑锛夛細`search_api` 鐨� `context_lines` 鍙傛暟琚�蹇界暐锛屽疄闄呬笉鐢熸晥

鏂囦欢锛歚core/tools_fs.py` 鈫� `run_search_api()`

```python
def run_search_api(symbol, path="mc_java_sources", max_results=10, context_lines=0):
    ...
    out = run_grep(symbol, path=path, glob_filter="*.java", max_results=max_results)
```

- `run_search_api` 鎺ユ敹 `context_lines`锛屼絾璋冪敤 `run_grep` 鏃�**娌℃湁浼� `context_lines`**
- 鑰� `run_grep` 鏈�韬�鏄�鏀�鎸� `context_lines` 鐨�
- `search_api` 鐨� OpenAI schema 涔熷叕寮�浜� `context_lines`

缁撴灉锛�
- 妯″瀷/鐢ㄦ埛浠ヤ负浼犱簡 `context_lines` 鑳界湅鍒颁笂涓嬫枃锛屽疄闄呮案杩滅湅涓嶅埌
- 灞炰簬鈥滃嚱鏁板弬鏁版毚闇蹭絾瀹炵幇澶辨晥鈥濈殑 bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round18.md`
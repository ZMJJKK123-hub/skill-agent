# New Bug Audit Round 28

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 74锛堜綆锛夛細`_SEARCH_SKIP_DIRS` 鍖呭惈瀹芥硾鐨� `bin`銆乣run`锛屽彲鑳借��鎺掗櫎鍚堟硶鐩�褰�

鏂囦欢锛歚core/tools_fs.py`

```python
_SEARCH_SKIP_DIRS = { ..., "run", "bin", "venv", ...}
```

- 宸ヤ綔鍖洪噷濡傛灉鏈夊悕涓� `bin/`銆乣run/` 鐨勪笟鍔＄洰褰曪紙渚嬪�� `src/main/resources/bin/`锛夛紝`run_grep`/`run_glob` 浼氳烦杩�
- 杩欎簺鍚嶅瓧澶�閫氱敤锛屽�规槗璇�浼ゅ悎娉曞唴瀹�

褰卞搷锛氭悳绱㈢粨鏋滀笉瀹屾暣銆�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
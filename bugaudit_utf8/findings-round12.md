# Bug Audit Round 12

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 24锛堜綆锛夛細`start_gradle_task` 鎵撳紑鐨勬棩蹇楁枃浠跺彞鏌勬湭鏄惧紡鍏抽棴

鏂囦欢锛歚core/gradletools.py`

```python
log_file = open(log_path, "a", encoding="utf-8", errors="replace")
proc = subprocess.Popen(..., stdout=log_file, ...)
```
`log_file` 娌℃湁 close锛屼緷璧� GC/杩涚▼閫�鍑哄悗鍥炴敹銆傝繘绋嬮暱鏃堕棿杩愯�屾椂鍙ユ焺浼氫繚鎸佹墦寮�锛涜櫧鐒跺奖鍝嶅皬锛屼絾灞炰簬璧勬簮绠＄悊闂�棰樸��

---

## 鍙戠幇 25锛堜綆锛夛細鍓嶇�� `api()` 瀵圭┖ JSON 鍝嶅簲澶勭悊涓嶇ǔ

鏂囦欢锛歚server_app/frontend/src/lib/api.ts`

```ts
if (ct.includes('application/json')) return (await res.json()) as T
```

濡傛灉鍚庣��杩斿洖 `200` + `Content-Type: application/json` 浣� body 涓虹┖锛宍res.json()` 浼氭姏寮傚父銆傜洰鍓嶆帴鍙ｅ熀鏈�閮戒細杩斿洖 JSON 瀵硅薄锛屽奖鍝嶅皬銆�

---

## 璇存槑

- 鍚庣��瀛愪唬鐞嗕粛鍦ㄨ繍琛�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round12.md`
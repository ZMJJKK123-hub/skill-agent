# Bug Audit Round 5

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 13锛堥珮锛夛細MOD 鎶�鑳藉姞杞借�勫垯鑷�鐩哥煕鐩�

鏂囦欢瀵规瘮锛�

- `core/config.py` SYSTEM_MOD锛�
  > "Before writing ANY MOD Java/resource, load the most relevant skill with load_skill"
  > HARD RULES: "SKILLS FIRST (MOD) ... Skills are the PRIMARY reference"
  > "Before starting any task: `load_skill` the most relevant skill first"

- `docs/agent/TOOL_GUIDE.md` Appendix F锛�
  > "Skills are reference material, not gatekeepers. There is NO mandatory skill load."
  > "There is NO mandatory `<skill-source>` citation after changes."

杩欎袱浠芥枃妗ｉ兘浼氳繘鍏� agent 鐨勫伐浣滃尯/涓婁笅鏂囷細
- SYSTEM_MOD 鍦ㄤ富寰�鐜� system prompt 閲�
- TOOL_GUIDE.md 鐢� `server.py` 澶嶅埗杩涗細璇濆伐浣滃尯锛宎gent 鍙� `read_file` 璇诲埌

褰卞搷锛�
- agent 浼氭敹鍒颁簰鐩哥煕鐩剧殑鎸囦护锛氣�滃繀椤� load_skill鈥� vs 鈥滀笉鏄�寮哄埗鈥�
- 鍙�鑳藉�艰嚧 agent 琛屼负涓嶇ǔ瀹氾細鏈夌殑浼氳瘽涓ユ牸鍔犺浇鎶�鑳斤紝鏈夌殑浼氳瘽鐩存帴鍐欎唬鐮�
- 瀵光�渟kill-first 绾�寰嬧�濊繖涓�鏍稿績璁捐�℃潵璇达紝杩欐槸鏄庣‘鐭涚浘

---

## 鍙戠幇 14锛堜綆锛夛細compact 鍙�鑳芥妸鍒濆�嬩换鍔￠敋鐐归噸澶嶅甫鍏�

鏂囦欢锛歚core/compact.py` 鈫� `auto_compact()`

```python
region = messages[:keep_from]   # 鍖呭惈绗�涓�鏉� user 娑堟伅锛坅nchor锛�
summary = summarize_region(region)
...
if anchor is not None:
    new_messages.append(anchor)   # 鍘熷�� anchor
new_messages.append({"role": "user", "content": "..." + summary + "..."})
```

鍘熷�� anchor 鏃㈣��鎽樿�佽繘 summary锛屽張琚�鍘熸牱淇濈暀锛屽彲鑳藉嚭鐜颁俊鎭�閲嶅�嶃�傚奖鍝嶈緝灏忋��

---

## 鍙戠幇 15锛堜綆锛夛細WorktreeManager `_load_index` 閮ㄥ垎璺�寰勬棤閿�

鏂囦欢锛歚core/worktree.py`

`_load_index()` 鐩存帴璇绘枃浠讹紝娌℃湁缁熶竴鍔� `_io_lock`锛沗_save_index` 鏈夐攣銆傚苟鍙戣��+鍐欐椂鍙�鑳借�诲埌鍗婃埅 JSON锛堣櫧鐒舵�傜巼浣庯級銆�

---

## 璇存槑

- 鍓嶇��瀛愪唬鐞嗕粛鍦ㄨ繍琛岋紝杩斿洖鍚庡苟鍏ヤ笅涓�杞�
- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round5.md`
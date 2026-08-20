# Bug Audit Round 21

> 鏈�杞�鍙�璇绘��鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��

## 鍙戠幇 35锛堜綆锛夛細SkillLoader 鎵�鎻忓彧璇绘枃浠跺ご 8KB锛岃秴澶� frontmatter 浼氳��鎴�鏂�

鏂囦欢锛歚core/tools_skills.py` 鈫� `SkillLoader._read_head()`

```python
def _read_head(path: str, max_bytes: int = 8192) -> str:
    ...
```

- 鍙�璇诲墠 8KB 鏉ヨВ鏋� YAML frontmatter
- 濡傛灉鏌愪釜 `SKILL.md` 鐨� frontmatter锛坄---` 鍐咃級瓒呰繃 8KB锛岃В鏋愪細寰楀埌涓嶅畬鏁� YAML
- `yaml.safe_load` 鍙�鑳芥姤閿欐垨瑙ｆ瀽鍑洪敊璇� meta锛屾妧鑳借��涓㈠純/琛屼负寮傚父

褰卞搷锛�
- 鐩�鍓嶆妧鑳� frontmatter 閮借緝灏忥紝褰卞搷浣�
- 浣嗗睘浜庢綔鍦ㄨВ鏋愯竟鐣� bug

---

## 绱�璁�

- 绱�璁℃姤鍛婏細`findings-round1.md` ~ `findings-round21.md`
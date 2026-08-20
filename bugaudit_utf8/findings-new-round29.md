# New Bug Audit Round 29

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 75锛堜綆锛夛細鎶�鑳芥枃浠跺甫 UTF-8 BOM 鏃� frontmatter 瑙ｆ瀽鍙�鑳藉け璐�

鏂囦欢锛歚core/tools_skills.py`

- `_read_head` 璇� bytes 鍚� `decode("utf-8", errors="replace")`
- 濡傛灉鏂囦欢甯� BOM锛坄EF BB BF`锛夛紝寮�澶翠細鍙樻垚 `\ufeff---`
- `raw.startswith("---")` 涓� False锛屽綋鍓嶄唬鐮佷細鎶婂畠褰撯�滄棤 frontmatter鈥濆�勭悊锛孻AML 鍏冩暟鎹�涓㈠け

褰卞搷锛�
- 甯� BOM 鐨� SKILL.md 浼氫涪澶� name/description 绛夊厓鏁版嵁
- 鍘嗗彶涓婃浘鍥犳�ゅ嚭杩囬棶棰橈紙YAML 鍏煎�癸級

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
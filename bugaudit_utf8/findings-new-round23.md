# New Bug Audit Round 23

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 69锛堜綆锛夛細鎶�鑳芥�ｆ枃鑻ュ寘鍚� `</skill>` 瀛楁牱锛屼細琚� `load_skill` 鐨勬�ｅ垯鎻愬墠鎴�鏂�

鏂囦欢锛歚core/tools_skills.py` / `core/skillcheck.py`

- `SkillLoader.get_content()` 杩斿洖 `<skill name="...">\n{body}\n</skill>`
- `skillcheck` 鐨� `_SKILL_BLOCK_RE` 浣跨敤闈炶椽濠� `(.*?)</skill>`
- 濡傛灉鎶�鑳芥�ｆ枃閲屽嚭鐜� `</skill>` 鏂囨湰锛堜緥濡� Markdown 浠ｇ爜鍧楃ず渚嬶級锛岃В鏋愪細鎻愬墠缁撴潫锛屾妧鑳藉叏鏂囪��鎴�鏂�

褰卞搷锛�
- 鎶�鑳藉唴瀹逛涪澶�
- 姝ｇ‘鎬�/涓婁笅鏂囦笉瀹屾暣

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
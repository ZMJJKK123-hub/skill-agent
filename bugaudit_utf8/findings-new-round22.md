# New Bug Audit Round 22

> 鍙�璇讳笉鏀逛唬鐮侊紝浠呮柊澧炴湰璁板綍銆�

## 鍙戠幇 68锛堜腑锛夛細`move_skills_to_end` 姣忚疆鍔犺浇鏂版妧鑳介兘浼氳拷鍔犳柊鐨� `<active-skills>`锛屾棫鍧椾笉娓呯悊

鏂囦欢锛歚core/skillcheck.py` 鈫� `move_skills_to_end()`

- 姣忔�″彂鐜版柊鐨� `load_skill` 宸ュ叿缁撴灉锛屼細鎶婃妧鑳藉叏鏂囦互 `<active-skills>` user 娑堟伅杩藉姞鍒版湯灏�
- 涓嶄細绉婚櫎鏃х殑 `<active-skills>` 娑堟伅
- 澶氭�″姞杞戒笉鍚屾妧鑳藉悗锛屼笂涓嬫枃閲屼細绱�绉�澶氫唤鎶�鑳藉叏鏂囧潡

褰卞搷锛�
- 涓婁笅鏂囪啫鑳�
- 鏃ф妧鑳藉叏鏂囧崰鐢� token
- 涓庘�滄粴鍔ㄥ埌鏈�鏂般�佷笉绱�绉�鈥濈殑璁捐�℃剰鍥句笉绗︼紙鏃� tool 娑堟伅琚�鍗犱綅锛屼絾鏃� active-skills user 娑堟伅娌¤��娓呯悊锛�

---

## 璇存槑

- 缁х画鍦� `bugaudit/` 涓嬬疮鍔犺�板綍
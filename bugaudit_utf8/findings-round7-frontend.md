# Bug Audit Round 7 鈥斺�� 鍓嶇��瀛愪唬鐞嗗�¤�＄粨鏋�

> 鏉ユ簮锛氬墠绔�瀹¤�″瓙浠ｇ悊 7dc3a5a9 杩斿洖缁撴灉銆�
> 鍙�璇诲�¤�★紝鏈�淇�鏀逛换浣曟枃浠躲��

## 楂樹弗閲嶅害

### 1. `poll()` 璺ㄤ細璇濈珵鎬侊紝鏃т細璇濇暟鎹�鍙�鑳借�嗙洊鏂颁細璇�
- 鏂囦欢锛歚server_app/frontend/src/lib/session.ts` 217-265 琛�
- `poll()` 鍏堝彇 `sid = state.sessionId`锛宎wait 鏈熼棿鐢ㄦ埛鍒囦細璇�/鏂板缓浼氳瘽鍚庯紝鏃� in-flight 鍝嶅簲浠嶄細 `setState` 瑕嗙洊褰撳墠鏂颁細璇濈姸鎬併��
- 褰卞搷锛氬垏鎹㈠巻鍙�/鏂板缓瀵硅瘽鏃舵棫浼氳瘽浜嬩欢銆佺姸鎬併�乧ursor 娣峰叆鏂颁細璇濓紝鐣岄潰閿欎贡銆�

### 2. 鑷�鍔ㄧ画璺戝け璐ヤ細姘镐箙鍗″湪 running 涓� pending 褰掗浂
- 鏂囦欢锛歚server_app/frontend/src/lib/session.ts` 245-250 琛�
- `st.finished && pending>0` 鏃跺厛缃� `phase:'running', pending:0`锛屽啀 `await api.startTask`锛涜嫢 startTask 鎶涢敊琚� catch 鍚炴帀锛岀姸鎬佹案涔� running銆乸ending 娓呴浂锛屾帓闃熸秷鎭�姘歌繙涓嶇画璺戙��

## 涓�涓ラ噸搴�

### 3. Composer 鍚庣画娑堟伅纭�缂栫爜 mode='chat'锛屼笌缁�璺�/鎭㈠�嶄娇鐢ㄧ殑 state.mode 涓嶄竴鑷�
- `plugins/conversation.tsx` 421 琛� vs `lib/session.ts` 124/209/248 琛�
- MOD 浼氳瘽涓�缁х画鍙戞秷鎭�浼氭寜 chat 妯″紡鍙戦�侊紝鍙�鑳戒笉璧� MOD 閫昏緫銆�

### 4. `openHistorySession`/`loadConversation` 鍦ㄩ�炲洖璋冨彲鑳借�嗙洊鏂颁細璇�
- `lib/session.ts` 353-359銆�288-295 琛�
- 蹇�閫熻繛缁�鍒囨崲鍘嗗彶浼氳瘽鏃讹紝鏃у搷搴旇�嗙洊鏂颁細璇濇皵娉°��

### 5. API Key 瀹為檯鎸佷箙鍖栧埌 localStorage锛屼笌鏂囨�堚�滀笉钀界洏鈥濈煕鐩�
- `lib/store.ts` persist() 鍐欏叆 apiKey/visionApiKey/searchApiKey
- `lib/i18n.ts` 鏂囨�堣�粹�滀粎瀛樺綋鍓嶄細璇濓紝涓嶈惤鐩� / never persisted鈥�
- 瀹夊叏/闅愮�佺煕鐩俱��

## 浣庝弗閲嶅害

### 6. 缂� i18n 璇嶆潯锛歚auth.logout`銆乣toast.newChat`
### 7. `resolveModelConfig` 閲嶅�嶄笖鎭掔湡鏉′欢
### 8. DeepSeek 閫夐」閲嶅�嶏紙models 鏁扮粍 + optgroup锛�
### 9. `resumeTask` 鏈�浼� model/baseUrl 绛夐厤缃�锛岄潬鍚庣��榛樿�ゅ��
### 10. 鏆傚仠鎬佸彂閫佸け璐ュ悗涔愯�傛坊鍔犵殑 chatMessage 鏈�鍥炴粴

## 瀛愪唬鐞嗚�や负姝ｅ父鐨勬柟闈�

- `api.ts` 閴存潈/Content-Type/璺�寰勫熀鏈�姝ｇ‘
- `store.ts` 蹇�鐓�/璁㈤槄/鎸佷箙鍖栨満鍒舵�ｅ父
- `registry.tsx` 妲戒綅绯荤粺銆乣AppShell.tsx` 甯冨眬姝ｅ父
- 绫诲瀷瀹氫箟涓庝娇鐢ㄦ柟鍩烘湰涓�鑷�
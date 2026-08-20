# skill-agent Bug Audit Summary

> 鐘舵�侊細鍙�璇诲贰鏌ワ紝鏈�淇�鏀逛换浣曠幇鏈変唬鐮併��
> 鍙戠幇鏃堕棿锛氭寔缁�杞�娆°��

## 楂樺嵄

| # | 闂�棰� | 浣嶇疆 | 鐘舵�� |
|---|------|------|------|
| 1 | 8001 `_run_agent` 鍦ㄩ攣澶栧垏鎹� cwd/env锛屽苟鍙戜覆浼氳瘽 | `tsinghua agent server/main.py` | 寰呬慨 |
| 5 | `TaskManager.create()` 骞跺彂閲嶅�� task_id | `core/tools_tasks.py` | 宸查獙璇� |
| 9 | `run_in_background` 缁曡繃 workspace-write 娌欑�� | `core/tools_background.py` | 寰呬慨 |
| 19 | `auth_store` 鐢ㄦ埛鍚嶆棤璺�寰勬牎楠岋紝鍘嗗彶鏂囦欢璺�寰勭┛瓒� | `server_app/auth_store.py` | 宸查獙璇� |
| 21 | Agent 鎻愮ず璇� Windows 鍛戒护瑙勫垯锛屼絾 8001 鍦� Linux | `core/config.py` | 寰呬慨 |
| 鍚庣��楂樺嵄 | `server.py` `delete_history` / `_purge_session_dir` 浠绘剰鐩�褰曞垹闄� | `server_app/server.py` | 宸查獙璇� |

## 涓�鍗�

| # | 闂�棰� | 浣嶇疆 |
|---|------|------|
| 2 | 鏂囦欢宸ュ叿鍩哄骇浠嶆槸鍏ㄥ眬 `.runtime`锛屼笉鏄�浼氳瘽鐩�褰� | `core/tools_runtime.py` / `main.py` |
| 6 | 1.21.9/1.21.10 澶嶅埗 1.21.11 婧愮爜 | `server_app/server.py` |
| 7 | auth_store JSON 鍐欐枃浠舵棤閿� | `server_app/auth_store.py` |
| 8 | grep schema 缂� `context_lines` | `core/tools.py` |
| 10 | inject_pending_requests 姣忚疆閲嶅�嶈拷鍔� | `core/protocol.py` |
| 11 | 鍓嶇�� poll 骞跺彂閲嶅�嶄簨浠� | `frontend/src/lib/session.ts` |
| 13 | MOD 鎶�鑳藉姞杞借�勫垯鑷�鐩哥煕鐩� | `core/config.py` vs `docs/agent/TOOL_GUIDE.md` |
| 16 | search_api 鏃犳妧鑳藉姞杞芥椂鎷掔粷鎵ц�� | `core/tools_fs.py` |
| 20 | compact 瀵瑰瓙浠ｇ悊/闃熷弸鍙�瑙佷絾鎵ц�屾棤 handler | `core/subagent.py` / `tools_team.py` |
| 22 | MessageBus.read_inbox 鎹熷潖 JSON 宕╂簝 | `core/tools_team.py` |
| 23 | TodoManager 鏃犻攣 | `core/tools_tasks.py` |
| 26 | `_session_stats` 姣忔�￠亶鍘� mc_java_sources | `server_app/server.py` |
| 27 | `get_status` 鍏ㄩ噺璇� run.log | `server_app/server.py` |
| 30 | 閲嶅�� spawn idle 闃熷弸鍚�鍔ㄩ噸澶嶇嚎绋� | `core/tools_team.py` |
| 鍚庣��涓�鍗� | get_result / 浜嬩欢娓告爣 / 浜嬩欢閲嶅�� / 浜嬩欢 id / 浜嬩欢琛屽悶 / cursor 缁�浼� / finished_at 瑕嗙洊 | `server_app/server.py`銆乣log_events.py` |

## 浣庡嵄

| # | 闂�棰� | 浣嶇疆 |
|---|------|------|
| 3 | MOD 鍏抽敭璇嶅瓙涓茶��鍒� | `main.py` |
| 4 | 鍓嶇��妯″瀷鍒楄〃鍐椾綑 | `frontend/src/plugins/conversation.tsx` |
| 12 | Linux 涓� Windows-only 宸ュ叿涓嶅彲鐢� | `core/tools_game.py` / `tools_vision.py` |
| 14 | compact 鍒濆�嬮敋鐐归噸澶� | `core/compact.py` |
| 15 | WorktreeManager `_load_index` 鏃犻攣 | `core/worktree.py` |
| 17 | 鍓嶇�� `models` 鍙橀噺鏈�浣跨敤 | `conversation.tsx` |
| 18 | cleanup_workspace Windows 鍏滃簳鍦� Linux 鏃犳晥 | `core/tools_cleanup.py` |
| 24 | start_gradle_task 鏃ュ織鍙ユ焺鏈�鍏抽棴 | `core/gradletools.py` |
| 25 | 鍓嶇�� api() 绌� JSON 鍝嶅簲鎶涘紓甯� | `frontend/src/lib/api.ts` |
| 28 | `_save_session_log` cwd 鐩稿�硅矾寰� | `core/agent.py` |
| 29 | run_web_fetch 鍏抽棴閲嶅畾鍚� | `core/tools_web.py` |
| 鍓嶇��浣庡嵄 | i18n 缂鸿瘝鏉� / resolveModelConfig 鍐椾綑 / resumeTask 鏈�浼犻厤缃� / 涔愯�傛秷鎭�鏈�鍥炴粴 | `frontend/src/*` |
| 鍚庣��浣庡嵄 | 鍏ㄥ眬涓嬭浇閿� / fd 娉勬紡 / 姝讳唬鐮� / finalize 鏃� try | `server.py`銆乣run_task.py` |

## 楠岃瘉鑴氭湰

```
bugaudit/test_taskmanager_race.py
bugaudit/test_auth_store_path_traversal.py
bugaudit/test_server_purge_path_traversal.py
bugaudit/check_tool_args.py
bugaudit/check_tool_required_args.py
```

## 璇存槑

- 鎵�鏈夐棶棰樺潎鏈�淇�鏀圭幇鏈変唬鐮�
- 璇︾粏鍒嗚疆鎶ュ憡瑙� `findings-round*.md`
- 鎴�鑷� round 28锛岀疮璁� 42 椤瑰彂鐜帮紙鍚�澶氭�￠獙璇佽剼鏈�纭�璁わ級
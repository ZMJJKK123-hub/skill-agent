# Agent Tool Guide

> 本文件是 agent 的完整工具手册，防止上下文压缩后信息丢失。系统提示词只保留精简版；
> 需要看某个工具的详细用法时，用 `read_file` 读本文件对应章节，或 `grep` 搜索工具名。

## 通行规则

1. 优先使用已有工具，只有完全没有对应工具时才使用 `bash`。
2. 文件操作用 `read_file` / `write_file` / `edit_file` / `glob` / `grep`，不要用 bash 重定向写文件。
3. 阶段式开放：初始只开放基础开发工具；需要构建/测试/游戏验证时调用 `activate_test_mode` 解锁全部工具。
4. 遇到错误或思考转圈时，先读 `docs/agent/ERROR_LIST.md`；找不到解决方案再把新错误追加进去。
5. 常用自循环：
   `validate_resources` → `activate_test_mode` → `run_mod_test_cycle`
   → 失败则 `read_game_test_log` / `read_crash_report` / `analyze_crash` / `tail_log`
   → 修复 → 再验证 → `git_commit` / `snapshot`。

## 工具分区

### 基础开发工具（初始开放）

文件/代码：`read_file` `write_file` `edit_file` `glob` `grep`
Shell：`bash` `run_in_background`
工作树：`worktree_create` `worktree_list` `worktree_use` `worktree_remove` `worktree_run` `worktree_recover`
搜索：`web_search` `web_fetch` `search_minecraft_docs`
环境/工具：`detect_environment` `validate_resources` `download_file` `extract_archive` `cleanup_workspace`
任务/团队/协议：`todo` `task` `task_create` `task_get` `task_list` `task_update` `task_clear` `claim_task`
`spawn_teammate` `send_to_teammate` `shutdown_teammate` `team_status` `protocol_status`
`request_shutdown` `respond_to_request` `submit_plan`
会话/记忆：`set_auto_mode` `compact` `load_skill` `ask_user_question`
解锁入口：`activate_test_mode`

### 扩展工具（activate_test_mode 后开放）

构建/数据/GameTest：`build_mod_jar_forge` `run_data_gen` `run_test_data`
`run_game_test_server` `run_test_gametest` `run_test_server` `run_test_client`
`parse_gametest_results` `read_game_test_log` `parse_build_output` `run_mod_test_cycle`
服务端/客户端：`run_server` `run_client` `start_mc_server` `start_mc_client`
`mc_status` `stop_mc_process` `kill_game` `server_console`
`wait_for_mc_ready` `wait_for_port`
游戏内交互：`send_game_command` `game_input` `press_key` `type_text`
`wait_for_log` `wait_for_screen` `verify_visual_loop`
截图/视觉：`screenshot` `analyze_image`
日志/崩溃/产物：`read_crash_report` `analyze_crash` `verify_artifact` `tail_log`
Git/快照：`git_status` `git_diff` `git_commit` `snapshot` `restore_snapshot`

## 高频耦合关系

- `run_mod_test_cycle` = `validate_resources` + `build_mod_jar_forge` + `run_test_gametest` + `parse_gametest_results`
- `start_mc_server` 传 `rcon_port` / `rcon_password` 会自动写 `server.properties`
- `server_console` 优先写 stdin，失败自动 fallback RCON
- `wait_for_mc_ready` = 日志匹配 + 端口探测，不要重复等待
- `verify_visual_loop` 内部已完成截图 + 识图
- `git_commit` / `snapshot` 都会 `git add -A`

## 禁止事项

- 禁止 `taskkill /f /im python.exe`（会杀死 agent 自身）
- 禁止用 bash 裸跑 `gradlew runServer/runClient`；用 `start_mc_server` / `start_mc_client`
- 禁止用 bash 写文件；用 `write_file` / `edit_file`
- 禁止不读错误名单就反复猜测同一个错误
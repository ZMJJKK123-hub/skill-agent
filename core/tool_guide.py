# -*- coding: utf-8 -*-
"""Detailed tool usage guide injected into the agent system prompt.

The goal is to make the agent:
1. Notice every available tool instead of falling back to bash.
2. Understand which tools call other tools (couplings), so it does not duplicate work.
3. Use the most suitable high-level tool before writing raw shell commands.
"""

TOOL_USAGE_GUIDE = r"""【工具使用总则】
1. 本系统已注册 80 个专用工具。执行任何任务时，必须先检查是否有现成工具；只有完全没有对应工具时，才允许使用 bash/终端。
2. 终端（bash）是最后手段。优先使用 read_file/write_file/edit_file/glob/grep 处理文件；优先使用专用工具处理构建、测试、游戏交互、Git。
3. 很多工具会内部调用其他工具，使用高层工具可以避免重复劳动：
   - run_mod_test_cycle = validate_resources + build_mod_jar_forge + run_test_gametest + parse_gametest_results
   - start_mc_server 会自动写 run/server.properties（enable-rcon/rcon.port/rcon.password/online-mode=false）
   - server_console 优先写进程 stdin，失败后自动 fallback 到 RCON
   - wait_for_mc_ready 同时检查日志匹配和端口开放
   - verify_visual_loop = 发 RCON 命令 + 截图 + analyze_image 循环
   - snapshot / git_commit 都会执行 git add -A
4. MOD 自循环推荐路径：
   改代码 → validate_resources → run_mod_test_cycle（或自己分步 build+gametest）→ parse_gametest_results → 失败则 read_game_test_log / read_crash_report / analyze_crash / tail_log → 修复 → 再验证 → 通过后 git_commit/snapshot。
5. 需要后台开服/开客户端时，用 start_mc_server / start_mc_client（或 run_server / run_client），不要用 bash 裸跑 gradlew runServer/runClient。
6. 需要向游戏发命令时，优先 start_mc_server + RCON（rcon_password）→ send_game_command / server_console；实在没有 RCON 才考虑 press_key/type_text 手动按键。
7. 涉及 Git 检查点：用 git_status / git_diff / git_commit / snapshot / restore_snapshot，不要在 bash 里拼 git 命令。

【工具详细说明】

## 一、文件/代码操作
- read_file：读取文件内容。需要查看源码、日志、配置时优先用它。可传 limit 限制行数。
- write_file：整文件写入/覆盖。写代码/资源/配置必须用它，不要用 bash 重定向（Windows 编码会损坏中文/emoji）。
- edit_file：精确替换文件片段，改一处代码比 write_file 更安全。old_text 必须唯一且完全匹配。
- glob：按通配符找文件路径，如 **/*.java。用于确认文件存在、列目录。
- grep：按正则搜索文件内容，返回文件名+行号。用于快速定位报错、引用、TODO。比 bash findstr 更安全。

## 二、Shell/后台
- bash：执行命令。仅当没有专用工具时使用；Windows 语法，禁止 taskkill /f /im python.exe。
- run_in_background：把长时间命令放后台执行，返回 job id，不要用它代替 start_mc_*。

## 三、工作区/多工作树
- worktree_create：创建隔离工作树，适用于并行实验/多版本尝试。
- worktree_list：查看所有工作树。
- worktree_use：切换到指定工作树；后续文件/构建默认作用于该工作树。
- worktree_remove：删除工作树。
- worktree_run：在指定工作树里执行命令。
- worktree_recover：恢复异常/丢失的工作树。

## 四、搜索/网络
- web_search：联网搜索（优先 Tavily，没 Key 自动 DuckDuckGo）。查最新文档/资料时用它。
- web_fetch：抓取指定网页正文。需要阅读某个 URL 内容时用它。
- search_minecraft_docs：定向搜索 Minecraft Wiki / Forge 文档 / NeoForged / GitHub。查 MC/Forge 专用知识时优先用它，比 web_search 更准。

## 五、构建/数据/GameTest
- build_mod_jar_forge：执行 gradlew build 并复制 jar 到 dist/。验证编译和打包时用它；耗时较长。
- run_data_gen：运行 Forge DataGen，生成生产资源（模型/配方/战利品/语言等）。
- run_test_data：运行 DataGen 但加载 src/test，生成测试专用占位内容，不污染生产 assets。
- run_game_test_server：运行 GameTest 服务器（较通用）；通常自回归用 run_test_gametest 更直接。
- run_test_gametest：核心验收工具，运行 runTestGameTestServer 并返回成功/失败。修改代码后必须用它验证。
- run_test_server：启动测试专用服务端（加载 src/test），用于测试侧 classloading/side-isolation。
- run_test_client：启动测试专用客户端（加载 src/test），用于手动/视觉调试。
- parse_gametest_results：解析 run/logs/latest.log，提取通过/失败/异常摘要，输出 RESULT。
- read_game_test_log：直接读取 GameTest 日志内容。
- parse_build_output：从构建日志/文本中提取 error: 和 FAILED 任务，快速定位编译错。
- run_mod_test_cycle：一键闭环 = validate_resources → build_mod_jar_forge → run_test_gametest → parse_gametest_results。优先用它做回归；需要单独控制某一步时才分步调用。

## 六、服务端/客户端生命周期
- run_server：后台启动生产服务端（src/main），等价 start_mc_server(默认)。
- run_client：后台启动生产客户端（src/main），等价 start_mc_client(默认)。
- start_mc_server：后台启动服务端；若传 rcon_port/rcon_password 会自动写 server.properties 开启 RCON。之后用 wait_for_mc_ready/wait_for_port 等就绪。
- start_mc_client：后台启动客户端；之后可用 wait_for_screen/screenshot/analyze_image 观察。
- mc_status：查看所有后台进程、端口、日志就绪提示。每次启动后先调它确认状态。
- stop_mc_process：按 handle 停止进程（如 mc-server/mc-client），默认 all。
- kill_game：强制杀所有/指定游戏进程（taskkill /T 树杀）。
- server_console：向服务端进程 stdin 发命令；写不了会自动 fallback RCON（需要 rcon_password）。
- wait_for_mc_ready：等待服务端/客户端就绪 = 日志匹配 或 端口开放。
- wait_for_port：等待某个 TCP 端口开放（如 25565/25575）。

## 七、游戏内交互
- send_game_command：通过 RCON 向运行中的服务端发命令（/give /tp /reload 等）。必须先有 RCON 密码和端口。
- game_input：通用输入；action=key 按键 / action=type 输入文本。
- press_key：向当前聚焦窗口发单个按键（e 开背包、esc 退出等）。注意窗口必须在前台。
- type_text：向当前聚焦窗口输入文本（聊天/搜索框）。
- wait_for_log：等待日志中出现指定正则，用于等启动/测试完成。
- wait_for_screen：等待几秒后截图，可选 analyze_image 分析画面。
- verify_visual_loop：视觉验证循环 = 每轮先 RCON 发命令 → 截图 → analyze_image 分析，重复多轮。需要视觉能力时用它，不要手动反复截图。

## 八、截图/视觉
- screenshot：截取当前屏幕，返回图片路径。确认游戏/UI 画面时用。
- analyze_image：用视觉模型分析图片，回答关于画面内容的问题。必须配合 screenshot/verify_visual_loop 使用。

## 九、日志/崩溃/环境/产物
- read_crash_report：读取最新 crash-report。
- analyze_crash：分析崩溃报告，提取 cause/堆栈。
- detect_environment：检测 Java/Gradle/MC/Forge/modid/目录布局，开始任务前可先跑一次。
- verify_artifact：检查 jar/zip 是否包含 mods.toml/pack.mcmeta/assets/data，以及是否混入 build/run 垃圾。
- cleanup_workspace：清理 build/.gradle/cache 或全部运行缓存；只在需要释放空间/重置环境时用。
- download_file：下载文件到工作区。
- extract_archive：安全解压 zip/tar.gz/jar。
- tail_log：快速读日志末尾，比 read_file 更适合看最新输出。

## 十、资源校验
- validate_resources：扫描并校验 MOD 资源：item definitions、model/texture 引用、blockstate、recipe、JSON 语法。写资源后先跑它。

## 十一、任务/待办/团队/协议
- todo：维护待办列表，多步任务必须用。
- task_create / task_get / task_list / task_update / task_clear：子任务 DAG 管理。需要并行/隔离研究时用 task 而非自己手写。
- claim_task：认领一个任务。
- spawn_teammate：创建子 agent，适合独立子问题。
- send_to_teammate：给已创建的子 agent 发消息。
- shutdown_teammate：关闭子 agent。
- team_status：查看子 agent 状态。
- protocol_status：查看外部请求/协议状态。
- request_shutdown：请求关闭协作/外部服务。
- respond_to_request：响应外部请求。
- submit_plan：提交计划，用于需要审批/展示计划的场景。

## 十二、会话/自动模式/记忆
- set_auto_mode：切换全自动模式；开启后 ask_user_question 不阻塞。
- compact：上下文过长时压缩历史，压缩内容会保存到 .transcripts/。
- load_skill：加载技能文档。写 MOD 前必须按规则加载相关技能。

## 十三、Git/快照
- git_status：查看 git 状态。
- git_diff：查看当前改动 diff/stat。
- git_commit：提交改动（默认 git add -A）。每个通过节点建议调用。
- snapshot：打一个 git 快照提交，返回 HEAD；适合当作“本次正确基线”。
- restore_snapshot：hard reset 回滚到指定快照。破坏性操作，只有确认要回退时才用。

## 十四、用户交互
- ask_user_question：需要用户确认/选择时使用；全自动模式下不会阻塞。

【常见耦合与避坑】
- run_mod_test_cycle 已含 validate/build/gametest/parse，不要再单独重复调一遍。
- start_mc_server 若传了 RCON 参数，之后 send_game_command 直接可用；不要再手动 echo 进 server.properties。
- server_console 和 send_game_command 都可以发命令；优先前者（本地 stdin），失败再 RCON。
- wait_for_mc_ready 已经会看日志和端口，不要再同时调 wait_for_log + wait_for_port 重复等。
- verify_visual_loop 已经内部截图+识图，不要再在外面单独 screenshot+analyze_image 堆一遍。
- git_commit/snapshot 都会 add -A，不要先 git add 再调它们。
- 除非没有专用工具，否则不要用 bash 跑 gradlew、git、findstr、curl 等；用对应工具更稳。
"""
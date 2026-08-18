# -*- coding: utf-8 -*-
"""Base and extended tool usage guides.

The agent initially only receives BASE_TOOL_GUIDE. When it calls
activate_test_mode, EXTENDED_TOOL_GUIDE is appended to the system prompt and
all tools become visible for the rest of the session.
"""

BASE_TOOL_GUIDE = r"""【工具使用总则（基础阶段）】
1. 本系统采用“阶段式工具开放”。你现在处于【开发阶段】，只开放基础开发工具。
2. 优先使用已有工具；只有完全没有对应工具时，才允许使用 bash/终端。
3. 文件操作用 read_file / write_file / edit_file / glob / grep，不要用 bash 重定向写文件（Windows 编码会损坏中文/emoji）。
4. 当你需要进入测试/验证阶段（构建、GameTest、启动服务端/客户端、游戏内交互、截图识图、Git 快照）时，
   必须调用 activate_test_mode 解锁全部工具。调用后你会获得完整工具列表和完整使用说明。
5. 解锁后本会话永久生效，不需要重复解锁。
6. 终端（bash）是最后手段；有专用工具就用专用工具。
7. 完整工具手册保存在 docs/agent/TOOL_GUIDE.md；遇到错误或思考转圈时，先 read_file docs/agent/ERROR_LIST.md，
   找不到解决方案再把新错误追加到该文件对应分类。

【基础工具详细说明】

## 一、文件/代码操作
- read_file：读取文件内容。查看源码、日志、配置时优先用它。
- write_file：整文件写入/覆盖。写代码/资源/配置必须用它，不要用 bash 重定向。
- edit_file：精确替换文件片段。改一处代码比 write_file 更安全。
- glob：按通配符找文件路径（如 **/*.java），用于确认文件存在/列目录。
- grep：按正则搜索文件内容，返回文件名+行号，快速定位引用/报错/TODO。

## 二、Shell/后台
- bash：执行命令。仅当没有专用工具时使用；Windows 语法，禁止 taskkill /f /im python.exe。
- run_in_background：把长时间命令放后台执行，返回 job id。

## 三、工作区/多工作树
- worktree_create：创建隔离工作树，适合并行实验/多版本尝试。
- worktree_list：查看所有工作树。
- worktree_use：切换当前工作树；后续文件/构建默认作用于该工作树。
- worktree_remove：删除工作树。
- worktree_run：在指定工作树里执行命令。
- worktree_recover：恢复异常/丢失的工作树。

## 四、搜索/网络
- web_search：联网搜索（Tavily/DDG），查最新资料。
- web_fetch：抓取指定网页正文。
- search_minecraft_docs：定向搜索 Minecraft Wiki / Forge / NeoForged / GitHub，查 MC/Forge 专用知识优先用它。

## 五、环境/资源/工具
- detect_environment：检测 Java/Gradle/MC/Forge/modid/目录布局，任务开始前可先跑一次。
- validate_resources：扫描并校验 MOD 资源（item definitions、model/texture 引用、blockstate、recipe、JSON 语法）。写资源后先跑它。
- download_file：下载文件到工作区。
- extract_archive：安全解压 zip/tar.gz/jar。
- cleanup_workspace：清理 build/.gradle/cache 或运行缓存；需要释放空间/重置环境时用。

## 六、任务/待办/团队/协议
- todo：维护待办列表，多步任务必须用。
- task_create / task_get / task_list / task_update / task_clear：子任务 DAG 管理。
- task：派发一个独立子任务给隔离子 agent（异步，后台执行）。
- claim_task：认领任务。
- spawn_teammate：创建子 agent。
- send_to_teammate：给子 agent 发消息。
- shutdown_teammate：关闭子 agent。
- team_status：查看子 agent 状态。
- protocol_status：查看外部请求/协议状态。
- request_shutdown：请求关闭协作/外部服务。
- respond_to_request：响应外部请求。
- submit_plan：提交计划。

## 七、会话/自动模式/记忆/用户
- set_auto_mode：切换全自动模式；开启后 ask_user_question 不阻塞。
- compact：上下文过长时压缩历史。
- load_skill：加载技能文档；写 MOD 前必须按规则加载相关技能。
- ask_user_question：需要用户确认/选择时使用。

## 八、测试模式解锁
- activate_test_mode：进入测试/验证阶段的关键入口。调用后本会话会解锁全部剩余工具（构建、GameTest、
  服务端/客户端生命周期、游戏内交互、截图识图、Git 快照、日志/崩溃/产物验证等），
  并注入完整的扩展工具使用说明。返回结果中会列出新解锁的工具清单。
  当任务需要验证/运行/测试 MOD 时，必须调用它，不要用 bash 裸跑 gradlew。
"""

EXTENDED_TOOL_GUIDE = r"""【扩展工具使用说明（测试/验证阶段）】
你已通过 activate_test_mode 解锁全部工具。本阶段拥有完整 80 个工具。
继续遵守总则：优先使用专用工具，非必要不用 bash/终端。

【新增/解锁工具详细说明】

## 一、构建/数据/GameTest
- build_mod_jar_forge：执行 gradlew build 并复制 jar 到 dist/。验证编译和打包时用它。
- run_data_gen：运行 Forge DataGen，生成生产资源（模型/配方/战利品/语言等）。
- run_test_data：运行 DataGen 但加载 src/test，生成测试专用占位内容，不污染生产 assets。
- run_game_test_server：运行 GameTest 服务器（较通用）；通常自回归用 run_test_gametest 更直接。
- run_test_gametest：核心验收工具，运行 runTestGameTestServer 并返回成功/失败。修改代码后必须用它验证。
- run_test_server：启动测试专用服务端（加载 src/test）。
- run_test_client：启动测试专用客户端（加载 src/test）。
- parse_gametest_results：解析 run/logs/latest.log，提取通过/失败/异常摘要，输出 RESULT。
- read_game_test_log：直接读取 GameTest 日志内容。
- parse_build_output：从构建日志/文本中提取 error: 和 FAILED 任务，快速定位编译错。
- run_mod_test_cycle：一键闭环 = validate_resources → build_mod_jar_forge → run_test_gametest → parse_gametest_results。
  优先用它做回归；需要单独控制某一步时才分步调用。不要再重复调它内部已包含的工具。

## 二、服务端/客户端生命周期
- run_server：后台启动生产服务端（src/main），等价 start_mc_server(默认)。
- run_client：后台启动生产客户端（src/main），等价 start_mc_client(默认)。
- start_mc_server：后台启动服务端；若传 rcon_port/rcon_password 会自动写 run/server.properties 开启 RCON。
- start_mc_client：后台启动客户端。
- mc_status：查看所有后台进程、端口、日志就绪提示。每次启动后先调它确认状态。
- stop_mc_process：按 handle 停止进程（mc-server/mc-client），默认 all。
- kill_game：强制杀所有/指定游戏进程（taskkill /T 树杀）。
- server_console：向服务端进程 stdin 发命令；写不了会自动 fallback RCON（需要 rcon_password）。
- wait_for_mc_ready：等待服务端/客户端就绪 = 日志匹配 或 端口开放。
- wait_for_port：等待某个 TCP 端口开放（如 25565/25575）。

## 三、游戏内交互
- send_game_command：通过 RCON 向运行中的服务端发命令（/give /tp /reload 等）。必须先有 RCON 密码和端口。
- game_input：通用输入；action=key 按键 / action=type 输入文本。
- press_key：向当前聚焦窗口发单个按键（e 开背包、esc 退出等）。注意窗口必须在前台。
- type_text：向当前聚焦窗口输入文本。
- wait_for_log：等待日志中出现指定正则。
- wait_for_screen：等待几秒后截图，可选 analyze_image 分析画面。
- verify_visual_loop：视觉验证循环 = 每轮先 RCON 发命令 → 截图 → analyze_image 分析，重复多轮。
  内部已含截图+识图，不要再外面重复 screenshot+analyze_image。

## 四、截图/视觉
- screenshot：截取当前屏幕，返回图片路径。
- analyze_image：用视觉模型分析图片，回答关于画面内容的问题。

## 五、日志/崩溃/产物
- read_crash_report：读取最新 crash-report。
- analyze_crash：分析崩溃报告，提取 cause/堆栈。
- verify_artifact：检查 jar/zip 是否包含 mods.toml/pack.mcmeta/assets/data，以及是否混入垃圾文件。
- tail_log：快速读日志末尾，比 read_file 更适合看最新输出。

## 六、Git/快照
- git_status：查看 git 状态。
- git_diff：查看当前改动 diff/stat。
- git_commit：提交改动（默认 git add -A）。
- snapshot：打一个 git 快照提交，返回 HEAD；适合当作“本次正确基线”。
- restore_snapshot：hard reset 回滚到指定快照。破坏性操作，只有确认要回退时才用。

【常见耦合与避坑】
- run_mod_test_cycle 已含 validate/build/gametest/parse，不要再单独重复调一遍。
- start_mc_server 若传了 RCON 参数，之后 send_game_command 直接可用；不要再手动 echo 进 server.properties。
- server_console 和 send_game_command 都可以发命令；优先前者（本地 stdin），失败再 RCON。
- wait_for_mc_ready 已经会看日志和端口，不要再同时调 wait_for_log + wait_for_port 重复等。
- verify_visual_loop 已经内部截图+识图，不要再在外面单独 screenshot+analyze_image 堆一遍。
- git_commit/snapshot 都会 add -A，不要先 git add 再调它们。
- 除非没有专用工具，否则不要用 bash 跑 gradlew、git、findstr、curl 等；用对应工具更稳。

【推荐测试闭环】
改代码 → validate_resources → run_mod_test_cycle → parse_gametest_results
→ 失败则 read_game_test_log / read_crash_report / analyze_crash / tail_log
→ 修复 → 再验证 → 通过后 git_commit/snapshot。
需要视觉验证时：start_mc_client → wait_for_screen → verify_visual_loop。
"""

# 兼容保留：完整手册 = 基础 + 扩展
TOOL_USAGE_GUIDE = BASE_TOOL_GUIDE + "\n\n" + EXTENDED_TOOL_GUIDE

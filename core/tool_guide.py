# -*- coding: utf-8 -*-
"""Base and extended tool usage guides.

The agent initially only receives BASE_TOOL_GUIDE. When it calls
activate_test_mode, EXTENDED_TOOL_GUIDE is appended to the system prompt and
all tools become visible for the rest of the session.
"""

BASE_TOOL_GUIDE = r"""【工具使用总则（精简版）】
1. 阶段式开放：当前只开放基础工具。需要构建/测试/游戏验证时，先调用 activate_test_mode 解锁全部工具（解锁后本会话永久有效）。
2. 优先用已有工具；只有没有对应工具才用 bash。文件统一 read_file/write_file/edit_file/glob/grep，禁止 bash 重定向写文件。
3. 完整工具手册：docs/agent/TOOL_GUIDE.md（需要时 read_file/grep 对应章节）。
4. 遇到错误/思考转圈：先 read docs/agent/ERROR_LIST.md；找不到再解决并追加。
5. 命名规则：根据用户需求取 modid/包名/类名/物品名，禁止 examplemod 等默认名。
6. 构建文件禁区：禁止修改 build.gradle/settings.gradle/gradle-wrapper（除非任务明确要求）。
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

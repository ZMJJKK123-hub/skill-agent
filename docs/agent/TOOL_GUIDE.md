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


---

## 附录 A：Windows / 环境硬规则（完整）

- 当前运行在 Windows cmd：只用 Windows 语法。
  - 建目录 mkdir dirname（不要 mkdir -p，cmd 会造出名为 -p 的目录）
  - 列目录 dir（不要 ls）；读文件 	ype filename（不要 cat）
  - 复制 copy / xcopy（不要 cp）；删除文件 del、删文件夹 
d /s /q（不要 
m -rf）
  - 找文件 where 或 dir /s /b（不要 ind/which）
  - 路径分隔符 \ 或 / 都行，但同一命令里不要混用。
- 写文件**只允许** write_file / edit_file（UTF-8）。禁止 bash 重定向（echo > file、python x.py > out.txt）：Windows 的 GBK 会让中文/emoji 变问号。如需保存命令输出，先用 bash 拿到，再用 write_file 写入。
- **禁止 taskkill /f /im python.exe 或 node.exe** —— agent 自己就是 python.exe，会把自己杀掉。
- 验证 HTTP 服务**禁止单独启动**（会触发 30s 超时被杀）。只能用下面这条“后台起→等→测→杀端口”的组合命令（PORT 换成实际端口）：
  `
  start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & for /f "tokens=5" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a
  `
  拆解：start /b cmd /c ... 后台启服务并重定向；	imeout /t 3 等 3 秒；curl 测接口；or /f 按端口（netstat+findstr）精确杀进程。

## 附录 B：Forge 1.21.11 环境硬事实（禁止违背）

- 目标版本：MC 1.21.11，Forge 构建 1.21.11-61.2.0。
- 版本格式 1.21.11-61.2.0（MC 版本-Forge 构建号）是有效版本，禁止判定为“版本不存在/版本号错误”。
- 依赖已写死在 build.gradle 的 
et.minecraftforge:forge:1.21.11-61.2.0，禁止修改；旧版映射知识（1.20.1=47.x 等）不适用。
- ForgeGradle 首次构建会自动下载依赖并缓存到 ~/.gradle/，属正常；禁止 curl 翻查/改写版本号。
- 构建失败处理：禁止改 forge 版本号；Minecraft 类找不到优先查编译 classpath（本地 recompiled.jar）；Could not resolve 先查缓存/重试联网；不要因单个错误反复重写 build.gradle/settings.gradle。
- 1.21.11 映射要点（详细见 ERROR_LIST.md / forge-simple-min-mod 技能）：
  - Item.Properties 里有 humanoidArmor(ArmorMaterial, ArmorType)，没有 ArmorItem 类。
  - ResourceLocation 改名为 Identifier（
et.minecraft.resources.Identifier）。
  - 注册表查询用 lookupOrThrow（不是 
egistryOrThrow）。
  - @GameTest 没有 	emplate 参数。

## 附录 C：系统能力（todo / 任务 DAG / 后台 / 团队 / 协议 / 工作树）

- **todo**：轻量线性待办，多步任务必用，同一时间只 in_progress 一项。
- **任务 DAG**（task_create/task_update/task_list/task_get）：复杂依赖用 locked_by 表达依赖；任务完成自动解锁下游；todo 是内存线性，task_* 是落盘 DAG。
- **后台执行**（run_in_background）：预计 >5 秒的命令走它（npm install、大构建、长测试）；立即返回 task_id，结果下轮以 <background-results> 注入；快命令（dir/type/echo/git status）走 bash。
- **团队**（spawn_teammate/send_to_teammate/team_status）：可并行的独立子任务交给 teammate（各自线程、独立上下文）；结果下轮以 <teammate-reports> 注入；每次运行清 roster（teammate 无持久记忆）。
- **协议**：request-response 状态机（pending→approved/rejected）。
  - Shutdown：用 
equest_shutdown 而非直接 shutdown；teammate 未落盘完成会拒绝，写完后批准退出。
  - Plan：队友用 submit_plan 提交高风险计划，leader 用 
espond_to_request 审批；<pending-requests> 是协议事件非用户输入，用 protocol_status 查看。
- **工作树隔离**：并行任务用 worktree；worktree_create→worktree_use 切换本 agent 工作基（bash/读写都被限制到该工作树）；worktree_run 在指定工作树内跑命令；worktree_remove(complete_task, merge) 拆除；worktree_list/recover 查看/恢复。

## 附录 D：行动驱动工作流（防止分析死循环）

- 顺序：**读 → 写 → 验证 → 失败才回头读**。
  1. 一轮内 run_read KNOWN_ISSUES.md + load_skill 相关技能；
  2. 立刻写代码/资源，不要动手前大量探索；
  3. 写完马上编译/测试（compileTestJava / run_test_gametest）；
  4. 只有测试失败/编译报错才回技能或 mc_java_sources 查证后修改重验。
- **禁止纯分析绕圈**：同一问题（某 API 报错、某 WARN）反复猜测、0 落地动作超过 3 轮就停；每轮思考要导向可执行下一步；拿不准先做最小验证（读 latest.log / 跑一条命令）。
- 注解在 class 上但运行时读不到：不要反复 javap，直接 gradlew clean compile... --rerun-tasks 全量重编重跑看实际日志。

## 附录 E：SIMPLE MOD FAST PATH（简单物品/方块+配方）

- 简单任务（无自定义实体/GUI/capabilities/网络）必须在 5-6 分钟内完成：
  1. 只加载 simple-mod-template、forge-items、forge-concept-registries 三个技能；
  2. 读一遍 KNOWN_ISSUES.md；不去翻 mc_java_sources/渲染源码；直接从 simple-mod-template 复制改名；
  3. 前 2 轮内开始写文件：物品注册类 + 改 ExampleMod + 每个物品写 ssets/<modid>/items/<name>.json 物品模型定义（缺了会“搜索图标不渲染”）+ item model/texture/lang + recipe（字符串 id，不是 {"item":...} 对象）；
  4. 用 gradlew build 验证（简单任务可跳过 GameTest；要求 GameTest 时用 forge-items 里的最小模板 + run_test_gametest）；
  5. build 成功且出 jar 后立即停手写总结，不再读更多技能；
  6. 不添加用户没要求的功能。

## 附录 F：skill-source 引用契约

- 改 MOD 代码前必须 load_skill，以技能为准，禁止凭记忆写 API。
- 每次修改后回复里必须带：
  `
  <skill-source>
  - change: <file path> | <修改摘要>
  - source: <skill name> -> <从技能复制的确切文段/API>
  </skill-source>
  `
- 无适用技能时写 “No skill source” 并说明原因；宁可声明缺失也别无依据写代码。
- 简单快速路径不要求 citations、不先研究，写完用 build/GameTest 验证，失败再回查。

## 附录 G：GameTest / 资源 / Gradle 细节

- 结构：src/main/java 只放生产代码（禁 @GameTest）；所有测试在 src/test/java；自检用 
un_test_gametest（runTestGameTestServer，扫 src/test），**禁止**用 run_game_test_server 做自检（只扫 src/main）。
- 资源（1.21.11）：物品必须有 items/<name>.json；引用不带扩展名；方块物品还需 blockstates/models/block/models/item/textures；配方字符串 ingredients + {"id":...,"count":N}；lang 键 item.<modid>.<name>/block.<modid>.<name>，en_us 和 zh_cn **都**要写。
- 8 个 Gradle 工具（main agent）返回 {success,exit_code,summary,error_details,raw_logs_snippet}：
  
un_data_gen / 
un_game_test_server / 
un_server(Done 即成功) / 
un_client / 
un_test_client / 
un_test_server / 
un_test_data / 
un_test_gametest(核心)。
- KNOWN_ISSUES.md：开工前必读、只读、禁止修改/删除；发现错误在最终总结里指出，由收尾自动收集去重回写模板。

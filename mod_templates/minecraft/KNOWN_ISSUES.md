# KNOWN ISSUES LOGBOOK（已验证问题与规避）

> 本文件是此环境的事实来源之一：**优先级高于技能描述**——若技能与本文条目冲突，以本文为准。
> 规则：开工前 `run_read KNOWN_ISSUES.md`；遇到新的重复性构建/运行错误，**追加**到文件末尾（永不覆盖旧条目）。

---

## [2026-08] 首次构建 JDK8 下载被 SSL 拦截（ForgeGradle Mavenizer）
- 症状: `gradlew build / runData / runServer` 报 `Failed to find JDK for version 8` + `JavaProvisionerException` / `PKIX path building failed`。
- 根因: ForgeGradle 配置阶段需自动下载其内部 JDK（含 Java 8），服务器 SSL/证书校验被代理/网络拦截。
- 规避: 无需手动切换 JAVA_HOME（Gradle 本身要求 JVM 17+，保持系统主 JDK 25/21 即可）。修复服务器 SSL 证书/网络代理（放行 github.com 与 adoptium 下载）后重新生成。

## [2026-08] run_bash 30s 超时杀进程树
- 症状: 启动服务器类命令（node server.js / npm start / python -m http.server）在 run_bash 中 30s 超时被杀。
- 根因: run_bash 有 30s 硬超时，前台等待服务器进程永远无法返回。
- 规避: 禁止单独执行启动命令。必须用一条组合命令「后台启动 → 等待 → 测试 → 杀进程」：
  `start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & for /f "tokens=5" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a`
  注意：禁止 `taskkill /f /im python.exe`（会杀掉 Agent 自身）。

## [2026-08] 禁止无技能依据写 MOD 文件
- 症状: 直接 write_file/edit_file 写 src/main、build.gradle、mods.toml 等 MOD 文件被拒绝。
- 根因: run_write/run_edit 对 MOD 工程文件强制要求先 `load_skill` 加载相关技能（技能依据护栏）。
- 规避: 先调用 load_skill 加载对应技能（如 forge-items / forge-blocks / forge-resources-* / forge-networking / forge-blockentities），再写文件。

## [2026-08] GameTest 自检必须用 run_test_gametest（src/test）
- 症状: 用 run_game_test_server 验证自己的 GameTest 却不运行。
- 根因: run_game_test_server 只扫描 src/main（随 jar 发布的蛋/奖励测试）；Agent 自检验证必须走 src/test。
- 规避: 自检一律用 `run_test_gametest`（gradlew runTestGameTestServer，扫描 src/test/java），修复循环：写测试 → 跑 → read_game_test_log 读 run/logs/latest.log → 修复 → 重跑至 Passed。

## [2026-08] src/main 禁止放 @GameTest
- 症状: src/main 里写了 @GameTest/@GameTestHolder，构建或规则检查报错。
- 根因: 项目结构规则：src/main/java 只放生产代码；所有测试必须在 src/test/java（如 src/test/java/com/<pkg>/tests/）。
- 规避: 把测试类移到 src/test/java 下，src/main 保持纯生产代码。

## [2026-08] 技能目录核心：forge 技能必须按域加载
- 症状: 写物品/方块/实体注册、JSON 资源、网络包、能力等时，跳过 load_skill 直接写，产出不符合规范需返工。
- 根因: Forge 技能按域拆分（forge-concept-registries / forge-blocks / forge-items / forge-resources-client / forge-resources-server / forge-networking / forge-datastorage-capabilities / forge-datastorage-codecs / forge-blockentities / forge-gameeffects-sounds / forge-gameeffects-particles / forge-gui / forge-concept-lifecycle / forge-concept-events / forge-concept-sides）。
- 规避: 写任何 MOD 代码/资源前，先按域 load_skill 再动手；每次改动后附 `<skill-source>` 说明。

## [2026-08] mc_source 仅作兜底，优先技能
- 症状: 类 API 不明确时直接读整个 mc_java_sources 文件，上下文爆炸。
- 根因: mc_source 是 FALLBACK-ONLY 工具，默认 head=120 行 / search=命中+5 行窗口，永不返回完整文件。
- 规避: 技能优先；技能不足/证伪时才用 mc_source（mode=head 或 mode=search+keyword），需要更多行时显式传 max_lines(1-500)。

## [2026-08] 数据驱动 GameTest 注册卡死（MC 26.2 / Forge 65.1.1）
- 症状: GameTest 自检反复绕圈——一直调 run_game_test_server 却跑不出自己的测试；写了 test_instance JSON 后测试函数仍找不到，报测试 0/0 通过或 "Unknown/No test"；日志长时间在 TEST_INSTANCE / TEST_FUNCTION / gatherTests / always_pass 之间打转。
- 根因: MC 26.2 / Forge 65.1.1 起 GameTest 已迁移为数据驱动注册表：测试实例从 `data/<modid>/test_instance/*.json` 加载（`"type":"function"` 引用 TEST_FUNCTION 注册表）；且 `BuiltInRegistries.TEST_FUNCTION` 在 mod 加载前已被冻结，Forge 不再自动扫描 `@GameTestNamespace`。必须手动把 @GameTest 方法写入 TEST_FUNCTION registry。
- 规避（完整正确模板，已验证 4/4 通过）:
  1) 测试类放 **src/test/java**：
     ```java
     @GameTestNamespace(MOD_ID)
     public class CrystalGameTests {
         @GameTest(structure = "minecraft:empty")
         public static void crystalItemRegistered(GameTestHelper helper) {
             helper.assertTrue(条件, "描述");
             helper.succeed();
         }
     }
     ```
  2) 在 TutorialMod 构造器调用注册工具（仅 GameTestServer 生效）:
     ```java
     if (!ForgeGameTestHooks.isGametestEnabled()) return;
     Map<Identifier, ForgeGameTestHooks.TestReference> tests =
         ForgeGameTestHooks.gatherTests(CrystalGameTests.class, null);
     MappedRegistry<Consumer<GameTestHelper>> reg = (MappedRegistry<Consumer<GameTestHelper>>)
         (MappedRegistry<?>) BuiltInRegistries.TEST_FUNCTION;
     reg.unfreeze(); // 注册表冻结前临时解冻
     for (Map.Entry<Identifier, ForgeGameTestHooks.TestReference> e : tests.entrySet())
         Registry.register(reg, ResourceKey.create(Registries.TEST_FUNCTION, e.getKey()),
             e.getValue().consumer());
     ```
  3) 每个测试写 `data/<modid>/test_instance/*.json`。`"function"` 键 = 类名全小写 **直接拼接** 方法名 snake_case 全小写（中间无分隔符）。例：类 `CrystalGameTests` + 方法 `crystalItemRegistered` → `tutorial_mod:crystalgametestscrystal_item_registered`。
     ```json
     { "type": "function", "function": "tutorial_mod:crystalgametestscrystal_item_registered",
       "environment": "minecraft:default", "structure": "minecraft:empty", "max_ticks": 100 }
     ```
  4) 自检只跑 `run_test_gametest`（同时加载 src/main + src/test）；run_game_test_server 只扫 src/main，永远跑不出 src/test 的测试（见上文两条）。

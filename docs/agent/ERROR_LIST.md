# Agent Error List（错误名单）

> 用途：当模型思考转圈、反复试错、遇到同类报错时，先读本文件。找到已知解法就直接采用；
> 遇到新的可复现错误，把“现象/根因/解法”追加到对应分类，防止下次再绕路。

## 1. 构建类

- **Gradle SSL/PKIX 错误**
  - 现象：`PKIX path building failed`、`SSLHandshakeException`、`Failed to find JDK for version 8`
  - 根因：公司网络/代理拦截，或 Gradle 下载依赖时证书校验失败
  - 解法：不要改版本号；修复证书/代理/网络后重试。首次构建下载依赖耗时长属正常。

- **`gradlew build` 失败但本机无 Java**
  - 现象：`java` 不在 PATH、JAVA_HOME 未设置
  - 解法：先 `detect_environment` 确认 Java 是否可用；没有则不要强行跑构建。

- **`Could not resolve`**
  - 解法：先查本地 Gradle 缓存，再让 Gradle 联网下载；不要反复改 build.gradle 版本号。

## 2. 资源加载类（1.21.11+）

- **物品没有模型**
  - 根因：MC 1.21.11+ 需要 `assets/<modid>/items/<name>.json`，只有 `models/item/*.json` 不够
  - 解法：补 `items/<name>.json`，内容形如 `{"model": {"type": "minecraft:model", "model": "modid:item/<name>"}}`

- **模型/贴图引用加了扩展名**
  - 根因：在 JSON 里写 `item/foo.json` / `textures/foo.png`
  - 解法：引用一律不带 `.json` / `.png`

- **vanilla 父模型/贴图报 missing**
  - 解法：`minecraft:` 命名空间属于原版，跳过本工作区校验；只校验自己 modid 的资源。

- **配方不加载**
  - 根因：1.21.11+ 配方结果必须 `{"id": "modid:item", "count": N}`，原料用字符串 id
  - 解法：按新格式重写 recipe JSON。

- **同一个 MOD 里中英文名混杂（如方块是英文、物品是中文）**
  - 根因：`zh_cn.json` 漏了某个 item/block 的翻译键，游戏在中文环境会回退到英文
  - 解法：每个注册的 Item/Block 必须在 `en_us.json` 和 `zh_cn.json` 都写对应键：`item.<modid>.<name>` / `block.<modid>.<name>`

## 3. GameTest 类

- **GameTest 全部未运行 / 无结果**
  - 根因：测试类可能放错位置，或没有 `@GameTest` 注解，或方法签名不是 1.21.11 标准
  - 解法：测试类放 `src/test/java`；确认注解与 `StringTestFunction` 签名正确；自检用 `run_test_gametest`，不要用 `run_game_test_server`。

- **`run_test_gametest` 失败**
  - 解法：先 `parse_gametest_results` 看失败列表，再 `read_game_test_log` / `tail_log` 看完整异常。

## 4. 服务端/客户端与游戏交互

- **RCON 连接失败**
  - 现象：`RCON authentication failed` / `connection refused`
  - 解法：`start_mc_server` 传 `rcon_port` + `rcon_password` 自动写配置；或手动确认 `server.properties` 的 `enable-rcon=true`。

- **按键/输入无效**
  - 根因：游戏窗口不在前台
  - 解法：先把游戏窗口切到前台，再 `press_key` / `type_text`。

- **后台启动后一直没就绪**
  - 解法：用 `mc_status` 看进程是否存活，`tail_log` 看日志，`wait_for_mc_ready` 等待；若进程已退出则看崩溃报告。

## 5. Windows/环境类

- **写文件中文/emoji 变问号**
  - 根因：bash 重定向用 GBK
  - 解法：永远用 `write_file` / `edit_file`。

- **删除长路径目录被拒**
  - 解法：Windows 下用 `cmd /c rd /s /q "\\?\<绝对路径>"`。

- **禁止 `taskkill /f /im python.exe`**
  - 原因：agent 自身就是 python.exe，会杀死自己。

## 6. 模型“转圈/反复试错”规则

- 同一错误连续猜测超过 2 次 → 立即停止推测，执行最小验证动作（读日志/读错误名单/跑一次构建）。
- 如果错误名单里已有同现象，必须直接采用已知解法，禁止重新探索。
- 如果错误名单没有，且已确认可复现 → 把“现象 / 根因 / 解法”追加到本文件对应分类，再继续。

## 7. API/模型调用类（Paratera）

- **`reasoning_content` must be passed back**
  - 现象：`The reasoning_content in the thinking mode must be passed back to the API. assistant message at index N has tool_calls but no reasoning_content`
  - 根因：Paratera 思考模式要求历史 assistant 消息保留 `reasoning_content`
  - 解法：`core/agent.py` 的 `message.to_dict()` 必须包含 `reasoning_content`（已修，别回退）。

- **模型名找不到**
  - 现象：`There are no healthy deployments for this model=deepseek-v4-flash`
  - 解法：Paratera 可用模型为 `DeepSeek-V4-Pro`；默认已切换。

## 8. 模板/构建类

- **`gradlew build` 的 `:test` 失败**
  - 现象：`test task did not discover any tests`，但 `src/test` 有 GameTest 源码
  - 根因：GameTest 不是 JUnit，Gradle 默认 `failOnNoDiscoveredTests=true`
  - 解法：模板 `build.gradle` 已加 `failOnNoDiscoveredTests=false`，不要删。

- **Gradle wrapper `.lck` 文件访问拒绝**
  - 现象：`FileNotFoundException ... gradle-9.5.0-bin.zip.lck (拒绝访问)`
  - 解法：这是环境/沙箱对 `C:\Users\59639\.gradle` 写权限限制；服务端需以 full-access 运行，或先手动跑通一次 Gradle 初始化。

## 9. 复杂功能 / 1.21.11 映射类

- **找不到 `ArmorItem` 类**
  - 现象：`import net.minecraft.world.item.ArmorItem; 找不到符号`
  - 根因：1.21.11 已移除 `ArmorItem` 类，装甲用 `Item.Properties()` 的 `humanoidArmor(ArmorMaterial, ArmorType)`
  - 解法：自定义 Item 继承 `Item`，构造器里 `super(properties.humanoidArmor(material, type))`；护甲材料用 `ArmorMaterials.IRON` 等。

- **找不到 `ResourceLocation`**
  - 现象：`import net.minecraft.resources.ResourceLocation; 找不到符号`
  - 根因：1.21.11 中 `ResourceLocation` 改名为 `Identifier`
  - 解法：用 `net.minecraft.resources.Identifier`，如 `Identifier.fromNamespaceAndPath(modid, name)`。

- **找不到 `registryOrThrow`**
  - 现象：`方法 registryOrThrow(ResourceKey<Registry<Item>>) 找不到`
  - 根因：1.21.11 的 `RegistryAccess` 用 `lookupOrThrow` 而不是 `registryOrThrow`
  - 解法：`helper.getLevel().registryAccess().lookupOrThrow(Registries.ITEM).get(key)`。

- **`@GameTest` 报找不到 `template()`**
  - 根因：该版本 `@GameTest` 没有 `template` 参数
  - 解法：直接用 `@GameTest`，不要写 `@GameTest(template = "empty")`。

- **改 build.gradle 导致构建系统损坏**
  - 现象：agent 把 ForgeGradle 换成 NeoGradle，插件解析失败，Supervisor 反复告警
  - 根因：无必要触动构建文件
  - 解法：模板已正确配置 `net.minecraftforge.gradle` + `forge:1.21.11-61.2.0`；构建失败先查代码/错误名单，禁止切构建系统。

## 追加格式

```md
- **一句话现象**
  - 现象：...
  - 根因：...
  - 解法：...
```
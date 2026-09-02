# KNOWN ISSUES — MC 1.21.11 / Forge 1.21.11-61.2.0（agent 只读）

> 本文件是该版本（forge-1.21.11 模板）独立的环境经验沉淀，只对使用此模板的会话生效。
> 由系统在会话结束后自动追加（finalize_known_issues）。agent 只读遵守，不修改；旧条目永不删除。
>
> 当前环境硬性事实（来自 core/config.py）：
> - MC 1.21.11 · Forge 1.21.11-61.2.0（build.gradle 已写死，禁止修改）
> - Loader version = [61,)，Minecraft versionRange = [1.21.11,1.22)
> - Java toolchain 21；Mojang mappings official 1.21.11
> - ForgeGradle 首次构建自动从 maven.minecraftforge.net 下载依赖并缓存，禁止 curl 在线翻查/改写版本号


## [2026-08-31] AgentBridge 放置与 dist 守卫（4e9bcf6328e5 红宝石剑实测）
- 症状: 把 starter/bridge/AgentBridge.java 放进 src/main 并在 @Mod 构造器直接 `new com.agentbridge.AgentBridge();` 后，runTestGameTestServer 报 `Attempted to load class net/minecraft/client/gui/components/events/GuiEventListener for invalid dist DEDICATED_SERVER`（DISTXFORM），mod 加载失败、GameTest 全挂。
- 根因: AgentBridge import 客户端专属类；专用服务器一旦加载该类必炸。反向放置（src/test + 反射 + runTestClient）也不行——test 源集在重复类加载器里，主构造器的 Class.forName 找不到（webserv_moonstone 实测 LinkageError）。
- 规避: 唯一正确姿势 = src/main 放置 + 构造器末尾 `if (net.minecraftforge.fml.loading.FMLEnvironment.dist.isClient()) { new com.agentbridge.AgentBridge(); }`（守卫使服务器路径永不触发类加载）+ `start_mc_client` 启动。工具描述/指南/starter 注释三处已统一为该姿势。


## [2026-09-01] 方块物品名字回显 key（jarverify 实测）
- 症状: /give 后聊天显示 `item.<modid>.<name>` 而不是本地化名字；快捷栏 hover 同样。
- 根因: 1.21.11 里 `Item.Properties` 默认翻译前缀是 `item.`（`ITEM_DESCRIPTION_ID`），BlockItem 不自动改；lang 写了 `block.` 前缀就两边不匹配。
- 规避: 方块物品注册链上加 `.useBlockDescriptionPrefix()`（推荐，配 `block.` lang），或 lang 改用 `item.` 前缀。验证方式：/give 看聊天回执的名字。

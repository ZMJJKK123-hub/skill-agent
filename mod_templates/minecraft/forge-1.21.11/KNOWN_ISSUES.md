# KNOWN ISSUES — MC 1.21.11 / Forge 1.21.11-61.2.0（agent 只读）

> 本文件是该版本（forge-1.21.11 模板）独立的环境经验沉淀，只对使用此模板的会话生效。
> 由系统在会话结束后自动追加（finalize_known_issues）。agent 只读遵守，不修改；旧条目永不删除。
>
> 当前环境硬性事实（来自 core/config.py）：
> - MC 1.21.11 · Forge 1.21.11-61.2.0（build.gradle 已写死，禁止修改）
> - Loader version = [61,)，Minecraft versionRange = [1.21.11,1.22)
> - Java toolchain 21；Mojang mappings official 1.21.11
> - ForgeGradle 首次构建自动从 maven.minecraftforge.net 下载依赖并缓存，禁止 curl 在线翻查/改写版本号
# 常见错误与解决方案

> **通用**: 适用于Forge 65.x (MC 26.2)

---

## 注册错误

| 错误现象 | 原因 | 解决方案 |
|---------|------|---------|
| `Registry entry not present` | BlockItem注册名与Block不同 | 确保同名: `ITEMS.register("my_block", ...)` |
| 紫黑方块/物品 | 纹理文件缺失 | 检查 `textures/block/<name>.png` 或 `textures/item/<name>.png` |
| 物品无图标 | 模型JSON指向错误纹理路径 | `layer0` 应为 `<modid>:item/<name>` |
| `Duplicate registry entry` | 重复注册 | 检查两个DeferredRegister是否注册了同名 |
| 方块在创造模式为空气 | BlockItem未创建 | 需在ModItems中同时注册BlockItem |

---

## Gradle/构建错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `Could not find forge` | forge_version格式错误 | MC 26.2用 `65.1.0` |
| `Unsupported class file major version 65` | JDK版本不对 | MC 26.x需要JDK 21 |
| 插件找不到 | settings.gradle缺少仓库 | 添加 `maven { url 'https://maven.minecraftforge.net/' }` |
| `Could not resolve: net.minecraftforge:forge` | 依赖格式错误 | 检查 `${mc}-${forge}` 格式如 `26.2-65.1.0` |

---

## 资源文件错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 配方不工作 | result格式为旧式 | MC 26.x用 `{"id":"mod:item","count":1}` |
| 方块无正确挖掘工具 | 缺少mineable标签 | 添加 `mineable/pickaxe.json` 标签 |
| 方块被秒挖 | 缺少needs_*_tool标签 | 添加 `needs_diamond_tool.json` 等 |
| 模型不显示 | blockstate JSON错误 | 检查model路径和variants配置 |

---

## API 变更 (1.21.x -> 26.x)

| 旧API | 新API |
|-------|------|
| `Registry.BLOCK` | `ForgeRegistries.BLOCKS` |
| `"result": "modid:item"` | `"result": {"id": "modid:item", "count": 1}` |
| `DamageSource.IN_FIRE` | `DamageTypes.IN_FIRE` (damage type体系) |
| NBT `CompoundTag` | 逐步迁移到Data Component |
| `Item.Properties()` | `Item.Properties()` (不变，但某些内部API变) |

---

## 网络错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 数据包收不到 | 未在两端注册 | C2S和S2C都需要在SimpleChannel注册 |
| `IndexOutOfBoundsException` | packetId冲突 | 确保packetId自增不重复 |
| 客户端数据不同步 | 未加enqueueWork | `ctx.enqueueWork(() -> { ... })` |

---

## 事件错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 事件不触发 | 注册到错误总线 | MOD Bus -> `modEventBus`; 运行时 -> `MinecraftForge.EVENT_BUS` |
| `@SubscribeEvent` 无效 | 方法非static或类未注册 | 确保类注册到事件总线 |

---

name: minecraft-registry
description: "Minecraft Registry 注册表机制：Categories 分类（Built-in registries 内置注册表 硬编码 内容不可修改 跨世界共享、Writable registries 可写注册表 从数据包加载 世界绑定 数据依赖、Network-synchronized registries 网络同步注册表 可写注册表通过 registry_data 数据包同步到客户端）、Indexing 索引（命名空间ID映射到值 如BLOCK注册表的grass_block、数字ID仅网络使用缩短数据、标签映射到多个值 如#air=air+cave_air+void_air 标签永不硬编码 可由数据包定义任何注册表、同步注册表 通过 update_tags 数据包同步标签）、Structure 结构（每个可写注册表有反序列化器 如ENCHANTMENT↔附魔格式、数据包路径P：文件 data/<N>/<P>/<I>.json 注册值 N:I、标签文件 data/<N>/tags/<P>/<I>.json 包含子目录 创建 #N:I 标签、注册表本身注册在特殊注册表中 不能添加或移除）。"
whenToUse: "Use when understanding how datapack registries (enchantment, jukebox_song, tags, etc.) work."

---

# Registries

This content applies only to Java Edition.

Registries are a widely used game mechanism organizing values of the same type.

## Categories

- **Built-in registries**: hardcoded; contents cannot be modified; shared across worlds.
- **Writable registries**: loaded from datapacks; world-bound and data-dependent.
- **Network-synchronized registries**: writable registries synced to clients via the `registry_data` packet during configuration.

## Indexing

- Namespace IDs map to values (e.g. `grass_block` in the `BLOCK` registry).
- Numeric IDs are used only on the network to shorten data.
- Tags map to multiple values (e.g. `#air` = `air` + `cave_air` + `void_air`); tags are never hardcoded and can be defined by datapacks for any registry. Synced registries (all built-in + network-synchronized writable ones) sync tags via the `update_tags` packet.

## Structure

Every writable registry has a deserializer (e.g. `ENCHANTMENT` ↔ enchantment format) and a datapack path P: files `data/<N>/<P>/<I>.json` register value `N:I`. Example: `data/minecraft/jukebox_song/5.json` registers `minecraft:5`. Tags: files `data/<N>/tags/<P>/<I>.json` (including subdirectories) create tag `#N:I`, e.g. `data/minecraft/tags/block/mineable/axe.json` → `#minecraft:mineable/axe`.

Registries themselves are registered in a special registry; they cannot be added or removed.

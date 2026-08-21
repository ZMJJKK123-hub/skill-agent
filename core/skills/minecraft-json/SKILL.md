---

name: minecraft-json
description: "Minecraft JSON 语法：Syntax 语法（Unicode码点序列、6个结构符号 []{}:,, 字符串、数字、3个字面量 true/false/null null在数据包标准文件中不使用）、Data Value Types 数据值类型（Object 对象 {} 键值对 键唯一、Array 数组 [] 逗号分隔 可混合类型、String 字符串 双引号+转义、Number 数字 整数/小数/指数、Boolean 布尔 true/false）、Serialization 序列化（数据包文件加载时反序列化为程序对象、游戏验证数据 额外对象成员可能丢弃 数值范围重新计算、严格验证 非法值可能抛出异常阻塞加载、所有必要属性必须存在 否则加载失败）、Usage 使用场景（Bedrock 书/标志牌/自定义名称/tellraw/titleraw、pack.mcmeta/manifest.json、资源包模型/音效/UI文件、行为包实体行为文件、进度和统计数据、启动器配置、Java数据包文件：进度/战利品表/标签/配方/维度/维度类型/谓词等）。"
whenToUse: "Use when writing or validating JSON files in datapacks and resource packs."

---

# JSON in Minecraft

JavaScript Object Notation (JSON) is a lightweight data interchange format used by Minecraft for:

- (Bedrock) text in written books, signs, custom names, `/tellraw`, `/titleraw`
- `pack.mcmeta` (Java resource/datapack descriptors) and `manifest.json` (Bedrock addons)
- Model, sound event, and UI files in resource packs; entity behavior files in behavior packs
- Advancements and statistics (`.minecraft/saves/*/data/stats/*.json`)
- Launcher profiles (`launcher_profiles.json`), version metadata
- (Java) datapack files: advancements, loot tables, tags, recipes, dimensions, dimension types, predicates, etc.

## Syntax

JSON text is a sequence of Unicode code points forming valid JSON data values: six structural symbols (`[` `{` `]` `}` `:` `,`), strings, numbers, and three literals (`true`, `false`, `null` — `null` is not used in Minecraft's datapack standard files).

Data value types: object, array, string, number, boolean, null.

- **Object**: `{...}` with 0+ key-value pairs; keys are strings, values any type; keys must be unique.
- **Array**: `[...]` with 0+ comma-separated values; unlike NBT lists, values may have mixed types.
- **String**: double-quoted with `\` escapes.
- **Number**: integers, decimals, and exponents (e.g. `2`, `-0.5`, `3e6`).
- **Boolean**: `true` or `false`.

## Serialization

Datapack files are deserialized into program objects when loaded. The game validates the data — extra object members may be dropped and numeric ranges recomputed; under strict validation, illegal values can throw during datapack load and block it. All "necessary" properties must be present or loading fails.

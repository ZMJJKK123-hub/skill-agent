---

name: minecraft-namespaced-id
description: "Minecraft Namespaced ID 命名空间ID：Definition 定义（namespace:path 命名空间唯一性范围 默认minecraft、path 通常镜像包内文件路径、字符串形式用:连接）、Legal Characters 合法字符（Java 命名空间和路径 0-9/a-z/_/-/. 推荐snake_case、/在命名空间非法但在路径允许目录分隔符、命名空间不能是..；Bedrock 除/和:外任何字符）、String Conversion 字符串转换（ID→字符串 ns:path、字符串→ID 约束：最多一个:、两部分满足合法字符规则、有:时前部分不能包含/或.、无:时命名空间默认minecraft）、Usage 使用（Java Registry Content 所有注册表对象使用命名空间ID；Java Non-Registry Content 数据包：函数/结构模板/标签；资源包：装备模型/字体/烘焙模型/方块状态映射/物品模型定义/音效/着色器/后处理管线/纹理/路点样式；其他可修改内容：boss bars/命令存储/属性修饰符/随机序列/自定义点击事件标识符等）、Actual File Paths 实际文件路径（<pack type>/<namespace>/<object type>/<name>.<extension>↔ID <namespace>:<name>）、Namespaces 命名空间（minecraft 游戏自身命名空间 默认 不指定时使用；Custom namespaces 每个项目/内容使用自己的 避免重名；Other built-in namespaces realms/brigadier）。"
whenToUse: "Use when referencing objects by namespaced ID in data packs, resource packs, or commands."

---

# Namespaced ID

Namespaced identifiers (identifiers / resource locations / namespaced strings) identify game objects unambiguously: `namespace:path`. The default namespace is `minecraft` (Realms uses `realms`).

## Definition

- **Namespace** — uniqueness scope (default `minecraft`).
- **Path** — often mirrors the file path inside the pack; may be a pure identifier.
- String form joins them with `:`.

## Legal Characters

Java Edition:

- Namespace and path: `0-9`, `a-z`, `_`, `-`, `.` (snake_case recommended).
- `/` is illegal in namespaces but allowed in paths (directory separators).
- The namespace cannot be `..` (literally).

Bedrock: any characters except `/` and `:` (slash allowed in loot table/function names but not namespaces).

## String Conversion

ID → string: always possible (`ns:path`). String → ID constraints:

- At most one `:`.
- Both parts must satisfy the legal-character rules.
- With a `:` present, the part before it must not contain `/` or `.`.
- Without a `:`, the namespace defaults to `minecraft`.

## Usage

### Java — Registry Content

All registry objects (blocks, items, entity types, recipes, advancements, tags, enchantments, ...) use namespaced IDs.

### Java — Non-Registry Content

- Data packs: functions, structure templates, tags.
- Resource packs: equipment models, fonts, baked models, blockstate mappings, item model definitions, sounds, sound event reference names, shaders (includes + core), post-processing pipelines, textures, waypoint styles.
- Other modifiable content: boss bars, command storage, attribute modifiers, random sequences, custom click event identifiers, post-processing render targets, stopwatches, time markers.

### Bedrock

Built-in blocks/items/entities/effects/dimensions/biomes/features, item components in commands, add-on components, add-on JSON schemas, GameTest-enabled components; behavior pack content (blocks, entities, items, spawn rules, biomes, features, feature rules, function domains, recipes, structures, GameTests, NPC dialogs); resource pack content (attachments, camera perspectives, particles, fog settings).

## Actual File Paths (Java)

The file path is usually `<pack type>/<namespace>/<object type>/<name>.<extension>` ↔ ID `<namespace>:<name>`; `/`s inside the object type or name are directory separators. (Some resource pack elements, like GUI textures, don't rely on namespaced IDs.)

## Namespaces

- **`minecraft`** — the game's own namespace; the default when unspecified (`something` == `minecraft:something`). Only use it to override vanilla data or append to vanilla tags (e.g. `#minecraft:load`).
- **Custom namespaces** — each project/content should use its own; reuse another's only to override or extend it. Prefer specific names: avoid trivial abbreviations (`nc`) and vague words (`battle_royale`; `player_name_battle_royale` is better).
- **Other built-in namespaces** — `realms` (Realms language files `assets/realms/lang/<code>.json` and textures), `brigadier` (brigadier command argument types).

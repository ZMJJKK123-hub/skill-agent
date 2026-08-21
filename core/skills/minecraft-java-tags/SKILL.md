---

name: minecraft-java-tags
description: "Minecraft Java Tags Java版标签：Definition 定义（data/<namespace>/tags/<registry path>/<name>.json、每个注册表内容可有标签 除了advancements和recipes、Functions 在 tags/function/ 下、标签ID命名空间格式 #前缀引用 #minecraft:air 块标签）、File Format 文件格式（replace 默认false 覆盖低优先级包同ID标签 false=追加、values 列表：资源ID字符串、#标签ID 引用其他标签、{id required} required:false 缺失条目静默忽略）、Loading Behavior 加载行为（底部向上加载每个包、缺失必需条目或循环→标签无效、可选 required:false 缺失条目忽略、上包 replace:true 丢弃下层数据 即使下层标签无效 上层正常加载、上包 replace:false 合并 下层无效标签使合并标签无效）、Usage 使用（测试成员资格 任何列出条目匹配、原版标签控制游戏行为 方块标签 climbable 等 物品标签 dyeable 等 实体类型标签节肢动物 蛛网、进度/配方使用标签条件）、Vanilla Tag Directories 原版标签目录（data/minecraft/tags/：banner_pattern/block/damage_type/dialog/enchantment/entity_type/fluid/function/game_event/instrument/item/painting_variant/point_of_interest_type/potion/timeline/villager_trade/worldgen/）、Examples 示例（新标签 my_logs.json、嵌套标签 #minecraft:logs、可选条目 required:false、扩展原版 sword_efficient 羊毛、替换原版 beacon_base_blocks lodestone）。"
whenToUse: "Use when defining or extending tags in data packs."

---

# Tags (Java Edition)

Tags group game resources via JSON files. Java Edition only (Bedrock has its own tags).

## Definition

Tags live in `data/<namespace>/tags/<registry path>/<name>.json`. Every registry content can have tags except advancements and recipes (though not every registry tag has a call site). Functions (not registry content) sit at the same level under `tags/function/`.

Tag IDs follow the namespaced-ID format and are referenced with a `#` prefix (`#minecraft:air` = the block tag; `minecraft:air` = the block).

## File Format

- `replace` (default false) — fully override lower-priority packs' same-ID tag (false = append).
- `values` (required) — list of:
  - `"<ns>:<path>"` — a resource.
  - `"#<ns>:<path>"` — another tag (cycles fail loading).
  - `{id, required (default true)}` — with `required: false`, a missing entry is silently ignored instead of failing the tag.

## Loading Behavior

Tags load bottom-up per pack:

- Missing required entries or cycles → the tag is invalid.
- Optional (`required: false`) missing entries are ignored.
- Upper pack with `replace: true` discards lower data (even if the lower tag was invalid, the upper one loads fine).
- Upper pack with `replace: false` merges; an invalid lower tag makes the merged tag invalid.

## Usage

Testing membership is the common use (any listed entry matches). Vanilla tags gate behavior in the game source (block tags: climbable etc.; item tags: dyeable etc.; entity type tags: arthropods for Bane of Arthropods; advancements/recipes use tags for conditions). Vanilla ships no functions or function tags, but datapack-defined ones load normally.

## Vanilla Tag Directories

`data/minecraft/tags/`: `banner_pattern`, `block`, `damage_type`, `dialog`, `enchantment`, `entity_type`, `fluid`, `function` (not preset in client.jar), `game_event`, `instrument`, `item`, `painting_variant`, `point_of_interest_type`, `potion`, `timeline`, `villager_trade`, `worldgen/` (biome, configured_feature/feature, flat_level_generator_preset, structure, world_preset, ...). Full lists and meanings: see the Minecraft Wiki "Tag" pages.

## Examples

- New tag `data/example/tags/block/my_logs.json`: `{"values":["minecraft:oak_log","minecraft:birch_log","minecraft:spruce_log"]}`; use `#example:my_logs` (e.g. `/fill ... air replace #example:my_logs`).
- Nested tags: `{"values":["#minecraft:logs","minecraft:tnt"]}`.
- Optional entries: `{"values":[{"id":"example:custom_item","required":false}]}`.
- Extending vanilla: `data/minecraft/tags/block/sword_efficient.json` with `{"values":["#minecraft:wool"]}` (wool breaks faster with swords).
- Replacing vanilla: `data/minecraft/tags/block/beacon_base_blocks.json` with `{"replace":true,"values":["minecraft:lodestone"]}` (beacon bases = lodestone only).

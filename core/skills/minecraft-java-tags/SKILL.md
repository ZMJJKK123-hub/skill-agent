---

name: minecraft-java-tags
description: "Tags (Java Edition) — directory structure, file format, replace/required, loading."
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

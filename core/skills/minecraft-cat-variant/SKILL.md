---

name: minecraft-cat-variant
description: "Minecraft Cat Variant 猫变体定义：CAT_VARIANT 注册表、data/<namespace>/cat_variant/ 数据包路径、tags/<namespace>/tags/cat_variant/ 标签、JSON 格式（asset_id 成年猫纹理、baby_asset_id 幼猫纹理、spawn_conditions 生成条件）、asset_id/baby_asset_id 纹理解析（assets/<namespace>/textures/<path>.png）、Spawn Conditions 生成条件选择器（condition.type 生物群系/月光亮度/结构、biome biomes 标签/ID/列表、moon_brightness range 范围（满月1/新月0）、structure structures 标签/ID/列表、priority 优先级 随机打破平局）、服务器启动加载（/reload 不重新加载）、CAT_VARIANT 注册表至少一个元素、最高优先级有效选择器生成猫变体。"
whenToUse: "Use when writing datapack cat_variant definitions or custom cat variants."

---

# Cat Variants

This content applies only to Java Edition.

Cat variant definition files define cat variants and their spawn rules.

## Definition format

Cat variants use the `CAT_VARIANT` registry; the datapack path is `cat_variant` (definitions in `data/<namespace>/cat_variant`, tags in `data/<namespace>/tags/cat_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) cat texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby cat texture; resolved the same way.
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): `type` (string, required): `biome` (`biomes` string/list: tag `#`, ID, or list), `moon_brightness` (`range` min-max bounds; full moon 1, new moon 0), or `structure` (`structures` string/list: tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties resolved randomly.

## Definition behavior

Cat variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CAT_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a cat, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

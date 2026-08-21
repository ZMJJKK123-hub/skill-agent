---

name: minecraft-pig-variant
description: "Minecraft Pig Variant 猪变体定义：PIG_VARIANT 注册表、data/<namespace>/pig_variant/ 数据包路径、JSON 格式（asset_id 成年猪纹理、baby_asset_id 幼猪纹理、model 模型类型 normal/cold、spawn_conditions 生成条件选择器）、asset_id/baby_asset_id 纹理解析（assets/<namespace>/textures/<path>.png）、Model 模型类型（normal 温带/热带猪、cold 寒冷猪）、Spawn Conditions 生成条件选择器（condition.type 生物群系/月光亮度/结构、biome biomes 标签/ID/列表、moon_brightness range 范围（满月1/新月0）、structure structures 标签/ID/列表、priority 优先级 随机打破平局）、服务器启动加载（/reload 不重新加载）、PIG_VARIANT 注册表至少一个元素、最高优先级有效选择器生成猪变体。"
whenToUse: "Use when writing datapack pig_variant definitions or custom pig variants."

---

# Pig Variants

This content applies only to Java Edition.

Pig variant definition files define pig variants and their spawn rules.

## Definition format

Pig variants use the `PIG_VARIANT` registry; the datapack path is `pig_variant` (definitions in `data/<namespace>/pig_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) pig texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby pig texture; resolved the same way.
  - `model` (string, default `normal`): `normal` (temperate/tropical pigs) or `cold` (cold pigs).
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): conditions for the selector; absent = always.
        - `type` (string, required): `biome` (checks `biomes` — tag `#`, ID, or list), `moon_brightness` (checks `range` min-max bounds; full moon 1, new moon 0), or `structure` (checks `structures` — tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties are resolved randomly.

## Definition behavior

Pig variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `PIG_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a pig, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

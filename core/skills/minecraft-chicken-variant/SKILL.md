---

name: minecraft-chicken-variant
description: "Minecraft Chicken Variant 鸡变体定义：CHICKEN_VARIANT 注册表、data/<namespace>/chicken_variant/ 数据包路径、JSON 格式（asset_id 成年鸡纹理、baby_asset_id 幼鸡纹理、model 模型类型 normal/cold、spawn_conditions 生成条件）、asset_id/baby_asset_id 纹理解析（assets/<namespace>/textures/<path>.png）、Model 模型类型（normal 温带/热带鸡、cold 寒冷鸡）、Spawn Conditions 生成条件选择器（condition.type 生物群系/月光亮度/结构、biome biomes 标签/ID/列表、moon_brightness range 范围（满月1/新月0）、structure structures 标签/ID/列表、priority 优先级 随机打破平局）、服务器启动加载（/reload 不重新加载）、CHICKEN_VARIANT 注册表至少一个元素、最高优先级有效选择器生成鸡变体。"
whenToUse: "Use when writing datapack chicken_variant definitions or custom chicken variants."

---

# Chicken Variants

This content applies only to Java Edition.

Chicken variant definition files define chicken variants and their spawn rules.

## Definition format

Chicken variants use the `CHICKEN_VARIANT` registry; the datapack path is `chicken_variant` (definitions in `data/<namespace>/chicken_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) chicken texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby chicken texture.
  - `model` (string, default `normal`): `normal` (temperate/tropical chickens) or `cold` (cold chickens).
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): `type` (string, required): `biome` (`biomes` string/list: tag `#`, ID, or list), `moon_brightness` (`range` min-max bounds; full moon 1, new moon 0), or `structure` (`structures` string/list: tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties resolved randomly.

## Definition behavior

Chicken variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CHICKEN_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a chicken, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

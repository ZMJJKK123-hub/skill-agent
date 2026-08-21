---

name: minecraft-frog-variant
description: "Minecraft Frog Variant 青蛙变体定义：FROG_VARIANT 注册表、data/<namespace>/frog_variant/ 数据包路径、tags/frog_variant/ 标签、JSON 格式（asset_id 青蛙纹理、spawn_conditions 生成条件选择器）、asset_id 纹理解析（assets/<namespace>/textures/<path>.png）、Spawn Conditions 生成条件选择器（condition.type 生物群系/月光亮度/结构、biome biomes 标签/ID/列表、moon_brightness range 范围（满月1/新月0）、structure structures 标签/ID/列表、priority 优先级 随机打破平局）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载、FROG_VARIANT 注册表至少一个元素）、生成青蛙时评估所有变体选择器 选择最高优先级有效选择器生成对应变体。"
whenToUse: "Use when writing datapack frog_variant definitions or custom frog variants."

---

# Frog Variants

This content applies only to Java Edition.

Frog variant definition files define frog variants and their spawn rules.

## Definition format

Frog variants use the `FROG_VARIANT` registry; the datapack path is `frog_variant` (definitions in `data/<namespace>/frog_variant`, tags in `data/<namespace>/tags/frog_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) frog texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `spawn_conditions` (list, required): variant spawn selectors controlling spawn conditions and priority.
    - One selector (compound):
      - `condition` (compound): conditions under which the selector applies; absent = always.
        - `type` (string, required): selector condition type.
          - `biome`: checks the biome at the spawn point; `biomes` (string/list, required): biome tag (`#`), ID, or list.
          - `moon_brightness`: checks moon brightness; `range` (double/compound, required): min-max bounds; full moon = 1, new moon = 0.
          - `structure`: checks whether the spawn point is inside the given structure pieces; `structures` (string/list, required): structure tag (`#`), ID, or list.
      - `priority` (int, required): selection priority. The game picks the valid selectors with the highest priority across all variants; ties are resolved randomly.

## Definition behavior

Frog variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `FROG_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a frog, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

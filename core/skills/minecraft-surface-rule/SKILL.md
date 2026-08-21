---

name: minecraft-surface-rule
description: "Minecraft Surface Rule 表面规则（材质规则）：Definition Format 定义格式（26.3后 MATERIAL_RULE 注册表 data/<namespace>/worldgen/material_rule/、MATERIAL_CONDITION 注册表 worldgen/material_condition、条件和序列决策树 在位置放置方块）、Rule Types 规则类型（bandlands badlands 陶瓦条带、block 放置结果方块状态 result_state、condition 条件 if_true 表面规则条件+then_run 成功时递归规则、sequence 序列 规则列表 每个位置取第一个成功规则）、Condition Types 条件类型（above_preliminary_surface 位置高于初步表面层、biome 生物群系 biome_is 列表、hole 表面厚度<0 噪声计算、noise_threshold 噪声阈值 noise min/max_threshold is_3d、not 取反 invert 递归条件、steep 陡坡 阴影面 高度差>4方块、stone_depth 到表面/洞穴表面距离≤限制 offset/add_surface_depth/secondary_depth_range/surface_type floor/ceiling、temperature 温度 允许雪、vertical_gradient 垂直渐变 false_at_and_above/true_at_and_below 成功概率线性插值、water 流体下厚度 offset/surface_depth_multiplier/add_stone_depth、y_above Y以上 anchor/surface_depth_multiplier/add_stone_depth）、Application Order 应用顺序（1检查eroded_badlands 放置陶瓦柱、2应用噪声设置表面规则、3检查frozen_ocean/deep_frozen_ocean 放置冰山）。"
whenToUse: "Use when authoring surface/material rules in noise settings (worldgen)."

---

# Surface Rule

Material rules (surface rules) replace the initial terrain blocks after generation, giving biomes their surface (grass, sand, ...) and also placing bedrock/deepslate. Java Edition only.

## Definition Format

From 26.3: registry `MATERIAL_RULE`, data pack path `worldgen/material_rule` (files in `data/<namespace>/worldgen/material_rule/`; tags in `tags/worldgen/material_rule/`); conditions use registry `MATERIAL_CONDITION` at `worldgen/material_condition`. A surface rule is a decision tree of conditions and sequences placing blocks at positions; noise settings reference rules by ID or inline.

## Rule Types

- `bandlands` (sic, wiki typo for "badlands") — places badlands terracotta bands.
- `block` — places `result_state` (block state).
- `condition` — `if_true` (a surface rule condition) + `then_run` (recursive rule applied on success).
- `sequence` — `sequence` (list of rules; may be empty; entries by ID or inline): each position gets the first successful rule.

## Condition Types

- `above_preliminary_surface` — position is above the preliminary surface level (interpolated `noise_router.preliminary_surface_level`, offset 8 down, plus surface thickness).
- `biome` — `biome_is` (list of biome IDs, may be empty).
- `hole` — surface thickness < 0 (surface thickness = ⌊2.75s + 0.25r + 3⌋ from the `surface` noise at [X,0,Z] and a position random).
- `noise_threshold` — `noise` (noise ID), `min_threshold`/`max_threshold` (closed interval), `is_3d` (default false — sample at Y=0 vs at the position).
- `not` — `invert` (recursive condition or ID).
- `steep` — shaded (north/east facing) steep slope with >4 block height difference (heightmap `WORLD_SURFACE_WG`).
- `stone_depth` — distance to the surface/cave surface ≤ limit: `offset` (max distance), `add_surface_depth` (add surface thickness), `secondary_depth_range` (add `range × surface_secondary` noise), `surface_type` (`floor` — distance to the nearest air above minus 1; `ceiling` — distance to the nearest liquid/air below). (Carver stage: distances are always 1.)
- `temperature` — biome temperature allows snow (from `temperature`, `temperature_modifier`, and Y).
- `vertical_gradient` — `random_name` (seed), `false_at_and_above` (vertical anchor: always fail at/above), `true_at_and_below` (vertical anchor: always pass at/below); between them success probability = (false_at_and_above − Y)/(false_at_and_above − true_at_and_below).
- `water` — thickness under a fluid (negative values): `offset` (relative to the fluid surface; surface stage uses the fluid block's top face, carver stage the bottom face; values > −1 pass only when no fluid between, −1 behaves like > −1 at surface stage and always passes in carver stage), `surface_depth_multiplier` (−20..20, adds surface thickness × value), `add_stone_depth` (use distance + non-fluid blocks between this Y plane and the air above).
- `y_above` — `anchor` (vertical anchor; min Y), `surface_depth_multiplier` (−20..20), `add_stone_depth` (same adjustments as `water`).

## Application Order

During surface application the game: (1) checks `eroded_badlands` (Y = WORLD_SURFACE_WG + 1 with `legacy_random_source`, else fixed Y=0) and places terracotta pillars; (2) applies the noise settings' surface rule; (3) checks `frozen_ocean`/`deep_frozen_ocean` (same Y rule) and places icebergs. Rules load once at server startup (`/reload` doesn't reload them — restart).

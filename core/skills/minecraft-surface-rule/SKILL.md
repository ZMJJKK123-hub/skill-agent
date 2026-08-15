---

name: minecraft-surface-rule
description: "Surface (material) rule format — rule types, conditions, application order."
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

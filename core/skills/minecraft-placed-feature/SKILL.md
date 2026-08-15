---
name: minecraft-placed-feature
description: Placed feature format — placement mechanics and all placement modifiers.
whenToUse: Use when authoring placed feature JSON files in data/worldgen/placed_feature/.
---

# Placed Feature

Placed features decide where configured features generate. Java Edition only.

## Definition Format

Registry `PLACED_FEATURE`, data pack path `worldgen/placed_feature` (files in `data/<namespace>/worldgen/placed_feature/`; tags in `tags/worldgen/placed_feature/`).

```json
{
  "feature": "<configured feature ID or inline>",
  "placement": [ { "type": "...", ... }, ... ]
}
```

Placement modifiers run **in order** — swapping them changes results. Definitions load once at server startup (restart required).

## Placement Mechanics

A feature gets an initial coordinate (the chunk's NW-lower corner during decoration; the calling coordinate when invoked by another feature/structure pool). Modifiers take input coordinates and produce output coordinates (each output = one placement attempt): they may move the coordinate, repeat it (more attempts), emit several distinct coordinates, or return nothing (cancel). Each modifier receives the previous one's outputs.

During decoration, features may generate across the 3×3 chunk area around the generating chunk; cross-chunk interference plus chunk loading order (player path) makes final placement order-dependent.

## Placement Modifiers

- `biome` — pass if the input coordinate's biome can host this feature (its configured feature's biomes); else nothing. **Placed features using this modifier cannot be called by other features** (fatal error/disconnect during worldgen).
- `block_predicate_filter` — `predicate` (block predicate); pass if the block at the input passes.
- `count` — `count` (int provider, 0–4096): repeat the same coordinate that many times.
- `count_on_every_layer` — `count` (int provider, 0–256): within the (0,0)–(16,16) horizontal range, find each non-bedrock layer separated by air/water/lava and return that many coordinates one block above those blocks.
- `environment_scan` — scan up/down from the input until the target is found: `direction_of_search` (`up`/`down`), `max_steps` (0–32), `target_condition` (block predicate for the result position), `allowed_search_condition` (each checked position must pass, else return nothing).
- `fixed_placement` — `positions` (list of `[x,y,z]`): all output coordinates.
- `height_range` — replace the Y with a height provider: `height`.
- `heightmap` — set Y to the heightmap + 1: `heightmap` = `MOTION_BLOCKING`, `MOTION_BLOCKING_NO_LEAVES`, `OCEAN_FLOOR`, `OCEAN_FLOOR_WG`, `WORLD_SURFACE`, `WORLD_SURFACE_WG`. (Note: the wiki lists the type as `height_range` in the example — the actual type is `heightmap`.)
- `in_square` — add independent random 0–15 offsets to X and Z (equivalent to `random_offset` with y_spread 0 and xz_spread uniform 0–15); for a chunk-corner input this picks a random position in the chunk.
- `noise_based_count` — return count = ceil((noise(x/factor, z/factor) + offset) × ratio) copies (empty when ≤ 0): `noise_factor`, `noise_offset` (default 0), `noise_to_count_ratio`.
- `noise_threshold_count` — noise(x/200, z/200) vs `noise_level`: `below_noise` / `above_noise` counts (negative → 0).
- `random_offset` — `xz_spread` and `y_spread` (int providers, −16..16; X and Z use different random sources).
- `rarity_filter` — pass with probability 1/`chance` (>0).
- `surface_relative_threshold_filter` — pass if Y ∈ [surface + `min_inclusive`, surface + `max_inclusive`] (heightmap; defaults −2147483648/2147483647).
- `surface_water_depth_filter` — pass if (WORLD_SURFACE − OCEAN_FLOOR) ≤ `max_water_depth` (fluid thickness above the highest solid block).

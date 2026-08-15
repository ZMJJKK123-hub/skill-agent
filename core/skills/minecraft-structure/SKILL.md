---

name: minecraft-structure
description: "Structure (feature) definition format — fields and structure types."
whenToUse: "Use when authoring structure JSON files in data/worldgen/structure/."

---

# Structure Definition

Structure definition files are the data-driven definitions of **structure features** (the structures controlled by the "Generate structures" world option). Java Edition only.

## Definition Format

Registry `STRUCTURE`, data pack path `worldgen/structure` (files in `data/<namespace>/worldgen/structure/`; tags in `tags/worldgen/structure/`).

Common fields:

- `biomes` (required) — biomes where the structure can generate (ID / list / tag).
- `spawn_overrides` (required) — overrides mob spawning in the structure's biomes: per spawn category: `bounding_box` (`piece` — the pieces' regions, or `full` — the whole structure region) and `spawns` (list of `{type` (entity ID; "other" category spawns pigs only), `weight`, `minCount` (>0), `maxCount` (>0)`; empty list = no spawns of that category).
- `step` (required) — the decoration stage the structure generates in (structure pieces generate before features within the same stage): `raw_generation`, `lakes`, `local_modifications`, `underground_structures`, `surface_structures`, `strongholds`, `underground_ores`, `underground_decoration`, `fluid_springs`, `vegetal_decoration`, `top_layer_modification`.
- `terrain_adaptation` (default `none`) — `none`; `beard_thin` (add terrain under, remove inside; pillager outposts, villages, abandoned camps); `beard_box` (stronger beard_thin; ancient cities); `bury` (bury in terrain; strongholds, trail ruins); `encapsulate` (stronger bury; trial chambers).
- `type` (required) — the structure type.

## Structure Types

- `jigsaw` — structure templates assembled via jigsaw blocks:
  - `start_pool` (required) — starting template pool.
  - `start_jigsaw_name` — name of the jigsaw block connecting the start template (missing → generation fails).
  - `start_height` (required) — height provider; `project_start_to_heightmap` — a heightmap (`WORLD_SURFACE_WG`, `WORLD_SURFACE`, `OCEAN_FLOOR_WG`, `OCEAN_FLOOR`, `MOTION_BLOCKING`, `MOTION_BLOCKING_NO_LEAVES`) to project onto, offset by `start_height`.
  - `use_expansion_hack` (required) — allow secondary pieces to exceed the base piece's Y size.
  - `size` (required, 1–20) — generation depth.
  - `max_distance_from_center` — max 3D Chebyshev distance from the start (int = horizontal only, 1–128; with terrain_adaptation 1–116; `horizontal` also 1–4096, default 4096).
  - `pool_aliases` — template pool mappings: `direct` (`alias` → `target`), `random` (`alias` + weighted `targets`), `random_group` (weighted groups of nested mappings).
  - `dimension_padding` (≥0, default 0; `bottom`/`top` or int) — vertical padding to keep structures out of bedrock.
  - `liquid_settings` (default `apply_waterlogging`) — `apply_waterlogging` (waterlog waterloggable blocks) or `ignore_waterlogging` (replace liquids directly).
  - Empty start pool also fails generation. Pieces connect jigsaw-to-jigsaw ("face to face"); jigsaw blocks become their `final_state` during worldgen. Inward-pointing jigsaws forbid the secondary piece exceeding the base piece; outward-pointing ones forbid overlap or exceeding the vertical padding. Generation stops past the depth/max distance. Selection: highest selection priority first; placement: highest placement priority first; fall back to lower priorities; stop when none connect.
- `mineshaft` — hardcoded mineshaft: `mineshaft_type` = `normal` (oak) or `mesa` (dark oak). Pieces never generate in `#mineshaft_blocking` biomes or liquid areas.
- `nether_fossil` — Nether fossils from templates: `height` (required height provider). Placement scans the chunk, placing on soul-sand-like or full-top-surface blocks above sea level touching air; 50% chance to place a desiccated ghast at the bottom layer.
- `ocean_ruin` — ocean ruins: `biome_temp` (`cold`/`warm`), `large_probability` (0–1), `cluster_probability` (0–1 — a cluster instead of a single ruin).
- `ruined_portal` — ruined portals: `setups` (non-empty, weighted list of `{weight, placement (see below), air_pocket_probability (0–1), mossiness (0–1, `block_age` processor param), overgrown (jungle leaves), vines, can_be_cold (lava → netherrack when cold instead of 20% magma blocks), replace_with_blackstone (`blackstone_replace` processor)}`). Placement methods define min/max Y (random between, or the min if max < min), using h0 = highest non-air block at the point, h1 = the template's height (see the wiki for per-method formulas).
- `shipwreck` — shipwrecks: `is_beached` — true: on the highest non-air block; false: on the highest motion-blocking block.

## Behavior

Structure definitions load once at server startup (`/reload` doesn't reload them — restart). Structures generate via structure sets in "Generate structures" worlds or directly via `/place structure <id>`.

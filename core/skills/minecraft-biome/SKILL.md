---

name: minecraft-biome
description: "Minecraft Biome 生物群系定义：BIOME 注册表、data/<namespace>/worldgen/biome/ 数据包路径、JSON 格式（has_precipitation/temperature/temperature_modifier/downfall/attributes）、Effects 环境效果（water_color/dry_foliage_color/foliage_color/grass_color/grass_color_modifier）、Carvers 雕刻器（tag/ID/inline/list）、Features 生成特性（11个装饰阶段 RAW_GENERATION/LAKES/LOCAL_MODIFICATIONS/UNDERGROUND_STRUCTURES/SURFACE_STRUCTURES/STRONGHOLDS/UNDERGROUND_ORES/UNDERGROUND_DECORATION/FLUID_SPRINGS/VEGETAL_DECORATION/TOP_LAYER_MODIFICATION、Feature order cycle found 排序规则）、creature_spawn_probability 生物生成概率、Spawners 生物生成条目（type/weight/minCount/maxCount）、spawn_costs 生成成本（energyBudget/charge）、Legacy Effects 旧版效果（fog_color/sky_color/water_fog_color/particle/ambient_sound/additions_sound/mood_sound/music/music_volume）、biome.<ns>.<path> 本地化键、plains 生物群系必需。"
whenToUse: "Use when authoring biome JSON files in data/worldgen/biome/."

---

# Biome Definition

Biome definition files define biomes data-driven. Java Edition only.

## Definition Format

Registry `BIOME`, data pack path `worldgen/biome` (files in `data/<namespace>/worldgen/biome/`; tags in `tags/worldgen/biome/`).

- `has_precipitation` (required) — whether the biome has precipitation.
- `temperature` (required) — temperature value.
- `temperature_modifier` (default `none`) — `none` or `frozen` (sets some areas to 0.2 before height adjustment).
- `downfall` (required) — affects plant colors (with temperature) but not actual precipitation.
- `attributes` — environment attribute map (position-dependent attributes only; duplicates → last value wins). See the environment-attributes skill.
- `effects` (required) — environmental effects (see below).
- `carvers` (required, may be empty) — carvers usable in the biome (tag/ID/inline/list).
- `features` (required, may be empty) — placed features; must have exactly 11 elements (one per decoration stage); each element is a feature tag/ID/list/inline.
- `creature_spawn_probability` (0–0.9999999, default 0.1) — initial animal spawn probability during worldgen.
- `spawners` (required, may be empty) — mob spawn entries per spawn category: `{type (entity ID; "other"-category entities spawn pigs only), weight, minCount (>0), maxCount (>0)}`.
- `spawn_costs` (required, may be empty) — spawn "potential" per entity: `energyBudget` (max energy a spawn can consume; smaller → fewer spawns) and `charge` (point-charge model; larger → fewer spawns).

### Effects

- `water_color` (required) — RGB color.
- `dry_foliage_color` — dead-bush coloring.
- `foliage_color` — leaves/vines coloring.
- `grass_color` — grass block, grass, ferns, bushes, sugar cane, flower stems coloring.
- `grass_color_modifier` (default `none`) — `none`, `dark_forest` ((color & FEFEFE + 2634762) averaged), or `swamp` (noise-picked from 5011004/6975545).
- Unspecified plant colors use temperature/downfall color maps. Colors are affected by the "biome transition distance" video option.

## Behavior

Biome definitions load once at server startup (`/reload` doesn't reload them — restart). In single-biome world presets every registered biome is selectable; its display name defaults to the namespace ID but can be set with the `biome.<ns>.<path>` localization key. Without a `plains` element in the `BIOME` registry the game refuses to load the world.

## Feature Generation

The `features` list maps to the 11 decoration stages used by structure generation too:

1. `RAW_GENERATION` (End floating islands) 2. `LAKES` (lava lakes) 3. `LOCAL_MODIFICATIONS` (geodes, icebergs, basalt pillars) 4. `UNDERGROUND_STRUCTURES` (dungeons, fossils) 5. `SURFACE_STRUCTURES` (desert wells, blue ice, ice spikes) 6. `STRONGHOLDS` (unused) 7. `UNDERGROUND_ORES` (ore blobs) 8. `UNDERGROUND_DECORATION` (non-ore clusters, Nether ores) 9. `FLUID_SPRINGS` 10. `VEGETAL_DECORATION` (plants) 11. `TOP_LAYER_MODIFICATION` (frozen top layer).

Features beyond the 11 stages still place. **Critical ordering rule**: for all biomes in one dimension, each stage's features must have the SAME relative order (lists order by list order; tags by their `values` order; inline/IDs have no order). Violations crash the game at decoration with `Feature order cycle found` — the game does not pre-check, so verify manually.

Bone meal on grass in a biome can spawn any feature in the `#can_spawn_from_bone_meal` placed-feature tag whose placement succeeds there (vanilla uses this for biome-specific flowers).

## Legacy Effects

Pre-1.19 effects (now replaced by environment attributes): `fog_color`, `sky_color`, `water_fog_color`, `particle` (options + probability), `ambient_sound`, `additions_sound`, `mood_sound` (tick_delay, block_search_extent, offset), `music` (weighted list of `{data (sound, min_delay, max_delay, replace_current_music), weight}`; empty = no music), `music_volume` (default 1).

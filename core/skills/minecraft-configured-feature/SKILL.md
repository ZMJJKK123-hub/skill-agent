---
name: minecraft-configured-feature
description: Configured feature format — JSON in data packs; all feature types and configs.
whenToUse: Use when authoring worldgen configured features, features, or related tags in data packs.
---

# Configured Feature

Configured features (often just "features") are the basic units of world generation. Java Edition only. Note: this page was flagged on the wiki for needing updates for 26.2/26.3 registry renames.

## Definition Format

- Before Java 26.3: registry `CONFIGURED_FEATURE`, data pack path `worldgen/configured_feature` (files in `data/<namespace>/worldgen/configured_feature`; tags in `data/<namespace>/tags/worldgen/configured_feature`).
- From Java 26.3: registry `FEATURE`, data pack path `worldgen/feature` (files in `data/<namespace>/worldgen/feature`; tags in `data/<namespace>/tags/worldgen/feature`).

File format:

```json
{
  "type": "<namespace id>",
  "config": { ... }
}
```

- `type` (required) — the feature type (namespace ID).
- `config` (required) — per-type configuration; some types use an empty object `{}`.

## Behavior

Configured features are loaded once at server startup; `/reload` does not reload them — the server must be restarted. A configured feature pairs a feature type with config data; some types are fully defined by themselves (`config: {}`), others need detailed config.

## Feature Types

Each entry: purpose + config fields (see the Minecraft Wiki "Configured feature" page or `worldgen/feature/` JSON files in the source for full details; shared field types: block state, block state provider, int/float provider, rule test, block test, and placed feature references by ID/tag/inline).

- `bamboo` — bamboo; needs `#bamboo_plantable_on` at the position. Config: `probability` (0–1, chance of podzol under bamboo).
- `basalt_columns` — basalt column forest. Config: `height` (int provider, 1–10), `reach` (int provider, 0–3).
- `basalt_pillar` — a basalt pillar downward from the position (position must be air with a block above). Config: `{}`.
- `block_blob` — a random 3×3×3 block blob; position must be 3+ blocks above the world bottom. Config: `state` (block state), `can_place_on` (block test, retried one block down until 3 above bottom).
- `block_column` — a column of layered blocks. Config: `allowed_placement` (block test), `direction` (`up`/`down`/`north`/`south`/`west`/`east`), `layers` (list of `{height: int provider ≥0, provider: block state provider, prioritize_tip: bool}`).
- `block_pile` — a pile of blocks; position must be 5+ blocks above world bottom. Config: `state_provider`.
- `blue_ice` — a blue ice pile; position ≤ sea level −1, water at position or below, floating ice within 5 directions. Config: `{}`.
- `bonus_chest` — a bonus chest. Config: `{}`.
- `chorus_plant` — chorus plant; needs End stone below. Config: `{}`.
- `coral_claw` / `coral_mushroom` / `coral_tree` — claw/mushroom/tree coral reef; position must be in water. Config: `{}`.
- `delta_feature` — a delta (e.g. lava deltas); position not the delta body block, air above, other five directions not air. Config: `contents` (body block state), `rim` (edge block state), `rim_size` (int provider 0–16), `size` (int provider 0–16).
- `desert_well` — a desert well; needs sand below. Config: `{}`.
- `disk` — a disk (e.g. clay/gravel). Config: `half_height` (0–4), `radius` (int provider 0–8), `rules` (list of `{if_true: block test, then: block state provider}`), `state_provider`, `target` (block test).
- `dripstone_cluster` — dripstone clusters. Config: `floor_to_ceiling_search_range` (1–512), `height` (int provider 1–128), `radius` (int provider 1–128), `max_stalagmite_stalactite_height_diff` (1–64), `height_deviation` (1–64), `dripstone_block_layer_thickness` (int provider 0–128), `density` (float provider 0–2), `wetness` (float provider 0–2), `chance_of_dripstone_column_at_max_distance_from_center` (0–1), `max_distance_from_edge_affecting_chance_of_dripstone_column` (1–64), `max_distance_from_center_affecting_height_bias` (1–64).
- `end_gateway` — an end gateway. Config: `exact` (precise teleport), `exit` (`[x, y, z]` destination).
- `end_island` — an End island. Config: `{}`.
- `end_platform` — the obsidian platform. Config: `{}`.
- `end_spike` — obsidian spikes. Config: `crystal_invulnerable` (default false), `spikes` (list of `{centerX, centerZ, radius, height (defaults 0), guarded (iron bars), crystal_beam_target ([x,y,z])}`).
- `fallen_tree` — a fallen tree. Config: `trunk_provider`, `log_length` (int provider 0–16), `stump_decorators`, `log_decorators` (tree decorator lists).
- `fill_layer` — fills 16×1×16. Config: `height` (0–4032), `state`.
- `fossil` — fossil from structure templates. Config: `fossil_structures` (template list, same length as `overlay_structures`), `overlay_structures`, `fossil_processors` (processor list ID or inline), `overlay_processors`, `max_empty_corners_allowed` (0–7).
- `freeze_top_layer` — places snow/ice and sets snowy grass at the `MOTION_BLOCKING` heightmap per temperature. Config: `{}`.
- `geode` — a geode. Config: `blocks` (block set: `filling_provider`, `inner_layer_provider`, `alternate_inner_layer_provider`, `middle_layer_provider`, `outer_layer_provider`), `inner_placements` (non-empty block state list), `cannot_replace`, `invalid_blocks` (air hardcoded invalid), `layers` (thickness: `filling` 1.7, `inner_layer` 2.2, `middle_layer` 3.2, `outer_layer` 4.2, 0.01–50), `crack` (`generate_crack_chance` 1.0, `base_crack_size` 2.0, `crack_point_offset` 2), `use_potential_placements_chance` (0.35), `use_alternate_layer0_chance` (0.0), `placements_require_layer0_alternate` (true), `outer_wall_distance` (int provider 1–20), plus distribution params (distribution type per placed feature).
- `glowstone_blob` — a glowstone blob; position must be netherrack, basalt, or blackstone. Config: `{}`.
- `huge_brown_mushroom` — a huge brown mushroom; position in `#dirt`/`#mushroom_grow_block`, clearance above. Config: `cap_provider`, `stem_provider`, `foliage_radius` (default 2), `can_place_on`.
- `huge_fungus` — a huge Nether fungus. Config: `valid_base_block`, `stem_state`, `hat_state`, `decor_state`, `planted` (default false — when false, highest Y must stay under the dimension's total terrain height and replaced blocks drop nothing), `replaceable_blocks`.
- `huge_red_mushroom` — a huge red mushroom; position in `#dirt`/`#mushroom_grow_block`. Config: same as huge_brown_mushroom.
- `iceberg` — an iceberg. Config: `state`.
- `kelp` — kelp; position must be water. Config: `{}`.
- `lake` — a lake. Config: `fluid`, `barrier` (block state providers), `can_place_feature`, `can_replace_with_air_or_fluid`, `can_replace_with_barrier` (block tests).
- `large_dripstone` — large dripstone columns. Config: `replaceable_blocks`, `floor_to_ceiling_search_range` (default 30), `column_radius` (int provider min/max, 1–60), `height_scale` (float provider 0–20), `max_column_radius_to_cave_height_ratio` (0–1), `stalactite_bluntness` / `stalagmite_bluntness` (float providers 0.1–10), `wind_speed` (float provider 0–2), `min_radius_for_wind` (0–100), `min_bluntness_for_wind` (0–5).
- `monster_room` — a dungeon; needs solid 9×9 areas below/above and 1–4 non-solid blocks on the 7×7/7×9/9×9 ring. Config: `{}`.
- `multiface_growth` — glow lichen / sculk vein growth. Config: `block` (default `glow_lichen`; only `glow_lichen` or `sculk_vein`), `search_range` (default 10), `can_place_on_floor`/`can_place_on_ceiling`/`can_place_on_wall` (default false), `chance_of_spreading` (0–0.5), `can_be_placed_on` (block ID/tag/list).
- `nether_forest_vegetation` — a vegetation pile; position in `#nylium`. Config: `state_provider`, `spread_width` (>0, width = 2×−1), `spread_height` (>0).
- `netherrack_replace_blobs` — replaces target blocks in a radius (moves down on failure). Config: `target` (block state, `Properties` ignored), `state`, `radius` (int provider 0–12).
- `no_op` — does nothing; used to override existing features. Config: `{}`.
- `ore` — a spherical ore blob. Config: `targets` (list of `{target: rule test, state}`), `size` (0–64), `discard_chance_on_air_exposure` (0–1).
- `random_boolean_selector` — places one of two features by random boolean. Config: `feature_false`, `feature_true` (placed features).
- `random_selector` — tries a weighted list in order; first success wins. Config: `features` (list of `{chance: 0–1, feature}`), `default` (placed feature).
- `replace_single_block` — replaces one block. Config: `targets` (list of `{target: rule test, state}`).
- `root_system` — a surface feature with underground roots. Config: `feature` (surface placed feature), `allowed_tree_position` (block test), `root_state_provider`, `root_replaceable`, `hanging_root_state_provider`, `required_vertical_space_for_tree` (1–64), `allowed_vertical_water_for_tree` (1–64), `root_radius` (1–64), `root_column_max_height` (1–256), `root_placement_attempts` (1–4096), `hanging_root_radius` (1–64), `hanging_root_placement_attempts` (1–256).
- `scattered_ore` — a scattered ore blob (like `ore`). Config: `targets`, `size` (0–64), `discard_chance_on_air_exposure`.
- `sculk_patch` — a sculk patch. Config: `charge_count` (1–32), `amount_per_charge` (1–500), `spread_attempts` (1–64), `growth_rounds` (1–8), `spread_rounds` (1–8), `extra_rare_growths` (int provider 1–64, sculk shriekers), `catalyst_chance` (0–1).
- `seagrass` — seagrass; position must be water. Config: `probability` (0–1, tall seagrass chance).
- `sea_pickle` — sea pickles. Config: `count` (int provider 0–256).
- `sequence` — places features in order; stops at the first failure. Config: `features` (placed feature ID/tag/list/inline).
- `simple_block` — places a single block. Config: `to_place` (block state provider), `schedule_tick` (default false — schedule 1 random tick).
- `simple_random_selector` — random selection from a list. Config: `features` (same formats as sequence).
- `speleothem` — pointed dripstone growth. Config: `base_block`, `pointed_block`, `replaceable_blocks`, `chance_of_taller_generation` (0.2), `chance_of_directional_spread` (0.7), `chance_of_spread_radius2` (0.5), `chance_of_spread_radius3` (0.5).
- `speleothem_cluster` — dripstone-like clusters (same fields as `dripstone_cluster`, named `speleothem_block_layer_thickness`, `chance_of_speleothem_at_max_distance_from_center`, `max_distance_from_edge_affecting_chance_of_speleothem`).
- `spike` — a spike. Config: `state`, `can_place_on` (block test), `can_replace` (block test; air always replaceable).
- `spring_feature` — a fluid spring. Config: `state` (`Name` fluid ID + `Properties`), `requires_block_below` (default true), `rock_count` (default 4), `hole_count` (default 4), `valid_blocks` (block ID/tag/list).
- `template` — a random structure template. Config: `templates` (list of `{id: template ID, rotations: [none|clockwise_90|180|counterclockwise_90]}`; rotations default random).
- `tree` — a tree. Config: `ignore_vines` (default false), `trunk_provider`, `foliage_provider`, `below_trunk_provider` (defaults to a rule-based dirt provider respecting `#cannot_replace_below_tree_trunk`; absent = no replacement), `trunk_placer`, `foliage_placer`, `root_placer` (absent = no roots), `minimum_size` (see below). See the tree placer/foliage placer/root placer/decorator details below.
- `twisting_vines` — twisting vines; position must be netherrack, nether wart block, or crimson nylium. Config: `spread_width` (>0), `spread_height` (>0), `max_height` (>0; height in [1, max_height×2]).
- `underwater_magma` — underwater magma blocks. Config: `floor_search_range` (0–512), `placement_radius_around_floor` (0–64), `placement_probability_per_valid_position` (0–1).
- `vegetation_patch` — a vegetation patch. Config: `replaceable`, `ground_state` (block state provider), `vegetation_feature` (placed feature), `surface` (`floor`/`ceiling`), `xz_radius` (int provider), `depth` (0–128), `vertical_range` (int provider 0–256), `extra_bottom_block_chance` (0–1), `extra_edge_column_chance` (0–1), `vegetation_chance` (0–1).
- `vines` — vines. Config: `{}`.
- `void_start_platform` — the void platform. Config: `{}`.
- `waterlogged_vegetation_patch` — like `vegetation_patch`; also waterlogs generated blocks (`ground_state` replaced by water on the top layer away from edges). Config: same fields as vegetation_patch.
- `weeping_vines` — weeping vines; position must be netherrack or nether wart block. Config: `{}`.

## Tree Sub-formats

### Trunk Placers

Common: `base_height` (0–32), `height_rand_a` (0–24), `height_rand_b` (0–24) — trunk base height = base + randA + randB (max 80). `type` one of: `straight_trunk_placer`, `giant_trunk_placer` (2×2), `forking_trunk_placer`, `fancy_trunk_placer`, `mega_jungle_trunk_placer`, `dark_oak_trunk_placer`, `bending_trunk_placer` (extra: `bend_length` int provider 0–24, `min_height_for_leaves` >0), `upwards_branching_trunk_placer` (extra: `extra_branch_steps` >0, `extra_branch_length` ≥0, `place_branch_per_log_probability` 0–1, `can_grow_through`).

### Foliage Placers

Common: `radius` (int provider 0–16), `offset` (int provider 0–16 — top of foliage vs top of trunk). `type` one of: `acacia_foliage_placer`, `dark_oak_foliage_placer`, `blob_foliage_placer` (oak/birch; extra `height` 0–16), `bush_foliage_placer` (pyramid; extra `height`), `fancy_foliage_placer` (ball; extra `height`), `jungle_foliage_placer` (extra `height`), `spruce_foliage_placer` (extra `trunk_height` int provider 0–24), `pine_foliage_placer` (sparse spruce; extra `height` int provider 0–24), `mega_pine_foliage_placer` (extra `crown_height` int provider 0–24), `random_spread_foliage_placer` (extra `foliage_height` int provider 0–512, `leaf_placement_attempts` 0–256).

### Root Placers

`trunk_offset_y` (int provider), `root_provider`, optional `above_root_placement` (`above_root_provider`, `above_root_placement_chance` 0–1). `type` currently only `mangrove_root_placer` with `mangrove_root_placement`: `max_root_width` (0–12), `max_root_length` (0–64), `random_skew_chance` (0–1), `can_grow_through`, `muddy_roots_in` (replaced blocks become muddy roots), `muddy_roots_provider`.

### Tree Decorators

`type` one of: `trunk_vine`, `leave_vine` (extra `probability`), `cocoa` (extra `probability`), `beehive` (extra `probability`), `alter_ground` (extra `provider`), `attached_to_leaves` (extra `block_provider`, `probability`, `exclusion_radius_xz`, `exclusion_radius_y`, `required_empty_blocks` 0–16, `directions` non-empty), `attached_to_logs` (extra `block_provider`, `probability`, `directions`), `creaking_heart` (extra `probability`), `pale_moss` (extra `probability`, `leaves_probability`, `ground_probability` — places `pale_moss_patch`), `place_on_ground` (extra `tries` default 128, `radius` default 2, `height` default 1, block provider).

### Minimum Size

- `two_layers_feature_size`: `limit` (default 1), `lower_size` (default 0), `upper_size` (default 1) — minimum space (2u+1)² above/below `limit`.
- `three_layers_feature_size`: `limit` (default 1), `upper_limit` (default 1), `lower_size` (default 0), `middle_size` (default 1), `upper_size` (default 1) — three tiers; with optional `min_clipped_height` (0–80) allowing trees that can't reach full height to still generate if they exceed that height.

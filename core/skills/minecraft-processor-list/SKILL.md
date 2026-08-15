---
name: minecraft-processor-list
description: Processor list format — all processor types and behavior.
whenToUse: Use when authoring structure processor lists in data/worldgen/processor_list/.
---

# Processor List

Processor lists replace blocks placed from structure templates during world generation per rules. Java Edition only.

## Definition Format

Registry `PROCESSOR_LIST`, data pack path `worldgen/processor_list` (files in `data/<namespace>/worldgen/processor_list/`; tags in `tags/worldgen/processor_list/`). A file is either a root array of processors or an object with a `processors` list. Each processor:

```json
{ "processor_type": "<namespace id>", ... }
```

## Processor Types

- `blackstone_replace` — replaces stone-type blocks with blackstone variants and iron bars with chains.
- `block_age` — ages blocks: `mossiness` (0–1 clamped).
- `block_ignore` — `blocks` (list of block states; states not checked): removes those blocks; their positions keep the pre-existing blocks (not overwritten).
- `block_rot` — randomly removes blocks: `integrity` (0–1; removal chance), `rottable_blocks` (ID/array/tag; absent = all blocks).
- `capped` — caps the number of processed blocks: `delegate` (recursive processor), `limit` (int provider; if the structure has fewer blocks, all are processed, else a random subset).
- `gravity` — shifts the structure vertically per terrain: `heightmap` (default `WORLD_SURFACE_WG`; one of the six standard heightmaps), `offset` (default 0).
- `jigsaw_replacement` — replaces jigsaw blocks and removes structure void; auto-applied for worldgen jigsaw structures (no need to declare).
- `lava_submerged_block` — when a structure block replaces lava, blocks with incomplete collision boxes don't replace the lava.
- `nop` — does nothing.
- `protected_blocks` — `value` (ID/list/tag): these blocks can't be overwritten by the structure.
- `rule` — custom rules, applied in list order:
  - `position_predicate` (default always true) — test on the distance from the structure start: `predicate_type` = `always_true`, `linear_pos` (3D Manhattan distance; `min_chance`/`max_chance` with linear interpolation between `min_dist`/`max_dist`; probabilities clamped 0–1), or `axis_aligned_linear_pos` (same but on one `axis` = x/y/z, default y, distances positive).
  - `input_predicate` (required) — rule test applied to the placed block (see the rule-test skill).
  - `location_predicate` (required) — rule test applied to the block at the position before generation.
  - `output_state` (required) — the block to place.
  - `block_entity_modifier` (optional) — modifies the block entity on placement: `passthrough` (default, keep fields), `clear` (remove fields), `append_static` (`data` NBT added), `append_loot` (`loot_table` added, with a seed based on the block position).

## Behavior

Processors run in list order per template block; they're also called block processors / structure post-processors. For template pool jigsaw elements, processors run BEFORE terrain adaptation — the actual placement position may differ from the processed position. Definitions load once at server startup (restart required).

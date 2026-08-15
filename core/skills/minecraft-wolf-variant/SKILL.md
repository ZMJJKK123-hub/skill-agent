---
name: minecraft-wolf-variant
description: Wolf variant definition JSON: WOLF_VARIANT registry, textures, spawn conditions.
whenToUse: Use when writing datapack wolf_variant definitions or custom wolf variants.
---

# Wolf Variants

This content applies only to Java Edition.

Wolf variant definition files define wolf variants and their spawn rules.

## Definition format

Wolf variants use the `WOLF_VARIANT` registry; the datapack path is `wolf_variant` (definitions in `data/<namespace>/wolf_variant`, tags in `data/<namespace>/tags/wolf_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `assets` (compound, required): textures per wolf state, each `(namespace ID)` resolved to `assets/<namespace>/textures/<path>.png`:
    - `angry` (string, required), `tame` (string, required), `wild` (string, required).
  - `baby_assets` (compound, required): same format as `assets`, for baby wolves.
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): `type` (string, required): `biome` (`biomes` string/list: tag `#`, ID, or list), `moon_brightness` (`range` min-max bounds; full moon 1, new moon 0), or `structure` (`structures` string/list: tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties resolved randomly.

## Definition behavior

Wolf variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `WOLF_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a wolf, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

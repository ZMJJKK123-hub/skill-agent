---

name: minecraft-pig-variant
description: "Pig variant definition JSON: PIG_VARIANT registry, textures, model, spawn conditions."
whenToUse: "Use when writing datapack pig_variant definitions or custom pig variants."

---

# Pig Variants

This content applies only to Java Edition.

Pig variant definition files define pig variants and their spawn rules.

## Definition format

Pig variants use the `PIG_VARIANT` registry; the datapack path is `pig_variant` (definitions in `data/<namespace>/pig_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) pig texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby pig texture; resolved the same way.
  - `model` (string, default `normal`): `normal` (temperate/tropical pigs) or `cold` (cold pigs).
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): conditions for the selector; absent = always.
        - `type` (string, required): `biome` (checks `biomes` — tag `#`, ID, or list), `moon_brightness` (checks `range` min-max bounds; full moon 1, new moon 0), or `structure` (checks `structures` — tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties are resolved randomly.

## Definition behavior

Pig variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `PIG_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a pig, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

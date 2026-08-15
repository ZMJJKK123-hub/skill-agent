---

name: minecraft-chicken-variant
description: "Chicken variant definition JSON: CHICKEN_VARIANT registry, textures, model, spawn conditions."
whenToUse: "Use when writing datapack chicken_variant definitions or custom chicken variants."

---

# Chicken Variants

This content applies only to Java Edition.

Chicken variant definition files define chicken variants and their spawn rules.

## Definition format

Chicken variants use the `CHICKEN_VARIANT` registry; the datapack path is `chicken_variant` (definitions in `data/<namespace>/chicken_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) chicken texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby chicken texture.
  - `model` (string, default `normal`): `normal` (temperate/tropical chickens) or `cold` (cold chickens).
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): `type` (string, required): `biome` (`biomes` string/list: tag `#`, ID, or list), `moon_brightness` (`range` min-max bounds; full moon 1, new moon 0), or `structure` (`structures` string/list: tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties resolved randomly.

## Definition behavior

Chicken variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CHICKEN_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a chicken, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

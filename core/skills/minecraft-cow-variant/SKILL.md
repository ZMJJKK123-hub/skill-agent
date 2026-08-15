---

name: minecraft-cow-variant
description: "Cow variant definition JSON: COW_VARIANT registry, textures, model, spawn conditions."
whenToUse: "Use when writing datapack cow_variant definitions or custom cow variants."

---

# Cow Variants

This content applies only to Java Edition.

Cow variant definition files define cow variants and their spawn rules.

## Definition format

Cow variants use the `COW_VARIANT` registry; the datapack path is `cow_variant` (definitions in `data/<namespace>/cow_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) cow texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `baby_asset_id` (string, required): (namespace ID) baby cow texture.
  - `model` (string, default `normal`): `normal`, `cold`, or `warm` (temperate/cold/tropical cows).
  - `spawn_conditions` (list, required): variant spawn selectors.
    - One selector (compound):
      - `condition` (compound): `type` (string, required): `biome` (`biomes` string/list: tag `#`, ID, or list), `moon_brightness` (`range` min-max bounds; full moon 1, new moon 0), or `structure` (`structures` string/list: tag `#`, ID, or list).
      - `priority` (int, required): selection priority; ties resolved randomly.

## Definition behavior

Cow variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `COW_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a cow, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

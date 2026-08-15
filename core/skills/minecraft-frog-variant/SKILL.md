---

name: minecraft-frog-variant
description: "Frog variant definition JSON: FROG_VARIANT registry, texture, spawn conditions."
whenToUse: "Use when writing datapack frog_variant definitions or custom frog variants."

---

# Frog Variants

This content applies only to Java Edition.

Frog variant definition files define frog variants and their spawn rules.

## Definition format

Frog variants use the `FROG_VARIANT` registry; the datapack path is `frog_variant` (definitions in `data/<namespace>/frog_variant`, tags in `data/<namespace>/tags/frog_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) frog texture; resolved to `assets/<namespace>/textures/<path>.png`.
  - `spawn_conditions` (list, required): variant spawn selectors controlling spawn conditions and priority.
    - One selector (compound):
      - `condition` (compound): conditions under which the selector applies; absent = always.
        - `type` (string, required): selector condition type.
          - `biome`: checks the biome at the spawn point; `biomes` (string/list, required): biome tag (`#`), ID, or list.
          - `moon_brightness`: checks moon brightness; `range` (double/compound, required): min-max bounds; full moon = 1, new moon = 0.
          - `structure`: checks whether the spawn point is inside the given structure pieces; `structures` (string/list, required): structure tag (`#`), ID, or list.
      - `priority` (int, required): selection priority. The game picks the valid selectors with the highest priority across all variants; ties are resolved randomly.

## Definition behavior

Frog variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `FROG_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

When spawning a frog, the game evaluates all variant selectors and spawns the variant of a highest-priority valid selector (random among ties).

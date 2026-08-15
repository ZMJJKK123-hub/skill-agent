---
name: minecraft-cat-sound-variant
description: Cat sound variant definition JSON: CAT_SOUND_VARIANT registry, adult/baby sound events.
whenToUse: Use when writing datapack cat_sound_variant definitions or custom cat sounds.
---

# Cat Sound Variants

This content applies only to Java Edition.

Cat sound variant definition files are the data-driven definitions of cat sound variants in datapacks.

## Definition format

Cat sound variants use the `CAT_SOUND_VARIANT` registry; the datapack path is `cat_sound_variant` (definitions in `data/<namespace>/cat_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult cats. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `beg_for_food_sound` (begging), `death_sound`, `eat_sound`, `hiss_sound` (hissing at phantoms), `hurt_sound`, `purr_sound` (purring), `purreow_sound` (tamed idle), `stray_ambient_sound` (untamed idle).
  - `baby_sounds` (compound, required): same format, for baby cats.

## Definition behavior

Cat sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CAT_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Cat sound variants are independent of cat variants; each spawned cat randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `eat_sound`. Random sounds: `hiss_sound` (hissing at phantoms), `beg_for_food_sound`, `purr_sound`, `purreow_sound` (idle when tamed), `stray_ambient_sound` (untamed), `ambient_sound` (idle, alternating randomly with `purreow_sound`).

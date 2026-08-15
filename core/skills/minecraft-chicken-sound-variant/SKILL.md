---

name: minecraft-chicken-sound-variant
description: "Chicken sound variant definition JSON: CHICKEN_SOUND_VARIANT registry, sound events."
whenToUse: "Use when writing datapack chicken_sound_variant definitions or custom chicken sounds."

---

# Chicken Sound Variants

This content applies only to Java Edition.

Chicken sound variant definition files are the data-driven definitions of chicken sound variants in datapacks.

## Definition format

Chicken sound variants use the `CHICKEN_SOUND_VARIANT` registry; the datapack path is `chicken_sound_variant` (definitions in `data/<namespace>/chicken_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult chickens. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `death_sound`, `hurt_sound`, `step_sound`.
  - `baby_sounds` (compound, required): same format, for baby chickens.

## Definition behavior

Chicken sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `CHICKEN_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Chicken sound variants are independent of chicken variants; each spawned chicken randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `step_sound`. Random sounds: `ambient_sound` (idle).

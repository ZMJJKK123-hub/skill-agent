---
name: minecraft-cow-sound-variant
description: Cow sound variant definition JSON: COW_SOUND_VARIANT registry, sound events.
whenToUse: Use when writing datapack cow_sound_variant definitions or custom cow sounds.
---

# Cow Sound Variants

This content applies only to Java Edition.

Cow sound variant definition files are the data-driven definitions of cow sound variants in datapacks.

## Definition format

Cow sound variants use the `COW_SOUND_VARIANT` registry; the datapack path is `cow_sound_variant` (definitions in `data/<namespace>/cow_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult cows. Each is a sound event (registry name or inline):
    - `ambient_sound` (idle), `death_sound`, `hurt_sound`, `step_sound`.
  - `baby_sounds` (compound, required): same format, for baby cows.

## Definition behavior

Cow sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `COW_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Cow sound variants are independent of cow variants; each spawned cow randomly picks one registered sound variant.

Immediate sounds: `hurt_sound`, `death_sound`, `step_sound`. Random sounds: `ambient_sound` (idle).

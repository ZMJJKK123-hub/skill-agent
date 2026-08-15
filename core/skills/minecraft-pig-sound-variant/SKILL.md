---
name: minecraft-pig-sound-variant
description: Pig sound variant definition JSON: PIG_SOUND_VARIANT registry, sound events.
whenToUse: Use when writing datapack pig_sound_variant definitions or custom pig sounds.
---

# Pig Sound Variants

This content applies only to Java Edition.

Pig sound variant definition files are the data-driven definitions of pig sound variants in datapacks.

## Definition format

Pig sound variants use the `PIG_SOUND_VARIANT` registry; the datapack path is `pig_sound_variant` (definitions in `data/<namespace>/pig_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult pigs.
    - `ambient_sound` (string/compound): idle sound event (registry name or inline; same format for all below).
    - `death_sound` (string/compound): death sound event.
    - `hurt_sound` (string/compound): hurt sound event.
    - `step_sound` (string/compound): step sound event.
    - `eat_sound` (string/compound): eating sound event.
  - `baby_sounds` (compound, required): sounds used by baby pigs; same format as `adult_sounds`.

## Definition behavior

Pig sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `PIG_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Pig sound variants are independent of pig variants; each spawned pig randomly picks one registered sound variant. Immediate sounds: `hurt_sound` (hurt), `death_sound` (death), `step_sound` (walking), `eat_sound` (eating). Random sounds: `ambient_sound` (idle).

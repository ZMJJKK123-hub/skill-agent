---

name: minecraft-wolf-sound-variant
description: "Wolf sound variant definition JSON: WOLF_SOUND_VARIANT registry defining adult and baby wolf sound events including ambient_sound, death_sound, hurt_sound, step_sound, and ambient_whine for idle behavior."
whenToUse: "Use when writing datapack wolf_sound_variant definitions or custom wolf sounds."

---

# Wolf Sound Variants

This content applies only to Java Edition.

Wolf sound variant definition files are the data-driven definitions of wolf sound variants in datapacks.

## Definition format

Wolf sound variants use the `WOLF_SOUND_VARIANT` registry; the datapack path is `wolf_sound_variant` (definitions in `data/<namespace>/wolf_sound_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `adult_sounds` (compound, required): sounds used by adult wolves.
    - `ambient_sound` (string/compound): idle sound event (registry name or inline; same format for all below).
    - `death_sound` (string/compound): death sound event.
    - `growl_sound` (string/compound): growling sound event.
    - `hurt_sound` (string/compound): hurt sound event.
    - `pant_sound` (string/compound): panting sound event.
    - `whine_sound` (string/compound): whining sound event.
  - `baby_sounds` (compound, required): sounds used by baby wolves; same format as `adult_sounds`.

## Definition behavior

Wolf sound variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `WOLF_SOUND_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

Wolf sound variants are independent of wolf variants; each spawned wolf randomly picks one registered sound variant.

Immediate sounds: `hurt_sound` (hurt, when wolf armor is not absorbing), `death_sound` (death). Random sounds: `growl_sound` (angry), `whine_sound` (tamed with health <20), `pant_sound` (tamed with health ≥20, or untamed), `ambient_sound` (when growl/whine conditions don't apply).

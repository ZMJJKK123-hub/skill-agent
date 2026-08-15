---
name: minecraft-goat-horn
description: Goat horn instrument definition JSON: INSTRUMENT registry, sound, range, duration.
whenToUse: Use when writing datapack instrument definitions or custom goat horn instruments.
---

# Goat Horn Instruments

This content applies only to Java Edition.

Goat horn instruments (instruments) determine the behavior when a player blows a goat horn. Definition files are their data-driven definitions in datapacks.

## Definition format

Instruments use the `INSTRUMENT` registry; the datapack path is `instrument` (definitions in `data/<namespace>/instrument`, tags in `data/<namespace>/tags/instrument`).

Definition files use JSON with the following structure:

- JSON file root object
  - `description` (string/compound/list, required): (text component) the instrument's name.
  - `sound_event` (string/compound, required): sound event played when blowing (registry name or inline definition).
  - `durability_damage` (int): (≥0) durability consumed per blow.
  - `range` (float, required): (>0) maximum distance the sound travels.
  - `use_duration` (float, required): (>0) blowing duration in seconds; affects the item cooldown.

## Definition behavior

Instrument data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

When a player blows a goat horn with the `instrument` item stack component, the game reads the instrument and plays it. The sound belongs to the `record` (jukebox/note block) category: volume = `range`/16, pitch 1, plays immediately with linear attenuation. The audible distance is the minimum of the referenced `sound_id`'s `attenuation_distance`, the instrument's `range`, and the sound event's `range`.

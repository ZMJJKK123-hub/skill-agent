---

name: minecraft-superflat-preset
description: "Flat level generator preset JSON: FLAT_LEVEL_GENERATOR_PRESET registry."
whenToUse: "Use when writing datapack flat_level_generator_preset definitions."

---

# Flat Level Generator Presets

This content applies only to Java Edition. This article covers datapack presets (for in-game presets, see superflat worlds).

Flat world presets are selectable presets on the superflat screen. Definition files are their data-driven definitions in datapacks.

## Definition format

Presets use the `FLAT_LEVEL_GENERATOR_PRESET` registry; the datapack path is `worldgen/flat_level_generator_preset` (definitions in `data/<namespace>/worldgen/flat_level_generator_preset`, tags in `data/<namespace>/tags/worldgen/flat_level_generator_preset`).

Definition files use JSON with the following structure:

- JSON file root object
  - `display` (string, required): preset icon as an item namespace ID.
  - `settings` (compound, required): the Overworld flat generator settings (flat generator settings format).

## Definition behavior

Preset data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Like world presets, flat presets are only effective before world creation.

Presets can be used on the superflat "Choose a preset" screen, showing the icon, preset code, and layer blocks (blocks without items show as air). To appear on the screen, a preset must be in the `#visible` tag. The translation key is `flat_world_preset.<namespace>.<name>`.

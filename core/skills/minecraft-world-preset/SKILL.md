---

name: minecraft-world-preset
description: "World preset definition JSON: WORLD_PRESET registry, dimension sets, tags."
whenToUse: "Use when writing datapack worldgen world_preset definitions."

---

# World Presets

This content applies only to Java Edition.

World preset definition files are the data-driven definitions of world presets in datapacks.

## Definition format

World presets use the `WORLD_PRESET` registry; the datapack path is `worldgen/world_preset` (definitions in `data/<namespace>/worldgen/world_preset`, tags in `data/<namespace>/tags/worldgen/world_preset`).

Definition files use JSON with the following structure:

- JSON file root object
  - `dimensions` (compound, required): the preset's dimension set; must include the Overworld (`overworld`). Each value is a dimension (see the dimension definition format).

## Definition behavior

World preset data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Presets provide preconfigured dimension sets for the menu screen; they are only effective before world creation. The dimension set is written into `level.dat`; dimension definition files with the same IDs override preset settings.

Two hardcoded presets allow modifying the Overworld: `flat` (superflat generator + settings) and `single_biome_surface` (single biome); dimension files still take precedence.

## Tags

- `#extended`: selectable while holding Alt.
- `#normal`: selectable without Alt.

If the preset tag is empty, all registered presets appear on the "World" screen.

## Text

Translation key: `generator.<namespace>.<path>`; the button shows "World type: generator.<namespace>.<path>".

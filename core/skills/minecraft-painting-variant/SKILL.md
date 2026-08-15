---

name: minecraft-painting-variant
description: "Painting variant definition JSON: PAINTING_VARIANT registry, size, texture."
whenToUse: "Use when writing datapack painting_variant definitions or custom paintings."

---

# Painting Variants

This content applies only to Java Edition.

Painting variants determine a painting's content and dimensions. Definition files are their data-driven definitions in datapacks.

## Definition format

Painting variants use the `PAINTING_VARIANT` registry; the datapack path is `painting_variant` (definitions in `data/<namespace>/painting_variant`, tags in `data/<namespace>/tags/painting_variant`).

Definition files use JSON with the following structure:

- JSON file root object
  - `width` (int, required): (1≤v≤16) painting width in blocks.
  - `height` (int, required): (1≤v≤16) painting height in blocks.
  - `asset_id` (string, required): (namespace ID) painting texture; resolved to `assets/<namespace>/textures/painting/<path>.png`.
  - `title` (string/compound/list): (text component) painting title.
  - `author` (string/compound/list): (text component) painting author.

## Definition behavior

Painting variant data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. The `PAINTING_VARIANT` registry must have at least one element, or the game errors during sync and blocks world loading.

### Tooltip

The painting item shows the dimensions of its `painting/variant` component variant in the tooltip, plus the author and title if set.

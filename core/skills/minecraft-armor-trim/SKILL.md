---

name: minecraft-armor-trim
description: "Armor trim definition format — patterns, materials, tooltips, texture generation."
whenToUse: "Use when authoring armor trim patterns/materials in data packs."

---

# Armor Trim Definition

Armor trims are decorative appearances added to armor/equipment models, combining a **trim pattern** and a **trim material**. Java Edition only.

## Trim Pattern

Registry `TRIM_PATTERN`, data pack path `trim_pattern` (files in `data/<namespace>/trim_pattern/`; tags in `tags/trim_pattern/`):

- `description` (required) — text component shown in tooltips.
- `asset_id` (required) — namespace ID affecting the trim texture.
- `decal` (default false) — render the trim only over the base armor texture's non-transparent pixels.

## Trim Material

Registry `TRIM_MATERIAL`, data pack path `trim_material` (files in `data/<namespace>/trim_material/`; tags in `tags/trim_material/`):

- `description` (required) — tooltip name.
- `asset_name` (required) — string suffix of the trim texture path.
- `palette_id` (required) — the palette used for trim texture tinting.
- `override_armor_assets` — per equipment asset: a string overriding `asset_name` for that asset.

Definitions load once at server startup (restart required). The smithing trim recipe defines the material inline in the addition's `provides_trim_material` component and names the pattern; applying it adds the `trim` component.

## Tooltips

Trimmed items show two tooltip lines: the pattern name, then the material name. Material name styles override the pattern's styles for the same properties.

## Textures

- **Pre-26.3**: trims render from the `minecraft:armor_trims` atlas; textures resolve to `assets/<ns>/textures/trims/entity/<equipment model layer>/<pattern path>_<material string>.png`. Trim textures share the armor model's UV mapping (any item can render trims). Vanilla defines base patterns and palettes and generates combinations via the `paletted_permutations` atlas source — non-vanilla trim textures aren't loaded without modifying the atlas.
- **From 26.3**: entity trims generate on demand; item trims pre-generate via `paletted_permutations`. For entities, the game combines the equipment asset, material, and pattern:
  1. Pattern texture → `assets/<ns>/textures/trim/entity/<layer>/<path>.png` (e.g. `humanoid/flow.png`).
  2. The pattern texture's metadata `palette.base_palette` → the base palette (`assets/<ns>/textures/palettes/<path>.png`, e.g. `trim_base`).
  3. The material's `palette_id` → the target palette (e.g. `trim/gold`).
  Then every base-texture pixel matching a base-palette color is replaced with the target palette's corresponding pixel, rendered over the armor via the layer's UV mapping. Missing/mismatched palettes render nothing. Equipment assets may define `trim_palette_replacements` to swap target palettes under conditions.

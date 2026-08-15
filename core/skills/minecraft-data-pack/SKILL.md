---
name: minecraft-data-pack
description: Data pack — usage, directory structure, pack.mcmeta, loading, experimental features.
whenToUse: Use when creating or managing data packs (pack.mcmeta, structure, reloading).
---

# Data Pack

Data packs customize game content: advancements, recipes, loot tables, enchantments, damage types, mob variants, world generation, and more. Java Edition only.

## Usage

Data packs are folders or `.zip` archives in `<save root>/datapacks/`. New packs can be configured (order, enabled, search) in the "More" tab of the create-world screen; selected packs are cached under the Java temp directory (`mcworld-<id>`).

- Loading: packs load on every save load. `/reload` reloads only advancements, recipes, functions, loot tables, predicates, and item modifiers; other content (worldgen, enchantments, armor trims, jukebox songs, ...) loads once at server startup — re-enter the save. Syntax errors in those files can trigger a "safe mode" screen blocking the save until the pack is disabled.
- Order: the configured order (stored in `level.dat` → `DataPacks`) applies; upper packs override lower ones. `/datapack list` shows the order; `/datapack disable` / `/datapack enable` toggle packs (auto-reload after).

## Experimental Features

Some pack content is flagged experimental; enabling it shows a warning screen when loading the save. Currently all non-hot-reloadable content triggers this whenever the pack content differs from vanilla.

## Directory Structure

```
<pack name>/
├── pack.mcmeta      # metadata
├── pack.png         # icon (optional)
└── data/
    └── <namespace>/
        ├── datapacks/          # built-in experimental packs (internal only)
        ├── function/           # functions (.mcfunction)
        ├── structure/          # structure templates (.nbt)
        └── advancement/ banner_pattern/ cat_variant/ chat_type/ chicken_variant/
            cow_variant/ damage_type/ decorated_pot_pattern/ dialog/ dimension/
            dimension_type/ enchantment/ enchantment_provider/ frog_variant/
            instrument/ item_modifier/ loot_table/ ... (JSON registries)
```

Each `data/<namespace>/<registry>/<path>.json` registers `<namespace>:<path>`; tags live in `data/<namespace>/tags/<registry>/<path>.json` (referenced with a `#` prefix). Functions and structure templates load similarly though they are not registry entries. Structure templates, advancements, and recipes have no tags. When multiple packs define the same file, upper packs win. Overlay directories fully override the pack's own content for matching files (even merge-on-load behaviors load only the last overlay's data).

## pack.mcmeta

Root object with a `pack` object:

- `description` (required) — text component shown in the datapack UI and on hover over `/datapack list` names.
- `min_format` (required) — minimum supported pack version: `[major, minor]` array (a bare int = `[n, 0]`).
- `max_format` (required) — maximum supported pack version (bare int = `[n, 0x7fffffff]`).
- `pack_format` / `supported_formats` — deprecated compatibility fields.
- `overlays` — sub-packs applied on top of the standard content: `entries` (in order) with `directory` (relative path; chars `a-z0-9_-`), `min_format`, `max_format` (or deprecated `formats`).
- `filter` — files to ignore: `block` list of `{namespace (regex), path (regex)}` patterns (omitted fields match everything).
- `features` — experimental features to enable: `enabled` list of namespace IDs. Adding this field requires adding the pack at world creation (or editing an old save's level.dat).

Example (new format):

```json
{ "pack": { "description": "Example pack", "min_format": [88, 0], "max_format": [107, 1] } }
```

## Data Pack Icon

`pack.png` at the pack root shows in the create-world screen's pack list; missing/broken icons fall back to `assets/minecraft/textures/misc/unknown_pack.png`.

## Data Pack Versions

The pack format number rises per release (e.g. 48 → 81 → 88 → 107...); see the Minecraft Wiki "Data pack" page for the version table and history.

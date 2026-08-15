---
name: minecraft-banner-pattern
description: Banner pattern definition JSON format: BANNER_PATTERN registry, asset_id, translation keys.
whenToUse: Use when writing datapack banner_pattern definitions or custom banner/shield patterns.
---

# Banner Pattern Definitions

This content applies only to Java Edition.

Banner patterns define the pattern types available for banners and shields. Banner pattern definition files are their data-driven definitions in datapacks.

## Definition format

Banner patterns use the `BANNER_PATTERN` registry; the datapack path is `banner_pattern`, so definitions live in `data/<namespace>/banner_pattern`, and tags in `data/<namespace>/tags/banner_pattern`.

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) texture used by the pattern; rendered from `assets/<namespace>/textures/entity/banner/<path>.png` (banners) and `assets/<namespace>/textures/entity/shield/<path>.png` (shields).
  - `translation_key` (string, required): prefix of the pattern's tooltip translation key; the full key is `<value>.<color name>` using the layer's color.

## Definition behavior

Banner pattern data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

A banner pattern defines the style of one pattern layer; each layer has a style and a color, rendered in list order (later layers cover earlier ones). The layer name is derived from `translation_key` and the color. For example, with translation key `block.minecraft.banner.custom.pattern` and color red, the full key is `block.minecraft.banner.custom.pattern.red`.

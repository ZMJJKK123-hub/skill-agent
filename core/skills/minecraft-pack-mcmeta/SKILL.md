---
name: minecraft-pack-mcmeta
description: pack.mcmeta — pack metadata, version validation, overlays, filters, languages.
whenToUse: Use when writing pack.mcmeta for resource packs or data packs.
---

# pack.mcmeta

The pack metadata is the only required file for a folder/zip to be recognized as a data pack or resource pack. Java Edition only.

## Resource Pack Metadata

`pack` object:

- `description` (required) — text component shown in the pack list (max 2 lines; truncates; formatting codes allowed).
- `min_format` (required) / `max_format` (required) — version range as `[major, minor]` arrays (bare int = `[n, 0]`; max_format bare int = max possible).
- `pack_format` / `supported_formats` — deprecated compatibility fields.
- `overlays` — sub-packs applied by version: `entries` (order matters; later entries take priority) each with `directory` (relative path; zips can't be overlay directories — inside a zip it's a path within it), `min_format`/`max_format` (or deprecated `formats`). Overlay packs ignore metadata and icons.
- `language` — extra languages: per language code (1–16 chars): `bidirectional` (default false), `name` (full name), `region` (country/region); the language file is `assets/<ns>/lang/<code>.json`.
- `filter` — blocks lower-priority packs' resources (position-dependent): `block` list of `{namespace (regex), path (regex)}`; empty object matches everything (fully blocks).

## Data Pack Metadata

Same core fields as above (`description`, `min_format`, `max_format`, deprecated `pack_format`/`supported_formats`), plus:

- `overlays` — same semantics (directory chars `a-z0-9_-`).
- `filter` — `block` patterns of files to ignore.
- `features` — experimental features to enable: `enabled` list of namespace IDs; adding this field requires adding the pack at world creation (or editing an old save's level.dat).

## Version Validation

Version ranges also gate overlay usage; whether the pack actually works depends on content, not metadata. Two format eras (boundary: game 1.21.8, data pack 81, resource pack 64):

- **Only post-1.21.8** (min > 81/64): must specify `min_format` + `max_format`; `pack_format`/`supported_formats` forbidden.
- **Only up to 1.21.8** (max < 82/65): must specify `pack_format`; `supported_formats` (if used) must contain `pack_format` and its max ≥ 15; `min_format`/`max_format` forbidden.
- **Both eras**: all four fields required; `min_format`'s major must equal `supported_formats`' min; the max is valid if `max_format`'s major equals `supported_formats`' max, OR `supported_formats`' max equals 64 (resource) / 81 (data) (then `max_format` is the actual max); `pack_format` must be inside the range.
- Overlays: if any overlay targets pre-1.21.8, `formats` must be specified; if none does, `formats` must not be specified (kept for old-version file validation even when the pack is post-1.21.8).

Min version 2147483647 or failed validation shows "(broken or incompatible)".

## Format Version List

The per-release pack format numbers (Java and April Fools versions; April Fools changes don't affect later versions): see the Minecraft Wiki "Pack format" page. External tool: the pack.mcmeta generator on misode.github.io.

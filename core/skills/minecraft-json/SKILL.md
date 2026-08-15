---
name: minecraft-json
description: JSON syntax used in Minecraft: values, objects, arrays, strings, numbers.
whenToUse: Use when writing or validating JSON files in datapacks and resource packs.
---

# JSON in Minecraft

JavaScript Object Notation (JSON) is a lightweight data interchange format used by Minecraft for:

- (Bedrock) text in written books, signs, custom names, `/tellraw`, `/titleraw`
- `pack.mcmeta` (Java resource/datapack descriptors) and `manifest.json` (Bedrock addons)
- Model, sound event, and UI files in resource packs; entity behavior files in behavior packs
- Advancements and statistics (`.minecraft/saves/*/data/stats/*.json`)
- Launcher profiles (`launcher_profiles.json`), version metadata
- (Java) datapack files: advancements, loot tables, tags, recipes, dimensions, dimension types, predicates, etc.

## Syntax

JSON text is a sequence of Unicode code points forming valid JSON data values: six structural symbols (`[` `{` `]` `}` `:` `,`), strings, numbers, and three literals (`true`, `false`, `null` — `null` is not used in Minecraft's datapack standard files).

Data value types: object, array, string, number, boolean, null.

- **Object**: `{...}` with 0+ key-value pairs; keys are strings, values any type; keys must be unique.
- **Array**: `[...]` with 0+ comma-separated values; unlike NBT lists, values may have mixed types.
- **String**: double-quoted with `\` escapes.
- **Number**: integers, decimals, and exponents (e.g. `2`, `-0.5`, `3e6`).
- **Boolean**: `true` or `false`.

## Serialization

Datapack files are deserialized into program objects when loaded. The game validates the data — extra object members may be dropped and numeric ranges recomputed; under strict validation, illegal values can throw during datapack load and block it. All "necessary" properties must be present or loading fails.

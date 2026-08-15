---

name: minecraft-namespaced-id
description: "Namespaced ID — legal characters, string conversion, usage, namespaces."
whenToUse: "Use when referencing objects by namespaced ID in data packs, resource packs, or commands."

---

# Namespaced ID

Namespaced identifiers (identifiers / resource locations / namespaced strings) identify game objects unambiguously: `namespace:path`. The default namespace is `minecraft` (Realms uses `realms`).

## Definition

- **Namespace** — uniqueness scope (default `minecraft`).
- **Path** — often mirrors the file path inside the pack; may be a pure identifier.
- String form joins them with `:`.

## Legal Characters

Java Edition:

- Namespace and path: `0-9`, `a-z`, `_`, `-`, `.` (snake_case recommended).
- `/` is illegal in namespaces but allowed in paths (directory separators).
- The namespace cannot be `..` (literally).

Bedrock: any characters except `/` and `:` (slash allowed in loot table/function names but not namespaces).

## String Conversion

ID → string: always possible (`ns:path`). String → ID constraints:

- At most one `:`.
- Both parts must satisfy the legal-character rules.
- With a `:` present, the part before it must not contain `/` or `.`.
- Without a `:`, the namespace defaults to `minecraft`.

## Usage

### Java — Registry Content

All registry objects (blocks, items, entity types, recipes, advancements, tags, enchantments, ...) use namespaced IDs.

### Java — Non-Registry Content

- Data packs: functions, structure templates, tags.
- Resource packs: equipment models, fonts, baked models, blockstate mappings, item model definitions, sounds, sound event reference names, shaders (includes + core), post-processing pipelines, textures, waypoint styles.
- Other modifiable content: boss bars, command storage, attribute modifiers, random sequences, custom click event identifiers, post-processing render targets, stopwatches, time markers.

### Bedrock

Built-in blocks/items/entities/effects/dimensions/biomes/features, item components in commands, add-on components, add-on JSON schemas, GameTest-enabled components; behavior pack content (blocks, entities, items, spawn rules, biomes, features, feature rules, function domains, recipes, structures, GameTests, NPC dialogs); resource pack content (attachments, camera perspectives, particles, fog settings).

## Actual File Paths (Java)

The file path is usually `<pack type>/<namespace>/<object type>/<name>.<extension>` ↔ ID `<namespace>:<name>`; `/`s inside the object type or name are directory separators. (Some resource pack elements, like GUI textures, don't rely on namespaced IDs.)

## Namespaces

- **`minecraft`** — the game's own namespace; the default when unspecified (`something` == `minecraft:something`). Only use it to override vanilla data or append to vanilla tags (e.g. `#minecraft:load`).
- **Custom namespaces** — each project/content should use its own; reuse another's only to override or extend it. Prefer specific names: avoid trivial abbreviations (`nc`) and vague words (`battle_royale`; `player_name_battle_royale` is better).
- **Other built-in namespaces** — `realms` (Realms language files `assets/realms/lang/<code>.json` and textures), `brigadier` (brigadier command argument types).

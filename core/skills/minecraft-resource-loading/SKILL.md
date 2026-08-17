---
name: minecraft-resource-loading
description: "How to write item/block models, textures, blockstates, item model definitions, recipes, and lang so resources load correctly in MC 1.21.11+ Forge."
whenToUse: "Use when creating or fixing MOD assets: item/block models, textures, blockstates, item model definitions, recipes, lang, pack.mcmeta."
---

# Minecraft Resource Loading (MC 1.21.11+ Forge)

> Goal: make every image/texture and JSON resource actually load in the game.
> The single most common failure is a **path/namespace mismatch** or a **missing required file**,
> not a complex rendering problem.

## 0. Core Rule: Resource Location == File Path

Minecraft resolves `namespace:path` to a file under `src/main/resources/`:

| Resource location | Actual file (relative to `src/main/resources/`) |
|---|---|
| `simplemod:item/template_item` | `assets/simplemod/models/item/template_item.json` |
| `simplemod:item/template_item` (inside a model's `textures`) | `assets/simplemod/textures/item/template_item.png` |
| `simplemod:block/example_block` | `assets/simplemod/models/block/example_block.json` |
| `simplemod:item/example_block` | `assets/simplemod/models/item/example_block.json` |

Rules:
- **Never** include `.json` or `.png` in a resource location inside JSON files.
- The namespace must exactly match the mod id in `META-INF/mods.toml` and the Java `@Mod(MODID)`.
- Directory names are singular and fixed: `items/`, `models/item/`, `models/block/`, `blockstates/`, `textures/item/`, `textures/block/`, `lang/`, `recipe/`.

## 1. Every Item / Block Item Needs an Item Model Definition

File: `src/main/resources/assets/<modid>/items/<registry_name>.json`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<modid>:item/<registry_name>"
  }
}
```

- Missing this file is the #1 cause of **inventory/search icon showing as missing/unrendered**,
  even when the block itself renders in the world.
- The `model` value points to `assets/<modid>/models/item/<registry_name>.json`.

## 2. Item Model + Texture (normal item)

File: `src/main/resources/assets/<modid>/models/item/<registry_name>.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "<modid>:item/<registry_name>"
  }
}
```

File: `src/main/resources/assets/<modid>/textures/item/<registry_name>.png`

- Must exist. Use a valid PNG (16×16 is standard; RGBA for transparent items).
- The texture reference `"<modid>:item/<registry_name>"` maps to `textures/item/<registry_name>.png`.

## 3. Block Model + Blockstate + Block Item

Files needed for a simple full block:

`assets/<modid>/blockstates/<registry_name>.json`

```json
{
  "variants": {
    "": {
      "model": "<modid>:block/<registry_name>"
    }
  }
}
```

`assets/<modid>/models/block/<registry_name>.json`

```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "<modid>:block/<registry_name>"
  }
}
```

`assets/<modid>/models/item/<registry_name>.json`

```json
{
  "parent": "<modid>:block/<registry_name>"
}
```

`assets/<modid>/textures/block/<registry_name>.png`

- Must exist.
- Also create `assets/<modid>/items/<registry_name>.json` for the block item (see section 1).

## 4. Recipe (MC 1.21.11+ format)

File: `src/main/resources/data/<modid>/recipe/<name>.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "category": "misc",
  "ingredients": [
    "minecraft:stick",
    "minecraft:iron_ingot"
  ],
  "result": {
    "id": "<modid>:<item_name>",
    "count": 1
  }
}
```

- **1.21.11+ ingredients are plain item id strings**, e.g. `"minecraft:stick"`.
  Do NOT use the old object form `{"item": "minecraft:stick"}`.
- Result uses `"id"` + `"count"`, not `"item"` + `"count"`.

## 5. Lang (display name)

`assets/<modid>/lang/en_us.json` / `zh_cn.json`

```json
{
  "item.<modid>.<item_name>": "English Name",
  "block.<modid>.<block_name>": "English Block Name",
  "itemGroup.<modid>.<tab_name>": "Creative Tab Name"
}
```

Missing lang does not prevent loading, but the item/block will show an ugly raw translation key.

## 6. pack.mcmeta (1.21.11)

`src/main/resources/pack.mcmeta`

```json
{
  "pack": {
    "description": "${mod_id} resources",
    "max_format": 94,
    "min_format": [94, 1]
  }
}
```

- Use `min_format` / `max_format` for this MC version.
- Wrong pack format can make the whole resource pack fail to load or warn in the log.

## 7. Common Failure Checklist

If an image/model is not loading, check in this order:

1. Does `assets/<modid>/items/<name>.json` exist? If not → inventory icon broken.
2. Does `assets/<modid>/models/item/<name>.json` exist? If not → no model.
3. Does `assets/<modid>/textures/item/<name>.png` (or `textures/block/<name>.png`) exist? If not → missing texture.
4. Is every `model` / `texture` value a namespaced path **without** `.json` / `.png`?
5. Does the namespace match `mods.toml` modId and Java `MODID`?
6. Is the JSON valid? No comments, no trailing commas.
7. For blocks: is there a `blockstates/<name>.json`? Does its `model` point to an existing `models/block/<name>.json`?
8. For recipes: are ingredients plain strings and result using `"id"`?
9. Is the PNG valid? Non-square/odd sizes can render unexpectedly; missing/transparent item texture shows purple/black missing texture.

## 8. Verification Loop (mandatory after writing assets)

After creating/editing any MOD resource:

1. **Run `validate_resources`** — this tool checks every item definition, model, texture, blockstate, recipe, and JSON syntax automatically.
2. **Check file paths exist** — use `glob` or `read_file` to confirm every referenced JSON/PNG exists if you need extra detail.
3. **Validate JSON syntax** — run `python -m json.tool <file>` for each JSON file (or use `bash` with a small loop).
3. **Build** — run `gradlew build` (or `build_mod_jar_forge`) and fix compile/resource errors from the log.
4. **GameTest** — for complex tasks, run `run_test_gametest` and read `read_game_test_log`; fix failures.
5. **Visual verification (optional)** — if the task is about visuals and vision mode is enabled, use `run_client` (or `run_test_client`), then `screenshot` + `analyze_image` to confirm the icon/model actually renders.

## 9. Related Skills

- `forge-items` — item registration, creative tabs, BEWLR.
- `minecraft-model` — model JSON details (parents, elements, tints, item models).
- `minecraft-texture` — texture format, animation, atlas rules.
- `minecraft-item-model-mapping` — advanced item model definitions in `assets/<ns>/items/`.
- `minecraft-pack-mcmeta` — pack metadata versions.
- `simple-mod-template` — complete simple item/block template with working examples.

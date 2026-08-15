---

name: minecraft-tutorial-custom-armor-trim
description: "Tutorial — custom armor trims: recipe, pattern/material, atlases, models."
whenToUse: "Use when adding custom armor trim patterns or materials via data + resource packs."

---

# Tutorial: Custom Armor Trims

Java Edition, for 1.21.5+ (older versions: "Custom armor trim/old"). Prerequisites: datapack basics. Tools: the Misode Recipe/Atlas/Item generators (Ctrl+S saves into the web datapack).

## Data Pack

### Recipe

The smithing table has 3 inputs (template, base, addition) + 1 output. A `smithing_trim` recipe e.g. bamboo pattern + blaze powder addition:

```json
{
  "type": "minecraft:smithing_trim",
  "template": "minecraft:bamboo",
  "base": "#minecraft:trimmable_armor",
  "addition": "minecraft:blaze_powder",
  "pattern": "example:bamboo"
}
```

`#minecraft:trimmable_armor` = all trimmable armor (extend it to add more). To also allow vanilla trim materials as additions, add the new item to `#minecraft:trim_materials` and use that tag as `addition`.

### Trim Pattern

`data/example/trim_pattern/bamboo.json`:

```json
{
  "asset_id": "example:bamboo",
  "description": { "translate": "trim_pattern.example.bamboo", "fallback": "Bamboo Trim" },
  "decal": false
}
```

### Trim Material

The material is NOT a recipe field — it comes from the addition item's `provides_trim_material` data component:

```mcfunction
give @s blaze_powder[provides_trim_material="example:blaze_powder"]
```

Then `data/example/trim_material/blaze.json`:

```json
{
  "asset_name": "blaze",
  "description": { "translate": "trim_material.example.blaze", "fallback": "Blaze Trim Material" }
}
```

## Resource Pack

### Equipment Model Atlas

Trim textures on equipment models come from atlases. Override `assets/minecraft/atlases/armor_trims.json` (merges, doesn't replace vanilla). Draw two textures (`example:textures/trims/entity/humanoid/bamboo.png` and `humanoid_leggings/bamboo.png` — BlockBench "Armor (Main)"/"Armor (Leggings)" templates help; the palette maps palette-key pixels to permutation pixels, others unchanged):

```json
{
  "sources": [
    {
      "type": "paletted_permutations",
      "textures": [ "example:trims/entity/humanoid/bamboo", "example:trims/entity/humanoid_leggings/bamboo" ],
      "palette_key": "minecraft:trims/color_palettes/trim_palette",
      "permutations": { "blaze": "example:trims/color_palettes/blaze" }
    }
  ]
}
```

`palette_key` = the base grayscale colors; `permutations` keys = the material's `asset_name`; `textures` = the patterns to tint.

### Item Model Atlas

Item trim textures are generated from `assets/minecraft/atlases/blocks.json` (merge). Vanilla textures reused:

```json
{
  "sources": [
    {
      "type": "paletted_permutations",
      "palette_key": "minecraft:trims/color_palettes/trim_palette",
      "permutations": { "blaze": "example:trims/color_palettes/blaze" },
      "textures": [
        "minecraft:trims/items/helmet_trim", "minecraft:trims/items/chestplate_trim",
        "minecraft:trims/items/leggings_trim", "minecraft:trims/items/boots_trim"
      ]
    }
  ]
}
```

This produces e.g. `minecraft:trims/items/helmet_trim_blaze`.

### Item Models

Item model definitions select trim textures by the `trim` component: `assets/minecraft/items/iron_chestplate.json` uses a `select` with `property: minecraft:trim_material` and cases per material (`minecraft:quartz`, `minecraft:iron`, `minecraft:netherite`, `minecraft:redstone`, `minecraft:copper`, `minecraft:gold`, ...) with a fallback to the untrimmed model; add a case for your material (here `example:blaze` → `example:item/iron_chestplate_blaze_trim`).

The model file itself (per armor piece; helmet example shown):

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/iron_helmet",
    "layer1": "minecraft:trims/items/helmet_trim_blaze"
  }
}
```

`layer0` renders first, `layer1` (from the blocks atlas) over it. Repeat the pattern/leggings/boots equivalents for full coverage.

The complete file set for this tutorial is in the linked public GitHub repository (see the wiki page).

---
name: minecraft-recipe
description: Recipe system — acquisition, recipe book, Java recipe JSON types, Bedrock.
whenToUse: Use when authoring recipe JSON files for data packs (Java) or behavior packs (Bedrock).
---

# Recipe

Recipes guide players through crafting, smelting, and other block/item conversions. Crafting, smelting, blasting, campfire, smoking, smithing, stonecutting, and brewing (Java 26.3+) all use the recipe system; cartography too on Bedrock. Most recipes are data-driven.

## Acquisition

Using a recipe auto-discovers it; `/recipe` grants it directly; conditions (e.g. obtaining items) unlock it — in Java via advancement rewards, in Bedrock via the recipe itself. Discovered recipes are stored in the player's `recipeBook` (or `recipe_unlocking`) NBT.

## Usage

Recipes appear in the recipe book, but discovery is only required with the `limited_crafting` game rule. Recipes show only in matching interfaces (smelting in furnaces, etc.); the inventory recipe book shows only 2×2-compatible recipes.

## Java Edition

Registry `RECIPE`, data pack path `recipe` (files in `data/<namespace>/recipe/`). There are no recipe tags — `data/<namespace>/tags/recipe/` is never loaded. Files are JSON:

```json
{ "type": "<namespace id>", ... }
```

Common fields (crafting recipes): `group` (default "", groups merge in the book), `category` (default `misc`; `building`, `redstone`, `equipment`, `misc`), `show_notification` (default true).

### Crafting Recipes

- `crafting_shaped` — shaped recipe. `key` (map char → item ID / item list / item tag; chars are single non-space characters), `pattern` (1–3 rows, equal lengths, spaces = empty), `result` (item template). Mirror-symmetric arrangements are automatically valid.
- `crafting_shapeless` — `ingredients` (1–9 entries: item ID/list/tag), `result`. 9 identical ingredients are treated internally as a shaped recipe.
- `crafting_transmute` — changes the item type while keeping the input's component revision: `input`, `material` (consumed), `material_count` (default [1,1], subrange of [1,8]), `result`, `add_material_to_result_count` (default false — adds the count of material slots to the output stack size). No effect when input == output.
- `crafting_dye` — dyeing: `target`, `dye` (must have the `dye` component), `result`. Requires ≥2 items and exactly one `target`; the target goes through the transmute processing, then a new `dyed_color` component is set from existing + input dye colors.
- `crafting_imbue` — potion effect copying (Java 26.3+): the grid center must be `source`, the 8 surrounding slots `material`; the source's `potion_contents` component is copied to `result`.

### Custom (Special) Recipes

Handled by internal code; the JSON only restricts ingredients. Not shown in the recipe book, cannot be unlocked, unaffected by `limited_crafting`.

- `crafting_decorated_pot` — `back` (row 1 col 2), `left` (row 2 col 1), `right` (row 2 col 3), `front` (row 3 col 2), `result`; output gets a `pot_decorations` component from the ingredients.
- `crafting_special_bannerduplicate` — `banner`, `result`. Exactly 2 stacks; both must be banners of the same base color; pattern source's `banner_patterns` must be ≤ 6 layers. The pattern source is NOT consumed (unless it has a remainder item).
- `crafting_special_bookcloning` — `source` (must have `written_book_content`), `material`, `allowed_generations` (default [0,1], subrange of [0,2]; 0 = original, 1 = copy of original, 2 = copy of copy, 3 = tattered), `result`. Copies the content with `generation` +1; consumed material count adds to the output count; the source is not consumed.
- `crafting_special_firework_rocket` — `shell` (exactly one), `fuel` (≤3, +1 `flight_duration` each), `star` (provides `firework_explosion` components in grid order), `result`; output gets a `fireworks` component.
- `crafting_special_firework_star` — `trail`, `twinkle`, `fuel`, `dye` (must have `dye` component; each modifier at most once), `shapes` (`small_ball`, `large_ball`, `burst`, `star`, `creeper`; default small ball), `result`; output gets a `firework_explosion` component.
- `crafting_special_firework_star_fade` — `target`, `fuel` (dyes), `result`; sets `fade_colors` in the `firework_explosion` component (≥2 items, exactly one target).
- `crafting_special_mapextending` — `map` (center; must have `map_id`, the map data must exist, not be an explorer map, scale ≠ 4), `material` (8 around), `result`; sets `map_post_processing` to 1.
- `crafting_special_repairitem` — no other fields. Two items of the same type with `damage`/`max_damage` components; output takes the max max-durability, sums remaining durability + 5%; keeps both curse enchantments; other enchantments take the highest level.
- `crafting_special_shielddecoration` — `banner` (must be a banner), `target` (no or empty `banner_patterns`), `result`; sets `base_color` and `banner_patterns` from the banner.

### Smelting Recipes

Common fields: `group`, `category` (`food`, `blocks`, `misc`), `show_notification`, `experience` (default 0), `cookingtime` (default 200 for `smelting`; 100 for `blasting`, `smoking`, `campfire_cooking`), `ingredient`, `result`.

- `smelting` — furnace.
- `blasting` — blast furnace.
- `smoking` — smoker.
- `campfire_cooking` — campfire and soul campfire. All vanilla campfire recipes use 600 ticks (30 s). Does not trigger the `recipe_unlocked` advancement trigger.

### Stonecutting

`stonecutting` — `ingredient`, `result` (no group/category).

### Brewing (Java 26.3 dev)

`brewing` — `input` (`item` + optional `potion_contents`), `output` (item template), `reagent` (item).

### Smithing

- `smithing_transform` — `template`, `base` (required), `addition`, `result`; the base item is transmuted into the result (components preserved).
- `smithing_trim` — `template`, `base` (required), `addition` (required; its `provides_trim_material` component determines the trim material), `pattern` (trim pattern).

## Bedrock Edition

Files are JSON in the behavior pack's `recipes/` directory. Ingredient format: `{item, data (int or Molang), tag}`; output format: `{item, data, count}`. Types (each under `format_version` + the type key, with `description.identifier`, `tags` (valid vanilla tags listed per type), `group`, `priority` (lower = higher priority), `unlock` (list of required items or `{context: AlwaysUnlocked | PlayerInWater | PlayerHasManyItems}`)):

- `minecraft:recipe_shaped` — `key` + `pattern` + `result` (single item or list), `assume_symmetry` (default true). Tags: `crafting_table`.
- `minecraft:recipe_shapeless` — `ingredients` + `result` (exactly one). Tags: `crafting_table`, `stonecutter`, `cartography_table`. The stonecutter uses this system.
- `minecraft:recipe_furnace` — `input` + `output`. Tags: `furnace`, `blast_furnace`, `smoker`, `campfire`, `soul_campfire`.
- `minecraft:recipe_brewing_container` — `input`, `output`, `reagent`. Tag: `brewing_stand`.
- `minecraft:recipe_brewing_mix` — `input` (potion effect), `output` (potion effect), `reagent`. Tag: `brewing_stand`.
- `minecraft:recipe_smithing_transform` — `template`, `base`, `addition`, `result`. Tag: `smithing_table`; items need `minecraft:trim_templates`/`trimmable_armors`/`trim_materials` tags to be placeable (only netherite ingots are valid additions in vanilla).
- `minecraft:recipe_smithing_trim` — `template`, `base`, `addition`. Tag: `smithing_table`.
- `minecraft:recipe_material_reduction` (Education) — `input` + `output` (≤9). Tag: `material_reducer`.

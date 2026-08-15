---

name: minecraft-item-modifier
description: "Item modifier (loot function) format — all modifier types with fields."
whenToUse: "Use when writing item modifier JSON files or inline loot functions."

---

# Item Modifier

Item modifiers (also loot modifiers, loot functions, item functions) are technical JSON files in `data/<namespace>/item_modifier/`, applied to items via loot tables or the `/item` command. They are essentially loot item functions (conditional functions with optional `conditions`). Vanilla ships no default modifiers — they come from data packs.

## Usage

- `/item modify (block <pos>|entity <targets>) <slot> <modifier>` — applies a modifier directly.
- `/item replace (block <pos>|entity <targets>) <slot> from (block <pos>|entity <targets>) [<modifier>]` — replaces the item, then applies the modifier.
- Loot tables call item modifiers inline (in `functions` fields); the `reference` modifier calls a standalone file.

## Basic Format

A modifier is one object or an array of objects:

```json
{ "function": "<namespace id>", "conditions": [ ... ], ... }
```

`conditions` — loot predicates that must all pass. For count-increasing modifiers: negative original counts are reset to 0 first; stacks with final count ≤ 0 become empty.

## Modifier Types

- `apply_bonus` — extra count from an enchantment level: `enchantment`, `formula` = `uniform_bonus_count` (uniform random in [c, c + b·l]; `bonusMultiplier`), `ore_drops` (l=0 → c; else up to l+1 times), `binomial_with_bonus_count` (binomial with `extra` trials + level, `probability`).
- `copy_components` — copy components from a source: `source` = `block_entity`, `this`, `attacker`, `attacking_player`, `direct_attacker`, `tool`, `target_entity`, `interacting_entity`; `include` / `exclude` component ID lists (absent include = all except exclude).
- `copy_custom_data` — copy NBT into the `custom_data` component: `ops` list of `{op: replace|append|merge, source (NBT path), target (NBT path in components.'minecraft:custom_data')}` with the source given as `source` + `type` (`context` with `target` entity/block-entity, or `storage` with `source` storage ID).
- `copy_name` — copy a name into `custom_name`: `source` = `this`, `attacker`, `last_damage_player`, `block_entity`, `direct_attacker`, `target_entity`, `interacting_entity`.
- `copy_state` — copy block state into the `block_state` component: `block` (block ID, mismatches void the modifier), `properties` (list).
- `enchanted_count_increase` — enchantment-based count: `count` (per level, added as round(count × level)), `enchantment`, `limit` (0 = unlimited).
- `enchant_randomly` — random enchantment (level also random): `only_compatible` (default true; books unrestricted), `options` (enchantment ID/tag/list, default all), `include_additional_cost_component` (default false; villager trade count, needs `additional_cost_component_allowed` context).
- `enchant_with_levels` — enchant like an enchanting table at a level: `levels` (number provider), `options`, `include_additional_cost_component`.
- `exploration_map` — turn a map into an explorer map: `decoration` (default `mansion`), `destination` (structure tag without `#`, default `on_treasure_maps`), `search_radius` (Chebyshev, default 50), `skip_existing_chunks` (default true), `zoom` (default 2).
- `explosion_decay` — each item has 1/explosion radius chance to vanish (per item for stacks) when dropped by an explosion; else no-op.
- `discard` — replace the stack with an empty stack.
- `fill_player_head` — set a player head's profile: `entity` (this/attacker/attacking_player/direct_attacker/target_entity/interacting_entity).
- `filtered` — `item_filter` (item predicate); `on_pass` / `on_fail` modifiers.
- `furnace_smelt` — convert to the smelting result (no-op if unsmeltable).
- `limit_count` — `limit` = `{min, max}` number providers (clamp).
- `modify_contents` — apply a `modifier` to contents of `component` = `container`, `bundle_contents`, or `charged_projectiles`.
- `reference` — `name` (modifier ID; cycles warn).
- `sequence` — `functions` list applied in order.
- `set_attributes` — `modifiers` list of `{amount (number provider), attribute, id, operation (add_value/add_multiplied_base/add_multiplied_total), slot (mainhand/offhand/head/chest/legs/feet/hand/body/armor/any/saddle or list), replace (default true)}`.
- `set_banner_pattern` — `append` (bool), `patterns` (list of `{color, pattern}`).
- `set_book_cover` — `author`, `generation` (0–3), `title` (≤32 chars, with `filtered`/`raw`).
- `set_custom_model_data` — set `custom_model_data` component lists: `colors`/`floats`/`strings`/`flags`, each with `values` and `mode` (`append`/`insert` (+`offset`)/`replace_all`/`replace_section` (+`offset`, `size`)).
- `set_components` — `components` (patch: `id` = value, `!id` = remove).
- `set_contents` — `component` (container/bundle_contents/charged_projectiles), `entries` (loot pool entries).
- `set_count` — `count` (number provider), `add` (default false; true adds to existing).
- `set_custom_data` — `tag` (SNBT string or compound; merged into `custom_data`).
- `set_damage` — `damage` (number provider; durability ratio), `add` (default false; final = ceil((ratio + current ratio) × max)). Watch float precision (e.g. use −0.10001 for −1 on a 10-durability item).
- `set_enchantments` — `enchantments` (map ID → level number provider), `add` (default false; true adds levels, not anvil-style).
- `set_firework_explosion` — `colors`, `fade_colors` (RGB ints; unknown dye colors show "custom"; multiple colors picked randomly per particle; absent = black), `trail`, `twinkle`, `shape` (`small_ball`/`large_ball`/`star`/`creeper`/`burst`).
- `set_fireworks` — `flight_duration` (unsigned byte, gunpowder count), `explosions` (values ≤256, each like set_firework_explosion with `has_trail`/`has_twinkle`/`shape`; `mode` like set_custom_model_data).
- `set_instrument` — `options` (instrument ID/tag/list) for goat horns.
- `set_item` — `item` (new item ID; keeps count and components).
- `set_loot_table` — for container block items: `name` (loot table), `seed`, `type` (block entity ID).
- `set_lore` — `lore` (text components), `entity` (for `@s` in components), `mode` (append/insert/replace_all/replace_section with offset/size).
- `set_name` — `name` (text component), `entity`, `target` = `custom_name` or `item_name`.
- `set_ominous_bottle_amplifier` — `amplifier` (number provider) for the `ominous_bottle_amplifier` component.
- `set_potion` — `id` (potion effect ID).
- `set_random_dyes` — `number_of_dyes` (number provider; 16 colors, may repeat) → `dyed_color`.
- `set_random_potion` — `options` (potion effect ID/tag/list).
- `set_stew_effect` — `effects` list of `{duration (number provider), type}` for suspicious stew.
- `set_writable_book_pages` — `pages` (strings ≤1024 or `{text, filtered}`), `mode` (append/insert/replace_all/replace_section).
- `set_written_book_pages` — `pages` (text components or `{raw, filtered}`), `mode` (same).
- `toggle_tooltips` — `toggles` (component ID → visible bool).
- (Also: `set_tool`, `set_trim_material`, `set_trim_pattern`, `set_written_book_cover` exist in the wiki's table — see the Minecraft Wiki "Item modifier" page for the complete list.)

## Removed Modifiers

- `copy_nbt` — removed in 1.20.5; renamed `copy_custom_data` (copied into the item `tag` before components).
- `set_nbt` — removed in 1.20.5; renamed `set_custom_data`.
- `looting_enchant` — removed in 1.21; renamed `enchanted_count_increase` (per-level Looting count with `limit`).

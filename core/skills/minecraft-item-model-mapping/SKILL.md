---
name: minecraft-item-model-mapping
description: Item model definition format — condition/range/select dispatch, tints, special models.
whenToUse: Use when authoring item model definition JSON files in assets/<namespace>/items/.
---

# Item Model Definition

Item model definitions (officially "item models" / "client-side item info") select which baked model an item stack renders, based on the stack's data. Java Edition only. Files are JSON in `assets/<namespace>/items/` (one per item ID; vanilla: `assets/minecraft/items/<item id>.json`). Invalid definitions fall back to the missing model.

## Root Format

- `hand_animation_on_swap` (default true) — play the swap animation when switching to this stack in the hotbar (never plays if stacks differ only by durability, per the `damage` component).
- `oversized_in_gui` (default false) — allow rendering beyond the slot bounds in GUIs.
- `swap_animation_scale` (default 1) — speed multiplier of the swap animation (larger models may need larger values).
- `model` (required) — the item model definition (see below).

## Item Model Definitions

Every definition has `type` (namespace ID) plus type-specific fields, and may carry a `transformation`:

- `condition` — boolean dispatch: `property` (predicate type) with `on_true` / `on_false` (recursive definitions). If the property value is missing/invalid, `on_false` is used.
- `range_dispatch` — numeric dispatch: compute a numeric property, multiply by `scale` (default 1), pick the first sorted `entries` item whose `threshold` is reached (entries are sorted at runtime); below all thresholds use `fallback` (absent → missing model).
- `select` — enum dispatch: `cases` (list of `{when: value or list, model}`; duplicate cases error with `Duplicate case conditions: ...`), `fallback` for unmatched values (absent → missing model).
- `model` — render a baked model: `model` (path → `assets/<ns>/models/<path>.json`), `tints` (list indexed by tint index of color providers):
  - `custom_model_data` — color from `custom_model_data` component `colors[index]` (`default` RGB, `index` default 0).
  - `constant` — fixed `value` (RGB int).
  - `grass` — biome grass color from `temperature` + `downfall` (0–1 each) using `grass.png`.
  - `firework` — average of the `firework_explosion` component's `colors`.
  - `dye` — the `dyed_color` component color.
  - `potion` — the `potion_contents` component color.
  - `map_color` — the `map_color` component color.
  - `team` — the holding entity's team color.
  - (the last five use `default` RGB when unavailable).
- `bundle/selected_item` — renders the currently selected item inside the bundle; requires the `bundle_contents` component, else nothing renders.
- `composite` — computes all `models` (list) and renders them back to front (e.g. bundle back layer + selected item + front layer).
- `special` — hardcoded special model rendering: `base` (base item model providing transforms/gui light/particle texture) + `model`:
  - `banner` — banner from base color + `banner_patterns`: `attachment` (`wall`/`ground`, default `ground`), `color`.
  - `book` — lectern-like book: `open_angle` (0 closed – 90 flat), `page1`, `page2` (0 left – 1 right).
  - `chest` — chest: `chest_type` (`single`/`left`/`right`), `openness` (default 0), `texture` (→ `assets/<ns>/textures/entity/chest/<path>.png`).
  - `copper_golem_statue` — `pose` (`standing`/`sitting`/`running`/`star`), `texture` (→ `assets/<ns>/<path>`).
  - `end_cube` — special-effect cube: `effect` (`portal` or `gateway`).
  - `head` — mob head: `kind` (`creeper`/`dragon`/`piglin`/`player`/`skeleton`/`wither_skeleton`/`zombie`), `animation` (default 0; dragon/piglin animation progress), `texture` (→ `assets/<ns>/textures/entity/<path>.png`).
  - `shulker_box` — `openness` (default 0), `texture` (→ `assets/<ns>/textures/entity/shulker/<path>.png`).

### Transformation

Applied after the baked model's own `display` transforms, origin at the stack's position:

- Matrix form: 16 floats, row-major; elements 13–15 have no effect; element 16 scales the first 12 (division).
- Decomposed form (all required, applied in order): `right_rotation` (quaternion `[x,y,z,w]` — non-unit scales the model — or `{angle (radians), axis}`), `scale` `[x,y,z]`, `left_rotation` (same formats), `translation` `[x,y,z]`.

## Condition Properties (boolean)

- `broken` — item is broken (damage ≥ max_damage). Example: elytra → `item/elytra_broken`.
- `bundle/has_selected_item` — the bundle has a selected item.
- `damaged` — the item has damage.
- `using_item` — a mob is currently using the item (bow pulling, brush brushing...).
- `custom_model_data` — reads `custom_model_data` component `flags[index]` (index default 0; missing component or out of range → false).
- `component` — `predicate` (data component predicate type) + `value` (predicate contents); true when the stack satisfies it.
- `has_component` — `component` (component type); `ignore_default` (default false) — treat default-valued components as absent.
- `keybind_down` — `keybind` (binding localization key) is currently pressed.

## Range Properties (numeric)

- `custom_model_data` — `floats[index]` (index default 0; missing/out of range → 0).
- `compass` — compass wobble progress (0–1). `target`: `spawn` (toward the world spawn in the Overworld), `lodestone` (toward the `lodestone_tracker` position; random wobble when no target, cross-dimension, or <1e-5 distance), `none` (random). `wobble` (default true) — extra wobble oscillation.
- `count` — stack count, clamped to max stack size; `normalize` (default true) — return count/maxStack instead.
- `damage` — damage value (0 if undamaged/unbreakable; clamped to max durability); `normalize` (default true) — return damage/max.
- `time` — smooth clock wobble progress (0–1) of the current dimension time: `source` = `daytime` (time of day), `random` (random), `moon_phase` (0–1 per moon phase); `wobble` (default true).
- `use_cycle` — remaining use time modulo `period` (default 1). Example: brush animates over a 10.0 period scaled 0.1.
- `use_duration` — use time or remaining use time (`remaining`, default false). Example: bow pulling states.
- (Also in the property table on the wiki: `cooldown`.)

## Select Properties (enum)

- `context_dimension` — the current dimension ID (e.g. compass: `minecraft:overworld` vs random fallback).
- `trim_material` — the trim material from the `trim` component (chainmail boots per-material models).
- `block_state` — the `block_state` component's block property value: `block_state_property` (e.g. `honey_level` on bee nests/hives; no component/property → null, unmatched).
- `component` — full component value match (persistent components only; non-persistent or mismatched values fail loading). Matching is exact (SNBT-normalized): `{a:data,b:true}` == `"{\"a\":\"data\",\"b\":true}"`; partial matches like `{"a":"data"}` do NOT match `{a:data,b:true}`.
- `custom_model_data` — `strings[index]` (missing/out of range → null).
- `local_time` — formatted local date/time string: `pattern` (date format, e.g. `MM-dd`), `locale` (default ""), `time_zone` (default system). Fetched at most once per second. Example: chest uses the Christmas texture on 12-24..12-26.
- (Other enum properties in the table: `main_hand`, etc. — see the Minecraft Wiki "Item model definition" page for the complete table.)

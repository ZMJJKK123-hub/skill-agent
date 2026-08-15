---
name: minecraft-slot-source
description: Slot source format — all slot source types (slot_range, contents, group...).
whenToUse: Use when writing slot sources in loot tables or /item commands.
---

# Slot Source

Slot sources select specific slots from slot-holding objects (block entities, entities). Java Edition only. Used in loot tables and (from 26.3) command parameters.

## Definition Format

Before 26.3, slot sources are loot-table-only. From 26.3: registry `SLOT_SOURCE`, data pack path `slot_source` (files in `data/<namespace>/slot_source/`; tags in `tags/slot_source/`).

A slot source is an object `{type, ...}` or a list of slot sources (list = `group` behavior).

## Types

- `group` — `terms` (recursive list): concatenates the slot lists in order, duplicates included (`[a,b]` + `[a,c]` → `[a,b,a,c]`).
- `filtered` — `item_filter` (item stack predicate) + `slot_source` (recursive): drops slots whose item fails the test.
- `limit_slots` — `limit` (max count) + `slot_source`: keeps only the first `limit` slots in order.
- `slot_range` — picks slots from a source's slot range: `source` (from the loot context: `block_entity`, `this`, `attacking_entity`, `last_damage_player`, `direct_attacker`, `target_entity`, `interacting_entity`; default `container`) and `slots` (slot range like `armor.chest`, `container.*`). From 26.3, directly specifying a slot range in the `slot_source` command parameter converts to this type (source = the command's `container` context parameter).
- `contents` — gets slots from container components of the input slots' items: `component` (`bundle_contents`, `charged_projectiles`, or `container`) + `slot_source` (recursive). Empty/missing items or components yield no slots. From 26.3, `/item` targeting component slots first sets the component on the item when missing; `(fill|override)` gets all available component slots; `bundle_contents` fills in slot order, stopping when the bundle would overflow.
- `reference` (26.3) — `name` (slot source ID); cycles fail parsing.
- `empty` — no slots.

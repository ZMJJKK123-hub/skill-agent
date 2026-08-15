---
name: minecraft-tutorial-line-of-sight
description: Tutorial — sight magic datapack: raycast, explosion, bee inspection.
whenToUse: Use when building datapack spells/raycasts triggered by right-click items (Java 1.21.2+).
---

# Tutorial: Datapack Example — Sight Magic

Java Edition only; requires 1.21.2+ (the raycast tutorial it builds on is the base). Prerequisites: the raycasting tutorial, datapack/resourcepack tutorials.

## Goal

Right-clicking an item causes events at the block the player is looking at:

- an **explosion**, and
- if the target is a **beehive or bee nest**, print the counts of adult and baby bees inside.

## Raycast Improvements

The base raycast (`generic/function/raycast/`) is enhanced:

- Step length 0.5 instead of 0.1 (fewer recursions).
- `#raycast_check_times` counter vs `#raycast_max_check_times` (max 1000) → `return run function generic:raycast/end`.
- Stop when the block at `~ ~ ~` is not `#generic:raycast/can_pass`.
- Entity check at `~ ~-0.5 ~` with `@n[dx=0,dy=0,dz=0]`-style tiny box (flag `#raycast_pass_entity`).
- Start from the executor's eye position: `execute as @s anchored eyes run ...`.
- Optional debugging: `particle minecraft:end_rod ~ ~ ~ 0 0 0 0 0`; interaction entity `execute positioned ~ ~-0.5 ~ run summon interaction ^ ^ ^ {Tags:["test","source_entity"]}`.

## Right-Click Detection

A `minecraft:consume_item` advancement fires only when the consumed item matches a `custom_data` predicate (`{listen_event:'right_click'}`), and rewards a function:

```json
{
  "criteria": {
    "generic:right_click_event": {
      "trigger": "minecraft:consume_item",
      "conditions": { "item": { "predicates": { "custom_data": "{listen_event:'right_click'}" } } }
    }
  },
  "rewards": { "function": "generic:event/right_click" }
}
```

`generic/function/event/right_click.mcfunction` revokes the advancement, then **simulates a coroutine**: store the executor and its held item (e.g. into a storage or a marker entity), wait 1 tick, then restore the item so it is not actually consumed (the consume_item trigger fires before the stack is truly eaten).

## Sight Explosion Magic

Explosion at the aim point: summon an instant-igniting TNT or a Creeper at the ray end.

- `generic/tags/function/right_click.json` — function-tag interface: `{ "values": ["test:sight_magic/extender/right_click"] }`.
- `test/sight_magic/extender/right_click.mcfunction` — implements the interface:
  - Guard: `execute unless items entity @s weapon.mainhand * [custom_data ~ {id:'sight_magic'}] run return fail`.
  - Domain flag pair: `tag @s add used_sight_magic` ... `tag @s remove used_sight_magic` (closed around the branch).
  - Branch by held item: `execute if items entity @s weapon.mainhand * [custom_data ~ {cause_event:'explosion'}] run function test:sight_magic/explosion/start`.
- `explosion/start` — tags the player, sets `#raycast_max_check_times`, calls the raycast; `explosion/end` (via the raycast end interface) summons the TNT/Creeper at `~ ~ ~` and cleans up.

## Bee Finder Magic

Same skeleton, new branch: `cause_event:'get_bees'` → `test:sight_magic/bee_finder/start`.

- start: `tag @s add get_bees`, set raycast max checks, run raycast.
- end: check the block at the ray end — if it is `beehive`/`bee_nest`, read the block entity with `/data get block ~ ~ ~ bees` and count entries; adult vs baby by each bee's `entity_data.Age` (`-1` = baby); output e.g. `tellraw @a "Adults: X, Babies: Y"`. Clean up tags and counters.

## Carrot-on-a-Stick Toggle (optional, older pattern)

Scoreboard-based toggle for using carrot-on-a-stick as a "remote":

- `nuke:entities/player`: `execute as @s[scores={nukeUseCSt=1..}] at @s run function nuke:use_carrot_on_a_stick/type`.
- `type`: checks `weapon.mainhand` / `weapon.offhand` for `carrot_on_a_stick`, dispatches to mainhand/offhand functions, then `scoreboard players reset @s nukeUseCSt`.
- `mainhand`/`offhand`: check `carrot_on_a_stick {id:'nuke:remote'}` custom data to enable the effect, else the plain carrot-on-a-stick behavior (pig riding); toggling sets the score. (Note: this section is flagged as outdated for current versions — prefer the consume_item advancement approach.)

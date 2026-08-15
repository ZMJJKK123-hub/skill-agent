---
name: minecraft-advancement
description: Advancement definition format — JSON in data packs: criteria, triggers, display, rewards.
whenToUse: Use when authoring or validating advancement JSON files in data packs.
---

# Advancement Format

Advancements are technical JSON files in data packs that define progression. Java Edition only.

## Folder Structure

```
<data pack>/
├── pack.mcmeta
└── data/<namespace>/
    └── advancement/<name>.json
```

## Root Format

- `criteria` — the criteria of this advancement (see Criteria below).
- `display` — display information (see Display below).
- `parent` — namespace ID of the parent advancement. If absent, this advancement is a root advancement. Cyclic parent links cause a load failure.
- `requirements` — how the criteria are combined: a list of sublists, each holding several criterion names. The advancement is granted when at least one criterion in **every** sublist is met. Default (absent): all criteria are required. An empty sublist makes the advancement impossible to obtain except via cheats.
- `rewards` — granted when the advancement is completed:
  - `experience` (default 0) — XP granted to the player.
  - `function` — a function executed with the player as executor at their position (function tags are not supported).
  - `loot` — loot tables granted to the player.
  - `recipes` — recipes unlocked for the player.
- `sends_telemetry_event` (default `false`) — whether telemetry is collected when the advancement is earned. Only effective for advancements in the `minecraft` namespace.

### Example

```json
{
  "criteria": {
    "crafting_table": {
      "conditions": { "items": [ { "items": "minecraft:crafting_table" } ] },
      "trigger": "minecraft:inventory_changed"
    }
  },
  "display": {
    "announce_to_chat": false,
    "background": "minecraft:gui/advancements/backgrounds/stone",
    "description": { "translate": "advancements.story.root.description" },
    "icon": { "count": 1, "id": "minecraft:grass_block" },
    "show_toast": false,
    "title": { "translate": "advancements.story.root.title" }
  },
  "requirements": [ [ "crafting_table" ] ],
  "sends_telemetry_event": true
}
```

## Display

- `announce_to_chat` (default `true`) — announce completion in chat.
- `background` (root advancements only) — tiled background texture, referenced as `<namespace>:<path>`; file at `<namespace>/textures/<path>.png` in the resource pack, omitting `textures/` and `.png`.
- `description` — text component shown as the description in the advancement screen.
- `frame` (default `task`) — icon frame type: `challenge`, `goal`, or `task`.
- `hidden` (default `false`) — hide this advancement and all its children until it is completed. No effect on the root itself, but still affects its children.
- `icon` — an item stack used as the icon (item template).
- `show_toast` (default `true`) — show a toast notification on completion.
- `title` — text component shown as the title.

An advancement appears in the advancement screen only if: it is a root advancement, or its parent is shown, `display` is defined, and `hidden` is `false`.

## Tabs

A root advancement with `display` (no `parent`) automatically creates a tab at the edge of the advancement screen. When a player obtains any advancement in that root's tree, the root and its tab are revealed to that player; the tab icon matches the root icon. The root's `background` does not affect the tab. Children appear in the tab only if they define `display`.

## Layout

On data pack load, the game arranges advancements automatically and sends the layout to the client. Each advancement gets an arrow from the nearest visible ancestor (skipping ancestors without `display`). Roots sit in the leftmost column; every column is sorted by file name.

## Missing Display

Advancements without `display` (e.g. vanilla ones unlocked by recipes) are used purely for logic — triggers and rewards replace commands and functions, stay invisible to players, and load faster.

## Criteria

- `<criterion name>` — a criterion; names must be unique within the advancement.
  - `trigger` (required) — namespace ID of the trigger. Each trigger has its own triggering situation and checkable conditions.
  - `conditions` — conditions that must be met when the trigger fires; trigger-specific.
  - `player` — an entity predicate (or list of predicates) the player must match. Available for all triggers except `minecraft:impossible`.

## Triggers

All triggers require the player to be online — an offline player does not retroactively earn advancements after rejoining. The trigger IDs below are the full `minecraft:` trigger names; each has trigger-specific `conditions` summarized inline. For the complete condition schema of each trigger, see the Minecraft Wiki page "Advancement definition" or the vanilla files under `data/minecraft/advancement/` in the Minecraft source.

- `allay_drop_item_on_block` — when an Allay drops an item toward its chosen target block. Conditions: `location` (list of location predicates).
- `any_block_use` — any player–block interaction (including default interaction and non-empty-hand use). Conditions: `location`.
- `avoid_vibration` — the player creates a vibration that Sculk Sensors, Calibrated Sculk Sensors, or the Warden cannot detect because the player is sneaking.
- `bee_nest_destroyed` — the player destroys a bee nest or beehive. Conditions: `block` (only `minecraft:beehive`/`minecraft:bee_nest` can pass), `item` (item predicate), `num_bees_inside` (int bounds).
- `bred_animals` — two animals breed. Conditions: `child`, `parent`, `partner` (entity predicates).
- `brewed_potion` — the player takes a potion from a brewing stand. Conditions: `potion` (potion ID).
- `changed_dimension` — the player teleports to another dimension or respawns there. Conditions: `from`, `to` (dimension IDs such as `minecraft:overworld`, `minecraft:the_nether`, `minecraft:the_end`).
- `channeled_lightning` — lightning created by the Channeling enchantment. Conditions: `victims` (list of entity predicates; one entity per predicate).
- `construct_beacon` — a beacon activates (base changed; players within 10 Chebyshev blocks horizontally, 5 up, 9 down of the beacon center). Conditions: `level` (int bounds).
- `consume_item` — the player consumes an item carrying the `consumable` component. Conditions: `item`.
- `crafter_recipe_crafted` — the Crafter ejects an item as an entity (fires once per item). Conditions: `recipe_id` (required), `ingredients` (item predicates; each item matches only one predicate).
- `cured_zombie_villager` — a zombie villager is cured; fires for the player who fed the golden apple. Conditions: `villager`, `zombie` (entity predicates).
- `default_block_use` — non-sneaking block interaction. Conditions: `location`.
- `effects_changed` — the player gains or loses a status effect. Conditions: `effects` (mob effect predicate), `source` (entity predicate).
- `enchanted_item` — the player enchants an item at an enchanting table. Conditions: `item`, `levels` (int bounds; XP already deducted).
- `enter_block` — every game tick, per block intersecting the player's collision box; also when a thrown Ender Pearl enters an end gateway. Conditions: `block` (ID), `state` (block state properties with `min`/`max`).
- `entity_hurt_player` — the player takes or blocks damage (the source need not be an entity, e.g. lava). Conditions: `damage` (damage predicate).
- `entity_killed_player` — an entity kills the player. Conditions: `entity` (entity predicate), `killing_blow` (damage source predicate).
- `fall_after_explosion` — the player starts falling after being launched by an explosion or wind burst. Conditions: `start_position` (location predicate), `distance` (distance predicate), `cause` (entity predicate).
- `fall_from_height` — the player lands after a fall. Conditions: `start_position`, `distance`.
- `filled_bucket` — the player fills a bucket (not from a cauldron). Conditions: `item` (the filled bucket).
- `fishing_rod_hooked` — the player successfully fishes an item or pulls an entity. Conditions: `entity`, `item`, `rod` (item/entity predicates; absent `item` never passes).
- `hero_of_the_village` — after a raid victory, for every player who killed at least one raider (not in spectator mode).
- `impossible` — cannot trigger at all; grant only directly via `/advancement grant`.
- `inventory_changed` — the player's inventory changes. Conditions: `items` (item predicates on all added items), `slots` with `empty`/`full`/`occupied` (int bounds on slot counts).
- `item_durability_changed` — any item in the inventory takes damage. Conditions: `delta` (int bounds; negative = durability lost), `durability` (int bounds), `item` (predicate on the item *before* damage).
- `item_used_on_block` — the player uses an item (or empty hand) on a block. Conditions: `location`. (All triggering actions: MC-259075.)
- `kill_mob_near_sculk_catalyst` — when a Sculk Catalyst spreads from a dead mob, for the damage source player. Conditions: `entity`, `killing_blow`.
- `killed_by_arrow` — an arrow kills an entity; fires for the shooter. Conditions: `unique_entity_types` (int bounds), `fired_from_weapon` (item predicate), `victims` (entity predicates).
- `levitation` — every game tick while the player has Levitation. Conditions: `distance`, `duration` (int bounds, game ticks).
- `lightning_strike` — lightning disappears; fires for players within 256 blocks. Conditions: `lightning` (entity predicate), `bystander` (entities not struck, within 15 horizontal / 21 up / 15 down Chebyshev blocks).
- `location` — every 20 game ticks (1 second) for all players.
- `nether_travel` — the player enters the Nether and later returns to the Overworld. Conditions: `start_position` (last Overworld position before the trip), `distance`.
- `placed_block` — the player places a block item, water or lava, or uses flint and steel (fire charges do not trigger it). Conditions: `location`.
- `player_generates_container_loot` — the player interacts with a block/container/mob so that it generates loot from a loot table. Conditions: `loot_table` (required).
- `player_hurt_entity` — the player damages an entity (including itself). Conditions: `damage`, `entity`.
- `player_interacted_with_entity` — the player interacts with an entity. Conditions: `item`, `entity`.
- `player_killed_entity` — the player kills an entity. Conditions: `entity`, `killing_blow`.
- `player_sheared_equipment` — the player shears equipment off a mob. Conditions: `item` (sheared-off item), `entity`.
- `recipe_crafted` — the player crafts with a crafting table, furnace, blast furnace, smoker, stonecutter, inventory, or smithing table. Conditions: `recipe_id` (required), `ingredients`.
- `recipe_unlocked` — the player unlocks a recipe. Conditions: `recipe` (required).
- `ride_entity_in_lava` — every game tick while riding an entity standing in lava. Conditions: `start_position`, `distance`.
- `shot_crossbow` — the player fires a projectile with a crossbow. Conditions: `item` (the crossbow).
- `slept_in_bed` — the player sleeps in a bed.
- `slide_down_block` — the player slides down a honey block. Conditions: `block` (only `honey_block` can pass), `state` (honey blocks have no properties, so `state` checks nothing).
- `started_riding` — an entity gets mounted; fires for all players riding it.
- `summoned_entity` — structure-summoned Iron Golem / Snow Golem (within 5 Chebyshev blocks), Wither (50 blocks), or Ender Dragon respawn (within 192 blocks of `0,0,0` in the End). Conditions: `entity`.
- `spear_mobs` — the player performs a charge attack with any item. Conditions: `count` (minimum number of mobs hit in one attack).
- `tame_animal` — the player tames an animal. Conditions: `entity`.
- `target_hit` — the player shoots a target block. Conditions: `signal_strength` (int bounds), `projectile` (entity predicate).
- `thrown_item_picked_up_by_entity` — an entity picks up an item thrown by the player; fires for the thrower. Conditions: `item`, `entity`.
- `thrown_item_picked_up_by_player` — the player picks up an item thrown by an entity. Conditions: `item`, `entity`.
- `tick` — every game tick for all players.
- `used_ender_eye` — the player uses an Eye of Ender to locate a stronghold. Conditions: `distance` (double bounds; horizontal distance to the stronghold).
- `used_totem` — the player survives death with a Totem of Undying. Conditions: `item` (the consumed totem).
- `using_item` — every game tick while using a continuously-used item: bow, crossbow, honey bottle, milk bucket, potion, shield, spyglass, trident, food, eye of ender. Conditions: `item`.
- `villager_trade` — the player completes a trade. Conditions: `item` (bought item), `villager` (entity predicate; villager or wandering trader).
- `voluntary_exile` — the player triggers a new raid.

## Removed Triggers

- `arbitrary_player_tick` — fired for one player per game tick; no conditions. Removed.
- `item_delivered_to_player` — when an Allay throws an item to the player. Removed (superseded by `allay_drop_item_on_block`).
- `player_damaged` — when the player takes damage; `damage`. Removed (superseded by `entity_hurt_player`).
- `safely_harvest_honey` — harvesting honey from a campfire-lit bee nest/hive; `block`, `item`. Removed.
- `killed_by_crossbow` — crossbow kills; `unique_entity_types`, `victims`. Removed (superseded by `killed_by_arrow`).

## External Links

- [Advancement Generator](https://misode.github.io) on misode.github.io — visual advancement editor.

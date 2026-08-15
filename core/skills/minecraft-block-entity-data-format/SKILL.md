---

name: minecraft-block-entity-data-format
description: "Block entity NBT format — common tags, per-block-entity tags, chunk storage (keepPacked)."
whenToUse: "Use when reading or writing block entity NBT in commands, data packs, or save files."

---

# Block Entity Data Format

Block entities extend block states with extra behavior and data. Java Edition only.

## Common Tags

Every block entity shares:

- `x`, `y`, `z` (required) — block coordinates.
- `id` (required) — block entity type namespace ID.
- `components` — data components copied from the item used to place the block entity (only components the item carries that are not handled by inheritance serialization). See the data-component skill, "Block entities" section.

## Block Entity Data List

Per-block-entity tags (each includes the common tags above). See the Minecraft Wiki "Block entity format" page for complete details; `*` marks required tags.

- **Banner** — `CustomName` (text component; → component `custom_name`), `patterns` (default empty; list of `{color, pattern}` banner patterns; → `banner_patterns`).
- **Barrel** — container: `CustomName`, `lock` (item predicate), `Items` (27 slots; → `container`), `LootTable` + `LootTableSeed` (→ `container_loot`; removed after loot generates).
- **Beacon** — `Levels` (pyramid level, not modifiable via `/data`), `lock`, `CustomName`, `primary_effect`, `secondary_effect` (effect IDs).
- **Bed** — no extra tags.
- **Beehive** — `bees` (list of `{entity_data` (partial bee NBT; only `#beehive_inhabitors` entities load; many movement tags are not saved), `min_ticks_in_hive`, `ticks_in_hive`, `flower_pos`}; → `bees` component).
- **Bell** — no extra tags.
- **Blast Furnace / Furnace / Smoker** — smelting state: `CustomName`, `lock`, `Items` (slot 0 input, 1 fuel, 2 result), `cooking_time_spent`, `cooking_total_time`, `lit_time_remaining`, `lit_total_time`, `speed_multiplier` (default 1.0), `RecipesUsed` (recipe IDs → count).
- **Brewing Stand** — `BrewTime` (remaining, −1/tick), `Fuel` (energy; refills to 20 with blaze powder when <0), `Items` (slots 0–2 potions, 3 ingredient, 4 fuel), `CustomName`, `lock`.
- **Suspicious Sand / Suspicious Gravel** — `hit_direction` (0–5 = down/up/north/south/west/east; load/`/data` only), `item` (held item), `LootTable` + `LootTableSeed`.
- **Calibrated Sculk Sensor / Sculk Sensor** — `last_vibration_frequency` (analog output), `listener` (vibration listener data).
- **Campfire** — `CookingTimes`, `CookingTotalTimes` (4-element int arrays), `Items` (4 slots).
- **Chest / Trapped Chest / Ender Chest / Shulker Box** — container tags: `CustomName`, `lock`, `Items` (27 slots), `LootTable` + `LootTableSeed`.
- **Chiseled Bookshelf** — `Items` (6 slots, left-to-right top-to-bottom), `last_interacted_slot` (−1–5).
- **Command Block** — `auto` (always active), `Command`, `conditionMet`, `CustomName` (default "@"), `LastOutput` (when `TrackOutput`), `LastExecution` (when `UpdateLastExecution`), `powered`, `SuccessCount` (comparator output), `TrackOutput` (default true), `UpdateLastExecution` (default true).
- **Comparator** — `OutputSignal`.
- **Conduit** — `Target` (UUID int array of current target).
- **Copper Golem** — no extra tags; custom name of the golem comes from the `minecraft:custom_name` component.
- **Crafter** — container tags plus `crafting_ticks_remaining` (6 ticks after crafting, sets `crafting` block property), `disabled_slots` (int array), `triggered` (1 = true, synced with `triggered` property).
- **Creaking Heart** — `creaking` (UUID int array of bound Creaking).
- **Daylight Detector** — no extra tags.
- **Decorated Pot** — `item` (held item), `LootTable` + `LootTableSeed`, `sherds` (4 entries back/left/right/front; `minecraft:brick` default; → `pot_decorations`).
- **Dispenser / Dropper** — container tags (9 slots).
- **Enchanting Table** — `CustomName`.
- **End Gateway** — `Age` (beam control: <200 ticks magenta beam; divisible by 2400 → 40-tick teleport cooldown + purple beam), `ExactTeleport`, `exit_portal` ([x,y,z]).
- **End Portal** — no extra tags.
- **Hanging Sign / Sign** — `front_text` / `back_text` each with `messages` (4 text component lines), `color` (default black), `has_glowing_text`, `filtered_messages` (chat-filtered variants); `is_waxed` (text locked, commands still run).
- **Hopper** — container tags (5 slots) plus `TransferCooldown` (default −1; at 0 transfers and resets to 8 ticks).
- **Jigsaw Block** — `name` (default `minecraft:empty`), `final_state` (default `minecraft:air`), `joint` (`rollable`/`aligned`), `placement_priority`, `pool`, `target` (defaults `minecraft:empty`), `selection_priority`.
- **Jukebox** — `RecordItem` (music disc item), `ticks_since_song_started`.
- **Lectern** — `Book` (written book item), `Page` (0-based; out of range clamps).
- **Monster Spawner** — spawner common tags (spawn data, spawn range, delay, potentials...).
- **Moving Piston** — `blockState`, `extending`, `facing` (0–5 = down/up/north/south/west/east), `progress` (0–1), `source`.
- **Sculk Catalyst** — `cursors` (list of spread signals: `charge` 0–1000, `decay_delay` 0/1, `pos`, `update_delay`, `facings`).
- **Sculk Shrieker** — `listener` (vibration listener), `warning_level` (default 0; sets to the activating player's warning level).
- **Shelf** — `Items` (3 slots), `align_items_to_bottom` (default false; uses `on_shelf` display transform when true).
- **Skull** — `custom_name` (→ `custom_name` component), `note_block_sound` (→ `note_block_sound` component), `profile` (game profile; string form loads then converts; → `profile` component). Profile `textures` data is Base64-decoded JSON: `profileId`, `profileName`, `signatureRequired`, `textures` with `CAPE`/`SKIN` (`url`, optional `metadata.model` = `slim`), `timestamp`.
- **Structure Block** — `author`, `ignoreEntities` (default true), `integrity`, `metadata`, `mirror` (`NONE`/`LEFT_RIGHT`/`FRONT_BACK`), `mode` (`SAVE`/`LOAD`/`CORNER`/`DATA`), `name`, `posX/Y/Z` (−48–48, Y default 1), `powered`, `rotation` (`NONE`/`CLOCKWISE_90`/`CLOCKWISE_180`/`COUNTERCLOCKWISE_90`), `seed`, `sizeX/Y/Z` (0–48), `showair`, `showboundingbox` (default true), `strict`.
- **Test Block** — `message`, `mode` (invalid → `fail`), `powered`.
- **Test Instance Block** — `data` (instance data), `error_message` (only when `status` is `finished`), `ignore_entities`, `rotation`, `size` (int array), `status` (`cleared`/`running`/`finished`), `test` (test instance ID), `errors` (list of `{pos, text}` markers).
- **Trial Spawner** — `normal_config` / `ominous_config` (trial spawner config by ID or inline: `items_to_drop_when_ominous` (default `spawners/trial_chamber/items_to_drop_when_ominous`), `loot_tables_to_eject` (weighted list; defaults `spawners/trial_chamber/consumables` and `spawners/trial_chamber/key` at weight 1), `simultaneous_mobs` (default 2), `simultaneous_mobs_added_per_player` (default 1), `spawn_potentials` (weighted spawn data), `spawn_range` (Chebyshev, default 4), `total_mobs` (default 6), `total_mobs_added_per_player` (default 2), `ticks_between_spawn` (default 40)); plus `cooldown_ends_at`, `current_mobs` (UUIDs), `ejecting_loot_table`, `next_mob_spawns_at`, `registered_players` (UUIDs), `required_player_range` (Euclidean, default 14), `spawn_data`, `target_cooldown_length` (default 36000 ticks), `total_mobs_spawned`.
- **Vault** — `config`: `activation_range` (default 4), `deactivation_range` (default 4.5), `key_item` (default trial key; absent = unlockable), `loot_table` (default `chests/trial_chambers/reward`), `override_loot_table_to_display`; `server_data`: `items_to_eject`, `rewarded_players` (max 128), `state_updating_resumes_at`, `total_ejections_needed`; `shared_data` (client render): `connected_particles_range` (default 4.5), `connected_players` (UUIDs), `display_item`.

## Storage Format

All block entities are stored in the chunk's `block_entities` list. Storage format equals the data format plus:

- `keepPacked` (required) — true while the block entity is data-only and not yet added to the world (false for world-accessible ones).

During world generation, blocks with block entity data are written with `keepPacked: 1` and `id: "DUMMY"`; they are deserialized and added to the world when the prototype chunk converts to a world chunk (or when the position is accessed), after which `keepPacked` becomes false.

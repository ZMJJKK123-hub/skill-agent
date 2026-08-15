---
name: minecraft-chunk-format
description: Java Edition save format — locations, folder structure, dimension dirs, region files.
whenToUse: Use when locating or reading world save files (level.dat, region files, player data).
---

# Java Edition Save Format

A level is the game's persistent representation of a world. Java Edition only; Bedrock has its own save format. This page describes the current (26.1+) structure; see "Java Edition save format/1.21.11" for the pre-26.1 layout.

## Save Locations

- Client: every save is a directory under `.minecraft/saves/`; a directory counts as a save only if it contains `level.dat` or `level.dat_old`.
- Server: root = `u/w` where `u` is the `--universe` launch argument (default `.`, the working directory) and `w` is the `--world` argument or `level-name` from `server.properties`.

## Save Structure

Bold = always present (after initialization with at least one player joining); backups (`level.dat_old`, `session.lock` variants) not shown.

### Dimension-Independent Files (save root)

- `icon.png` — save icon.
- `level.dat` — base save data.
- `resourcepacks/` — world-specific resource pack directory; `resources.zip` — world-specific resource pack.
- `session.lock` — session lock file.
- `players/` — player data:
  - `advancements/<player UUID>.json` — advancements.
  - `data/<player UUID>.dat` — player data.
  - `stats/<player UUID>.json` — statistics.
- `data/` — save data:
  - `minecraft/` — data in the minecraft namespace:
    - `maps/` — `last_id.dat` (map counter) + `<map ID>.dat` (map data).
    - `command_storage.dat` — command storage.
    - `custom_boss_events.dat` — custom boss bars.
    - `game_rules.dat` — game rules.
    - `random_sequences.dat` — random sequences.
    - `scheduled_events.dat` — scheduled events (planned ticks).
    - `scoreboard.dat` — scoreboard.
    - `stopwatches.dat` — stopwatches.
    - `wandering_trader.dat` — wandering trader data.
    - `weather.dat` — weather data.
    - `world_clocks.dat` — world clocks.
    - `world_gen_settings.dat` — world generation settings.
  - `<namespace>/` — other namespaces (currently only command storage uses non-minecraft namespaces).
- `datapacks/` — world-specific data packs.
- `generated/<namespace>/structure/<name>.nbt` — generated structures (structure block exports).

### Dimension Directories

Relative to the save root: Overworld = the save root itself, Nether = `DIM-1`, End = `DIM1` (custom dimensions use their own folders). Each dimension directory:

- `data/minecraft/` — dimension data: `chunk_tickets.dat` (chunk tickets), `raids.dat`, `ender_dragon_fight.dat` (End only, or dimensions with a dragon fight; not auto-created elsewhere), `world_border.dat`.
- `entities/` — `r.<region X>.<region Z>.mca` region entity files (+ `c.<chunk X>.<chunk Z>.mcc` region extra files).
- `poi/` — point-of-interest data: `r.<region X>.<region Z>.mca` (+ `.mcc` extra files).
- `region/` — chunk data: `r.<region X>.<region Z>.mca` (+ `.mcc` extra files).

### Upgraded Saves

Older saves may additionally contain `level.dat_mcr` and `worldgen_settings_export.json` (world generation settings export).

## Storage History

- Alpha: each chunk stored in its own file.
- Beta 1.3: MCRegion format.
- 12w07a: Anvil file format — regions of 32×32 chunks in `.mca` files, still used today (`.mcc` extra files added later for region overflow data).

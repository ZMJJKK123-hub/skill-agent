---
name: minecraft-dimension-type
description: Dimension type definition JSON: DIMENSION_TYPE registry and all its fields.
whenToUse: Use when writing datapack dimension_type definitions or custom dimension behaviors.
---

# Dimension Types

This content applies only to Java Edition.

Dimension types control a dimension's environmental lighting, build height, and many other behaviors. Definition files are their data-driven definitions in datapacks.

## Definition format

Dimension types use the `DIMENSION_TYPE` registry; the datapack path is `dimension_type` (definitions in `data/<namespace>/dimension_type`, tags in `data/<namespace>/tags/dimension_type`).

Definition files use JSON with the following structure:

- JSON file root object
  - `has_fixed_time` (bool, default `false`): whether the dimension logically has day/night (see below).
  - `has_skylight` (bool, required): whether the dimension has skylight (see below).
  - `has_ceiling` (bool, required): whether the dimension has a ceiling (see below).
  - `has_ender_dragon_fight` (bool, required): whether the ender dragon fight can start.
  - `ambient_light` (float, required): ambient light (0–1 under vanilla shaders).
  - `coordinate_scale` (double, required): (0.00001≤v≤30000000.0) coordinate scaling, affects nether portal travel and `/execute in`.
  - `infiniburn` (string/list, required): blocks on which fire burns indefinitely (block ID, tag, or list).
  - `min_y` (int, required): (−2032≤v≤2031, multiple of 16) lowest buildable height.
  - `height` (int, required): (16≤v≤2032−min_y, multiple of 16) total buildable height.
  - `logical_height` (int, required): (0≤v≤height) max height for chorus fruit teleportation and generated nether portals.
  - `monster_spawn_block_light_limit` (int, required): (0≤v≤15) max block light for monster spawns.
  - `monster_spawn_light_level` (int/compound, required): (0≤v≤15) max light for monster spawns using internal sky light (sky −10 during thunderstorms); a range is sampled per spawn attempt (int provider).
  - `attributes` (compound): dimension environment attribute map; duplicate attributes use the last value.
  - `timelines` (string/list): active timelines (ID, tag, or list); duplicate timeline-defined attribute changes use the last.
  - `skybox` (string, default `overworld`): `none` / `end` (periodic end flashes using world clock time) / `overworld` (sun, moon, stars, day/night).
  - `cardinal_light` (string, default `default`): block lighting type `default` or `nether` (shade=false blocks get 10% less brightness on top/bottom instead of 0/50%; fluids and shade=true blocks get 10% less on all faces).
  - `default_clock` (string): (namespace ID) world clock used in this dimension; absent = no world clock.

## Definition behavior

Dimension type data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Inline dimension types in datapacks and `level.dat` are supported but dimensions using them cannot be loaded.

### Dimension behaviors

`has_fixed_time` does not control visual day/night; it disables day/night logic for some behaviors: sleeping at any game time, Drowned always hostile, wandering traders stop drinking invisibility potions/milk, patrols always spawn, endermen never increase random teleport chance, foxes never head to villages or sleep, zombie sieges always spawn, some undead stop avoiding sunlight.

`has_skylight` controls: skylight existence (daylight sensors), phantom spawning, and weather.

`has_ceiling` controls: initial animal spawn search, player spawn preference (Y=64 instead of highest block, except superflat), some map updates, and weather absence.

### Hardcoded behaviors

Players always spawn in the Overworld. Nether portals teleport with dimension scaling to/from the Nether; end portals to/from the End. Frosted ice melts by block light (not skylight) in the End. The End never has weather. Nether map player icons rotate randomly.

## Built-in dimension types

- `overworld`, `the_nether`, `the_end`, `overworld_caves` (unused directly; for legacy cave worlds).

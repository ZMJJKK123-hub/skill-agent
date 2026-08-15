---
name: minecraft-tag-structure
description: Structure tags and their members, used for locating structures, explorer maps, and related commands.
whenToUse: Use when querying or using structure tags for structure location.
---

# Structure Tags

This content applies only to Java Edition.

Structure tags are groups of generated structures.

## Usage

Structure tags are typically used for locating structures, such as explorer maps and the `/locate structure` command.

## Tag list

### `#abandoned_camp` (18 entries)

Contains all abandoned camps. Members are named after biomes, e.g.:

- `abandoned_camp_bamboo_jungle`
- `abandoned_camp_birch_forest`
- `abandoned_camp_cherry_grove`
- `abandoned_camp_taiga`
- `abandoned_camp_swamp`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#cats_spawn_as_black` (1 entry)

Black cats spawn in structures in this tag:

- `swamp_hut` (Swamp Hut)

### `#cats_spawn_in` (1 entry)

Cats spawn in structures in this tag:

- `swamp_hut` (Swamp Hut)

### `#dolphin_located` (2 entries)

Dolphins lead players toward structures in this tag after being fed raw cod or raw salmon:

- `#ocean_ruin`
- `#shipwreck`

### `#eye_of_ender_located` (1 entry)

Eyes of ender point toward the nearest structure in this tag:

- `stronghold` (Stronghold)

### `#mineshaft` (2 entries)

Contains all mineshafts:

- `mineshaft` (Mineshaft)
- `mineshaft_mesa` (Mineshaft)

### `#ocean_ruin` (2 entries)

Contains all ocean ruins:

- `ocean_ruin_cold` (Ocean Ruin)
- `ocean_ruin_warm` (Ocean Ruin)

### `#on_desert_village_maps` (1 entry)

Desert village maps point toward the nearest structure in this tag:

- `village_desert` (Desert Village)

### `#on_jungle_explorer_maps` (1 entry)

Jungle explorer maps point toward the nearest structure in this tag:

- `jungle_pyramid` (Jungle Pyramid)

### `#on_ocean_explorer_maps` (1 entry)

Ocean explorer maps point toward the nearest structure in this tag:

- `monument` (Ocean Monument)

### `#on_plains_village_maps` (1 entry)

Plains village maps point toward the nearest structure in this tag:

- `village_plains` (Plains Village)

### `#on_savanna_village_maps` (1 entry)

Savanna village maps point toward the nearest structure in this tag:

- `village_savanna` (Savanna Village)

### `#on_snowy_village_maps` (1 entry)

Snowy village maps point toward the nearest structure in this tag:

- `village_snowy` (Snowy Village)

### `#on_swamp_explorer_maps` (1 entry)

Swamp explorer maps point toward the nearest structure in this tag:

- `swamp_hut` (Swamp Hut)

### `#on_taiga_village_maps` (1 entry)

Taiga village maps point toward the nearest structure in this tag:

- `village_taiga` (Taiga Village)

### `#on_treasure_maps` (1 entry)

Treasure maps point toward the nearest structure in this tag:

- `buried_treasure` (Buried Treasure)

### `#on_trial_chambers_maps` (1 entry)

Trial explorer maps point toward the nearest structure in this tag:

- `trial_chambers` (Trial Chambers)

### `#on_woodland_explorer_maps` (1 entry)

Woodland explorer maps point toward the nearest structure in this tag:

- `mansion` (Woodland Mansion)

### `#ruined_portal` (7 entries)

Contains all ruined portals, e.g.:

- `ruined_portal_desert` (Ruined Portal)
- `ruined_portal_jungle` (Ruined Portal)
- `ruined_portal_nether` (Ruined Portal)
- `ruined_portal_ocean` (Ruined Portal)
- `ruined_portal` (Ruined Portal)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#shipwreck` (2 entries)

Contains all shipwrecks:

- `shipwreck` (Shipwreck)
- `shipwreck_beached` (Shipwreck)

### `#village` (5 entries)

Contains all villages:

- `village_plains` (Plains Village)
- `village_desert` (Desert Village)
- `village_savanna` (Savanna Village)
- `village_snowy` (Snowy Village)
- `village_taiga` (Taiga Village)

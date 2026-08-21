---

name: minecraft-tag-biome
description: "Biome tags controlling structure generation, mob spawning, and game mechanics. Includes #has_structure/* tags for structure generation (abandoned_camp, ancient_city, bastion_remnant, etc.), #is_* classification tags (is_badlands, is_beach, is_forest, etc.), spawning tags (#spawns_cold_variant_farm_animals, #spawns_warm_variant_frogs), and gameplay tags (#allows_surface_slime_spawns, #without_zombie_sieges)."
whenToUse: "Use when querying or using biome tags for structure generation or mob spawning."

---

# Biome Tags

This content applies only to Java Edition.

Biome tags are groups of biomes.

## Usage

Biome tags control structure generation, mob spawning, and many other functions. Commands such as `/locate biome` and `/execute if biome` can also reference biome tags.

## Tag list

### `#allows_surface_slime_spawns` (2 entries)

Slimes spawn in these biomes regardless of slime chunk restrictions, but are affected by the moon phase:

- `swamp` (Swamp)
- `mangrove_swamp` (Mangrove Swamp)

### `#allows_tropical_fish_spawns_at_any_height` (1 entry)

Tropical fish spawn in these biomes regardless of the height limit:

- `lush_caves` (Lush Caves)

### `#has_structure/abandoned_camp_*` (18 tags)

This section contains content from an upcoming update (Java Edition 26.3 development versions).

Biomes where each abandoned camp variant can generate; each tag has 1 member, the biome itself, e.g.:

- `has_structure/abandoned_camp_bamboo_jungle`: `bamboo_jungle` (Bamboo Jungle)
- `has_structure/abandoned_camp_birch_forest`: `birch_forest` (Birch Forest)
- `has_structure/abandoned_camp_cherry_grove`: `cherry_grove` (Cherry Grove)
- `has_structure/abandoned_camp_taiga`: `taiga` (Taiga)
- `has_structure/abandoned_camp_swamp`: `swamp` (Swamp)

For the complete list, see the tag definitions under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#has_structure/ancient_city` (1 entry)

Biomes where ancient cities can generate:

- `deep_dark` (Deep Dark)

### `#has_structure/bastion_remnant` (4 entries)

Biomes where bastion remnants can generate:

- `crimson_forest` (Crimson Forest)
- `nether_wastes` (Nether Wastes)
- `soul_sand_valley` (Soul Sand Valley)
- `warped_forest` (Warped Forest)

### `#has_structure/buried_treasure` (1 entry)

Biomes where buried treasure can generate:

- `#is_beach`

### `#has_structure/desert_pyramid` (1 entry)

Biomes where desert pyramids can generate:

- `desert` (Desert)

### `#has_structure/end_city` (2 entries)

Biomes where end cities can generate:

- `end_highlands` (End Highlands)
- `end_midlands` (End Midlands)

### `#has_structure/igloo` (3 entries)

Biomes where igloos can generate:

- `snowy_taiga` (Snowy Taiga)
- `snowy_plains` (Snowy Plains)
- `snowy_slopes` (Snowy Slopes)

### `#has_structure/jungle_temple` (2 entries)

Biomes where jungle temples can generate:

- `bamboo_jungle` (Bamboo Jungle)
- `jungle` (Jungle)

### `#has_structure/mineshaft` (23 entries)

Biomes where regular (underground) mineshafts can generate; members include multiple `#is_*` biome tag references and directly listed biomes, e.g.:

- `#is_ocean`
- `#is_river`
- `#is_taiga`
- `desert` (Desert)
- `dripstone_caves` (Dripstone Caves)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#has_structure/mineshaft_mesa` (1 entry)

Biomes where badlands-variant (surface) mineshafts can generate:

- `#is_badlands`

### `#has_structure/nether_fortress` (1 entry)

Biomes where nether fortresses can generate:

- `#is_nether`

### `#has_structure/nether_fossil` (1 entry)

Biomes where nether fossils can generate:

- `soul_sand_valley` (Soul Sand Valley)

### `#has_structure/ocean_monument` (1 entry)

Biomes where ocean monuments can generate:

- `#is_deep_ocean`

### `#has_structure/ocean_ruin_cold` (6 entries)

Biomes where cold-ocean-variant ocean ruins can generate:

- `frozen_ocean` (Frozen Ocean)
- `cold_ocean` (Cold Ocean)
- `ocean` (Ocean)
- `deep_frozen_ocean` (Deep Frozen Ocean)
- `deep_cold_ocean` (Deep Cold Ocean)
- `deep_ocean` (Deep Ocean)

### `#has_structure/ocean_ruin_warm` (3 entries)

Biomes where warm-ocean-variant ocean ruins can generate:

- `lukewarm_ocean` (Lukewarm Ocean)
- `warm_ocean` (Warm Ocean)
- `deep_lukewarm_ocean` (Deep Lukewarm Ocean)

### `#has_structure/pillager_outpost` (7 entries)

Biomes where pillager outposts can generate, e.g.:

- `desert` (Desert)
- `plains` (Plains)
- `savanna` (Savanna)
- `snowy_plains` (Snowy Plains)
- `taiga` (Taiga)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#has_structure/ruined_portal_desert` (1 entry)

Biomes where desert-variant ruined portals can generate:

- `desert` (Desert)

### `#has_structure/ruined_portal_jungle` (1 entry)

Biomes where jungle-variant ruined portals can generate:

- `#is_jungle`

### `#has_structure/ruined_portal_mountain` (6 entries)

Biomes where mountain-variant ruined portals can generate:

- `#is_badlands`
- `#is_hill`
- `savanna_plateau` (Savanna Plateau)
- `windswept_savanna` (Windswept Savanna)
- `stony_shore` (Stony Shore)
- `#is_mountain`

### `#has_structure/ruined_portal_nether` (1 entry)

Biomes where nether-variant ruined portals can generate:

- `#is_nether`

### `#has_structure/ruined_portal_ocean` (1 entry)

Biomes where ocean-variant ruined portals can generate:

- `#is_ocean`

### `#has_structure/ruined_portal_standard` (13 entries)

Biomes where regular ruined portals can generate, e.g.:

- `#is_beach`
- `#is_river`
- `#is_taiga`
- `#is_forest`
- `plains` (Plains)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#has_structure/ruined_portal_swamp` (2 entries)

Biomes where swamp-variant ruined portals can generate:

- `swamp` (Swamp)
- `mangrove_swamp` (Mangrove Swamp)

### `#has_structure/shipwreck` (1 entry)

Biomes where regular shipwrecks can generate:

- `#is_ocean`

### `#has_structure/shipwreck_beached` (1 entry)

Biomes where beached shipwrecks can generate:

- `#is_beach`

### `#has_structure/stronghold` (1 entry)

Biomes where strongholds can generate:

- `#is_overworld`

### `#has_structure/swamp_hut` (1 entry)

Biomes where swamp huts can generate:

- `swamp` (Swamp)

### `#has_structure/trail_ruins` (6 entries)

Biomes where trail ruins can generate:

- `taiga` (Taiga)
- `snowy_taiga` (Snowy Taiga)
- `old_growth_pine_taiga` (Old Growth Pine Taiga)
- `old_growth_spruce_taiga` (Old Growth Spruce Taiga)
- `old_growth_birch_forest` (Old Growth Birch Forest)
- `jungle` (Jungle)

### `#has_structure/trial_chambers` (55 entries)

Biomes where trial chambers can generate, e.g.:

- `mushroom_fields` (Mushroom Fields)
- `swamp` (Swamp)
- `plains` (Plains)
- `desert` (Desert)
- `dripstone_caves` (Dripstone Caves)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#has_structure/village_desert` (1 entry)

Biomes where desert-variant villages can generate:

- `desert` (Desert)

### `#has_structure/village_plains` (2 entries)

Biomes where plains-variant villages can generate:

- `plains` (Plains)
- `meadow` (Meadow)

### `#has_structure/village_savanna` (1 entry)

Biomes where savanna-variant villages can generate:

- `savanna` (Savanna)

### `#has_structure/village_snowy` (1 entry)

Biomes where snowy-variant villages can generate:

- `snowy_plains` (Snowy Plains)

### `#has_structure/village_taiga` (1 entry)

Biomes where taiga-variant villages can generate:

- `taiga` (Taiga)

### `#has_structure/woodland_mansion` (2 entries)

Biomes where woodland mansions can generate:

- `dark_forest` (Dark Forest)
- `pale_garden` (Pale Garden)

### `#is_badlands` (3 entries)

Badlands biomes. Wolves spawning in these biomes are striped:

- `badlands` (Badlands)
- `eroded_badlands` (Eroded Badlands)
- `wooded_badlands` (Wooded Badlands)

### `#is_beach` (2 entries)

Beach biomes:

- `beach` (Beach)
- `snowy_beach` (Snowy Beach)

### `#is_deep_ocean` (4 entries)

Deep ocean biomes:

- `deep_frozen_ocean` (Deep Frozen Ocean)
- `deep_cold_ocean` (Deep Cold Ocean)
- `deep_ocean` (Deep Ocean)
- `deep_lukewarm_ocean` (Deep Lukewarm Ocean)

### `#is_end` (5 entries)

End biomes:

- `the_end` (The End)
- `end_highlands` (End Highlands)
- `end_midlands` (End Midlands)
- `small_end_islands` (Small End Islands)
- `end_barrens` (End Barrens)

### `#is_forest` (8 entries)

Forest biomes, e.g.:

- `forest` (Forest)
- `flower_forest` (Flower Forest)
- `birch_forest` (Birch Forest)
- `old_growth_birch_forest` (Old Growth Birch Forest)
- `dappled_forest` (Dappled Forest)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#is_hill` (3 entries)

Windswept hill biomes:

- `windswept_hills` (Windswept Hills)
- `windswept_forest` (Windswept Forest)
- `windswept_gravelly_hills` (Windswept Gravelly Hills)

### `#is_jungle` (3 entries)

Jungle biomes. Wolves spawning in these biomes are chestnut:

- `bamboo_jungle` (Bamboo Jungle)
- `jungle` (Jungle)
- `sparse_jungle` (Sparse Jungle)

### `#is_mountain` (6 entries)

Mountain biomes:

- `meadow` (Meadow)
- `frozen_peaks` (Frozen Peaks)
- `jagged_peaks` (Jagged Peaks)
- `stony_peaks` (Stony Peaks)
- `snowy_slopes` (Snowy Slopes)
- `cherry_grove` (Cherry Grove)

### `#is_nether` (5 entries)

Nether biomes:

- `nether_wastes` (Nether Wastes)
- `soul_sand_valley` (Soul Sand Valley)
- `crimson_forest` (Crimson Forest)
- `warped_forest` (Warped Forest)
- `basalt_deltas` (Basalt Deltas)

### `#is_ocean` (6 entries)

Ocean biomes:

- `#is_deep_ocean`
- `frozen_ocean` (Frozen Ocean)
- `ocean` (Ocean)
- `cold_ocean` (Cold Ocean)
- `lukewarm_ocean` (Lukewarm Ocean)
- `warm_ocean` (Warm Ocean)

### `#is_overworld` (56 entries)

Overworld biomes, e.g.:

- `mushroom_fields` (Mushroom Fields)
- `ocean` (Ocean)
- `plains` (Plains)
- `desert` (Desert)
- `deep_dark` (Deep Dark)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#is_river` (2 entries)

River biomes:

- `river` (River)
- `frozen_river` (Frozen River)

### `#is_savanna` (3 entries)

Savanna biomes. Wolves spawning in these biomes are spotted:

- `savanna` (Savanna)
- `savanna_plateau` (Savanna Plateau)
- `windswept_savanna` (Windswept Savanna)

### `#is_taiga` (4 entries)

Taiga biomes:

- `taiga` (Taiga)
- `snowy_taiga` (Snowy Taiga)
- `old_growth_pine_taiga` (Old Growth Pine Taiga)
- `old_growth_spruce_taiga` (Old Growth Spruce Taiga)

### `#mineshaft_blocking` (1 entry)

Mineshaft generation is blocked in these biomes:

- `deep_dark` (Deep Dark)

### `#more_frequent_drowned_spawns` (1 entry)

Drowned spawning in these biomes is not subject to the Y<58 height limit:

- `#is_river`

### `#polar_bears_spawn_on_alternate_blocks` (2 entries)

Polar bears spawn on ice in these biomes:

- `frozen_ocean` (Frozen Ocean)
- `deep_frozen_ocean` (Deep Frozen Ocean)

### `#produces_corals_from_bonemeal` (1 entry)

Using bone meal on specific underwater blocks in these biomes can generate coral:

- `warm_ocean` (Warm Ocean)

### `#reduce_water_ambient_spawns` (1 entry)

Underwater ambient mobs spawn less frequently here:

- `#is_river`

### `#required_ocean_monument_surrounding` (2 entries)

Ocean monuments require all surrounding biomes to be in this tag:

- `#is_ocean`
- `#is_river`

### `#spawns_cold_variant_farm_animals` (23 entries)

Pigs, cows, and chickens spawn as cold variants in these biomes; sheep wool is more often black:

- `snowy_plains` (Snowy Plains)
- `frozen_ocean` (Frozen Ocean)
- `deep_dark` (Deep Dark)
- `taiga` (Taiga)
- `#is_end`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#spawns_cold_variant_frogs` (13 entries)

Frogs spawn with green skin in these biomes:

- `snowy_plains` (Snowy Plains)
- `frozen_ocean` (Frozen Ocean)
- `deep_dark` (Deep Dark)
- `snowy_taiga` (Snowy Taiga)
- `#is_end`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#spawns_coral_variant_zombie_nautilus` (1 entry)

Biomes where coral-variant zombie nautiluses can spawn:

- `warm_ocean` (Warm Ocean)

### `#spawns_gold_rabbits` (1 entry)

Rabbits spawn with golden fur in these biomes:

- `desert` (Desert)

### `#spawns_snow_foxes` (10 entries)

Foxes spawn with white fur in these biomes, e.g.:

- `snowy_plains` (Snowy Plains)
- `ice_spikes` (Ice Spikes)
- `frozen_ocean` (Frozen Ocean)
- `snowy_taiga` (Snowy Taiga)
- `grove` (Grove)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#spawns_warm_variant_farm_animals` (9 entries)

Pigs, cows, and chickens spawn as warm variants in these biomes; sheep wool is more often brown:

- `desert` (Desert)
- `warm_ocean` (Warm Ocean)
- `#is_jungle`
- `#is_savanna`
- `#is_nether`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#spawns_warm_variant_frogs` (7 entries)

Frogs spawn with white skin in these biomes:

- `desert` (Desert)
- `warm_ocean` (Warm Ocean)
- `#is_jungle`
- `#is_savanna`
- `#is_nether`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#spawns_white_rabbits` (10 entries)

Rabbits spawn with white fur in these biomes, e.g.:

- `snowy_plains` (Snowy Plains)
- `ice_spikes` (Ice Spikes)
- `frozen_ocean` (Frozen Ocean)
- `snowy_taiga` (Snowy Taiga)
- `grove` (Grove)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#stronghold_biased_to` (38 entries)

Biomes strongholds are biased toward:

- `plains` (Plains)
- `desert` (Desert)
- `forest` (Forest)
- `taiga` (Taiga)
- `meadow` (Meadow)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#water_on_map_outlines` (4 entries)

Biomes with this tag show as water on unexplored explorer maps:

- `#is_ocean`
- `#is_river`
- `swamp` (Swamp)
- `mangrove_swamp` (Mangrove Swamp)

### `#without_wandering_trader_spawns` (1 entry)

Wandering traders do not spawn in these biomes:

- `the_void` (The Void)

### `#without_zombie_sieges` (1 entry)

Zombie sieges do not occur in these biomes:

- `mushroom_fields` (Mushroom Fields)

## Removed tags

### `#has_closer_water_fog`

Added in 22w11a, removed in 25w42a. Underwater fog appears closer to the player in these biomes:

- `swamp`
- `mangrove_swamp`

### `#increased_fire_burnout`

Added in 23w03a, removed in 25w42a. Fire burns out faster in these biomes, e.g.:

- `bamboo_jungle`
- `mushroom_fields`
- `mangrove_swamp`
- `snowy_slopes`
- `frozen_peaks`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#plays_underwater_music`

Added in 22w11a, removed in 25w42a. Underwater music plays while the player is in these biomes:

- `#is_ocean`
- `#is_river`

### `#snow_golem_melts`

Added in 23w03a, removed in 25w42a. Snow golems melt in these biomes, e.g.:

- `badlands`
- `basalt_deltas`
- `crimson_forest`
- `desert`
- `nether_wastes`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#without_patrol_spawns`

Added in 22w11a, removed in 25w45a. Illager patrols do not spawn in these biomes:

- `mushroom_fields`

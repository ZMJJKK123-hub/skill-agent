---
name: minecraft-tag-villager-trade
description: Villager trade tags: purpose, naming, member structure.
whenToUse: Use when customizing villager trade offers by profession and level via villager trade tags.
---

# Villager Trade Tags

This content applies only to Java Edition.

Villager trade tags are groups of villager trades.

## Usage

Trade sets reference villager trade tags as the pool of all possible trade offers to draw from.

## Tag list

Tags are named `profession/level` (`level_1`–`level_5` = Novice to Master); members are concrete trade records (datapack paths such as `data/butcher/1/chicken_emerald`). Some tags reference others in the form `#common_smith/level_N`. For complete member lists, see the tag definitions under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#armorer/level_1` (5 entries)

Novice armorer trade offers:

- `#common_smith/level_1`
- `armorer/1/emerald_iron_leggings`
- `armorer/1/emerald_iron_boots`
- `armorer/1/emerald_iron_helmet`
- `armorer/1/emerald_iron_chestplate`

### `#armorer/level_2` (3 entries)

Apprentice armorer trade offers:

- `#common_smith/level_2`
- `armorer/2/emerald_chainmail_boots`
- `armorer/2/emerald_chainmail_leggings`

### `#armorer/level_3` (6 entries)

Journeyman armorer trade offers:

- `#common_smith/level_3`
- `armorer/3/lava_bucket_emerald`
- `armorer/3/emerald_chainmail_helmet`
- `armorer/3/emerald_chainmail_chestplate`
- `armorer/3/emerald_shield`
- `armorer/3/diamond_emerald`

### `#armorer/level_4` (3 entries)

Expert armorer trade offers:

- `#common_smith/level_4`
- `armorer/4/emerald_enchanted_diamond_leggings`
- `armorer/4/emerald_enchanted_diamond_boots`

### `#armorer/level_5` (3 entries)

Master armorer trade offers:

- `#common_smith/level_5`
- `armorer/5/emerald_enchanted_diamond_helmet`
- `armorer/5/emerald_enchanted_diamond_chestplate`

### `#butcher/level_1` (4 entries)

Novice butcher trade offers:

- `butcher/1/chicken_emerald`
- `butcher/1/porkchop_emerald`
- `butcher/1/rabbit_emerald`
- `butcher/1/emerald_rabbit_stew`

### `#butcher/level_2` (3 entries)

Apprentice butcher trade offers:

- `butcher/2/coal_emerald`
- `butcher/2/emerald_cooked_porkchop`
- `butcher/2/emerald_cooked_chicken`

### `#butcher/level_3` (2 entries)

Journeyman butcher trade offers:

- `butcher/3/mutton_emerald`
- `butcher/3/beef_emerald`

### `#butcher/level_4` (1 entry)

Expert butcher trade offers:

- `butcher/4/dried_kelp_block_emerald`

### `#butcher/level_5` (1 entry)

Master butcher trade offers:

- `butcher/5/sweet_berries_emerald`

### `#cartographer/level_1` (2 entries)

Novice cartographer trade offers:

- `cartographer/1/paper_emerald`
- `cartographer/1/emerald_map`

### `#cartographer/level_2` (8 entries)

Apprentice cartographer trade offers:

- `cartographer/2/glass_pane_emerald`
- `cartographer/2/emerald_and_compass_village_taiga_map`
- `cartographer/2/emerald_and_compass_explorer_swamp_map`
- `cartographer/2/emerald_and_compass_village_snowy_map`
- `cartographer/2/emerald_and_compass_village_savanna_map`
- `cartographer/2/emerald_and_compass_village_plains_map`
- `cartographer/2/emerald_and_compass_explorer_jungle_map`
- `cartographer/2/emerald_and_compass_village_desert_map`

### `#cartographer/level_3` (3 entries)

Journeyman cartographer trade offers:

- `cartographer/3/compass_emerald`
- `cartographer/3/emerald_and_compass_ocean_explorer_map`
- `cartographer/3/emerald_and_compass_trial_chamber_map`

### `#cartographer/level_4` (16 entries)

Expert cartographer trade offers (item frames and banners of many colors):

- `cartographer/4/emerald_item_frame`
- `cartographer/4/emerald_white_banner`
- `cartographer/4/emerald_orange_banner`
- `cartographer/4/emerald_magenta_banner`
- `cartographer/4/emerald_blue_banner`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#cartographer/level_5` (2 entries)

Master cartographer trade offers:

- `cartographer/5/emerald_globe_banner_pattern`
- `cartographer/5/emerald_and_compass_woodland_mansion_map`

### `#cleric/level_1` (2 entries)

Novice cleric trade offers:

- `cleric/1/rotten_flesh_emerald`
- `cleric/1/emerald_redstone`

### `#cleric/level_2` (2 entries)

Apprentice cleric trade offers:

- `cleric/2/gold_ingot_emerald`
- `cleric/2/emerald_lapis_lazuli`

### `#cleric/level_3` (2 entries)

Journeyman cleric trade offers:

- `cleric/3/rabbit_foot_emerald`
- `cleric/3/emerald_glowstone`

### `#cleric/level_4` (3 entries)

Expert cleric trade offers:

- `cleric/4/turtle_scute_emerald`
- `cleric/4/glass_bottle_emerald`
- `cleric/4/emerald_ender_pearl`

### `#cleric/level_5` (2 entries)

Master cleric trade offers:

- `cleric/5/nether_wart_emerald`
- `cleric/5/emerald_experience_bottle`

### `#common_smith/level_1` (1 entry)

Common trade offers for novice smiths (toolsmith, armorer, weaponsmith):

- `smith/1/coal_emerald`

### `#common_smith/level_2` (2 entries)

Common trade offers for apprentice smiths:

- `smith/2/iron_ingot_emerald`
- `smith/2/emerald_bell`

### `#common_smith/level_3` (0 entries)

Common trade offers for journeyman smiths. No content.

### `#common_smith/level_4` (0 entries)

Common trade offers for expert smiths. No content.

### `#common_smith/level_5` (0 entries)

Common trade offers for master smiths. No content.

### `#farmer/level_1` (5 entries)

Novice farmer trade offers:

- `farmer/1/wheat_emerald`
- `farmer/1/potato_emerald`
- `farmer/1/carrot_emerald`
- `farmer/1/beetroot_emerald`
- `farmer/1/emerald_bread`

### `#farmer/level_2` (3 entries)

Apprentice farmer trade offers:

- `farmer/2/pumpkin_emerald`
- `farmer/2/emerald_pumpkin_pie`
- `farmer/2/emerald_apple`

### `#farmer/level_3` (2 entries)

Journeyman farmer trade offers:

- `farmer/3/emerald_cookie`
- `farmer/3/melon_emerald`

### `#farmer/level_4` (2 entries)

Expert farmer trade offers:

- `farmer/4/emerald_cake`
- `farmer/4/emerald_suspicious_stew`

### `#farmer/level_5` (2 entries)

Master farmer trade offers:

- `farmer/5/emerald_golden_carrot`
- `farmer/5/emerald_glistening_melon_slice`

### `#fisherman/level_1` (4 entries)

Novice fisherman trade offers:

- `fisherman/1/string_emerald`
- `fisherman/1/coal_emerald`
- `fisherman/1/raw_cod_and_emerald_cooked_cod`
- `fisherman/1/emerald_cod_bucket`

### `#fisherman/level_2` (3 entries)

Apprentice fisherman trade offers:

- `fisherman/2/cod_emerald`
- `fisherman/2/salmon_and_emerald_cooked_salmon`
- `fisherman/2/emerald_campfire`

### `#fisherman/level_3` (2 entries)

Journeyman fisherman trade offers:

- `fisherman/3/salmon_emerald`
- `fisherman/3/emerald_enchanted_fishing_rod`

### `#fisherman/level_4` (1 entry)

Expert fisherman trade offers:

- `fisherman/4/tropical_fish_emerald`

### `#fisherman/level_5` (6 entries)

Master fisherman trade offers:

- `fisherman/5/pufferfish_emerald`
- `fisherman/5/oak_boat_emerald`
- `fisherman/5/spruce_boat_emerald`
- `fisherman/5/jungle_boat_emerald`
- `fisherman/5/acacia_boat_emerald`
- `fisherman/5/dark_oak_boat_emerald`

### `#fletcher/level_1` (3 entries)

Novice fletcher trade offers:

- `fletcher/1/stick_emerald`
- `fletcher/1/emerald_arrow`
- `fletcher/1/gravel_and_emerald_flint`

### `#fletcher/level_2` (2 entries)

Apprentice fletcher trade offers:

- `fletcher/2/flint_emerald`
- `fletcher/2/emerald_bow`

### `#fletcher/level_3` (2 entries)

Journeyman fletcher trade offers:

- `fletcher/3/string_emerald`
- `fletcher/3/emerald_crossbow`

### `#fletcher/level_4` (2 entries)

Expert fletcher trade offers:

- `fletcher/4/feather_emerald`
- `fletcher/4/emerald_enchanted_bow`

### `#fletcher/level_5` (3 entries)

Master fletcher trade offers:

- `fletcher/5/tripwire_hook_emerald`
- `fletcher/5/emerald_enchanted_crossbow`
- `fletcher/5/arrow_and_emerald_tipped_arrow`

### `#leatherworker/level_1` (3 entries)

Novice leatherworker trade offers:

- `leatherworker/1/leather_emerald`
- `leatherworker/1/emerald_dyed_leather_leggings`
- `leatherworker/1/emerald_dyed_leather_chestplate`

### `#leatherworker/level_2` (3 entries)

Apprentice leatherworker trade offers:

- `leatherworker/2/flint_emerald`
- `leatherworker/2/emerald_dyed_leather_helmet`
- `leatherworker/2/emerald_dyed_leather_boots`

### `#leatherworker/level_3` (2 entries)

Journeyman leatherworker trade offers:

- `leatherworker/3/rabbit_hide_emerald`
- `leatherworker/3/emerald_dyed_leather_chestplate`

### `#leatherworker/level_4` (2 entries)

Expert leatherworker trade offers:

- `leatherworker/4/turtle_scute_emerald`
- `leatherworker/4/emerald_dyed_leather_horse_armor`

### `#leatherworker/level_5` (2 entries)

Master leatherworker trade offers:

- `leatherworker/5/emerald_saddle`
- `leatherworker/5/emerald_dyed_leather_helmet`

### `#librarian/level_1` (3 entries)

Novice librarian trade offers:

- `librarian/1/paper_emerald`
- `librarian/1/emerald_and_book_enchanted_book`
- `librarian/1/emerald_bookshelf`

### `#librarian/level_2` (3 entries)

Apprentice librarian trade offers:

- `librarian/2/book_emerald`
- `librarian/2/emerald_and_book_enchanted_book`
- `librarian/2/emerald_lantern`

### `#librarian/level_3` (3 entries)

Journeyman librarian trade offers:

- `librarian/3/ink_sac_emerald`
- `librarian/3/emerald_and_book_enchanted_book`
- `librarian/3/emerald_glass`

### `#librarian/level_4` (4 entries)

Expert librarian trade offers:

- `librarian/4/writable_book_emerald`
- `librarian/4/emerald_book_and_enchanted_book`
- `librarian/4/emerald_clock`
- `librarian/4/emerald_compass`

### `#librarian/level_5` (2 entries)

Master librarian trade offers:

- `librarian/5/emerald_yellow_candle`
- `librarian/5/emerald_red_candle`

### `#mason/level_1` (2 entries)

Novice mason trade offers:

- `mason/1/clay_ball_emerald`
- `mason/1/emerald_brick`

### `#mason/level_2` (2 entries)

Apprentice mason trade offers:

- `mason/2/stone_emerald`
- `mason/2/emerald_chiseled_stone_bricks`

### `#mason/level_3` (7 entries)

Journeyman mason trade offers:

- `mason/3/granite_emerald`
- `mason/3/andesite_emerald`
- `mason/3/diorite_emerald`
- `mason/3/emerald_dripstone_block`
- `mason/3/emerald_polished_andesite`
- `mason/3/emerald_polished_diorite`
- `mason/3/emerald_polished_granite`

### `#mason/level_4` (33 entries)

Expert mason trade offers (16 terracotta and 16 glazed terracotta colors):

- `mason/4/quartz_emerald`
- `mason/4/emerald_white_terracotta`
- `mason/4/emerald_orange_terracotta`
- `mason/4/emerald_white_glazed_terracotta`
- `mason/4/emerald_black_glazed_terracotta`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#mason/level_5` (2 entries)

Master mason trade offers:

- `mason/5/emerald_quartz_pillar`
- `mason/5/emerald_quartz_block`

### `#shepherd/level_1` (5 entries)

Novice shepherd trade offers:

- `shepherd/1/white_wool_emerald`
- `shepherd/1/brown_wool_emerald`
- `shepherd/1/gray_wool_emerald`
- `shepherd/1/black_wool_emerald`
- `shepherd/1/emerald_shears`

### `#shepherd/level_2` (37 entries)

Apprentice shepherd trade offers (5 dyes, wool and carpet in 16 colors each):

- `shepherd/2/white_dye_emerald`
- `shepherd/2/gray_dye_emerald`
- `shepherd/2/emerald_white_wool`
- `shepherd/2/emerald_orange_wool`
- `shepherd/2/emerald_white_carpet`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#shepherd/level_3` (21 entries)

Journeyman shepherd trade offers (5 dyes and beds in 16 colors):

- `shepherd/3/yellow_dye_emerald`
- `shepherd/3/light_gray_dye_emerald`
- `shepherd/3/emerald_white_bed`
- `shepherd/3/emerald_orange_bed`
- `shepherd/3/emerald_black_bed`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#shepherd/level_4` (22 entries)

Expert shepherd trade offers (6 dyes and banners in 16 colors):

- `shepherd/4/brown_dye_emerald`
- `shepherd/4/purple_dye_emerald`
- `shepherd/4/emerald_white_banner`
- `shepherd/4/emerald_orange_banner`
- `shepherd/4/emerald_black_banner`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#shepherd/level_5` (1 entry)

Master shepherd trade offers:

- `shepherd/5/emerald_painting`

### `#toolsmith/level_1` (5 entries)

Novice toolsmith trade offers:

- `#common_smith/level_1`
- `toolsmith/1/emerald_stone_axe`
- `toolsmith/1/emerald_stone_shovel`
- `toolsmith/1/emerald_stone_pickaxe`
- `toolsmith/1/emerald_stone_hoe`

### `#toolsmith/level_2` (1 entry)

Apprentice toolsmith trade offers:

- `#common_smith/level_2`

### `#toolsmith/level_3` (6 entries)

Journeyman toolsmith trade offers:

- `#common_smith/level_3`
- `toolsmith/3/flint_emerald`
- `toolsmith/3/emerald_enchanted_iron_axe`
- `toolsmith/3/emerald_enchanted_iron_shovel`
- `toolsmith/3/emerald_enchanted_iron_pickaxe`
- `toolsmith/3/emerald_diamond_hoe`

### `#toolsmith/level_4` (4 entries)

Expert toolsmith trade offers:

- `#common_smith/level_4`
- `toolsmith/4/emerald_enchanted_diamond_axe`
- `toolsmith/4/emerald_enchanted_diamond_shovel`
- `toolsmith/4/diamond_emerald`

### `#toolsmith/level_5` (2 entries)

Master toolsmith trade offers:

- `#common_smith/level_5`
- `toolsmith/5/emerald_enchanted_diamond_pickaxe`

### `#weaponsmith/level_1` (3 entries)

Novice weaponsmith trade offers:

- `#common_smith/level_1`
- `weaponsmith/1/emerald_iron_axe`
- `weaponsmith/1/emerald_enchanted_iron_sword`

### `#weaponsmith/level_2` (1 entry)

Apprentice weaponsmith trade offers:

- `#common_smith/level_2`

### `#weaponsmith/level_3` (2 entries)

Journeyman weaponsmith trade offers:

- `#common_smith/level_3`
- `weaponsmith/3/flint_emerald`

### `#weaponsmith/level_4` (3 entries)

Expert weaponsmith trade offers:

- `#common_smith/level_4`
- `weaponsmith/4/emerald_enchanted_diamond_axe`
- `weaponsmith/4/diamond_emerald`

### `#weaponsmith/level_5` (2 entries)

Master weaponsmith trade offers:

- `#common_smith/level_5`
- `weaponsmith/5/emerald_enchanted_diamond_sword`

### `#wandering_trader/buying` (6 entries)

Wandering trader buying offers:

- `wandering_trader/water_bottle_emerald`
- `wandering_trader/water_bucket_emerald`
- `wandering_trader/milk_bucket_emerald`
- `wandering_trader/fermented_spider_eye_emerald`
- `wandering_trader/baked_potato_emerald`
- `wandering_trader/hay_block_emerald`

### `#wandering_trader/common` (78 entries)

Wandering trader common selling offers (16 dyes, various fish buckets, plants, seeds, etc.):

- `wandering_trader/emerald_white_dye`
- `wandering_trader/emerald_orange_dye`
- `wandering_trader/emerald_fish_bucket`
- `wandering_trader/emerald_nautilus_shell`
- `wandering_trader/emerald_glowstone`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#wandering_trader/uncommon` (16 entries)

Wandering trader uncommon selling offers (logs, enchanted iron pickaxe, potion of invisibility, etc.):

- `wandering_trader/emerald_packed_ice`
- `wandering_trader/emerald_blue_ice`
- `wandering_trader/emerald_gunpowder`
- `wandering_trader/emerald_podzol`
- `wandering_trader/emerald_acacia_log`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

## Villager trade balancing

This section contains experimental content: these features require the "villager trade rebalancing" option to be enabled. The following tags override the same-named tags above.

### `#armorer/level_1` (2 entries)

Novice armorer trade offers; overrides the same-named tag:

- `smith/1/coal_emerald`
- `armorer/1/iron_ingot_emerald`

### `#armorer/level_2` (8 entries)

Apprentice armorer trade offers; overrides the same-named tag:

- `armorer/2/emerald_enchanted_iron_boots_group_1`
- `armorer/2/emerald_enchanted_iron_chestplate_group_1`
- `armorer/2/emerald_enchanted_iron_leggings_group_1`
- `armorer/2/emerald_enchanted_iron_helmet_group_1`
- `armorer/2/emerald_enchanted_chainmail_helmet_group_2`
- `armorer/2/emerald_enchanted_chainmail_boots_group_2`
- `armorer/2/emerald_enchanted_chainmail_chainmail_group_2`
- `armorer/2/emerald_enchanted_chainmail_leggings_group_2`

### `#armorer/level_3` (3 entries)

Journeyman armorer trade offers; overrides the same-named tag:

- `armorer/3/lava_bucket_emerald`
- `armorer/3/emerald_shield`
- `armorer/3/emerald_bell`

### `#armorer/level_4` (26 entries)

Expert armorer trade offers; overrides the same-named tag. Enchanted iron/chainmail/diamond equipment trades divided by biome (desert, plains, savanna, snow, jungle, swamp, taiga, etc.):

- `armorer/4/emerald_enchanted_iron_boots_desert`
- `armorer/4/emerald_enchanted_iron_helmet_plains`
- `armorer/4/emerald_enchanted_chainmail_boots_jungle`
- `armorer/4/emerald_enchanted_chainmail_helmet_swamp`
- `armorer/4/emerald_and_diamond_helmet_diamond_boots_taiga`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#armorer/level_5` (16 entries)

Master armorer trade offers; overrides the same-named tag. Diamond/chainmail equipment trades divided by biome:

- `armorer/5/emerald_and_diamond_diamond_chestplate_desert`
- `armorer/5/emerald_and_diamond_diamond_boots_plains`
- `armorer/5/emerald_and_diamond_diamond_helmet_savanna`
- `armorer/5/emerald_and_diamond_diamond_boots_snow`
- `armorer/5/emerald_chainmail_helmet_jungle`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#librarian/level_1` (9 entries)

Novice librarian trade offers; overrides the same-named tag:

- `librarian/1/paper_emerald`
- `librarian/1/emerald_bookshelf`
- `librarian/1/emerald_and_book_desert_enchanted_book`
- `librarian/1/emerald_and_book_jungle_enchanted_book`
- `librarian/1/emerald_and_book_plains_enchanted_book`
- `librarian/1/emerald_and_book_savanna_enchanted_book`
- `librarian/1/emerald_and_book_snow_enchanted_book`
- `librarian/1/emerald_and_book_swamp_enchanted_book`
- `librarian/1/emerald_and_book_taiga_enchanted_book`

### `#librarian/level_2` (9 entries)

Apprentice librarian trade offers; overrides the same-named tag:

- `librarian/2/book_emerald`
- `librarian/2/emerald_lantern`
- `librarian/2/emerald_and_book_desert_enchanted_book`
- `librarian/2/emerald_and_book_jungle_enchanted_book`
- `librarian/2/emerald_and_book_plains_enchanted_book`
- `librarian/2/emerald_and_book_savanna_enchanted_book`
- `librarian/2/emerald_and_book_snow_enchanted_book`
- `librarian/2/emerald_and_book_swamp_enchanted_book`
- `librarian/2/emerald_and_book_taiga_enchanted_book`

### `#librarian/level_3` (9 entries)

Journeyman librarian trade offers; overrides the same-named tag:

- `librarian/3/ink_sac_emerald`
- `librarian/3/emerald_glass`
- `librarian/3/emerald_and_book_desert_enchanted_book`
- `librarian/3/emerald_and_book_jungle_enchanted_book`
- `librarian/3/emerald_and_book_plains_enchanted_book`
- `librarian/3/emerald_and_book_savanna_enchanted_book`
- `librarian/3/emerald_and_book_snow_enchanted_book`
- `librarian/3/emerald_and_book_swamp_enchanted_book`
- `librarian/3/emerald_and_book_taiga_enchanted_book`

### `#librarian/level_4` (3 entries)

Expert librarian trade offers; overrides the same-named tag:

- `librarian/4/writable_book_emerald`
- `librarian/4/emerald_clock`
- `librarian/4/emerald_compass`

### `#librarian/level_5` (9 entries)

Master librarian trade offers; overrides the same-named tag:

- `librarian/5/emerald_yellow_candle`
- `librarian/5/emerald_red_candle`
- `librarian/5/emerald_and_book_desert_enchanted_book`
- `librarian/5/emerald_and_book_jungle_enchanted_book`
- `librarian/5/emerald_and_book_plains_enchanted_book`
- `librarian/5/emerald_and_book_savanna_enchanted_book`
- `librarian/5/emerald_and_book_snow_enchanted_book`
- `librarian/5/emerald_and_book_swamp_enchanted_book`
- `librarian/5/emerald_and_book_taiga_enchanted_book`

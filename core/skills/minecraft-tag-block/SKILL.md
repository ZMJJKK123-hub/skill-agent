---

name: minecraft-tag-block
description: "Java Edition block tags: 305 tags including #mineable/* (axe/pickaxe/shovel/hoe), #needs_*_tool, #climbable, #beds, #doors, #fences, #logs, #wool, #copper, #concrete, #terracotta, #glazed_terracotta, #ores, #supports_* vegetation tags, and many more controlling game mechanics like mob spawning, block interactions, and world generation."
whenToUse: "Use when querying or writing block tags, or understanding which game behavior a block group controls."

---

# Block Tags

This content applies only to Java Edition.

Block tags are groups of blocks. They are used by advancements, world generation, commands that test blocks, and many game behaviors — a test succeeds if the block is in the tag.

## Tag list (305 tags)

For every tag, the purpose and representative members are listed. **For the complete member list of any tag, see the JSON definition under `data/minecraft/tags/block/` in mc_java_sources/, or Minecraft Wiki.**

### `#acacia_logs` (4)
For `#logs_that_burn`. Members: `acacia_log`, `acacia_wood`, `stripped_acacia_log`, `stripped_acacia_wood`

### `#air` (3)
Used by the Frost Walker enchantment to detect air above water. Members: `air`, `void_air`, `cave_air`

### `#all_hanging_signs` (2)
For `#all_signs`. Members: `#ceiling_hanging_signs`, `#wall_hanging_signs`

### `#all_signs` (2)
Members: `#signs`, `#all_hanging_signs`

### `#ancient_city_replaceable` (12)
Determines which blocks ancient cities can replace when generating. Members: `deepslate`, `deepslate_bricks`, `deepslate_tiles`, `deepslate_brick_slab`…

### `#animals_spawnable_on` (1)
Used for animal spawning checks. Members: `grass_block`

### `#anvil` (3)
Determines which blocks can open the anvil GUI; whether falling block variants of the block hurt entities; whether the block "breaks" when used or landed on; reads NBT from falling block entities to set `hurtEntities`; whether the block can be damaged through the anvil GUI. Members: `anvil`, `chipped_anvil`, `damaged_anvil`

### `#armadillo_spawnable_on` (4)
Armadillos can spawn naturally on these blocks. Members: `#animals_spawnable_on`, `#badlands_terracotta`, `red_sand`, `coarse_dirt`

### `#axolotls_spawnable_on` (1)
Used for axolotl spawning checks. Members: `clay`

### `#azalea_grows_on` (5)
Determines where azalea trees can generate and which blocks the rooted dirt below can replace. Members: `#substrate_overworld`, `#sand`, `#terracotta`, `snow_block`…

### `#azalea_root_replaceable` (9)
Determines which blocks the large rooted-dirt and hanging-root clusters of azalea trees can replace. Members: `#base_stone_overworld`, `#substrate_overworld`, `#terracotta`, `red_sand`…

### `#badlands_terracotta` (7)
Determines which terracotta armadillos can spawn on. Members: `terracotta`, `white_terracotta`, `yellow_terracotta`, `orange_terracotta`…

### `#bamboo_blocks` (2)
Members: `bamboo_block`, `stripped_bamboo_block`

### `#banners` (32)
Determines whether clicking the block with a map marks the point on the map; adding other blocks causes the use animation but no marker; also for `#wall_post_override`. Members: `white_banner`, `orange_banner`, `black_banner`, `white_wall_banner`…

### `#bars` (9)
Contains all bars. Members: `iron_bars`, `copper_bars`, `exposed_copper_bars`, `weathered_copper_bars`…

### `#base_stone_nether` (3)
Blocks in this tag can be replaced by ancient debris when generating. Members: `netherrack`, `basalt`, `blackstone`

### `#base_stone_overworld` (6)
Determines which blocks dirt, gravel, granite, diorite, andesite, tuff, and clay can replace as underground ores; which blocks dripstone clusters replace; for `#dripstone_replaceable_blocks` and `#moss_replaceable`. Members: `stone`, `granite`, `diorite`, `andesite`…

### `#bats_spawnable_on` (1)
Used for bat spawning checks. Members: `#base_stone_overworld`

### `#beacon_base_blocks` (5)
Blocks in this tag activate a beacon when placed underneath it. Members: `netherite_block`, `emerald_block`, `diamond_block`, `gold_block`…

### `#beds` (16)
Determines where cats sit/lie down; villager POI detection; which blocks can be slept in; which blocks baby villagers can jump onto. Adding a block without front/back halves may crash the game. Members: `white_bed`, `orange_bed`, `magenta_bed`, `light_blue_bed`…

### `#bee_attractive` (29)
Bees try to pollinate these blocks. Members: `dandelion`, `poppy`, `blue_orchid`, `sunflower`…

### `#bee_growables` (4)
These plants grow one stage when pollinated by bees; removing blocks from this tag has no effect. Members: `#crops`, `sweet_berry_bush`, `cave_vines`, `cave_vines_plant`

### `#beehives` (2)
Determines which blocks bees fill with honey when carrying pollen; dispensers with glass bottles or shears can collect honey from these blocks; used by the husbandry/safely_harvest_honey.json advancement. Members: `bee_nest`, `beehive`

### `#beneath_bamboo_podzol_replaceable` (1)
Blocks replaceable by podzol beneath bamboo. Members: `#substrate_overworld`

### `#beneath_tree_podzol_replaceable` (1)
Blocks replaceable by podzol beneath trees. Members: `#substrate_overworld`

### `#birch_logs` (4)
For `#logs_that_burn`. Members: `birch_log`, `birch_wood`, `stripped_birch_log`, `stripped_birch_wood`

### `#blocks_dolphin_jump`
(Upcoming content, Java Edition 26.3.) Dolphins treat these blocks as blocking when leaping out of water. Members: `#blocks_motion`

### `#blocks_fluid_flow`
(Upcoming content, Java Edition 26.3.) Blocks that stop fluid flow. Members: `#blocks_motion`, `#all_signs`

### `#blocks_lava_fire_spread`
(Upcoming content, Java Edition 26.3.) Blocks that prevent lava from creating fire. Members: `#blocks_motion`

### `#blocks_motion`
(Upcoming content, Java Edition 26.3.) All blocks considered to block movement. Members: `#blocks_motion_no_leaves`, `#leaves`

### `#blocks_motion_in_heightmap`
(Upcoming content, Java Edition 26.3.) Used for the `MOTION_BLOCKING` heightmap. Members: `#blocks_motion`

### `#blocks_motion_in_heightmap_no_leaves`
(Upcoming content, Java Edition 26.3.) Used for the `MOTION_BLOCKING_NO_LEAVES` heightmap. Members: `#blocks_motion_no_leaves`

### `#blocks_motion_no_leaves` (340)
(Upcoming content, Java Edition 26.3.) Members: `#all_hanging_signs`, `#chains`, `#banners`, `#shulker_boxes`…

### `#blocks_wind_charge_explosions` (2)
Blocks that block wind charge explosions. Members: `barrier`, `bedrock`

### `#buttons` (2)
Members: `#wooden_buttons`, `#stone_buttons`

### `#camel_sand_step_sound_blocks` (2)
Camels play the sand step sound when walking on these blocks. Members: `#sand`, `#concrete_powders`

### `#camels_spawnable_on` (1)
Specifies which blocks camels can spawn on. Members: `#sand`

### `#campfires` (2)
Bees, parrots, and turtles pathfind around these as fire damage; campfires use this tag to determine if lit; flint and steel uses it to light campfires. Adding blocks has no effect; blocks with a `lit` state get it set to false when hit by splash water bottles. Members: `campfire`, `soul_campfire`

### `#candle_cakes` (17)
Blocks in this tag are treated as candle cakes and can be lit unless their `lit` state is false. Members: `candle_cake`, `white_candle_cake`, `orange_candle_cake`, `magenta_candle_cake`…

### `#candles` (17)
Blocks in this tag are treated as candles and can be lit if both `lit` and `waterlogged` states are false. Members: `candle`, `white_candle`, `orange_candle`, `magenta_candle`…

### `#cannot_place_basalt_pillar_on` (10)
(Upcoming content, Java Edition 26.3.) Members: `lava`, `bedrock`, `magma_block`, `soul_sand`…

### `#cannot_replace_below_tree_trunk` (4)
Members: `#dirt`, `#mud`, `#moss_blocks`, `podzol`

### `#cannot_support_kelp` (1)
Kelp cannot be placed on these blocks. Members: `magma_block`

### `#cannot_support_seagrass` (1)
Seagrass and tall seagrass cannot be placed on these blocks. Members: `magma_block`

### `#cannot_support_snow_layer` (3)
Snow cannot be placed on these blocks. Members: `ice`, `packed_ice`, `barrier`

### `#can_glide_through` (6)
Blocks that can be climbed without interrupting gliding. Members: `vine`, `twisting_vines`, `twisting_vines_plant`, `weeping_vines`…

### `#cats_can_lie_on`
(Upcoming content, Java Edition 26.3.) Blocks cats can lie on. Members: `#beds`

### `#cats_can_sit_on`
(Upcoming content, Java Edition 26.3.) Blocks cats can sit on. Members: `furnace`, `chest`, `#beds`

### `#cauldrons` (4)
Used to confirm pathfinding. Members: `cauldron`, `water_cauldron`, `lava_cauldron`, `powder_snow_cauldron`

### `#causes_continuous_geyser_eruptions` (1)
Strong sulfur tries to create continuous geysers above these blocks. Members: `lava`

### `#causes_periodic_geyser_eruptions` (1)
Strong sulfur tries to create periodic geysers above these blocks. Members: `magma_block`

### `#causes_suffocation`
(Upcoming content, Java Edition 26.3.) Blocks the game treats as view-blocking; full-collision blocks always count. Members: `#blocks_motion`

### `#cave_vines` (2)
For `#moss_replaceable`. Members: `cave_vines_plant`, `cave_vines`

### `#ceiling_hanging_signs` (13)
For `#all_hanging_signs`. Members: `oak_hanging_sign`, `spruce_hanging_sign`, `birch_hanging_sign`, `acacia_hanging_sign`…

### `#chains` (9)
Contains all chains. Members: `iron_chain`, `copper_chain`, `exposed_copper_chain`, `weathered_copper_chain`…

### `#cherry_logs` (4)
For `#logs_that_burn`. Members: `cherry_log`, `cherry_wood`, `stripped_cherry_log`, `stripped_cherry_wood`

### `#climbable` (9)
Used for mob pathfinding; determines which blocks can be climbed. Added blocks need a small enough collision box for the mob's center to fit; scaffolding removal prevents smooth climbing but still allows jumping. Members: `ladder`, `vine`, `scaffolding`, `weeping_vines`…

### `#coal_ores` (2)
Members: `coal_ore`, `deepslate_coal_ore`

### `#combination_step_sound_blocks` (8)
Whether step sounds of these blocks merge with the block below. Members: `#wool_carpets`, `moss_carpet`, `pale_moss_carpet`, `snow`…

### `#completes_find_tree_tutorial` (3)
Blocks completing the "Finding a Tree" tutorial. Members: `#logs`, `#leaves`, `#wart_blocks`

### `#concrete` (16)
Members: `white_concrete`, `orange_concrete`, `magenta_concrete`, `light_blue_concrete`…

### `#concrete_powders` (16)
Members: `white_concrete_powder`, `orange_concrete_powder`, `magenta_concrete_powder`, `light_blue_concrete_powder`…

### `#concrete_slabs` (16)
(Upcoming content, Java Edition 26.3.) Members: `white_concrete_slab`, `orange_concrete_slab`, `magenta_concrete_slab`, `light_blue_concrete_slab`…

### `#concrete_stairs` (16)
(Upcoming content, Java Edition 26.3.) Members: `white_concrete_stairs`, `orange_concrete_stairs`, `magenta_concrete_stairs`, `light_blue_concrete_stairs`…

### `#convertable_to_mud` / `#convertible_to_mud` (3)
Using a water bottle on these blocks converts them to mud. Members: `dirt`, `coarse_dirt`, `rooted_dirt`

### `#copper` (8)
Contains all copper blocks. Members: `copper_block`, `exposed_copper`, `weathered_copper`, `oxidized_copper`…

### `#copper_chests` (8)
Contains all copper chests. Members: `copper_chest`, `exposed_copper_chest`, `weathered_copper_chest`, `oxidized_copper_chest`…

### `#copper_golem_statues` (8)
Contains all copper golem statues. Members: `copper_golem_statue`, `exposed_copper_golem_statue`, `weathered_copper_golem_statue`, `oxidized_copper_golem_statue`…

### `#copper_ores` (2)
Members: `copper_ore`, `deepslate_copper_ore`

### `#coral_blocks` (5)
Used to generate coral reefs; bone meal on a sea pickle above these blocks grows more sea pickles. Members: `tube_coral_block`, `brain_coral_block`, `bubble_coral_block`, `fire_coral_block`…

### `#coral_plants` (5)
For `#corals`. Members: `tube_coral`, `brain_coral`, `bubble_coral`, `fire_coral`…

### `#corals` (6)
Used to generate coral reefs. Members: `#coral_plants`, `tube_coral_fan`, `brain_coral_fan`, `bubble_coral_fan`…

### `#crimson_stems` (4)
For `#logs`. Members: `crimson_stem`, `stripped_crimson_stem`, `crimson_hyphae`, `stripped_crimson_hyphae`

### `#crops` (8)
For `#bee_growables`. Members: `beetroots`, `carrots`, `potatoes`, `wheat`…

### `#cushion_uses_collision_shape`
(Upcoming content, Java Edition 26.3.) Cushion placement clicks use the collision shape instead of the interaction shape on these blocks. Members: `#cauldrons`, `hopper`, `composter`

### `#crystal_sound_blocks` (2)
Blocks playing the crystal sound when stepped on. Members: `amethyst_block`, `budding_amethyst`

### `#dampens_vibrations` (4)
Entities do not emit vibrations on these blocks. Members: `#wool`, `#wool_carpets`, `#wool_slabs`, `#wool_stairs`

### `#dark_oak_logs` (4)
For `#logs_that_burn`. Members: `dark_oak_log`, `dark_oak_wood`, `stripped_dark_oak_log`, `stripped_dark_oak_wood`

### `#deepslate_ore_replaceables` (2)
Blocks replaceable by deepslate ores during world generation; shallow variant in `#stone_ore_replaceables`. Members: `deepslate`, `tuff`

### `#default_immune_to` (0)
Mobs do not treat these blocks as dangerous by default. No members.

### `#diamond_ores` (2)
Members: `diamond_ore`, `deepslate_diamond_ore`

### `#dirt` (3)
For `#moss_replaceable`. Members: `dirt`, `coarse_dirt`, `rooted_dirt`

### `#does_not_block_hoppers` (1)
Full-collision blocks in this tag do not block hoppers from catching item entities. Members: `#beehives`

### `#doors` (10)
Mobs do not jump onto these blocks during pathfinding; these blocks may convert to air when zombie villages generate. Members: `#wooden_doors`, `copper_door`, `exposed_copper_door`, `weathered_copper_door`…

### `#dragon_immune` (19)
Blocks the ender dragon cannot destroy. Members: `barrier`, `bedrock`, `end_portal`, `end_portal_frame`…

### `#dragon_transparent` (2)
Members: `light`, `#fire`

### `#dripstone_replaceable_blocks` (1)
Members: `#base_stone_overworld`

### `#edible_for_sheep` (4)
Blocks sheep can eat. Members: `short_grass`, `short_dry_grass`, `tall_dry_grass`, `fern`

### `#emerald_ores` (2)
Members: `emerald_ore`, `deepslate_emerald_ore`

### `#enables_bubble_column_drag_down` (1)
Fluids create bubble column whirlpools above these blocks. Members: `magma_block`

### `#enables_bubble_column_push_up` (1)
Fluids create bubble column currents above these blocks. Members: `soul_sand`

### `#enchantment_power_provider` (1)
Blocks that increase the enchanting table's maximum enchantment level. Members: `bookshelf`

### `#enchantment_power_transmitter` (1)
Blocks that do not block enchanting table power transmission. Members: `#replaceable`

### `#enderman_holdable` (23)
Blocks endermen can pick up. Members: `#small_flowers`, `#dirt`, `#mud`, `#moss_blocks`…

### `#entities_can_teleport_to`
(Upcoming content, Java Edition 26.3.) Blocks entities are allowed to teleport to; `/spreadplayers` treats them as valid. Members: `#blocks_motion`

### `#fall_damage_resetting` (3)
Blocks (besides liquids) that reset fall damage. Members: `#climbable`, `sweet_berry_bush`, `cobweb`

### `#features_cannot_replace` (7)
Members: `bedrock`, `spawner`, `chest`, `end_portal_frame`…

### `#fence_gates` (13)
Members: `acacia_fence_gate`, `birch_fence_gate`, `dark_oak_fence_gate`, `pale_oak_fence_gate`…

### `#fences` (2)
Mobs treat these blocks as fences for pathfinding; leads can attach; leash knot entities use it to decide when to break. Members: `#wooden_fences`, `nether_brick_fence`

### `#fire` (2)
Ignored when detecting valid inactive nether portals (removed on activation); mobs treat these as fire for pathfinding; they do not block falling blocks; fire-extinguishing potions remove them; for `#dragon_transparent`. Members: `fire`, `soul_fire`

### `#flower_pots` (40)
Members: `flower_pot`, `potted_poppy`, `potted_oak_sapling`, `potted_red_mushroom`…

### `#flowers` (15)
Members: `#small_flowers`, `sunflower`, `lilac`, `peony`…

### `#forest_rock_can_place_on` (2)
Blocks the `forest_rock` feature can place on. Members: `#substrate_overworld`, `#base_stone_overworld`

### `#foxes_spawnable_on` (5)
Used for fox spawning checks. Members: `grass_block`, `snow`, `snow_block`, `podzol`…

### `#fox_immune_to` (1)
Foxes do not treat these blocks as dangerous. Members: `sweet_berry_bush`

### `#frog_prefer_jump_to` (2)
Members: `lily_pad`, `big_dripleaf`

### `#frogs_spawnable_on` (4)
Used for frog spawning checks. Members: `grass_block`, `mud`, `mangrove_roots`, `muddy_mangrove_roots`

### `#geode_invalid_blocks` (6)
Members: `bedrock`, `water`, `lava`, `ice`…

### `#glazed_terracotta` (16)
Members: `white_glazed_terracotta`, `orange_glazed_terracotta`, `magenta_glazed_terracotta`, `light_blue_glazed_terracotta`…

### `#goats_spawnable_on` (6)
Members: `#animals_spawnable_on`, `stone`, `snow`, `snow_block`…

### `#gold_ores` (3)
Members: `gold_ore`, `nether_gold_ore`, `deepslate_gold_ore`

### `#grass_blocks` (3)
Members: `grass_block`, `podzol`, `mycelium`

### `#grows_crops` (1)
Wheat, carrots, potatoes, beetroots, torchflower, pitcher plants, pumpkin stems, and melon stems can grow on these blocks. Members: `farmland`

### `#guarded_by_piglins` (10)
Piglins become hostile toward players opening or destroying these blocks. Members: `#copper_chests`, `gold_block`, `barrel`, `chest`…

### `#happy_ghast_avoids` (6)
Ghasts and happy ghasts tend to stay away from these blocks. Members: `sweet_berry_bush`, `cactus`, `wither_rose`, `magma_block`…

### `#height_specific_ore_replaceables` (1)
Ores replaced by their deepslate variants below Y=8. Members: `tuff`

### `#hoglin_repellents` (4)
Hoglins stay away from these blocks. Members: `warped_fungus`, `potted_warped_fungus`, `nether_portal`, `respawn_anchor`

### `#huge_brown_mushroom_can_place_on` (5)
Blocks the `huge_brown_mushroom` feature can place on. Members: `#substrate_overworld`, `mycelium`, `podzol`, `crimson_nylium`…

### `#huge_red_mushroom_can_place_on` (5)
Blocks the `huge_red_mushroom` feature can place on. Members: `#substrate_overworld`, `mycelium`, `podzol`, `crimson_nylium`…

### `#ice` (4)
Ocean ruins do not generate on these blocks. Members: `ice`, `packed_ice`, `blue_ice`, `frosted_ice`

### `#ice_spike_replaceable` (3)
Blocks ice spikes can replace. Members: `#substrate_overworld`, `snow_block`, `ice`

### `#ice_melts_when_destroyed_above` (1)
Ice above these blocks creates water when broken if allowed. Members: `#blocks_motion`

### `#impermeable` (19)
Blocks in this tag do not show dripping water/lava particles above liquids. Members: `white_stained_glass`, `orange_stained_glass`, `magenta_stained_glass`, `light_blue_stained_glass`…

### `#incorrect_for_copper_tool` (2)
Blocks mined with copper tools do not drop. Members: `#needs_diamond_tool`, `#needs_iron_tool`

### `#incorrect_for_diamond_tool` (0)
Blocks mined with diamond tools do not drop. No members.

### `#incorrect_for_gold_tool` (3)
Blocks mined with golden tools do not drop. Members: `#needs_diamond_tool`, `#needs_iron_tool`, `#needs_stone_tool`

### `#incorrect_for_iron_tool` (1)
Blocks mined with iron tools do not drop. Members: `#needs_diamond_tool`

### `#incorrect_for_netherite_tool` (0)
Blocks mined with netherite tools do not drop. No members.

### `#incorrect_for_stone_tool` (2)
Blocks mined with stone tools do not drop. Members: `#needs_diamond_tool`, `#needs_iron_tool`

### `#incorrect_for_wooden_tool` (3)
Blocks mined with wooden tools do not drop. Members: `#needs_diamond_tool`, `#needs_iron_tool`, `#needs_stone_tool`

### `#infiniburn_end` (2)
Fire burns indefinitely on these blocks in the End. Members: `#infiniburn_overworld`, `bedrock`

### `#infiniburn_nether` (1)
Fire burns indefinitely on these blocks in the Nether. Members: `#infiniburn_overworld`

### `#infiniburn_overworld` (2)
Fire burns indefinitely on these blocks in the Overworld. Members: `netherrack`, `magma_block`

### `#inside_step_sound_blocks` (8)
Blocks playing the snow step sound when walked inside. Members: `powder_snow`, `sculk_vein`, `glow_lichen`, `lily_pad`…

### `#invalid_spawn_inside` (2)
Positions with these blocks are not chosen as respawn points. Members: `end_portal`, `end_gateway`

### `#iron_ores` (2)
Members: `iron_ore`, `deepslate_iron_ore`

### `#jungle_logs` (4)
Cocoa can be placed on them. Members: `jungle_log`, `jungle_wood`, `stripped_jungle_log`, `stripped_jungle_wood`

### `#lanterns` (10)
Contains all lanterns. Members: `lantern`, `soul_lantern`, `copper_lantern`, `exposed_copper_lantern`…

### `#lightning_rods` (8)
Contains all lightning rods. Members: `lightning_rod`, `exposed_lightning_rod`, `weathered_lightning_rod`, `oxidized_lightning_rod`…

### `#lapis_ores` (2)
Members: `lapis_ore`, `deepslate_lapis_ore`

### `#lava_pool_stone_cannot_replace` (3)
Members: `#features_cannot_replace`, `#leaves`, `#logs`

### `#leaves` (14)
These blocks do not obstruct many structures (bonus chests, trees, huge mushrooms); used to determine placement. Members: `jungle_leaves`, `oak_leaves`, `spruce_leaves`, `pale_oak_leaves`…

### `#logs` (3)
One of the requirements for parrots to perch; leaf blocks near these update their `distance` state. Members: `#logs_that_burn`, `#crimson_stems`, `#warped_stems`

### `#logs_that_burn` (10)
Members: `#dark_oak_logs`, `#pale_oak_logs`, `#oak_logs`, `#acacia_logs`…

### `#lush_ground_replaceable` (4)
Members: `#moss_replaceable`, `clay`, `gravel`, `sand`

### `#maintains_farmland` (13)
Blocks that keep farmland from reverting to dirt. Members: `pumpkin_stem`, `attached_pumpkin_stem`, `melon_stem`, `attached_melon_stem`…

### `#mangrove_logs` (4)
Members: `mangrove_log`, `mangrove_wood`, `stripped_mangrove_log`, `stripped_mangrove_wood`

### `#mangrove_logs_can_grow_through` (8)
Blocks mangrove logs can grow through. Members: `mud`, `muddy_mangrove_roots`, `mangrove_roots`, `mangrove_leaves`…

### `#mangrove_roots_can_grow_through` (7)
Blocks mangrove roots can grow through. Members: `mud`, `muddy_mangrove_roots`, `mangrove_roots`, `moss_carpet`…

### `#mineable/axe` (55)
Blocks mined faster with axes. Members: `#banners`, `#fence_gates`, `#logs`, `#planks`…

### `#mineable/hoe` (19)
Blocks mined faster with hoes. Members: `#leaves`, `nether_wart_block`, `warped_wart_block`, `hay_block`…

### `#mineable/pickaxe` (449)
Blocks mined faster with pickaxes. Members: `stone`, `granite`, `cobblestone`, `deepslate`…

### `#mineable/shovel` (21)
Blocks mined faster with shovels. Members: `clay`, `dirt`, `coarse_dirt`, `podzol`…

### `#mob_interactable_doors` (9)
Blocks interactable as doors by mobs. Members: `#wooden_doors`, `copper_door`, `exposed_copper_door`, `weathered_copper_door`…

### `#mooshrooms_spawnable_on` (1)
Used for mooshroom spawning checks. Members: `mycelium`

### `#moss_blocks` (2)
Members: `moss_block`, `pale_moss_block`

### `#moss_replaceable` (6)
Blocks replaceable by moss blocks spread with bone meal. Members: `#base_stone_overworld`, `#cave_vines`, `#dirt`, `#mud`

### `#mud` (2)
Members: `mud`, `muddy_mangrove_roots`

### `#needs_diamond_tool` (5)
Blocks requiring at least a diamond tool to drop items. Members: `obsidian`, `crying_obsidian`, `netherite_block`, `respawn_anchor`…

### `#needs_iron_tool` (12)
Blocks requiring at least an iron tool to drop items. Members: `diamond_block`, `diamond_ore`, `deepslate_diamond_ore`, `emerald_ore`…

### `#needs_stone_tool` (77)
Blocks requiring at least a stone tool to drop items. Members: `#copper_chests`, `#lightning_rods`, `iron_block`, `iron_ore`…

### `#nether_carver_replaceables` (7)
Blocks removable by the Nether carver. Members: `#base_stone_overworld`, `#base_stone_nether`, `#substrate_overworld`, `#nylium`…

### `#nylium` (2)
Members: `crimson_nylium`, `warped_nylium`

### `#oak_logs` (4)
Members: `oak_log`, `oak_wood`, `stripped_oak_log`, `stripped_oak_wood`

### `#occludes_vibration_signals` (1)
Blocks vibration propagation. Members: `#wool`

### `#ores` (9)
Members: `#copper_ores`, `#gold_ores`, `#iron_ores`, `#coal_ores`…

### `#overrides_mushroom_light_requirement` (4)
Mushrooms cannot survive outside this tag at light levels ≥13. Members: `mycelium`, `podzol`, `crimson_nylium`, `warped_nylium`

### `#overworld_carver_replaceables` (19)
Blocks removable by the Overworld carver. Members: `#base_stone_overworld`, `#substrate_overworld`, `#sand`, `#terracotta`…

### `#overworld_natural_logs` (10)
Members: `acacia_log`, `birch_log`, `oak_log`, `jungle_log`…

### `#pale_oak_logs` (4)
Members: `pale_oak_log`, `pale_oak_wood`, `stripped_pale_oak_log`, `stripped_pale_oak_wood`

### `#parrots_spawnable_on` (4)
Used for parrot spawning checks. Members: `grass_block`, `air`, `#leaves`, `#logs`

### `#piglin_repellents` (5)
Piglins stay away from these blocks. Members: `soul_fire`, `soul_torch`, `soul_lantern`, `soul_wall_torch`…

### `#planks` (13)
Members: `oak_planks`, `spruce_planks`, `birch_planks`, `jungle_planks`…

### `#polar_bear_immune_to` (1)
Polar bears do not treat these blocks as dangerous. Members: `powder_snow`

### `#polar_bears_spawnable_on_alternate` (1)
Used for polar bear spawning checks. Members: `ice`

### `#poplar_logs` (4)
Members: `poplar_log`, `poplar_wood`, `stripped_poplar_log`, `stripped_poplar_wood`

### `#portals` (3)
Dismounting riders do not land in these blocks to prevent unwanted teleports. Members: `nether_portal`, `end_portal`, `end_gateway`

### `#pressure_plates` (4)
Members: `light_weighted_pressure_plate`, `heavy_weighted_pressure_plate`, `#wooden_pressure_plates`, `#stone_pressure_plates`

### `#prevent_mob_spawning_inside` (1)
Mobs cannot spawn inside these blocks. Members: `#rails`

### `#prevents_nearby_leaf_decay` (1)
Leaves within Manhattan distance 6 of these blocks do not decay. Members: `#logs`

### `#rabbits_spawnable_on` (4)
Used for rabbit spawning checks. Members: `grass_block`, `snow`, `snow_block`, `sand`

### `#rails` (4)
Checks rail connections; minecart rideability and placement. Adding other blocks crashes the game; TNT minecarts inside do not destroy the block and the one below. Members: `rail`, `powered_rail`, `detector_rail`, `activator_rail`

### `#redstone_ores` (2)
Members: `redstone_ore`, `deepslate_redstone_ore`

### `#replaceable` (30)
Members: `air`, `water`, `lava`, `short_grass`…

### `#replaceable_by_mushrooms` (32)
Blocks replaceable when mushrooms are placed or grow. Members: `#leaves`, `#small_flowers`, `pale_moss_carpet`, `short_grass`…

### `#replaceable_by_trees` (27)
Blocks replaceable by grown trees. Members: `#leaves`, `#small_flowers`, `pale_moss_carpet`, `short_grass`…

### `#required_for_poplar_leaf_ambience` (1)
Used for poplar leaf ambience sound checks. Members: `#overworld_natural_logs`

### `#sand` (3)
Determines whether turtle eggs can hatch on the block. Members: `sand`, `red_sand`, `suspicious_sand`

### `#saplings` (12)
Blocks replaced when trees grow. Members: `oak_sapling`, `spruce_sapling`, `birch_sapling`, `jungle_sapling`…

### `#sculk_growth_inhibitors` (2)
Blocks that prevent sculk spread. Members: `sculk_sensor`, `sculk_shrieker`

### `#sculk_replaceable` (19)
Determines which blocks the sculk catalyst converts to sculk when spreading. Members: `#base_stone_overworld`, `#substrate_overworld`, `#terracotta`, `#nylium`…

### `#sculk_replaceable_world_gen` (7)
Determines which blocks sculk vein clusters replace during world generation. Members: `#sculk_replaceable`, `deepslate_bricks`, `deepslate_tiles`, `cobbled_deepslate`…

### `#shears_extreme_breaking_speed` (1)
Blocks broken by shears at 15x speed; Haste does not affect cobwebs. Members: `#leaves`

### `#shears_major_breaking_speed` (3)
Blocks broken by shears at 5x speed. Members: `#wool`, `#wool_slabs`, `#wool_stairs`

### `#shears_minor_breaking_speed` (2)
Blocks broken by shears at 2x speed. Members: `glow_lichen`, `vine`

### `#shulker_boxes` (17)
Fences, walls, and glass panes do not connect to these blocks. Members: `shulker_box`, `white_shulker_box`, `orange_shulker_box`, `magenta_shulker_box`…

### `#signs` (2)
Flowing water does not break these blocks. Members: `#standing_signs`, `#wall_signs`

### `#skulls` (7)
Members: `player_head`, `creeper_head`, `zombie_head`, `skeleton_skull`…

### `#slabs` (59)
Members: `#wooden_slabs`, `#wool_slabs`, `#concrete_slabs`, `stone_slab`…

### `#small_flowers` (17)
Bees try to collect pollen from these blocks. Members: `dandelion`, `open_eyeblossom`, `poppy`, `blue_orchid`…

### `#smelts_to_glass` (2)
These blocks can be smelted into glass. Members: `sand`, `red_sand`

### `#snaps_goat_horn` (7)
Goats drop goat horns when ramming these blocks. Members: `#overworld_natural_logs`, `stone`, `packed_ice`, `iron_ore`…

### `#sniffer_diggable_block` (5)
Sniffers can find seeds in these blocks. Members: `#dirt`, `#mud`, `#moss_blocks`, `grass_block`…

### `#sniffer_egg_hatch_boost` (1)
These blocks speed up sniffer egg hatching. Members: `moss_block`

### `#snow` (3)
Members: `snow`, `snow_block`, `powder_snow`

### `#snow_golem_immune_to` (1)
Snow golems do not treat these blocks as dangerous. Members: `powder_snow`

### `#soul_fire_base_blocks` (2)
Soul fire burns on these blocks. Members: `soul_sand`, `soul_soil`

### `#soul_speed_blocks` (2)
Soul Speed boots move faster on these blocks. Members: `soul_sand`, `soul_soil`

### `#speeds_up_zombie_villager_curing` (2)
Blocks that speed up zombie villager curing. Members: `iron_bars`, `#beds`

### `#speleothems` (2)
Members: `pointed_dripstone`, `sulfur_spike`

### `#spruce_logs` (4)
Members: `spruce_log`, `spruce_wood`, `stripped_spruce_log`, `stripped_spruce_wood`

### `#stairs` (55)
Members: `#wooden_stairs`, `#wool_stairs`, `#concrete_stairs`, `cobblestone_stairs`…

### `#standing_signs` (13)
Members: `oak_sign`, `spruce_sign`, `birch_sign`, `acacia_sign`…

### `#stone_bricks` (4)
Members: `stone_bricks`, `mossy_stone_bricks`, `cracked_stone_bricks`, `chiseled_stone_bricks`

### `#stone_buttons` (2)
Members: `stone_button`, `polished_blackstone_button`

### `#stone_ore_replaceables` (4)
Blocks replaceable by ores during world generation; deepslate variant in `#deepslate_ore_replaceables`. Members: `stone`, `granite`, `diorite`, `andesite`

### `#stone_pressure_plates` (2)
Members: `stone_pressure_plate`, `polished_blackstone_pressure_plate`

### `#stray_immune_to` (1)
Strays do not treat these blocks as dangerous. Members: `powder_snow`

### `#strider_warm_blocks` (1)
Striders shiver when not in these blocks. Members: `lava`

### `#substrate_overworld` (4)
Used to aggregate world generation conditions. Members: `#dirt`, `#mud`, `#moss_blocks`, `#grass_blocks`

### `#sulfur_spike_replaceable_blocks` (2)
Sulfur spikes can replace these blocks when generating. Members: `sulfur`, `cinnabar`

### `#support_override_cactus_flower` (2)
Cactus flowers can be placed and survive on these blocks even with an incomplete top surface. Members: `cactus`, `farmland`

### `#support_override_snow_layer` (3)
Snow can be placed and survive on these blocks even with an incomplete top surface. Members: `honey_block`, `soul_sand`, `mud`

### `#supports_azalea` (2)
Azalea and flowering azalea bushes can be placed and survive on these blocks. Members: `#supports_vegetation`, `clay`

### `#supports_bamboo` (6)
Bamboo and bamboo saplings can be placed and survive on these blocks. Members: `#sand`, `#substrate_overworld`, `bamboo`, `bamboo_sapling`…

### `#supports_big_dripleaf` (11)
Big dripleaves can be placed and survive on these blocks. Members: `#supports_small_dripleaf`, `dirt`, `grass_block`, `podzol`…

### `#supports_cactus` (1)
Cacti can be placed and survive on these blocks. Members: `#sand`

### `#supports_chorus_flower` (1)
Chorus flowers can be placed and survive on these blocks. Members: `end_stone`

### `#supports_chorus_plant` (1)
Chorus plants can be placed and survive on these blocks; chorus trees generate on them. Members: `end_stone`

### `#supports_cocoa` (1)
Cocoa can be placed and survive on these blocks. Members: `#jungle_logs`

### `#supports_crimson_fungus` (1)
Crimson fungi can be placed and survive on these blocks. Members: `#supports_warped_fungus`

### `#supports_crimson_roots` (1)
Crimson roots can be placed and survive on these blocks. Members: `#supports_warped_roots`

### `#supports_crops` (1)
Wheat, carrots, potatoes, beetroots, torchflower, and pitcher plants can be placed and survive on these blocks. Members: `farmland`

### `#supports_dry_vegetation` (3)
Short and tall dry grass can be placed and survive on these blocks. Members: `#sand`, `#terracotta`, `#supports_vegetation`

### `#supports_frogspawn` (0)
Frogspawn can be placed and survive on these blocks. No members.

### `#supports_hanging_mangrove_propagule` (1)
Mangrove propagules can survive below these blocks; cannot be manually placed. Members: `mangrove_leaves`

### `#supports_lily_pad` (2)
Lily pads can be placed and survive on these blocks. Members: `ice`, `frosted_ice`

### `#supports_mangrove_propagule` (2)
Mangrove propagules can be placed and survive on these blocks. Members: `#supports_vegetation`, `clay`

### `#supports_melon_stem` (1)
Melon stems can be placed and survive on these blocks. Members: `#supports_stem_crops`

### `#supports_melon_stem_fruit` (1)
Melon stems can grow melons above these blocks. Members: `#supports_stem_fruit`

### `#supports_nether_sprouts` (3)
Nether sprouts can be placed and survive on these blocks. Members: `#supports_vegetation`, `#nylium`, `soul_soil`

### `#supports_nether_wart` (1)
Nether wart can be placed and survive on these blocks. Members: `soul_sand`

### `#supports_pumpkin_stem` (1)
Pumpkin stems can be placed and survive on these blocks. Members: `#supports_stem_crops`

### `#supports_pumpkin_stem_fruit` (1)
Pumpkin stems can grow pumpkins above these blocks. Members: `#supports_stem_fruit`

### `#supports_small_dripleaf` (2)
Small dripleaves can be placed and survive on these blocks. Members: `clay`, `moss_block`

### `#supports_stem_crops` (1)
Melon or pumpkin stems can be placed and survive on these blocks. Members: `#supports_crops`

### `#supports_stem_fruit` (1)
Members: `#supports_vegetation`

### `#supports_sugar_cane` (2)
Sugar cane can be placed and survive on these blocks. Members: `#substrate_overworld`, `#sand`

### `#supports_sugar_cane_adjacently` (1)
Sugar cane can be placed and survive on blocks adjacent to these. Members: `frosted_ice`

### `#supports_vegetation` (2)
All short/tall grass, ferns, flowers, saplings, and other vegetation can be placed and survive on these blocks. Members: `#substrate_overworld`, `farmland`

### `#supports_warped_fungus` (4)
Warped fungi can be placed and survive on these blocks. Members: `#supports_vegetation`, `#nylium`, `mycelium`, `soul_soil`

### `#supports_warped_roots` (3)
Warped roots can be placed and survive on these blocks. Members: `#supports_vegetation`, `#nylium`, `soul_soil`

### `#supports_wither_rose` (4)
Wither roses can be placed and survive on these blocks. Members: `#supports_vegetation`, `netherrack`, `soul_sand`, `soul_soil`

### `#suppresses_bounce` (1)
Entities lose bounce when colliding with these blocks. Members: `honey_block`

### `#sword_efficient` (12)
Blocks broken by swords at 1.5x speed. Members: `#leaves`, `vine`, `glow_lichen`, `pumpkin`…

### `#sword_instantly_mines` (2)
Blocks instantly broken by swords. Members: `bamboo`, `bamboo_sapling`

### `#terracotta` (17)
Members: `terracotta`, `white_terracotta`, `orange_terracotta`, `magenta_terracotta`…

### `#trail_ruins_replaceable` (1)
Suspicious gravel can replace these blocks in trail ruins. Members: `gravel`

### `#trapdoors` (10)
Mobs treat these blocks as trapdoors during pathfinding. Members: `#wooden_trapdoors`, `iron_trapdoor`, `copper_trapdoor`, `exposed_copper_trapdoor`…

### `#triggers_ambient_desert_dry_vegetation_block_sounds` (3)
Blocks that can trigger desert ambience sounds. Members: `#terracotta`, `sand`, `red_sand`

### `#triggers_ambient_dried_ghast_block_sounds` (2)
Blocks valid for dried ghast ambience sound checks. Members: `soul_sand`, `soul_soil`

### `#triggers_ambient_desert_sand_block_sounds` (2)
Blocks valid for desert sand ambience sound checks. Members: `sand`, `red_sand`

### `#turns_into_dirt_path` (6)
Blocks convertible to dirt paths with a shovel. Members: `grass_block`, `dirt`, `podzol`, `coarse_dirt`…

### `#turns_into_farmland` (3)
Blocks convertible to farmland with a hoe. Members: `grass_block`, `dirt_path`, `dirt`

### `#underwater_bonemeals` (3)
When bone meal is used underwater in warm ocean biomes, these blocks replace water source blocks (within 5 horizontal and 2 vertical blocks); custom members apply to any biome. These blocks do not hold water by default. Members: `seagrass`, `#corals`, `#wall_corals`

### `#unstable_bottom_center` (1)
Members: `#fence_gates`

### `#valid_spawn` (2)
Determines valid player spawn positions. Members: `grass_block`, `podzol`

### `#vibration_resonators` (1)
Blocks that can resonate. Members: `amethyst_block`

### `#villager_babies_can_jump_on_bed` (1)
Blocks baby villagers can jump on. Members: `#beds`

### `#villagers_can_sleep_on_bed` (1)
Blocks villagers can sleep on. Members: `#beds`

### `#wall_corals` (5)
Used to generate coral reefs. Members: `tube_coral_wall_fan`, `brain_coral_wall_fan`, `bubble_coral_wall_fan`, `fire_coral_wall_fan`…

### `#wall_hanging_signs` (13)
For `#all_hanging_signs`. Members: `oak_wall_hanging_sign`, `spruce_wall_hanging_sign`, `birch_wall_hanging_sign`, `acacia_wall_hanging_sign`…

### `#wall_post_override` (9)
Placing these on a wall makes the wall show a post. Members: `torch`, `soul_torch`, `redstone_torch`, `copper_torch`…

### `#wall_signs` (13)
Members: `oak_wall_sign`, `spruce_wall_sign`, `birch_wall_sign`, `acacia_wall_sign`…

### `#walls` (32)
Mobs treat these blocks as fences during pathfinding; fence gates adjacent to them get `in_wall` = `true`. Members: `cobblestone_wall`, `brick_wall`, `stone_brick_wall`, `nether_brick_wall`…

### `#warped_stems` (4)
Members: `warped_stem`, `stripped_warped_stem`, `warped_hyphae`, `stripped_warped_hyphae`

### `#wart_blocks` (2)
Hoglins cannot spawn on these blocks. Members: `nether_wart_block`, `warped_wart_block`

### `#washed_away_by_fluids` (134)
Flowing fluids destroy these blocks; no effect on blocks not destroyed by fluid flow. Members: `#fire`, `#saplings`, `#corals`, `#wall_corals`…

### `#wither_immune` (15)
Blocks the wither cannot destroy. Members: `barrier`, `bedrock`, `end_portal`, `end_portal_frame`…

### `#wither_immune_to` (1)
The wither does not treat these blocks as dangerous. Members: `wither_rose`

### `#wither_skeleton_immune_to` (1)
Wither skeletons do not treat these blocks as dangerous. Members: `wither_rose`

### `#wither_summon_base_blocks` (2)
Blocks used to build the wither. Members: `soul_sand`, `soul_soil`

### `#wolves_spawnable_on` (5)
Used for wolf spawning checks. Members: `grass_block`, `snow`, `snow_block`, `coarse_dirt`…

### `#wooden_buttons` (13)
For `#buttons`. Members: `oak_button`, `spruce_button`, `birch_button`, `jungle_button`…

### `#wooden_doors` (13)
For `#doors`; villagers use it to detect doors. Members: `oak_door`, `spruce_door`, `birch_door`, `jungle_door`…

### `#wooden_fences` (13)
Members: `oak_fence`, `acacia_fence`, `dark_oak_fence`, `pale_oak_fence`…

### `#wooden_pressure_plates` (13)
Members: `oak_pressure_plate`, `spruce_pressure_plate`, `birch_pressure_plate`, `jungle_pressure_plate`…

### `#wooden_slabs` (13)
Members: `oak_slab`, `spruce_slab`, `birch_slab`, `jungle_slab`…

### `#wooden_stairs` (13)
Members: `oak_stairs`, `spruce_stairs`, `birch_stairs`, `jungle_stairs`…

### `#wooden_shelves` (13)
Contains all wooden shelves. Members: `acacia_shelf`, `bamboo_shelf`, `birch_shelf`, `cherry_shelf`…

### `#wooden_trapdoors` (13)
Members: `acacia_trapdoor`, `birch_trapdoor`, `dark_oak_trapdoor`, `pale_oak_trapdoor`…

### `#wool` (16)
Note blocks on these blocks play the guitar sound; for `#occludes_vibration_signals`. Members: `white_wool`, `orange_wool`, `magenta_wool`, `light_blue_wool`…

### `#wool_carpets` (16)
Members: `white_carpet`, `orange_carpet`, `magenta_carpet`, `light_blue_carpet`…

### `#wool_stairs` (16)
Members: `white_wool_stairs`, `orange_wool_stairs`, `magenta_wool_stairs`, `light_blue_wool_stairs`…

### `#wool_slabs` (16)
Members: `white_wool_slab`, `orange_wool_slab`, `magenta_wool_slab`, `light_blue_wool_slab`…

## Removed tags

- `#azalea_log_replaceable` — added 21w05a, removed 21w10a
- `#dirt_like` — added 18w43a, removed 19w41a
- `#fire_aspect_lightable` — blocks lightable by Fire Aspect attacks; added 24w19a, removed Java 1.21-pre1
- `#lush_plants_replaceable` — replaced by `moss_replaceable`; added 21w05a, removed 21w16a
- `#non_flammable_wood` — an item tag with the same name still exists; added 20w13a, removed 22w44a
- `#replaceable_plants` — replaced by `replaceable_by_trees`; added Java 1.18-pre5, removed 23w14a
- `#stripped_logs` — added 22w42a, removed 22w46a
- `#tall_flowers` — added 19w34a, removed 24w45a
- `#water_hacked` — added 18w07a, removed 18w10c
- `#waterlogged` — added 18w07b, removed 18w10c

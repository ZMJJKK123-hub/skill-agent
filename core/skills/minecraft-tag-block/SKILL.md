---
name: minecraft-tag-block
description: |
  Java版标签/方块（Minecraft Wiki 中文版全量正文）。
  
  【概述】“方块标签”重定向至此。关于基岩版中的方块标签，请见“基岩版标签/方块”。
  
  【涵盖内容】
  - acacia_logs
  - air
  - all_hanging_signs
  - all_signs
  - ancient_city_replaceable
  - animals_spawnable_on
  - anvil
  - armadillo_spawnable_on
  - axolotls_spawnable_on
  - azalea_grows_on
  - azalea_root_replaceable
  - badlands_terracotta
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/方块 的完整规范时
---

“方块标签”重定向至此。关于基岩版中的方块标签，请见“基岩版标签/方块”。
本条目所述内容仅适用于Java版。
方块标签（Block Tags）是方块的组合。

# 使用

方块标签被用于进度和世界生成等文件，也用于命令测试方块。只要方块在标签中则测试成功。

游戏定义了一系列方块标签，有些是同类方块的简单分组。部分标签被游戏内部用于特殊用途，如生物生成、世界生成和方块行为等。

# 标签列表

## acacia_logs

- 用于 ``` #logs_that_burn ``` 。

- #acacia_logs（4项） - ``` acacia_log ``` （金合欢原木） - ``` acacia_wood ``` （金合欢木） - ``` stripped_acacia_log ``` （去皮金合欢原木） - ``` stripped_acacia_wood ``` （去皮金合欢木）

## air

- 用于冰霜行者魔咒检测水上方的空气。

- #air（3项） - ``` air ``` （空气） - ``` void_air ``` （虚空空气） - ``` cave_air ``` （洞穴空气）

## all_hanging_signs

- 用于 ``` #all_signs ``` 。

- #all_hanging_signs（2项） - ``` #ceiling_hanging_signs ``` - ``` #wall_hanging_signs ```

## all_signs

- #all_signs（2项） - ``` #signs ``` - ``` #all_hanging_signs ```

## ancient_city_replaceable

- 用于决定远古城市在生成时能取代哪些方块。

- #ancient_city_replaceable（12项） - ``` deepslate ``` （深板岩） - ``` deepslate_bricks ``` （深板岩砖） - ``` deepslate_tiles ``` （深板岩瓦） - ``` deepslate_brick_slab ``` （深板岩砖台阶） - ``` deepslate_tile_slab ``` （深板岩瓦台阶） - ``` deepslate_brick_stairs ``` （深板岩砖楼梯） - ``` deepslate_tile_wall ``` （深板岩瓦墙） - ``` deepslate_brick_wall ``` （深板岩砖墙） - ``` cobbled_deepslate ``` （深板岩圆石） - ``` cracked_deepslate_bricks ``` （裂纹深板岩砖） - ``` cracked_deepslate_tiles ``` （裂纹深板岩瓦） - ``` gray_wool ``` （灰色羊毛）

## animals_spawnable_on

- 用于动物的生成判断。

- #animals_spawnable_on（1项） - ``` grass_block ``` （草方块）

## anvil

- 用来决定哪些方块能够用来打开铁砧的GUI界面
- 对其他方块无效，但是将默认元素移出该标签会使得GUI在消失之前快速闪烁。
- 用来决定其下落方块形式是否伤害实体，用于死亡消息。
- 用来判断一个方块是否会在使用或落地时“破坏”。
- 在标签里添加其他可以自然掉落的方块不会使它们受影响，除非使用命令召唤。例如，添加 ``` sand ``` 后不会使自然落下的落沙伤害实体，但是通过命令生成的落沙会对实体有伤害。
- 用于从掉落中的方块实体中读取NBT，以把没有设置 ``` HurtEntities ``` NBT标签的掉落的方块实体的 ``` hurtEntities ``` 设置为 ``` true ``` 。
- 用来决定方块是否有机会被通过铁砧GUI破损。

- #anvil（3项） - ``` anvil ``` （铁砧） - ``` chipped_anvil ``` （开裂的铁砧） - ``` damaged_anvil ``` （损坏的铁砧）

## armadillo_spawnable_on

- 犰狳可以在这些方块上自然生成。

- #armadillo_spawnable_on（4项） - ``` #animals_spawnable_on ``` - ``` #badlands_terracotta ``` - ``` red_sand ``` （红沙） - ``` coarse_dirt ``` （砂土）

## axolotls_spawnable_on

- 用于美西螈生成判断。

- #axolotls_spawnable_on（1项） - ``` clay ``` （黏土）

## azalea_grows_on

- 用于决定杜鹃树可以在哪些方块上自然生成。
- 用于决定杜鹃树在自然生成时其下方1格的缠根泥土能取代哪些方块。

- #azalea_grows_on（5项） - ``` #substrate_overworld ``` - ``` #sand ``` - ``` #terracotta ``` - ``` snow_block ``` （雪块） - ``` powder_snow ``` （细雪）

## azalea_root_replaceable

- 用于决定杜鹃树在自然生成时，下方大量团簇状的缠根泥土和垂根能取代哪些方块。

- #azalea_root_replaceable（9项） - ``` #base_stone_overworld ``` - ``` #substrate_overworld ``` - ``` #terracotta ``` - ``` red_sand ``` （红沙） - ``` clay ``` （黏土） - ``` gravel ``` （沙砾） - ``` sand ``` （沙子） - ``` snow_block ``` （雪块） - ``` powder_snow ``` （细雪）

## badlands_terracotta

- 用于决定犰狳可以在哪些陶瓦上自然生成。

- #badlands_terracotta（7项） - ``` terracotta ``` （陶瓦） - ``` white_terracotta ``` （白色陶瓦） - ``` yellow_terracotta ``` （黄色陶瓦） - ``` orange_terracotta ``` （橙色陶瓦） - ``` red_terracotta ``` （红色陶瓦） - ``` brown_terracotta ``` （棕色陶瓦） - ``` light_gray_terracotta ``` （淡灰色陶瓦）

## bamboo_blocks

- #bamboo_blocks（2项） - ``` bamboo_block ``` （竹块） - ``` stripped_bamboo_block ``` （去皮竹块）

## banners

- 用于检测用地图点击该方块是否应该在地图上标记该点。将其他方块加入此标签会导致用地图点击时产生使用动画，但不会添加标记。
- 用于 ``` #wall_post_override ``` 。

- #banners（32项） - ``` white_banner ``` （白色旗帜） - ``` orange_banner ``` （橙色旗帜） - ``` magenta_banner ``` （品红色旗帜） - ``` light_blue_banner ``` （淡蓝色旗帜） - ``` yellow_banner ``` （黄色旗帜） - ``` lime_banner ``` （黄绿色旗帜） - ``` pink_banner ``` （粉红色旗帜） - ``` gray_banner ``` （灰色旗帜） - ``` light_gray_banner ``` （淡灰色旗帜） - ``` cyan_banner ``` （青色旗帜） - ``` purple_banner ``` （紫色旗帜） - ``` blue_banner ``` （蓝色旗帜） - ``` brown_banner ``` （棕色旗帜） - ``` green_banner ``` （绿色旗帜） - ``` red_banner ``` （红色旗帜） - ``` black_banner ``` （黑色旗帜） - ``` white_wall_banner ``` （墙上的白色旗帜） - ``` orange_wall_banner ``` （墙上的橙色旗帜） - ``` magenta_wall_banner ``` （墙上的品红色旗帜） - ``` light_blue_wall_banner ``` （墙上的淡蓝色旗帜） - ``` yellow_wall_banner ``` （墙上的黄色旗帜） - ``` lime_wall_banner ``` （墙上的黄绿色旗帜） - ``` pink_wall_banner ``` （墙上的粉红色旗帜） - ``` gray_wall_banner ``` （墙上的灰色旗帜） - ``` light_gray_wall_banner ``` （墙上的淡灰色旗帜） - ``` cyan_wall_banner ``` （墙上的青色旗帜） - ``` purple_wall_banner ``` （墙上的紫色旗帜） - ``` blue_wall_banner ``` （墙上的蓝色旗帜） - ``` brown_wall_banner ``` （墙上的棕色旗帜） - ``` green_wall_banner ``` （墙上的绿色旗帜） - ``` red_wall_banner ``` （墙上的红色旗帜） - ``` black_wall_banner ``` （墙上的黑色旗帜）

## bars

- 包含所有栏杆。

- #bars（9项） - ``` iron_bars ``` （铁栏杆） - ``` copper_bars ``` （铜栏杆） - ``` exposed_copper_bars ``` （斑驳的铜栏杆） - ``` weathered_copper_bars ``` （锈蚀的铜栏杆） - ``` oxidized_copper_bars ``` （氧化的铜栏杆） - ``` waxed_copper_bars ``` （涂蜡的铜栏杆） - ``` waxed_exposed_copper_bars ``` （涂蜡的斑驳铜栏杆） - ``` waxed_weathered_copper_bars ``` （涂蜡的锈蚀铜栏杆） - ``` waxed_oxidized_copper_bars ``` （涂蜡的氧化铜栏杆）

## base_stone_nether

- 持有该标签的方块在生成时可以被远古残骸替代。

- #base_stone_nether（3项） - ``` netherrack ``` （下界岩） - ``` basalt ``` （玄武岩） - ``` blackstone ``` （黑石）

## base_stone_overworld

- 用于决定作为地下矿石生成时，泥土、沙砾、花岗岩、闪长岩、安山岩、凝灰岩、黏土能取代哪些方块。
- 用于决定“滴水石簇”能取代哪些方块。
- 用于“滴水石簇”的生成。
- 用于 ``` #dripstone_replaceable_blocks ``` 和 ``` #moss_replaceable ``` 。

- #base_stone_overworld（6项） - ``` stone ``` （石头） - ``` granite ``` （花岗岩） - ``` diorite ``` （闪长岩） - ``` andesite ``` （安山岩） - ``` tuff ``` （凝灰岩） - ``` deepslate ``` （深板岩）

## bats_spawnable_on

- 用于决定蝙蝠可以在哪些方块上自然生成。

- #bats_spawnable_on（1项） - ``` #base_stone_overworld ```

## beacon_base_blocks

- 拥有此标签的方块在信标下方放置时能激活信标。

- #beacon_base_blocks（5项） - ``` netherite_block ``` （下界合金块） - ``` emerald_block ``` （绿宝石块） - ``` diamond_block ``` （钻石块） - ``` gold_block ``` （金块） - ``` iron_block ``` （铁块）

## beds

- 用于确定猫是否会在上面坐下或躺下。
- 用于检测村民的兴趣点。
- 用于决定可以睡在哪些方块中。
- 用于确定幼年村民可以跳到哪些方块上。
- 向该标签添加不分前后两部分的方块可能会导致游戏崩溃。

- #beds（16项） - ``` white_bed ``` （白色床） - ``` orange_bed ``` （橙色床） - ``` magenta_bed ``` （品红色床） - ``` light_blue_bed ``` （淡蓝色床） - ``` yellow_bed ``` （黄色床） - ``` lime_bed ``` （黄绿色床） - ``` pink_bed ``` （粉红色床） - ``` gray_bed ``` （灰色床） - ``` light_gray_bed ``` （淡灰色床） - ``` cyan_bed ``` （青色床） - ``` purple_bed ``` （紫色床） - ``` blue_bed ``` （蓝色床） - ``` brown_bed ``` （棕色床） - ``` green_bed ``` （绿色床） - ``` red_bed ``` （红色床） - ``` black_bed ``` （黑色床）

## bee_attractive

- 蜜蜂会尝试在这些方块上授粉。

- #bee_attractive（29项） - ``` dandelion ``` （蒲公英） - ``` open_eyeblossom ``` （张开的眼眸花） - ``` poppy ``` （虞美人） - ``` blue_orchid ``` （兰花） - ``` allium ``` （绒球葱） - ``` azure_bluet ``` （蓝花美耳草） - ``` red_tulip ``` （红色郁金香） - ``` orange_tulip ``` （橙色郁金香） - ``` white_tulip ``` （白色郁金香） - ``` pink_tulip ``` （粉红色郁金香） - ``` oxeye_daisy ``` （滨菊） - ``` cornflower ``` （矢车菊） - ``` lily_of_the_valley ``` （铃兰） - ``` wither_rose ``` （凋灵玫瑰） - ``` torchflower ``` （火把花） - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` peony ``` （牡丹） - ``` rose_bush ``` （玫瑰丛） - ``` pitcher_plant ``` （瓶子草） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_leaves ``` （樱花树叶） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` chorus_flower ``` （紫颂花） - ``` spore_blossom ``` （孢子花） - ``` cactus_flower ``` （仙人掌花）

## bee_growables

- 当蜜蜂对这些植株进行授粉时，它们会生长一个阶段。
- 从该标签中删除方块没有效果。

- #bee_growables（4项） - ``` #crops ``` - ``` sweet_berry_bush ``` （甜浆果丛） - ``` cave_vines ``` （洞穴藤蔓） - ``` cave_vines_plant ``` （洞穴藤蔓植株）

## beehives

- 确定当蜜蜂带有花粉时可以为哪些方块填充蜂蜜。
- 该标签中的方块可以用带有玻璃瓶或剪刀的发射器清除蜂蜜。
- 用于进度文件husbandry/safely_harvest_honey.json。

- #beehives（2项） - ``` bee_nest ``` （蜂巢） - ``` beehive ``` （蜂箱）

## beneath_bamboo_podzol_replaceable

- 定义适用于竹子下方可被灰化土替代的方块。

- #beneath_bamboo_podzol_replaceable（1项） - ``` #substrate_overworld ```

## beneath_tree_podzol_replaceable

- 定义适用于树木下方可被灰化土替代的方块。

- #beneath_tree_podzol_replaceable（1项） - ``` #substrate_overworld ```

## birch_logs

- 用于 ``` #logs_that_burn ``` 。

- #birch_logs（4项） - ``` birch_log ``` （白桦原木） - ``` birch_wood ``` （白桦木） - ``` stripped_birch_log ``` （去皮白桦原木） - ``` stripped_birch_wood ``` （去皮白桦木）

## blocks_dolphin_jump

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 海豚飞出水面时会将这些方块视为阻挡方块。

- #blocks_dolphin_jump（1项） - ``` #blocks_motion ```

## blocks_fluid_flow

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 阻止流体流动的方块。

- #blocks_fluid_flow（2项） - ``` #blocks_motion ``` - ``` #all_signs ```

## blocks_lava_fire_spread

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 阻止熔岩生成火的方块。

- #blocks_lava_fire_spread（1项） - ``` #blocks_motion ```

## blocks_motion

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 所有被认为阻止运动的方块。

- #blocks_motion（2项） - ``` #blocks_motion_no_leaves ``` - ``` #leaves ```

## blocks_motion_in_heightmap

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 用于高度图 ``` MOTION_BLOCKING ``` 的计算。

- #blocks_motion_in_heightmap（1项） - ``` #blocks_motion ```

## blocks_motion_in_heightmap_no_leaves

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 用于高度图 ``` MOTION_BLOCKING_NO_LEAVES ``` 的计算。

- #blocks_motion_in_heightmap_no_leaves（1项） - ``` #blocks_motion_no_leaves ```

## blocks_motion_no_leaves

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #blocks_motion_no_leaves（340项） - ``` #all_hanging_signs ``` - ``` #chains ``` - ``` #banners ``` - ``` #shulker_boxes ``` - ``` #lanterns ``` - ``` #candle_cakes ``` - ``` #lightning_rods ``` - ``` #beds ``` - ``` #wool ``` - ``` #bars ``` - ``` #cauldrons ``` - ``` #terracotta ``` - ``` #glazed_terracotta ``` - ``` #concrete ``` - ``` #concrete_powders ``` - ``` #copper ``` - ``` #copper_chests ``` - ``` #pressure_plates ``` - ``` #fences ``` - ``` #fence_gates ``` - ``` #walls ``` - ``` #coral_blocks ``` - ``` #planks ``` - ``` #logs ``` - ``` #bamboo_blocks ``` - ``` #wooden_shelves ``` - ``` #stairs ``` - ``` #slabs ``` - ``` #doors ``` - ``` #trapdoors ``` - ``` #ores ``` - ``` #speleothems ``` - ``` #grass_blocks ``` - ``` #dirt ``` - ``` #sand ``` - ``` #ice ``` - ``` #stone_bricks ``` - ``` #anvil ``` - ``` white_stained_glass ``` （白色染色玻璃） - ``` orange_stained_glass ``` （橙色染色玻璃） - ``` magenta_stained_glass ``` （品红色染色玻璃） - ``` light_blue_stained_glass ``` （淡蓝色染色玻璃） - ``` yellow_stained_glass ``` （黄色染色玻璃） - ``` lime_stained_glass ``` （黄绿色染色玻璃） - ``` pink_stained_glass ``` （粉红色染色玻璃） - ``` gray_stained_glass ``` （灰色染色玻璃） - ``` light_gray_stained_glass ``` （淡灰色染色玻璃） - ``` cyan_stained_glass ``` （青色染色玻璃） - ``` purple_stained_glass ``` （紫色染色玻璃） - ``` blue_stained_glass ``` （蓝色染色玻璃） - ``` brown_stained_glass ``` （棕色染色玻璃） - ``` green_stained_glass ``` （绿色染色玻璃） - ``` red_stained_glass ``` （红色染色玻璃） - ``` black_stained_glass ``` （黑色染色玻璃） - ``` white_stained_glass_pane ``` （白色染色玻璃板） - ``` orange_stained_glass_pane ``` （橙色染色玻璃板） - ``` magenta_stained_glass_pane ``` （品红色染色玻璃板） - ``` light_blue_stained_glass_pane ``` （淡蓝色染色玻璃板） - ``` yellow_stained_glass_pane ``` （黄色染色玻璃板） - ``` lime_stained_glass_pane ``` （黄绿色染色玻璃板） - ``` pink_stained_glass_pane ``` （粉红色染色玻璃板） - ``` gray_stained_glass_pane ``` （灰色染色玻璃板） - ``` light_gray_stained_glass_pane ``` （淡灰色染色玻璃板） - ``` cyan_stained_glass_pane ``` （青色染色玻璃板） - ``` purple_stained_glass_pane ``` （紫色染色玻璃板） - ``` blue_stained_glass_pane ``` （蓝色染色玻璃板） - ``` brown_stained_glass_pane ``` （棕色染色玻璃板） - ``` green_stained_glass_pane ``` （绿色染色玻璃板） - ``` red_stained_glass_pane ``` （红色染色玻璃板） - ``` black_stained_glass_pane ``` （黑色染色玻璃板） - ``` cut_copper ``` （切制铜块） - ``` exposed_cut_copper ``` （斑驳的切制铜块） - ``` weathered_cut_copper ``` （锈蚀的切制铜块） - ``` oxidized_cut_copper ``` （氧化的切制铜块） - ``` waxed_cut_copper ``` （涂蜡的切制铜块） - ``` waxed_exposed_cut_copper ``` （涂蜡的斑驳切制铜块） - ``` waxed_weathered_cut_copper ``` （涂蜡的锈蚀切制铜块） - ``` waxed_oxidized_cut_copper ``` （涂蜡的氧化切制铜块） - ``` chiseled_copper ``` （雕纹铜块） - ``` exposed_chiseled_copper ``` （斑驳的雕纹铜块） - ``` weathered_chiseled_copper ``` （锈蚀的雕纹铜块） - ``` oxidized_chiseled_copper ``` （氧化的雕纹铜块） - ``` waxed_chiseled_copper ``` （涂蜡的雕纹铜块） - ``` waxed_exposed_chiseled_copper ``` （涂蜡的斑驳雕纹铜块） - ``` waxed_weathered_chiseled_copper ``` （涂蜡的锈蚀雕纹铜块） - ``` waxed_oxidized_chiseled_copper ``` （涂蜡的氧化雕纹铜块） - ``` copper_grate ``` （铜格栅） - ``` exposed_copper_grate ``` （斑驳的铜格栅） - ``` weathered_copper_grate ``` （锈蚀的铜格栅） - ``` oxidized_copper_grate ``` （氧化的铜格栅） - ``` waxed_copper_grate ``` （涂蜡的铜格栅） - ``` waxed_exposed_copper_grate ``` （涂蜡的斑驳铜格栅） - ``` waxed_weathered_copper_grate ``` （涂蜡的锈蚀铜格栅） - ``` waxed_oxidized_copper_grate ``` （涂蜡的氧化铜格栅） - ``` copper_bulb ``` （铜灯） - ``` exposed_copper_bulb ``` （斑驳的铜灯） - ``` weathered_copper_bulb ``` （锈蚀的铜灯） - ``` oxidized_copper_bulb ``` （氧化的铜灯） - ``` waxed_copper_bulb ``` （涂蜡的铜灯） - ``` waxed_exposed_copper_bulb ``` （涂蜡的斑驳铜灯） - ``` waxed_weathered_copper_bulb ``` （涂蜡的锈蚀铜灯） - ``` waxed_oxidized_copper_bulb ``` （涂蜡的氧化铜灯） - ``` dead_tube_coral_wall_fan ``` （墙上的失活管珊瑚扇） - ``` dead_brain_coral_wall_fan ``` （墙上的失活脑纹珊瑚扇） - ``` dead_bubble_coral_wall_fan ``` （墙上的失活气泡珊瑚扇） - ``` dead_fire_coral_wall_fan ``` （墙上的失活火珊瑚扇） - ``` dead_horn_coral_wall_fan ``` （墙上的失活鹿角珊瑚扇） - ``` moving_piston ``` （移动的活塞） - ``` piston_head ``` （活塞头） - ``` cake ``` （蛋糕） - ``` turtle_egg ``` （海龟蛋） - ``` dried_ghast ``` （失水恶魂） - ``` dead_tube_coral_block ``` （失活的管珊瑚块） - ``` dead_brain_coral_block ``` （失活的脑纹珊瑚块） - ``` dead_bubble_coral_block ``` （失活的气泡珊瑚块） - ``` dead_fire_coral_block ``` （失活的火珊瑚块） - ``` dead_horn_coral_block ``` （失活的鹿角珊瑚块） - ``` dead_tube_coral ``` （失活的管珊瑚） - ``` dead_brain_coral ``` （失活的脑纹珊瑚） - ``` dead_bubble_coral ``` （失活的气泡珊瑚） - ``` dead_fire_coral ``` （失活的火珊瑚） - ``` dead_horn_coral ``` （失活的鹿角珊瑚） - ``` dead_tube_coral_fan ``` （失活的管珊瑚扇） - ``` dead_brain_coral_fan ``` （失活的脑纹珊瑚扇） - ``` dead_bubble_coral_fan ``` （失活的气泡珊瑚扇） - ``` dead_fire_coral_fan ``` （失活的火珊瑚扇） - ``` dead_horn_coral_fan ``` （失活的鹿角珊瑚扇） - ``` conduit ``` （潮涌核心） - ``` bamboo ``` （竹子） - ``` bell ``` （钟） - ``` amethyst_cluster ``` （紫水晶簇） - ``` large_amethyst_bud ``` （大型紫晶芽） - ``` medium_amethyst_bud ``` （中型紫晶芽） - ``` small_amethyst_bud ``` （小型紫晶芽） - ``` sculk_vein ``` （幽匿脉络） - ``` stone ``` （石头） - ``` granite ``` （花岗岩） - ``` polished_granite ``` （磨制花岗岩） - ``` diorite ``` （闪长岩） - ``` polished_diorite ``` （磨制闪长岩） - ``` andesite ``` （安山岩） - ``` polished_andesite ``` （磨制安山岩） - ``` cobblestone ``` （圆石） - ``` bamboo_mosaic ``` （竹马赛克） - ``` bedrock ``` （基岩） - ``` gravel ``` （沙砾） - ``` suspicious_gravel ``` （可疑的沙砾） - ``` mangrove_roots ``` （红树根） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` sponge ``` （海绵） - ``` wet_sponge ``` （湿海绵） - ``` glass ``` （玻璃） - ``` lapis_block ``` （青金石块） - ``` dispenser ``` （发射器） - ``` sandstone ``` （砂岩） - ``` chiseled_sandstone ``` （雕纹砂岩） - ``` cut_sandstone ``` （切制砂岩） - ``` note_block ``` （音符盒） - ``` sticky_piston ``` （黏性活塞） - ``` piston ``` （活塞） - ``` gold_block ``` （金块） - ``` iron_block ``` （铁块） - ``` bricks ``` （红砖块） - ``` tnt ``` （TNT） - ``` bookshelf ``` （书架） - ``` chiseled_bookshelf ``` （雕纹书架） - ``` mossy_cobblestone ``` （苔石） - ``` obsidian ``` （黑曜石） - ``` spawner ``` （刷怪笼） - ``` creaking_heart ``` （嘎枝之心） - ``` chest ``` （箱子） - ``` diamond_block ``` （钻石块） - ``` crafting_table ``` （工作台） - ``` farmland ``` （耕地） - ``` furnace ``` （熔炉） - ``` snow_block ``` （雪块） - ``` cactus ``` （仙人掌） - ``` clay ``` （黏土） - ``` jukebox ``` （唱片机） - ``` netherrack ``` （下界岩） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土） - ``` basalt ``` （玄武岩） - ``` polished_basalt ``` （磨制玄武岩） - ``` glowstone ``` （荧石） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` jack_o_lantern ``` （南瓜灯） - ``` packed_mud ``` （泥坯） - ``` mud_bricks ``` （泥砖） - ``` infested_stone ``` （虫蚀石头） - ``` infested_cobblestone ``` （虫蚀圆石） - ``` infested_stone_bricks ``` （虫蚀石砖） - ``` infested_mossy_stone_bricks ``` （虫蚀苔石砖） - ``` infested_cracked_stone_bricks ``` （虫蚀裂纹石砖） - ``` infested_chiseled_stone_bricks ``` （虫蚀雕纹石砖） - ``` brown_mushroom_block ``` （棕色蘑菇方块） - ``` red_mushroom_block ``` （红色蘑菇方块） - ``` mushroom_stem ``` （蘑菇柄） - ``` glass_pane ``` （玻璃板） - ``` pumpkin ``` （南瓜） - ``` melon ``` （西瓜） - ``` resin_block ``` （树脂块） - ``` resin_bricks ``` （树脂砖块） - ``` chiseled_resin_bricks ``` （雕纹树脂砖块） - ``` nether_bricks ``` （下界砖块） - ``` enchanting_table ``` （附魔台） - ``` brewing_stand ``` （酿造台） - ``` end_portal_frame ``` （末地传送门框架） - ``` end_stone ``` （末地石） - ``` dragon_egg ``` （龙蛋） - ``` redstone_lamp ``` （红石灯） - ``` ender_chest ``` （末影箱） - ``` emerald_block ``` （绿宝石块） - ``` command_block ``` （命令方块） - ``` beacon ``` （信标） - ``` trapped_chest ``` （陷阱箱） - ``` daylight_detector ``` （阳光探测器） - ``` redstone_block ``` （红石块） - ``` hopper ``` （漏斗） - ``` quartz_block ``` （石英块） - ``` chiseled_quartz_block ``` （雕纹石英块） - ``` quartz_pillar ``` （石英柱） - ``` dropper ``` （投掷器） - ``` slime_block ``` （黏液块） - ``` barrier ``` （屏障） - ``` prismarine ``` （海晶石） - ``` prismarine_bricks ``` （海晶石砖） - ``` dark_prismarine ``` （暗海晶石） - ``` sea_lantern ``` （海晶灯） - ``` hay_block ``` （干草捆） - ``` coal_block ``` （煤炭块） - ``` red_sandstone ``` （红砂岩） - ``` chiseled_red_sandstone ``` （雕纹红砂岩） - ``` cut_red_sandstone ``` （切制红砂岩） - ``` smooth_stone ``` （平滑石头） - ``` smooth_sandstone ``` （平滑砂岩） - ``` smooth_quartz ``` （平滑石英块） - ``` smooth_red_sandstone ``` （平滑红砂岩） - ``` purpur_block ``` （紫珀块） - ``` purpur_pillar ``` （紫珀柱） - ``` end_stone_bricks ``` （末地石砖） - ``` dirt_path ``` （土径） - ``` repeating_command_block ``` （循环型命令方块） - ``` chain_command_block ``` （连锁型命令方块） - ``` magma_block ``` （岩浆块） - ``` nether_wart_block ``` （下界疣块） - ``` red_nether_bricks ``` （红色下界砖块） - ``` bone_block ``` （骨块） - ``` observer ``` （侦测器） - ``` dried_kelp_block ``` （干海带块） - ``` sniffer_egg ``` （嗅探兽蛋） - ``` loom ``` （织布机） - ``` barrel ``` （木桶） - ``` smoker ``` （烟熏炉） - ``` blast_furnace ``` （高炉） - ``` cartography_table ``` （制图台） - ``` fletching_table ``` （制箭台） - ``` grindstone ``` （砂轮） - ``` lectern ``` （讲台） - ``` smithing_table ``` （锻造台） - ``` stonecutter ``` （切石机） - ``` campfire ``` （营火） - ``` soul_campfire ``` （灵魂营火） - ``` warped_nylium ``` （诡异菌岩） - ``` warped_wart_block ``` （诡异疣块） - ``` crimson_nylium ``` （绯红菌岩） - ``` shroomlight ``` （菌光体） - ``` structure_block ``` （结构方块） - ``` jigsaw ``` （拼图方块） - ``` test_block ``` （测试方块） - ``` test_instance_block ``` （测试实例方块） - ``` composter ``` （堆肥桶） - ``` target ``` （标靶） - ``` bee_nest ``` （蜂巢） - ``` beehive ``` （蜂箱） - ``` honey_block ``` （蜂蜜块） - ``` honeycomb_block ``` （蜜脾块） - ``` netherite_block ``` （下界合金块） - ``` ancient_debris ``` （远古残骸） - ``` crying_obsidian ``` （哭泣的黑曜石） - ``` respawn_anchor ``` （重生锚） - ``` lodestone ``` （磁石） - ``` blackstone ``` （黑石） - ``` polished_blackstone ``` （磨制黑石） - ``` polished_blackstone_bricks ``` （磨制黑石砖） - ``` cracked_polished_blackstone_bricks ``` （裂纹磨制黑石砖） - ``` chiseled_polished_blackstone ``` （雕纹磨制黑石） - ``` gilded_blackstone ``` （镶金黑石） - ``` chiseled_nether_bricks ``` （雕纹下界砖块） - ``` cracked_nether_bricks ``` （裂纹下界砖块） - ``` quartz_bricks ``` （石英砖） - ``` amethyst_block ``` （紫水晶块） - ``` budding_amethyst ``` （紫水晶母岩） - ``` tuff ``` （凝灰岩） - ``` polished_tuff ``` （磨制凝灰岩） - ``` chiseled_tuff ``` （雕纹凝灰岩） - ``` tuff_bricks ``` （凝灰岩砖） - ``` chiseled_tuff_bricks ``` （雕纹凝灰岩砖） - ``` sulfur ``` （硫黄） - ``` potent_sulfur ``` （烈性硫黄） - ``` polished_sulfur ``` （磨制硫黄） - ``` sulfur_bricks ``` （硫黄砖） - ``` chiseled_sulfur ``` （雕纹硫黄） - ``` cinnabar ``` （朱砂） - ``` polished_cinnabar ``` （磨制朱砂） - ``` cinnabar_bricks ``` （朱砂砖） - ``` chiseled_cinnabar ``` （雕纹朱砂） - ``` calcite ``` （方解石） - ``` tinted_glass ``` （遮光玻璃） - ``` sculk_sensor ``` （幽匿感测体） - ``` calibrated_sculk_sensor ``` （校频幽匿感测体） - ``` sculk ``` （幽匿块） - ``` sculk_catalyst ``` （幽匿催发体） - ``` sculk_shrieker ``` （幽匿尖啸体） - ``` dripstone_block ``` （滴水石块） - ``` moss_block ``` （苔藓块） - ``` mud ``` （泥巴） - ``` deepslate ``` （深板岩） - ``` cobbled_deepslate ``` （深板岩圆石） - ``` polished_deepslate ``` （磨制深板岩） - ``` deepslate_tiles ``` （深板岩瓦） - ``` deepslate_bricks ``` （深板岩砖） - ``` chiseled_deepslate ``` （雕纹深板岩） - ``` cracked_deepslate_bricks ``` （裂纹深板岩砖） - ``` cracked_deepslate_tiles ``` （裂纹深板岩瓦） - ``` infested_deepslate ``` （虫蚀深板岩） - ``` smooth_basalt ``` （平滑玄武岩） - ``` raw_iron_block ``` （粗铁块） - ``` raw_copper_block ``` （粗铜块） - ``` raw_gold_block ``` （粗金块） - ``` ochre_froglight ``` （赭黄蛙明灯） - ``` verdant_froglight ``` （青翠蛙明灯） - ``` pearlescent_froglight ``` （珠光蛙明灯） - ``` reinforced_deepslate ``` （强化深板岩） - ``` decorated_pot ``` （饰纹陶罐） - ``` crafter ``` （合成器） - ``` trial_spawner ``` （试炼刷怪笼） - ``` vault ``` （宝库） - ``` pale_moss_block ``` （苍白苔藓块） - ``` straw_bed ``` （麦秆床）

## blocks_wind_charge_explosions

- 能够阻挡风弹爆炸的方块。

- #blocks_wind_charge_explosions（2项） - ``` barrier ``` （屏障） - ``` bedrock ``` （基岩）

## buttons

- #buttons（2项） - ``` #wooden_buttons ``` - ``` #stone_buttons ```

## camel_sand_step_sound_blocks

- 当骆驼在拥有此标签的方块上行走时，播放骆驼在沙子上方行走音效。

- #camel_sand_step_sound_blocks（2项） - ``` #sand ``` - ``` #concrete_powders ```

## camels_spawnable_on

- 指定哪些方块可以生成骆驼。

- #camels_spawnable_on（1项） - ``` #sand ```

## campfires

- 蜜蜂、鹦鹉和海龟将此标记的方块视为造成火焰伤害并相应地进行路径查找。
- 营火使用这个标签来确定它们是否被点燃。
- 打火石用这个标签来确定它是否能点燃营火。给此标签添加方块无效果。
- 属于该标签的方块若具有 ``` lit ``` 方块状态，则当被喷溅水瓶击中时，其 ``` lit ``` 值将被设为false。

- #campfires（2项） - ``` campfire ``` （营火） - ``` soul_campfire ``` （灵魂营火）

## candle_cakes

- 拥有这个标签的方块会被视为插上蜡烛的蛋糕并能被点燃，除非它们的 ``` lit ``` 方块状态被设定为false。

- #candle_cakes（17项） - ``` candle_cake ``` （插上蜡烛的蛋糕） - ``` white_candle_cake ``` （插上白色蜡烛的蛋糕） - ``` orange_candle_cake ``` （插上橙色蜡烛的蛋糕） - ``` magenta_candle_cake ``` （插上品红色蜡烛的蛋糕） - ``` light_blue_candle_cake ``` （插上淡蓝色蜡烛的蛋糕） - ``` yellow_candle_cake ``` （插上黄色蜡烛的蛋糕） - ``` lime_candle_cake ``` （插上黄绿色蜡烛的蛋糕） - ``` pink_candle_cake ``` （插上粉红色蜡烛的蛋糕） - ``` gray_candle_cake ``` （插上灰色蜡烛的蛋糕） - ``` light_gray_candle_cake ``` （插上淡灰色蜡烛的蛋糕） - ``` cyan_candle_cake ``` （插上青色蜡烛的蛋糕） - ``` purple_candle_cake ``` （插上紫色蜡烛的蛋糕） - ``` blue_candle_cake ``` （插上蓝色蜡烛的蛋糕） - ``` brown_candle_cake ``` （插上棕色蜡烛的蛋糕） - ``` green_candle_cake ``` （插上绿色蜡烛的蛋糕） - ``` red_candle_cake ``` （插上红色蜡烛的蛋糕） - ``` black_candle_cake ``` （插上黑色蜡烛的蛋糕）

## candles

- 拥有这个标签的方块会被视为蜡烛并能够点燃，如果有 ``` lit ``` 和​ ``` waterlogged ``` 这两个方块状态且都是false。

- #candles（17项） - ``` candle ``` （蜡烛） - ``` white_candle ``` （白色蜡烛） - ``` orange_candle ``` （橙色蜡烛） - ``` magenta_candle ``` （品红色蜡烛） - ``` light_blue_candle ``` （淡蓝色蜡烛） - ``` yellow_candle ``` （黄色蜡烛） - ``` lime_candle ``` （黄绿色蜡烛） - ``` pink_candle ``` （粉红色蜡烛） - ``` gray_candle ``` （灰色蜡烛） - ``` light_gray_candle ``` （淡灰色蜡烛） - ``` cyan_candle ``` （青色蜡烛） - ``` purple_candle ``` （紫色蜡烛） - ``` blue_candle ``` （蓝色蜡烛） - ``` brown_candle ``` （棕色蜡烛） - ``` green_candle ``` （绿色蜡烛） - ``` red_candle ``` （红色蜡烛） - ``` black_candle ``` （黑色蜡烛）

## cannot_place_basalt_pillar_on

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #cannot_place_basalt_pillar_on（10项） - ``` lava ``` （熔岩） - ``` bedrock ``` （基岩） - ``` magma_block ``` （岩浆块） - ``` soul_sand ``` （灵魂沙） - ``` nether_bricks ``` （下界砖块） - ``` nether_brick_fence ``` （下界砖栅栏） - ``` nether_brick_stairs ``` （下界砖楼梯） - ``` nether_wart ``` （下界疣） - ``` chest ``` （箱子） - ``` spawner ``` （刷怪笼）

## cannot_replace_below_tree_trunk

- #cannot_replace_below_tree_trunk（4项） - ``` #dirt ``` - ``` #mud ``` - ``` #moss_blocks ``` - ``` podzol ``` （灰化土）

## cannot_support_kelp

- 海带无法放置在这些方块上。

- #cannot_support_kelp（1项） - ``` magma_block ``` （岩浆块）

## cannot_support_seagrass

- 海草或高海草无法放置在这些方块上。

- #cannot_support_seagrass（1项） - ``` magma_block ``` （岩浆块）

## cannot_support_snow_layer

- 雪无法放置在这些方块上。

- #cannot_support_snow_layer（3项） - ``` ice ``` （冰） - ``` packed_ice ``` （浮冰） - ``` barrier ``` （屏障）

## can_glide_through

- 可以攀爬且不打断滑翔的方块。

- #can_glide_through（6项） - ``` vine ``` （藤蔓） - ``` twisting_vines ``` （缠怨藤） - ``` twisting_vines_plant ``` （缠怨藤植株） - ``` weeping_vines ``` （垂泪藤） - ``` weeping_vines_plant ``` （垂泪藤植株） - ``` #cave_vines ```

## cats_can_lie_on

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 猫可以躺在上面的方块。

- #cats_can_lie_on（1项） - ``` #beds ```

## cats_can_sit_on

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 猫可以坐在上面的方块。

- #cats_can_sit_on（3项） - ``` furnace ``` （熔炉） - ``` chest ``` （箱子） - ``` #beds ```

## cauldrons

- 这个标签被用于确认寻路过程。

- #cauldrons（4项） - ``` cauldron ``` （炼药锅） - ``` water_cauldron ``` （装有水的炼药锅） - ``` lava_cauldron ``` （装有熔岩的炼药锅） - ``` powder_snow_cauldron ``` （装有细雪的炼药锅）

## causes_continuous_geyser_eruptions

- 烈性硫黄在这些方块上方时会尝试生成持续的间歇泉。

- #causes_continuous_geyser_eruptions（1项） - ``` lava ``` （熔岩）

## causes_periodic_geyser_eruptions

- 烈性硫黄在这些方块上方时会尝试生成非持续的间歇泉。

- #causes_periodic_geyser_eruptions（1项） - ``` magma_block ``` （岩浆块）

## causes_suffocation

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 被游戏视为视野阻挡方块的方块。如果方块碰撞箱完整，则始终被视为视野阻挡方块。

- #causes_suffocation（1项） - ``` #blocks_motion ```

## cave_vines

- 用于 ``` #moss_replaceable ``` 。

- #cave_vines（2项） - ``` cave_vines_plant ``` （洞穴藤蔓植株） - ``` cave_vines ``` （洞穴藤蔓）

## ceiling_hanging_signs

- 用于 ``` #all_hanging_signs ``` 。

- #ceiling_hanging_signs（13项） - ``` oak_hanging_sign ``` （悬挂式橡木告示牌） - ``` spruce_hanging_sign ``` （悬挂式云杉木告示牌） - ``` birch_hanging_sign ``` （悬挂式白桦木告示牌） - ``` acacia_hanging_sign ``` （悬挂式金合欢木告示牌） - ``` cherry_hanging_sign ``` （悬挂式樱花木告示牌） - ``` jungle_hanging_sign ``` （悬挂式丛林木告示牌） - ``` dark_oak_hanging_sign ``` （悬挂式深色橡木告示牌） - ``` pale_oak_hanging_sign ``` （悬挂式苍白橡木告示牌） - ``` crimson_hanging_sign ``` （悬挂式绯红木告示牌） - ``` warped_hanging_sign ``` （悬挂式诡异木告示牌） - ``` mangrove_hanging_sign ``` （悬挂式红树木告示牌） - ``` poplar_hanging_sign ``` （悬挂式杨木告示牌） - ``` bamboo_hanging_sign ``` （悬挂式竹告示牌）

## chains

- 包含所有锁链。

- #chains（9项） - ``` iron_chain ``` （铁链） - ``` copper_chain ``` （铜链） - ``` exposed_copper_chain ``` （斑驳的铜链） - ``` weathered_copper_chain ``` （锈蚀的铜链） - ``` oxidized_copper_chain ``` （氧化的铜链） - ``` waxed_copper_chain ``` （涂蜡的铜链） - ``` waxed_exposed_copper_chain ``` （涂蜡的斑驳铜链） - ``` waxed_weathered_copper_chain ``` （涂蜡的锈蚀铜链） - ``` waxed_oxidized_copper_chain ``` （涂蜡的氧化铜链）

## cherry_logs

- 用于 ``` #logs_that_burn ``` 。

- #cherry_logs（4项） - ``` cherry_log ``` （樱花原木） - ``` cherry_wood ``` （樱花木） - ``` stripped_cherry_log ``` （去皮樱花原木） - ``` stripped_cherry_wood ``` （去皮樱花木）

## climbable

- 用于生物寻路。
- 该标签用于确定哪些方块可以攀爬。 - 向该标签添加其他的方块时，为了使生物能够攀爬，这个方块碰撞箱必须足够小，以使生物碰撞箱的中心可以位于这一方块。 - 这意味着不能从侧面攀登箱子等方块，而可以从顶部攀登。 - 如果删除了脚手架，则生物将无法平滑地爬升，但仍可以跳上并潜下。

- #climbable（9项） - ``` ladder ``` （梯子） - ``` vine ``` （藤蔓） - ``` scaffolding ``` （脚手架） - ``` weeping_vines ``` （垂泪藤） - ``` weeping_vines_plant ``` （垂泪藤植株） - ``` twisting_vines ``` （缠怨藤） - ``` twisting_vines_plant ``` （缠怨藤植株） - ``` cave_vines ``` （洞穴藤蔓） - ``` cave_vines_plant ``` （洞穴藤蔓植株）

## coal_ores

- #coal_ores（2项） - ``` coal_ore ``` （煤矿石） - ``` deepslate_coal_ore ``` （深层煤矿石）

## combination_step_sound_blocks

- 此处定义的方块的行走音效是否与其下方方块的行走音效合并。

- #combination_step_sound_blocks（8项） - ``` #wool_carpets ``` - ``` moss_carpet ``` （覆地苔藓） - ``` pale_moss_carpet ``` （苍白覆地苔藓） - ``` snow ``` （雪） - ``` nether_sprouts ``` （下界苗） - ``` warped_roots ``` （诡异菌索） - ``` crimson_roots ``` （绯红菌索） - ``` resin_clump ``` （树脂团）

## completes_find_tree_tutorial

- 拥有这个标签的方块可用于完成“找到一棵树”教学提示。

- #completes_find_tree_tutorial（3项） - ``` #logs ``` - ``` #leaves ``` - ``` #wart_blocks ```

## concrete

- #concrete（16项） - ``` white_concrete ``` （白色混凝土） - ``` orange_concrete ``` （橙色混凝土） - ``` magenta_concrete ``` （品红色混凝土） - ``` light_blue_concrete ``` （淡蓝色混凝土） - ``` yellow_concrete ``` （黄色混凝土） - ``` lime_concrete ``` （黄绿色混凝土） - ``` pink_concrete ``` （粉红色混凝土） - ``` gray_concrete ``` （灰色混凝土） - ``` light_gray_concrete ``` （淡灰色混凝土） - ``` cyan_concrete ``` （青色混凝土） - ``` purple_concrete ``` （紫色混凝土） - ``` blue_concrete ``` （蓝色混凝土） - ``` brown_concrete ``` （棕色混凝土） - ``` green_concrete ``` （绿色混凝土） - ``` red_concrete ``` （红色混凝土） - ``` black_concrete ``` （黑色混凝土）

## concrete_powders

- #concrete_powders（16项） - ``` white_concrete_powder ``` （白色混凝土粉末） - ``` orange_concrete_powder ``` （橙色混凝土粉末） - ``` magenta_concrete_powder ``` （品红色混凝土粉末） - ``` light_blue_concrete_powder ``` （淡蓝色混凝土粉末） - ``` yellow_concrete_powder ``` （黄色混凝土粉末） - ``` lime_concrete_powder ``` （黄绿色混凝土粉末） - ``` pink_concrete_powder ``` （粉红色混凝土粉末） - ``` gray_concrete_powder ``` （灰色混凝土粉末） - ``` light_gray_concrete_powder ``` （淡灰色混凝土粉末） - ``` cyan_concrete_powder ``` （青色混凝土粉末） - ``` purple_concrete_powder ``` （紫色混凝土粉末） - ``` blue_concrete_powder ``` （蓝色混凝土粉末） - ``` brown_concrete_powder ``` （棕色混凝土粉末） - ``` green_concrete_powder ``` （绿色混凝土粉末） - ``` red_concrete_powder ``` （红色混凝土粉末） - ``` black_concrete_powder ``` （黑色混凝土粉末）

## concrete_slabs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #concrete_slabs（16项） - ``` white_concrete_slab ``` （白色混凝土台阶） - ``` orange_concrete_slab ``` （橙色混凝土台阶） - ``` magenta_concrete_slab ``` （品红色混凝土台阶） - ``` light_blue_concrete_slab ``` （淡蓝色混凝土台阶） - ``` yellow_concrete_slab ``` （黄色混凝土台阶） - ``` lime_concrete_slab ``` （黄绿色混凝土台阶） - ``` pink_concrete_slab ``` （粉红色混凝土台阶） - ``` gray_concrete_slab ``` （灰色混凝土台阶） - ``` light_gray_concrete_slab ``` （淡灰色混凝土台阶） - ``` cyan_concrete_slab ``` （青色混凝土台阶） - ``` purple_concrete_slab ``` （紫色混凝土台阶） - ``` blue_concrete_slab ``` （蓝色混凝土台阶） - ``` brown_concrete_slab ``` （棕色混凝土台阶） - ``` green_concrete_slab ``` （绿色混凝土台阶） - ``` red_concrete_slab ``` （红色混凝土台阶） - ``` black_concrete_slab ``` （黑色混凝土台阶）

## concrete_stairs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #concrete_stairs（16项） - ``` white_concrete_stairs ``` （白色混凝土楼梯） - ``` orange_concrete_stairs ``` （橙色混凝土楼梯） - ``` magenta_concrete_stairs ``` （品红色混凝土楼梯） - ``` light_blue_concrete_stairs ``` （淡蓝色混凝土楼梯） - ``` yellow_concrete_stairs ``` （黄色混凝土楼梯） - ``` lime_concrete_stairs ``` （黄绿色混凝土楼梯） - ``` pink_concrete_stairs ``` （粉红色混凝土楼梯） - ``` gray_concrete_stairs ``` （灰色混凝土楼梯） - ``` light_gray_concrete_stairs ``` （淡灰色混凝土楼梯） - ``` cyan_concrete_stairs ``` （青色混凝土楼梯） - ``` purple_concrete_stairs ``` （紫色混凝土楼梯） - ``` blue_concrete_stairs ``` （蓝色混凝土楼梯） - ``` brown_concrete_stairs ``` （棕色混凝土楼梯） - ``` green_concrete_stairs ``` （绿色混凝土楼梯） - ``` red_concrete_stairs ``` （红色混凝土楼梯） - ``` black_concrete_stairs ``` （黑色混凝土楼梯）

## convertable_to_mud [ 原文如此 ] / convertible_to_mud

- 对拥有此标签的方块使用水瓶时可以将其转化为泥巴。

- #convertable_to_mud（3项） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` rooted_dirt ``` （缠根泥土）

- #convertible_to_mud（3项） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` rooted_dirt ``` （缠根泥土）

## copper

- 包含所有铜块。

- #copper（8项） - ``` copper_block ``` （铜块） - ``` exposed_copper ``` （斑驳的铜块） - ``` weathered_copper ``` （锈蚀的铜块） - ``` oxidized_copper ``` （氧化的铜块） - ``` waxed_copper_block ``` （涂蜡的铜块） - ``` waxed_exposed_copper ``` （涂蜡的斑驳铜块） - ``` waxed_weathered_copper ``` （涂蜡的锈蚀铜块） - ``` waxed_oxidized_copper ``` （涂蜡的氧化铜块）

## copper_chests

- 包含所有铜箱子。

- #copper_chests（8项） - ``` copper_chest ``` （铜箱子） - ``` exposed_copper_chest ``` （斑驳的铜箱子） - ``` weathered_copper_chest ``` （锈蚀的铜箱子） - ``` oxidized_copper_chest ``` （氧化的铜箱子） - ``` waxed_copper_chest ``` （涂蜡的铜箱子） - ``` waxed_exposed_copper_chest ``` （涂蜡的斑驳铜箱子） - ``` waxed_weathered_copper_chest ``` （涂蜡的锈蚀铜箱子） - ``` waxed_oxidized_copper_chest ``` （涂蜡的氧化铜箱子）

## copper_golem_statues

- 包含所有铜傀儡像。

- #copper_golem_statues（8项） - ``` copper_golem_statue ``` （铜傀儡像） - ``` exposed_copper_golem_statue ``` （斑驳的铜傀儡像） - ``` weathered_copper_golem_statue ``` （锈蚀的铜傀儡像） - ``` oxidized_copper_golem_statue ``` （氧化的铜傀儡像） - ``` waxed_copper_golem_statue ``` （涂蜡的铜傀儡像） - ``` waxed_exposed_copper_golem_statue ``` （涂蜡的斑驳铜傀儡像） - ``` waxed_weathered_copper_golem_statue ``` （涂蜡的锈蚀铜傀儡像） - ``` waxed_oxidized_copper_golem_statue ``` （涂蜡的氧化铜傀儡像）

## copper_ores

- #copper_ores（2项） - ``` copper_ore ``` （铜矿石） - ``` deepslate_copper_ore ``` （深层铜矿石）

## coral_blocks

- 用于生成珊瑚礁。
- 对单个海泡菜使用骨粉，如果海泡菜位于这些方块上方，会生长出更多的海泡菜。

- #coral_blocks（5项） - ``` tube_coral_block ``` （管珊瑚块） - ``` brain_coral_block ``` （脑纹珊瑚块） - ``` bubble_coral_block ``` （气泡珊瑚块） - ``` fire_coral_block ``` （火珊瑚块） - ``` horn_coral_block ``` （鹿角珊瑚块）

## coral_plants

- 用于 ``` #corals ``` 。

- #coral_plants（5项） - ``` tube_coral ``` （管珊瑚） - ``` brain_coral ``` （脑纹珊瑚） - ``` bubble_coral ``` （气泡珊瑚） - ``` fire_coral ``` （火珊瑚） - ``` horn_coral ``` （鹿角珊瑚）

## corals

- 用于生成珊瑚礁。

- #corals（6项） - ``` #coral_plants ``` - ``` tube_coral_fan ``` （管珊瑚扇） - ``` brain_coral_fan ``` （脑纹珊瑚扇） - ``` bubble_coral_fan ``` （气泡珊瑚扇） - ``` fire_coral_fan ``` （火珊瑚扇） - ``` horn_coral_fan ``` （鹿角珊瑚扇）

## crimson_stems

- 用于 ``` #logs ``` 。

- #crimson_stems（4项） - ``` crimson_stem ``` （绯红菌柄） - ``` stripped_crimson_stem ``` （去皮绯红菌柄） - ``` crimson_hyphae ``` （绯红菌核） - ``` stripped_crimson_hyphae ``` （去皮绯红菌核）

## crops

- 用于 ``` #bee_growables ``` 。

- #crops（8项） - ``` beetroots ``` （甜菜根） - ``` carrots ``` （胡萝卜） - ``` potatoes ``` （马铃薯） - ``` wheat ``` （小麦植株） - ``` melon_stem ``` （西瓜茎） - ``` pumpkin_stem ``` （南瓜茎） - ``` torchflower_crop ``` （火把花植株） - ``` pitcher_crop ``` （瓶子草植株）

## cushion_uses_collision_shape

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 坐垫的放置判定对拥有这个标签的方块会按照轮廓箱而不是互动箱计算点击方向。

- #cushion_uses_collision_shape（3项） - ``` #cauldrons ``` - ``` hopper ``` （漏斗） - ``` composter ``` （堆肥桶）

## crystal_sound_blocks

- 拥有这个标签的方块在被踩中时会播放水晶的音效。

- #crystal_sound_blocks（2项） - ``` amethyst_block ``` （紫水晶块） - ``` budding_amethyst ``` （紫水晶母岩）

## dampens_vibrations

- 实体不会在拥有这个标签的方块上发出振动。

- #dampens_vibrations（4项） - ``` #wool ``` - ``` #wool_carpets ``` - ``` #wool_slabs ``` - ``` #wool_stairs ```

## dark_oak_logs

- 用于 ``` #logs_that_burn ``` 。

- #dark_oak_logs（4项） - ``` dark_oak_log ``` （深色橡木原木） - ``` dark_oak_wood ``` （深色橡木） - ``` stripped_dark_oak_log ``` （去皮深色橡木原木） - ``` stripped_dark_oak_wood ``` （去皮深色橡木）

## deepslate_ore_replaceables

- 用于决定在世界生成时能被深层矿石替换的方块，浅层变种见 ``` #stone_ore_replaceables ``` 。

- #deepslate_ore_replaceables（2项） - ``` deepslate ``` （深板岩） - ``` tuff ``` （凝灰岩）

## default_immune_to

- 生物默认不会将这些方块视为危险方块。

- #default_immune_to（0项） - 无内容

## diamond_ores

- #diamond_ores（2项） - ``` diamond_ore ``` （钻石矿石） - ``` deepslate_diamond_ore ``` （深层钻石矿石）

## dirt

- 用于 ``` #moss_replaceable ``` 。

- #dirt（3项） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` rooted_dirt ``` （缠根泥土）

## does_not_block_hoppers

- 用来决定哪些碰撞箱完整的方块不会阻挡漏斗捕捉物品实体。

- #does_not_block_hoppers（1项） - ``` #beehives ```

## doors

- 实体寻路过程中不会尝试跳跃上拥有这个标签的方块。
- 生成僵尸村庄时拥有此标签的方块有概率被转换为空气。

- #doors（10项） - ``` #wooden_doors ``` - ``` copper_door ``` （铜门） - ``` exposed_copper_door ``` （斑驳的铜门） - ``` weathered_copper_door ``` （锈蚀的铜门） - ``` oxidized_copper_door ``` （氧化的铜门） - ``` waxed_copper_door ``` （涂蜡的铜门） - ``` waxed_exposed_copper_door ``` （涂蜡的斑驳铜门） - ``` waxed_weathered_copper_door ``` （涂蜡的锈蚀铜门） - ``` waxed_oxidized_copper_door ``` （涂蜡的氧化铜门） - ``` iron_door ``` （铁门）

## dragon_immune

- 用来决定哪些方块不能被末影龙摧毁。

- #dragon_immune（19项） - ``` barrier ``` （屏障） - ``` bedrock ``` （基岩） - ``` end_portal ``` （末地传送门） - ``` end_portal_frame ``` （末地传送门框架） - ``` end_gateway ``` （末地折跃门） - ``` command_block ``` （命令方块） - ``` repeating_command_block ``` （循环型命令方块） - ``` chain_command_block ``` （连锁型命令方块） - ``` structure_block ``` （结构方块） - ``` jigsaw ``` （拼图方块） - ``` moving_piston ``` （移动的活塞） - ``` obsidian ``` （黑曜石） - ``` crying_obsidian ``` （哭泣的黑曜石） - ``` end_stone ``` （末地石） - ``` iron_bars ``` （铁栏杆） - ``` respawn_anchor ``` （重生锚） - ``` reinforced_deepslate ``` （强化深板岩） - ``` test_block ``` （测试方块） - ``` test_instance_block ``` （测试实例方块）

## dragon_transparent

- #dragon_transparent（2项） - ``` light ``` （光源方块） - ``` #fire ```

## dripstone_replaceable_blocks

- #dripstone_replaceable_blocks（1项） - ``` #base_stone_overworld ```

## edible_for_sheep

- 用来决定哪些方块可被绵羊吃掉。

- #edible_for_sheep（4项） - ``` short_grass ``` （矮草丛） - ``` short_dry_grass ``` （矮枯草丛） - ``` tall_dry_grass ``` （高枯草丛） - ``` fern ``` （蕨）

## emerald_ores

- #emerald_ores（2项） - ``` emerald_ore ``` （绿宝石矿石） - ``` deepslate_emerald_ore ``` （深层绿宝石矿石）

## enables_bubble_column_drag_down

- 流体在这些方块上方生成气泡柱涡流。

- #enables_bubble_column_drag_down（1项） - ``` magma_block ``` （岩浆块）

## enables_bubble_column_push_up

- 流体在这些方块上方生成气泡柱涌流。

- #enables_bubble_column_push_up（1项） - ``` soul_sand ``` （灵魂沙）

## enchantment_power_provider

- 可以增加附魔台最大附魔等级的方块。

- #enchantment_power_provider（1项） - ``` bookshelf ``` （书架）

## enchantment_power_transmitter

- 不会阻断附魔台附魔等级增益的方块。

- #enchantment_power_transmitter（1项） - ``` #replaceable ```

## enderman_holdable

- 用来决定哪些方块可以被末影人拾起。

- #enderman_holdable（23项） - ``` #small_flowers ``` - ``` #dirt ``` - ``` #mud ``` - ``` #moss_blocks ``` - ``` #grass_blocks ``` - ``` sand ``` （沙子） - ``` red_sand ``` （红沙） - ``` gravel ``` （沙砾） - ``` brown_mushroom ``` （棕色蘑菇） - ``` red_mushroom ``` （红色蘑菇） - ``` tnt ``` （TNT） - ``` cactus ``` （仙人掌） - ``` clay ``` （黏土） - ``` pumpkin ``` （南瓜） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` melon ``` （西瓜） - ``` crimson_fungus ``` （绯红菌） - ``` crimson_nylium ``` （绯红菌岩） - ``` crimson_roots ``` （绯红菌索） - ``` warped_fungus ``` （诡异菌） - ``` warped_nylium ``` （诡异菌岩） - ``` warped_roots ``` （诡异菌索） - ``` cactus_flower ``` （仙人掌花）

## entities_can_teleport_to

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 实体被允许传送到的方块。
- ``` / spreadplayers ``` 视这些方块为有效传送位置。

- #entities_can_teleport_to（1项） - ``` #blocks_motion ```

## fall_damage_resetting

- 用来决定除液体外哪些方块可以重置摔落伤害。

- #fall_damage_resetting（3项） - ``` #climbable ``` - ``` sweet_berry_bush ``` （甜浆果丛） - ``` cobweb ``` （蜘蛛网）

## features_cannot_replace

- #features_cannot_replace（7项） - ``` bedrock ``` （基岩） - ``` spawner ``` （刷怪笼） - ``` chest ``` （箱子） - ``` end_portal_frame ``` （末地传送门框架） - ``` reinforced_deepslate ``` （强化深板岩） - ``` trial_spawner ``` （试炼刷怪笼） - ``` vault ``` （宝库）

## fence_gates

- #fence_gates（13项） - ``` acacia_fence_gate ``` （金合欢木栅栏门） - ``` birch_fence_gate ``` （白桦木栅栏门） - ``` dark_oak_fence_gate ``` （深色橡木栅栏门） - ``` pale_oak_fence_gate ``` （苍白橡木栅栏门） - ``` jungle_fence_gate ``` （丛林木栅栏门） - ``` oak_fence_gate ``` （橡木栅栏门） - ``` spruce_fence_gate ``` （云杉木栅栏门） - ``` crimson_fence_gate ``` （绯红木栅栏门） - ``` warped_fence_gate ``` （诡异木栅栏门） - ``` mangrove_fence_gate ``` （红树木栅栏门） - ``` bamboo_fence_gate ``` （竹栅栏门） - ``` cherry_fence_gate ``` （樱花木栅栏门） - ``` poplar_fence_gate ``` （杨木栅栏门）

## fences

- 生物将这个标签中的所有方块视为栅栏，并据此进行寻路。
- 可以将拴绳连接到此标签中的方块上。
- 拴绳结实体使用此标签来检测它是否应该断开。

- #fences（2项） - ``` #wooden_fences ``` - ``` nether_brick_fence ``` （下界砖栅栏）

## fire

- 当检测到有效的未激活下界传送门时，将忽略此标签中的方块，并将在激活后将其删除。
- 生物将这个标签中的所有方块视作火并据此寻路。
- 此标签中的方块不会阻挡沙子等方块掉落。
- 能够扑灭火焰的药水会移除此标签中的方块。
- 用于 ``` #dragon_transparent ``` 。

- #fire（2项） - ``` fire ``` （火） - ``` soul_fire ``` （灵魂火）

## flower_pots

- #flower_pots（40项） - ``` flower_pot ``` （花盆） - ``` potted_open_eyeblossom ``` （张开的眼眸花盆栽） - ``` potted_closed_eyeblossom ``` （闭合的眼眸花盆栽） - ``` potted_poppy ``` （虞美人盆栽） - ``` potted_blue_orchid ``` （兰花盆栽） - ``` potted_allium ``` （绒球葱盆栽） - ``` potted_azure_bluet ``` （蓝花美耳草盆栽） - ``` potted_red_tulip ``` （红色郁金香盆栽） - ``` potted_orange_tulip ``` （橙色郁金香盆栽） - ``` potted_white_tulip ``` （白色郁金香盆栽） - ``` potted_pink_tulip ``` （粉红色郁金香盆栽） - ``` potted_oxeye_daisy ``` （滨菊盆栽） - ``` potted_dandelion ``` （蒲公英盆栽） - ``` potted_oak_sapling ``` （橡树树苗盆栽） - ``` potted_spruce_sapling ``` （云杉树苗盆栽） - ``` potted_birch_sapling ``` （白桦树苗盆栽） - ``` potted_jungle_sapling ``` （丛林树苗盆栽） - ``` potted_acacia_sapling ``` （金合欢树苗盆栽） - ``` potted_dark_oak_sapling ``` （深色橡树树苗盆栽） - ``` potted_pale_oak_sapling ``` （苍白橡树树苗盆栽） - ``` potted_red_mushroom ``` （红色蘑菇盆栽） - ``` potted_brown_mushroom ``` （棕色蘑菇盆栽） - ``` potted_dead_bush ``` （枯萎的灌木盆栽） - ``` potted_fern ``` （蕨盆栽） - ``` potted_cactus ``` （仙人掌盆栽） - ``` potted_cornflower ``` （矢车菊盆栽） - ``` potted_lily_of_the_valley ``` （铃兰盆栽） - ``` potted_wither_rose ``` （凋灵玫瑰盆栽） - ``` potted_bamboo ``` （竹子盆栽） - ``` potted_crimson_fungus ``` （绯红菌盆栽） - ``` potted_warped_fungus ``` （诡异菌盆栽） - ``` potted_crimson_roots ``` （绯红菌索盆栽） - ``` potted_warped_roots ``` （诡异菌索盆栽） - ``` potted_azalea_bush ``` （杜鹃花丛盆栽） - ``` potted_flowering_azalea_bush ``` （盛开的杜鹃花丛盆栽） - ``` potted_mangrove_propagule ``` （红树胎生苗盆栽） - ``` potted_cherry_sapling ``` （樱花树苗盆栽） - ``` potted_torchflower ``` （火把花盆栽） - ``` potted_golden_dandelion ``` （金蒲公英盆栽） - ``` potted_poplar_sapling ``` （杨树树苗盆栽）

## flowers

- #flowers（15项） - ``` #small_flowers ``` - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` peony ``` （牡丹） - ``` rose_bush ``` （玫瑰丛） - ``` pitcher_plant ``` （瓶子草） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_leaves ``` （樱花树叶） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` chorus_flower ``` （紫颂花） - ``` spore_blossom ``` （孢子花） - ``` cactus_flower ``` （仙人掌花）

## forest_rock_can_place_on

- 定义哪些方块之上可放置 ``` forest_rock ``` 地物。

- #forest_rock_can_place_on（2项） - ``` #substrate_overworld ``` - ``` #base_stone_overworld ```

## foxes_spawnable_on

- 用于狐狸的生成判定。

- #foxes_spawnable_on（5项） - ``` grass_block ``` （草方块） - ``` snow ``` （雪） - ``` snow_block ``` （雪块） - ``` podzol ``` （灰化土） - ``` coarse_dirt ``` （砂土）

## fox_immune_to

- 狐狸不会将这些方块视为危险方块。

- #fox_immune_to（1项） - ``` sweet_berry_bush ``` （甜浆果丛）

## frog_prefer_jump_to

- #frog_prefer_jump_to（2项） - ``` lily_pad ``` （睡莲） - ``` big_dripleaf ``` （大型垂滴叶）

## frogs_spawnable_on

- 用于青蛙的生成判定。

- #frogs_spawnable_on（4项） - ``` grass_block ``` （草方块） - ``` mud ``` （泥巴） - ``` mangrove_roots ``` （红树根） - ``` muddy_mangrove_roots ``` （沾泥的红树根）

## geode_invalid_blocks

- #geode_invalid_blocks（6项） - ``` bedrock ``` （基岩） - ``` water ``` （水） - ``` lava ``` （熔岩） - ``` ice ``` （冰） - ``` packed_ice ``` （浮冰） - ``` blue_ice ``` （蓝冰）

## glazed_terracotta

- #glazed_terracotta（16项） - ``` white_glazed_terracotta ``` （白色带釉陶瓦） - ``` orange_glazed_terracotta ``` （橙色带釉陶瓦） - ``` magenta_glazed_terracotta ``` （品红色带釉陶瓦） - ``` light_blue_glazed_terracotta ``` （淡蓝色带釉陶瓦） - ``` yellow_glazed_terracotta ``` （黄色带釉陶瓦） - ``` lime_glazed_terracotta ``` （黄绿色带釉陶瓦） - ``` pink_glazed_terracotta ``` （粉红色带釉陶瓦） - ``` gray_glazed_terracotta ``` （灰色带釉陶瓦） - ``` light_gray_glazed_terracotta ``` （淡灰色带釉陶瓦） - ``` cyan_glazed_terracotta ``` （青色带釉陶瓦） - ``` purple_glazed_terracotta ``` （紫色带釉陶瓦） - ``` blue_glazed_terracotta ``` （蓝色带釉陶瓦） - ``` brown_glazed_terracotta ``` （棕色带釉陶瓦） - ``` green_glazed_terracotta ``` （绿色带釉陶瓦） - ``` red_glazed_terracotta ``` （红色带釉陶瓦） - ``` black_glazed_terracotta ``` （黑色带釉陶瓦）

## goats_spawnable_on

- #goats_spawnable_on（6项） - ``` #animals_spawnable_on ``` - ``` stone ``` （石头） - ``` snow ``` （雪） - ``` snow_block ``` （雪块） - ``` packed_ice ``` （浮冰） - ``` gravel ``` （沙砾）

## gold_ores

- #gold_ores（3项） - ``` gold_ore ``` （金矿石） - ``` nether_gold_ore ``` （下界金矿石） - ``` deepslate_gold_ore ``` （深层金矿石）

## grass_blocks

- #grass_blocks（3项） - ``` grass_block ``` （草方块） - ``` podzol ``` （灰化土） - ``` mycelium ``` （菌丝体）

## grows_crops

- 小麦植株、胡萝卜、马铃薯、甜菜根、火把花植株、瓶子草植株、南瓜茎、西瓜茎可以在这些方块上生长。

- #grows_crops（1项） - ``` farmland ``` （耕地）

## guarded_by_piglins

- 猪灵将与开启或摧毁拥有这个标签的方块的玩家敌对。

- #guarded_by_piglins（10项） - ``` #copper_chests ``` - ``` gold_block ``` （金块） - ``` barrel ``` （木桶） - ``` chest ``` （箱子） - ``` ender_chest ``` （末影箱） - ``` gilded_blackstone ``` （镶金黑石） - ``` trapped_chest ``` （陷阱箱） - ``` raw_gold_block ``` （粗金块） - ``` #shulker_boxes ``` - ``` #gold_ores ```

## happy_ghast_avoids

- 恶魂和快乐恶魂会倾向于远离这些方块。

- #happy_ghast_avoids（6项） - ``` sweet_berry_bush ``` （甜浆果丛） - ``` cactus ``` （仙人掌） - ``` wither_rose ``` （凋灵玫瑰） - ``` magma_block ``` （岩浆块） - ``` fire ``` （火） - ``` #speleothems ```

## height_specific_ore_replaceables

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 在Y=8以下时会被替换为深层变种的矿石。

- #height_specific_ore_replaceables（1项） - ``` tuff ``` （凝灰岩）

## hoglin_repellents

- 疣猪兽会远离这些方块。

- #hoglin_repellents（4项） - ``` warped_fungus ``` （诡异菌） - ``` potted_warped_fungus ``` （诡异菌盆栽） - ``` nether_portal ``` （下界传送门） - ``` respawn_anchor ``` （重生锚）

## huge_brown_mushroom_can_place_on

- 定义哪些方块之上可放置 ``` huge_brown_mushroom ``` 地物。

- #huge_brown_mushroom_can_place_on（5项） - ``` #substrate_overworld ``` - ``` mycelium ``` （菌丝体） - ``` podzol ``` （灰化土） - ``` crimson_nylium ``` （绯红菌岩） - ``` warped_nylium ``` （诡异菌岩）

## huge_red_mushroom_can_place_on

- 定义哪些方块之上可放置 ``` huge_red_mushroom ``` 地物。

- #huge_red_mushroom_can_place_on（5项） - ``` #substrate_overworld ``` - ``` mycelium ``` （菌丝体） - ``` podzol ``` （灰化土） - ``` crimson_nylium ``` （绯红菌岩） - ``` warped_nylium ``` （诡异菌岩）

## ice

- 海底废墟不会在这些方块上生成。

- #ice（4项） - ``` ice ``` （冰） - ``` packed_ice ``` （浮冰） - ``` blue_ice ``` （蓝冰） - ``` frosted_ice ``` （霜冰）

## ice_spike_replaceable

- 定义冰刺可替换哪些方块。

- #ice_spike_replaceable（3项） - ``` #substrate_overworld ``` - ``` snow_block ``` （雪块） - ``` ice ``` （冰）

## ice_melts_when_destroyed_above

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 冰在这些方块上时，若被破坏后允许生成水则会生成水。

- #ice_melts_when_destroyed_above（1项） - ``` #blocks_motion ```

## impermeable

- 这个标签下的方块的上方有液体时不会展示水滴/熔岩粒子效果。

- #impermeable（19项） - ``` white_stained_glass ``` （白色染色玻璃） - ``` orange_stained_glass ``` （橙色染色玻璃） - ``` magenta_stained_glass ``` （品红色染色玻璃） - ``` light_blue_stained_glass ``` （淡蓝色染色玻璃） - ``` yellow_stained_glass ``` （黄色染色玻璃） - ``` lime_stained_glass ``` （黄绿色染色玻璃） - ``` pink_stained_glass ``` （粉红色染色玻璃） - ``` gray_stained_glass ``` （灰色染色玻璃） - ``` light_gray_stained_glass ``` （淡灰色染色玻璃） - ``` cyan_stained_glass ``` （青色染色玻璃） - ``` purple_stained_glass ``` （紫色染色玻璃） - ``` blue_stained_glass ``` （蓝色染色玻璃） - ``` brown_stained_glass ``` （棕色染色玻璃） - ``` green_stained_glass ``` （绿色染色玻璃） - ``` red_stained_glass ``` （红色染色玻璃） - ``` black_stained_glass ``` （黑色染色玻璃） - ``` glass ``` （玻璃） - ``` tinted_glass ``` （遮光玻璃） - ``` barrier ``` （屏障）

## incorrect_for_copper_tool

- 标记为该标签的方块被铜质工具挖掘后不会掉落。

- #incorrect_for_copper_tool（2项） - ``` #needs_diamond_tool ``` - ``` #needs_iron_tool ```

## incorrect_for_diamond_tool

- 标记为该标签的方块被钻石质工具挖掘后不会掉落。

- #incorrect_for_diamond_tool（0项） - 无内容

## incorrect_for_gold_tool

- 标记为该标签的方块被金质工具挖掘后不会掉落。

- #incorrect_for_gold_tool（3项） - ``` #needs_diamond_tool ``` - ``` #needs_iron_tool ``` - ``` #needs_stone_tool ```

## incorrect_for_iron_tool

- 标记为该标签的方块被铁质工具挖掘后不会掉落。

- #incorrect_for_iron_tool（1项） - ``` #needs_diamond_tool ```

## incorrect_for_netherite_tool

- 标记为该标签的方块被下界合金质工具挖掘后不会掉落。

- #incorrect_for_netherite_tool（0项） - 无内容

## incorrect_for_stone_tool

- 标记为该标签的方块被石质工具挖掘后不会掉落。

- #incorrect_for_stone_tool（2项） - ``` #needs_diamond_tool ``` - ``` #needs_iron_tool ```

## incorrect_for_wooden_tool

- 标记为该标签的方块被木质工具挖掘后不会掉落。

- #incorrect_for_wooden_tool（3项） - ``` #needs_diamond_tool ``` - ``` #needs_iron_tool ``` - ``` #needs_stone_tool ```

## infiniburn_end

- 在末地中，火会在使用该标签的方块上无限燃烧。

- #infiniburn_end（2项） - ``` #infiniburn_overworld ``` - ``` bedrock ``` （基岩）

## infiniburn_nether

- 在下界中，火会在使用该标签的方块上无限燃烧。

- #infiniburn_nether（1项） - ``` #infiniburn_overworld ```

## infiniburn_overworld

- 在主世界中，火会在使用该标签的方块上无限燃烧。

- #infiniburn_overworld（2项） - ``` netherrack ``` （下界岩） - ``` magma_block ``` （岩浆块）

## inside_step_sound_blocks

- 拥有这个标签的方块在被踩中时会播放在雪地行走的音效。

- #inside_step_sound_blocks（8项） - ``` powder_snow ``` （细雪） - ``` sculk_vein ``` （幽匿脉络） - ``` glow_lichen ``` （发光地衣） - ``` lily_pad ``` （睡莲） - ``` small_amethyst_bud ``` （小型紫晶芽） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` leaf_litter ``` （枯叶堆）

## invalid_spawn_inside

- 这个位置上的方块和它上方的方块带有此标签，则不会被选为重生位置。

- #invalid_spawn_inside（2项） - ``` end_portal ``` （末地传送门） - ``` end_gateway ``` （末地折跃门）

## iron_ores

- #iron_ores（2项） - ``` iron_ore ``` （铁矿石） - ``` deepslate_iron_ore ``` （深层铁矿石）

## jungle_logs

- 可可豆可以放置其上。

- #jungle_logs（4项） - ``` jungle_log ``` （丛林原木） - ``` jungle_wood ``` （丛林木） - ``` stripped_jungle_log ``` （去皮丛林原木） - ``` stripped_jungle_wood ``` （去皮丛林木）

## lanterns

- 包含所有灯笼。

- #lanterns（10项） - ``` lantern ``` （灯笼） - ``` soul_lantern ``` （灵魂灯笼） - ``` copper_lantern ``` （铜灯笼） - ``` exposed_copper_lantern ``` （斑驳的铜灯笼） - ``` weathered_copper_lantern ``` （锈蚀的铜灯笼） - ``` oxidized_copper_lantern ``` （氧化的铜灯笼） - ``` waxed_copper_lantern ``` （涂蜡的铜灯笼） - ``` waxed_exposed_copper_lantern ``` （涂蜡的斑驳铜灯笼） - ``` waxed_weathered_copper_lantern ``` （涂蜡的锈蚀铜灯笼） - ``` waxed_oxidized_copper_lantern ``` （涂蜡的氧化铜灯笼）

## lightning_rods

- 包含所有避雷针。

- #lightning_rods（8项） - ``` lightning_rod ``` （避雷针） - ``` exposed_lightning_rod ``` （斑驳的避雷针） - ``` weathered_lightning_rod ``` （锈蚀的避雷针） - ``` oxidized_lightning_rod ``` （氧化的避雷针） - ``` waxed_lightning_rod ``` （涂蜡的避雷针） - ``` waxed_exposed_lightning_rod ``` （涂蜡的斑驳避雷针） - ``` waxed_weathered_lightning_rod ``` （涂蜡的锈蚀避雷针） - ``` waxed_oxidized_lightning_rod ``` （涂蜡的氧化避雷针）

## lapis_ores

- #lapis_ores（2项） - ``` lapis_ore ``` （青金石矿石） - ``` deepslate_lapis_ore ``` （深层青金石矿石）

## lava_pool_stone_cannot_replace

- #lava_pool_stone_cannot_replace（3项） - ``` #features_cannot_replace ``` - ``` #leaves ``` - ``` #logs ```

## leaves

- 此标签中的方块不会阻碍许多结构的生成，如奖励箱、树和巨型蘑菇。
- 用于确定某些方块是否可以放置其上。

- #leaves（14项） - ``` jungle_leaves ``` （丛林树叶） - ``` oak_leaves ``` （橡树树叶） - ``` spruce_leaves ``` （云杉树叶） - ``` pale_oak_leaves ``` （苍白橡树树叶） - ``` dark_oak_leaves ``` （深色橡树树叶） - ``` acacia_leaves ``` （金合欢树叶） - ``` birch_leaves ``` （白桦树叶） - ``` azalea_leaves ``` （杜鹃树叶） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` mangrove_leaves ``` （红树树叶） - ``` cherry_leaves ``` （樱花树叶） - ``` red_poplar_leaves ``` （红色杨树树叶） - ``` orange_poplar_leaves ``` （橙色杨树树叶） - ``` yellow_poplar_leaves ``` （黄色杨树树叶）

## logs

- 用于鹦鹉AI在方块上栖息时对方块的要求之一。
- 如果该标签的方块周围有树叶，树叶方块会将其 ``` distance ``` 方块状态设为与其最近的距离。

- #logs（3项） - ``` #logs_that_burn ``` - ``` #crimson_stems ``` - ``` #warped_stems ```

## logs_that_burn

- #logs_that_burn（10项） - ``` #dark_oak_logs ``` - ``` #pale_oak_logs ``` - ``` #oak_logs ``` - ``` #acacia_logs ``` - ``` #birch_logs ``` - ``` #jungle_logs ``` - ``` #spruce_logs ``` - ``` #mangrove_logs ``` - ``` #cherry_logs ``` - ``` #poplar_logs ```

## lush_ground_replaceable

- #lush_ground_replaceable（4项） - ``` #moss_replaceable ``` - ``` clay ``` （黏土） - ``` gravel ``` （沙砾） - ``` sand ``` （沙子）

## maintains_farmland

- 不会使耕地退化为泥土的方块。

- #maintains_farmland（13项） - ``` pumpkin_stem ``` （南瓜茎） - ``` attached_pumpkin_stem ``` （结果的南瓜茎） - ``` melon_stem ``` （西瓜茎） - ``` attached_melon_stem ``` （结果的西瓜茎） - ``` beetroots ``` （甜菜根） - ``` carrots ``` （胡萝卜） - ``` potatoes ``` （马铃薯） - ``` torchflower_crop ``` （火把花植株） - ``` torchflower ``` （火把花） - ``` pitcher_crop ``` （瓶子草植株） - ``` wheat ``` （小麦植株） - ``` moving_piston ``` （移动的活塞） - ``` #fence_gates ```

## mangrove_logs

- #mangrove_logs（4项） - ``` mangrove_log ``` （红树原木） - ``` mangrove_wood ``` （红树木） - ``` stripped_mangrove_log ``` （去皮红树原木） - ``` stripped_mangrove_wood ``` （去皮红树木）

## mangrove_logs_can_grow_through

- 红树生成时，红树原木可以穿过的方块。

- #mangrove_logs_can_grow_through（8项） - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` mangrove_roots ``` （红树根） - ``` mangrove_leaves ``` （红树树叶） - ``` mangrove_log ``` （红树原木） - ``` mangrove_propagule ``` （红树胎生苗） - ``` moss_carpet ``` （覆地苔藓） - ``` vine ``` （藤蔓）

## mangrove_roots_can_grow_through

- 红树生成时，红树根可以穿过的方块。

- #mangrove_roots_can_grow_through（7项） - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` mangrove_roots ``` （红树根） - ``` moss_carpet ``` （覆地苔藓） - ``` vine ``` （藤蔓） - ``` mangrove_propagule ``` （红树胎生苗） - ``` snow ``` （雪）

## mineable/axe

- 此标签内的方块用斧挖掘更快。

- #mineable/axe（55项） - ``` note_block ``` （音符盒） - ``` bamboo ``` （竹子） - ``` barrel ``` （木桶） - ``` bee_nest ``` （蜂巢） - ``` beehive ``` （蜂箱） - ``` big_dripleaf_stem ``` （大型垂滴叶茎） - ``` big_dripleaf ``` （大型垂滴叶） - ``` bookshelf ``` （书架） - ``` brown_mushroom_block ``` （棕色蘑菇方块） - ``` campfire ``` （营火） - ``` cartography_table ``` （制图台） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` chest ``` （箱子） - ``` chorus_flower ``` （紫颂花） - ``` chorus_plant ``` （紫颂植株） - ``` cocoa ``` （可可果） - ``` composter ``` （堆肥桶） - ``` crafting_table ``` （工作台） - ``` daylight_detector ``` （阳光探测器） - ``` fletching_table ``` （制箭台） - ``` glow_lichen ``` （发光地衣） - ``` jack_o_lantern ``` （南瓜灯） - ``` jukebox ``` （唱片机） - ``` ladder ``` （梯子） - ``` lectern ``` （讲台） - ``` loom ``` （织布机） - ``` melon ``` （西瓜） - ``` mushroom_stem ``` （蘑菇柄） - ``` pumpkin ``` （南瓜） - ``` red_mushroom_block ``` （红色蘑菇方块） - ``` smithing_table ``` （锻造台） - ``` soul_campfire ``` （灵魂营火） - ``` trapped_chest ``` （陷阱箱） - ``` vine ``` （藤蔓） - ``` #banners ``` - ``` #fence_gates ``` - ``` #logs ``` - ``` #planks ``` - ``` #signs ``` - ``` #wooden_buttons ``` - ``` #wooden_doors ``` - ``` #wooden_fences ``` - ``` #wooden_pressure_plates ``` - ``` #wooden_slabs ``` - ``` #wooden_stairs ``` - ``` #wooden_trapdoors ``` - ``` mangrove_roots ``` （红树根） - ``` #all_hanging_signs ``` - ``` bamboo_mosaic ``` （竹马赛克） - ``` bamboo_mosaic_slab ``` （竹马赛克台阶） - ``` bamboo_mosaic_stairs ``` （竹马赛克楼梯） - ``` #bamboo_blocks ``` - ``` chiseled_bookshelf ``` （雕纹书架） - ``` #wooden_shelves ``` - ``` creaking_heart ``` （嘎枝之心）

## mineable/hoe

- 此标签内的方块用锄挖掘更快。

- #mineable/hoe（19项） - ``` #leaves ``` - ``` nether_wart_block ``` （下界疣块） - ``` warped_wart_block ``` （诡异疣块） - ``` hay_block ``` （干草捆） - ``` dried_kelp_block ``` （干海带块） - ``` target ``` （标靶） - ``` shroomlight ``` （菌光体） - ``` sponge ``` （海绵） - ``` wet_sponge ``` （湿海绵） - ``` sculk_sensor ``` （幽匿感测体） - ``` calibrated_sculk_sensor ``` （校频幽匿感测体） - ``` moss_block ``` （苔藓块） - ``` moss_carpet ``` （覆地苔藓） - ``` pale_moss_block ``` （苍白苔藓块） - ``` pale_moss_carpet ``` （苍白覆地苔藓） - ``` sculk ``` （幽匿块） - ``` sculk_catalyst ``` （幽匿催发体） - ``` sculk_vein ``` （幽匿脉络） - ``` sculk_shrieker ``` （幽匿尖啸体）

## mineable/pickaxe

- 此标签内的方块用镐挖掘更快。

- #mineable/pickaxe（449项） - ``` stone ``` （石头） - ``` granite ``` （花岗岩） - ``` polished_granite ``` （磨制花岗岩） - ``` diorite ``` （闪长岩） - ``` polished_diorite ``` （磨制闪长岩） - ``` andesite ``` （安山岩） - ``` polished_andesite ``` （磨制安山岩） - ``` cobblestone ``` （圆石） - ``` gold_ore ``` （金矿石） - ``` deepslate_gold_ore ``` （深层金矿石） - ``` iron_ore ``` （铁矿石） - ``` deepslate_iron_ore ``` （深层铁矿石） - ``` coal_ore ``` （煤矿石） - ``` deepslate_coal_ore ``` （深层煤矿石） - ``` nether_gold_ore ``` （下界金矿石） - ``` lapis_ore ``` （青金石矿石） - ``` deepslate_lapis_ore ``` （深层青金石矿石） - ``` lapis_block ``` （青金石块） - ``` dispenser ``` （发射器） - ``` sandstone ``` （砂岩） - ``` chiseled_sandstone ``` （雕纹砂岩） - ``` cut_sandstone ``` （切制砂岩） - ``` gold_block ``` （金块） - ``` iron_block ``` （铁块） - ``` bricks ``` （红砖块） - ``` mossy_cobblestone ``` （苔石） - ``` obsidian ``` （黑曜石） - ``` spawner ``` （刷怪笼） - ``` diamond_ore ``` （钻石矿石） - ``` deepslate_diamond_ore ``` （深层钻石矿石） - ``` diamond_block ``` （钻石块） - ``` furnace ``` （熔炉） - ``` cobblestone_stairs ``` （圆石楼梯） - ``` stone_pressure_plate ``` （石头压力板） - ``` iron_door ``` （铁门） - ``` redstone_ore ``` （红石矿石） - ``` deepslate_redstone_ore ``` （深层红石矿石） - ``` netherrack ``` （下界岩） - ``` basalt ``` （玄武岩） - ``` polished_basalt ``` （磨制玄武岩） - ``` stone_bricks ``` （石砖） - ``` mossy_stone_bricks ``` （苔石砖） - ``` cracked_stone_bricks ``` （裂纹石砖） - ``` chiseled_stone_bricks ``` （雕纹石砖） - ``` brick_stairs ``` （红砖楼梯） - ``` stone_brick_stairs ``` （石砖楼梯） - ``` nether_bricks ``` （下界砖块） - ``` nether_brick_fence ``` （下界砖栅栏） - ``` nether_brick_stairs ``` （下界砖楼梯） - ``` enchanting_table ``` （附魔台） - ``` brewing_stand ``` （酿造台） - ``` end_stone ``` （末地石） - ``` sandstone_stairs ``` （砂岩楼梯） - ``` emerald_ore ``` （绿宝石矿石） - ``` deepslate_emerald_ore ``` （深层绿宝石矿石） - ``` ender_chest ``` （末影箱） - ``` emerald_block ``` （绿宝石块） - ``` light_weighted_pressure_plate ``` （轻质测重压力板） - ``` heavy_weighted_pressure_plate ``` （重质测重压力板） - ``` redstone_block ``` （红石块） - ``` nether_quartz_ore ``` （下界石英矿石） - ``` hopper ``` （漏斗） - ``` quartz_block ``` （石英块） - ``` chiseled_quartz_block ``` （雕纹石英块） - ``` quartz_pillar ``` （石英柱） - ``` quartz_stairs ``` （石英楼梯） - ``` dropper ``` （投掷器） - ``` iron_trapdoor ``` （铁活板门） - ``` prismarine ``` （海晶石） - ``` prismarine_bricks ``` （海晶石砖） - ``` dark_prismarine ``` （暗海晶石） - ``` prismarine_stairs ``` （海晶石楼梯） - ``` prismarine_brick_stairs ``` （海晶石砖楼梯） - ``` dark_prismarine_stairs ``` （暗海晶石楼梯） - ``` prismarine_slab ``` （海晶石台阶） - ``` prismarine_brick_slab ``` （海晶石砖台阶） - ``` dark_prismarine_slab ``` （暗海晶石台阶） - ``` terracotta ``` （陶瓦） - ``` coal_block ``` （煤炭块） - ``` red_sandstone ``` （红砂岩） - ``` chiseled_red_sandstone ``` （雕纹红砂岩） - ``` cut_red_sandstone ``` （切制红砂岩） - ``` red_sandstone_stairs ``` （红砂岩楼梯） - ``` stone_slab ``` （石头台阶） - ``` smooth_stone_slab ``` （平滑石头台阶） - ``` sandstone_slab ``` （砂岩台阶） - ``` cut_sandstone_slab ``` （切制砂岩台阶） - ``` petrified_oak_slab ``` （石化橡木台阶） - ``` cobblestone_slab ``` （圆石台阶） - ``` brick_slab ``` （红砖台阶） - ``` stone_brick_slab ``` （石砖台阶） - ``` nether_brick_slab ``` （下界砖台阶） - ``` quartz_slab ``` （石英台阶） - ``` red_sandstone_slab ``` （红砂岩台阶） - ``` cut_red_sandstone_slab ``` （切制红砂岩台阶） - ``` purpur_slab ``` （紫珀台阶） - ``` smooth_stone ``` （平滑石头） - ``` smooth_sandstone ``` （平滑砂岩） - ``` smooth_quartz ``` （平滑石英块） - ``` smooth_red_sandstone ``` （平滑红砂岩） - ``` purpur_block ``` （紫珀块） - ``` purpur_pillar ``` （紫珀柱） - ``` purpur_stairs ``` （紫珀楼梯） - ``` end_stone_bricks ``` （末地石砖） - ``` magma_block ``` （岩浆块） - ``` red_nether_bricks ``` （红色下界砖块） - ``` bone_block ``` （骨块） - ``` observer ``` （侦测器） - ``` dead_tube_coral_block ``` （失活的管珊瑚块） - ``` dead_brain_coral_block ``` （失活的脑纹珊瑚块） - ``` dead_bubble_coral_block ``` （失活的气泡珊瑚块） - ``` dead_fire_coral_block ``` （失活的火珊瑚块） - ``` dead_horn_coral_block ``` （失活的鹿角珊瑚块） - ``` tube_coral_block ``` （管珊瑚块） - ``` brain_coral_block ``` （脑纹珊瑚块） - ``` bubble_coral_block ``` （气泡珊瑚块） - ``` fire_coral_block ``` （火珊瑚块） - ``` horn_coral_block ``` （鹿角珊瑚块） - ``` dead_tube_coral ``` （失活的管珊瑚） - ``` dead_brain_coral ``` （失活的脑纹珊瑚） - ``` dead_bubble_coral ``` （失活的气泡珊瑚） - ``` dead_fire_coral ``` （失活的火珊瑚） - ``` dead_horn_coral ``` （失活的鹿角珊瑚） - ``` dead_tube_coral_fan ``` （失活的管珊瑚扇） - ``` dead_brain_coral_fan ``` （失活的脑纹珊瑚扇） - ``` dead_bubble_coral_fan ``` （失活的气泡珊瑚扇） - ``` dead_fire_coral_fan ``` （失活的火珊瑚扇） - ``` dead_horn_coral_fan ``` （失活的鹿角珊瑚扇） - ``` dead_tube_coral_wall_fan ``` （墙上的失活管珊瑚扇） - ``` dead_brain_coral_wall_fan ``` （墙上的失活脑纹珊瑚扇） - ``` dead_bubble_coral_wall_fan ``` （墙上的失活气泡珊瑚扇） - ``` dead_fire_coral_wall_fan ``` （墙上的失活火珊瑚扇） - ``` dead_horn_coral_wall_fan ``` （墙上的失活鹿角珊瑚扇） - ``` polished_granite_stairs ``` （磨制花岗岩楼梯） - ``` smooth_red_sandstone_stairs ``` （平滑红砂岩楼梯） - ``` mossy_stone_brick_stairs ``` （苔石砖楼梯） - ``` polished_diorite_stairs ``` （磨制闪长岩楼梯） - ``` mossy_cobblestone_stairs ``` （苔石楼梯） - ``` end_stone_brick_stairs ``` （末地石砖楼梯） - ``` stone_stairs ``` （石头楼梯） - ``` smooth_sandstone_stairs ``` （平滑砂岩楼梯） - ``` smooth_quartz_stairs ``` （平滑石英楼梯） - ``` granite_stairs ``` （花岗岩楼梯） - ``` andesite_stairs ``` （安山岩楼梯） - ``` red_nether_brick_stairs ``` （红色下界砖楼梯） - ``` polished_andesite_stairs ``` （磨制安山岩楼梯） - ``` diorite_stairs ``` （闪长岩楼梯） - ``` polished_granite_slab ``` （磨制花岗岩台阶） - ``` smooth_red_sandstone_slab ``` （平滑红砂岩台阶） - ``` mossy_stone_brick_slab ``` （苔石砖台阶） - ``` polished_diorite_slab ``` （磨制闪长岩台阶） - ``` mossy_cobblestone_slab ``` （苔石台阶） - ``` end_stone_brick_slab ``` （末地石砖台阶） - ``` smooth_sandstone_slab ``` （平滑砂岩台阶） - ``` smooth_quartz_slab ``` （平滑石英台阶） - ``` granite_slab ``` （花岗岩台阶） - ``` andesite_slab ``` （安山岩台阶） - ``` red_nether_brick_slab ``` （红色下界砖台阶） - ``` polished_andesite_slab ``` （磨制安山岩台阶） - ``` diorite_slab ``` （闪长岩台阶） - ``` smoker ``` （烟熏炉） - ``` blast_furnace ``` （高炉） - ``` grindstone ``` （砂轮） - ``` stonecutter ``` （切石机） - ``` bell ``` （钟） - ``` warped_nylium ``` （诡异菌岩） - ``` crimson_nylium ``` （绯红菌岩） - ``` netherite_block ``` （下界合金块） - ``` ancient_debris ``` （远古残骸） - ``` crying_obsidian ``` （哭泣的黑曜石） - ``` respawn_anchor ``` （重生锚） - ``` lodestone ``` （磁石） - ``` blackstone ``` （黑石） - ``` blackstone_stairs ``` （黑石楼梯） - ``` blackstone_slab ``` （黑石台阶） - ``` polished_blackstone ``` （磨制黑石） - ``` polished_blackstone_bricks ``` （磨制黑石砖） - ``` cracked_polished_blackstone_bricks ``` （裂纹磨制黑石砖） - ``` chiseled_polished_blackstone ``` （雕纹磨制黑石） - ``` polished_blackstone_brick_slab ``` （磨制黑石砖台阶） - ``` polished_blackstone_brick_stairs ``` （磨制黑石砖楼梯） - ``` gilded_blackstone ``` （镶金黑石） - ``` polished_blackstone_stairs ``` （磨制黑石楼梯） - ``` polished_blackstone_slab ``` （磨制黑石台阶） - ``` polished_blackstone_pressure_plate ``` （磨制黑石压力板） - ``` chiseled_nether_bricks ``` （雕纹下界砖块） - ``` cracked_nether_bricks ``` （裂纹下界砖块） - ``` quartz_bricks ``` （石英砖） - ``` tuff ``` （凝灰岩） - ``` calcite ``` （方解石） - ``` copper_ore ``` （铜矿石） - ``` deepslate_copper_ore ``` （深层铜矿石） - ``` dripstone_block ``` （滴水石块） - ``` deepslate ``` （深板岩） - ``` cobbled_deepslate ``` （深板岩圆石） - ``` cobbled_deepslate_stairs ``` （深板岩圆石楼梯） - ``` cobbled_deepslate_slab ``` （深板岩圆石台阶） - ``` polished_deepslate ``` （磨制深板岩） - ``` polished_deepslate_stairs ``` （磨制深板岩楼梯） - ``` polished_deepslate_slab ``` （磨制深板岩台阶） - ``` deepslate_tiles ``` （深板岩瓦） - ``` deepslate_tile_stairs ``` （深板岩瓦楼梯） - ``` deepslate_tile_slab ``` （深板岩瓦台阶） - ``` deepslate_bricks ``` （深板岩砖） - ``` deepslate_brick_stairs ``` （深板岩砖楼梯） - ``` deepslate_brick_slab ``` （深板岩砖台阶） - ``` chiseled_deepslate ``` （雕纹深板岩） - ``` cracked_deepslate_bricks ``` （裂纹深板岩砖） - ``` cracked_deepslate_tiles ``` （裂纹深板岩瓦） - ``` smooth_basalt ``` （平滑玄武岩） - ``` raw_iron_block ``` （粗铁块） - ``` raw_copper_block ``` （粗铜块） - ``` raw_gold_block ``` （粗金块） - ``` ice ``` （冰） - ``` packed_ice ``` （浮冰） - ``` blue_ice ``` （蓝冰） - ``` piston ``` （活塞） - ``` sticky_piston ``` （黏性活塞） - ``` piston_head ``` （活塞头） - ``` amethyst_cluster ``` （紫水晶簇） - ``` small_amethyst_bud ``` （小型紫晶芽） - ``` medium_amethyst_bud ``` （中型紫晶芽） - ``` large_amethyst_bud ``` （大型紫晶芽） - ``` amethyst_block ``` （紫水晶块） - ``` budding_amethyst ``` （紫水晶母岩） - ``` infested_cobblestone ``` （虫蚀圆石） - ``` infested_chiseled_stone_bricks ``` （虫蚀雕纹石砖） - ``` infested_cracked_stone_bricks ``` （虫蚀裂纹石砖） - ``` infested_deepslate ``` （虫蚀深板岩） - ``` infested_stone ``` （虫蚀石头） - ``` infested_mossy_stone_bricks ``` （虫蚀苔石砖） - ``` infested_stone_bricks ``` （虫蚀石砖） - ``` #stone_buttons ``` - ``` #walls ``` - ``` #shulker_boxes ``` - ``` #anvil ``` - ``` #cauldrons ``` - ``` #rails ``` - ``` conduit ``` （潮涌核心） - ``` mud_bricks ``` （泥砖） - ``` mud_brick_stairs ``` （泥砖楼梯） - ``` mud_brick_slab ``` （泥砖台阶） - ``` packed_mud ``` （泥坯） - ``` crafter ``` （合成器） - ``` tuff_slab ``` （凝灰岩台阶） - ``` tuff_stairs ``` （凝灰岩楼梯） - ``` tuff_wall ``` （凝灰岩墙） - ``` chiseled_tuff ``` （雕纹凝灰岩） - ``` polished_tuff ``` （磨制凝灰岩） - ``` polished_tuff_slab ``` （磨制凝灰岩台阶） - ``` polished_tuff_stairs ``` （磨制凝灰岩楼梯） - ``` polished_tuff_wall ``` （磨制凝灰岩墙） - ``` tuff_bricks ``` （凝灰岩砖） - ``` tuff_brick_slab ``` （凝灰岩砖台阶） - ``` tuff_brick_stairs ``` （凝灰岩砖楼梯） - ``` tuff_brick_wall ``` （凝灰岩砖墙） - ``` chiseled_tuff_bricks ``` （雕纹凝灰岩砖） - ``` heavy_core ``` （沉重核心） - ``` resin_bricks ``` （树脂砖块） - ``` resin_brick_slab ``` （树脂砖台阶） - ``` resin_brick_wall ``` （树脂砖墙） - ``` resin_brick_stairs ``` （树脂砖楼梯） - ``` chiseled_resin_bricks ``` （雕纹树脂砖块） - ``` cinnabar ``` （朱砂） - ``` cinnabar_slab ``` （朱砂台阶） - ``` cinnabar_stairs ``` （朱砂楼梯） - ``` cinnabar_wall ``` （朱砂墙） - ``` polished_cinnabar ``` （磨制朱砂） - ``` polished_cinnabar_slab ``` （磨制朱砂台阶） - ``` polished_cinnabar_stairs ``` （磨制朱砂楼梯） - ``` polished_cinnabar_wall ``` （磨制朱砂墙） - ``` cinnabar_bricks ``` （朱砂砖） - ``` cinnabar_brick_slab ``` （朱砂砖台阶） - ``` cinnabar_brick_stairs ``` （朱砂砖楼梯） - ``` cinnabar_brick_wall ``` （朱砂砖墙） - ``` chiseled_cinnabar ``` （雕纹朱砂） - ``` sulfur ``` （硫黄） - ``` potent_sulfur ``` （烈性硫黄） - ``` sulfur_slab ``` （硫黄台阶） - ``` sulfur_stairs ``` （硫黄楼梯） - ``` sulfur_wall ``` （硫黄墙） - ``` polished_sulfur ``` （磨制硫黄） - ``` polished_sulfur_slab ``` （磨制硫黄台阶） - ``` polished_sulfur_stairs ``` （磨制硫黄楼梯） - ``` polished_sulfur_wall ``` （磨制硫黄墙） - ``` sulfur_bricks ``` （硫黄砖） - ``` sulfur_brick_slab ``` （硫黄砖台阶） - ``` sulfur_brick_stairs ``` （硫黄砖楼梯） - ``` sulfur_brick_wall ``` （硫黄砖墙） - ``` chiseled_sulfur ``` （雕纹硫黄） - ``` #copper_chests ``` - ``` #copper_golem_statues ``` - ``` #lightning_rods ``` - ``` #lanterns ``` - ``` #chains ``` - ``` #bars ``` - ``` copper_block ``` （铜块） - ``` exposed_copper ``` （斑驳的铜块） - ``` weathered_copper ``` （锈蚀的铜块） - ``` oxidized_copper ``` （氧化的铜块） - ``` waxed_copper_block ``` （涂蜡的铜块） - ``` waxed_exposed_copper ``` （涂蜡的斑驳铜块） - ``` waxed_weathered_copper ``` （涂蜡的锈蚀铜块） - ``` waxed_oxidized_copper ``` （涂蜡的氧化铜块） - ``` copper_bulb ``` （铜灯） - ``` exposed_copper_bulb ``` （斑驳的铜灯） - ``` weathered_copper_bulb ``` （锈蚀的铜灯） - ``` oxidized_copper_bulb ``` （氧化的铜灯） - ``` waxed_copper_bulb ``` （涂蜡的铜灯） - ``` waxed_exposed_copper_bulb ``` （涂蜡的斑驳铜灯） - ``` waxed_weathered_copper_bulb ``` （涂蜡的锈蚀铜灯） - ``` waxed_oxidized_copper_bulb ``` （涂蜡的氧化铜灯） - ``` cut_copper ``` （切制铜块） - ``` exposed_cut_copper ``` （斑驳的切制铜块） - ``` weathered_cut_copper ``` （锈蚀的切制铜块） - ``` oxidized_cut_copper ``` （氧化的切制铜块） - ``` waxed_cut_copper ``` （涂蜡的切制铜块） - ``` waxed_exposed_cut_copper ``` （涂蜡的斑驳切制铜块） - ``` waxed_weathered_cut_copper ``` （涂蜡的锈蚀切制铜块） - ``` waxed_oxidized_cut_copper ``` （涂蜡的氧化切制铜块） - ``` chiseled_copper ``` （雕纹铜块） - ``` exposed_chiseled_copper ``` （斑驳的雕纹铜块） - ``` weathered_chiseled_copper ``` （锈蚀的雕纹铜块） - ``` oxidized_chiseled_copper ``` （氧化的雕纹铜块） - ``` waxed_chiseled_copper ``` （涂蜡的雕纹铜块） - ``` waxed_exposed_chiseled_copper ``` （涂蜡的斑驳雕纹铜块） - ``` waxed_weathered_chiseled_copper ``` （涂蜡的锈蚀雕纹铜块） - ``` waxed_oxidized_chiseled_copper ``` （涂蜡的氧化雕纹铜块） - ``` cut_copper_stairs ``` （切制铜楼梯） - ``` exposed_cut_copper_stairs ``` （斑驳的切制铜楼梯） - ``` weathered_cut_copper_stairs ``` （锈蚀的切制铜楼梯） - ``` oxidized_cut_copper_stairs ``` （氧化的切制铜楼梯） - ``` waxed_cut_copper_stairs ``` （涂蜡的切制铜楼梯） - ``` waxed_exposed_cut_copper_stairs ``` （涂蜡的斑驳切制铜楼梯） - ``` waxed_weathered_cut_copper_stairs ``` （涂蜡的锈蚀切制铜楼梯） - ``` waxed_oxidized_cut_copper_stairs ``` （涂蜡的氧化切制铜楼梯） - ``` cut_copper_slab ``` （切制铜台阶） - ``` exposed_cut_copper_slab ``` （斑驳的切制铜台阶） - ``` weathered_cut_copper_slab ``` （锈蚀的切制铜台阶） - ``` oxidized_cut_copper_slab ``` （氧化的切制铜台阶） - ``` waxed_cut_copper_slab ``` （涂蜡的切制铜台阶） - ``` waxed_exposed_cut_copper_slab ``` （涂蜡的斑驳切制铜台阶） - ``` waxed_weathered_cut_copper_slab ``` （涂蜡的锈蚀切制铜台阶） - ``` waxed_oxidized_cut_copper_slab ``` （涂蜡的氧化切制铜台阶） - ``` copper_door ``` （铜门） - ``` exposed_copper_door ``` （斑驳的铜门） - ``` weathered_copper_door ``` （锈蚀的铜门） - ``` oxidized_copper_door ``` （氧化的铜门） - ``` waxed_copper_door ``` （涂蜡的铜门） - ``` waxed_exposed_copper_door ``` （涂蜡的斑驳铜门） - ``` waxed_weathered_copper_door ``` （涂蜡的锈蚀铜门） - ``` waxed_oxidized_copper_door ``` （涂蜡的氧化铜门） - ``` copper_trapdoor ``` （铜活板门） - ``` exposed_copper_trapdoor ``` （斑驳的铜活板门） - ``` weathered_copper_trapdoor ``` （锈蚀的铜活板门） - ``` oxidized_copper_trapdoor ``` （氧化的铜活板门） - ``` waxed_copper_trapdoor ``` （涂蜡的铜活板门） - ``` waxed_exposed_copper_trapdoor ``` （涂蜡的斑驳铜活板门） - ``` waxed_weathered_copper_trapdoor ``` （涂蜡的锈蚀铜活板门） - ``` waxed_oxidized_copper_trapdoor ``` （涂蜡的氧化铜活板门） - ``` copper_grate ``` （铜格栅） - ``` exposed_copper_grate ``` （斑驳的铜格栅） - ``` weathered_copper_grate ``` （锈蚀的铜格栅） - ``` oxidized_copper_grate ``` （氧化的铜格栅） - ``` waxed_copper_grate ``` （涂蜡的铜格栅） - ``` waxed_exposed_copper_grate ``` （涂蜡的斑驳铜格栅） - ``` waxed_weathered_copper_grate ``` （涂蜡的锈蚀铜格栅） - ``` waxed_oxidized_copper_grate ``` （涂蜡的氧化铜格栅） - ``` white_glazed_terracotta ``` （白色带釉陶瓦） - ``` orange_glazed_terracotta ``` （橙色带釉陶瓦） - ``` magenta_glazed_terracotta ``` （品红色带釉陶瓦） - ``` light_blue_glazed_terracotta ``` （淡蓝色带釉陶瓦） - ``` yellow_glazed_terracotta ``` （黄色带釉陶瓦） - ``` lime_glazed_terracotta ``` （黄绿色带釉陶瓦） - ``` pink_glazed_terracotta ``` （粉红色带釉陶瓦） - ``` gray_glazed_terracotta ``` （灰色带釉陶瓦） - ``` light_gray_glazed_terracotta ``` （淡灰色带釉陶瓦） - ``` cyan_glazed_terracotta ``` （青色带釉陶瓦） - ``` purple_glazed_terracotta ``` （紫色带釉陶瓦） - ``` blue_glazed_terracotta ``` （蓝色带釉陶瓦） - ``` brown_glazed_terracotta ``` （棕色带釉陶瓦） - ``` green_glazed_terracotta ``` （绿色带釉陶瓦） - ``` red_glazed_terracotta ``` （红色带釉陶瓦） - ``` black_glazed_terracotta ``` （黑色带釉陶瓦） - ``` white_terracotta ``` （白色陶瓦） - ``` orange_terracotta ``` （橙色陶瓦） - ``` magenta_terracotta ``` （品红色陶瓦） - ``` light_blue_terracotta ``` （淡蓝色陶瓦） - ``` yellow_terracotta ``` （黄色陶瓦） - ``` lime_terracotta ``` （黄绿色陶瓦） - ``` pink_terracotta ``` （粉红色陶瓦） - ``` gray_terracotta ``` （灰色陶瓦） - ``` light_gray_terracotta ``` （淡灰色陶瓦） - ``` cyan_terracotta ``` （青色陶瓦） - ``` purple_terracotta ``` （紫色陶瓦） - ``` blue_terracotta ``` （蓝色陶瓦） - ``` brown_terracotta ``` （棕色陶瓦） - ``` green_terracotta ``` （绿色陶瓦） - ``` red_terracotta ``` （红色陶瓦） - ``` black_terracotta ``` （黑色陶瓦） - ``` white_concrete ``` （白色混凝土） - ``` orange_concrete ``` （橙色混凝土） - ``` magenta_concrete ``` （品红色混凝土） - ``` light_blue_concrete ``` （淡蓝色混凝土） - ``` yellow_concrete ``` （黄色混凝土） - ``` lime_concrete ``` （黄绿色混凝土） - ``` pink_concrete ``` （粉红色混凝土） - ``` gray_concrete ``` （灰色混凝土） - ``` light_gray_concrete ``` （淡灰色混凝土） - ``` cyan_concrete ``` （青色混凝土） - ``` purple_concrete ``` （紫色混凝土） - ``` blue_concrete ``` （蓝色混凝土） - ``` brown_concrete ``` （棕色混凝土） - ``` green_concrete ``` （绿色混凝土） - ``` red_concrete ``` （红色混凝土） - ``` black_concrete ``` （黑色混凝土） - ``` #speleothems ``` - ``` white_concrete_stairs ``` （白色混凝土楼梯） - ``` orange_concrete_stairs ``` （橙色混凝土楼梯） - ``` magenta_concrete_stairs ``` （品红色混凝土楼梯） - ``` light_blue_concrete_stairs ``` （淡蓝色混凝土楼梯） - ``` yellow_concrete_stairs ``` （黄色混凝土楼梯） - ``` lime_concrete_stairs ``` （黄绿色混凝土楼梯） - ``` pink_concrete_stairs ``` （粉红色混凝土楼梯） - ``` gray_concrete_stairs ``` （灰色混凝土楼梯） - ``` light_gray_concrete_stairs ``` （淡灰色混凝土楼梯） - ``` cyan_concrete_stairs ``` （青色混凝土楼梯） - ``` purple_concrete_stairs ``` （紫色混凝土楼梯） - ``` blue_concrete_stairs ``` （蓝色混凝土楼梯） - ``` brown_concrete_stairs ``` （棕色混凝土楼梯） - ``` green_concrete_stairs ``` （绿色混凝土楼梯） - ``` red_concrete_stairs ``` （红色混凝土楼梯） - ``` black_concrete_stairs ``` （黑色混凝土楼梯） - ``` white_concrete_slab ``` （白色混凝土台阶） - ``` orange_concrete_slab ``` （橙色混凝土台阶） - ``` magenta_concrete_slab ``` （品红色混凝土台阶） - ``` light_blue_concrete_slab ``` （淡蓝色混凝土台阶） - ``` yellow_concrete_slab ``` （黄色混凝土台阶） - ``` lime_concrete_slab ``` （黄绿色混凝土台阶） - ``` pink_concrete_slab ``` （粉红色混凝土台阶） - ``` gray_concrete_slab ``` （灰色混凝土台阶） - ``` light_gray_concrete_slab ``` （淡灰色混凝土台阶） - ``` cyan_concrete_slab ``` （青色混凝土台阶） - ``` purple_concrete_slab ``` （紫色混凝土台阶） - ``` blue_concrete_slab ``` （蓝色混凝土台阶） - ``` brown_concrete_slab ``` （棕色混凝土台阶） - ``` green_concrete_slab ``` （绿色混凝土台阶） - ``` red_concrete_slab ``` （红色混凝土台阶） - ``` black_concrete_slab ``` （黑色混凝土台阶）

## mineable/shovel

- 此标签内的方块用锹挖掘更快。

- #mineable/shovel（21项） - ``` clay ``` （黏土） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` podzol ``` （灰化土） - ``` farmland ``` （耕地） - ``` grass_block ``` （草方块） - ``` gravel ``` （沙砾） - ``` mycelium ``` （菌丝体） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙） - ``` snow_block ``` （雪块） - ``` snow ``` （雪） - ``` soul_sand ``` （灵魂沙） - ``` dirt_path ``` （土径） - ``` soul_soil ``` （灵魂土） - ``` rooted_dirt ``` （缠根泥土） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` mud ``` （泥巴） - ``` suspicious_sand ``` （可疑的沙子） - ``` suspicious_gravel ``` （可疑的沙砾） - ``` #concrete_powders ```

## mob_interactable_doors

- 此标签内的方块可作为门被生物交互。

- #mob_interactable_doors（9项） - ``` #wooden_doors ``` - ``` copper_door ``` （铜门） - ``` exposed_copper_door ``` （斑驳的铜门） - ``` weathered_copper_door ``` （锈蚀的铜门） - ``` oxidized_copper_door ``` （氧化的铜门） - ``` waxed_copper_door ``` （涂蜡的铜门） - ``` waxed_exposed_copper_door ``` （涂蜡的斑驳铜门） - ``` waxed_weathered_copper_door ``` （涂蜡的锈蚀铜门） - ``` waxed_oxidized_copper_door ``` （涂蜡的氧化铜门）

## mooshrooms_spawnable_on

- 用于哞菇的生成判断。

- #mooshrooms_spawnable_on（1项） - ``` mycelium ``` （菌丝体）

## moss_blocks

- #moss_blocks（2项） - ``` moss_block ``` （苔藓块） - ``` pale_moss_block ``` （苍白苔藓块）

## moss_replaceable

- 可以被骨粉复制的苔藓块替换的方块。

- #moss_replaceable（6项） - ``` #base_stone_overworld ``` - ``` #cave_vines ``` - ``` #dirt ``` - ``` #mud ``` - ``` #moss_blocks ``` - ``` #grass_blocks ```

## mud

- #mud（2项） - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根）

## needs_diamond_tool

- 标签中的方块需要钻石质以上的工具破坏才可能掉落物品。

- #needs_diamond_tool（5项） - ``` obsidian ``` （黑曜石） - ``` crying_obsidian ``` （哭泣的黑曜石） - ``` netherite_block ``` （下界合金块） - ``` respawn_anchor ``` （重生锚） - ``` ancient_debris ``` （远古残骸）

## needs_iron_tool

- 标签中的方块需要铁质以上的工具破坏才可能掉落物品。

- #needs_iron_tool（12项） - ``` diamond_block ``` （钻石块） - ``` diamond_ore ``` （钻石矿石） - ``` deepslate_diamond_ore ``` （深层钻石矿石） - ``` emerald_ore ``` （绿宝石矿石） - ``` deepslate_emerald_ore ``` （深层绿宝石矿石） - ``` emerald_block ``` （绿宝石块） - ``` gold_block ``` （金块） - ``` raw_gold_block ``` （粗金块） - ``` gold_ore ``` （金矿石） - ``` deepslate_gold_ore ``` （深层金矿石） - ``` redstone_ore ``` （红石矿石） - ``` deepslate_redstone_ore ``` （深层红石矿石）

## needs_stone_tool

- 标签中的方块需要石质以上的工具破坏才可能掉落物品。

- #needs_stone_tool（77项） - ``` iron_block ``` （铁块） - ``` raw_iron_block ``` （粗铁块） - ``` iron_ore ``` （铁矿石） - ``` deepslate_iron_ore ``` （深层铁矿石） - ``` lapis_block ``` （青金石块） - ``` lapis_ore ``` （青金石矿石） - ``` deepslate_lapis_ore ``` （深层青金石矿石） - ``` raw_copper_block ``` （粗铜块） - ``` copper_ore ``` （铜矿石） - ``` deepslate_copper_ore ``` （深层铜矿石） - ``` crafter ``` （合成器） - ``` #copper_chests ``` - ``` #lightning_rods ``` - ``` copper_block ``` （铜块） - ``` exposed_copper ``` （斑驳的铜块） - ``` weathered_copper ``` （锈蚀的铜块） - ``` oxidized_copper ``` （氧化的铜块） - ``` waxed_copper_block ``` （涂蜡的铜块） - ``` waxed_exposed_copper ``` （涂蜡的斑驳铜块） - ``` waxed_weathered_copper ``` （涂蜡的锈蚀铜块） - ``` waxed_oxidized_copper ``` （涂蜡的氧化铜块） - ``` copper_bulb ``` （铜灯） - ``` exposed_copper_bulb ``` （斑驳的铜灯） - ``` weathered_copper_bulb ``` （锈蚀的铜灯） - ``` oxidized_copper_bulb ``` （氧化的铜灯） - ``` waxed_copper_bulb ``` （涂蜡的铜灯） - ``` waxed_exposed_copper_bulb ``` （涂蜡的斑驳铜灯） - ``` waxed_weathered_copper_bulb ``` （涂蜡的锈蚀铜灯） - ``` waxed_oxidized_copper_bulb ``` （涂蜡的氧化铜灯） - ``` cut_copper ``` （切制铜块） - ``` exposed_cut_copper ``` （斑驳的切制铜块） - ``` weathered_cut_copper ``` （锈蚀的切制铜块） - ``` oxidized_cut_copper ``` （氧化的切制铜块） - ``` waxed_cut_copper ``` （涂蜡的切制铜块） - ``` waxed_exposed_cut_copper ``` （涂蜡的斑驳切制铜块） - ``` waxed_weathered_cut_copper ``` （涂蜡的锈蚀切制铜块） - ``` waxed_oxidized_cut_copper ``` （涂蜡的氧化切制铜块） - ``` chiseled_copper ``` （雕纹铜块） - ``` exposed_chiseled_copper ``` （斑驳的雕纹铜块） - ``` weathered_chiseled_copper ``` （锈蚀的雕纹铜块） - ``` oxidized_chiseled_copper ``` （氧化的雕纹铜块） - ``` waxed_chiseled_copper ``` （涂蜡的雕纹铜块） - ``` waxed_exposed_chiseled_copper ``` （涂蜡的斑驳雕纹铜块） - ``` waxed_weathered_chiseled_copper ``` （涂蜡的锈蚀雕纹铜块） - ``` waxed_oxidized_chiseled_copper ``` （涂蜡的氧化雕纹铜块） - ``` cut_copper_stairs ``` （切制铜楼梯） - ``` exposed_cut_copper_stairs ``` （斑驳的切制铜楼梯） - ``` weathered_cut_copper_stairs ``` （锈蚀的切制铜楼梯） - ``` oxidized_cut_copper_stairs ``` （氧化的切制铜楼梯） - ``` waxed_cut_copper_stairs ``` （涂蜡的切制铜楼梯） - ``` waxed_exposed_cut_copper_stairs ``` （涂蜡的斑驳切制铜楼梯） - ``` waxed_weathered_cut_copper_stairs ``` （涂蜡的锈蚀切制铜楼梯） - ``` waxed_oxidized_cut_copper_stairs ``` （涂蜡的氧化切制铜楼梯） - ``` cut_copper_slab ``` （切制铜台阶） - ``` exposed_cut_copper_slab ``` （斑驳的切制铜台阶） - ``` weathered_cut_copper_slab ``` （锈蚀的切制铜台阶） - ``` oxidized_cut_copper_slab ``` （氧化的切制铜台阶） - ``` waxed_cut_copper_slab ``` （涂蜡的切制铜台阶） - ``` waxed_exposed_cut_copper_slab ``` （涂蜡的斑驳切制铜台阶） - ``` waxed_weathered_cut_copper_slab ``` （涂蜡的锈蚀切制铜台阶） - ``` waxed_oxidized_cut_copper_slab ``` （涂蜡的氧化切制铜台阶） - ``` copper_trapdoor ``` （铜活板门） - ``` exposed_copper_trapdoor ``` （斑驳的铜活板门） - ``` weathered_copper_trapdoor ``` （锈蚀的铜活板门） - ``` oxidized_copper_trapdoor ``` （氧化的铜活板门） - ``` waxed_copper_trapdoor ``` （涂蜡的铜活板门） - ``` waxed_exposed_copper_trapdoor ``` （涂蜡的斑驳铜活板门） - ``` waxed_weathered_copper_trapdoor ``` （涂蜡的锈蚀铜活板门） - ``` waxed_oxidized_copper_trapdoor ``` （涂蜡的氧化铜活板门） - ``` copper_grate ``` （铜格栅） - ``` exposed_copper_grate ``` （斑驳的铜格栅） - ``` weathered_copper_grate ``` （锈蚀的铜格栅） - ``` oxidized_copper_grate ``` （氧化的铜格栅） - ``` waxed_copper_grate ``` （涂蜡的铜格栅） - ``` waxed_exposed_copper_grate ``` （涂蜡的斑驳铜格栅） - ``` waxed_weathered_copper_grate ``` （涂蜡的锈蚀铜格栅） - ``` waxed_oxidized_copper_grate ``` （涂蜡的氧化铜格栅）

## nether_carver_replaceables

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

- 拥有此标签的方块可以被下界地形雕刻器切掉。

- #nether_carver_replaceables（7项） - ``` #base_stone_overworld ``` - ``` #base_stone_nether ``` - ``` #substrate_overworld ``` - ``` #nylium ``` - ``` #wart_blocks ``` - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## nylium

- #nylium（2项） - ``` crimson_nylium ``` （绯红菌岩） - ``` warped_nylium ``` （诡异菌岩）

## oak_logs

- #oak_logs（4项） - ``` oak_log ``` （橡木原木） - ``` oak_wood ``` （橡木） - ``` stripped_oak_log ``` （去皮橡木原木） - ``` stripped_oak_wood ``` （去皮橡木）

## occludes_vibration_signals

- 阻挡振动的传播

- #occludes_vibration_signals（1项） - ``` #wool ```

## ores

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #ores（9项） - ``` #copper_ores ``` - ``` #gold_ores ``` - ``` #iron_ores ``` - ``` #coal_ores ``` - ``` #diamond_ores ``` - ``` #emerald_ores ``` - ``` #lapis_ores ``` - ``` #redstone_ores ``` - ``` nether_quartz_ore ``` （下界石英矿石）

## overrides_mushroom_light_requirement

- 蘑菇不能在不属于上述标签且光照等于大于13的位置存活。

- #overrides_mushroom_light_requirement（4项） - ``` mycelium ``` （菌丝体） - ``` podzol ``` （灰化土） - ``` crimson_nylium ``` （绯红菌岩） - ``` warped_nylium ``` （诡异菌岩）

## overworld_carver_replaceables

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

- 拥有此标签的方块可以被主世界地形雕刻器切掉。

- #overworld_carver_replaceables（19项） - ``` #base_stone_overworld ``` - ``` #substrate_overworld ``` - ``` #sand ``` - ``` #terracotta ``` - ``` #iron_ores ``` - ``` #copper_ores ``` - ``` #snow ``` - ``` water ``` （水） - ``` gravel ``` （沙砾） - ``` suspicious_gravel ``` （可疑的沙砾） - ``` sandstone ``` （砂岩） - ``` red_sandstone ``` （红砂岩） - ``` calcite ``` （方解石） - ``` packed_ice ``` （浮冰） - ``` raw_iron_block ``` （粗铁块） - ``` raw_copper_block ``` （粗铜块） - ``` cinnabar ``` （朱砂） - ``` sulfur ``` （硫黄） - ``` potent_sulfur ``` （烈性硫黄）

## overworld_natural_logs

- #overworld_natural_logs（10项） - ``` acacia_log ``` （金合欢原木） - ``` birch_log ``` （白桦原木） - ``` oak_log ``` （橡木原木） - ``` jungle_log ``` （丛林原木） - ``` spruce_log ``` （云杉原木） - ``` dark_oak_log ``` （深色橡木原木） - ``` pale_oak_log ``` （苍白橡木原木） - ``` mangrove_log ``` （红树原木） - ``` cherry_log ``` （樱花原木） - ``` poplar_log ``` （杨木原木）

## pale_oak_logs

- #pale_oak_logs（4项） - ``` pale_oak_log ``` （苍白橡木原木） - ``` pale_oak_wood ``` （苍白橡木） - ``` stripped_pale_oak_log ``` （去皮苍白橡木原木） - ``` stripped_pale_oak_wood ``` （去皮苍白橡木）

## parrots_spawnable_on

- 用于鹦鹉生成判定。

- #parrots_spawnable_on（4项） - ``` grass_block ``` （草方块） - ``` air ``` （空气） - ``` #leaves ``` - ``` #logs ```

## piglin_repellents

- 猪灵会远离这些方块。

- #piglin_repellents（5项） - ``` soul_fire ``` （灵魂火） - ``` soul_torch ``` （灵魂火把） - ``` soul_lantern ``` （灵魂灯笼） - ``` soul_wall_torch ``` （墙上的灵魂火把） - ``` soul_campfire ``` （灵魂营火）

## planks

- #planks（13项） - ``` oak_planks ``` （橡木木板） - ``` spruce_planks ``` （云杉木板） - ``` birch_planks ``` （白桦木板） - ``` jungle_planks ``` （丛林木板） - ``` acacia_planks ``` （金合欢木板） - ``` dark_oak_planks ``` （深色橡木木板） - ``` pale_oak_planks ``` （苍白橡木木板） - ``` crimson_planks ``` （绯红木板） - ``` warped_planks ``` （诡异木板） - ``` mangrove_planks ``` （红树木板） - ``` bamboo_planks ``` （竹板） - ``` cherry_planks ``` （樱花木板） - ``` poplar_planks ``` （杨木木板）

## polar_bear_immune_to

- 北极熊不会将这些方块视为危险方块。

- #polar_bear_immune_to（1项） - ``` powder_snow ``` （细雪）

## polar_bears_spawnable_on_alternate

- 用于北极熊生成判定。

- #polar_bears_spawnable_on_alternate（1项） - ``` ice ``` （冰）

## poplar_logs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #poplar_logs（4项） - ``` poplar_log ``` （杨木原木） - ``` poplar_wood ``` （杨木） - ``` stripped_poplar_log ``` （去皮杨木原木） - ``` stripped_poplar_wood ``` （去皮杨木）

## portals

- 当骑着一个实体的实体从其上脱离时，它将不会落在这些方块中以防止不需要的传送，而是会脱离在被骑乘的实体的位置。

- #portals（3项） - ``` nether_portal ``` （下界传送门） - ``` end_portal ``` （末地传送门） - ``` end_gateway ``` （末地折跃门）

## pressure_plates

- #pressure_plates（4项） - ``` light_weighted_pressure_plate ``` （轻质测重压力板） - ``` heavy_weighted_pressure_plate ``` （重质测重压力板） - ``` #wooden_pressure_plates ``` - ``` #stone_pressure_plates ```

## prevent_mob_spawning_inside

- 生物不能在这些方块里生成。

- #prevent_mob_spawning_inside（1项） - ``` #rails ```

## prevents_nearby_leaf_decay

- 树叶距离这些方块曼哈顿距离6格内时不消失。

- #prevents_nearby_leaf_decay（1项） - ``` #logs ```

## rabbits_spawnable_on

- 用于兔子的生成判定。

- #rabbits_spawnable_on（4项） - ``` grass_block ``` （草方块） - ``` snow ``` （雪） - ``` snow_block ``` （雪块） - ``` sand ``` （沙子）

## rails

- 检测是否与铁轨相连。
- 矿车是否可在此方块上行驶。
- 检测是否可以放置矿车。
- 向此标签添加其他方块会导致游戏崩溃。
- TNT矿车位于这些方块内时，不会破坏所在位置的方块和下方的方块。

- #rails（4项） - ``` rail ``` （铁轨） - ``` powered_rail ``` （动力铁轨） - ``` detector_rail ``` （探测铁轨） - ``` activator_rail ``` （激活铁轨）

## redstone_ores

- #redstone_ores（2项） - ``` redstone_ore ``` （红石矿石） - ``` deepslate_redstone_ore ``` （深层红石矿石）

## replaceable

- #replaceable（30项） - ``` air ``` （空气） - ``` water ``` （水） - ``` lava ``` （熔岩） - ``` short_grass ``` （矮草丛） - ``` fern ``` （蕨） - ``` dead_bush ``` （枯萎的灌木） - ``` bush ``` （灌木丛） - ``` red_shrub ``` （红灌木） - ``` short_dry_grass ``` （矮枯草丛） - ``` tall_dry_grass ``` （高枯草丛） - ``` seagrass ``` （海草） - ``` tall_seagrass ``` （高海草） - ``` fire ``` （火） - ``` soul_fire ``` （灵魂火） - ``` snow ``` （雪） - ``` vine ``` （藤蔓） - ``` glow_lichen ``` （发光地衣） - ``` resin_clump ``` （树脂团） - ``` light ``` （光源方块） - ``` tall_grass ``` （高草丛） - ``` large_fern ``` （大型蕨） - ``` structure_void ``` （结构空位） - ``` void_air ``` （虚空空气） - ``` cave_air ``` （洞穴空气） - ``` bubble_column ``` （气泡柱） - ``` warped_roots ``` （诡异菌索） - ``` nether_sprouts ``` （下界苗） - ``` crimson_roots ``` （绯红菌索） - ``` leaf_litter ``` （枯叶堆） - ``` hanging_roots ``` （垂根）

## replaceable_by_mushrooms

- 蘑菇被放置或生长时可替换的方块。

- #replaceable_by_mushrooms（32项） - ``` #leaves ``` - ``` #small_flowers ``` - ``` pale_moss_carpet ``` （苍白覆地苔藓） - ``` short_grass ``` （矮草丛） - ``` fern ``` （蕨） - ``` dead_bush ``` （枯萎的灌木） - ``` vine ``` （藤蔓） - ``` glow_lichen ``` （发光地衣） - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` rose_bush ``` （玫瑰丛） - ``` peony ``` （牡丹） - ``` tall_grass ``` （高草丛） - ``` large_fern ``` （大型蕨） - ``` hanging_roots ``` （垂根） - ``` pitcher_plant ``` （瓶子草） - ``` water ``` （水） - ``` seagrass ``` （海草） - ``` tall_seagrass ``` （高海草） - ``` brown_mushroom ``` （棕色蘑菇） - ``` red_mushroom ``` （红色蘑菇） - ``` brown_mushroom_block ``` （棕色蘑菇方块） - ``` red_mushroom_block ``` （红色蘑菇方块） - ``` warped_roots ``` （诡异菌索） - ``` nether_sprouts ``` （下界苗） - ``` crimson_roots ``` （绯红菌索） - ``` leaf_litter ``` （枯叶堆） - ``` short_dry_grass ``` （矮枯草丛） - ``` tall_dry_grass ``` （高枯草丛） - ``` bush ``` （灌木丛） - ``` red_shrub ``` （红灌木） - ``` firefly_bush ``` （萤火虫灌木丛）

## replaceable_by_trees

- 可被长成的树木替换的方块。

- #replaceable_by_trees（27项） - ``` #leaves ``` - ``` #small_flowers ``` - ``` pale_moss_carpet ``` （苍白覆地苔藓） - ``` short_grass ``` （矮草丛） - ``` fern ``` （蕨） - ``` dead_bush ``` （枯萎的灌木） - ``` vine ``` （藤蔓） - ``` glow_lichen ``` （发光地衣） - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` rose_bush ``` （玫瑰丛） - ``` peony ``` （牡丹） - ``` tall_grass ``` （高草丛） - ``` large_fern ``` （大型蕨） - ``` hanging_roots ``` （垂根） - ``` pitcher_plant ``` （瓶子草） - ``` water ``` （水） - ``` seagrass ``` （海草） - ``` tall_seagrass ``` （高海草） - ``` bush ``` （灌木丛） - ``` firefly_bush ``` （萤火虫灌木丛） - ``` warped_roots ``` （诡异菌索） - ``` nether_sprouts ``` （下界苗） - ``` crimson_roots ``` （绯红菌索） - ``` leaf_litter ``` （枯叶堆） - ``` short_dry_grass ``` （矮枯草丛） - ``` tall_dry_grass ``` （高枯草丛）

## required_for_poplar_leaf_ambience

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 用于杨树树叶环境音效的判定。

- #required_for_poplar_leaf_ambience（1项） - ``` #overworld_natural_logs ```

## sand

- 用于确定海龟蛋是否能在该方块上孵化。

- #sand（3项） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙） - ``` suspicious_sand ``` （可疑的沙子）

## saplings

- 树生长时可以替代此标签的方块。

- #saplings（12项） - ``` oak_sapling ``` （橡树树苗） - ``` spruce_sapling ``` （云杉树苗） - ``` birch_sapling ``` （白桦树苗） - ``` jungle_sapling ``` （丛林树苗） - ``` acacia_sapling ``` （金合欢树苗） - ``` dark_oak_sapling ``` （深色橡树树苗） - ``` pale_oak_sapling ``` （苍白橡树树苗） - ``` azalea ``` （杜鹃花丛） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_sapling ``` （樱花树苗） - ``` poplar_sapling ``` （杨树树苗）

## sculk_growth_inhibitors

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 能够阻止幽匿块扩散的方块。

- #sculk_growth_inhibitors（2项） - ``` sculk_sensor ``` （幽匿感测体） - ``` sculk_shrieker ``` （幽匿尖啸体）

## sculk_replaceable

- 用于确定幽匿催发体在蔓延时会将何种方块转化为幽匿块。

- #sculk_replaceable（19项） - ``` #base_stone_overworld ``` - ``` #substrate_overworld ``` - ``` #terracotta ``` - ``` #nylium ``` - ``` #base_stone_nether ``` - ``` sand ``` （沙子） - ``` red_sand ``` （红沙） - ``` gravel ``` （沙砾） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土） - ``` calcite ``` （方解石） - ``` smooth_basalt ``` （平滑玄武岩） - ``` clay ``` （黏土） - ``` dripstone_block ``` （滴水石块） - ``` end_stone ``` （末地石） - ``` red_sandstone ``` （红砂岩） - ``` sandstone ``` （砂岩） - ``` sulfur ``` （硫黄） - ``` cinnabar ``` （朱砂）

## sculk_replaceable_world_gen

- 用于确定在世界生成阶段哪些方块会被幽匿斑簇替换。

- #sculk_replaceable_world_gen（7项） - ``` #sculk_replaceable ``` - ``` deepslate_bricks ``` （深板岩砖） - ``` deepslate_tiles ``` （深板岩瓦） - ``` cobbled_deepslate ``` （深板岩圆石） - ``` cracked_deepslate_bricks ``` （裂纹深板岩砖） - ``` cracked_deepslate_tiles ``` （裂纹深板岩瓦） - ``` polished_deepslate ``` （磨制深板岩）

## shears_extreme_breaking_speed

- 被剪刀以15倍的速度破坏的方块。
- 对蜘蛛网的急迫不受此标签影响。

- #shears_extreme_breaking_speed（1项） - ``` #leaves ```

## shears_major_breaking_speed

- 被剪刀以5倍的速度破坏的方块。

- #shears_major_breaking_speed（3项） - ``` #wool ``` - ``` #wool_slabs ``` - ``` #wool_stairs ```

## shears_minor_breaking_speed

- 被剪刀以2倍的速度破坏的方块。

- #shears_minor_breaking_speed（2项） - ``` glow_lichen ``` （发光地衣） - ``` vine ``` （藤蔓）

## shulker_boxes

- 栅栏、墙和玻璃板不会连接到这些方块。

- #shulker_boxes（17项） - ``` shulker_box ``` （潜影盒） - ``` white_shulker_box ``` （白色潜影盒） - ``` orange_shulker_box ``` （橙色潜影盒） - ``` magenta_shulker_box ``` （品红色潜影盒） - ``` light_blue_shulker_box ``` （淡蓝色潜影盒） - ``` yellow_shulker_box ``` （黄色潜影盒） - ``` lime_shulker_box ``` （黄绿色潜影盒） - ``` pink_shulker_box ``` （粉红色潜影盒） - ``` gray_shulker_box ``` （灰色潜影盒） - ``` light_gray_shulker_box ``` （淡灰色潜影盒） - ``` cyan_shulker_box ``` （青色潜影盒） - ``` purple_shulker_box ``` （紫色潜影盒） - ``` blue_shulker_box ``` （蓝色潜影盒） - ``` brown_shulker_box ``` （棕色潜影盒） - ``` green_shulker_box ``` （绿色潜影盒） - ``` red_shulker_box ``` （红色潜影盒） - ``` black_shulker_box ``` （黑色潜影盒）

## signs

- 流水不会破坏这些方块。

- #signs（2项） - ``` #standing_signs ``` - ``` #wall_signs ```

## skulls

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #skulls（7项） - ``` player_head ``` （玩家的头） - ``` creeper_head ``` （苦力怕的头） - ``` zombie_head ``` （僵尸的头） - ``` skeleton_skull ``` （骷髅头颅） - ``` wither_skeleton_skull ``` （凋灵骷髅头颅） - ``` dragon_head ``` （龙首） - ``` piglin_head ``` （猪灵的头）

## slabs

- #slabs（59项） - ``` #wooden_slabs ``` - ``` stone_slab ``` （石头台阶） - ``` smooth_stone_slab ``` （平滑石头台阶） - ``` stone_brick_slab ``` （石砖台阶） - ``` sandstone_slab ``` （砂岩台阶） - ``` cobblestone_slab ``` （圆石台阶） - ``` brick_slab ``` （红砖台阶） - ``` nether_brick_slab ``` （下界砖台阶） - ``` quartz_slab ``` （石英台阶） - ``` red_sandstone_slab ``` （红砂岩台阶） - ``` prismarine_slab ``` （海晶石台阶） - ``` prismarine_brick_slab ``` （海晶石砖台阶） - ``` dark_prismarine_slab ``` （暗海晶石台阶） - ``` purpur_slab ``` （紫珀台阶） - ``` end_stone_brick_slab ``` （末地石砖台阶） - ``` petrified_oak_slab ``` （石化橡木台阶） - ``` cut_sandstone_slab ``` （切制砂岩台阶） - ``` smooth_sandstone_slab ``` （平滑砂岩台阶） - ``` cut_red_sandstone_slab ``` （切制红砂岩台阶） - ``` smooth_red_sandstone_slab ``` （平滑红砂岩台阶） - ``` smooth_quartz_slab ``` （平滑石英台阶） - ``` mossy_cobblestone_slab ``` （苔石台阶） - ``` mossy_stone_brick_slab ``` （苔石砖台阶） - ``` granite_slab ``` （花岗岩台阶） - ``` polished_granite_slab ``` （磨制花岗岩台阶） - ``` diorite_slab ``` （闪长岩台阶） - ``` polished_diorite_slab ``` （磨制闪长岩台阶） - ``` andesite_slab ``` （安山岩台阶） - ``` polished_andesite_slab ``` （磨制安山岩台阶） - ``` red_nether_brick_slab ``` （红色下界砖台阶） - ``` blackstone_slab ``` （黑石台阶） - ``` polished_blackstone_slab ``` （磨制黑石台阶） - ``` polished_blackstone_brick_slab ``` （磨制黑石砖台阶） - ``` cut_copper_slab ``` （切制铜台阶） - ``` exposed_cut_copper_slab ``` （斑驳的切制铜台阶） - ``` weathered_cut_copper_slab ``` （锈蚀的切制铜台阶） - ``` oxidized_cut_copper_slab ``` （氧化的切制铜台阶） - ``` waxed_cut_copper_slab ``` （涂蜡的切制铜台阶） - ``` waxed_exposed_cut_copper_slab ``` （涂蜡的斑驳切制铜台阶） - ``` waxed_weathered_cut_copper_slab ``` （涂蜡的锈蚀切制铜台阶） - ``` waxed_oxidized_cut_copper_slab ``` （涂蜡的氧化切制铜台阶） - ``` cobbled_deepslate_slab ``` （深板岩圆石台阶） - ``` polished_deepslate_slab ``` （磨制深板岩台阶） - ``` deepslate_brick_slab ``` （深板岩砖台阶） - ``` deepslate_tile_slab ``` （深板岩瓦台阶） - ``` mud_brick_slab ``` （泥砖台阶） - ``` bamboo_mosaic_slab ``` （竹马赛克台阶） - ``` tuff_slab ``` （凝灰岩台阶） - ``` polished_tuff_slab ``` （磨制凝灰岩台阶） - ``` tuff_brick_slab ``` （凝灰岩砖台阶） - ``` resin_brick_slab ``` （树脂砖台阶） - ``` cinnabar_slab ``` （朱砂台阶） - ``` polished_cinnabar_slab ``` （磨制朱砂台阶） - ``` cinnabar_brick_slab ``` （朱砂砖台阶） - ``` sulfur_slab ``` （硫黄台阶） - ``` polished_sulfur_slab ``` （磨制硫黄台阶） - ``` sulfur_brick_slab ``` （硫黄砖台阶） - ``` #wool_slabs ``` - ``` #concrete_slabs ```

## small_flowers

- 蜜蜂会尝试采集这些方块的花粉。

- #small_flowers（17项） - ``` dandelion ``` （蒲公英） - ``` open_eyeblossom ``` （张开的眼眸花） - ``` poppy ``` （虞美人） - ``` blue_orchid ``` （兰花） - ``` allium ``` （绒球葱） - ``` azure_bluet ``` （蓝花美耳草） - ``` red_tulip ``` （红色郁金香） - ``` orange_tulip ``` （橙色郁金香） - ``` white_tulip ``` （白色郁金香） - ``` pink_tulip ``` （粉红色郁金香） - ``` oxeye_daisy ``` （滨菊） - ``` cornflower ``` （矢车菊） - ``` lily_of_the_valley ``` （铃兰） - ``` wither_rose ``` （凋灵玫瑰） - ``` torchflower ``` （火把花） - ``` closed_eyeblossom ``` （闭合的眼眸花） - ``` golden_dandelion ``` （金蒲公英）

## smelts_to_glass

- 这些方块可以被烧炼成玻璃。

- #smelts_to_glass（2项） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙）

## snaps_goat_horn

- 山羊冲撞到这些方块会掉落山羊角。

- #snaps_goat_horn（7项） - ``` #overworld_natural_logs ``` - ``` stone ``` （石头） - ``` packed_ice ``` （浮冰） - ``` iron_ore ``` （铁矿石） - ``` coal_ore ``` （煤矿石） - ``` copper_ore ``` （铜矿石） - ``` emerald_ore ``` （绿宝石矿石）

## sniffer_diggable_block

- 嗅探兽可以从这些方块中找到种子。

- #sniffer_diggable_block（5项） - ``` #dirt ``` - ``` #mud ``` - ``` #moss_blocks ``` - ``` grass_block ``` （草方块） - ``` podzol ``` （灰化土）

## sniffer_egg_hatch_boost

- 这些方块可以加速嗅探兽蛋的孵化。

- #sniffer_egg_hatch_boost（1项） - ``` moss_block ``` （苔藓块）

## snow

- #snow（3项） - ``` snow ``` （雪） - ``` snow_block ``` （雪块） - ``` powder_snow ``` （细雪）

## snow_golem_immune_to

- 雪傀儡不会将这些方块视为危险方块。

- #snow_golem_immune_to（1项） - ``` powder_snow ``` （细雪）

## soul_fire_base_blocks

- 灵魂火会在这些方块上燃烧。

- #soul_fire_base_blocks（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## soul_speed_blocks

- 穿着附有灵魂疾行魔咒的靴子在这些方块上的行走速度会得到提高。

- #soul_speed_blocks（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## speeds_up_zombie_villager_curing

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 能够加速治愈僵尸村民的方块。

- #speeds_up_zombie_villager_curing（2项） - ``` iron_bars ``` （铁栏杆） - ``` #beds ```

## speleothems

- #speleothems（2项） - ``` pointed_dripstone ``` （滴水石锥） - ``` sulfur_spike ``` （硫黄尖锥）

## spruce_logs

- #spruce_logs（4项） - ``` spruce_log ``` （云杉原木） - ``` spruce_wood ``` （云杉木） - ``` stripped_spruce_log ``` （去皮云杉原木） - ``` stripped_spruce_wood ``` （去皮云杉木）

## stairs

- #stairs（55项） - ``` #wooden_stairs ``` - ``` cobblestone_stairs ``` （圆石楼梯） - ``` sandstone_stairs ``` （砂岩楼梯） - ``` brick_stairs ``` （红砖楼梯） - ``` stone_brick_stairs ``` （石砖楼梯） - ``` nether_brick_stairs ``` （下界砖楼梯） - ``` quartz_stairs ``` （石英楼梯） - ``` red_sandstone_stairs ``` （红砂岩楼梯） - ``` prismarine_stairs ``` （海晶石楼梯） - ``` prismarine_brick_stairs ``` （海晶石砖楼梯） - ``` dark_prismarine_stairs ``` （暗海晶石楼梯） - ``` purpur_stairs ``` （紫珀楼梯） - ``` end_stone_brick_stairs ``` （末地石砖楼梯） - ``` stone_stairs ``` （石头楼梯） - ``` smooth_sandstone_stairs ``` （平滑砂岩楼梯） - ``` smooth_red_sandstone_stairs ``` （平滑红砂岩楼梯） - ``` smooth_quartz_stairs ``` （平滑石英楼梯） - ``` mossy_cobblestone_stairs ``` （苔石楼梯） - ``` mossy_stone_brick_stairs ``` （苔石砖楼梯） - ``` granite_stairs ``` （花岗岩楼梯） - ``` polished_granite_stairs ``` （磨制花岗岩楼梯） - ``` diorite_stairs ``` （闪长岩楼梯） - ``` polished_diorite_stairs ``` （磨制闪长岩楼梯） - ``` andesite_stairs ``` （安山岩楼梯） - ``` polished_andesite_stairs ``` （磨制安山岩楼梯） - ``` red_nether_brick_stairs ``` （红色下界砖楼梯） - ``` blackstone_stairs ``` （黑石楼梯） - ``` polished_blackstone_stairs ``` （磨制黑石楼梯） - ``` polished_blackstone_brick_stairs ``` （磨制黑石砖楼梯） - ``` cut_copper_stairs ``` （切制铜楼梯） - ``` exposed_cut_copper_stairs ``` （斑驳的切制铜楼梯） - ``` weathered_cut_copper_stairs ``` （锈蚀的切制铜楼梯） - ``` oxidized_cut_copper_stairs ``` （氧化的切制铜楼梯） - ``` waxed_cut_copper_stairs ``` （涂蜡的切制铜楼梯） - ``` waxed_exposed_cut_copper_stairs ``` （涂蜡的斑驳切制铜楼梯） - ``` waxed_weathered_cut_copper_stairs ``` （涂蜡的锈蚀切制铜楼梯） - ``` waxed_oxidized_cut_copper_stairs ``` （涂蜡的氧化切制铜楼梯） - ``` cobbled_deepslate_stairs ``` （深板岩圆石楼梯） - ``` polished_deepslate_stairs ``` （磨制深板岩楼梯） - ``` deepslate_brick_stairs ``` （深板岩砖楼梯） - ``` deepslate_tile_stairs ``` （深板岩瓦楼梯） - ``` mud_brick_stairs ``` （泥砖楼梯） - ``` bamboo_mosaic_stairs ``` （竹马赛克楼梯） - ``` tuff_stairs ``` （凝灰岩楼梯） - ``` polished_tuff_stairs ``` （磨制凝灰岩楼梯） - ``` tuff_brick_stairs ``` （凝灰岩砖楼梯） - ``` resin_brick_stairs ``` （树脂砖楼梯） - ``` cinnabar_stairs ``` （朱砂楼梯） - ``` polished_cinnabar_stairs ``` （磨制朱砂楼梯） - ``` cinnabar_brick_stairs ``` （朱砂砖楼梯） - ``` sulfur_stairs ``` （硫黄楼梯） - ``` polished_sulfur_stairs ``` （磨制硫黄楼梯） - ``` sulfur_brick_stairs ``` （硫黄砖楼梯） - ``` #wool_stairs ``` - ``` #concrete_stairs ```

## standing_signs

- #standing_signs（13项） - ``` oak_sign ``` （橡木告示牌） - ``` spruce_sign ``` （云杉木告示牌） - ``` birch_sign ``` （白桦木告示牌） - ``` acacia_sign ``` （金合欢木告示牌） - ``` jungle_sign ``` （丛林木告示牌） - ``` dark_oak_sign ``` （深色橡木告示牌） - ``` pale_oak_sign ``` （苍白橡木告示牌） - ``` crimson_sign ``` （绯红木告示牌） - ``` warped_sign ``` （诡异木告示牌） - ``` mangrove_sign ``` （红树木告示牌） - ``` poplar_sign ``` （杨木告示牌） - ``` bamboo_sign ``` （竹告示牌） - ``` cherry_sign ``` （樱花木告示牌）

## stone_bricks

- #stone_bricks（4项） - ``` stone_bricks ``` （石砖） - ``` mossy_stone_bricks ``` （苔石砖） - ``` cracked_stone_bricks ``` （裂纹石砖） - ``` chiseled_stone_bricks ``` （雕纹石砖）

## stone_buttons

- #stone_buttons（2项） - ``` stone_button ``` （石头按钮） - ``` polished_blackstone_button ``` （磨制黑石按钮）

## stone_ore_replaceables

- 用于决定在世界生成时能被矿石替换的方块，深层变种见 ``` #deepslate_ore_replaceables ``` 。

- #stone_ore_replaceables（4项） - ``` stone ``` （石头） - ``` granite ``` （花岗岩） - ``` diorite ``` （闪长岩） - ``` andesite ``` （安山岩）

## stone_pressure_plates

- #stone_pressure_plates（2项） - ``` stone_pressure_plate ``` （石头压力板） - ``` polished_blackstone_pressure_plate ``` （磨制黑石压力板）

## stray_immune_to

- 流浪者不会将这些方块视为危险方块。

- #stray_immune_to（1项） - ``` powder_snow ``` （细雪）

## strider_warm_blocks

- 炽足兽若不在此标签的方块当中，就会打寒颤。

- #strider_warm_blocks（1项） - ``` lava ``` （熔岩）

## substrate_overworld

- 用于集合世界生成条件。

- #substrate_overworld（4项） - ``` #dirt ``` - ``` #mud ``` - ``` #moss_blocks ``` - ``` #grass_blocks ```

## sulfur_spike_replaceable_blocks

- 硫黄尖锥生成时可以取代这些方块。

- #sulfur_spike_replaceable_blocks（2项） - ``` sulfur ``` （硫黄） - ``` cinnabar ``` （朱砂）

## support_override_cactus_flower

- 仙人掌花可以放置并存活在这些方块上，即使方块上表面不完整。

- #support_override_cactus_flower（2项） - ``` cactus ``` （仙人掌） - ``` farmland ``` （耕地）

## support_override_snow_layer

- 雪可以放置并存活在这些方块上，即使方块上表面不完整。

- #support_override_snow_layer（3项） - ``` honey_block ``` （蜂蜜块） - ``` soul_sand ``` （灵魂沙） - ``` mud ``` （泥巴）

## supports_azalea

- 杜鹃花丛、盛开的杜鹃花丛可以放置并存活在这些方块上。

- #supports_azalea（2项） - ``` #supports_vegetation ``` - ``` clay ``` （黏土）

## supports_bamboo

- 竹子、竹笋可以放置并存活在这些方块上。

- #supports_bamboo（6项） - ``` #sand ``` - ``` #substrate_overworld ``` - ``` bamboo ``` （竹子） - ``` bamboo_sapling ``` （竹笋） - ``` gravel ``` （沙砾） - ``` suspicious_gravel ``` （可疑的沙砾）

## supports_big_dripleaf

- 大型垂滴叶可以放置并存活在这些方块上。

- #supports_big_dripleaf（11项） - ``` #supports_small_dripleaf ``` - ``` dirt ``` （泥土） - ``` grass_block ``` （草方块） - ``` podzol ``` （灰化土） - ``` coarse_dirt ``` （砂土） - ``` mycelium ``` （菌丝体） - ``` rooted_dirt ``` （缠根泥土） - ``` moss_block ``` （苔藓块） - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` farmland ``` （耕地）

## supports_cactus

- 仙人掌可以放置并存活在这些方块上。

- #supports_cactus（1项） - ``` #sand ```

## supports_chorus_flower

- 紫颂花可以放置并存活在这些方块上。

- #supports_chorus_flower（1项） - ``` end_stone ``` （末地石）

## supports_chorus_plant

- 紫颂植株可以放置并存活在这些方块上。
- 紫颂树会在这些方块上生成。

- #supports_chorus_plant（1项） - ``` end_stone ``` （末地石）

## supports_cocoa

- 可可果可以放置并存活在这些方块上。

- #supports_cocoa（1项） - ``` #jungle_logs ```

## supports_crimson_fungus

- 绯红菌可以放置并存活在这些方块上。

- #supports_crimson_fungus（1项） - ``` #supports_warped_fungus ```

## supports_crimson_roots

- 绯红菌索可以放置并存活在这些方块上。

- #supports_crimson_roots（1项） - ``` #supports_warped_roots ```

## supports_crops

- 小麦植株、胡萝卜、马铃薯、甜菜根、火把花植株、瓶子草植株可以放置并存活在这些方块上。

- #supports_crops（1项） - ``` farmland ``` （耕地）

## supports_dry_vegetation

- 矮枯草丛、高枯草丛可以放置并存活在这些方块上。

- #supports_dry_vegetation（3项） - ``` #sand ``` - ``` #terracotta ``` - ``` #supports_vegetation ```

## supports_frogspawn

- 青蛙卵可以放置并存活在这些方块上。

- #supports_frogspawn（0项） - 无内容

## supports_hanging_mangrove_propagule

- 红树胎生苗可以在这些方块下存活。不能手动放置。

- #supports_hanging_mangrove_propagule（1项） - ``` mangrove_leaves ``` （红树树叶）

## supports_lily_pad

- 睡莲可以放置并存活在这些方块上。

- #supports_lily_pad（2项） - ``` ice ``` （冰） - ``` frosted_ice ``` （霜冰）

## supports_mangrove_propagule

- 红树胎生苗可以放置并存活在这些方块上。

- #supports_mangrove_propagule（2项） - ``` #supports_vegetation ``` - ``` clay ``` （黏土）

## supports_melon_stem

- 西瓜茎可以放置并存活在这些方块上。

- #supports_melon_stem（1项） - ``` #supports_stem_crops ```

## supports_melon_stem_fruit

- 西瓜茎能在这些方块上方生成西瓜。

- #supports_melon_stem_fruit（1项） - ``` #supports_stem_fruit ```

## supports_nether_sprouts

- 下界苗可以放置并存活在这些方块上。

- #supports_nether_sprouts（3项） - ``` #supports_vegetation ``` - ``` #nylium ``` - ``` soul_soil ``` （灵魂土）

## supports_nether_wart

- 下界疣可以放置并存活在这些方块上。

- #supports_nether_wart（1项） - ``` soul_sand ``` （灵魂沙）

## supports_pumpkin_stem

- 南瓜茎可以放置并存活在这些方块上。

- #supports_pumpkin_stem（1项） - ``` #supports_stem_crops ```

## supports_pumpkin_stem_fruit

- 南瓜茎能在这些方块上方生成南瓜。

- #supports_pumpkin_stem_fruit（1项） - ``` #supports_stem_fruit ```

## supports_small_dripleaf

- 小型垂滴叶可以放置并存活在这些方块上。

- #supports_small_dripleaf（2项） - ``` clay ``` （黏土） - ``` moss_block ``` （苔藓块）

## supports_stem_crops

- 西瓜茎或南瓜茎可以放置并存活在这些方块上。

- #supports_stem_crops（1项） - ``` #supports_crops ```

## supports_stem_fruit

- #supports_stem_fruit（1项） - ``` #supports_vegetation ```

## supports_sugar_cane

- 甘蔗可以放置并存活在这些方块上。

- #supports_sugar_cane（2项） - ``` #substrate_overworld ``` - ``` #sand ```

## supports_sugar_cane_adjacently

- 甘蔗可以放置并存活在这些方块毗邻方块上。

- #supports_sugar_cane_adjacently（1项） - ``` frosted_ice ``` （霜冰）

## supports_vegetation

- 灌木丛、矮草丛、高草丛、蕨、大型蕨、瓶子草、向日葵、丁香、玫瑰丛、牡丹、眼眸花、萤火虫灌木丛、粉红色花簇、野花簇、蒲公英、火把花、虞美人、兰花、绒球葱、红色郁金香、橙色郁金香、白色郁金香、粉红色郁金香、滨菊、矢车菊、甜浆果丛、橡树树苗、白桦树苗、云杉树苗、丛林树苗、金合欢树苗、深色橡树树苗、樱花树苗、苍白橡树树苗可以放置并存活在这些方块上。

- #supports_vegetation（2项） - ``` #substrate_overworld ``` - ``` farmland ``` （耕地）

## supports_warped_fungus

- 诡异菌可以放置并存活在这些方块上。

- #supports_warped_fungus（4项） - ``` #supports_vegetation ``` - ``` #nylium ``` - ``` mycelium ``` （菌丝体） - ``` soul_soil ``` （灵魂土）

## supports_warped_roots

- 诡异菌索可以放置并存活在这些方块上。

- #supports_warped_roots（3项） - ``` #supports_vegetation ``` - ``` #nylium ``` - ``` soul_soil ``` （灵魂土）

## supports_wither_rose

- 凋灵玫瑰可以放置并存活在这些方块上。

- #supports_wither_rose（4项） - ``` #supports_vegetation ``` - ``` netherrack ``` （下界岩） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## suppresses_bounce

- 实体与这些方块碰撞后会减小弹性。

- #suppresses_bounce（1项） - ``` honey_block ``` （蜂蜜块）

## sword_efficient

- 被剑以1.5倍的速度破坏的方块。

- #sword_efficient（12项） - ``` #leaves ``` - ``` vine ``` （藤蔓） - ``` glow_lichen ``` （发光地衣） - ``` pumpkin ``` （南瓜） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` jack_o_lantern ``` （南瓜灯） - ``` melon ``` （西瓜） - ``` cocoa ``` （可可果） - ``` big_dripleaf ``` （大型垂滴叶） - ``` big_dripleaf_stem ``` （大型垂滴叶茎） - ``` chorus_plant ``` （紫颂植株） - ``` chorus_flower ``` （紫颂花）

## sword_instantly_mines

- 可被剑瞬间破坏的方块。

- #sword_instantly_mines（2项） - ``` bamboo ``` （竹子） - ``` bamboo_sapling ``` （竹笋）

## terracotta

- #terracotta（17项） - ``` terracotta ``` （陶瓦） - ``` white_terracotta ``` （白色陶瓦） - ``` orange_terracotta ``` （橙色陶瓦） - ``` magenta_terracotta ``` （品红色陶瓦） - ``` light_blue_terracotta ``` （淡蓝色陶瓦） - ``` yellow_terracotta ``` （黄色陶瓦） - ``` lime_terracotta ``` （黄绿色陶瓦） - ``` pink_terracotta ``` （粉红色陶瓦） - ``` gray_terracotta ``` （灰色陶瓦） - ``` light_gray_terracotta ``` （淡灰色陶瓦） - ``` cyan_terracotta ``` （青色陶瓦） - ``` purple_terracotta ``` （紫色陶瓦） - ``` blue_terracotta ``` （蓝色陶瓦） - ``` brown_terracotta ``` （棕色陶瓦） - ``` green_terracotta ``` （绿色陶瓦） - ``` red_terracotta ``` （红色陶瓦） - ``` black_terracotta ``` （黑色陶瓦）

## trail_ruins_replaceable

- 可疑的沙砾可以替换古迹废墟中的这些方块生成。

- #trail_ruins_replaceable（1项） - ``` gravel ``` （沙砾）

## trapdoors

- 当寻路时，生物把这个标签中的所有方块都视为活板门。

- #trapdoors（10项） - ``` #wooden_trapdoors ``` - ``` iron_trapdoor ``` （铁活板门） - ``` copper_trapdoor ``` （铜活板门） - ``` exposed_copper_trapdoor ``` （斑驳的铜活板门） - ``` weathered_copper_trapdoor ``` （锈蚀的铜活板门） - ``` oxidized_copper_trapdoor ``` （氧化的铜活板门） - ``` waxed_copper_trapdoor ``` （涂蜡的铜活板门） - ``` waxed_exposed_copper_trapdoor ``` （涂蜡的斑驳铜活板门） - ``` waxed_weathered_copper_trapdoor ``` （涂蜡的锈蚀铜活板门） - ``` waxed_oxidized_copper_trapdoor ``` （涂蜡的氧化铜活板门）

## triggers_ambient_desert_dry_vegetation_block_sounds

- 指定哪些方块可以触发沙漠环境音效。

- #triggers_ambient_desert_dry_vegetation_block_sounds（3项） - ``` #terracotta ``` - ``` sand ``` （沙子） - ``` red_sand ``` （红沙）

## triggers_ambient_dried_ghast_block_sounds

- 在沙子和红沙的环境音效判定中有效的方块。

- #triggers_ambient_dried_ghast_block_sounds（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## triggers_ambient_desert_sand_block_sounds

- 在失水恶魂的环境音效判定中有效的方块。

- #triggers_ambient_desert_sand_block_sounds（2项） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙）

## turns_into_dirt_path

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 可以被锹转变为土径的方块。

- #turns_into_dirt_path（6项） - ``` grass_block ``` （草方块） - ``` dirt ``` （泥土） - ``` podzol ``` （灰化土） - ``` coarse_dirt ``` （砂土） - ``` mycelium ``` （菌丝体） - ``` rooted_dirt ``` （缠根泥土）

## turns_into_farmland

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 可以被锄转变为耕地的方块。

- #turns_into_farmland（3项） - ``` grass_block ``` （草方块） - ``` dirt_path ``` （土径） - ``` dirt ``` （泥土）

## underwater_bonemeals

- 当在暖洋生物群系中在水下使用骨粉时，该标签中的方块将取代水源方块（在5个水平块和2个垂直块内）。
- 如果该标记中的方块是自定义的，则该行为将应用于任何生物群系中的水源方块。这些方块在默认情况下不会含水。

- #underwater_bonemeals（3项） - ``` seagrass ``` （海草） - ``` #corals ``` - ``` #wall_corals ```

## unstable_bottom_center

- #unstable_bottom_center（1项） - ``` #fence_gates ```

## valid_spawn

- 用于确定位置是否是玩家的有效出生位置。

- #valid_spawn（2项） - ``` grass_block ``` （草方块） - ``` podzol ``` （灰化土）

## vibration_resonators

- 可以产生共振的方块。

- #vibration_resonators（1项） - ``` amethyst_block ``` （紫水晶块）

## villager_babies_can_jump_on_bed

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 幼年村民可以在上面跳跃的方块。

- #villager_babies_can_jump_on_bed（1项） - ``` #beds ```

## villagers_can_sleep_on_bed

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 村民可以睡在上面的方块。

- #villagers_can_sleep_on_bed（1项） - ``` #beds ```

## wall_corals

- 用于生成珊瑚礁。

- #wall_corals（5项） - ``` tube_coral_wall_fan ``` （墙上的管珊瑚扇） - ``` brain_coral_wall_fan ``` （墙上的脑纹珊瑚扇） - ``` bubble_coral_wall_fan ``` （墙上的气泡珊瑚扇） - ``` fire_coral_wall_fan ``` （墙上的火珊瑚扇） - ``` horn_coral_wall_fan ``` （墙上的鹿角珊瑚扇）

## wall_hanging_signs

- 用于 ``` #all_hanging_signs ``` 。

- #wall_hanging_signs（13项） - ``` oak_wall_hanging_sign ``` （墙上的悬挂式橡木告示牌） - ``` spruce_wall_hanging_sign ``` （墙上的悬挂式云杉木告示牌） - ``` birch_wall_hanging_sign ``` （墙上的悬挂式白桦木告示牌） - ``` acacia_wall_hanging_sign ``` （墙上的悬挂式金合欢木告示牌） - ``` cherry_wall_hanging_sign ``` （墙上的悬挂式樱花木告示牌） - ``` jungle_wall_hanging_sign ``` （墙上的悬挂式丛林木告示牌） - ``` dark_oak_wall_hanging_sign ``` （墙上的悬挂式深色橡木告示牌） - ``` pale_oak_wall_hanging_sign ``` （墙上的悬挂式苍白橡木告示牌） - ``` crimson_wall_hanging_sign ``` （墙上的悬挂式绯红木告示牌） - ``` warped_wall_hanging_sign ``` （墙上的悬挂式诡异木告示牌） - ``` mangrove_wall_hanging_sign ``` （墙上的悬挂式红树木告示牌） - ``` bamboo_wall_hanging_sign ``` （墙上的悬挂式竹告示牌） - ``` poplar_wall_hanging_sign ``` （墙上的悬挂式杨木告示牌）

## wall_post_override

- 插在墙上，墙会出现柱子。

- #wall_post_override（9项） - ``` torch ``` （火把） - ``` soul_torch ``` （灵魂火把） - ``` redstone_torch ``` （红石火把） - ``` copper_torch ``` （铜火把） - ``` tripwire ``` （绊线） - ``` #signs ``` - ``` #banners ``` - ``` #pressure_plates ``` - ``` cactus_flower ``` （仙人掌花）

## wall_signs

- #wall_signs（13项） - ``` oak_wall_sign ``` （墙上的橡木告示牌） - ``` spruce_wall_sign ``` （墙上的云杉木告示牌） - ``` birch_wall_sign ``` （墙上的白桦木告示牌） - ``` acacia_wall_sign ``` （墙上的金合欢木告示牌） - ``` jungle_wall_sign ``` （墙上的丛林木告示牌） - ``` dark_oak_wall_sign ``` （墙上的深色橡木告示牌） - ``` pale_oak_wall_sign ``` （墙上的苍白橡木告示牌） - ``` crimson_wall_sign ``` （墙上的绯红木告示牌） - ``` warped_wall_sign ``` （墙上的诡异木告示牌） - ``` mangrove_wall_sign ``` （墙上的红树木告示牌） - ``` bamboo_wall_sign ``` （墙上的竹告示牌） - ``` cherry_wall_sign ``` （墙上的樱花木告示牌） - ``` poplar_wall_sign ``` （墙上的杨木告示牌）

## walls

- 当寻路时，生物把这个标签中的方块视为栅栏。
- 栅栏门紧挨着这些方块时，方块状态 ``` in_wall ``` 的值为 ``` true ``` 。

- #walls（32项） - ``` cobblestone_wall ``` （圆石墙） - ``` mossy_cobblestone_wall ``` （苔石墙） - ``` brick_wall ``` （红砖墙） - ``` prismarine_wall ``` （海晶石墙） - ``` red_sandstone_wall ``` （红砂岩墙） - ``` mossy_stone_brick_wall ``` （苔石砖墙） - ``` granite_wall ``` （花岗岩墙） - ``` stone_brick_wall ``` （石砖墙） - ``` nether_brick_wall ``` （下界砖墙） - ``` andesite_wall ``` （安山岩墙） - ``` red_nether_brick_wall ``` （红色下界砖墙） - ``` sandstone_wall ``` （砂岩墙） - ``` end_stone_brick_wall ``` （末地石砖墙） - ``` diorite_wall ``` （闪长岩墙） - ``` blackstone_wall ``` （黑石墙） - ``` polished_blackstone_brick_wall ``` （磨制黑石砖墙） - ``` polished_blackstone_wall ``` （磨制黑石墙） - ``` cobbled_deepslate_wall ``` （深板岩圆石墙） - ``` polished_deepslate_wall ``` （磨制深板岩墙） - ``` deepslate_tile_wall ``` （深板岩瓦墙） - ``` deepslate_brick_wall ``` （深板岩砖墙） - ``` mud_brick_wall ``` （泥砖墙） - ``` tuff_wall ``` （凝灰岩墙） - ``` polished_tuff_wall ``` （磨制凝灰岩墙） - ``` tuff_brick_wall ``` （凝灰岩砖墙） - ``` resin_brick_wall ``` （树脂砖墙） - ``` cinnabar_wall ``` （朱砂墙） - ``` polished_cinnabar_wall ``` （磨制朱砂墙） - ``` cinnabar_brick_wall ``` （朱砂砖墙） - ``` sulfur_wall ``` （硫黄墙） - ``` polished_sulfur_wall ``` （磨制硫黄墙） - ``` sulfur_brick_wall ``` （硫黄砖墙）

## warped_stems

- #warped_stems（4项） - ``` warped_stem ``` （诡异菌柄） - ``` stripped_warped_stem ``` （去皮诡异菌柄） - ``` warped_hyphae ``` （诡异菌核） - ``` stripped_warped_hyphae ``` （去皮诡异菌核）

## wart_blocks

- 疣猪兽不能生成在这些方块上。

- #wart_blocks（2项） - ``` nether_wart_block ``` （下界疣块） - ``` warped_wart_block ``` （诡异疣块）

## washed_away_by_fluids

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 流体流动时会破坏这些方块。如果方块本身不会被流体流动破坏，则此标签没有效果。

- #washed_away_by_fluids（134项） - ``` #fire ``` - ``` #saplings ``` - ``` #corals ``` - ``` #wall_corals ``` - ``` #air ``` - ``` #flower_pots ``` - ``` #buttons ``` - ``` #wool_carpets ``` - ``` #candles ``` - ``` #rails ``` - ``` #skulls ``` - ``` copper_golem_statue ``` （铜傀儡像） - ``` exposed_copper_golem_statue ``` （斑驳的铜傀儡像） - ``` weathered_copper_golem_statue ``` （锈蚀的铜傀儡像） - ``` oxidized_copper_golem_statue ``` （氧化的铜傀儡像） - ``` waxed_copper_golem_statue ``` （涂蜡的铜傀儡像） - ``` waxed_exposed_copper_golem_statue ``` （涂蜡的斑驳铜傀儡像） - ``` waxed_weathered_copper_golem_statue ``` （涂蜡的锈蚀铜傀儡像） - ``` waxed_oxidized_copper_golem_statue ``` （涂蜡的氧化铜傀儡像） - ``` water ``` （水） - ``` lava ``` （熔岩） - ``` tall_seagrass ``` （高海草） - ``` wall_torch ``` （墙上的火把） - ``` redstone_wall_torch ``` （墙上的红石火把） - ``` soul_wall_torch ``` （墙上的灵魂火把） - ``` copper_wall_torch ``` （墙上的铜火把） - ``` attached_pumpkin_stem ``` （结果的南瓜茎） - ``` attached_melon_stem ``` （结果的西瓜茎） - ``` kelp_plant ``` （海带植株） - ``` weeping_vines_plant ``` （垂泪藤植株） - ``` twisting_vines_plant ``` （缠怨藤植株） - ``` cave_vines_plant ``` （洞穴藤蔓植株） - ``` big_dripleaf_stem ``` （大型垂滴叶茎） - ``` skeleton_wall_skull ``` （墙上的骷髅头颅） - ``` wither_skeleton_wall_skull ``` （墙上的凋灵骷髅头颅） - ``` zombie_wall_head ``` （墙上的僵尸的头） - ``` player_wall_head ``` （墙上的玩家的头） - ``` creeper_wall_head ``` （墙上的苦力怕的头） - ``` dragon_wall_head ``` （墙上的龙首） - ``` piglin_wall_head ``` （墙上的猪灵的头） - ``` bamboo_sapling ``` （竹笋） - ``` cobweb ``` （蜘蛛网） - ``` snow ``` （雪） - ``` end_rod ``` （末地烛） - ``` chorus_plant ``` （紫颂植株） - ``` chorus_flower ``` （紫颂花） - ``` big_dripleaf ``` （大型垂滴叶） - ``` scaffolding ``` （脚手架） - ``` powder_snow ``` （细雪） - ``` short_grass ``` （矮草丛） - ``` fern ``` （蕨） - ``` dead_bush ``` （枯萎的灌木） - ``` bush ``` （灌木丛） - ``` short_dry_grass ``` （矮枯草丛） - ``` tall_dry_grass ``` （高枯草丛） - ``` seagrass ``` （海草） - ``` dandelion ``` （蒲公英） - ``` golden_dandelion ``` （金蒲公英） - ``` torchflower ``` （火把花） - ``` poppy ``` （虞美人） - ``` blue_orchid ``` （兰花） - ``` allium ``` （绒球葱） - ``` azure_bluet ``` （蓝花美耳草） - ``` red_tulip ``` （红色郁金香） - ``` orange_tulip ``` （橙色郁金香） - ``` white_tulip ``` （白色郁金香） - ``` pink_tulip ``` （粉红色郁金香） - ``` oxeye_daisy ``` （滨菊） - ``` cornflower ``` （矢车菊） - ``` wither_rose ``` （凋灵玫瑰） - ``` lily_of_the_valley ``` （铃兰） - ``` brown_mushroom ``` （棕色蘑菇） - ``` red_mushroom ``` （红色蘑菇） - ``` torch ``` （火把） - ``` redstone_wire ``` （红石线） - ``` wheat ``` （小麦植株） - ``` lever ``` （拉杆） - ``` redstone_torch ``` （红石火把） - ``` cactus_flower ``` （仙人掌花） - ``` soul_torch ``` （灵魂火把） - ``` copper_torch ``` （铜火把） - ``` pumpkin_stem ``` （南瓜茎） - ``` melon_stem ``` （西瓜茎） - ``` vine ``` （藤蔓） - ``` glow_lichen ``` （发光地衣） - ``` resin_clump ``` （树脂团） - ``` nether_wart ``` （下界疣） - ``` tripwire_hook ``` （绊线钩） - ``` tripwire ``` （绊线） - ``` carrots ``` （胡萝卜） - ``` potatoes ``` （马铃薯） - ``` light ``` （光源方块） - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` rose_bush ``` （玫瑰丛） - ``` peony ``` （牡丹） - ``` tall_grass ``` （高草丛） - ``` large_fern ``` （大型蕨） - ``` torchflower_crop ``` （火把花植株） - ``` pitcher_crop ``` （瓶子草植株） - ``` pitcher_plant ``` （瓶子草） - ``` beetroots ``` （甜菜根） - ``` kelp ``` （海带） - ``` sweet_berry_bush ``` （甜浆果丛） - ``` warped_fungus ``` （诡异菌） - ``` warped_roots ``` （诡异菌索） - ``` nether_sprouts ``` （下界苗） - ``` crimson_fungus ``` （绯红菌） - ``` weeping_vines ``` （垂泪藤） - ``` twisting_vines ``` （缠怨藤） - ``` crimson_roots ``` （绯红菌索） - ``` cave_vines ``` （洞穴藤蔓） - ``` spore_blossom ``` （孢子花） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` leaf_litter ``` （枯叶堆） - ``` small_dripleaf ``` （小型垂滴叶） - ``` hanging_roots ``` （垂根） - ``` frogspawn ``` （青蛙卵） - ``` pale_hanging_moss ``` （苍白垂须） - ``` open_eyeblossom ``` （张开的眼眸花） - ``` closed_eyeblossom ``` （闭合的眼眸花） - ``` firefly_bush ``` （萤火虫灌木丛） - ``` repeater ``` （红石中继器） - ``` lily_pad ``` （睡莲） - ``` cocoa ``` （可可果） - ``` comparator ``` （红石比较器） - ``` sea_pickle ``` （海泡菜） - ``` moss_carpet ``` （覆地苔藓） - ``` heavy_core ``` （沉重核心） - ``` pale_moss_carpet ``` （苍白覆地苔藓） - ``` red_shrub ``` （红灌木） - ``` shelf_mushroom ``` （层孔菇） - ``` straw_bed ``` （麦秆床）

## wither_immune

- 用来确定哪些方块凋灵不能破坏。

- #wither_immune（15项） - ``` barrier ``` （屏障） - ``` bedrock ``` （基岩） - ``` end_portal ``` （末地传送门） - ``` end_portal_frame ``` （末地传送门框架） - ``` end_gateway ``` （末地折跃门） - ``` command_block ``` （命令方块） - ``` repeating_command_block ``` （循环型命令方块） - ``` chain_command_block ``` （连锁型命令方块） - ``` structure_block ``` （结构方块） - ``` jigsaw ``` （拼图方块） - ``` moving_piston ``` （移动的活塞） - ``` light ``` （光源方块） - ``` reinforced_deepslate ``` （强化深板岩） - ``` test_block ``` （测试方块） - ``` test_instance_block ``` （测试实例方块）

## wither_immune_to

- 凋零不会将这些方块视为危险方块。

- #wither_immune_to（1项） - ``` wither_rose ``` （凋灵玫瑰）

## wither_skeleton_immune_to

- 凋零骷髅不会将这些方块视为危险方块。

- #wither_skeleton_immune_to（1项） - ``` wither_rose ``` （凋灵玫瑰）

## wither_summon_base_blocks

- 可以用来搭建凋灵的方块。

- #wither_summon_base_blocks（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## wolves_spawnable_on

- 用于狼的生成判定。

- #wolves_spawnable_on（5项） - ``` grass_block ``` （草方块） - ``` snow ``` （雪） - ``` snow_block ``` （雪块） - ``` coarse_dirt ``` （砂土） - ``` podzol ``` （灰化土）

## wooden_buttons

- 用于 ``` #buttons ``` 。

- #wooden_buttons（13项） - ``` oak_button ``` （橡木按钮） - ``` spruce_button ``` （云杉木按钮） - ``` birch_button ``` （白桦木按钮） - ``` jungle_button ``` （丛林木按钮） - ``` acacia_button ``` （金合欢木按钮） - ``` dark_oak_button ``` （深色橡木按钮） - ``` pale_oak_button ``` （苍白橡木按钮） - ``` crimson_button ``` （绯红木按钮） - ``` warped_button ``` （诡异木按钮） - ``` mangrove_button ``` （红树木按钮） - ``` bamboo_button ``` （竹按钮） - ``` cherry_button ``` （樱花木按钮） - ``` poplar_button ``` （杨木按钮）

## wooden_doors

- 用于标签 ``` #doors ``` 。 村民用它来检测门。

- #wooden_doors（13项） - ``` oak_door ``` （橡木门） - ``` spruce_door ``` （云杉木门） - ``` birch_door ``` （白桦木门） - ``` jungle_door ``` （丛林木门） - ``` acacia_door ``` （金合欢木门） - ``` dark_oak_door ``` （深色橡木门） - ``` pale_oak_door ``` （苍白橡木门） - ``` crimson_door ``` （绯红木门） - ``` warped_door ``` （诡异木门） - ``` mangrove_door ``` （红树木门） - ``` bamboo_door ``` （竹门） - ``` cherry_door ``` （樱花木门） - ``` poplar_door ``` （杨木门）

## wooden_fences

- #wooden_fences（13项） - ``` oak_fence ``` （橡木栅栏） - ``` acacia_fence ``` （金合欢木栅栏） - ``` dark_oak_fence ``` （深色橡木栅栏） - ``` pale_oak_fence ``` （苍白橡木栅栏） - ``` spruce_fence ``` （云杉木栅栏） - ``` birch_fence ``` （白桦木栅栏） - ``` jungle_fence ``` （丛林木栅栏） - ``` crimson_fence ``` （绯红木栅栏） - ``` warped_fence ``` （诡异木栅栏） - ``` mangrove_fence ``` （红树木栅栏） - ``` bamboo_fence ``` （竹栅栏） - ``` cherry_fence ``` （樱花木栅栏） - ``` poplar_fence ``` （杨木栅栏）

## wooden_pressure_plates

- #wooden_pressure_plates（13项） - ``` oak_pressure_plate ``` （橡木压力板） - ``` spruce_pressure_plate ``` （云杉木压力板） - ``` birch_pressure_plate ``` （白桦木压力板） - ``` jungle_pressure_plate ``` （丛林木压力板） - ``` acacia_pressure_plate ``` （金合欢木压力板） - ``` dark_oak_pressure_plate ``` （深色橡木压力板） - ``` pale_oak_pressure_plate ``` （苍白橡木压力板） - ``` crimson_pressure_plate ``` （绯红木压力板） - ``` warped_pressure_plate ``` （诡异木压力板） - ``` mangrove_pressure_plate ``` （红树木压力板） - ``` bamboo_pressure_plate ``` （竹压力板） - ``` cherry_pressure_plate ``` （樱花木压力板） - ``` poplar_pressure_plate ``` （杨木压力板）

## wooden_slabs

- #wooden_slabs（13项） - ``` oak_slab ``` （橡木台阶） - ``` spruce_slab ``` （云杉木台阶） - ``` birch_slab ``` （白桦木台阶） - ``` jungle_slab ``` （丛林木台阶） - ``` acacia_slab ``` （金合欢木台阶） - ``` dark_oak_slab ``` （深色橡木台阶） - ``` pale_oak_slab ``` （苍白橡木台阶） - ``` crimson_slab ``` （绯红木台阶） - ``` warped_slab ``` （诡异木台阶） - ``` mangrove_slab ``` （红树木台阶） - ``` bamboo_slab ``` （竹台阶） - ``` cherry_slab ``` （樱花木台阶） - ``` poplar_slab ``` （杨木台阶）

## wooden_stairs

- #wooden_stairs（13项） - ``` oak_stairs ``` （橡木楼梯） - ``` spruce_stairs ``` （云杉木楼梯） - ``` birch_stairs ``` （白桦木楼梯） - ``` jungle_stairs ``` （丛林木楼梯） - ``` acacia_stairs ``` （金合欢木楼梯） - ``` dark_oak_stairs ``` （深色橡木楼梯） - ``` pale_oak_stairs ``` （苍白橡木楼梯） - ``` crimson_stairs ``` （绯红木楼梯） - ``` warped_stairs ``` （诡异木楼梯） - ``` mangrove_stairs ``` （红树木楼梯） - ``` bamboo_stairs ``` （竹楼梯） - ``` cherry_stairs ``` （樱花木楼梯） - ``` poplar_stairs ``` （杨木楼梯）

## wooden_shelves

- 包含所有木质展示架。

- #wooden_shelves（13项） - ``` acacia_shelf ``` （金合欢木展示架） - ``` bamboo_shelf ``` （竹展示架） - ``` birch_shelf ``` （白桦木展示架） - ``` cherry_shelf ``` （樱花木展示架） - ``` crimson_shelf ``` （绯红木展示架） - ``` dark_oak_shelf ``` （深色橡木展示架） - ``` jungle_shelf ``` （丛林木展示架） - ``` mangrove_shelf ``` （红树木展示架） - ``` oak_shelf ``` （橡木展示架） - ``` pale_oak_shelf ``` （苍白橡木展示架） - ``` spruce_shelf ``` （云杉木展示架） - ``` warped_shelf ``` （诡异木展示架） - ``` poplar_shelf ``` （杨木展示架）

## wooden_trapdoors

- #wooden_trapdoors（13项） - ``` acacia_trapdoor ``` （金合欢木活板门） - ``` birch_trapdoor ``` （白桦木活板门） - ``` dark_oak_trapdoor ``` （深色橡木活板门） - ``` pale_oak_trapdoor ``` （苍白橡木活板门） - ``` jungle_trapdoor ``` （丛林木活板门） - ``` oak_trapdoor ``` （橡木活板门） - ``` spruce_trapdoor ``` （云杉木活板门） - ``` crimson_trapdoor ``` （绯红木活板门） - ``` warped_trapdoor ``` （诡异木活板门） - ``` mangrove_trapdoor ``` （红树木活板门） - ``` bamboo_trapdoor ``` （竹活板门） - ``` cherry_trapdoor ``` （樱花木活板门） - ``` poplar_trapdoor ``` （杨木活板门）

## wool

- 放在该标签的方块上的音符盒会发出吉他音效。 - 如果导致音符盒播放不同乐器音效的方块加入此标签，则这些方块会导致音符盒播放吉他。
- 用于 ``` #occludes_vibration_signals ``` 。

- #wool（16项） - ``` white_wool ``` （白色羊毛） - ``` orange_wool ``` （橙色羊毛） - ``` magenta_wool ``` （品红色羊毛） - ``` light_blue_wool ``` （淡蓝色羊毛） - ``` yellow_wool ``` （黄色羊毛） - ``` lime_wool ``` （黄绿色羊毛） - ``` pink_wool ``` （粉红色羊毛） - ``` gray_wool ``` （灰色羊毛） - ``` light_gray_wool ``` （淡灰色羊毛） - ``` cyan_wool ``` （青色羊毛） - ``` purple_wool ``` （紫色羊毛） - ``` blue_wool ``` （蓝色羊毛） - ``` brown_wool ``` （棕色羊毛） - ``` green_wool ``` （绿色羊毛） - ``` red_wool ``` （红色羊毛） - ``` black_wool ``` （黑色羊毛）

## wool_carpets

- #wool_carpets（16项） - ``` white_carpet ``` （白色地毯） - ``` orange_carpet ``` （橙色地毯） - ``` magenta_carpet ``` （品红色地毯） - ``` light_blue_carpet ``` （淡蓝色地毯） - ``` yellow_carpet ``` （黄色地毯） - ``` lime_carpet ``` （黄绿色地毯） - ``` pink_carpet ``` （粉红色地毯） - ``` gray_carpet ``` （灰色地毯） - ``` light_gray_carpet ``` （淡灰色地毯） - ``` cyan_carpet ``` （青色地毯） - ``` purple_carpet ``` （紫色地毯） - ``` blue_carpet ``` （蓝色地毯） - ``` brown_carpet ``` （棕色地毯） - ``` green_carpet ``` （绿色地毯） - ``` red_carpet ``` （红色地毯） - ``` black_carpet ``` （黑色地毯）

## wool_stairs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #wool_stairs（16项） - ``` white_wool_stairs ``` （白色羊毛楼梯） - ``` orange_wool_stairs ``` （橙色羊毛楼梯） - ``` magenta_wool_stairs ``` （品红色羊毛楼梯） - ``` light_blue_wool_stairs ``` （淡蓝色羊毛楼梯） - ``` yellow_wool_stairs ``` （黄色羊毛楼梯） - ``` lime_wool_stairs ``` （黄绿色羊毛楼梯） - ``` pink_wool_stairs ``` （粉红色羊毛楼梯） - ``` gray_wool_stairs ``` （灰色羊毛楼梯） - ``` light_gray_wool_stairs ``` （淡灰色羊毛楼梯） - ``` cyan_wool_stairs ``` （青色羊毛楼梯） - ``` purple_wool_stairs ``` （紫色羊毛楼梯） - ``` blue_wool_stairs ``` （蓝色羊毛楼梯） - ``` brown_wool_stairs ``` （棕色羊毛楼梯） - ``` green_wool_stairs ``` （绿色羊毛楼梯） - ``` red_wool_stairs ``` （红色羊毛楼梯） - ``` black_wool_stairs ``` （黑色羊毛楼梯）

## wool_slabs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #wool_slabs（16项） - ``` white_wool_slab ``` （白色羊毛台阶） - ``` orange_wool_slab ``` （橙色羊毛台阶） - ``` magenta_wool_slab ``` （品红色羊毛台阶） - ``` light_blue_wool_slab ``` （淡蓝色羊毛台阶） - ``` yellow_wool_slab ``` （黄色羊毛台阶） - ``` lime_wool_slab ``` （黄绿色羊毛台阶） - ``` pink_wool_slab ``` （粉红色羊毛台阶） - ``` gray_wool_slab ``` （灰色羊毛台阶） - ``` light_gray_wool_slab ``` （淡灰色羊毛台阶） - ``` cyan_wool_slab ``` （青色羊毛台阶） - ``` purple_wool_slab ``` （紫色羊毛台阶） - ``` blue_wool_slab ``` （蓝色羊毛台阶） - ``` brown_wool_slab ``` （棕色羊毛台阶） - ``` green_wool_slab ``` （绿色羊毛台阶） - ``` red_wool_slab ``` （红色羊毛台阶） - ``` black_wool_slab ``` （黑色羊毛台阶）

# 已移除的标签

## azalea_log_replaceable

添加于：21w05a。移除于：21w10a。

- #azalea_log_replaceable（6项） - ``` #flowers ``` - ``` #leaves ``` - ``` short_grass ``` - ``` fern ``` - ``` sweet_berry_bush ``` - ``` small_dripleaf ```

## dirt_like

添加于：18w43a。移除于：19w41a。

- #dirt_like（5项） - ``` dirt ``` - ``` grass_block ``` - ``` podzol ``` - ``` coarse_dirt ``` - ``` mycelium ```

## fire_aspect_lightable

- 能被带火焰附加魔咒的物品攻击点燃的方块。

添加于：24w19a。移除于：Java版1.21-pre1。

- #fire_aspect_lightable（3项） - ``` #candles ``` - ``` #candle_cakes ``` - ``` #campfires ```

## lush_plants_replaceable

- 被 ``` moss_replaceable ``` 替代。

添加于：21w05a。移除于：21w16a。

- #lush_plants_replaceable（14项） - ``` #base_stone_overworld ``` - ``` #cave_vines ``` - ``` dirt ``` - ``` gravel ``` - ``` sand ``` - ``` moss_block ``` - ``` #flowers ``` - ``` short_grass ``` - ``` tall_grass ``` - ``` moss_carpet ``` - ``` small_dripleaf ``` - ``` big_dripleaf ``` - ``` big_dripleaf_stem ``` - ``` vine ```

## non_flammable_wood

在物品标签中仍存在与此同名的标签。

添加于：20w13a。移除于：22w44a。

- #non_flammable_wood（34项） - ``` warped_stem ``` - ``` stripped_warped_stem ``` - ``` warped_hyphae ``` - ``` stripped_warped_hyphae ``` - ``` crimson_stem ``` - ``` stripped_crimson_stem ``` - ``` crimson_hyphae ``` - ``` stripped_crimson_hyphae ``` - ``` crimson_planks ``` - ``` warped_planks ``` - ``` crimson_slab ``` - ``` warped_slab ``` - ``` crimson_pressure_plate ``` - ``` warped_pressure_plate ``` - ``` crimson_fence ``` - ``` warped_fence ``` - ``` crimson_trapdoor ``` - ``` warped_trapdoor ``` - ``` crimson_fence_gate ``` - ``` warped_fence_gate ``` - ``` crimson_stairs ``` - ``` warped_stairs ``` - ``` crimson_button ``` - ``` warped_button ``` - ``` crimson_door ``` - ``` warped_door ``` - ``` crimson_sign ``` - ``` warped_sign ``` - ``` crimson_wall_sign ``` - ``` warped_wall_sign ``` - ``` crimson_hanging_sign ``` - ``` warped_hanging_sign ``` - ``` crimson_wall_hanging_sign ``` - ``` warped_wall_hanging_sign ```

## replaceable_plants

- 被 ``` replaceable_by_trees ``` 替代。

添加于：Java版1.18-pre5。移除于：23w14a。

- #replaceable_plants（12项） - ``` short_grass ``` - ``` fern ``` - ``` dead_bush ``` - ``` vine ``` - ``` glow_lichen ``` - ``` sunflower ``` - ``` lilac ``` - ``` rose_bush ``` - ``` peony ``` - ``` tall_grass ``` - ``` large_fern ``` - ``` hanging_roots ```

## stripped_logs

添加于：22w42a。移除于：22w46a。

- #stripped_logs（9项） - ``` stripped_oak_log ``` - ``` stripped_spruce_log ``` - ``` stripped_birch_log ``` - ``` stripped_jungle_log ``` - ``` stripped_acacia_log ``` - ``` stripped_dark_oak_log ``` - ``` stripped_crimson_stem ``` - ``` stripped_warped_stem ``` - ``` stripped_mangrove_log ```

## tall_flowers

添加于：19w34a。移除于：24w45a。

- #tall_flowers（5项） - ``` sunflower ``` - ``` lilac ``` - ``` peony ``` - ``` rose_bush ``` - ``` pitcher_plant ```

## water_hacked

添加于：18w07a。移除于：18w10c。

- #water_hacked（4项） - ``` #stairs ``` - ``` #waterlogged ``` - ``` #slabs ``` - ``` chest ```

## waterlogged

添加于：18w07b。移除于：18w10c。

- #waterlogged（5项） - ``` bubble_column ``` - ``` kelp ``` - ``` kelp_top ``` - ``` sea_grass ``` - ``` tall_sea_grass ```

# 历史

# 导航

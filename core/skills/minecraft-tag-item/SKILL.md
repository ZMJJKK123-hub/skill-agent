---
name: minecraft-tag-item
description: |
  Java版标签/物品（Minecraft Wiki 中文版全量正文）。
  
  【概述】物品标签（Item Tags）是物品的组合。
  
  【涵盖内容】
  - acacia_logs
  - anvil
  - armadillo_food
  - arrows
  - axes
  - axolotl_food
  - bamboo_blocks
  - banners
  - bars
  - beacon_payment_items
  - beds
  - bee_food
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/物品 的完整规范时
---

本条目所述内容仅适用于Java版。
物品标签（Item Tags）是物品的组合。

# 使用

物品标签常用于物品类型的判断。例如物品谓词、配方原料、命令
```
/
execute
 if items
```

等。只要物品在此标签内，测试就会成功。

在创造模式物品栏中，可以使用
```
#<
任意文字
>
```

来依靠标签搜索物品。

游戏也使用物品标签控制了一些游戏行为。

# 标签列表

## acacia_logs

- 用于 ``` acacia_planks.json ``` 进度和配方文件。

- #acacia_logs（4项） - ``` acacia_log ``` （金合欢原木） - ``` acacia_wood ``` （金合欢木） - ``` stripped_acacia_log ``` （去皮金合欢原木） - ``` stripped_acacia_wood ``` （去皮金合欢木）

## anvil

- #anvil（3项） - ``` anvil ``` （铁砧） - ``` chipped_anvil ``` （开裂的铁砧） - ``` damaged_anvil ``` （损坏的铁砧）

## armadillo_food

- 可以用于喂食犰狳的物品。

- #armadillo_food（1项） - ``` spider_eye ``` （蜘蛛眼）

## arrows

- 控制哪些物品可以被弓和弩射出。添加到标签中的任何物品都可以像箭一样被射出和捡起。

- #arrows（3项） - ``` arrow ``` （箭） - ``` tipped_arrow ``` （药箭） - ``` spectral_arrow ``` （光灵箭）

## axes

- #axes（7项） - ``` diamond_axe ``` （钻石斧） - ``` stone_axe ``` （石斧） - ``` golden_axe ``` （金斧） - ``` netherite_axe ``` （下界合金斧） - ``` wooden_axe ``` （木斧） - ``` iron_axe ``` （铁斧） - ``` copper_axe ``` （铜斧）

## axolotl_food

- 可用于喂食、引诱美西螈的物品。

- #axolotl_food（1项） - ``` tropical_fish_bucket ``` （热带鱼桶）

## bamboo_blocks

- #bamboo_blocks（2项） - ``` bamboo_block ``` （竹块） - ``` stripped_bamboo_block ``` （去皮竹块）

## banners

- 被视为旗帜的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #banners（16项） - ``` white_banner ``` （白色旗帜） - ``` orange_banner ``` （橙色旗帜） - ``` magenta_banner ``` （品红色旗帜） - ``` light_blue_banner ``` （淡蓝色旗帜） - ``` yellow_banner ``` （黄色旗帜） - ``` lime_banner ``` （黄绿色旗帜） - ``` pink_banner ``` （粉红色旗帜） - ``` gray_banner ``` （灰色旗帜） - ``` light_gray_banner ``` （淡灰色旗帜） - ``` cyan_banner ``` （青色旗帜） - ``` purple_banner ``` （紫色旗帜） - ``` blue_banner ``` （蓝色旗帜） - ``` brown_banner ``` （棕色旗帜） - ``` green_banner ``` （绿色旗帜） - ``` red_banner ``` （红色旗帜） - ``` black_banner ``` （黑色旗帜）

## bars

- #bars（9项） - ``` iron_bars ``` （铁栏杆） - ``` copper_bars ``` （铜栏杆） - ``` exposed_copper_bars ``` （斑驳的铜栏杆） - ``` weathered_copper_bars ``` （锈蚀的铜栏杆） - ``` oxidized_copper_bars ``` （氧化的铜栏杆） - ``` waxed_copper_bars ``` （涂蜡的铜栏杆） - ``` waxed_exposed_copper_bars ``` （涂蜡的斑驳铜栏杆） - ``` waxed_weathered_copper_bars ``` （涂蜡的锈蚀铜栏杆） - ``` waxed_oxidized_copper_bars ``` （涂蜡的氧化铜栏杆）

## beacon_payment_items

- 用于检查哪些物品可以放置在信标GUI中以选择效果。

- #beacon_payment_items（5项） - ``` netherite_ingot ``` （下界合金锭） - ``` emerald ``` （绿宝石） - ``` diamond ``` （钻石） - ``` gold_ingot ``` （金锭） - ``` iron_ingot ``` （铁锭）

## beds

- #beds（16项） - ``` white_bed ``` （白色床） - ``` orange_bed ``` （橙色床） - ``` magenta_bed ``` （品红色床） - ``` light_blue_bed ``` （淡蓝色床） - ``` yellow_bed ``` （黄色床） - ``` lime_bed ``` （黄绿色床） - ``` pink_bed ``` （粉红色床） - ``` gray_bed ``` （灰色床） - ``` light_gray_bed ``` （淡灰色床） - ``` cyan_bed ``` （青色床） - ``` purple_bed ``` （紫色床） - ``` blue_bed ``` （蓝色床） - ``` brown_bed ``` （棕色床） - ``` green_bed ``` （绿色床） - ``` red_bed ``` （红色床） - ``` black_bed ``` （黑色床）

## bee_food

- 可以用于喂食蜜蜂的物品。

- #bee_food（29项） - ``` dandelion ``` （蒲公英） - ``` open_eyeblossom ``` （张开的眼眸花） - ``` poppy ``` （虞美人） - ``` blue_orchid ``` （兰花） - ``` allium ``` （绒球葱） - ``` azure_bluet ``` （蓝花美耳草） - ``` red_tulip ``` （红色郁金香） - ``` orange_tulip ``` （橙色郁金香） - ``` white_tulip ``` （白色郁金香） - ``` pink_tulip ``` （粉红色郁金香） - ``` oxeye_daisy ``` （滨菊） - ``` cornflower ``` （矢车菊） - ``` lily_of_the_valley ``` （铃兰） - ``` wither_rose ``` （凋灵玫瑰） - ``` torchflower ``` （火把花） - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` peony ``` （牡丹） - ``` rose_bush ``` （玫瑰丛） - ``` pitcher_plant ``` （瓶子草） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_leaves ``` （樱花树叶） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` chorus_flower ``` （紫颂花） - ``` spore_blossom ``` （孢子花） - ``` cactus_flower ``` （仙人掌花）

## birch_logs

- 用于 ``` birch_planks.json ``` 进度和配方文件。

- #birch_logs（4项） - ``` birch_log ``` （白桦原木） - ``` birch_wood ``` （白桦木） - ``` stripped_birch_log ``` （去皮白桦原木） - ``` stripped_birch_wood ``` （去皮白桦木）

## boats

- 被视为船或运输船的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加1200刻的燃烧时间。

- #boats（12项） - ``` oak_boat ``` （橡木船） - ``` spruce_boat ``` （云杉木船） - ``` birch_boat ``` （白桦木船） - ``` jungle_boat ``` （丛林木船） - ``` acacia_boat ``` （金合欢木船） - ``` dark_oak_boat ``` （深色橡木船） - ``` pale_oak_boat ``` （苍白橡木船） - ``` mangrove_boat ``` （红树木船） - ``` bamboo_raft ``` （竹筏） - ``` cherry_boat ``` （樱花木船） - ``` poplar_boat ``` （杨木船） - ``` #chest_boats ```

## book_cloning_target

- 可通过与成书合成来复制的物品。

- #book_cloning_target（1项） - ``` writable_book ``` （书与笔）

## bookshelf_books

- 可以被放入雕纹书架的柜位里的物品。

- #bookshelf_books（5项） - ``` book ``` （书） - ``` written_book ``` （成书） - ``` enchanted_book ``` （附魔书） - ``` writable_book ``` （书与笔） - ``` knowledge_book ``` （知识之书）

## breaks_decorated_pots

- 使用未附有精准采集魔咒且在此标签下的物品破坏饰纹陶罐会将其 ``` cracked ``` 方块状态设置为 ``` true ``` 。

- #breaks_decorated_pots（7项） - ``` #swords ``` - ``` #axes ``` - ``` #pickaxes ``` - ``` #shovels ``` - ``` #hoes ``` - ``` trident ``` （三叉戟） - ``` mace ``` （重锤）

## brewing_fuel

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

- 带有此标签的物品可被放入酿造台的燃料槽位并消耗。任意物品都会提供与烈焰粉相同的热值。

- #brewing_fuel（1项） - ``` blaze_powder ``` （烈焰粉）

## bundles

- 用于进度和收纳袋染色配方。

- #bundles（17项） - ``` bundle ``` （收纳袋） - ``` white_bundle ``` （白色收纳袋） - ``` orange_bundle ``` （橙色收纳袋） - ``` magenta_bundle ``` （品红色收纳袋） - ``` light_blue_bundle ``` （淡蓝色收纳袋） - ``` yellow_bundle ``` （黄色收纳袋） - ``` lime_bundle ``` （黄绿色收纳袋） - ``` pink_bundle ``` （粉红色收纳袋） - ``` gray_bundle ``` （灰色收纳袋） - ``` light_gray_bundle ``` （淡灰色收纳袋） - ``` cyan_bundle ``` （青色收纳袋） - ``` purple_bundle ``` （紫色收纳袋） - ``` blue_bundle ``` （蓝色收纳袋） - ``` brown_bundle ``` （棕色收纳袋） - ``` green_bundle ``` （绿色收纳袋） - ``` red_bundle ``` （红色收纳袋） - ``` black_bundle ``` （黑色收纳袋）

## buttons

- 被视为按钮的物品

- #buttons（2项） - ``` #wooden_buttons ``` - ``` #stone_buttons ```

## camel_food

- 可以用于喂食骆驼的物品。

- #camel_food（1项） - ``` cactus ``` （仙人掌）

## camel_husk_food

- 可以用于喂食骆驼尸壳的物品。

- #camel_husk_food（1项） - ``` rabbit_foot ``` （兔子脚）

## candles

- 蛋糕使用这个标签来决定蜡烛物品是否能放置在上面。
- 将其他物品加入这个标签不会有任何作用。

- #candles（17项） - ``` candle ``` （蜡烛） - ``` white_candle ``` （白色蜡烛） - ``` orange_candle ``` （橙色蜡烛） - ``` magenta_candle ``` （品红色蜡烛） - ``` light_blue_candle ``` （淡蓝色蜡烛） - ``` yellow_candle ``` （黄色蜡烛） - ``` lime_candle ``` （黄绿色蜡烛） - ``` pink_candle ``` （粉红色蜡烛） - ``` gray_candle ``` （灰色蜡烛） - ``` light_gray_candle ``` （淡灰色蜡烛） - ``` cyan_candle ``` （青色蜡烛） - ``` purple_candle ``` （紫色蜡烛） - ``` blue_candle ``` （蓝色蜡烛） - ``` brown_candle ``` （棕色蜡烛） - ``` green_candle ``` （绿色蜡烛） - ``` red_candle ``` （红色蜡烛） - ``` black_candle ``` （黑色蜡烛）

## cat_collar_dyes

- 用于给猫的项圈染色的物品,设置的颜色取自物品的 ``` minecraft:dye ``` 组件。

- #cat_collar_dyes（1项） - ``` #dyes ```

## cat_food

- 可以用于喂食猫的物品。

- #cat_food（2项） - ``` cod ``` （生鳕鱼） - ``` salmon ``` （生鲑鱼）

## cauldron_can_remove_dye

- 可以在装有水的炼药锅中使用以去除 ``` minecraft:dyed_color ``` 组件的物品。

- #cauldron_can_remove_dye（6项） - ``` leather_helmet ``` （皮革帽子） - ``` leather_chestplate ``` （皮革外套） - ``` leather_leggings ``` （皮革裤子） - ``` leather_boots ``` （皮革靴子） - ``` leather_horse_armor ``` （皮革马铠） - ``` wolf_armor ``` （狼铠）

## chains

- #chains（9项） - ``` iron_chain ``` （铁链） - ``` copper_chain ``` （铜链） - ``` exposed_copper_chain ``` （斑驳的铜链） - ``` weathered_copper_chain ``` （锈蚀的铜链） - ``` oxidized_copper_chain ``` （氧化的铜链） - ``` waxed_copper_chain ``` （涂蜡的铜链） - ``` waxed_exposed_copper_chain ``` （涂蜡的斑驳铜链） - ``` waxed_weathered_copper_chain ``` （涂蜡的锈蚀铜链） - ``` waxed_oxidized_copper_chain ``` （涂蜡的氧化铜链）

## cherry_logs

- #cherry_logs（4项） - ``` cherry_log ``` （樱花原木） - ``` cherry_wood ``` （樱花木） - ``` stripped_cherry_log ``` （去皮樱花原木） - ``` stripped_cherry_wood ``` （去皮樱花木）

## chest_armor

- 属于胸部盔甲（胸甲）的物品。

- #chest_armor（7项） - ``` leather_chestplate ``` （皮革外套） - ``` copper_chestplate ``` （铜胸甲） - ``` chainmail_chestplate ``` （锁链胸甲） - ``` golden_chestplate ``` （金胸甲） - ``` iron_chestplate ``` （铁胸甲） - ``` diamond_chestplate ``` （钻石胸甲） - ``` netherite_chestplate ``` （下界合金胸甲）

## chest_boats

- 被视为运输船的物品。

- #chest_boats（11项） - ``` oak_chest_boat ``` （橡木运输船） - ``` spruce_chest_boat ``` （云杉木运输船） - ``` birch_chest_boat ``` （白桦木运输船） - ``` jungle_chest_boat ``` （丛林木运输船） - ``` acacia_chest_boat ``` （金合欢木运输船） - ``` dark_oak_chest_boat ``` （深色橡木运输船） - ``` pale_oak_chest_boat ``` （苍白橡木运输船） - ``` mangrove_chest_boat ``` （红树木运输船） - ``` bamboo_chest_raft ``` （运输竹筏） - ``` cherry_chest_boat ``` （樱花木运输船） - ``` poplar_chest_boat ``` （杨木运输船）

## chicken_food

- 可以用于喂食鸡的物品。

- #chicken_food（6项） - ``` wheat_seeds ``` （小麦种子） - ``` melon_seeds ``` （西瓜种子） - ``` pumpkin_seeds ``` （南瓜种子） - ``` beetroot_seeds ``` （甜菜种子） - ``` torchflower_seeds ``` （火把花种子） - ``` pitcher_pod ``` （瓶子草荚果）

## clonable_maps

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 可以被复制的地图。

- #clonable_maps（17项） - ``` filled_map ``` （地图） - ``` ocean_explorer_map ``` （File:ItemSprite ocean-monument-explorer-map.png海底神殿探险家地图） - ``` woodland_explorer_map ``` （File:ItemSprite woodland-mansion-explorer-map.png林地府邸探险家地图） - ``` trial_explorer_map ``` （File:ItemSprite trial-chambers-explorer-map.png试炼密室探险家地图） - ``` jungle_explorer_map ``` （File:ItemSprite jungle-pyramid-explorer-map.png丛林神庙探险家地图） - ``` swamp_explorer_map ``` （File:ItemSprite swamp-hut-explorer-map.png沼泽小屋探险家地图） - ``` desert_village_map ``` （沙漠村庄地图） - ``` plains_village_map ``` （平原村庄地图） - ``` savanna_village_map ``` （热带草原村庄地图） - ``` snowy_village_map ``` （雪原村庄地图） - ``` taiga_village_map ``` （针叶林村庄地图） - ``` buried_treasure_map ``` （藏宝图） - ``` ancient_city_map ``` （远古城市地图） - ``` mineshaft_map ``` （Mineshaft Map） - ``` desert_pyramid_map ``` （沙漠神殿地图） - ``` abandoned_campsite_map ``` （废弃营地地图） - ``` warm_ocean_ruins_map ``` （Warm Ocean Ruins Map）

## cluster_max_harvestables

- 使用此标签下的物品破坏紫水晶簇可以获得最大掉落量的紫水晶碎片。

- #cluster_max_harvestables（7项） - ``` diamond_pickaxe ``` （钻石镐） - ``` golden_pickaxe ``` （金镐） - ``` iron_pickaxe ``` （铁镐） - ``` netherite_pickaxe ``` （下界合金镐） - ``` stone_pickaxe ``` （石镐） - ``` wooden_pickaxe ``` （木镐） - ``` copper_pickaxe ``` （铜镐）

## coal_ores

- #coal_ores（2项） - ``` coal_ore ``` （煤矿石） - ``` deepslate_coal_ore ``` （深层煤矿石）

## coals

- 用于营火的合成配方。

- #coals（2项） - ``` coal ``` （煤炭） - ``` charcoal ``` （木炭）

## compasses

- 被视为指南针的物品。

- #compasses（2项） - ``` compass ``` （指南针） - ``` recovery_compass ``` （追溯指针）

## completes_find_tree_tutorial

- 物品栏中有具此标签的物品时可完成“找到一棵树”教学提示步骤。

- #completes_find_tree_tutorial（3项） - ``` #logs ``` - ``` #leaves ``` - ``` #wart_blocks ```

## concrete

- 被视为混凝土的物品。

- #concrete（16项） - ``` white_concrete ``` （白色混凝土） - ``` orange_concrete ``` （橙色混凝土） - ``` magenta_concrete ``` （品红色混凝土） - ``` light_blue_concrete ``` （淡蓝色混凝土） - ``` yellow_concrete ``` （黄色混凝土） - ``` lime_concrete ``` （黄绿色混凝土） - ``` pink_concrete ``` （粉红色混凝土） - ``` gray_concrete ``` （灰色混凝土） - ``` light_gray_concrete ``` （淡灰色混凝土） - ``` cyan_concrete ``` （青色混凝土） - ``` purple_concrete ``` （紫色混凝土） - ``` blue_concrete ``` （蓝色混凝土） - ``` brown_concrete ``` （棕色混凝土） - ``` green_concrete ``` （绿色混凝土） - ``` red_concrete ``` （红色混凝土） - ``` black_concrete ``` （黑色混凝土）

## concrete_powders

- 被视为混凝土粉末的物品。

- #concrete_powders（16项） - ``` white_concrete_powder ``` （白色混凝土粉末） - ``` orange_concrete_powder ``` （橙色混凝土粉末） - ``` magenta_concrete_powder ``` （品红色混凝土粉末） - ``` light_blue_concrete_powder ``` （淡蓝色混凝土粉末） - ``` yellow_concrete_powder ``` （黄色混凝土粉末） - ``` lime_concrete_powder ``` （黄绿色混凝土粉末） - ``` pink_concrete_powder ``` （粉红色混凝土粉末） - ``` gray_concrete_powder ``` （灰色混凝土粉末） - ``` light_gray_concrete_powder ``` （淡灰色混凝土粉末） - ``` cyan_concrete_powder ``` （青色混凝土粉末） - ``` purple_concrete_powder ``` （紫色混凝土粉末） - ``` blue_concrete_powder ``` （蓝色混凝土粉末） - ``` brown_concrete_powder ``` （棕色混凝土粉末） - ``` green_concrete_powder ``` （绿色混凝土粉末） - ``` red_concrete_powder ``` （红色混凝土粉末） - ``` black_concrete_powder ``` （黑色混凝土粉末）

## concrete_slabs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 被视为混凝土台阶的物品。

- #concrete_slabs（16项） - ``` white_concrete_slab ``` （白色混凝土台阶） - ``` orange_concrete_slab ``` （橙色混凝土台阶） - ``` magenta_concrete_slab ``` （品红色混凝土台阶） - ``` light_blue_concrete_slab ``` （淡蓝色混凝土台阶） - ``` yellow_concrete_slab ``` （黄色混凝土台阶） - ``` lime_concrete_slab ``` （黄绿色混凝土台阶） - ``` pink_concrete_slab ``` （粉红色混凝土台阶） - ``` gray_concrete_slab ``` （灰色混凝土台阶） - ``` light_gray_concrete_slab ``` （淡灰色混凝土台阶） - ``` cyan_concrete_slab ``` （青色混凝土台阶） - ``` purple_concrete_slab ``` （紫色混凝土台阶） - ``` blue_concrete_slab ``` （蓝色混凝土台阶） - ``` brown_concrete_slab ``` （棕色混凝土台阶） - ``` green_concrete_slab ``` （绿色混凝土台阶） - ``` red_concrete_slab ``` （红色混凝土台阶） - ``` black_concrete_slab ``` （黑色混凝土台阶）

## concrete_stairs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 被视为混凝土楼梯的物品。

- #concrete_stairs（16项） - ``` white_concrete_stairs ``` （白色混凝土楼梯） - ``` orange_concrete_stairs ``` （橙色混凝土楼梯） - ``` magenta_concrete_stairs ``` （品红色混凝土楼梯） - ``` light_blue_concrete_stairs ``` （淡蓝色混凝土楼梯） - ``` yellow_concrete_stairs ``` （黄色混凝土楼梯） - ``` lime_concrete_stairs ``` （黄绿色混凝土楼梯） - ``` pink_concrete_stairs ``` （粉红色混凝土楼梯） - ``` gray_concrete_stairs ``` （灰色混凝土楼梯） - ``` light_gray_concrete_stairs ``` （淡灰色混凝土楼梯） - ``` cyan_concrete_stairs ``` （青色混凝土楼梯） - ``` purple_concrete_stairs ``` （紫色混凝土楼梯） - ``` blue_concrete_stairs ``` （蓝色混凝土楼梯） - ``` brown_concrete_stairs ``` （棕色混凝土楼梯） - ``` green_concrete_stairs ``` （绿色混凝土楼梯） - ``` red_concrete_stairs ``` （红色混凝土楼梯） - ``` black_concrete_stairs ``` （黑色混凝土楼梯）

## copper

- #copper（8项） - ``` copper_block ``` （铜块） - ``` exposed_copper ``` （斑驳的铜块） - ``` weathered_copper ``` （锈蚀的铜块） - ``` oxidized_copper ``` （氧化的铜块） - ``` waxed_copper_block ``` （涂蜡的铜块） - ``` waxed_exposed_copper ``` （涂蜡的斑驳铜块） - ``` waxed_weathered_copper ``` （涂蜡的锈蚀铜块） - ``` waxed_oxidized_copper ``` （涂蜡的氧化铜块）

## copper_chests

- #copper_chests（8项） - ``` copper_chest ``` （铜箱子） - ``` exposed_copper_chest ``` （斑驳的铜箱子） - ``` weathered_copper_chest ``` （锈蚀的铜箱子） - ``` oxidized_copper_chest ``` （氧化的铜箱子） - ``` waxed_copper_chest ``` （涂蜡的铜箱子） - ``` waxed_exposed_copper_chest ``` （涂蜡的斑驳铜箱子） - ``` waxed_weathered_copper_chest ``` （涂蜡的锈蚀铜箱子） - ``` waxed_oxidized_copper_chest ``` （涂蜡的氧化铜箱子）

## copper_golem_statues

- #copper_golem_statues（8项） - ``` copper_golem_statue ``` （铜傀儡像） - ``` exposed_copper_golem_statue ``` （斑驳的铜傀儡像） - ``` weathered_copper_golem_statue ``` （锈蚀的铜傀儡像） - ``` oxidized_copper_golem_statue ``` （氧化的铜傀儡像） - ``` waxed_copper_golem_statue ``` （涂蜡的铜傀儡像） - ``` waxed_exposed_copper_golem_statue ``` （涂蜡的斑驳铜傀儡像） - ``` waxed_weathered_copper_golem_statue ``` （涂蜡的锈蚀铜傀儡像） - ``` waxed_oxidized_copper_golem_statue ``` （涂蜡的氧化铜傀儡像）

## copper_ores

- #copper_ores（2项） - ``` copper_ore ``` （铜矿石） - ``` deepslate_copper_ore ``` （深层铜矿石）

## copper_tool_materials

- 用于铜质工具的合成配方和修复材料。

- #copper_tool_materials（1项） - ``` copper_ingot ``` （铜锭）

## cow_food

- 可以用于喂食牛的物品。

- #cow_food（1项） - ``` wheat ``` （小麦）

## creeper_drop_music_discs

- 用于确定苦力怕被骷髅杀死后掉落哪些物品。

- #creeper_drop_music_discs（12项） - ``` music_disc_13 ``` （音乐唱片） - ``` music_disc_cat ``` （音乐唱片） - ``` music_disc_blocks ``` （音乐唱片） - ``` music_disc_chirp ``` （音乐唱片） - ``` music_disc_far ``` （音乐唱片） - ``` music_disc_mall ``` （音乐唱片） - ``` music_disc_mellohi ``` （音乐唱片） - ``` music_disc_stal ``` （音乐唱片） - ``` music_disc_strad ``` （音乐唱片） - ``` music_disc_ward ``` （音乐唱片） - ``` music_disc_11 ``` （音乐唱片） - ``` music_disc_wait ``` （音乐唱片）

## creeper_igniters

- 用于确定苦力怕可被哪些物品点燃。

- #creeper_igniters（2项） - ``` flint_and_steel ``` （打火石） - ``` fire_charge ``` （火焰弹）

## crimson_stems

- 用于 ``` crimson_planks.json ``` 进度和配方文件。

- #crimson_stems（4项） - ``` crimson_stem ``` （绯红菌柄） - ``` stripped_crimson_stem ``` （去皮绯红菌柄） - ``` crimson_hyphae ``` （绯红菌核） - ``` stripped_crimson_hyphae ``` （去皮绯红菌核）

## cushions

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #cushions（16项） - ``` white_cushion ``` （白色坐垫） - ``` orange_cushion ``` （橙色坐垫） - ``` magenta_cushion ``` （品红色坐垫） - ``` light_blue_cushion ``` （淡蓝色坐垫） - ``` yellow_cushion ``` （黄色坐垫） - ``` lime_cushion ``` （黄绿色坐垫） - ``` pink_cushion ``` （粉红色坐垫） - ``` gray_cushion ``` （灰色坐垫） - ``` light_gray_cushion ``` （淡灰色坐垫） - ``` cyan_cushion ``` （青色坐垫） - ``` purple_cushion ``` （紫色坐垫） - ``` blue_cushion ``` （蓝色坐垫） - ``` brown_cushion ``` （棕色坐垫） - ``` green_cushion ``` （绿色坐垫） - ``` red_cushion ``` （红色坐垫） - ``` black_cushion ``` （黑色坐垫）

## dampens_vibrations

- #dampens_vibrations（4项） - ``` #wool ``` - ``` #wool_carpets ``` - ``` #wool_slabs ``` - ``` #wool_stairs ```

## dark_oak_logs

- 用于 ``` dark_oak_planks.json ``` 进度和配方文件。

- #dark_oak_logs（4项） - ``` dark_oak_log ``` （深色橡木原木） - ``` dark_oak_wood ``` （深色橡木） - ``` stripped_dark_oak_log ``` （去皮深色橡木原木） - ``` stripped_dark_oak_wood ``` （去皮深色橡木）

## decorated_pot_ingredients

- 带有此标签的物品能合成饰纹陶罐。

- #decorated_pot_ingredients（2项） - ``` brick ``` （红砖） - ``` #decorated_pot_sherds ```

## decorated_pot_sherds

- #decorated_pot_sherds（23项） - ``` angler_pottery_sherd ``` （垂钓纹样陶片） - ``` archer_pottery_sherd ``` （弓箭纹样陶片） - ``` arms_up_pottery_sherd ``` （举臂纹样陶片） - ``` blade_pottery_sherd ``` （利刃纹样陶片） - ``` brewer_pottery_sherd ``` （佳酿纹样陶片） - ``` burn_pottery_sherd ``` （烈焰纹样陶片） - ``` danger_pottery_sherd ``` （危机纹样陶片） - ``` explorer_pottery_sherd ``` （探险纹样陶片） - ``` friend_pottery_sherd ``` （挚友纹样陶片） - ``` heart_pottery_sherd ``` （爱心纹样陶片） - ``` heartbreak_pottery_sherd ``` （心碎纹样陶片） - ``` howl_pottery_sherd ``` （狼嚎纹样陶片） - ``` miner_pottery_sherd ``` （采矿纹样陶片） - ``` mourner_pottery_sherd ``` （悲恸纹样陶片） - ``` plenty_pottery_sherd ``` （富饶纹样陶片） - ``` prize_pottery_sherd ``` （珍宝纹样陶片） - ``` sheaf_pottery_sherd ``` （麦捆纹样陶片） - ``` shelter_pottery_sherd ``` （树荫纹样陶片） - ``` skull_pottery_sherd ``` （头颅纹样陶片） - ``` snort_pottery_sherd ``` （嗅探纹样陶片） - ``` flow_pottery_sherd ``` （涡流纹样陶片） - ``` guster_pottery_sherd ``` （旋风纹样陶片） - ``` scrape_pottery_sherd ``` （刮削纹样陶片）

## diamond_ores

- #diamond_ores（2项） - ``` diamond_ore ``` （钻石矿石） - ``` deepslate_diamond_ore ``` （深层钻石矿石）

## diamond_tool_materials

- 用于钻石工具的合成配方和修复材料。

- #diamond_tool_materials（1项） - ``` diamond ``` （钻石）

## dirt

- #dirt（3项） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` rooted_dirt ``` （缠根泥土）

## doors

- 被视为门的物品。

- #doors（10项） - ``` #wooden_doors ``` - ``` copper_door ``` （铜门） - ``` exposed_copper_door ``` （斑驳的铜门） - ``` weathered_copper_door ``` （锈蚀的铜门） - ``` oxidized_copper_door ``` （氧化的铜门） - ``` waxed_copper_door ``` （涂蜡的铜门） - ``` waxed_exposed_copper_door ``` （涂蜡的斑驳铜门） - ``` waxed_weathered_copper_door ``` （涂蜡的锈蚀铜门） - ``` waxed_oxidized_copper_door ``` （涂蜡的氧化铜门） - ``` iron_door ``` （铁门）

## douses_campfires

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 可以用于熄灭营火的物品。

- #douses_campfires（1项） - ``` #shovels ```

## drowned_preferred_weapons

- 溺尸更愿意拾取的物品。

- #drowned_preferred_weapons（1项） - ``` trident ``` （三叉戟）

## duplicates_allays

- 带有此标签的物品可对跳舞的悦灵使用以复制悦灵。

- #duplicates_allays（1项） - ``` amethyst_shard ``` （紫水晶碎片）

## dyes

- 被视为染料的物品。

- #dyes（16项） - ``` white_dye ``` （白色染料） - ``` orange_dye ``` （橙色染料） - ``` magenta_dye ``` （品红色染料） - ``` light_blue_dye ``` （淡蓝色染料） - ``` yellow_dye ``` （黄色染料） - ``` lime_dye ``` （黄绿色染料） - ``` pink_dye ``` （粉红色染料） - ``` gray_dye ``` （灰色染料） - ``` light_gray_dye ``` （淡灰色染料） - ``` cyan_dye ``` （青色染料） - ``` purple_dye ``` （紫色染料） - ``` blue_dye ``` （蓝色染料） - ``` brown_dye ``` （棕色染料） - ``` green_dye ``` （绿色染料） - ``` red_dye ``` （红色染料） - ``` black_dye ``` （黑色染料）

## eggs

- 被视为鸡蛋的物品。

- #eggs（3项） - ``` egg ``` （鸡蛋） - ``` blue_egg ``` （蓝色鸡蛋） - ``` brown_egg ``` （棕色鸡蛋）

## emerald_ores

- #emerald_ores（2项） - ``` emerald_ore ``` （绿宝石矿石） - ``` deepslate_emerald_ore ``` （深层绿宝石矿石）

## enchantable/armor

- 可以附上适用于盔甲的魔咒的物品。

- #enchantable/armor（4项） - ``` #enchantable/foot_armor ``` - ``` #enchantable/leg_armor ``` - ``` #enchantable/chest_armor ``` - ``` #enchantable/head_armor ```

## enchantable/bow

- 可以附上适用于弓的魔咒的物品。

- #enchantable/bow（1项） - ``` bow ``` （弓）

## enchantable/chest_armor

- 可以附上适用于胸甲的魔咒的物品。

- #enchantable/chest_armor（1项） - ``` #chest_armor ```

## enchantable/crossbow

- 可以附上适用于弩的魔咒的物品。

- #enchantable/crossbow（1项） - ``` crossbow ``` （弩）

## enchantable/durability

- 可以附上影响耐久度的魔咒的物品。

- #enchantable/durability（22项） - ``` #foot_armor ``` - ``` #leg_armor ``` - ``` #chest_armor ``` - ``` #head_armor ``` - ``` elytra ``` （鞘翅） - ``` shield ``` （盾牌） - ``` #swords ``` - ``` #axes ``` - ``` #pickaxes ``` - ``` #shovels ``` - ``` #hoes ``` - ``` bow ``` （弓） - ``` crossbow ``` （弩） - ``` trident ``` （三叉戟） - ``` flint_and_steel ``` （打火石） - ``` shears ``` （剪刀） - ``` brush ``` （刷子） - ``` fishing_rod ``` （钓鱼竿） - ``` carrot_on_a_stick ``` （胡萝卜钓竿） - ``` warped_fungus_on_a_stick ``` （诡异菌钓竿） - ``` mace ``` （重锤） - ``` #spears ```

## enchantable/equippable

- 可以附上可装备（Equippable）魔咒的物品。

- #enchantable/equippable（7项） - ``` #foot_armor ``` - ``` #leg_armor ``` - ``` #chest_armor ``` - ``` #head_armor ``` - ``` elytra ``` （鞘翅） - ``` #skulls ``` - ``` carved_pumpkin ``` （雕刻南瓜）

## enchantable/fire_aspect

- 可附魔火焰附加魔咒的物品

- #enchantable/fire_aspect（2项） - ``` #enchantable/melee_weapon ``` - ``` mace ``` （重锤）

## enchantable/fishing

- 可以附上适用于钓鱼竿的魔咒的物品。

- #enchantable/fishing（1项） - ``` fishing_rod ``` （钓鱼竿）

## enchantable/foot_armor

- 可以附上适用于靴子的魔咒的物品。

- #enchantable/foot_armor（1项） - ``` #foot_armor ```

## enchantable/head_armor

- 可以附上适用于头盔的魔咒的物品。

- #enchantable/head_armor（1项） - ``` #head_armor ```

## enchantable/leg_armor

- 可以附上适用于护腿的魔咒的物品。

- #enchantable/leg_armor（1项） - ``` #leg_armor ```

## enchantable/lunge

- 可以附上突进魔咒的物品。

- #enchantable/lunge（1项） - ``` #spears ```

## enchantable/mace

- 可以附上适用于重锤的魔咒的物品。

- #enchantable/mace（1项） - ``` mace ``` （重锤）

## enchantable/melee_weapon

- 可以附上适用于近战武器的魔咒的物品。

- #enchantable/melee_weapon（2项） - ``` #swords ``` - ``` #spears ```

## enchantable/mining

- 可以附上影响挖掘速度的魔咒的物品。

- #enchantable/mining（5项） - ``` #axes ``` - ``` #pickaxes ``` - ``` #shovels ``` - ``` #hoes ``` - ``` shears ``` （剪刀）

## enchantable/mining_loot

- 可以附上影响挖掘掉落物的魔咒的物品。

- #enchantable/mining_loot（4项） - ``` #axes ``` - ``` #pickaxes ``` - ``` #shovels ``` - ``` #hoes ```

## enchantable/sharp_weapon

- 可以附上锋利魔咒的物品。

- #enchantable/sharp_weapon（2项） - ``` #enchantable/melee_weapon ``` - ``` #axes ```

## enchantable/sweeping

- 可以附上横扫之刃魔咒的物品。

- #enchantable/sweeping（1项） - ``` #swords ```

## enchantable/trident

- 可以附上适用于三叉戟的魔咒的物品。

- #enchantable/trident（1项） - ``` trident ``` （三叉戟）

## enchantable/vanishing

- 可以附上可使物品消失的魔咒的物品。

- #enchantable/vanishing（4项） - ``` #enchantable/durability ``` - ``` compass ``` （指南针） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` #skulls ```

## enchantable/weapon

- 可以附上适用于武器的魔咒的物品。

- #enchantable/weapon（2项） - ``` #enchantable/sharp_weapon ``` - ``` mace ``` （重锤）

## extendable_maps

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 可以被比例缩小的地图。

- #extendable_maps（1项） - ``` filled_map ``` （地图）

## fence_gates

- 被视为栅栏门的物品。

- #fence_gates（13项） - ``` acacia_fence_gate ``` （金合欢木栅栏门） - ``` birch_fence_gate ``` （白桦木栅栏门） - ``` dark_oak_fence_gate ``` （深色橡木栅栏门） - ``` pale_oak_fence_gate ``` （苍白橡木栅栏门） - ``` jungle_fence_gate ``` （丛林木栅栏门） - ``` oak_fence_gate ``` （橡木栅栏门） - ``` spruce_fence_gate ``` （云杉木栅栏门） - ``` crimson_fence_gate ``` （绯红木栅栏门） - ``` warped_fence_gate ``` （诡异木栅栏门） - ``` mangrove_fence_gate ``` （红树木栅栏门） - ``` bamboo_fence_gate ``` （竹栅栏门） - ``` cherry_fence_gate ``` （樱花木栅栏门） - ``` poplar_fence_gate ``` （杨木栅栏门）

## fences

- 被视为栅栏的物品。

- #fences（2项） - ``` #wooden_fences ``` - ``` nether_brick_fence ``` （下界砖栅栏）

## fishes

- 此标签中的物品出现在玩家的主手或副手中时，海豚会背着玩家游泳。
- 使用此标签中的物品喂养海豚会使它们“信任”玩家。
- 用于统计已捕获的鱼的数量的fish_caught统计数据。

- #fishes（6项） - ``` cod ``` （生鳕鱼） - ``` cooked_cod ``` （熟鳕鱼） - ``` salmon ``` （生鲑鱼） - ``` cooked_salmon ``` （熟鲑鱼） - ``` pufferfish ``` （河豚） - ``` tropical_fish ``` （热带鱼）

## flowers

- #flowers（15项） - ``` #small_flowers ``` - ``` sunflower ``` （向日葵） - ``` lilac ``` （丁香） - ``` peony ``` （牡丹） - ``` rose_bush ``` （玫瑰丛） - ``` pitcher_plant ``` （瓶子草） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_leaves ``` （樱花树叶） - ``` pink_petals ``` （粉红色花簇） - ``` wildflowers ``` （野花簇） - ``` chorus_flower ``` （紫颂花） - ``` spore_blossom ``` （孢子花） - ``` cactus_flower ``` （仙人掌花）

## foot_armor

- 属于脚部盔甲（靴子）的物品。

- #foot_armor（7项） - ``` leather_boots ``` （皮革靴子） - ``` copper_boots ``` （铜靴子） - ``` chainmail_boots ``` （锁链靴子） - ``` golden_boots ``` （金靴子） - ``` iron_boots ``` （铁靴子） - ``` diamond_boots ``` （钻石靴子） - ``` netherite_boots ``` （下界合金靴子）

## fox_food

- 可以用于喂食狐狸的物品。

- #fox_food（2项） - ``` sweet_berries ``` （甜浆果） - ``` glow_berries ``` （发光浆果）

## freeze_immune_wearables

- 穿戴拥有此标签的物品可以使玩家免疫冰冻伤害。

- #freeze_immune_wearables（5项） - ``` leather_boots ``` （皮革靴子） - ``` leather_leggings ``` （皮革裤子） - ``` leather_chestplate ``` （皮革外套） - ``` leather_helmet ``` （皮革帽子） - ``` leather_horse_armor ``` （皮革马铠）

## frog_food

- 可以用于喂食青蛙的物品。

- #frog_food（1项） - ``` slime_ball ``` （黏液球）

## furnace_minecart_fuel

- 用于给动力矿车填充燃料的物品。

- #furnace_minecart_fuel（2项） - ``` coal ``` （煤炭） - ``` charcoal ``` （木炭）

## gaze_disguise_equipment

- 掩饰正在注视其他生物的玩家。

- #gaze_disguise_equipment（1项） - ``` carved_pumpkin ``` （雕刻南瓜）

## glazed_terracotta

- #glazed_terracotta（16项） - ``` white_glazed_terracotta ``` （白色带釉陶瓦） - ``` orange_glazed_terracotta ``` （橙色带釉陶瓦） - ``` magenta_glazed_terracotta ``` （品红色带釉陶瓦） - ``` light_blue_glazed_terracotta ``` （淡蓝色带釉陶瓦） - ``` yellow_glazed_terracotta ``` （黄色带釉陶瓦） - ``` lime_glazed_terracotta ``` （黄绿色带釉陶瓦） - ``` pink_glazed_terracotta ``` （粉红色带釉陶瓦） - ``` gray_glazed_terracotta ``` （灰色带釉陶瓦） - ``` light_gray_glazed_terracotta ``` （淡灰色带釉陶瓦） - ``` cyan_glazed_terracotta ``` （青色带釉陶瓦） - ``` purple_glazed_terracotta ``` （紫色带釉陶瓦） - ``` blue_glazed_terracotta ``` （蓝色带釉陶瓦） - ``` brown_glazed_terracotta ``` （棕色带釉陶瓦） - ``` green_glazed_terracotta ``` （绿色带釉陶瓦） - ``` red_glazed_terracotta ``` （红色带釉陶瓦） - ``` black_glazed_terracotta ``` （黑色带釉陶瓦）

## goat_food

- 可以用于喂食山羊的物品。

- #goat_food（1项） - ``` wheat ``` （小麦）

## gold_ores

- #gold_ores（3项） - ``` gold_ore ``` （金矿石） - ``` nether_gold_ore ``` （下界金矿石） - ``` deepslate_gold_ore ``` （深层金矿石）

## gold_tool_materials

- 用于金质工具的合成配方和修复材料。

- #gold_tool_materials（1项） - ``` gold_ingot ``` （金锭）

## grass_blocks

- #grass_blocks（3项） - ``` grass_block ``` （草方块） - ``` podzol ``` （灰化土） - ``` mycelium ``` （菌丝体）

## hanging_signs

- #hanging_signs（13项） - ``` oak_hanging_sign ``` （悬挂式橡木告示牌） - ``` spruce_hanging_sign ``` （悬挂式云杉木告示牌） - ``` birch_hanging_sign ``` （悬挂式白桦木告示牌） - ``` acacia_hanging_sign ``` （悬挂式金合欢木告示牌） - ``` cherry_hanging_sign ``` （悬挂式樱花木告示牌） - ``` jungle_hanging_sign ``` （悬挂式丛林木告示牌） - ``` dark_oak_hanging_sign ``` （悬挂式深色橡木告示牌） - ``` pale_oak_hanging_sign ``` （悬挂式苍白橡木告示牌） - ``` crimson_hanging_sign ``` （悬挂式绯红木告示牌） - ``` warped_hanging_sign ``` （悬挂式诡异木告示牌） - ``` mangrove_hanging_sign ``` （悬挂式红树木告示牌） - ``` poplar_hanging_sign ``` （悬挂式杨木告示牌） - ``` bamboo_hanging_sign ``` （悬挂式竹告示牌）

## happy_ghast_food

- 可以用于喂食快乐恶魂的物品。

- #happy_ghast_food（1项） - ``` snowball ``` （雪球）

## happy_ghast_tempt_items

- 可用于引诱快乐恶魂的物品。

- #happy_ghast_tempt_items（2项） - ``` #happy_ghast_food ``` - ``` #harnesses ```

## harnesses

- 被视为挽具的物品，用于其他标签。

- #harnesses（16项） - ``` white_harness ``` （白色挽具） - ``` orange_harness ``` （橙色挽具） - ``` magenta_harness ``` （品红色挽具） - ``` light_blue_harness ``` （淡蓝色挽具） - ``` yellow_harness ``` （黄色挽具） - ``` lime_harness ``` （黄绿色挽具） - ``` pink_harness ``` （粉红色挽具） - ``` gray_harness ``` （灰色挽具） - ``` light_gray_harness ``` （淡灰色挽具） - ``` cyan_harness ``` （青色挽具） - ``` purple_harness ``` （紫色挽具） - ``` blue_harness ``` （蓝色挽具） - ``` brown_harness ``` （棕色挽具） - ``` green_harness ``` （绿色挽具） - ``` red_harness ``` （红色挽具） - ``` black_harness ``` （黑色挽具）

## head_armor

- 属于头部盔甲（头盔）的物品。

- #head_armor（8项） - ``` leather_helmet ``` （皮革帽子） - ``` copper_helmet ``` （铜头盔） - ``` chainmail_helmet ``` （锁链头盔） - ``` golden_helmet ``` （金头盔） - ``` iron_helmet ``` （铁头盔） - ``` diamond_helmet ``` （钻石头盔） - ``` netherite_helmet ``` （下界合金头盔） - ``` turtle_helmet ``` （海龟壳）

## hoes

- #hoes（7项） - ``` diamond_hoe ``` （钻石锄） - ``` stone_hoe ``` （石锄） - ``` golden_hoe ``` （金锄） - ``` netherite_hoe ``` （下界合金锄） - ``` wooden_hoe ``` （木锄） - ``` iron_hoe ``` （铁锄） - ``` copper_hoe ``` （铜锄）

## hoglin_food

- 可以用于喂食疣猪兽的物品。

- #hoglin_food（1项） - ``` crimson_fungus ``` （绯红菌）

## horse_food

- 可以用于喂食马的物品。

- #horse_food（8项） - ``` wheat ``` （小麦） - ``` sugar ``` （糖） - ``` hay_block ``` （干草捆） - ``` apple ``` （苹果） - ``` carrot ``` （胡萝卜） - ``` golden_carrot ``` （金胡萝卜） - ``` golden_apple ``` （金苹果） - ``` enchanted_golden_apple ``` （附魔金苹果）

## horse_tempt_items

- 可以用于引诱马的物品。

- #horse_tempt_items（3项） - ``` golden_carrot ``` （金胡萝卜） - ``` golden_apple ``` （金苹果） - ``` enchanted_golden_apple ``` （附魔金苹果）

## ignored_by_piglin_babies

- 幼年猪灵不会试图拾起拥有这个标签的物品。 - 仍然遵循成年猪灵遵循的其他规则。

- #ignored_by_piglin_babies（1项） - ``` leather ``` （皮革）

## iron_ores

- #iron_ores（2项） - ``` iron_ore ``` （铁矿石） - ``` deepslate_iron_ore ``` （深层铁矿石）

## iron_tool_materials

- 用于铁质工具的合成配方和修复材料。

- #iron_tool_materials（1项） - ``` iron_ingot ``` （铁锭）

## jungle_logs

- 用于 ``` jungle_planks.json ``` 进度和配方文件。

- #jungle_logs（4项） - ``` jungle_log ``` （丛林原木） - ``` jungle_wood ``` （丛林木） - ``` stripped_jungle_log ``` （去皮丛林原木） - ``` stripped_jungle_wood ``` （去皮丛林木）

## lanterns

- #lanterns（10项） - ``` lantern ``` （灯笼） - ``` soul_lantern ``` （灵魂灯笼） - ``` copper_lantern ``` （铜灯笼） - ``` exposed_copper_lantern ``` （斑驳的铜灯笼） - ``` weathered_copper_lantern ``` （锈蚀的铜灯笼） - ``` oxidized_copper_lantern ``` （氧化的铜灯笼） - ``` waxed_copper_lantern ``` （涂蜡的铜灯笼） - ``` waxed_exposed_copper_lantern ``` （涂蜡的斑驳铜灯笼） - ``` waxed_weathered_copper_lantern ``` （涂蜡的锈蚀铜灯笼） - ``` waxed_oxidized_copper_lantern ``` （涂蜡的氧化铜灯笼）

## lapis_ores

- #lapis_ores（2项） - ``` lapis_ore ``` （青金石矿石） - ``` deepslate_lapis_ore ``` （深层青金石矿石）

## leaves

- #leaves（14项） - ``` jungle_leaves ``` （丛林树叶） - ``` oak_leaves ``` （橡树树叶） - ``` spruce_leaves ``` （云杉树叶） - ``` pale_oak_leaves ``` （苍白橡树树叶） - ``` dark_oak_leaves ``` （深色橡树树叶） - ``` acacia_leaves ``` （金合欢树叶） - ``` birch_leaves ``` （白桦树叶） - ``` azalea_leaves ``` （杜鹃树叶） - ``` flowering_azalea_leaves ``` （盛开的杜鹃树叶） - ``` mangrove_leaves ``` （红树树叶） - ``` cherry_leaves ``` （樱花树叶） - ``` red_poplar_leaves ``` （红色杨树树叶） - ``` orange_poplar_leaves ``` （橙色杨树树叶） - ``` yellow_poplar_leaves ``` （黄色杨树树叶）

## lectern_books

- 可以在讲台上放置的物品。讲台的实际功能取决于物品的物品堆叠组件。

- #lectern_books（2项） - ``` written_book ``` （成书） - ``` writable_book ``` （书与笔）

## leg_armor

- 属于腿部盔甲（护腿）的物品。

- #leg_armor（7项） - ``` leather_leggings ``` （皮革裤子） - ``` copper_leggings ``` （铜护腿） - ``` chainmail_leggings ``` （锁链护腿） - ``` golden_leggings ``` （金护腿） - ``` iron_leggings ``` （铁护腿） - ``` diamond_leggings ``` （钻石护腿） - ``` netherite_leggings ``` （下界合金护腿）

## lightning_rods

- #lightning_rods（8项） - ``` lightning_rod ``` （避雷针） - ``` exposed_lightning_rod ``` （斑驳的避雷针） - ``` weathered_lightning_rod ``` （锈蚀的避雷针） - ``` oxidized_lightning_rod ``` （氧化的避雷针） - ``` waxed_lightning_rod ``` （涂蜡的避雷针） - ``` waxed_exposed_lightning_rod ``` （涂蜡的斑驳避雷针） - ``` waxed_weathered_lightning_rod ``` （涂蜡的锈蚀避雷针） - ``` waxed_oxidized_lightning_rod ``` （涂蜡的氧化避雷针）

## llama_food

- 可以用于喂食羊驼的物品。

- #llama_food（2项） - ``` wheat ``` （小麦） - ``` hay_block ``` （干草捆）

## llama_tempt_items

- 可以用于引诱羊驼的物品。

- #llama_tempt_items（1项） - ``` hay_block ``` （干草捆）

## logs

- 用于各种检测，以跳过或进入“找到一棵树”教学提示步骤。

- #logs（3项） - ``` #logs_that_burn ``` - ``` #crimson_stems ``` - ``` #warped_stems ```

## logs_that_burn

- 用于木炭的进度和配方文件。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #logs_that_burn（10项） - ``` #dark_oak_logs ``` - ``` #pale_oak_logs ``` - ``` #oak_logs ``` - ``` #acacia_logs ``` - ``` #birch_logs ``` - ``` #jungle_logs ``` - ``` #spruce_logs ``` - ``` #mangrove_logs ``` - ``` #cherry_logs ``` - ``` #poplar_logs ```

## loom_dyes

- 允许在织布机界面上设置图案颜色的物品。
- 织布机屏幕仍然需要物品堆叠具有 ``` minecraft:dye ``` 组件。

- #loom_dyes（1项） - ``` #dyes ```

## loom_patterns

- 允许在织布机界面上解锁图案的物品。
- 织布机屏幕仍然需要物品堆叠具有 ``` minecraft:provides_banner_patterns ``` 组件。

- #loom_patterns（10项） - ``` flower_banner_pattern ``` （花朵盾徽旗帜图案） - ``` creeper_banner_pattern ``` （苦力怕盾徽旗帜图案） - ``` skull_banner_pattern ``` （头颅盾徽旗帜图案） - ``` mojang_banner_pattern ``` （Mojang徽标旗帜图案） - ``` globe_banner_pattern ``` （地球旗帜图案） - ``` piglin_banner_pattern ``` （猪鼻旗帜图案） - ``` flow_banner_pattern ``` （涡流旗帜图案） - ``` guster_banner_pattern ``` （旋风旗帜图案） - ``` field_masoned_banner_pattern ``` （砖纹旗帜图案） - ``` bordure_indented_banner_pattern ``` （波纹边旗帜图案）

## mangrove_logs

- 用于 ``` mangrove_planks.json ``` 进度和配方文件。

- #mangrove_logs（4项） - ``` mangrove_log ``` （红树原木） - ``` mangrove_wood ``` （红树木） - ``` stripped_mangrove_log ``` （去皮红树原木） - ``` stripped_mangrove_wood ``` （去皮红树木）

## map_invisibility_equipment

- 能被装备以隐藏在其他玩家地图上的玩家标记的物品。

- #map_invisibility_equipment（1项） - ``` carved_pumpkin ``` （雕刻南瓜）

## meat

- 肉类物品。未被游戏直接使用，但可能包含于其他标签中。

- #meat（11项） - ``` beef ``` （生牛肉） - ``` chicken ``` （生鸡肉） - ``` cooked_beef ``` （牛排） - ``` cooked_chicken ``` （熟鸡肉） - ``` cooked_mutton ``` （熟羊肉） - ``` cooked_porkchop ``` （熟猪排） - ``` cooked_rabbit ``` （熟兔肉） - ``` mutton ``` （生羊肉） - ``` porkchop ``` （生猪排） - ``` rabbit ``` （生兔肉） - ``` rotten_flesh ``` （腐肉）

## metal_nuggets

- 用于命名牌的合成配方。

- #metal_nuggets（3项） - ``` copper_nugget ``` （铜粒） - ``` iron_nugget ``` （铁粒） - ``` gold_nugget ``` （金粒）

## moss_blocks

- #moss_blocks（2项） - ``` moss_block ``` （苔藓块） - ``` pale_moss_block ``` （苍白苔藓块）

## mud

- #mud（2项） - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根）

## mushrooms

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #mushrooms（3项） - ``` brown_mushroom ``` （棕色蘑菇） - ``` red_mushroom ``` （红色蘑菇） - ``` shelf_mushroom ``` （层孔菇）

## nautilus_bucket_food

- 可以用于喂食鹦鹉螺和僵尸鹦鹉螺的桶类物品。使用后会返还水桶。

- #nautilus_bucket_food（4项） - ``` pufferfish_bucket ``` （河豚桶） - ``` cod_bucket ``` （鳕鱼桶） - ``` salmon_bucket ``` （鲑鱼桶） - ``` tropical_fish_bucket ``` （热带鱼桶）

## nautilus_food

- 可以用于喂食鹦鹉螺和僵尸鹦鹉螺的物品。

- #nautilus_food（2项） - ``` #fishes ``` - ``` #nautilus_bucket_food ```

## nautilus_taming_items

- 可驯服鹦鹉螺和僵尸鹦鹉螺的物品。

- #nautilus_taming_items（2项） - ``` pufferfish_bucket ``` （河豚桶） - ``` pufferfish ``` （河豚）

## netherite_tool_materials

- 用于下界合金质工具的锻造配方和修复材料。

- #netherite_tool_materials（1项） - ``` netherite_ingot ``` （下界合金锭）

## non_flammable_wood

- 此标签下的物品不能作为燃料在类熔炉中燃烧。

- #non_flammable_wood（32项） - ``` warped_stem ``` （诡异菌柄） - ``` stripped_warped_stem ``` （去皮诡异菌柄） - ``` warped_hyphae ``` （诡异菌核） - ``` stripped_warped_hyphae ``` （去皮诡异菌核） - ``` crimson_stem ``` （绯红菌柄） - ``` stripped_crimson_stem ``` （去皮绯红菌柄） - ``` crimson_hyphae ``` （绯红菌核） - ``` stripped_crimson_hyphae ``` （去皮绯红菌核） - ``` crimson_planks ``` （绯红木板） - ``` warped_planks ``` （诡异木板） - ``` crimson_slab ``` （绯红木台阶） - ``` warped_slab ``` （诡异木台阶） - ``` crimson_pressure_plate ``` （绯红木压力板） - ``` warped_pressure_plate ``` （诡异木压力板） - ``` crimson_fence ``` （绯红木栅栏） - ``` warped_fence ``` （诡异木栅栏） - ``` crimson_trapdoor ``` （绯红木活板门） - ``` warped_trapdoor ``` （诡异木活板门） - ``` crimson_fence_gate ``` （绯红木栅栏门） - ``` warped_fence_gate ``` （诡异木栅栏门） - ``` crimson_stairs ``` （绯红木楼梯） - ``` warped_stairs ``` （诡异木楼梯） - ``` crimson_button ``` （绯红木按钮） - ``` warped_button ``` （诡异木按钮） - ``` crimson_door ``` （绯红木门） - ``` warped_door ``` （诡异木门） - ``` crimson_sign ``` （绯红木告示牌） - ``` warped_sign ``` （诡异木告示牌） - ``` warped_hanging_sign ``` （悬挂式诡异木告示牌） - ``` crimson_hanging_sign ``` （悬挂式绯红木告示牌） - ``` warped_shelf ``` （诡异木展示架） - ``` crimson_shelf ``` （绯红木展示架）

## noteblock_top_instruments

- 对音符盒顶部使用此标签下的物品不会触发音符盒的默认交互功能。

- #noteblock_top_instruments（7项） - ``` zombie_head ``` （僵尸的头） - ``` skeleton_skull ``` （骷髅头颅） - ``` creeper_head ``` （苦力怕的头） - ``` dragon_head ``` （龙首） - ``` wither_skeleton_skull ``` （凋灵骷髅头颅） - ``` piglin_head ``` （猪灵的头） - ``` player_head ``` （玩家的头）

## oak_logs

- 用于 ``` oak_planks.json ``` 进度和配方文件。

- #oak_logs（4项） - ``` oak_log ``` （橡木原木） - ``` oak_wood ``` （橡木） - ``` stripped_oak_log ``` （去皮橡木原木） - ``` stripped_oak_wood ``` （去皮橡木）

## ocelot_food

- 可以用于喂食豹猫的物品。

- #ocelot_food（2项） - ``` cod ``` （生鳕鱼） - ``` salmon ``` （生鲑鱼）

## ores

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #ores（9项） - ``` #copper_ores ``` - ``` #gold_ores ``` - ``` #iron_ores ``` - ``` #coal_ores ``` - ``` #diamond_ores ``` - ``` #emerald_ores ``` - ``` #lapis_ores ``` - ``` #redstone_ores ``` - ``` nether_quartz_ore ``` （下界石英矿石）

## pale_oak_logs

- #pale_oak_logs（4项） - ``` pale_oak_log ``` （苍白橡木原木） - ``` pale_oak_wood ``` （苍白橡木） - ``` stripped_pale_oak_log ``` （去皮苍白橡木原木） - ``` stripped_pale_oak_wood ``` （去皮苍白橡木）

## panda_eats_from_ground

- 带有此标签的物品能被熊猫拿起。

- #panda_eats_from_ground（2项） - ``` #panda_food ``` - ``` cake ``` （蛋糕）

## panda_food

- 可以用于喂食熊猫的物品。

- #panda_food（1项） - ``` bamboo ``` （竹子）

## parrot_food

- 可以用于喂食鹦鹉的物品。

- #parrot_food（6项） - ``` wheat_seeds ``` （小麦种子） - ``` melon_seeds ``` （西瓜种子） - ``` pumpkin_seeds ``` （南瓜种子） - ``` beetroot_seeds ``` （甜菜种子） - ``` torchflower_seeds ``` （火把花种子） - ``` pitcher_pod ``` （瓶子草荚果）

## parrot_poisonous_food

- 可以用于喂食鹦鹉并致使其中毒的物品。

- #parrot_poisonous_food（1项） - ``` cookie ``` （曲奇）

## pickaxes

- #pickaxes（7项） - ``` diamond_pickaxe ``` （钻石镐） - ``` stone_pickaxe ``` （石镐） - ``` golden_pickaxe ``` （金镐） - ``` netherite_pickaxe ``` （下界合金镐） - ``` wooden_pickaxe ``` （木镐） - ``` iron_pickaxe ``` （铁镐） - ``` copper_pickaxe ``` （铜镐）

## pig_food

- 可以用于喂食猪的物品。

- #pig_food（3项） - ``` carrot ``` （胡萝卜） - ``` potato ``` （马铃薯） - ``` beetroot ``` （甜菜根）

## piglin_food

- 猪灵可以吃下拥有这个标签的物品。
- 猪灵可以将拥有这个标签的物品放在它们的物品栏中。

- #piglin_food（2项） - ``` porkchop ``` （生猪排） - ``` cooked_porkchop ``` （熟猪排）

## piglin_loved

- 猪灵“喜爱”含有此标签的物品，并且会主动寻找它们。
- 它们也会将持有此标签物品的玩家视为持有“喜爱”的物品。
- 用于金光闪闪进度。

- #piglin_loved（26项） - ``` #gold_ores ``` - ``` gold_block ``` （金块） - ``` gilded_blackstone ``` （镶金黑石） - ``` light_weighted_pressure_plate ``` （轻质测重压力板） - ``` gold_ingot ``` （金锭） - ``` bell ``` （钟） - ``` clock ``` （时钟） - ``` golden_carrot ``` （金胡萝卜） - ``` glistering_melon_slice ``` （闪烁的西瓜片） - ``` golden_apple ``` （金苹果） - ``` enchanted_golden_apple ``` （附魔金苹果） - ``` golden_helmet ``` （金头盔） - ``` golden_chestplate ``` （金胸甲） - ``` golden_leggings ``` （金护腿） - ``` golden_boots ``` （金靴子） - ``` golden_horse_armor ``` （金马铠） - ``` golden_nautilus_armor ``` （金鹦鹉螺铠） - ``` golden_sword ``` （金剑） - ``` golden_spear ``` （金矛） - ``` golden_pickaxe ``` （金镐） - ``` golden_shovel ``` （金锹） - ``` golden_axe ``` （金斧） - ``` golden_hoe ``` （金锄） - ``` raw_gold ``` （粗金） - ``` raw_gold_block ``` （粗金块） - ``` golden_dandelion ``` （金蒲公英）

## piglin_preferred_weapons

- 成年猪灵更愿意拾取的物品。

- #piglin_preferred_weapons（2项） - ``` crossbow ``` （弩） - ``` golden_spear ``` （金矛）

## piglin_repellents

- 猪灵不会尝试捡起这些物品。

- #piglin_repellents（3项） - ``` soul_torch ``` （灵魂火把） - ``` soul_lantern ``` （灵魂灯笼） - ``` soul_campfire ``` （灵魂营火）

## piglin_safe_armor

- 猪灵不会主动攻击装备这些物品的玩家。

- #piglin_safe_armor（4项） - ``` golden_helmet ``` （金头盔） - ``` golden_chestplate ``` （金胸甲） - ``` golden_leggings ``` （金护腿） - ``` golden_boots ``` （金靴子）

## pillager_preferred_weapons

- 掠夺者更愿意拾取的物品。

- #pillager_preferred_weapons（1项） - ``` crossbow ``` （弩）

## planks

- 用于各种检测，以跳过或进入“合成木板”教学提示步骤。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #planks（13项） - ``` oak_planks ``` （橡木木板） - ``` spruce_planks ``` （云杉木板） - ``` birch_planks ``` （白桦木板） - ``` jungle_planks ``` （丛林木板） - ``` acacia_planks ``` （金合欢木板） - ``` dark_oak_planks ``` （深色橡木木板） - ``` pale_oak_planks ``` （苍白橡木木板） - ``` crimson_planks ``` （绯红木板） - ``` warped_planks ``` （诡异木板） - ``` mangrove_planks ``` （红树木板） - ``` bamboo_planks ``` （竹板） - ``` cherry_planks ``` （樱花木板） - ``` poplar_planks ``` （杨木木板）

## poplar_logs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- #poplar_logs（4项） - ``` poplar_log ``` （杨木原木） - ``` poplar_wood ``` （杨木） - ``` stripped_poplar_log ``` （去皮杨木原木） - ``` stripped_poplar_wood ``` （去皮杨木）

## rabbit_food

- 可以用于喂食兔子的物品。

- #rabbit_food（3项） - ``` carrot ``` （胡萝卜） - ``` golden_carrot ``` （金胡萝卜） - ``` dandelion ``` （蒲公英）

## rails

- #rails（4项） - ``` rail ``` （铁轨） - ``` powered_rail ``` （动力铁轨） - ``` detector_rail ``` （探测铁轨） - ``` activator_rail ``` （激活铁轨）

## redstone_ores

- #redstone_ores（2项） - ``` redstone_ore ``` （红石矿石） - ``` deepslate_redstone_ore ``` （深层红石矿石）

## repairs_chain_armor

- 锁链盔甲的维修用物品，即锁链盔甲的 ``` repairable ``` 组件默认值。

- #repairs_chain_armor（1项） - ``` iron_ingot ``` （铁锭）

## repairs_copper_armor

- 铜盔甲的维修用物品，即铜盔甲的 ``` repairable ``` 组件默认值。

- #repairs_copper_armor（1项） - ``` copper_ingot ``` （铜锭）

## repairs_diamond_armor

- 钻石盔甲的维修用物品，即钻石盔甲的 ``` repairable ``` 组件默认值。

- #repairs_diamond_armor（1项） - ``` diamond ``` （钻石）

## repairs_gold_armor

- 金盔甲的维修用物品，即金盔甲的 ``` repairable ``` 组件默认值。

- #repairs_gold_armor（1项） - ``` gold_ingot ``` （金锭）

## repairs_iron_armor

- 铁盔甲的维修用物品，即铁盔甲的 ``` repairable ``` 组件默认值。

- #repairs_iron_armor（1项） - ``` iron_ingot ``` （铁锭）

## repairs_leather_armor

- 皮革盔甲的维修用物品，即皮革盔甲的 ``` repairable ``` 组件默认值。

- #repairs_leather_armor（1项） - ``` leather ``` （皮革）

## repairs_netherite_armor

- 下界合金盔甲的维修用物品，即下界合金盔甲的 ``` repairable ``` 组件默认值。

- #repairs_netherite_armor（1项） - ``` netherite_ingot ``` （下界合金锭）

## repairs_turtle_helmet

- 海龟鳞甲盔甲的维修用物品，即海龟壳的 ``` repairable ``` 组件默认值。

- #repairs_turtle_helmet（1项） - ``` turtle_scute ``` （海龟鳞甲）

## repairs_wolf_armor

- 犰狳鳞甲盔甲的维修用物品，即狼铠的 ``` repairable ``` 组件默认值。

- #repairs_wolf_armor（1项） - ``` armadillo_scute ``` （犰狳鳞甲）

## sand

- 用于 ``` glass.json ``` 进度和配方文件。

- #sand（3项） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙） - ``` suspicious_sand ``` （可疑的沙子）

## saplings

- 用于检查一个物品是否能进入熔炉的燃料槽并增加100刻的燃烧时间。

- #saplings（12项） - ``` oak_sapling ``` （橡树树苗） - ``` spruce_sapling ``` （云杉树苗） - ``` birch_sapling ``` （白桦树苗） - ``` jungle_sapling ``` （丛林树苗） - ``` acacia_sapling ``` （金合欢树苗） - ``` dark_oak_sapling ``` （深色橡树树苗） - ``` pale_oak_sapling ``` （苍白橡树树苗） - ``` azalea ``` （杜鹃花丛） - ``` flowering_azalea ``` （盛开的杜鹃花丛） - ``` mangrove_propagule ``` （红树胎生苗） - ``` cherry_sapling ``` （樱花树苗） - ``` poplar_sapling ``` （杨树树苗）

## shearable_from_copper_golem

- 可从铜傀儡头部剪下的物品。

- #shearable_from_copper_golem（1项） - ``` poppy ``` （虞美人）

## sheep_food

- 可以用于喂食羊的物品。

- #sheep_food（1项） - ``` wheat ``` （小麦）

## shovels

- #shovels（7项） - ``` diamond_shovel ``` （钻石锹） - ``` stone_shovel ``` （石锹） - ``` golden_shovel ``` （金锹） - ``` netherite_shovel ``` （下界合金锹） - ``` wooden_shovel ``` （木锹） - ``` iron_shovel ``` （铁锹） - ``` copper_shovel ``` （铜锹）

## shulker_boxes

- 用于进度和潜影盒染色配方。

- #shulker_boxes（17项） - ``` shulker_box ``` （潜影盒） - ``` white_shulker_box ``` （白色潜影盒） - ``` orange_shulker_box ``` （橙色潜影盒） - ``` magenta_shulker_box ``` （品红色潜影盒） - ``` light_blue_shulker_box ``` （淡蓝色潜影盒） - ``` yellow_shulker_box ``` （黄色潜影盒） - ``` lime_shulker_box ``` （黄绿色潜影盒） - ``` pink_shulker_box ``` （粉红色潜影盒） - ``` gray_shulker_box ``` （灰色潜影盒） - ``` light_gray_shulker_box ``` （淡灰色潜影盒） - ``` cyan_shulker_box ``` （青色潜影盒） - ``` purple_shulker_box ``` （紫色潜影盒） - ``` blue_shulker_box ``` （蓝色潜影盒） - ``` brown_shulker_box ``` （棕色潜影盒） - ``` green_shulker_box ``` （绿色潜影盒） - ``` red_shulker_box ``` （红色潜影盒） - ``` black_shulker_box ``` （黑色潜影盒）

## signs

- 被视为告示牌的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加200刻的燃烧时间。

- #signs（13项） - ``` oak_sign ``` （橡木告示牌） - ``` spruce_sign ``` （云杉木告示牌） - ``` birch_sign ``` （白桦木告示牌） - ``` acacia_sign ``` （金合欢木告示牌） - ``` jungle_sign ``` （丛林木告示牌） - ``` dark_oak_sign ``` （深色橡木告示牌） - ``` pale_oak_sign ``` （苍白橡木告示牌） - ``` crimson_sign ``` （绯红木告示牌） - ``` warped_sign ``` （诡异木告示牌） - ``` mangrove_sign ``` （红树木告示牌） - ``` poplar_sign ``` （杨木告示牌） - ``` bamboo_sign ``` （竹告示牌） - ``` cherry_sign ``` （樱花木告示牌）

## skeleton_preferred_weapons

- 骷髅、流浪者、沼骸和焦骸更愿意拾取的物品。

- #skeleton_preferred_weapons（1项） - ``` bow ``` （弓）

## skulls

- 属于生物头颅的物品。

- #skulls（7项） - ``` player_head ``` （玩家的头） - ``` creeper_head ``` （苦力怕的头） - ``` zombie_head ``` （僵尸的头） - ``` skeleton_skull ``` （骷髅头颅） - ``` wither_skeleton_skull ``` （凋灵骷髅头颅） - ``` dragon_head ``` （龙首） - ``` piglin_head ``` （猪灵的头）

## slabs

- 被视为台阶的物品。

- #slabs（59项） - ``` #wooden_slabs ``` - ``` stone_slab ``` （石头台阶） - ``` smooth_stone_slab ``` （平滑石头台阶） - ``` stone_brick_slab ``` （石砖台阶） - ``` sandstone_slab ``` （砂岩台阶） - ``` cobblestone_slab ``` （圆石台阶） - ``` brick_slab ``` （红砖台阶） - ``` nether_brick_slab ``` （下界砖台阶） - ``` quartz_slab ``` （石英台阶） - ``` red_sandstone_slab ``` （红砂岩台阶） - ``` prismarine_slab ``` （海晶石台阶） - ``` prismarine_brick_slab ``` （海晶石砖台阶） - ``` dark_prismarine_slab ``` （暗海晶石台阶） - ``` purpur_slab ``` （紫珀台阶） - ``` end_stone_brick_slab ``` （末地石砖台阶） - ``` petrified_oak_slab ``` （石化橡木台阶） - ``` cut_sandstone_slab ``` （切制砂岩台阶） - ``` smooth_sandstone_slab ``` （平滑砂岩台阶） - ``` cut_red_sandstone_slab ``` （切制红砂岩台阶） - ``` smooth_red_sandstone_slab ``` （平滑红砂岩台阶） - ``` smooth_quartz_slab ``` （平滑石英台阶） - ``` mossy_cobblestone_slab ``` （苔石台阶） - ``` mossy_stone_brick_slab ``` （苔石砖台阶） - ``` granite_slab ``` （花岗岩台阶） - ``` polished_granite_slab ``` （磨制花岗岩台阶） - ``` diorite_slab ``` （闪长岩台阶） - ``` polished_diorite_slab ``` （磨制闪长岩台阶） - ``` andesite_slab ``` （安山岩台阶） - ``` polished_andesite_slab ``` （磨制安山岩台阶） - ``` red_nether_brick_slab ``` （红色下界砖台阶） - ``` blackstone_slab ``` （黑石台阶） - ``` polished_blackstone_slab ``` （磨制黑石台阶） - ``` polished_blackstone_brick_slab ``` （磨制黑石砖台阶） - ``` cut_copper_slab ``` （切制铜台阶） - ``` exposed_cut_copper_slab ``` （斑驳的切制铜台阶） - ``` weathered_cut_copper_slab ``` （锈蚀的切制铜台阶） - ``` oxidized_cut_copper_slab ``` （氧化的切制铜台阶） - ``` waxed_cut_copper_slab ``` （涂蜡的切制铜台阶） - ``` waxed_exposed_cut_copper_slab ``` （涂蜡的斑驳切制铜台阶） - ``` waxed_weathered_cut_copper_slab ``` （涂蜡的锈蚀切制铜台阶） - ``` waxed_oxidized_cut_copper_slab ``` （涂蜡的氧化切制铜台阶） - ``` cobbled_deepslate_slab ``` （深板岩圆石台阶） - ``` polished_deepslate_slab ``` （磨制深板岩台阶） - ``` deepslate_brick_slab ``` （深板岩砖台阶） - ``` deepslate_tile_slab ``` （深板岩瓦台阶） - ``` mud_brick_slab ``` （泥砖台阶） - ``` bamboo_mosaic_slab ``` （竹马赛克台阶） - ``` tuff_slab ``` （凝灰岩台阶） - ``` polished_tuff_slab ``` （磨制凝灰岩台阶） - ``` tuff_brick_slab ``` （凝灰岩砖台阶） - ``` resin_brick_slab ``` （树脂砖台阶） - ``` cinnabar_slab ``` （朱砂台阶） - ``` polished_cinnabar_slab ``` （磨制朱砂台阶） - ``` cinnabar_brick_slab ``` （朱砂砖台阶） - ``` sulfur_slab ``` （硫黄台阶） - ``` polished_sulfur_slab ``` （磨制硫黄台阶） - ``` sulfur_brick_slab ``` （硫黄砖台阶） - ``` #wool_slabs ``` - ``` #concrete_slabs ```

## small_flowers

- 被视为小型花的物品。

- #small_flowers（17项） - ``` dandelion ``` （蒲公英） - ``` open_eyeblossom ``` （张开的眼眸花） - ``` poppy ``` （虞美人） - ``` blue_orchid ``` （兰花） - ``` allium ``` （绒球葱） - ``` azure_bluet ``` （蓝花美耳草） - ``` red_tulip ``` （红色郁金香） - ``` orange_tulip ``` （橙色郁金香） - ``` white_tulip ``` （白色郁金香） - ``` pink_tulip ``` （粉红色郁金香） - ``` oxeye_daisy ``` （滨菊） - ``` cornflower ``` （矢车菊） - ``` lily_of_the_valley ``` （铃兰） - ``` wither_rose ``` （凋灵玫瑰） - ``` torchflower ``` （火把花） - ``` closed_eyeblossom ``` （闭合的眼眸花） - ``` golden_dandelion ``` （金蒲公英）

## smelts_to_glass

- 可以被烧炼成玻璃的物品。

- #smelts_to_glass（2项） - ``` sand ``` （沙子） - ``` red_sand ``` （红沙）

## sniffer_food

- 可以用于喂食嗅探兽的物品。

- #sniffer_food（1项） - ``` torchflower_seeds ``` （火把花种子）

## soul_fire_base_blocks

- 此标签中的物品可用于制造灵魂营火和灵魂火把，并将解锁配方书中的配方。

- #soul_fire_base_blocks（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## spears

- #spears（7项） - ``` diamond_spear ``` （钻石矛） - ``` stone_spear ``` （石矛） - ``` golden_spear ``` （金矛） - ``` netherite_spear ``` （下界合金矛） - ``` wooden_spear ``` （木矛） - ``` iron_spear ``` （铁矛） - ``` copper_spear ``` （铜矛）

## spruce_logs

- 用于 ``` spruce_planks.json ``` 进度和配方文件。

- #spruce_logs（4项） - ``` spruce_log ``` （云杉原木） - ``` spruce_wood ``` （云杉木） - ``` stripped_spruce_log ``` （去皮云杉原木） - ``` stripped_spruce_wood ``` （去皮云杉木）

## stairs

- 被视为楼梯的物品。

- #stairs（55项） - ``` #wooden_stairs ``` - ``` cobblestone_stairs ``` （圆石楼梯） - ``` sandstone_stairs ``` （砂岩楼梯） - ``` brick_stairs ``` （红砖楼梯） - ``` stone_brick_stairs ``` （石砖楼梯） - ``` nether_brick_stairs ``` （下界砖楼梯） - ``` quartz_stairs ``` （石英楼梯） - ``` red_sandstone_stairs ``` （红砂岩楼梯） - ``` prismarine_stairs ``` （海晶石楼梯） - ``` prismarine_brick_stairs ``` （海晶石砖楼梯） - ``` dark_prismarine_stairs ``` （暗海晶石楼梯） - ``` purpur_stairs ``` （紫珀楼梯） - ``` end_stone_brick_stairs ``` （末地石砖楼梯） - ``` stone_stairs ``` （石头楼梯） - ``` smooth_sandstone_stairs ``` （平滑砂岩楼梯） - ``` smooth_red_sandstone_stairs ``` （平滑红砂岩楼梯） - ``` smooth_quartz_stairs ``` （平滑石英楼梯） - ``` mossy_cobblestone_stairs ``` （苔石楼梯） - ``` mossy_stone_brick_stairs ``` （苔石砖楼梯） - ``` granite_stairs ``` （花岗岩楼梯） - ``` polished_granite_stairs ``` （磨制花岗岩楼梯） - ``` diorite_stairs ``` （闪长岩楼梯） - ``` polished_diorite_stairs ``` （磨制闪长岩楼梯） - ``` andesite_stairs ``` （安山岩楼梯） - ``` polished_andesite_stairs ``` （磨制安山岩楼梯） - ``` red_nether_brick_stairs ``` （红色下界砖楼梯） - ``` blackstone_stairs ``` （黑石楼梯） - ``` polished_blackstone_stairs ``` （磨制黑石楼梯） - ``` polished_blackstone_brick_stairs ``` （磨制黑石砖楼梯） - ``` cut_copper_stairs ``` （切制铜楼梯） - ``` exposed_cut_copper_stairs ``` （斑驳的切制铜楼梯） - ``` weathered_cut_copper_stairs ``` （锈蚀的切制铜楼梯） - ``` oxidized_cut_copper_stairs ``` （氧化的切制铜楼梯） - ``` waxed_cut_copper_stairs ``` （涂蜡的切制铜楼梯） - ``` waxed_exposed_cut_copper_stairs ``` （涂蜡的斑驳切制铜楼梯） - ``` waxed_weathered_cut_copper_stairs ``` （涂蜡的锈蚀切制铜楼梯） - ``` waxed_oxidized_cut_copper_stairs ``` （涂蜡的氧化切制铜楼梯） - ``` cobbled_deepslate_stairs ``` （深板岩圆石楼梯） - ``` polished_deepslate_stairs ``` （磨制深板岩楼梯） - ``` deepslate_brick_stairs ``` （深板岩砖楼梯） - ``` deepslate_tile_stairs ``` （深板岩瓦楼梯） - ``` mud_brick_stairs ``` （泥砖楼梯） - ``` bamboo_mosaic_stairs ``` （竹马赛克楼梯） - ``` tuff_stairs ``` （凝灰岩楼梯） - ``` polished_tuff_stairs ``` （磨制凝灰岩楼梯） - ``` tuff_brick_stairs ``` （凝灰岩砖楼梯） - ``` resin_brick_stairs ``` （树脂砖楼梯） - ``` cinnabar_stairs ``` （朱砂楼梯） - ``` polished_cinnabar_stairs ``` （磨制朱砂楼梯） - ``` cinnabar_brick_stairs ``` （朱砂砖楼梯） - ``` sulfur_stairs ``` （硫黄楼梯） - ``` polished_sulfur_stairs ``` （磨制硫黄楼梯） - ``` sulfur_brick_stairs ``` （硫黄砖楼梯） - ``` #wool_stairs ``` - ``` #concrete_stairs ```

## stone_bricks

- 用于解锁雕纹石砖、石砖台阶和石砖楼梯的合成配方。

- #stone_bricks（4项） - ``` stone_bricks ``` （石砖） - ``` mossy_stone_bricks ``` （苔石砖） - ``` cracked_stone_bricks ``` （裂纹石砖） - ``` chiseled_stone_bricks ``` （雕纹石砖）

## stone_buttons

- #stone_buttons（2项） - ``` stone_button ``` （石头按钮） - ``` polished_blackstone_button ``` （磨制黑石按钮）

## stone_crafting_materials

- 用于酿造台和熔炉的配方。

- #stone_crafting_materials（3项） - ``` cobblestone ``` （圆石） - ``` blackstone ``` （黑石） - ``` cobbled_deepslate ``` （深板岩圆石）

## stone_tool_materials

- 用于石器时代进度。
- 用于石质工具的合成配方和修复材料。

- #stone_tool_materials（3项） - ``` cobblestone ``` （圆石） - ``` blackstone ``` （黑石） - ``` cobbled_deepslate ``` （深板岩圆石）

## strider_food

- 可以用于喂食炽足兽的物品。

- #strider_food（1项） - ``` warped_fungus ``` （诡异菌）

## strider_tempt_items

- 可以用于引诱炽足兽的物品。

- #strider_tempt_items（2项） - ``` #strider_food ``` - ``` warped_fungus_on_a_stick ``` （诡异菌钓竿）

## sulfur_cube_archetype/bouncy

- 吸收这些物品的硫方怪的原型会被设置为弹性。

- #sulfur_cube_archetype/bouncy（4项） - ``` #planks ``` - ``` bamboo_mosaic ``` （竹马赛克） - ``` #logs ``` - ``` #bamboo_blocks ```

## sulfur_cube_archetype/explosive

- 吸收这些物品的硫方怪的原型会被设置为爆炸。

- #sulfur_cube_archetype/explosive（1项） - ``` tnt ``` （TNT）

## sulfur_cube_archetype/fast_flat

- 吸收这些物品的硫方怪的原型会被设置为快速平移。

- #sulfur_cube_archetype/fast_flat（25项） - ``` tube_coral_block ``` （管珊瑚块） - ``` brain_coral_block ``` （脑纹珊瑚块） - ``` bubble_coral_block ``` （气泡珊瑚块） - ``` fire_coral_block ``` （火珊瑚块） - ``` horn_coral_block ``` （鹿角珊瑚块） - ``` dead_tube_coral_block ``` （失活的管珊瑚块） - ``` dead_brain_coral_block ``` （失活的脑纹珊瑚块） - ``` dead_bubble_coral_block ``` （失活的气泡珊瑚块） - ``` dead_fire_coral_block ``` （失活的火珊瑚块） - ``` dead_horn_coral_block ``` （失活的鹿角珊瑚块） - ``` sponge ``` （海绵） - ``` wet_sponge ``` （湿海绵） - ``` dried_kelp_block ``` （干海带块） - ``` #moss_blocks ``` - ``` resin_block ``` （树脂块） - ``` resin_bricks ``` （树脂砖块） - ``` chiseled_resin_bricks ``` （雕纹树脂砖块） - ``` melon ``` （西瓜） - ``` hay_block ``` （干草捆） - ``` pumpkin ``` （南瓜） - ``` carved_pumpkin ``` （雕刻南瓜） - ``` jack_o_lantern ``` （南瓜灯） - ``` ochre_froglight ``` （赭黄蛙明灯） - ``` pearlescent_froglight ``` （珠光蛙明灯） - ``` verdant_froglight ``` （青翠蛙明灯）

## sulfur_cube_archetype/fast_sliding

- 吸收这些物品的硫方怪的原型会被设置为快速滑行。

- #sulfur_cube_archetype/fast_sliding（3项） - ``` blue_ice ``` （蓝冰） - ``` packed_ice ``` （浮冰） - ``` snow_block ``` （雪块）

## sulfur_cube_archetype/high_resistance

- 吸收这些物品的硫方怪的原型会被设置为高阻力。

- #sulfur_cube_archetype/high_resistance（2项） - ``` soul_sand ``` （灵魂沙） - ``` soul_soil ``` （灵魂土）

## sulfur_cube_archetype/hot

- 吸收这些物品的硫方怪的原型会被设置为高温。

- #sulfur_cube_archetype/hot（1项） - ``` magma_block ``` （岩浆块）

## sulfur_cube_archetype/light

- 吸收这些物品的硫方怪的原型会被设置为轻盈。

- #sulfur_cube_archetype/light（1项） - ``` #wool ```

## sulfur_cube_archetype/regular

- 吸收这些物品的硫方怪的原型会被设置为普通。

- #sulfur_cube_archetype/regular（12项） - ``` #concrete_powders ``` - ``` mud ``` （泥巴） - ``` muddy_mangrove_roots ``` （沾泥的红树根） - ``` packed_mud ``` （泥坯） - ``` coal_block ``` （煤炭块） - ``` dirt ``` （泥土） - ``` coarse_dirt ``` （砂土） - ``` rooted_dirt ``` （缠根泥土） - ``` podzol ``` （灰化土） - ``` grass_block ``` （草方块） - ``` clay ``` （黏土） - ``` bone_block ``` （骨块）

## sulfur_cube_archetype/slow_bouncy

- 吸收这些物品的硫方怪的原型会被设置为缓慢弹性。

- #sulfur_cube_archetype/slow_bouncy（94项） - ``` amethyst_block ``` （紫水晶块） - ``` andesite ``` （安山岩） - ``` basalt ``` （玄武岩） - ``` blackstone ``` （黑石） - ``` bricks ``` （红砖块） - ``` calcite ``` （方解石） - ``` chiseled_cinnabar ``` （雕纹朱砂） - ``` chiseled_deepslate ``` （雕纹深板岩） - ``` chiseled_nether_bricks ``` （雕纹下界砖块） - ``` chiseled_polished_blackstone ``` （雕纹磨制黑石） - ``` chiseled_quartz_block ``` （雕纹石英块） - ``` chiseled_red_sandstone ``` （雕纹红砂岩） - ``` chiseled_sandstone ``` （雕纹砂岩） - ``` chiseled_stone_bricks ``` （雕纹石砖） - ``` chiseled_sulfur ``` （雕纹硫黄） - ``` chiseled_tuff ``` （雕纹凝灰岩） - ``` chiseled_tuff_bricks ``` （雕纹凝灰岩砖） - ``` cinnabar ``` （朱砂） - ``` cinnabar_bricks ``` （朱砂砖） - ``` cobbled_deepslate ``` （深板岩圆石） - ``` cobblestone ``` （圆石） - ``` cracked_deepslate_bricks ``` （裂纹深板岩砖） - ``` cracked_deepslate_tiles ``` （裂纹深板岩瓦） - ``` cracked_nether_bricks ``` （裂纹下界砖块） - ``` cracked_polished_blackstone_bricks ``` （裂纹磨制黑石砖） - ``` cracked_stone_bricks ``` （裂纹石砖） - ``` crimson_nylium ``` （绯红菌岩） - ``` crying_obsidian ``` （哭泣的黑曜石） - ``` cut_red_sandstone ``` （切制红砂岩） - ``` cut_sandstone ``` （切制砂岩） - ``` dark_prismarine ``` （暗海晶石） - ``` deepslate ``` （深板岩） - ``` deepslate_bricks ``` （深板岩砖） - ``` deepslate_tiles ``` （深板岩瓦） - ``` diamond_block ``` （钻石块） - ``` diorite ``` （闪长岩） - ``` dripstone_block ``` （滴水石块） - ``` emerald_block ``` （绿宝石块） - ``` end_stone ``` （末地石） - ``` end_stone_bricks ``` （末地石砖） - ``` gilded_blackstone ``` （镶金黑石） - ``` glowstone ``` （荧石） - ``` granite ``` （花岗岩） - ``` lapis_block ``` （青金石块） - ``` mossy_cobblestone ``` （苔石） - ``` mossy_stone_bricks ``` （苔石砖） - ``` mud_bricks ``` （泥砖） - ``` nether_bricks ``` （下界砖块） - ``` netherrack ``` （下界岩） - ``` observer ``` （侦测器） - ``` obsidian ``` （黑曜石） - ``` polished_andesite ``` （磨制安山岩） - ``` polished_basalt ``` （磨制玄武岩） - ``` polished_blackstone ``` （磨制黑石） - ``` polished_blackstone_bricks ``` （磨制黑石砖） - ``` polished_cinnabar ``` （磨制朱砂） - ``` polished_deepslate ``` （磨制深板岩） - ``` polished_diorite ``` （磨制闪长岩） - ``` polished_granite ``` （磨制花岗岩） - ``` polished_sulfur ``` （磨制硫黄） - ``` polished_tuff ``` （磨制凝灰岩） - ``` prismarine ``` （海晶石） - ``` prismarine_bricks ``` （海晶石砖） - ``` purpur_block ``` （紫珀块） - ``` purpur_pillar ``` （紫珀柱） - ``` quartz_block ``` （石英块） - ``` quartz_bricks ``` （石英砖） - ``` nether_quartz_ore ``` （下界石英矿石） - ``` quartz_pillar ``` （石英柱） - ``` red_nether_bricks ``` （红色下界砖块） - ``` red_sandstone ``` （红砂岩） - ``` redstone_lamp ``` （红石灯） - ``` sandstone ``` （砂岩） - ``` sea_lantern ``` （海晶灯） - ``` smooth_basalt ``` （平滑玄武岩） - ``` smooth_quartz ``` （平滑石英块） - ``` smooth_red_sandstone ``` （平滑红砂岩） - ``` smooth_sandstone ``` （平滑砂岩） - ``` smooth_stone ``` （平滑石头） - ``` stone ``` （石头） - ``` stone_bricks ``` （石砖） - ``` sulfur ``` （硫黄） - ``` sulfur_bricks ``` （硫黄砖） - ``` tuff ``` （凝灰岩） - ``` tuff_bricks ``` （凝灰岩砖） - ``` warped_nylium ``` （诡异菌岩） - ``` #concrete ``` - ``` #coal_ores ``` - ``` #lapis_ores ``` - ``` #redstone_ores ``` - ``` #diamond_ores ``` - ``` #emerald_ores ``` - ``` #terracotta ``` - ``` #glazed_terracotta ```

## sulfur_cube_archetype/slow_flat

- 吸收这些物品的硫方怪的原型会被设置为缓慢平移。

- #sulfur_cube_archetype/slow_flat（42项） - ``` iron_block ``` （铁块） - ``` gold_block ``` （金块） - ``` raw_copper_block ``` （粗铜块） - ``` raw_gold_block ``` （粗金块） - ``` raw_iron_block ``` （粗铁块） - ``` #gold_ores ``` - ``` #iron_ores ``` - ``` #copper_ores ``` - ``` netherite_block ``` （下界合金块） - ``` ancient_debris ``` （远古残骸） - ``` copper_block ``` （铜块） - ``` exposed_copper ``` （斑驳的铜块） - ``` weathered_copper ``` （锈蚀的铜块） - ``` oxidized_copper ``` （氧化的铜块） - ``` waxed_copper_block ``` （涂蜡的铜块） - ``` waxed_exposed_copper ``` （涂蜡的斑驳铜块） - ``` waxed_weathered_copper ``` （涂蜡的锈蚀铜块） - ``` waxed_oxidized_copper ``` （涂蜡的氧化铜块） - ``` copper_bulb ``` （铜灯） - ``` exposed_copper_bulb ``` （斑驳的铜灯） - ``` weathered_copper_bulb ``` （锈蚀的铜灯） - ``` oxidized_copper_bulb ``` （氧化的铜灯） - ``` waxed_copper_bulb ``` （涂蜡的铜灯） - ``` waxed_exposed_copper_bulb ``` （涂蜡的斑驳铜灯） - ``` waxed_weathered_copper_bulb ``` （涂蜡的锈蚀铜灯） - ``` waxed_oxidized_copper_bulb ``` （涂蜡的氧化铜灯） - ``` cut_copper ``` （切制铜块） - ``` exposed_cut_copper ``` （斑驳的切制铜块） - ``` weathered_cut_copper ``` （锈蚀的切制铜块） - ``` oxidized_cut_copper ``` （氧化的切制铜块） - ``` waxed_cut_copper ``` （涂蜡的切制铜块） - ``` waxed_exposed_cut_copper ``` （涂蜡的斑驳切制铜块） - ``` waxed_weathered_cut_copper ``` （涂蜡的锈蚀切制铜块） - ``` waxed_oxidized_cut_copper ``` （涂蜡的氧化切制铜块） - ``` chiseled_copper ``` （雕纹铜块） - ``` exposed_chiseled_copper ``` （斑驳的雕纹铜块） - ``` weathered_chiseled_copper ``` （锈蚀的雕纹铜块） - ``` oxidized_chiseled_copper ``` （氧化的雕纹铜块） - ``` waxed_chiseled_copper ``` （涂蜡的雕纹铜块） - ``` waxed_exposed_chiseled_copper ``` （涂蜡的斑驳雕纹铜块） - ``` waxed_weathered_chiseled_copper ``` （涂蜡的锈蚀雕纹铜块） - ``` waxed_oxidized_chiseled_copper ``` （涂蜡的氧化雕纹铜块）

## sulfur_cube_archetype/slow_sliding

- 吸收这些物品的硫方怪的原型会被设置为缓慢滑行。

- #sulfur_cube_archetype/slow_sliding（6项） - ``` brown_mushroom_block ``` （棕色蘑菇方块） - ``` red_mushroom_block ``` （红色蘑菇方块） - ``` mushroom_stem ``` （蘑菇柄） - ``` mycelium ``` （菌丝体） - ``` #wart_blocks ``` - ``` shroomlight ``` （菌光体）

## sulfur_cube_archetype/sticky

- 吸收这些物品的硫方怪的原型会被设置为黏性。

- #sulfur_cube_archetype/sticky（1项） - ``` honeycomb_block ``` （蜜脾块）

## sulfur_cube_food

- 可以用于喂食小型硫方怪的物品。

- #sulfur_cube_food（1项） - ``` slime_ball ``` （黏液球）

## sulfur_cube_swallowable

- 可以放置在中型硫方怪内的物品。

- #sulfur_cube_swallowable（12项） - ``` #sulfur_cube_archetype/bouncy ``` - ``` #sulfur_cube_archetype/regular ``` - ``` #sulfur_cube_archetype/slow_flat ``` - ``` #sulfur_cube_archetype/fast_flat ``` - ``` #sulfur_cube_archetype/light ``` - ``` #sulfur_cube_archetype/fast_sliding ``` - ``` #sulfur_cube_archetype/slow_sliding ``` - ``` #sulfur_cube_archetype/sticky ``` - ``` #sulfur_cube_archetype/high_resistance ``` - ``` #sulfur_cube_archetype/explosive ``` - ``` #sulfur_cube_archetype/hot ``` - ``` #sulfur_cube_archetype/slow_bouncy ```

## swords

- #swords（7项） - ``` diamond_sword ``` （钻石剑） - ``` stone_sword ``` （石剑） - ``` golden_sword ``` （金剑） - ``` netherite_sword ``` （下界合金剑） - ``` wooden_sword ``` （木剑） - ``` iron_sword ``` （铁剑） - ``` copper_sword ``` （铜剑）

## terracotta

- #terracotta（17项） - ``` terracotta ``` （陶瓦） - ``` white_terracotta ``` （白色陶瓦） - ``` orange_terracotta ``` （橙色陶瓦） - ``` magenta_terracotta ``` （品红色陶瓦） - ``` light_blue_terracotta ``` （淡蓝色陶瓦） - ``` yellow_terracotta ``` （黄色陶瓦） - ``` lime_terracotta ``` （黄绿色陶瓦） - ``` pink_terracotta ``` （粉红色陶瓦） - ``` gray_terracotta ``` （灰色陶瓦） - ``` light_gray_terracotta ``` （淡灰色陶瓦） - ``` cyan_terracotta ``` （青色陶瓦） - ``` purple_terracotta ``` （紫色陶瓦） - ``` blue_terracotta ``` （蓝色陶瓦） - ``` brown_terracotta ``` （棕色陶瓦） - ``` green_terracotta ``` （绿色陶瓦） - ``` red_terracotta ``` （红色陶瓦） - ``` black_terracotta ``` （黑色陶瓦）

## trapdoors

- 被视为活板门的物品。

- #trapdoors（10项） - ``` #wooden_trapdoors ``` - ``` iron_trapdoor ``` （铁活板门） - ``` copper_trapdoor ``` （铜活板门） - ``` exposed_copper_trapdoor ``` （斑驳的铜活板门） - ``` weathered_copper_trapdoor ``` （锈蚀的铜活板门） - ``` oxidized_copper_trapdoor ``` （氧化的铜活板门） - ``` waxed_copper_trapdoor ``` （涂蜡的铜活板门） - ``` waxed_exposed_copper_trapdoor ``` （涂蜡的斑驳铜活板门） - ``` waxed_weathered_copper_trapdoor ``` （涂蜡的锈蚀铜活板门） - ``` waxed_oxidized_copper_trapdoor ``` （涂蜡的氧化铜活板门）

## trim_materials

- 可用于在锻造台中作为附加盔甲纹饰的材料。

- #trim_materials（11项） - ``` amethyst_shard ``` （紫水晶碎片） - ``` copper_ingot ``` （铜锭） - ``` diamond ``` （钻石） - ``` emerald ``` （绿宝石） - ``` gold_ingot ``` （金锭） - ``` iron_ingot ``` （铁锭） - ``` lapis_lazuli ``` （青金石） - ``` netherite_ingot ``` （下界合金锭） - ``` quartz ``` （下界石英） - ``` redstone ``` （红石粉） - ``` resin_brick ``` （树脂砖）

## trimmable_armor

- #trimmable_armor（4项） - ``` #foot_armor ``` - ``` #leg_armor ``` - ``` #chest_armor ``` - ``` #head_armor ```

## turtle_food

- 可以用于喂食海龟的物品。

- #turtle_food（1项） - ``` seagrass ``` （海草）

## villager_picks_up

- 会吸引村民捡起的物品。

- #villager_picks_up（4项） - ``` #villager_plantable_seeds ``` - ``` bread ``` （面包） - ``` wheat ``` （小麦） - ``` beetroot ``` （甜菜根）

## villager_plantable_seeds

- 可被村民种植的物品。

- #villager_plantable_seeds（6项） - ``` wheat_seeds ``` （小麦种子） - ``` potato ``` （马铃薯） - ``` carrot ``` （胡萝卜） - ``` beetroot_seeds ``` （甜菜种子） - ``` torchflower_seeds ``` （火把花种子） - ``` pitcher_pod ``` （瓶子草荚果）

## walls

- 被视为墙的物品。

- #walls（32项） - ``` cobblestone_wall ``` （圆石墙） - ``` mossy_cobblestone_wall ``` （苔石墙） - ``` brick_wall ``` （红砖墙） - ``` prismarine_wall ``` （海晶石墙） - ``` red_sandstone_wall ``` （红砂岩墙） - ``` mossy_stone_brick_wall ``` （苔石砖墙） - ``` granite_wall ``` （花岗岩墙） - ``` stone_brick_wall ``` （石砖墙） - ``` nether_brick_wall ``` （下界砖墙） - ``` andesite_wall ``` （安山岩墙） - ``` red_nether_brick_wall ``` （红色下界砖墙） - ``` sandstone_wall ``` （砂岩墙） - ``` end_stone_brick_wall ``` （末地石砖墙） - ``` diorite_wall ``` （闪长岩墙） - ``` blackstone_wall ``` （黑石墙） - ``` polished_blackstone_brick_wall ``` （磨制黑石砖墙） - ``` polished_blackstone_wall ``` （磨制黑石墙） - ``` cobbled_deepslate_wall ``` （深板岩圆石墙） - ``` polished_deepslate_wall ``` （磨制深板岩墙） - ``` deepslate_tile_wall ``` （深板岩瓦墙） - ``` deepslate_brick_wall ``` （深板岩砖墙） - ``` mud_brick_wall ``` （泥砖墙） - ``` tuff_wall ``` （凝灰岩墙） - ``` polished_tuff_wall ``` （磨制凝灰岩墙） - ``` tuff_brick_wall ``` （凝灰岩砖墙） - ``` resin_brick_wall ``` （树脂砖墙） - ``` cinnabar_wall ``` （朱砂墙） - ``` polished_cinnabar_wall ``` （磨制朱砂墙） - ``` cinnabar_brick_wall ``` （朱砂砖墙） - ``` sulfur_wall ``` （硫黄墙） - ``` polished_sulfur_wall ``` （磨制硫黄墙） - ``` sulfur_brick_wall ``` （硫黄砖墙）

## warped_stems

- 用于 ``` warped_planks.json ``` 进度和配方文件。

- #warped_stems（4项） - ``` warped_stem ``` （诡异菌柄） - ``` stripped_warped_stem ``` （去皮诡异菌柄） - ``` warped_hyphae ``` （诡异菌核） - ``` stripped_warped_hyphae ``` （去皮诡异菌核）

## wart_blocks

- #wart_blocks（2项） - ``` nether_wart_block ``` （下界疣块） - ``` warped_wart_block ``` （诡异疣块）

## wither_skeleton_disliked_weapons

- 凋灵骷髅不想拾取的物品。

- #wither_skeleton_disliked_weapons（2项） - ``` bow ``` （弓） - ``` crossbow ``` （弩）

## wolf_collar_dyes

- 用于给狼的项圈染色的物品，设置的颜色取自物品的 ``` minecraft:dye ``` 组件。

- #wolf_collar_dyes（1项） - ``` #dyes ```

## wolf_food

- 可以用于喂食狼的物品。

- #wolf_food（8项） - ``` #meat ``` - ``` cod ``` （生鳕鱼） - ``` cooked_cod ``` （熟鳕鱼） - ``` salmon ``` （生鲑鱼） - ``` cooked_salmon ``` （熟鲑鱼） - ``` tropical_fish ``` （热带鱼） - ``` pufferfish ``` （河豚） - ``` rabbit_stew ``` （兔肉煲）

## wooden_buttons

- 被视为木按钮的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加100刻的燃烧时间。

- #wooden_buttons（13项） - ``` oak_button ``` （橡木按钮） - ``` spruce_button ``` （云杉木按钮） - ``` birch_button ``` （白桦木按钮） - ``` jungle_button ``` （丛林木按钮） - ``` acacia_button ``` （金合欢木按钮） - ``` dark_oak_button ``` （深色橡木按钮） - ``` pale_oak_button ``` （苍白橡木按钮） - ``` crimson_button ``` （绯红木按钮） - ``` warped_button ``` （诡异木按钮） - ``` mangrove_button ``` （红树木按钮） - ``` bamboo_button ``` （竹按钮） - ``` cherry_button ``` （樱花木按钮） - ``` poplar_button ``` （杨木按钮）

## wooden_doors

- 被视为木门的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加200刻的燃烧时间。

- #wooden_doors（13项） - ``` oak_door ``` （橡木门） - ``` spruce_door ``` （云杉木门） - ``` birch_door ``` （白桦木门） - ``` jungle_door ``` （丛林木门） - ``` acacia_door ``` （金合欢木门） - ``` dark_oak_door ``` （深色橡木门） - ``` pale_oak_door ``` （苍白橡木门） - ``` crimson_door ``` （绯红木门） - ``` warped_door ``` （诡异木门） - ``` mangrove_door ``` （红树木门） - ``` bamboo_door ``` （竹门） - ``` cherry_door ``` （樱花木门） - ``` poplar_door ``` （杨木门）

## wooden_fences

- 被视为木栅栏的物品。

- #wooden_fences（13项） - ``` oak_fence ``` （橡木栅栏） - ``` acacia_fence ``` （金合欢木栅栏） - ``` dark_oak_fence ``` （深色橡木栅栏） - ``` pale_oak_fence ``` （苍白橡木栅栏） - ``` spruce_fence ``` （云杉木栅栏） - ``` birch_fence ``` （白桦木栅栏） - ``` jungle_fence ``` （丛林木栅栏） - ``` crimson_fence ``` （绯红木栅栏） - ``` warped_fence ``` （诡异木栅栏） - ``` mangrove_fence ``` （红树木栅栏） - ``` bamboo_fence ``` （竹栅栏） - ``` cherry_fence ``` （樱花木栅栏） - ``` poplar_fence ``` （杨木栅栏）

## wooden_pressure_plates

- 被视为木压力板的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #wooden_pressure_plates（13项） - ``` oak_pressure_plate ``` （橡木压力板） - ``` spruce_pressure_plate ``` （云杉木压力板） - ``` birch_pressure_plate ``` （白桦木压力板） - ``` jungle_pressure_plate ``` （丛林木压力板） - ``` acacia_pressure_plate ``` （金合欢木压力板） - ``` dark_oak_pressure_plate ``` （深色橡木压力板） - ``` pale_oak_pressure_plate ``` （苍白橡木压力板） - ``` crimson_pressure_plate ``` （绯红木压力板） - ``` warped_pressure_plate ``` （诡异木压力板） - ``` mangrove_pressure_plate ``` （红树木压力板） - ``` bamboo_pressure_plate ``` （竹压力板） - ``` cherry_pressure_plate ``` （樱花木压力板） - ``` poplar_pressure_plate ``` （杨木压力板）

## wooden_shelves

- 被视为展示架的物品。

- #wooden_shelves（13项） - ``` acacia_shelf ``` （金合欢木展示架） - ``` bamboo_shelf ``` （竹展示架） - ``` birch_shelf ``` （白桦木展示架） - ``` cherry_shelf ``` （樱花木展示架） - ``` crimson_shelf ``` （绯红木展示架） - ``` dark_oak_shelf ``` （深色橡木展示架） - ``` jungle_shelf ``` （丛林木展示架） - ``` mangrove_shelf ``` （红树木展示架） - ``` oak_shelf ``` （橡木展示架） - ``` pale_oak_shelf ``` （苍白橡木展示架） - ``` spruce_shelf ``` （云杉木展示架） - ``` warped_shelf ``` （诡异木展示架） - ``` poplar_shelf ``` （杨木展示架）

## wooden_slabs

- 被视为木台阶的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加150刻的燃烧时间。
- 用于阳光探测器、堆肥桶、雕纹书架和讲台的配方。

- #wooden_slabs（13项） - ``` oak_slab ``` （橡木台阶） - ``` spruce_slab ``` （云杉木台阶） - ``` birch_slab ``` （白桦木台阶） - ``` jungle_slab ``` （丛林木台阶） - ``` acacia_slab ``` （金合欢木台阶） - ``` dark_oak_slab ``` （深色橡木台阶） - ``` pale_oak_slab ``` （苍白橡木台阶） - ``` crimson_slab ``` （绯红木台阶） - ``` warped_slab ``` （诡异木台阶） - ``` mangrove_slab ``` （红树木台阶） - ``` bamboo_slab ``` （竹台阶） - ``` cherry_slab ``` （樱花木台阶） - ``` poplar_slab ``` （杨木台阶）

## wooden_stairs

- 被视为木楼梯的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #wooden_stairs（13项） - ``` oak_stairs ``` （橡木楼梯） - ``` spruce_stairs ``` （云杉木楼梯） - ``` birch_stairs ``` （白桦木楼梯） - ``` jungle_stairs ``` （丛林木楼梯） - ``` acacia_stairs ``` （金合欢木楼梯） - ``` dark_oak_stairs ``` （深色橡木楼梯） - ``` pale_oak_stairs ``` （苍白橡木楼梯） - ``` crimson_stairs ``` （绯红木楼梯） - ``` warped_stairs ``` （诡异木楼梯） - ``` mangrove_stairs ``` （红树木楼梯） - ``` bamboo_stairs ``` （竹楼梯） - ``` cherry_stairs ``` （樱花木楼梯） - ``` poplar_stairs ``` （杨木楼梯）

## wooden_tool_materials

- 用于木质工具和盾牌的合成配方和修复材料。

- #wooden_tool_materials（1项） - ``` #planks ```

## wooden_trapdoors

- 被视为木活板门的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加300刻的燃烧时间。

- #wooden_trapdoors（13项） - ``` acacia_trapdoor ``` （金合欢木活板门） - ``` birch_trapdoor ``` （白桦木活板门） - ``` dark_oak_trapdoor ``` （深色橡木活板门） - ``` pale_oak_trapdoor ``` （苍白橡木活板门） - ``` jungle_trapdoor ``` （丛林木活板门） - ``` oak_trapdoor ``` （橡木活板门） - ``` spruce_trapdoor ``` （云杉木活板门） - ``` crimson_trapdoor ``` （绯红木活板门） - ``` warped_trapdoor ``` （诡异木活板门） - ``` mangrove_trapdoor ``` （红树木活板门） - ``` bamboo_trapdoor ``` （竹活板门） - ``` cherry_trapdoor ``` （樱花木活板门） - ``` poplar_trapdoor ``` （杨木活板门）

## wool

- 被视为羊毛的物品。
- 用于检查一个物品是否能进入熔炉的燃料槽并增加100刻的燃烧时间。
- 用于画的配方和配方解锁。

- #wool（16项） - ``` white_wool ``` （白色羊毛） - ``` orange_wool ``` （橙色羊毛） - ``` magenta_wool ``` （品红色羊毛） - ``` light_blue_wool ``` （淡蓝色羊毛） - ``` yellow_wool ``` （黄色羊毛） - ``` lime_wool ``` （黄绿色羊毛） - ``` pink_wool ``` （粉红色羊毛） - ``` gray_wool ``` （灰色羊毛） - ``` light_gray_wool ``` （淡灰色羊毛） - ``` cyan_wool ``` （青色羊毛） - ``` purple_wool ``` （紫色羊毛） - ``` blue_wool ``` （蓝色羊毛） - ``` brown_wool ``` （棕色羊毛） - ``` green_wool ``` （绿色羊毛） - ``` red_wool ``` （红色羊毛） - ``` black_wool ``` （黑色羊毛）

## wool_carpets

- 被视为地毯的物品。
- 用于检查物品是否能放入熔炉的燃料槽，并重置燃烧时间67。

- #wool_carpets（16项） - ``` white_carpet ``` （白色地毯） - ``` orange_carpet ``` （橙色地毯） - ``` magenta_carpet ``` （品红色地毯） - ``` light_blue_carpet ``` （淡蓝色地毯） - ``` yellow_carpet ``` （黄色地毯） - ``` lime_carpet ``` （黄绿色地毯） - ``` pink_carpet ``` （粉红色地毯） - ``` gray_carpet ``` （灰色地毯） - ``` light_gray_carpet ``` （淡灰色地毯） - ``` cyan_carpet ``` （青色地毯） - ``` purple_carpet ``` （紫色地毯） - ``` blue_carpet ``` （蓝色地毯） - ``` brown_carpet ``` （棕色地毯） - ``` green_carpet ``` （绿色地毯） - ``` red_carpet ``` （红色地毯） - ``` black_carpet ``` （黑色地毯）

## wool_stairs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 被视为羊毛楼梯的物品。

- #wool_stairs（16项） - ``` white_wool_stairs ``` （白色羊毛楼梯） - ``` orange_wool_stairs ``` （橙色羊毛楼梯） - ``` magenta_wool_stairs ``` （品红色羊毛楼梯） - ``` light_blue_wool_stairs ``` （淡蓝色羊毛楼梯） - ``` yellow_wool_stairs ``` （黄色羊毛楼梯） - ``` lime_wool_stairs ``` （黄绿色羊毛楼梯） - ``` pink_wool_stairs ``` （粉红色羊毛楼梯） - ``` gray_wool_stairs ``` （灰色羊毛楼梯） - ``` light_gray_wool_stairs ``` （淡灰色羊毛楼梯） - ``` cyan_wool_stairs ``` （青色羊毛楼梯） - ``` purple_wool_stairs ``` （紫色羊毛楼梯） - ``` blue_wool_stairs ``` （蓝色羊毛楼梯） - ``` brown_wool_stairs ``` （棕色羊毛楼梯） - ``` green_wool_stairs ``` （绿色羊毛楼梯） - ``` red_wool_stairs ``` （红色羊毛楼梯） - ``` black_wool_stairs ``` （黑色羊毛楼梯）

## wool_slabs

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- 被视为羊毛台阶的物品。

- #wool_slabs（16项） - ``` white_wool_slab ``` （白色羊毛台阶） - ``` orange_wool_slab ``` （橙色羊毛台阶） - ``` magenta_wool_slab ``` （品红色羊毛台阶） - ``` light_blue_wool_slab ``` （淡蓝色羊毛台阶） - ``` yellow_wool_slab ``` （黄色羊毛台阶） - ``` lime_wool_slab ``` （黄绿色羊毛台阶） - ``` pink_wool_slab ``` （粉红色羊毛台阶） - ``` gray_wool_slab ``` （灰色羊毛台阶） - ``` light_gray_wool_slab ``` （淡灰色羊毛台阶） - ``` cyan_wool_slab ``` （青色羊毛台阶） - ``` purple_wool_slab ``` （紫色羊毛台阶） - ``` blue_wool_slab ``` （蓝色羊毛台阶） - ``` brown_wool_slab ``` （棕色羊毛台阶） - ``` green_wool_slab ``` （绿色羊毛台阶） - ``` red_wool_slab ``` （红色羊毛台阶） - ``` black_wool_slab ``` （黑色羊毛台阶）

## zombie_horse_food

- 可以用于喂食僵尸马的物品。

- #zombie_horse_food（1项） - ``` red_mushroom ``` （红色蘑菇）

# 已移除的标签

## coral_blocks

添加于：18w16a。移除于：1.13-pre8。

- #coral_blocks（2项） - ``` dead_coral_blocks ``` - ``` live_coral_blocks ```

## coral_fans

添加于：18w10a。移除于：1.13-pre8。

- #coral_fans（5项） - ``` tube_coral_fan ``` - ``` brain_coral_fan ``` - ``` bubble_coral_fan ``` - ``` fire_coral_fan ``` - ``` horn_coral_fan ```

## corals

添加于：18w09a。移除于：1.13-pre8。

- #corals（5项） - ``` tube_coral ``` - ``` brain_coral ``` - ``` bubble_coral ``` - ``` fire_coral ``` - ``` horn_coral ```

## dead_coral_blocks

添加于：18w16a。移除于：1.13-pre8。

- #dead_coral_blocks（5项） - ``` dead_tube_coral_block ``` - ``` dead_brain_coral_block ``` - ``` dead_bubble_coral_block ``` - ``` dead_fire_coral_block ``` - ``` dead_horn_coral_block ```

## enchantable/sword

- 可以附上适用于剑的魔咒的物品。
- 被 ``` #enchantable/sweeping ``` 和 ``` #enchantable/melee_weapon ``` 替代。

- #enchantable/sword（1项） - ``` #swords ```

添加于：24w03a。移除于：25w41a。

## furnace_materials

- 被 ``` #stone_crafting_materials ``` 替代。

添加于：20w15a。移除于：20w28a。

- #furnace_materials（2项） - ``` cobblestone ``` - ``` blackstone ```

## live_coral_blocks

添加于：18w14b。移除于：1.13-pre8。

- #live_coral_blocks（5项） - ``` tube_coral_block ``` - ``` brain_coral_block ``` - ``` bubble_coral_block ``` - ``` fire_coral_block ``` - ``` horn_coral_block ```

## music_discs

曾用于判断物品是否是音乐唱片，因
```
jukebox_playable
```

组件的加入而不再需要。

添加于：18w43a。移除于：24w21a。

- #music_discs（8项） - ``` #creeper_drop_music_discs ``` - ``` music_disc_pigstep ``` - ``` music_disc_otherside ``` - ``` music_disc_5 ``` - ``` music_disc_relic ``` - ``` music_disc_creator ``` - ``` music_disc_creator_music_box ``` - ``` music_disc_precipice ```

## overworld_natural_logs

- 目前依然存在同名的方块标签。

添加于：22w17a。移除于：22w45a。

- #overworld_natural_logs（7项） - ``` acacia_log ``` - ``` birch_log ``` - ``` oak_log ``` - ``` jungle_log ``` - ``` spruce_log ``` - ``` dark_oak_log ``` - ``` mangrove_log ```

## stripped_logs

添加于：22w42a。移除于：22w46a。

- #stripped_logs（9项） - ``` stripped_oak_log ``` - ``` stripped_spruce_log ``` - ``` stripped_birch_log ``` - ``` stripped_jungle_log ``` - ``` stripped_acacia_log ``` - ``` stripped_dark_oak_log ``` - ``` stripped_crimson_stem ``` - ``` stripped_warped_stem ``` - ``` stripped_mangrove_log ```

## tall_flowers

添加于：19w34a。移除于：24w45a。

- #tall_flowers（5项） - ``` sunflower ``` - ``` lilac ``` - ``` peony ``` - ``` rose_bush ``` - ``` pitcher_plant ```

## tools

添加于：23w07a。移除于：1.20.5-pre1。

- #tools（6项） - ``` #swords ``` - ``` #axes ``` - ``` #pickaxes ``` - ``` #shovels ``` - ``` #hoes ``` - ``` trident ```

## trim_templates

添加于：23w04a。移除于：24w46a。

- #trim_templates（18项） - ``` ward_armor_trim_smithing_template ``` - ``` spire_armor_trim_smithing_template ``` - ``` coast_armor_trim_smithing_template ``` - ``` eye_armor_trim_smithing_template ``` - ``` dune_armor_trim_smithing_template ``` - ``` wild_armor_trim_smithing_template ``` - ``` rib_armor_trim_smithing_template ``` - ``` tide_armor_trim_smithing_template ``` - ``` sentry_armor_trim_smithing_template ``` - ``` vex_armor_trim_smithing_template ``` - ``` snout_armor_trim_smithing_template ``` - ``` wayfinder_armor_trim_smithing_template ``` - ``` shaper_armor_trim_smithing_template ``` - ``` silence_armor_trim_smithing_template ``` - ``` raiser_armor_trim_smithing_template ``` - ``` host_armor_trim_smithing_template ``` - ``` flow_armor_trim_smithing_template ``` - ``` bolt_armor_trim_smithing_template ```

# 历史

# 导航

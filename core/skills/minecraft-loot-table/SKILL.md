---
name: minecraft-loot-table
description: |
  战利品表（Minecraft Wiki 中文版全量正文）。
  
  【概述】本文章仅介绍Java版战利品表。
  
  【涵盖内容】
  - 原版调用
  - 自定义调用
  - 随机池
  - 抽取项
  - 单一抽取项
  - 复合抽取项
  - 特殊抽取项
  - 物品修饰器
  - 战利品表谓词
  
  【关键定义】
  - 注册表：LOOT_TABLE
  - 数据包路径：data/minecraft/loot_table、data/charged_creeper/root、data/chests/trial_chambers/reward
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 战利品表 的完整规范时
---

本文章仅介绍Java版战利品表。
基岩版战利品表请参见官方文档。

战利品表（Loot Table）用于决定游戏在何种情况下生成何种物品。

# 用途

## 原版调用

原版游戏本身就使用了许多战利品表来决定游戏行为。例如自然生成的容器内容物、可疑的方块内容物、破坏方块时的掉落物、杀死实体时的掉落物、钓鱼时可以钓上的物品和猪灵的以物易物。它不会影响经验的掉落和不掉落物品的实体，比如大型史莱姆产生的史莱姆和虫蚀方块中的蠹虫。

在游戏本体
```
client.jar
```

内，战利品表文件全部位于
```
data/minecraft/loot_table
```

目录下。下面为游戏本体内战利品表文件的目录及其作用：

[图:File directory.png：Minecraft中directory的精灵图] 
```
archaeology
```

：从可疑的方块中刷出的物品。

- - desert_pyramid - desert_well - ocean_ruin_cold - ocean_ruin_warm - trail_ruins_common - trail_ruins_rare

[图:File directory.png：Minecraft中directory的精灵图] 
```
blocks
```

：方块被破坏后的掉落物。

- - <方块ID>：对应方块的掉落物。

[图:File directory.png：Minecraft中directory的精灵图] 
```
brush
```

：使用刷子后得到的物品。

- - armadillo

[图:File directory.png：Minecraft中directory的精灵图] 
```
carve
```

：雕刻后得到的物品。

- - pumkin

[图:File directory.png：Minecraft中directory的精灵图] 
```
charged_creeper
```

：闪电苦力怕击杀生物后的掉落物。

- - creeper - piglin - root：闪电苦力怕击杀生物后，死亡生物额外掉落的物品。 - skeleton - wither_skeleton - zombie

[图:File directory.png：Minecraft中directory的精灵图] 
```
chests
```

：不同结构中的战利品容器中的物品。

- - abandoned_mineshaft：废弃矿井中的运输矿车。 - ancient_city：远古城市中的宝箱。 - ancient_city_ice_box：远古城市中冰窖的宝箱。 - bastion_bridge：堡垒遗迹桥梁上的箱子。 - bastion_hoglin_stable：堡垒遗迹疣猪兽棚中的箱子。 - bastion_other：堡垒遗迹中其他位置的箱子。 - bastion_treasure：堡垒遗迹宝藏室中的箱子。 - buried_treasure：埋藏的宝藏。 - desert_pyramid：沙漠神殿的宝藏室里的箱子。 - end_city_treasure：末地城里的箱子。 - igloo_chest：雪屋地下室里的箱子。 - jungle_temple：丛林神庙里的箱子。 - jungle_temple_dispenser：丛林神庙的发射器。 - nether_bridge：下界要塞里的箱子。 - pillager_outpost：掠夺者前哨站的箱子。 - ruined_portal：废弃传送门的箱子 - shipwreck_map：沉船的地图箱。 - shipwreck_supply：沉船的补给箱。 - shipwreck_treasure：沉船的宝箱。 - simple_dungeon：刷怪房里的箱子。 - spawn_bonus_chest：如果打开奖励箱选项的话，新世界生成时的奖励箱。 - stronghold_corridor：要塞台阶祭坛里的箱子。 - stronghold_crossing：要塞储存室里的箱子。 - stronghold_library：要塞图书馆里的箱子。 - trial_chambers - corridor - entrance - intersection - intersection_barrel - reward - reward_common - reward_ominous - reward_ominous_common - reward_ominous_rare - reward_ominous_unique - reward_rare - reward_unique - supply - underwater_ruin_big：海底废墟的大型建筑物的箱子。 - underwater_ruin_small：海底废墟的小型建筑物的箱子。 - village：村庄中的箱子。 - village_armorer：盔甲匠箱子。 - village_butcher：屠夫箱子。 - village_cartographer：制图师箱子。 - village_desert_house：沙漠房屋箱子。 - village_fisher：渔夫箱子。 - village_fletcher：制箭师箱子。 - village_mason：石匠箱子。 - village_plains_house：平原房屋箱子。 - village_savanna_house：热带草原房屋箱子。 - village_shepherd：牧羊人箱子。 - village_snowy_house：积雪房屋箱子。 - village_taiga_house：针叶林房屋箱子。 - village_tannery：皮匠箱子。 - village_temple：牧师箱子。 - village_toolsmith：工具匠箱子。 - village_weaponsmith：武器匠箱子。 - woodland_mansion：林地府邸的箱子。

[图:File directory.png：Minecraft中directory的精灵图] 
```
dispensers
```

：试炼密室的发射器中的物品。

- - trial_chambers - chamber - corridor - water

[图:File directory.png：Minecraft中directory的精灵图] 
```
entities
```

：生物被杀死后掉落的物品。

- - <实体ID>：对应生物的死亡掉落物。 - sheep：不同颜色的羊毛掉落。 - black - blue - brown - cyan - gray - green - light_blue - light_gray - lime - magenta - orange - pink - purple - red - white - yellow

[图:File directory.png：Minecraft中directory的精灵图] 
```
equipment
```

：试炼密室结构中试炼刷怪笼生成的生物所带有的装备。

- - trial_chamber - trial_chamber_melee - trial_chamber_ranged

[图:File directory.png：Minecraft中directory的精灵图] 
```
gameplay
```

：各种游戏玩法的物品。

- - armadillo_shed - cat_morning_gift：猫在与玩家睡觉后第二天给予的物品。 - chicken_lay - fishing：钓鱼时可能得到的物品。 - fish：钓鱼时可能得到的鱼，同时被守卫者和远古守卫者继承。 - junk：钓鱼时可能得到的垃圾。 - treasure：钓鱼时可能得到的宝藏。 - fishing：钓鱼战利品的主表，在fishing目录中抽取战利品表。 - hero_of_the_village：不同职业村民给予具有村庄英雄状态效果玩家的物品。 - armorer_gift - baby_gift - butcher_gift - cartographer_gift - cleric_gift - farmer_gift - fisherman_gift - fletcher_gift - leatherworker_gift - librarian_gift - mason_gift - shepherd_gift - toolsmith_gift - unemployed_gift - weaponsmith_gift - panda_sneeze - piglin_bartering：与猪灵以物易物可能得到的物品。 - sniffer_digging - turtle_grow

[图:File directory.png：Minecraft中directory的精灵图] 
```
pots
```

：试炼密室的饰纹陶罐中的物品。

- - trial_chambers - corridor

[图:File directory.png：Minecraft中directory的精灵图] 
```
harvest
```

：从方块收获的物品。

- - beehive - cave_vine - sweet_berry_bush

[图:File directory.png：Minecraft中directory的精灵图] 
```
shearing
```

：使用剪刀与某些实体交互时掉落的物品。

- - bogged - mooshroom：不同变种的蘑菇掉落。 - brown - red - mooshroom - sheep：不同颜色的羊毛掉落。 - black - blue - brown - cyan - gray - green - light_blue - light_gray - lime - magenta - orange - pink - purple - red - white - yellow - sheep - snow_golem

[图:File directory.png：Minecraft中directory的精灵图] 
```
spawners
```

：试炼刷怪笼所生成的战胜奖励。

- - ominous - trial_chamber - consumables - key - trial_chamber - consumables - items_to_drop_when_ominous - key

注意：

- 生存模式中不可破坏的方块，比如基岩、末地传送门，没有战利品表。
- 一些方块会共享战利品表，主要是方块的墙和地板变种，例如白色旗帜和墙上的白色旗帜均使用白色旗帜的战利品表。
- 凋灵掉落的下界之星不由战利品表控制。
- 生物被闪电苦力怕击杀时，会从战利品表 ``` charged_creeper/root ``` 额外抽取一次物品。如果闪电苦力怕单次击杀了多个生物，则只有一个生物会抽取。

## 自定义调用

生物和方块可通过NBT标签添加战利品表。可对其添加一个[图:字符串]标签，表示所引用的战利品表文件位置。还可能允许添加一个[图:长整型]标签，表示引用的战利品表所使用的战利品表种子。战利品表并不决定容器生成物的所在槽位，槽位是基于战利品表种子随机排布的。指定了相同种子和战利品表的生物或方块会有相同的物品生成模式。

对于箱子、陷阱箱等战利品容器和运输船、运输矿车、漏斗矿车、饰纹陶罐和可疑的方块而言：

- [图:NBT复合标签/JSON对象] 根标签。 - [图:字符串]LootTable：（命名空间ID）表示一个战利品表。若某容器应用了此标签，在它被打开后，或者被某物品交互后，游戏会尝试使用对应的战利品表进行物品装填。对于大型箱子，则仅带有此标签的半箱会单独受到影响。 - [图:长整型]LootTableSeed：战利品表种子，用于战利品表的生成。其工作模式类似于生成世界的种子。此项为空或者是0时则使用存档的随机序列。

一旦容器内容物发生了互动（如打开箱子或破坏箱子等），这些标签会被移除，也只有此时，战利品才会出现在容器中。

对于试炼刷怪笼而言：

- [图:NBT复合标签/JSON对象] 根标签。 - [图:NBT复合标签/JSON对象]normal_config：正常变种的试炼刷怪笼的设置数据。 - [图:字符串]items_to_drop_when_ominous：控制不祥变种的试炼刷怪笼激活状态时随机在周围生成的不祥之物生成器实体内的物品的战利品表。 - [图:NBT列表/JSON数组]loot_tables_to_eject：在试炼刷怪笼生成的所有生物被杀死后，决定喷出物品的战利品表。生成战利品与加入试炼玩家数有关。 - [图:NBT复合标签/JSON对象]：一项战利品项。 - [图:字符串]data：（命名空间ID）战利品表。 - [图:整型]weight：（大于0）相对其他项的选中此项的权重。 - [图:NBT复合标签/JSON对象]ominous_config：不祥变种的试炼刷怪笼的设置数据。格式与正常变种相同。

对于宝库而言：

- [图:NBT复合标签/JSON对象] 根标签。 - [图:NBT复合标签/JSON对象]config：宝库的配置数据。 - [图:字符串]loot_table：（默认为 ``` chests/trial_chambers/reward ``` ）宝库使用的战利品表的命名空间ID。 - [图:字符串]override_loot_table_to_display：覆盖奖励战利品表，设置用于展示物品的战利品表。

对于生物而言：

- [图:NBT复合标签/JSON对象] 根标签。 - [图:字符串]DeathLootTable：（命名空间ID）决定生物死亡时掉落物的战利品表。 - [图:长整型]DeathLootTableSeed：生成战利品表的种子，类似于生成世界的种子。此项为空或者是0时将使用随机序列。

刷怪笼和试炼刷怪笼可以用战利品表指定生物生成时带有的装备：

- - [图:NBT复合标签/JSON对象]spawn_data：下一次生成生物的数据。 - [图:NBT复合标签/JSON对象]equipment：设置生物生成时带有的物品。 - [图:字符串]loot_table：（命名空间ID）使用战利品表获得物品，装备到生成生物身上。

进度达成后的奖励可以指定战利品表，将在进度达成后给予玩家物品。

命令
```
/
loot
```

可以直接调用战利品表获取物品。既可以调用现有的战利品表，也可以以SNBT格式定义新的战利品表。

# 定义格式

战利品表在游戏中使用
```
LOOT_TABLE
```

注册表，数据包路径为
```
loot_table
```

，即所有战利品表定义文件都需要在
```
data/<
命名空间
>/loot_table
```

目录下定义。

战利品表定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]type：（默认为 ``` generic ``` ）游戏验证此战利品表的战利品上下文参数集。游戏会对此战利品表及调用的所有物品修饰器、谓词和数值提供器进行验证，如果缺失必要的上下文参数，则游戏日志中会输出警告信息。 - [图:字符串]random_sequence：该战利品表生成战利品时使用的随机序列。如果只有一个战利品表使用一个特定的随机序列，生成的随机物品组的顺序对于每个使用相同种子的世界来说是相同的。如果多个战利品表使用同一个随机序列，那么它们生成的任何战利品都依赖于其他战利品表的执行次数和顺序进行改变。 - [图:NBT列表/JSON数组]functions：应用在此战利品表生成的每个物品堆叠上的物品修饰器。此列表中的修饰器按顺序应用。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个物品修饰器。 - [图:NBT列表/JSON数组]pools：此战利品表的随机池列表，按照顺序抽取。 - [图:NBT复合标签/JSON对象]：一个随机池。

## 随机池

战利品随机池（Loot Pool）主要定义了若干待选的抽取项。每次抽取是独立的。

- [图:NBT复合标签/JSON对象] 战利品表随机池 - [图:整型][图:NBT复合标签/JSON对象]*rolls：指定该随机池的基础抽取次数。 - - 数值提供器，见战利品表/数值提供器 - [图:单精度浮点数][图:NBT复合标签/JSON对象]bonus_rolls：（默认为0）根据战利品上下文提供的幸运值增加抽取次数。游戏会将玩家幸运值属性的值和钓鱼时工具上fishing_luck_bonus魔咒效果的等级相加后，与此字段的值相乘并向下取整，作为额外的抽取次数。 - - 数值提供器，见战利品表/数值提供器 - [图:NBT列表/JSON数组]conditions：一个战利品表谓词列表。仅当满足列表中的所有条件时，该随机池才会被使用。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个战利品表谓词。 - [图:NBT列表/JSON数组]functions：一个物品修饰器列表，应用到本池生成的每个物品堆叠上。列表中的物品修饰器按顺序应用。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个物品修饰器。 - [图:NBT列表/JSON数组]*entries：定义随机池中的抽取项。每次抽取时，某个战利品项会以带权重的随机抽取的方式，从该池的抽取项中抽出，每次抽取是独立的，也即“有放回的抽取”。注意，并非直接根据权重抽取此列表中的元素，而是在展开所有复合抽取项、排除不符合其条件的单一抽取项后，再进行带权重的抽取。 - [图:NBT复合标签/JSON对象]：一个战利品表抽取项。

注：[图:单精度浮点数][图:NBT复合标签/JSON对象]bonus_rolls所需的幸运值依赖于战利品上下文，玩家幸运值属性只在玩家打开战利品容器方块、打开战利品容器实体、解锁宝库、钓鱼、击杀生物和扫刷可疑的方块时生效，魔咒效果
```
fishing_luck_bonus
```

只在钓鱼时生效。

## 抽取项

战利品池抽取项（Loot Pool Entry）决定了抽取物品的行为，其分为单一抽取项（Singleton Entry）和复合抽取项（Composite Entry）。

抽取项格式如下：

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type：抽取项类型。 - 依抽取项类型而定的附加字段。

### 单一抽取项

单一抽取项定义了单个物品生成行为，是随机池中最终要抽取的带权重的项目。

- [图:NBT复合标签/JSON对象] 单一抽取项共通字段

- - [图:NBT列表/JSON数组]functions：要对生成的物品堆叠应用物品修饰器。此列表中的修饰器按顺序应用。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个物品修饰器。 - 见物品修饰器。 - [图:整型]weight：（默认为1）决定了这个单一抽取项被抽取的权重。 - [图:整型]quality：（默认为0）若战利品上下文提供了幸运值，则据此修改物品堆被抽取的权重。经过修改的权重为max(⌊b+ql⌋,0)，其中b为[图:整型]weight的值，q为此字段的值，l为玩家幸运值属性的值和钓鱼时工具上fishing_luck_bonus魔咒效果的等级之和。此字段的幸运值生效条件与额外抽取次数[图:单精度浮点数][图:NBT复合标签/JSON对象]bonus_rolls的生效条件相同。 - [图:NBT列表/JSON数组]conditions：此单一抽取项的条件。仅当同时满足该列表中的所有谓词时，该单一抽取项才会包含在抽取池中。若有任一谓词不满足，则在进行抽取前从抽取池中剔除此单一抽取项。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个战利品表谓词。

#### item

生成单一物品堆叠。物品数量默认为1。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` item ``` - - 单一抽取项共通字段 - [图:字符串]*name：物品的命名空间ID。

#### loot_table

从另一个战利品表生成物品堆叠。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` loot_table ``` - - 单一抽取项共通字段 - [图:NBT复合标签/JSON对象][图:字符串]*value：将要调用的战利品表。不论是直接调用还是内联定义均不允许循环引用。

#### dynamic

生成的物品堆叠根据当前在破坏的方块决定。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` dynamic ``` - - 单一抽取项共通字段 - [图:字符串]*name：可以为 ``` sherds ``` （仅用于饰纹陶罐，掉落4个对应陶片）和 ``` contents ``` （仅用于潜影盒，使内容物掉落至世界而不是包含在物品中）。

#### empty

什么都不生成。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` empty ``` - - 单一抽取项共通字段

#### slots

从某个物品槽位中生成物品堆叠。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` slots ``` - - 单一抽取项共通字段 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*slot_source：槽位源，指定物品来源的槽位。 - 见槽位源。

### 复合抽取项

复合抽取项不是要抽取的项目，不会直接放入随机池中，而是展开为零个、一个或多个抽取项，即根据条件选取零个、一个或多个抽取项。被选取的抽取项如果是复合抽取项，还会再进行进一步的展开。直到展开结果全部为单一抽取项后，将这些单一抽取项放入随机池中。

所有的复合抽取项都被展开后，随机池中只包含单一抽取项。单一抽取项可具有条件（[图:NBT列表/JSON数组]conditions字段），如不满足条件，则此时会从随机池中将其剔除。剔除不满足条件的单一抽取项后，随机池中只包含满足条件的单一抽取项。每个单一抽取项都有权重（由[图:整型]weight和[图:整型]quality字段定义），游戏根据权重在此时的随机池中随机抽取一项，得到本次的抽取结果。

- [图:NBT复合标签/JSON对象] 复合抽取项共通字段

- - [图:NBT列表/JSON数组]children：子抽取项列表。 - [图:NBT复合标签/JSON对象]：一个战利品表抽取项。单一抽取项、复合抽取项均可。 - [图:NBT列表/JSON数组]conditions：此复合抽取项的条件。仅当同时满足该列表中的所有谓词时，此复合抽取项才会进行展开。若有任一谓词不满足，此复合抽取项会被直接忽略。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个战利品表谓词。

#### alternatives

若满足指定条件，从列表中选择第一个满足条件的子项。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` alternatives ``` - - 复合抽取项共通字段

#### group

若满足指定条件，选取所有子项。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` group ``` - - 复合抽取项共通字段

#### sequence

若满足指定条件，从列表开头开始，逐一选择子项，直到有一个子项不满足条件为止。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` sequence ``` - - 复合抽取项共通字段

### 特殊抽取项

#### tag

若[图:布尔型]expand为
```
false
```

，是单一抽取项：若抽取到此项，对指定物品标签中每个物品生成一个物品堆叠。物品数量默认为1。

若[图:布尔型]expand为
```
true
```

，是复合抽取项：展开为权重相同（均为指定的权重）的多个单一抽取项，物品标签中每个物品作为一个单一抽取项，物品数量为1，每一项类似于单一抽取项
```
item
```

，但无法使用物品修饰器。

- [图:NBT复合标签/JSON对象] 战利品表抽取项 - [图:字符串]type： ``` tag ``` - - 单一抽取项共通字段 - [图:布尔型]*expand：决定是否作为复合抽取项展开。 - [图:字符串]*name：一个物品标签。

## 物品修饰器

主条目：物品修饰器
战利品表使用物品修饰器来修改物品。参考物品修饰器以了解所有可用的修饰器。

## 战利品表谓词

主条目：谓词
战利品表使用了诸多判断条件来判断是否应用随机池等元素。参考谓词以了解所有可能的条件。

# 战利品上下文

主条目：战利品上下文
当游戏生成战利品时，会创建一个“战利品上下文”来存储当前用于生成战利品的信息，并将此上下文传入战利品表进行计算。战利品上下文内包含各种参数，以供战利品表谓词和物品修饰器使用。

战利品表文件内指定的战利品上下文只用于验证战利品表是否出现参数错误，不用于游戏真正生成战利品时的计算。

# 历史

# 参考

1. ↑ MC-149589
1. ↑ MC-184348
1. ↑ MC-120523
1. ↑ MC-262347
1. ↑ MC-110336
1. ↑ MC-212671 — 漏洞状态为“已修复”。

# 外部链接

- Loot Table Generator on misode.github.io，一个战利品表生成器。

# 导航

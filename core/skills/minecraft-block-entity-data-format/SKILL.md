---
name: minecraft-block-entity-data-format
description: |
  方块实体数据格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于基岩版中的方块实体格式，请见“基岩版存档格式/方块实体格式”。
  
  【涵盖内容】
  - 方块实体数据列表
  
  【关键定义】
  - 数据包路径：data/spawners/trial_chamber/items_to_drop_when_ominous、data/spawners/trial_chamber/consumables、data/spawners/trial_chamber/key、data/chests/trial_chambers/reward
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 方块实体数据格式 的完整规范时
---

关于基岩版中的方块实体格式，请见“基岩版存档格式/方块实体格式”。

本条目所述内容仅适用于Java版。
方块实体是对方块状态有穷集合的补充，扩展了方块的行为。

# 数据格式

所有方块实体都有一部分相同的数据格式，以保存方块实体的最基础的信息：

- [图:NBT复合标签/JSON对象] 根标签 - [图:整型]* *x：当前方块实体的X坐标。 - [图:整型]* *y：当前方块实体的Y坐标。 - [图:整型]* *z：当前方块实体的Z坐标。 - [图:字符串]* *id：（命名空间ID）方块实体的类型。 - [图:NBT复合标签/JSON对象]components：方块实体的数据组件信息。当使用此方块实体对应的物品放置此方块实体时，物品额外持有的且不会被继承序列化处理的数据组件会被复制存储入此标签内。 - [图:任意类型]<数据组件ID>：一项数据组件和其对应的数据。

关于各方块实体对数据组件的继承序列化处理，详见数据组件 § 方块实体。

## 方块实体数据列表

各种不同的方块实体在这个数据格式的基础上，附加了自身额外的信息。下列是Java版中所有方块实体的数据格式：

下面为Java版中所有的方块实体。

旗帜

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）表示旗帜的自定义名称。旗帜被破坏后所产生的掉落物将保留该名称。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT列表/JSON数组]patterns：（默认为空列表）按照顺序的旗帜图案列表。此项方块实体数据会被视为数据组件banner_patterns。 - [图:NBT复合标签/JSON对象]：一个单独的旗帜图案。 - [图:字符串]* *color：图案的染料颜色。 - [图:字符串][图:NBT复合标签/JSON对象]* *pattern：图案的命名空间ID或详细数据。 - - 旗帜图案，见Template:Nbt inherit/banner pattern/source

木桶

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前木桶的名称，会取代默认名称出现在木桶的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，木桶只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前木桶内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。木桶共有27个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定木桶第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

信标

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前信标的名称，会取代默认名称出现在信标的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:整型]*Levels：（无法通过 ``` / data ``` 修改）表示金字塔的可用等级。 - [图:NBT复合标签/JSON对象]lock：如果存在，信标只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:字符串]primary_effect：选定的主效果的命名空间ID。 - [图:字符串]secondary_effect：选定的辅助效果的命名空间ID。

床

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

蜂箱

- [图:NBT复合标签/JSON对象] 方块实体数据 - [图:NBT列表/JSON数组]* *bees：巢内目前存在的蜜蜂信息。此项方块实体数据会被视为数据组件bees。 - [图:NBT复合标签/JSON对象]：一只蜜蜂的数据。 - [图:NBT复合标签/JSON对象]entity_data：蜜蜂的部分实体数据。如果保存的实体数据不是带有 ``` #beehive_inhabitors ``` 的实体（默认为蜜蜂），则尝试放出此实体时实体不会被生成，其数据会被删除。 - [图:字符串]* *id：实体类型。 - 见实体数据格式。下列标签不会被保存，也不会被加载：[图:短整型]Air、[图:NBT复合标签/JSON对象]drop_chances、[图:NBT复合标签/JSON对象]equipment、[图:NBT复合标签/JSON对象]Brain、[图:布尔型]CanPickUpLoot、[图:短整型]DeathTime、[图:单精度浮点数]fall_distance、[图:布尔型]FallFlying、[图:短整型]Fire、[图:整型]HurtByTimestamp、[图:短整型]HurtTime、[图:布尔型]LeftHanded、[图:NBT列表/JSON数组]Motion、[图:布尔型]NoGravity、[图:布尔型]OnGround、[图:整型]PortalCooldown、[图:NBT列表/JSON数组]Pos、[图:NBT列表/JSON数组]Rotation、[图:整型数组]sleeping_pos、[图:整型]CannotEnterHiveTicks、[图:整型]TicksSincePollination、[图:整型]CropsGrownSincePollination、[图:整型数组]hive_pos、[图:NBT列表/JSON数组]Passengers、[图:整型数组][图:NBT复合标签/JSON对象]leash、[图:整型数组]UUID。 - [图:整型]* *min_ticks_in_hive：蜜蜂会在巢内滞留的最短时间。 - [图:整型]* *ticks_in_hive：蜜蜂在巢内已滞留的时间。 - [图:整型数组]flower_pos：储存花的位置，以便其他蜜蜂能够找到。内部的三个整数分别代表了位置的XYZ坐标值。

钟

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

高炉

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前高炉的名称，会取代默认名称出现在高炉的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，高炉只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:短整型]*cooking_time_spent[图:整型]*cooking_time_spent：（默认为0）烧炼物已被烧炼的时间。当该值等于[图:短整型]cooking_total_time[图:整型]cooking_total_time时，本次烧炼完成，此值重置为0。若[图:短整型]lit_time_remaining[图:整型]lit_time_remaining为0，此值每游戏刻减少2。若此值大于[图:短整型]cooking_total_time，则无法完成烧炼。 - [图:短整型]*cooking_total_time[图:整型]*cooking_total_time：（默认为0）烧炼物完成烧炼所需时间。 - [图:NBT列表/JSON数组]* *Items：当前高炉内物品的列表，超出槽位范围的物品无效。槽位0存放烧炼物数据；槽位1存放燃料数据；槽位2存放烧炼成品数据。 - [图:NBT复合标签/JSON对象]：物品数据。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:短整型]*lit_time_remaining[图:整型]*lit_time_remaining：（默认为0）当前使用的燃料剩余的燃烧时间。 - [图:短整型]*lit_total_time[图:整型]*lit_total_time：（默认为0）高炉应燃烧的总时长。 - [图:单精度浮点数]*speed_multiplier：（默认为1.0）该熔炉正在燃烧的燃料的烧炼速度乘数。 - [图:NBT复合标签/JSON对象]RecipesUsed：高炉从最后一次玩家取出成品到现在已烧炼的配方数，用于计算经验值。 - [图:整型]<配方的命名空间ID>：此配方烧炼完成的次数。

酿造台

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前酿造台的名称，会取代默认名称出现在酿造台的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，酿造台只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:短整型]* *BrewTime：酿造药水的剩余时间。当此值不为0时每游戏刻减1，直至为0时酿造完成。 - [图:字节型]* *Fuel：酿造台的剩余能量。每开始一次酿造减1。当此值小于0时才可以消耗燃料（烈焰粉），并将此值重置为20。 - [图:NBT列表/JSON数组]* *Items：当前酿造台内物品的列表，超出槽位范围的物品无效。槽位0代表左边的药水槽；槽位1代表中间的药水槽；槽位2代表右边的药水槽；槽位3代表酿造物品槽；槽位4代表燃料槽。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source

可疑的沙子

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型]hit_direction：（不能导出和保存，仅可以加载或使用 ``` / data ``` 修改，0≤值≤5）清刷的方向，决定物品渲染的位置。从0到5分别对应下上北南西东，如果超过值域则会报错。 - [图:NBT复合标签/JSON对象]item：（当[图:字符串]LootTable不存在时存在并有效）可疑的方块内含有的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:字符串]LootTable：决定可疑的方块第一次被清刷时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。

校频幽匿感测体

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型]* *last_vibration_frequency：上次触发校频幽匿感测体的游戏事件的振动频率，用于记录模拟信号输出。 - [图:NBT复合标签/JSON对象]*listener：振动监听器的数据。 - - 振动监听器，见Template:Nbt inherit/vibration listener/source

营火

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型数组]CookingTimes：每个物品已被烹饪多长时间。此标签一共有4个元素，第一个索引为槽位0，以此类推。 - [图:整型数组]CookingTotalTimes：每个物品需要被烹饪的时间。此标签一共有4个元素，第一个索引为槽位0，以此类推。 - [图:NBT列表/JSON数组]* *Items：正在烹饪的物品。营火一共有4个槽位，超出槽位范围的物品无效。 - - 物品共通标签，见Template:Nbt inherit/item/source

箱子

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前箱子的名称，会取代默认名称出现在箱子的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，箱子只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前箱子内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。箱子共有27个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定箱子第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

雕纹书架

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT列表/JSON数组]* *Items：雕纹书架内物品的列表，超出槽位范围的物品无效。雕纹书架共有6个槽位，从左上角起，按从左到右，从上到下的顺序进行编号。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:整型]* *last_interacted_slot：（-1≤值≤5）最后一次交互的槽位编号。若雕纹书架从未使用过则为-1。

命令方块

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:布尔型]* *auto：表示此命令方块是否保持开启。 - [图:字符串]* *Command：命令方块中的命令。 - [图:布尔型]* *conditionMet：表示受条件制约的命令方块是否满足条件。如果此命令方块不受制约，此值为true。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件，默认为“@”）表示命令方块的自定义名称。此项方块实体数据会被视为数据组件custom_name。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]LastOutput：（文本组件，当[图:布尔型]*TrackOutput为true时存在并有效）上一条命令的输出。游戏规则“广播命令方块输出”（ ``` command_block_output ``` ）为false时依旧会储存。 - [图:长整型]LastExecution：（当[图:布尔型]*UpdateLastExecution为true时存在并有效）上一条命令执行的时间戳。 - [图:布尔型]* *powered：表示命令方块是否已被激活。 - [图:整型]* *SuccessCount：命令执行的成功次数，影响用红石比较器输出的模拟信号强度。只在命令方块矿车用激活铁轨激活后更新。 - [图:布尔型]*TrackOutput：表示是否储存上一条命令的输出，在GUI中点击"上一个输出"文本框旁的按钮进行开关。按钮上的标志指示出目前的状态：O为true，X为false。当此项不存在时游戏默认为 ``` true ``` 。 - [图:布尔型]*UpdateLastExecution：表示是否储存上一条命令执行的时间戳。当此项不存在时游戏默认为 ``` true ``` 。

红石比较器

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型]* *OutputSignal：表示此红石比较器的模拟信号输出强度。

潮涌核心

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型数组]Target：潮涌核心目前正在攻击的生物的UUID。

铜傀儡像

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

铜傀儡像使用数据组件保存将要生成的铜傀儡的自定义名称。

- [图:NBT复合标签/JSON对象]components：方块实体的数据组件信息。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]minecraft:custom_name：（文本组件）自定义名称。

合成器

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前合成器的名称，会取代默认名称出现在合成器的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，合成器只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前合成器内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。合成器共有9个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定合成器第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。 - [图:整型]* *crafting_ticks_remaining：合成器取消合成状态倒计时。当合成器成功合成物品后，此值被设置为6游戏刻（0.3秒），并将方块属性 ``` crafting ``` 设置为true。当此值降低为0时， ``` crafting ``` 设置为false。 - [图:整型数组]* *disabled_slots：合成器内禁用的槽位，槽位编号与存放物品列表内的槽位编号顺序相同。 - [图:整型]* *triggered：表示合成器是否被红石信号激活，与方块属性 ``` triggered ``` 同步。当此值为1时代表true，其他值都代表false。

嘎枝之心

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型数组]creaking：绑定的嘎枝的UUID。

阳光探测器

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

饰纹陶罐

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]item：（当[图:字符串]LootTable不存在时存在并有效）饰纹陶罐存储的物品。此项方块实体数据会被视为数据组件container。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:字符串]LootTable：决定饰纹陶罐被破坏时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。 - [图:NBT列表/JSON数组]sherds：饰纹陶罐各个面的陶片样式，4个面按照后左右前排列。如果此项不存在则全部默认为红砖。此项方块实体数据会被视为数据组件pot_decorations。 - [图:字符串]：陶片的命名空间ID。如果此面没有陶片样式，则此值为 ``` minecraft:brick ``` （红砖）。 - [图:NBT复合标签/JSON对象]sherds：饰纹陶罐各个面的陶片样式。如果对应面的物品不存在provides_pottery_pattern组件，则此面没有额外样式。此项方块实体数据会被视为数据组件pot_decorations。 - [图:字符串][图:NBT复合标签/JSON对象]back：背面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]left：左面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]right：右面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]front：正面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source

发射器

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前发射器的名称，会取代默认名称出现在发射器的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，发射器只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前发射器内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。发射器共有9个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定发射器第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

投掷器

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前投掷器的名称，会取代默认名称出现在投掷器的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，投掷器只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前投掷器内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。投掷器共有9个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定投掷器第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

附魔台

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）表示当前附魔台的名称。会取代附魔台界面中的默认名称。此项方块实体数据会被视为数据组件custom_name。

末地折跃门

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:长整型]* *Age：末地折跃门方块的年龄，用于控制光柱的产生。当低于200游戏刻（10秒）时，代表此时折跃门刚刚生成，它会发出一束品红色光柱；当此值可以被2400游戏刻（120秒）整除时，折跃门会产生40游戏刻（2秒）传送冷却，并发出一束紫色光柱。 - [图:布尔型]ExactTeleport：表示是否把实体准确传送到[图:整型数组]exit_portal指定的坐标而不是传送到这个坐标附近的位置。 - [图:整型数组]exit_portal：当进入末地折跃门方块要把实体传送到的位置。内部的三个整数分别代表了位置的XYZ坐标值。

末地传送门

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

末影箱

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source

熔炉

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前熔炉的名称，会取代默认名称出现在熔炉的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，熔炉只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:短整型]*cooking_time_spent[图:整型]*cooking_time_spent：（默认为0）烧炼物已被烧炼的时间。当该值等于[图:短整型]cooking_total_time[图:整型]cooking_total_time时，本次烧炼完成，此值重置为0。若[图:短整型]lit_time_remaining[图:整型]lit_time_remaining为0，此值每游戏刻减少2。若此值大于[图:短整型]cooking_total_time，则无法完成烧炼。 - [图:短整型]*cooking_total_time[图:整型]*cooking_total_time：（默认为0）烧炼物完成烧炼所需时间。 - [图:NBT列表/JSON数组]* *Items：当前熔炉内物品的列表，超出槽位范围的物品无效。槽位0存放烧炼物数据；槽位1存放燃料数据；槽位2存放烧炼成品数据。 - [图:NBT复合标签/JSON对象]：物品数据。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:短整型]*lit_time_remaining[图:整型]*lit_time_remaining：（默认为0）当前使用的燃料剩余的燃烧时间。 - [图:短整型]*lit_total_time[图:整型]*lit_total_time：（默认为0）熔炉应燃烧的总时长。 - [图:单精度浮点数]*speed_multiplier：（默认为1.0）该熔炉正在燃烧的燃料的烧炼速度乘数。 - [图:NBT复合标签/JSON对象]RecipesUsed：熔炉从最后一次玩家取出成品到现在已烧炼的配方数，用于计算经验值。 - [图:整型]<配方的命名空间ID>：此配方烧炼完成的次数。

悬挂式告示牌

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]back_text：告示牌背面的文字信息。 - [图:字符串]*color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]*has_glowing_text：表示文字是否发光。 - [图:NBT列表/JSON数组]* *messages：告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:NBT复合标签/JSON对象]front_text：告示牌正面的文字信息。 - [图:字符串]*color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]*has_glowing_text：表示文字是否发光。 - [图:NBT列表/JSON数组]* *messages：告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]* *is_waxed：表示告示牌是否被涂蜡。涂蜡后告示牌的文字不能被修改，但允许告示牌文本中的命令执行。

漏斗

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前漏斗的名称，会取代默认名称出现在漏斗的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，漏斗只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前漏斗内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。漏斗共有5个槽位，从左到右进行编号。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定漏斗第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。 - [图:整型]* *TransferCooldown：（默认为-1）传输物品的冷却时间。此值为0时物品会被传输，并将此值设置为8游戏刻（0.4秒）。

拼图方块

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串]* *name：（默认为 ``` minecraft:empty ``` ）拼图方块的名称。 - [图:字符串]* *final_state：（默认为 ``` minecraft:air ``` ）这个拼图方块将变成的方块。 - [图:字符串]* *joint：拼接类型，只能是 ``` rollable ``` （可旋转）和 ``` aligned ``` （固定）。 - [图:整型]* *placement_priority：放置优先级。当放置拼图方块所对应的结构时，系统以放置优先级从大到小的顺序依次放置各个结构。如果两个结构具有相同的放置优先级，则以默认顺序放置。 - [图:字符串]* *pool：（默认为 ``` minecraft:empty ``` ）拼图方块的目标池，用于从中选择结构。 - [图:字符串]* *target：（默认为 ``` minecraft:empty ``` ）当结构从目标池中生成时要对接的拼图方块名称。 - [图:整型]* *selection_priority：选择优先级。当父级结构生成时，决定子级拼图方块的选择次序，按选择优先级从大到小排序依次选择。如果两个拼图方块具有相同的选择优先级，则以随机顺序选择。

唱片机

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]RecordItem：唱片机内的音乐唱片。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:长整型]ticks_since_song_started：音乐唱片已经播放的时间，以游戏刻为单位。如果此值不存在则唱片机当前没有播放音乐唱片。

讲台

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]Book：讲台上的书。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:整型]Page：讲台上的书目前翻开的页数，从0开始。如果设置值小于0则重置为0，超过书的页数范围则重置为书的最后一页。如果讲台上没有书则此项不存在。

刷怪笼

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - - 刷怪笼共通标签，见Template:Nbt inherit/spawner/source

移动的活塞

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象]* *blockState：所代表的被移动的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:布尔型]* *extending：表示移动的活塞是否是由推出的活塞移动而被创建的。 - [图:整型]* *facing：（0≤值≤5）创建移动的活塞的活塞的方向。从0到5分别对应下上北南西东，如果超过值域则对6取余并取绝对值后对应方向。 - [图:单精度浮点数]* *progress：（0≤值≤1）方块已经移动的进度。如果设置值超过1则重置为1，并到位。 - [图:布尔型]* *source：表示移动的活塞是否为引发移动的活塞或活塞头。

幽匿催发体

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT列表/JSON数组]* *cursors：包含储存蔓延信号的列表。 - [图:NBT复合标签/JSON对象]：一个信号。 - [图:整型]*charge：（0≤值≤1000）该信号拥有的能量。此值不存在或无效时游戏默认为0。 - [图:整型]*decay_delay：（0或1）与延迟无关，信号经过了幽匿块或幽匿脉络后为1，否则为0。为1时，信号可以自由蔓延；为0时，若蔓延至非幽匿类方块，则信号中的所有能量丢失。此值不存在或无效时默认为1。 - [图:整型数组]* *pos：信号目前所在的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:整型]*update_delay：（值≥0）距离下一次蔓延的时间。当方块刚刚被转化时为1游戏刻（0.05秒），否则为0。此值不存在或无效时默认为0。 - [图:NBT列表/JSON数组]facings：如果目前要转化的方块是空气或水，信号会尝试把这个方块转化为幽匿脉络，并储存幽匿脉络所有的面。如果要转化的方块不是空气或水，或者此列表为空时，信号会尝试向毗邻方块蔓延幽匿脉络。 - [图:字符串]：一个方向。可以为 ``` north ``` 、​ ``` south ``` 、​ ``` east ``` 、​ ``` west ``` 、​ ``` up ``` 和​ ``` down ``` 。

幽匿感测体

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:整型]* *last_vibration_frequency：上次触发幽匿感测体的游戏事件的振动频率，用于记录模拟信号输出。 - [图:NBT复合标签/JSON对象]*listener：振动监听器的数据。 - - 振动监听器，见Template:Nbt inherit/vibration listener/source

幽匿尖啸体

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]*listener：振动监听器的数据。 - - 振动监听器，见Template:Nbt inherit/vibration listener/source - [图:整型]*warning_level：警告等级。如果幽匿尖啸体在上一次收到信号后没有被成功激活，此值为0；如果上一次被成功激活，则设置为激活幽匿尖啸体的玩家的警告等级。此项不存在时游戏默认为0。

展示架

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:布尔型]*align_items_to_bottom：（默认为 ``` false ``` ）展示架中的物品是否在底部隔板上。若为 ``` true ``` ，物品高度取决于物品模型渲染变换 ``` on_shelf ``` 中自底部隔板向上的偏移高度；若为 ``` false ``` ，则物品高度居中。 - [图:NBT列表/JSON数组]* *Items：展示架内物品的列表，超出槽位范围的物品无效。展示架共有3个槽位，按从左到右的顺序进行编号。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source

潜影盒

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前潜影盒的名称，会取代默认名称出现在潜影盒的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，潜影盒只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前潜影盒内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。潜影盒共有27个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定潜影盒第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

告示牌

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]back_text：告示牌背面的文字信息。 - [图:字符串]*color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]*has_glowing_text：表示文字是否发光。 - [图:NBT列表/JSON数组]* *messages：告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:NBT复合标签/JSON对象]front_text：告示牌正面的文字信息。 - [图:字符串]*color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]*has_glowing_text：表示文字是否发光。 - [图:NBT列表/JSON数组]* *messages：告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌内的一行文字。 - [图:布尔型]* *is_waxed：表示告示牌是否被涂蜡。涂蜡后告示牌的文字不能被修改，但允许告示牌文本中的命令执行。

头颅

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]custom_name：（文本组件）表示该头颅的自定义名称，也表示其被破坏后所掉落的物品的自定义名称。此项方块实体数据会被视为数据组件custom_name。 - [图:字符串]note_block_sound：玩家的头放置在音符盒上时，敲击音符盒会发出的音效的命名空间ID。此项方块实体数据会被视为数据组件note_block_sound。 - [图:字符串][图:NBT复合标签/JSON对象]profile：玩家的头对应的玩家游戏档案，用于渲染玩家的头。字符串形式只用于加载不用于存储，在游戏读取后会直接转换为对应的玩家档案。此项方块实体数据会被视为数据组件profile。 - - 游戏档案，见Template:Nbt inherit/resolvable profile/source

游戏档案属性通常包括
```
textures
```

用于保存玩家的皮肤数据。在此属性的数据被Base64解码后具有如下结构：

- [图:NBT复合标签/JSON对象] JSON数据根元素 - [图:字符串]*profileId：游戏档案的UUID，不带连字符。 - [图:字符串]*profileName：游戏档案名称。 - [图:布尔型]signatureRequired：代表此纹理属性是否已被签名。如果[图:字符串]signature存在，则此项也存在并为true。 - [图:NBT复合标签/JSON对象]*textures：纹理数据。 - [图:NBT复合标签/JSON对象]CAPE：披风纹理。如果此游戏档案不包含披风，此项不存在。 - [图:字符串]*url：披风纹理的URL链接。 - [图:NBT复合标签/JSON对象]SKIN：皮肤纹理。如果此游戏档案不包含自定义皮肤，此项不存在。 - [图:NBT复合标签/JSON对象]metadata：皮肤的元数据。 - [图:字符串]model：固定值 ``` slim ``` 。当皮肤模型手臂为3像素时存在，否则不存在。 - [图:字符串]*url：皮肤纹理的URL链接。 - [图:整型]*timestamp：Unix时间戳，以毫秒为单位，时间为请求玩家游戏档案数据的时间。

烟熏炉

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前烟熏炉的名称，会取代默认名称出现在烟熏炉的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，烟熏炉只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:短整型]*cooking_time_spent[图:整型]*cooking_time_spent：（默认为0）烧炼物已被烧炼的时间。当该值等于[图:短整型]cooking_total_time[图:整型]cooking_total_time时，本次烧炼完成，此值重置为0。若[图:短整型]lit_time_remaining[图:整型]lit_time_remaining为0，此值每游戏刻减少2。若此值大于[图:短整型]cooking_total_time，则无法完成烧炼。 - [图:短整型]*cooking_total_time[图:整型]*cooking_total_time：（默认为0）烧炼物完成烧炼所需时间。 - [图:NBT列表/JSON数组]* *Items：当前烟熏炉内物品的列表，超出槽位范围的物品无效。槽位0存放烧炼物数据；槽位1存放燃料数据；槽位2存放烧炼成品数据。 - [图:NBT复合标签/JSON对象]：物品数据。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:短整型]*lit_time_remaining[图:整型]*lit_time_remaining：（默认为0）当前使用的燃料剩余的燃烧时间。 - [图:短整型]*lit_total_time[图:整型]*lit_total_time：（默认为0）烟熏炉应燃烧的总时长。 - [图:单精度浮点数]*speed_multiplier：（默认为1.0）该熔炉正在燃烧的燃料的烧炼速度乘数。 - [图:NBT复合标签/JSON对象]RecipesUsed：烟熏炉从最后一次玩家取出成品到现在已烧炼的配方数，用于计算经验值。 - [图:整型]<配方的命名空间ID>：此配方烧炼完成的次数。

结构方块

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串]* *author：结构方块的放置者。如果结构方块由玩家放置，则为放置此方块的玩家名称；其他情况下此值为空字符串。 - [图:布尔型]* *ignoreEntities：（默认为true）表示结构中的实体是否会被忽略。 - [图:单精度浮点数]* *integrity：结构完整度。 - [图:字符串]* *metadata：元数据，在数据模式时有效。 - [图:字符串]* *mirror：结构进行镜像的方法。只会是 ``` NONE ``` （无）、 ``` LEFT_RIGHT ``` （左/右）或 ``` FRONT_BACK ``` （前/后）中的一个。如果设置值无效则为 ``` NONE ``` （无）。 - [图:字符串]* *mode：此结构方块当前的模式。只会是 ``` SAVE ``` （保存）、 ``` LOAD ``` （加载）、 ``` CORNER ``` （角落）或 ``` DATA ``` （数据）中的一个。如果设置值无效则为 ``` DATA ``` （数据）。 - [图:字符串]* *name：结构的名称，是一个命名空间ID。 - [图:整型]* *posX：（-48≤值≤48）结构起始X坐标。如果设置值小于-48则重置为-48，如果设置值大于48则重置为48。 - [图:整型]* *posY：（-48≤值≤48，默认为1）结构起始Y坐标。如果设置值小于-48则重置为-48，如果设置值大于48则重置为48。 - [图:整型]* *posZ：（-48≤值≤48）结构起始Z坐标。如果设置值小于-48则重置为-48，如果设置值大于48则重置为48。 - [图:布尔型]* *powered：表示结构方块是否被激活。 - [图:字符串]* *rotation：结构的旋转角度。只会是 ``` NONE ``` （无）、 ``` CLOCKWISE_90 ``` （顺时针旋转90°）、 ``` CLOCKWISE_180 ``` （顺时针旋转180°）或 ``` COUNTERCLOCKWISE_90 ``` （逆时针旋转90°）中的一个。如果设置值无效则为 ``` NONE ``` （无）。 - [图:长整型]* *seed：加载结构使用的种子。 - [图:整型]* *sizeX：（0≤值≤48）该结构在X方向上的大小，即结构的长度。如果设置值小于0则重置为0，如果设置值大于48则重置为48。 - [图:整型]* *sizeY：（0≤值≤48）该结构在Y方向上的大小，即结构的高度。如果设置值小于0则重置为0，如果设置值大于48则重置为48。 - [图:整型]* *sizeZ：（0≤值≤48）该结构在Z方向上的大小，即结构的宽度。如果设置值小于0则重置为0，如果设置值大于48则重置为48。 - [图:布尔型]* *showair：表示是否显示隐形方块。 - [图:布尔型]* *showboundingbox：（默认为true）表示是否在创造模式中显示结构边框。 - [图:布尔型]* *strict：表示加载结构放置方块时是否禁用方块更新及相关副效果。

测试方块

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串]* *message：测试方块中储存的消息。 - [图:字符串]* *mode：测试方块实体的模式，控制方块的功能，与其使用的纹理无关。如果设置值无效则为 ``` fail ``` 。 - [图:布尔型]* *powered：测试方块是否已被充能。

测试实例方块

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]* *data：测试实例方块储存的实例数据。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]error_message：（文本组件）运行测试后产生的错误信息。此项只会在状态为 ``` finished ``` 时出现。 - [图:布尔型]* *ignore_entities：测试结构中的实体是否会被忽略。 - [图:字符串]* *rotation：测试结构的旋转角度。只会是 ``` none ``` （无）、 ``` clockwise_90 ``` （顺时针旋转90°）、 ``` clockwise_180 ``` （顺时针旋转180°）或 ``` counterclockwise_90 ``` （逆时针旋转90°）中的一个。如果设置值无效则为 ``` none ``` （无）。 - [图:整型数组]* *size：测试结构在X、Y、Z轴上的大小。 - [图:字符串]* *status：测试实例方块的状态。只会是 ``` cleared ``` （无任务）、 ``` running ``` （正在运行）或 ``` finished ``` （已完成）中的一个。 - [图:字符串]test：（命名空间ID）一个测试实例。 - [图:NBT列表/JSON数组]errors：测试实例的错误标记。 - [图:NBT复合标签/JSON对象]：一个错误标记。 - [图:整型数组]* *pos：错误标记的位置。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *text：（文本组件）错误标记的文本。

试炼刷怪笼

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:长整型]cooldown_ends_at：冷却的结束时间。不存在此项时游戏默认为0。 - [图:NBT列表/JSON数组]current_mobs：当前还存活的由试炼刷怪笼生成的生物。 - [图:整型数组]：生物的UUID。 - [图:字符串]ejecting_loot_table：（命名空间ID）正在喷出物品的战利品表。 - [图:长整型]next_mob_spawns_at：下一个生物生成的最早时间。不存在此项时游戏默认为0。 - [图:字符串][图:NBT复合标签/JSON对象]normal_config：正常变种的试炼刷怪笼使用的试炼刷怪笼配置数据，可以为命名空间ID也可以内联定义。内联格式下的所有字段若指定为默认值则不会被保存。 - - 试炼刷怪笼配置

- - [图:字符串]items_to_drop_when_ominous：（命名空间ID）战利品表，控制不祥状态的试炼刷怪笼激活状态时生成的不祥之物生成器实体内的物品。此项不存在时游戏默认为 ``` spawners/trial_chamber/items_to_drop_when_ominous ``` 。 - [图:NBT列表/JSON数组]loot_tables_to_eject：加权列表，决定试炼刷怪笼喷出的奖励物品。决定奖励时，游戏会从此列表中先抽出一项战利品表，然后根据参与试炼的玩家决定抽取次数。此项不存在时游戏默认为 ``` spawners/trial_chamber/consumables ``` 和 ``` spawners/trial_chamber/key ``` ，权重均为1。 - [图:NBT复合标签/JSON对象]：一项战利品项。 - [图:字符串]*data：（命名空间ID）战利品表。 - [图:整型]*weight：（值>0）此项的权重。 - [图:单精度浮点数]simultaneous_mobs：（值≥0，默认为2）同时存活的生成生物的最少数量，即仅一个玩家加入试炼时同时存活的生物数量。 - [图:单精度浮点数]simultaneous_mobs_added_per_player：（值≥0，默认为1）每增加一个加入试炼玩家，同时存活生物数量的增加值。设 ``` simultaneous_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的最大同时存活数量为⌊t+p(n−1)⌋。 - [图:NBT列表/JSON数组]spawn_potentials：（默认为空）加权列表，包含了可能生成的实体。在试炼刷怪笼进行一次尝试生成后，游戏将会随机从中选择一项用于下次生成。 - [图:NBT复合标签/JSON对象]：一次可能的生成。 - [图:NBT复合标签/JSON对象]*data：一项生成数据。 - - 生成数据，见Template:Nbt inherit/spawn data/source - [图:整型]*weight：（值>0）此项的权重。 - [图:整型]spawn_range：（1≤值≤128，默认为4）生成生物的范围，采用切比雪夫距离，越靠近试炼刷怪笼生成在此位置的概率越大。 - [图:单精度浮点数]total_mobs：（值≥0，默认为6）生成生物的最少总数量，即仅一个玩家加入试炼时生成的总生物数量。 - [图:单精度浮点数]total_mobs_added_per_player：（值≥0，默认为2）每增加一个加入试炼玩家，生成生物总数量的增加值。设 ``` total_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的生物总数量为⌊t+p(n−1)⌋。 - [图:整型]ticks_between_spawn：（值≥0，默认为40游戏刻（2秒））两次尝试生成生物的最小间隔时间。

- - [图:字符串][图:NBT复合标签/JSON对象]ominous_config：不祥变种的试炼刷怪笼使用的试炼刷怪笼配置数据，格式与[图:字符串][图:NBT复合标签/JSON对象]normal_config相同。 - - 试炼刷怪笼配置

- - [图:字符串]items_to_drop_when_ominous：（命名空间ID）战利品表，控制不祥状态的试炼刷怪笼激活状态时生成的不祥之物生成器实体内的物品。此项不存在时游戏默认为 ``` spawners/trial_chamber/items_to_drop_when_ominous ``` 。 - [图:NBT列表/JSON数组]loot_tables_to_eject：加权列表，决定试炼刷怪笼喷出的奖励物品。决定奖励时，游戏会从此列表中先抽出一项战利品表，然后根据参与试炼的玩家决定抽取次数。此项不存在时游戏默认为 ``` spawners/trial_chamber/consumables ``` 和 ``` spawners/trial_chamber/key ``` ，权重均为1。 - [图:NBT复合标签/JSON对象]：一项战利品项。 - [图:字符串]*data：（命名空间ID）战利品表。 - [图:整型]*weight：（值>0）此项的权重。 - [图:单精度浮点数]simultaneous_mobs：（值≥0，默认为2）同时存活的生成生物的最少数量，即仅一个玩家加入试炼时同时存活的生物数量。 - [图:单精度浮点数]simultaneous_mobs_added_per_player：（值≥0，默认为1）每增加一个加入试炼玩家，同时存活生物数量的增加值。设 ``` simultaneous_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的最大同时存活数量为⌊t+p(n−1)⌋。 - [图:NBT列表/JSON数组]spawn_potentials：（默认为空）加权列表，包含了可能生成的实体。在试炼刷怪笼进行一次尝试生成后，游戏将会随机从中选择一项用于下次生成。 - [图:NBT复合标签/JSON对象]：一次可能的生成。 - [图:NBT复合标签/JSON对象]*data：一项生成数据。 - - 生成数据，见Template:Nbt inherit/spawn data/source - [图:整型]*weight：（值>0）此项的权重。 - [图:整型]spawn_range：（1≤值≤128，默认为4）生成生物的范围，采用切比雪夫距离，越靠近试炼刷怪笼生成在此位置的概率越大。 - [图:单精度浮点数]total_mobs：（值≥0，默认为6）生成生物的最少总数量，即仅一个玩家加入试炼时生成的总生物数量。 - [图:单精度浮点数]total_mobs_added_per_player：（值≥0，默认为2）每增加一个加入试炼玩家，生成生物总数量的增加值。设 ``` total_mobs ``` 为t，此值为p，加入试炼的玩家总数量为n，则本次试炼的生物总数量为⌊t+p(n−1)⌋。 - [图:整型]ticks_between_spawn：（值≥0，默认为40游戏刻（2秒））两次尝试生成生物的最小间隔时间。

- - [图:NBT列表/JSON数组]registered_players：加入试炼的玩家列表。 - [图:整型数组]：玩家的UUID。 - [图:整型]required_player_range：（1≤值≤128，默认为14）检测加入试炼玩家的范围，采用欧几里得距离。 - [图:NBT复合标签/JSON对象]spawn_data：下一次生成生物的数据。在决定生成一次生物后，此项数据会从配置字段的[图:NBT列表/JSON数组]spawn_potentials中随机挑选一项作为自身的数据，并覆盖之前的数据。 - - 生成数据，见Template:Nbt inherit/spawn data/source - [图:整型]target_cooldown_length：（值≥0，默认为36000游戏刻（30分））从试炼刷怪笼生成的所有生物被杀死开始，到下一次可以进行试炼的冷却时间。 - [图:整型]total_mobs_spawned：（值≥0）从试炼开始到现在生成的总生物数量。不存在此项时游戏默认为0。

陷阱箱

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName：（文本组件）当前箱子的名称，会取代默认名称出现在箱子的界面中。此项方块实体数据会被视为数据组件custom_name。 - [图:NBT复合标签/JSON对象]lock：如果存在，箱子只能用符合该物品谓词的物品打开。此项方块实体数据会被视为数据组件lock。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT列表/JSON数组]Items：（当[图:字符串]LootTable不存在时存在且有效）当前箱子内物品的列表，超出槽位范围的物品无效。如果战利品未生成，则此项不存在。箱子共有27个槽位，从左上角槽位开始横向遍历到右下角槽位结束。此项方块实体数据会被视为数据组件container。 - [图:NBT复合标签/JSON对象]：一个物品。 - - 物品共通标签，见Template:Nbt inherit/item/source - [图:字符串]LootTable：决定箱子第一次被打开时，生成战利品所用的战利品表的命名空间ID。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的战利品表数据。 - [图:长整型]LootTableSeed：（当[图:字符串]LootTable存在时有效）生成战利品使用的种子，0或不输入将使用随机序列。此项将在战利品生成之后被删除。此项方块实体数据会被视为数据组件container_loot的随机序列数据。

宝库

- [图:NBT复合标签/JSON对象] 方块实体数据 - - 方块实体共通标签，见Template:Nbt inherit/blockentity/source - [图:NBT复合标签/JSON对象]*config：宝库的配置数据。 - [图:双精度浮点数]activation_range：（默认为4）激活宝库的玩家检测范围。只要有一个没有领取奖励的玩家进入这个检测范围时，宝库就会被激活。 - [图:双精度浮点数]deactivation_range：（默认为4.5，不小于[图:双精度浮点数]activation_range）取消激活宝库的玩家检测范围。当没有任何没有领取奖励的玩家进入这个检测范围时，宝库被取消激活。 - [图:NBT复合标签/JSON对象]key_item：（默认为试炼钥匙）解锁宝库所需的物品。如果此项不存在则无法使用任何物品解锁宝库。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:字符串]loot_table：（默认为 ``` chests/trial_chambers/reward ``` ）宝库使用的战利品表的命名空间ID。 - [图:字符串]override_loot_table_to_display：覆盖奖励战利品表，设置用于展示物品的战利品表。 - [图:NBT复合标签/JSON对象]*server_data：服务端用于计算宝库行为的数据。 - [图:NBT列表/JSON数组]items_to_eject：将要喷出的奖励物品。 - [图:NBT复合标签/JSON对象]：一项奖励物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source - [图:NBT列表/JSON数组]rewarded_players：已经接受奖励的玩家列表，总长度不会超过128。 - [图:整型数组]：玩家的UUID。 - [图:长整型]state_updating_resumes_at：下一次更新宝库状态的时间。此项不存在时游戏默认为0。 - [图:整型]total_ejections_needed：本次奖励中将要喷出的奖励物品总数。此项不存在时游戏默认为0。 - [图:NBT复合标签/JSON对象]*shared_data：客户端用于渲染宝库的数据。 - [图:双精度浮点数]connected_particles_range：（默认为4.5）在此范围内与宝库相关联的玩家可以渲染相应的粒子。 - [图:NBT列表/JSON数组]connected_players：与这个宝库相关联的玩家。 - [图:整型数组]：玩家的UUID。 - [图:NBT复合标签/JSON对象]display_item：宝库内渲染的物品。 - - 物品共通标签，见Template:Nbt inherit/itemnoslot/source

# 存储格式

所有方块实体都保存在区块数据中，位于区块数据的[图:NBT列表/JSON数组]block_entities标签内。

存储格式与数据格式类似，但附加了世界生成相关信息：

- [图:NBT复合标签/JSON对象] 方块实体根标签。 - [图:布尔型]* *keepPacked：此方块实体是否为纯数据形式，即还未真正加入世界。在世界中可访问的方块实体此项为false。 - 其他标签与数据格式相同。

当世界生成时，世界生成过程中放置的方块如果具有方块实体数据，游戏就会以[图:布尔型]keepPacked为true、[图:字符串]id为
```
DUMMY
```

的形式写入区块数据中，此时这些方块实体还不可访问，仅仅是保存了这些数据但没有加入到世界中。当原型区块转换为世界区块，或作为世界区块访问获取对应位置的方块实体数据时，这些数据会被立刻反序列化为方块实体并加入世界，在加入世界后[图:布尔型]keepPacked就会被设置为false。

# 历史

# 导航

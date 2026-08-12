---
name: minecraft-data-component
description: |
  数据组件（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于基岩版中的物品堆叠组件，请见“基岩版物品堆叠组件”。
  
  【涵盖内容】
  - 加载行为
  - 物品堆叠
  - 方块实体
  - 实体
  - attack_animation
  - attack_range
  - attribute_modifiers
  - banner_patterns
  - base_color
  - bees
  - block_entity_data
  - block_state
  
  【关键定义】
  - 数据包路径：data/chests/trial_chambers/reward_ominous、data/chicken/variant
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 数据组件 的完整规范时
---

关于基岩版中的物品堆叠组件，请见“基岩版物品堆叠组件”。

 “组件”重定向至此。关于其他用法，请见“组件（消歧义）”。
 “元件”重定向至此。关于建造红石电路的元件，请见“红石元件”。

本条目所述内容仅适用于Java版。
 Wiki上有与该主题相关的教程！
见教程:物品堆叠组件。

 Wiki上有与该主题相关的教程！
见教程:物品堆叠组件。

 
数据组件（Data Component），或简称为组件（Component），是用于定义和存储各种数据属性的结构化数据。

由于物品堆叠全面使用数据组件格式，故其也被称为物品堆叠组件（Item Stack Component）或物品组件（Item Component）。

# 行为

数据组件是结构化的数据，也即每一个组件都有自己独特的编码方式。如果组件的数据格式不正确，则游戏会立即解析失败，对应的命令和文件等全部无效。

由于数据组件的编码解码行为，使得其与通常的NBT标签数据不同。通常的NBT标签仅会在游戏尝试序列化为程序对象时才判断其是否符合编码格式，而组件自游戏加载之初就进行了判断。这使得数据组件格式拥有更快的加载性能，可以更早地发现命令和文件中的潜在错误。

除了编码方式外，每一个组件都有是否持久化和是否同步两个基本性质。不可持久化的组件通常仅用于网络传输，随游戏计算完毕或内存卸载而移除，不会保存到存档里，强行加载和保存也会导致游戏解析失败。若无特殊说明，下文的组件均指持久化组件。

## 加载行为

物品堆叠、方块实体和实体可以拥有数据组件。

目前方块实体和实体依然使用了非结构化的NBT标签存储。为了对方块实体或实体应用或获取数据组件，游戏会将对应的组件和对应的NBT标签绑定。这步绑定操作所用的组件在游戏内部被称为隐式组件（Implicit Component）。游戏通常在使用物品放置方块或实体时应用组件，而使用谓词检测或破坏方块时获取组件。

例如：当使用命名过的箱子放置箱子时，箱子物品的
```
custom_name
```

组件会应用到箱子的方块实体上。而方块实体会使用方块实体数据[图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName来保存它。而当从箱子获取
```
custom_name
```

组件时，游戏会将方块实体数据[图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]CustomName视为
```
custom_name
```

组件。

## 物品堆叠

 参见：物品格式 
物品堆叠全面使用数据组件格式。虽然游戏为每个物品定义了依据物品类型的默认组件，但默认组件只在内存中计算，不会保存到存档中。而存档会存储物品的组件修订（Data Component Patch）数据，组件修订中指定的组件会覆盖默认组件的值，且带
```
!
```

前缀的组件会移除该物品的默认组件。

绝大多数数据组件都对物品自身有实际作用，决定了物品的诸多性质，例如是否可堆叠、可损坏等，影响了大量的游戏行为。当以组件为单位修改物品时，游戏不允许物品同时具有
```
damage
```

组件和值大于1的
```
max_stack_size
```

的组件补丁，即物品不可以既可堆叠又可损坏。

- [图:NBT复合标签/JSON对象] 物品堆叠数据 - [图:字符串]* *id：（命名空间ID）表示某种类的物品堆叠。若未指定，游戏会在加载区块或者生成物品时将其变更为空气。 - [图:NBT复合标签/JSON对象]components：当前物品的组件修订，将修改物品的数据组件信息。 - [图:任意类型]<数据组件ID>：一项组件和其对应的数据，代表物品拥有此组件。设置组件数据时可以不写命名空间，但游戏在导出时会自行加上 ``` minecraft: ``` 前缀。 - [图:NBT复合标签/JSON对象]!<数据组件ID>：存在时，使一个数据组件失效。此复合标签的内容不影响行为。设置组件数据时可以不写命名空间，但游戏在导出时会自行加上 ``` minecraft: ``` 前缀。 - [图:整型]count：（0<值≤物品最大堆叠数量）物品的堆叠数。不存在或无效时则默认为1。

## 方块实体

 参见：方块实体数据格式 
方块实体部分采用数据组件格式。一部分组件以组件格式原样存储，另一部分则以隐式组件存储于NBT标签中。目前方块实体不支持删除组件。

当使用方块物品放置方块时，
```
block_state
```

和
```
block_entity_data
```

组件永远不会保存到方块实体中。

- [图:NBT复合标签/JSON对象] 方块实体数据 - [图:整型]* *x：当前方块实体的X坐标。 - [图:整型]* *y：当前方块实体的Y坐标。 - [图:整型]* *z：当前方块实体的Z坐标。 - [图:字符串]* *id：（命名空间ID）方块实体的类型。 - [图:NBT复合标签/JSON对象]components：方块实体的数据组件信息。当使用此方块实体对应的物品放置此方块实体时，物品额外持有的且不会被继承序列化处理的数据组件会被复制存储入此标签内。 - [图:任意类型]<数据组件ID>：一项数据组件和其对应的数据。

游戏内使用的以隐式组件存储的方块实体组件如下：

## 实体

实体的数据组件全部以隐式组件的形式存储于非组件结构的NBT数据中。

若物品同时具有
```
bucket_entity_data
```

、
```
entity_data
```

组件和其他实体组件，则应用优先级依次为
```
bucket_entity_data
```

、
```
entity_data
```

、其他组件。

游戏内使用的以隐式组件存储的实体组件如下：

# 数据组件类型

游戏总共定义了下列数据组件。此处仅简要介绍，完整格式和作用见下文。

- attack_animation（攻击动画）
- attack_range（攻击距离）
- attribute_modifiers（属性修饰符）
- banner_patterns（旗帜图案）
- base_color（盾牌基色）
- bees（蜜蜂数据）
- block_entity_data（方块实体数据）
- block_state（方块状态）
- block_transformer（物品交互方块变换效果）
- blocks_attacks（格挡攻击）
- break_sound（物品耐久耗尽音效）
- brewing_fuel（用于酿造的燃料）
- bucket_entity_data（生物桶所装实体数据）
- bundle_contents（收纳袋内物品）
- can_break（冒险模式下该物品可破坏的方块）
- can_place_on（冒险模式下该物品可放置于的方块）
- charged_projectiles（所装载的弹射物）
- compostable（堆肥行为）
- consumable（可消耗性）
- container（容器内物品）
- container_loot（容器战利品表）
- cooking_fuel（用于烧炼的燃料）
- custom_data（自定义数据）
- custom_model_data（自定义模型数据）
- custom_name（自定义名称）
- damage（物品损坏值）
- damage_resistant（不被指定伤害类型摧毁）
- damage_type（攻击造成的伤害类型）
- debug_stick_state（调试棒状态）
- death_protection（死亡保护）
- dye（染料颜色）
- dyed_color（所染颜色）
- enchantable（在附魔台上的附魔能力）
- enchantment_glint_override（附魔光效）
- enchantments（魔咒）
- entity_data（实体数据）
- equippable（可穿戴性）
- firework_explosion（烟火之星爆裂数据）
- fireworks（烟花火箭爆裂和飞行数据）
- food（食物）
- glider（穿戴后可滑翔）
- instrument（山羊角乐器）
- intangible_projectile（只能被创造模式玩家捡起的弹射物）
- interact_animation（交互动画）
- item_model（物品模型）
- item_name（物品名称）
- jukebox_playable（插入唱片机并播放音乐）
- kinetic_weapon（设置冲锋攻击）
- lock（锁）
- lodestone_tracker（所追踪的磁石位置）
- lore（物品提示框中的描述信息）
- map_color（地图在物品栏内的纹理颜色）
- map_decorations（地图图标）
- map_id（地图编号）
- max_damage（最大耐久度）
- max_stack_size（最大堆叠数）
- minimum_attack_charge（进行近战或穿刺攻击所需的冷却进度最小值）
- mob_visibility（装备对生物探测半径的影响）
- note_block_sound（放有玩家的头的音符盒音效）
- ominous_bottle_amplifier（物品的不祥之兆状态效果倍率）
- piercing_weapon（设置戳刺攻击）
- pot_decorations（饰纹陶罐陶片装饰）
- potion_contents（药水效果与状态效果信息）
- potion_duration_scale（状态效果时长缩放倍率）
- profile（玩家游戏档案信息）
- provides_banner_patterns（置于织布机旗帜图案槽位时提供的旗帜图案）
- provides_pottery_pattern（为饰纹陶罐提供的陶片样式）
- provides_trim_material（作为锻造原材料时提供的盔甲纹饰材料）
- rarity（稀有度）
- recipes（知识之书配方信息）
- repairable（可在铁砧上被修复）
- repair_cost（在铁砧上的累计惩罚值）
- sign_text_back（告示牌类方块的背面文本）
- sign_text_front（告示牌类方块的正面文本）
- stored_enchantments（所存储的“无活性”魔咒）
- sulfur_cube_content（硫方怪吸收的方块）
- suspicious_stew_effects（谜之炖菜效果）
- swing_animation（攻击动画）
- tool（成为挖掘某方块的工具）
- tooltip_display（物品提示框及附加信息的显示）
- tooltip_style（物品提示框背景和边框样式）
- trim（盔甲纹饰）
- unbreakable（无法破坏）
- use_cooldown（使用后冷却）
- use_effects（玩家使用物品时的行为）
- use_remainder（使用后返还物品）
- villager_food（村民食物）
- waxed（涂蜡）
- weapon（作为武器时的行为）
- writable_book_content（书与笔内容）
- written_book_content（成书内容）

实体变种组件

- axolotl/variant（美西螈变种）
- cat/collar（猫项圈颜色）
- cat/sound_variant（猫音效变种）
- cat/variant（猫变种）
- chicken/sound_variant（鸡音效变种）
- chicken/variant（鸡变种）
- cow/sound_variant（牛音效变种）
- cow/variant（牛变种）
- cushion/color（坐垫颜色）
- fox/variant（狐狸变种）
- frog/variant（青蛙变种）
- horse/variant（马变种）
- llama/variant（羊驼变种）
- mooshroom/variant（哞菇变种）
- parrot/variant（鹦鹉变种）
- painting/variant（画变种）
- pig/sound_variant（猪音效变种）
- pig/variant（猪变种）
- rabbit/variant（兔子变种）
- salmon/size（鲑鱼体型尺寸）
- sheep/color（绵羊变种）
- shulker/color（潜影贝颜色）
- tropical_fish/base_color（热带鱼体色）
- tropical_fish/pattern（热带鱼花纹）
- tropical_fish/pattern_color（热带鱼花纹颜色）
- villager/variant（村民变种）
- wolf/collar（狼项圈颜色）
- wolf/sound_variant（狼音效变种）
- wolf/variant（狼变种）

临时组件

- additional_trade_cost
- creative_slot_lock
- map_post_processing

# 命令格式

```
item_stack
```

和
```
item_predicate
```

参数类型支持物品堆叠组件。

```
item_stack
```

参数类型可以加载物品组件，也可通过在组件名前添加
```
!
```

来移除该物品的默认组件，在
```
/
give
```

等命令中使用。所提供的组件都会被设置，而未提供的组件会被设为默认值。格式参见参数类型 § item_stack。

```
item_predicate
```

参数类型可以检测物品组件，在
```
/
clear
```

等命令中使用。另外，该参数类型还可以直接使用数据组件谓词检测物品堆叠组件。格式参见参数类型 § item_predicate。

# 数据格式

## attack_animation

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:attack_animation：使用此物品攻击时的动画。 - [图:字符串]type：（默认为 ``` whack ``` ）摇摆动画类型。取值只能为 ``` whack ``` （默认攻击动画）、 ``` stab ``` （矛的戳刺攻击动画，部分人形生物持有时还有戳刺攻击的第三人称手部姿势）。 - [图:整型]duration：（默认为6）动画播放的周期刻数。

## attack_range

此组件负责生物使用物品攻击时使用的攻击距离。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:attack_range：生物持有此物品时的攻击距离，会覆写玩家的实体交互距离属性。 - [图:单精度浮点数]min_reach：（0≤值≤64，默认为0）攻击者到目标的最小有效距离。以攻击者眼睛位置、沿视角方向到被攻击者攻击判定箱的最小距离计算。 - [图:单精度浮点数]max_reach：（0≤值≤64，默认为3）攻击者到目标的最大有效距离。以攻击者眼睛位置、沿视角方向到被攻击者攻击判定箱的最小距离计算。 - [图:单精度浮点数]min_creative_reach：（0≤值≤64，默认为0）创造模式玩家到目标的最小有效距离，计算方式同上。 - [图:单精度浮点数]max_creative_reach：（0≤值≤64，默认为5）创造模式玩家到目标的最大有效距离，计算方式同上。 - [图:单精度浮点数]hitbox_margin：（0≤值≤1，默认为0.3）决定攻击判定箱的大小。游戏将实体的碰撞箱向各个方向扩展此距离得到攻击判定箱。 - [图:单精度浮点数]mob_factor：（0≤值≤2，默认为1.0）对于非玩家生物，其使用的最小有效距离和最大有效距离的缩放乘数。

## attribute_modifiers

此组件负责存储修饰生物属性的属性修饰符，当物品在生物的指定槽位上时可以修改其所在生物的属性。

此组件会为物品提示框提供显示内容，内容为此组件和物品具有的魔咒提供的物品属性修饰符。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:attribute_modifiers：物品为持有者提供的属性修饰符。 - [图:NBT复合标签/JSON对象]：一个修饰符。 - [图:双精度浮点数]* *amount：计算中修饰符调整基础值的数值。 - [图:NBT复合标签/JSON对象]display：属性修饰符在提示框的显示方式。 - [图:字符串]* *type：显示类型，枚举值见下。 - - 当[图:字符串]type为 ``` default ``` 时，显示此项计算后的属性修饰符值。此项也为默认值。 - - 当[图:字符串]type为 ``` hidden ``` 时，不显示此项属性修饰符值。 - - 当[图:字符串]type为 ``` override ``` 时，替换所显示的属性修饰符文本，附加字段如下： - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *value：（文本组件）替换后的文本。 - [图:字符串]* *id：（命名空间ID）当前属性修饰符的ID。 - [图:字符串]* *operation：定义修饰符对属性的基础值的运算方法。可以为 ``` add_value ``` （Op0）、 ``` add_multiplied_base ``` （Op1）、 ``` add_multiplied_total ``` （Op2）。 - [图:字符串]slot：（默认为 ``` any ``` ）一个装备槽位组，指定修饰符的有效槽位。 - [图:字符串]* *type：（命名空间ID）一个属性的ID，表示当前属性修饰符要修饰的属性。

示例
给予一个木棍，玩家手持该木棍时，玩家的尺寸会增加4倍（即原来的5倍大小）。物品提示框中将显示被
```
example:grow
```

属性修饰符修饰后的
```
scale
```

属性值。
```
/
give
 @s stick[attribute_modifiers=[{type:"scale",slot:"hand",id:"example:grow",amount:4,operation:"add_multiplied_base"}]]
```

## banner_patterns

此组件负责存储旗帜和盾牌上的旗帜图案。

此组件会为物品提示框提供显示内容，内容为物品具有的旗帜图案列表，按顺序显示。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:banner_patterns：旗帜图案的列表。 - [图:NBT复合标签/JSON对象]：一层图案。 - [图:字符串]* *color：这一层图案的颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。 - [图:字符串][图:NBT复合标签/JSON对象]* *pattern：这一层图案的样式。可以为旗帜图案的ID，也可以是旗帜图案的内联格式（见旗帜图案定义格式）。 - - 旗帜图案，见Template:Nbt inherit/banner pattern/source

## base_color

此组件负责盾牌的基础颜色。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:base_color：盾牌的基础颜色，同时影响盾牌的名称。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

示例
给予玩家一个盾牌基色为黄绿色的盾牌：
```
/
give
 @s shield[base_color=lime]
```

## bees

此组件负责保存蜂巢和蜂箱的蜜蜂数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:bees：蜂巢和蜂箱的蜜蜂数据。 - [图:NBT复合标签/JSON对象]：一只蜜蜂的数据。 - [图:字符串][图:NBT复合标签/JSON对象]entity_data：蜜蜂的部分实体数据。如果采用字符串格式进行定义，则游戏会将字符串的内容视为SNBT加载，游戏只保存为复合标签格式。 - 见实体数据格式。下列标签不会被保存，也不会被加载：[图:短整型]Air、[图:NBT复合标签/JSON对象]drop_chances、[图:NBT复合标签/JSON对象]equipment、[图:NBT复合标签/JSON对象]Brain、[图:布尔型]CanPickUpLoot、[图:短整型]DeathTime、[图:单精度浮点数]fall_distance、[图:布尔型]FallFlying、[图:短整型]Fire、[图:整型]HurtByTimestamp、[图:短整型]HurtTime、[图:布尔型]LeftHanded、[图:NBT列表/JSON数组]Motion、[图:布尔型]NoGravity、[图:布尔型]OnGround、[图:整型]PortalCooldown、[图:NBT列表/JSON数组]Pos、[图:NBT列表/JSON数组]Rotation、[图:整型数组]sleeping_pos、[图:整型]CannotEnterHiveTicks、[图:整型]TicksSincePollination、[图:整型]CropsGrownSincePollination、[图:整型数组]hive_pos、[图:NBT列表/JSON数组]Passengers、[图:整型数组][图:NBT复合标签/JSON对象]leash、[图:整型数组]UUID。 - [图:整型]* *min_ticks_in_hive：蜜蜂会在巢内滞留的最短时间。 - [图:整型]* *ticks_in_hive：蜜蜂在巢内已滞留的时间。

## block_entity_data

此组件负责保存方块实体数据。当玩家放置具有方块实体的方块时，此组件内部的NBT数据就会转化为方块实体数据。

若放置的方块为指定了附加数据的任意命令方块、讲台、任意告示牌、任意悬挂式告示牌、刷怪笼或试炼刷怪笼，则非管理员玩家使用这些物品时不会设置方块实体数据，且提示框中会显示安全警告。

此组件会为物品提示框提供内容：如果方块是刷怪笼或试炼刷怪笼，且此组件为空则会显示可以使用刷怪蛋设置生物；如果方块是刷怪笼，则会根据对应的NBT数据显示内部的生物。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:block_entity_data：物品放置方块时将应用到方块实体的数据。如果采用字符串格式进行定义，则游戏会将字符串的内容视为SNBT加载，游戏只保存为复合标签格式。 - [图:字符串]* *id：（命名空间ID）方块实体。 - 若干与该方块对应的方块实体数据标签，见方块实体数据格式。

示例
给予一个蜘蛛刷怪笼。要放置该刷怪笼，玩家必须要有管理员权限：
```
/
give
 @s spawner[block_entity_data={id:"mob_spawner",SpawnData:{entity:{id:"spider"}}}]
```

## block_state

此组件负责保存方块状态。当玩家放置方块时，游戏会根据此组件内部的方块属性及其值设置方块属性，没有指定的方块属性使用默认值。如果方块属性对于被放置的方块不存在或对应的方块属性值无效，则这项设置不起任何作用。

此组件会为物品提示框提供内容：若方块属性
```
honey_level
```

是一个数值的字符串，则提示框会显示蜂蜜等级信息。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:block_state：物品放置方块时将要设置的方块状态。 - [图:字符串]<方块属性>：此项方块属性的值。

示例
给予一个被放置时总位于方块网格的上半部分的竹台阶：
```
/
give
 @s bamboo_slab[block_state={type:"top"}]
```

## block_transformer

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此组件负责物品的对方块交互时的使用行为。当玩家对方块使用物品时，游戏会根据此组件提供的方块变换效果实施方块变换，并产生可能存在的掉落物。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:block_transformer：当使用物品与方块交互时的方块变换效果，至多有200项效果。 - [图:NBT复合标签/JSON对象]：一项方块变换效果。 - [图:NBT复合标签/JSON对象]* *block_state_provider：方块将要变换为的状态。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:字符串][图:NBT复合标签/JSON对象]block_sound：（默认为空）成功变换方块时播放的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串]particle：（默认为 ``` none ``` ）成功变换方块时产生的粒子效果。取值可以为 ``` none ``` （无粒子效果）、 ``` scrape ``` （除锈的粒子效果）、 ``` wax_on ``` （上蜡的粒子效果）或 ``` wax_off ``` （除蜡的粒子效果）。 - [图:NBT列表/JSON数组]disallowed_faces：（默认为空）与方块交互时不会触发方块变换的面。 - [图:字符串]：不会触发方块变换的面。取值可以为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - [图:字符串]loot：（命名空间ID）成功变换方块时产生的掉落物的战利品表。 - [图:字符串]drop_strategy：（默认为 ``` from_middle ``` ）成功变换方块时掉落物生成的方式。取值可以为 ``` clicked_face ``` （生成于交互面）或 ``` from_middle ``` （生成于方块中心）。 - [图:布尔型]update_from_neighbors：（默认为 ``` true ``` ）决定变换后的方块是否要根据临近的方块更新自身。 - [图:字符串]transform_type：（默认为 ``` single_block ``` ）决定方块变换的类型。取值可以为 ``` single_block ``` 或 ``` copper_chest ``` 。当值为 ``` single_block ``` 时，仅影响交互的方块；当值为 ``` copper_chest ``` 时，若变换前后的方块均为铜箱子或其任意锈蚀、涂蜡变种，此项变换会同时影响大型铜箱子的两个部分。 - [图:布尔型]consume_on_use：（默认为 ``` true ``` ）使用的物品是否会消耗。 - [图:整型]item_damage_per_use：（值≥0，默认为0）使用的物品消耗的耐久度。

## blocks_attacks

此组件负责物品的格挡行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:blocks_attacks：物品使用时的格挡行为。 - [图:单精度浮点数]block_delay_seconds：（值≥0，默认为 ``` 0 ``` ）成功阻挡攻击前需要按住右键的秒数。 - [图:字符串][图:NBT复合标签/JSON对象]block_sound：成功阻挡攻击时播放的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT列表/JSON数组]bypassed_by：可以无视此物品的阻挡而造成实际伤害的伤害类型。可以为单个ID、列表或标签。 - [图:NBT列表/JSON数组]damage_reductions：控制可阻挡多少伤害。未指定时，可阻挡一切伤害。 - [图:NBT复合标签/JSON对象]：控制可挡下的伤害量和伤害类型。阻挡成功时，伤害减少 ``` clamp(base + factor * 所受攻击伤害 , 0, 所受攻击伤害 ) ``` 。 - [图:单精度浮点数]* *base：固定阻挡的伤害。 - [图:单精度浮点数]* *factor：应被阻挡的伤害比例。 - [图:单精度浮点数]horizontal_blocking_angle：（值>0，角度制，默认为 ``` 90 ``` ）在水平方向上，以当前玩家视角的水平分量向量为基准，如果受伤害方向与基准方向夹角小于此角度则伤害可被阻挡，否则不能阻挡。 任何无来源伤害均被视为需要 ``` 180 ``` 度才能阻挡。 - [图:字符串][图:NBT列表/JSON数组]type：可阻挡的伤害类型。允许单个ID、列表或标签。未指定则表示对所有伤害有效。 - [图:单精度浮点数]disable_cooldown_scale：（值≥0，默认为 ``` 1 ``` ）被可停用阻挡的攻击击中时，物品冷却时长的乘数。为 ``` 0 ``` 时，此物品不能被攻击禁用。 - [图:字符串][图:NBT复合标签/JSON对象]disabled_sound：此物品被攻击禁用时播放的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:NBT复合标签/JSON对象]item_damage：控制攻击对物品造成的耐久损耗。如所受攻击伤害小于 ``` threshold ``` ，则不造成损耗；否则，物品耐久最终损耗 ``` floor(base + factor * 所受攻击伤害 ) ``` 。仅当最终值大于0时生效。 - [图:单精度浮点数]* *base：（默认为0）损耗物品固定耐久度。 - [图:单精度浮点数]* *factor：（默认为1）所受攻击伤害的乘数。 - [图:单精度浮点数]* *threshold：（默认为1，值≥0）最低可以对此物品造成耐久度损耗的伤害。

示例
给予一个弓，玩家使用此弓的同时会格挡前方所有类型所有伤害的攻击（因为使用物品和格挡的按键均为鼠标右键），且不会被可禁用阻挡的攻击禁用：
```
/
give
 @s bow[blocks_attacks={disable_cooldown_scale:0}]
```

## break_sound

此组件负责物品耐久度耗尽时播放的音效。音效的声音分类取决于持有此物品的生物。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:break_sound：物品耐久度耗尽时播放的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source

示例
给予一个物品破坏音效为紫水晶块被破坏的音效的金锹：
```
/
give
 @a minecraft:golden_shovel[minecraft:break_sound={sound_id:block.amethyst_block.break}]
```

## brewing_fuel

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:brewing_fuel：描述物品作为酿造台的燃料的行为。 - [图:单精度浮点数][图:字符串]* *uses：表示物品作为酿造台燃料时可供炼制药水次数的数值提供器。为浮点数时表示常量，为字符串时表示所引用的数值提供器的命名空间ID。 - [图:单精度浮点数][图:字符串]* *speed_multiplier：表示物品作为酿造台燃料时酿造速度倍率的数值提供器。为浮点数时表示常量，为字符串时表示所引用的数值提供器的命名空间ID。

## bucket_entity_data

此组件负责保存生物桶的数据。游戏从生物获取生物桶时会设置下列数据，放出生物时会设置对应的数据，指定其他的NBT数据不起作用。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:bucket_entity_data：生物桶对桶中生物的部分实体数据。如果采用字符串格式进行定义，则游戏会将字符串的内容视为SNBT加载，游戏只保存为复合标签格式。 - [图:布尔型]Glowing：表示桶中生物是否有发光的轮廓线。 - [图:单精度浮点数]Health：桶中生物的生命值。 - [图:布尔型]Invulnerable：表示桶中生物是否能抵抗绝大多数伤害。 - [图:布尔型]NoAI：表示桶中生物的AI是否被禁用。 - [图:布尔型]NoGravity：表示桶中生物是否不受重力影响。 - [图:布尔型]Silent：表示桶中生物是否不会发出任何声音。 - - 如果桶中生物是蝌蚪，则有下列2个额外标签： - [图:整型]Age：桶中蝌蚪的年龄。大于等于24000时，蝌蚪会长大成青蛙。 - [图:布尔型]AgeLocked：表示蝌蚪的年龄是否不会随时间自然增长。 - - 如果桶中生物是美西螈，则有下列3个额外标签： - [图:整型]Age：桶中美西螈的年龄。生物为幼体时为负值；生物为成体时为正值或0，如果为正值则表示距离生物能再次繁衍的时间。 - [图:布尔型]AgeLocked：表示美西螈的年龄是否不会随时间自然增长或减少。 - [图:长整型]HuntingCooldown：桶中美西螈生物记忆 ``` has_hunting_cooldown ``` 的过期倒计时。 - - 如果桶中生物是硫方怪，则有下列2个额外标签： - [图:整型]*age：（默认为0）表示桶中的硫方怪的年龄。原版游戏未使用。 - [图:布尔型]*age_locked：（默认为 ``` false ``` ）表示硫方怪的年龄是否不会随时间自然增长。原版游戏未使用。

## bundle_contents

此组件负责保存收纳袋内部包含的物品；拥有此组件的物品实体被摧毁时会释放内容物。

此组件会为物品提示框提供内容：如果物品是收纳袋，则会显示容量条。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:bundle_contents：收纳袋的内部物品栏。 - [图:字符串][图:NBT复合标签/JSON对象]：一个物品。后加入的物品在列表前方，先加入的物品在列表后方。 - - 物品模板，见Template:Nbt inherit/item template/source

示例
给予一个收纳袋，其中收纳袋内的物品从列表前方到后方分别为铜锭、铁锭、金锭：
```
/
give
 @s bundle[bundle_contents=[{id:"copper_ingot"},{id:"iron_ingot"},{id:"gold_ingot"}]]
```

## can_break 和 can_place_on

此组件负责控制冒险模式玩家能否破坏指定方块或与指定方块交互，可互动方块会在提示框中提示。如果存在此组件但方块谓词未指定或不满足条件，则显示于提示框的方块为“未知”，且此物品可与任何方块互动。游戏不会测试方块实体组件。

```
can_break
```

组件还可以触发红石矿石、龙蛋或音符盒的挖掘开始时效果。

指定列表时不能是空列表，且只有一个元素时游戏只保存为复合标签形式。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]minecraft:can_break：检查被破坏的方块是否满足指定的方块谓词，作为列表时内部元素与此标签作为复合标签时相同。 - - 方块谓词，见Template:Nbt inherit/block predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]minecraft:can_place_on：检查被交互的方块是否满足指定的方块谓词，作为列表时内部元素与此标签作为复合标签时相同。 - - 方块谓词，见Template:Nbt inherit/block predicate/source

示例
给予一把冒险模式下仅能挖掘一些矿石的金镐：
```
/
give
 @s golden_pickaxe[can_break={blocks:['copper_ore','coal_ore','iron_ore','gold_ore','diamond_ore','emerald_ore']}]
```

给予一个冒险模式下仅能放置在砂岩上的石头：

```
/
give
 @s stone[can_place_on={blocks:'sandstone'}]
```

## charged_projectiles

此组件负责存储弩装载的物品信息。此组件的所有物品将在提示框中显示，连续的相同内容物会合并显示。若物品列表存在烟花火箭则弩显示为“装填烟花火箭的弩”，否则为“装填箭的弩”。此组件不存在时代表弩没有装载任何物品。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:charged_projectiles：弩的内部物品栏，表示弩的装填物。最多只能有1024个元素。 - [图:字符串][图:NBT复合标签/JSON对象]：一个物品。 - - 物品模板，见Template:Nbt inherit/item template/source

## compostable

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此组件控制物品是否能被堆肥，以及堆肥后所增加的堆肥层数。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:compostable：物品的堆肥行为。 - [图:单精度浮点数][图:字符串]layers：表示物品堆肥时增加层数的数值提供器。为浮点数时表示常量，为字符串时表示所引用的数值提供器的命名空间ID。

## consumable

此组件控制物品是否具有消耗使用行为，以及使用后的效果。此处的消耗使用指物品数量在使用后会减少的操作，不包含方块物品的放置等对方块进行的有效操作。

这些物品即使使用此组件，也不能被消耗使用：船、运输船；满足放置条件的矿车、漏斗矿车、命令方块矿车、运输矿车、动力矿车和TNT矿车；成书；三叉戟；刷子；铁桶、水桶、熔岩桶、鳕鱼桶、鲑鱼桶、河豚桶、热带鱼桶、美西螈桶、蝌蚪桶；硫方怪桶；弓、弩；烟花火箭和所有刷怪蛋。

若物品同时具有
```
food
```

、​
```
ominous_bottle_amplifier
```

、​
```
potion_contents
```

和​
```
suspicious_stew_effects
```

等组件，则这些组件的效果也会一并应用。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:consumable：物品的消耗使用行为。 - [图:字符串]animation：（默认为 ``` eat ``` ）物品使用时的动画。可以为 ``` none ``` （无动作）、 ``` eat ``` （吃）、 ``` drink ``` （饮用）、 ``` block ``` （格挡）、 ``` bow ``` （拉弓）、 ``` brush ``` （清刷）、 ``` crossbow ``` （弩上弦）、 ``` spear ``` （矛蓄力）、 ``` trident ``` （三叉戟投掷）、 ``` spyglass ``` （看望远镜）、 ``` toot_horn ``` （吹山羊角）和 ``` bundle ``` （使用收纳袋）。 - [图:单精度浮点数]consume_seconds：（值≥0，默认为1.6）物品使用的时间，单位为秒。当此值为0时，物品立刻使用，不会像拉弓等操作需要等待时间。 - [图:布尔型]has_consume_particles：（默认为 ``` true ``` ）物品在使用时是否产生物品破碎粒子。 - [图:NBT列表/JSON数组]on_consume_effects：当物品被使用后产生的效果列表。 - [图:NBT复合标签/JSON对象]：一项消耗使用效果。 - [图:字符串]* *type：消耗使用效果类型。 - - 如果[图:字符串]type为 ``` apply_effects ``` ，则对使用此物品的生物添加状态效果： - [图:NBT列表/JSON数组]* *effects：物品使用后添加的状态效果。 - [图:NBT复合标签/JSON对象]：一项状态效果。 - - 状态效果，见Template:Nbt inherit/effect/source - [图:单精度浮点数]probability：（0≤值≤1，默认为1）使用后施加此状态效果的概率。 - - 如果[图:字符串]type为 ``` clear_all_effects ``` ，则对使用此物品的生物移除所有状态效果。 - - 如果[图:字符串]type为 ``` play_sound ``` ，则播放指定的声音： - [图:字符串][图:NBT复合标签/JSON对象]* *sound：要播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - - 如果[图:字符串]type为 ``` remove_effects ``` ，则对使用此物品的生物移除指定状态效果： - [图:字符串][图:NBT列表/JSON数组]* *effects：物品使用后要移除的状态效果。可以为以 ``` # ``` 开头的状态效果标签、一个状态效果ID、或以多个状态效果ID组成的列表。 - - 如果[图:字符串]type为 ``` teleport_randomly ``` ，则对使用此物品的生物进行随机传送： - [图:单精度浮点数]diameter：（值>0，默认为16）随机传送的半径，以传送前的位置作为原点。 - [图:字符串][图:NBT复合标签/JSON对象]sound：（默认为 ``` entity.generic.eat ``` ）使用物品时产生的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source

示例
给予当前实体一个铁镐，按下右键会花费1.6秒（32游戏刻）食用此铁镐，食用时播放声音事件“铁砧：着陆”，食用后获得6000游戏刻（5分）的不显示效果粒子的16级急迫效果：
```
/
give
 @s minecraft:iron_pickaxe[minecraft:consumable={animation:"eat",consume_seconds:1.6,on_consume_effects:[{type:"apply_effects",effects:[{amplifier:15,duration:6000,id:"haste",show_icon:true,show_particles:false}]}],sound:"block.anvil.land"}]
```

## container

此组件存储容器方块内部物品栏的物品。当此方块的物品实体被摧毁时会释放内容物。

此组件会为物品提示框提供内容：游戏会根据槽位顺序，依次显示对应的物品及数量，即潜影盒提示框的显示内容。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:container：方块物品的内部物品栏。 - [图:NBT复合标签/JSON对象]：一个槽位上的物品堆叠数据。 - [图:字符串][图:NBT复合标签/JSON对象]* *item：此槽位的物品堆叠数据。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:整型]* *slot：（0≤值≤255）物品堆叠所在的槽位。

示例
给予一个木桶，其中的第一个槽位放了一个苹果：
```
/
give
 @s barrel[container=[{slot:0,item:{id:apple}}]]
```

## container_loot

此组件负责保存战利品容器方块的战利品表数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:container_loot：战利品容器方块的战利品表数据。 - [图:字符串]* *loot_table：（命名空间ID）生成战利品使用的战利品表。 - [图:长整型]seed：（默认为0）生成战利品使用的种子，0或不输入将使用随机序列。

示例
给予一个箱子,当其被放置且打开时,从不祥宝库的战利品表
```
chests/trial_chambers/reward_ominous
```

抽取物品：
```
/
give
 @s chest[container_loot={loot_table:"chests/trial_chambers/reward_ominous"}]
```

## cooking_fuel

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:cooking_fuel：描述物品作为熔炉、高炉和烟熏炉的燃料的行为。 - [图:单精度浮点数][图:字符串]* *burn_time：表示物品作为上述方块的燃料时可供燃烧时间的数值提供器。为浮点数时表示常量，为字符串时表示所引用的数值提供器的命名空间ID。 - [图:单精度浮点数][图:字符串]* *speed_multiplier：表示物品作为上述方块的燃料时烧炼速度倍率的数值提供器。为浮点数时表示常量，为字符串时表示所引用的数值提供器的命名空间ID。

## custom_data

此组件负责保存自定义数据。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:custom_data：自定义的数据。如果采用字符串格式进行定义，则游戏会将字符串的内容视为SNBT加载，游戏只保存为复合标签格式。 - [图:任意类型]<自定义标签名>：一个可以为任意类型的自定义标签。

## custom_model_data

此组件负责保存自定义数据，供物品模型映射选择物品模型的自定义模型数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:custom_model_data：自定义物品模型数据。 - [图:NBT列表/JSON数组]colors：定义物品模型映射中的着色列表。 - [图:整型][图:NBT列表/JSON数组]：一个颜色。可以直接使用整数定义颜色，也可以使用RGB三个分量定义颜色，游戏只保存为整数形式。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:NBT列表/JSON数组]flags：定义 ``` condition ``` 物品模型映射类型的布尔值列表。 - [图:布尔型]：一个布尔值。 - [图:NBT列表/JSON数组]floats：定义 ``` range_dispatch ``` 物品模型映射类型的浮点数列表。 - [图:单精度浮点数]：一个浮点数。 - [图:NBT列表/JSON数组]strings：定义 ``` select ``` 物品模型映射类型的字符串列表。 - [图:字符串]：一个字符串。

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

## custom_name

此组件负责保存自定义名称。物品的自定义名称默认具有斜体。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]minecraft:custom_name：（文本组件）自定义名称。

示例
给予一个名为“Magic Wand”的木棍：
```
/
give
 @s stick[custom_name="Magic Wand"]
```

## damage

此组件负责存储物品的损坏值，和
```
max_damage
```

一起控制物品能否被损坏。此组件不存在时代表物品处于最大耐久值。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:damage：（值≥0）物品的损坏值。

示例
给予一把缺少50点耐久的下界合金镐：
```
/
give
 @s netherite_pickaxe[damage=50]
```

## damage_resistant

此组件负责控制物品免疫的伤害类型。当物品实体受到此类伤害时不会被摧毁，且物品被装备时也不会因为受到此类伤害而消耗耐久度。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:damage_resistant：物品免疫的伤害类型。 - [图:字符串][图:NBT列表/JSON数组]* *types：物品免疫的伤害类型。可以为单个ID、列表或标签。

示例
给予玩家一个不会被火焰伤害损坏的铁胸甲：
```
/
give
 @s minecraft:iron_chestplate[minecraft:damage_resistant={types:"#is_fire"}]
```

## damage_type

此组件负责生物使用此物品攻击时使用的伤害类型。如果不存在此组件，则正常使用生物默认的（如
```
player_attack
```

和
```
mob_attack
```

）伤害类型。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:damage_type：（命名空间ID）使用此物品攻击时造成的伤害类型。

示例
给予玩家一个会造成箭伤害的钻石剑：
```
/
give
 @s diamond_sword[damage_type=arrow]
```

## death_protection

此组件负责物品是否具有类似不死图腾的行为。当物品在手上时，如果生物受到伤害类型不为
```
#bypasses_invulnerability
```

的致死伤害，游戏会阻止生物死亡、将生命值设置为1，并消耗此物品。此消耗行为不属于消耗使用行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:death_protection：持有者将要死亡时阻止生物死亡后的效果。 - [图:NBT列表/JSON数组]death_effects：（默认为空）触发此物品后产生的效果。 - [图:NBT复合标签/JSON对象]：一项效果。 - [图:字符串]* *type：消耗使用效果类型。 - - 如果[图:字符串]type为 ``` apply_effects ``` ，则对使用此物品的生物添加状态效果： - [图:NBT列表/JSON数组]* *effects：物品使用后添加的状态效果。 - [图:NBT复合标签/JSON对象]：一项状态效果。 - - 状态效果，见Template:Nbt inherit/effect/source - [图:单精度浮点数]probability：（0≤值≤1，默认为1）使用后施加此状态效果的概率。 - - 如果[图:字符串]type为 ``` clear_all_effects ``` ，则对使用此物品的生物移除所有状态效果。 - - 如果[图:字符串]type为 ``` play_sound ``` ，则播放指定的声音： - [图:字符串][图:NBT复合标签/JSON对象]* *sound：要播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - - 如果[图:字符串]type为 ``` remove_effects ``` ，则对使用此物品的生物移除指定状态效果： - [图:字符串][图:NBT列表/JSON数组]* *effects：物品使用后要移除的状态效果。可以为以 ``` # ``` 开头的状态效果标签、一个状态效果ID、或以多个状态效果ID组成的列表。 - - 如果[图:字符串]type为 ``` teleport_randomly ``` ，则对使用此物品的生物进行随机传送： - [图:单精度浮点数]diameter：（值>0，默认为16）随机传送的半径，以传送前的位置作为原点。

## debug_stick_state

此组件负责保存调试棒的数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:debug_stick_state：调试棒的调试数据。 - [图:字符串]<方块命名空间ID>：一个方块和调试棒将对此方块修改的方块属性的键值对。

## dye

此组件负责存储物品的染料颜色。具有
```
dye
```

组件是物品可作为染料使用的必要条件，在对应的游戏场景测试成功后将使用此组件的颜色进行计算：

- 在各种配方中染色时，必须是提供染料的原料。（依配方定义不同）
- 在织布机中染色时，必须在标签 ``` #loom_dyes ``` 中。
- 给猫的项圈染色时，必须在标签 ``` #cat_collar_dyes ``` 中。
- 给狼的项圈染色时，必须在标签 ``` #wolf_collar_dyes ``` 中。
- 给绵羊的羊毛染色时，必须是染料物品。
- 给告示牌或悬挂式告示牌的文字染色时，必须是染料物品。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:dye：物品的染料颜色数据。取值为 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

## dyed_color

此组件负责保存物品的染色数据。根据不同的物品模型定义或其装备模型定义，此组件的颜色也会影响物品外观或装备外观。

此组件会为物品提示框提供内容：根据是否开启高级提示框显示对应的颜色或“已染色”。

- [图:NBT复合标签/JSON对象]components - [图:整型][图:NBT列表/JSON数组]minecraft:dyed_color：物品的颜色。只使用后24位，每个颜色通道占用8位，按RGB依次存储。 - - RGB颜色，见Template:Nbt inherit/rgb color/source

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

## enchantable

此组件负责存储物品的附魔能力。该组件不存在时，物品不可在附魔台中附魔。该组件存在时，若物品存在
```
enchantments
```

组件且为空，且存在可附加的魔咒，则该物品可在附魔台中附魔。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:enchantable - [图:整型]* *value：（值≥1）物品的附魔能力。

示例
给予一把可以附魔且附魔能力为2的剪刀：
```
/
give
 @s shears[enchantable={value:2}]
```

## enchantment_glint_override

此组件负责控制物品是否会显示光效，优先级高于其他任何影响光效的组件和物品自身属性。

- [图:NBT复合标签/JSON对象]components - [图:布尔型]minecraft:enchantment_glint_override：是否显示光效。

## enchantments 和 stored_enchantments

此组件负责存储物品的魔咒信息。物品提示框中也会显示魔咒及等级。

两个组件的区别在于：
```
enchantments
```

组件添加的是“带活性”的魔咒，其上的魔咒可以产生魔咒效果；而
```
stored_enchantments
```

组件添加的是“无活性”的魔咒，通常只用于附魔书存储魔咒，其上的魔咒不会产生效果。

需要注意的是，“无活性”魔咒在发挥实际附魔作用时会受到生存模式所能获取的对应附魔书的最大附魔等级的限制，例如给予自己一本锋利VI的附魔书，而其发挥的附魔作用只能为锋利V。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:enchantments：物品的魔咒数据。 - [图:整型]<魔咒命名空间ID>：（1≤值≤255）一个魔咒和对应魔咒的等级。 - [图:NBT复合标签/JSON对象]minecraft:stored_enchantments：附魔书保存的魔咒。 - [图:整型]<魔咒命名空间ID>：（1≤值≤255）一个魔咒和对应魔咒的等级。

示例
给予一把带有锋利III和击退II的木剑：
```
/
give
 @s wooden_sword[enchantments={sharpness:3,knockback:2}]
```

给予一本带有效率V和耐久III的附魔书：

```
/
give
 @s enchanted_book[stored_enchantments={efficiency:5,unbreaking:3}]
```

## entity_data

此组件负责存储物品生成对应实体时（如使用刷怪蛋或放置盔甲架）应用于所生成实体的数据。应用时采取合并的方式。若指定的实体类型无法在和平模式下存在，则提示框会提示“已在和平难度下禁用”。

若刷怪蛋将生成的实体为指定了附加数据的下落的方块、命令方块矿车或刷怪笼矿车，则非管理员玩家使用这些物品时不会设置实体数据，且提示框中会显示安全警告。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:entity_data：物品放出实体时应用到实体上的数据。如果采用字符串格式进行定义，则游戏会将字符串的内容视为SNBT加载，游戏只保存为复合标签格式。 - [图:字符串]* *id：（命名空间ID）实体类型。 - 若干与该实体对应的实体数据标签，见实体数据格式。

示例
给予一个在放置时成为小型盔甲架的盔甲架：
```
/
give
 @s armor_stand[entity_data={id:"armor_stand",Small:1b}]
```

## equippable

此组件负责物品是否可像盔甲一样穿戴，控制了盔甲等装备的行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:equippable：物品被穿戴的行为。 - [图:字符串][图:NBT列表/JSON数组]allowed_entities：（默认为全部生物）可以穿戴此物品的生物。可以为以 ``` # ``` 开头的实体类型标签、一个实体类型ID、或以多个实体类型ID组成的字符串列表。 - [图:字符串]asset_id：（命名空间ID）物品被穿戴时的装备资产。此值不存在时，若装备在头部则根据物品模型渲染物品，否则什么也不会渲染。 - [图:字符串]camera_overlay：（命名空间ID）当此项存在且物品被玩家穿戴时，玩家第一人称视角将渲染指定的纹理遮罩。多个设置此标签的物品遮罩可以互相叠加，按照主手、副手、头盔、胸甲、护腿、靴子的顺序依次渲染。身体和鞍槽位的纹理不会被渲染。当遮罩纹理渲染时，遮罩纹理被视为独立纹理，即无法作为动态纹理或GUI纹理渲染，但可以指定纹理过滤方式。 - [图:布尔型]can_be_sheared：（默认为 ``` false ``` ）满足未被骑乘等其他条件时，玩家是否可以对装备此物品的生物进行修剪来卸下此物品。 - [图:布尔型]damage_on_hurt：（默认为 ``` true ``` ）生物在受到会影响损害盔甲的伤害时此物品是否会受损而减少耐久。 - [图:布尔型]equip_on_interact：（默认为 ``` false ``` ）对生物使用此物品时，是否可以让被交互的生物在允许的空槽位上穿戴此物品。 - [图:字符串][图:NBT复合标签/JSON对象]equip_sound：（默认为 ``` item.armor.equip_generic ``` ）物品被穿戴时的声音。部分生物会对部分部位覆写这一声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:布尔型]dispensable：（默认为 ``` true ``` ）是否可以使用发射器使生物穿戴此物品。如果物品本身有特殊的发射器行为则此项无效。 - [图:字符串][图:NBT复合标签/JSON对象]shearing_sound：（默认为 ``` item.shears.snip ``` ）被玩家使用剪刀卸下此物品时播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串]* *slot：物品可被穿戴的装备槽位。 - [图:布尔型]swappable：（默认为 ``` true ``` ）物品是否可以直接使用穿戴。

## firework_explosion

此组件负责保存烟火之星的数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:firework_explosion：烟火之星的数据。 - [图:整型数组]colors：（默认为空数组）表示爆裂时的粒子颜色，只使用后24位，每个颜色通道占用8位，按RGB依次存储。如果颜色没有对应的染料颜色，游戏将在提示框中显示为“自定义”，但爆裂时会产生正确的颜色。当存在多个值时，每个爆裂粒子在渲染时会随机选择一种颜色用于渲染。不存在或数组为空时被视为黑色。 - [图:整型数组]fade_colors：（默认为空数组）表示爆裂后的淡化粒子颜色，只使用后24位，每个颜色通道占用8位，按RGB依次存储。当存在多个值时，每个爆裂粒子在渲染时会随机选择一种颜色用于渲染。 - [图:布尔型]has_trail：（默认为 ``` false ``` ）表示烟火是否有拖曳痕迹（使用钻石合成时）。 - [图:布尔型]has_twinkle：（默认为 ``` false ``` ）表示烟火是否出现闪烁效果（使用荧石粉合成时）。 - [图:字符串]* *shape：爆裂时的形态。可以为 ``` small_ball ``` （小型球状）、 ``` large_ball ``` （大型球状）、 ``` star ``` （星形）、 ``` creeper ``` （苦力怕状）、 ``` burst ``` （喷发状）。

## fireworks

此组件负责保存烟花火箭的数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:fireworks：烟花火箭的数据。 - [图:字节型]flight_duration：（无符号8位整数，默认为0）烟花火箭的飞行的时间，单位为“火药”（即表现为和在工作台上合成烟花火箭时所用的火药数相等）。 - [图:NBT列表/JSON数组]explosions：（最多256个元素）烟花火箭对应的烟火之星的数据，控制烟花火箭飞行结束时产生的爆裂烟花渲染。 - [图:NBT复合标签/JSON对象]：一个烟火之星的数据。 - [图:整型数组]colors：（默认为空数组）表示爆裂时的粒子颜色，只使用后24位，每个颜色通道占用8位，按RGB依次存储。如果颜色没有对应的染料颜色，游戏将在提示框中显示为“自定义”，但爆裂时会产生正确的颜色。当存在多个值时，每个爆裂粒子在渲染时会随机选择一种颜色用于渲染。不存在或数组为空时被视为黑色。 - [图:整型数组]fade_colors：（默认为空数组）表示爆裂后的淡化粒子颜色，只使用后24位，每个颜色通道占用8位，按RGB依次存储。当存在多个值时，每个爆裂粒子在渲染时会随机选择一种颜色用于渲染。 - [图:布尔型]has_trail：（默认为 ``` false ``` ）表示烟火是否有拖曳痕迹（使用钻石合成时）。 - [图:布尔型]has_twinkle：（默认为 ``` false ``` ）表示烟火是否出现闪烁效果（使用荧石粉合成时）。 - [图:字符串]* *shape：爆裂时的形态。可以为 ``` small_ball ``` （小型球状）、 ``` large_ball ``` （大型球状）、 ``` star ``` （星形）、 ``` creeper ``` （苦力怕状）、 ``` burst ``` （喷发状）。

## food

此组件控制物品被消耗使用后能提供的食物属性。要让物品能被玩家消耗使用，物品需要同时拥有
```
consumable
```

组件。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:food：物品的食物属性。 - [图:布尔型]can_always_eat：（默认为 ``` false ``` ）表示物品是否可以无视当前饥饿值食用。 - [图:整型]* *nutrition：（值≥0）食用物品时增加的饥饿值。 - [图:单精度浮点数]* *saturation：食用物品时增加的饱和度。

示例
给予一个海绵，该海绵可无视饥饿值食用，玩家食用后恢复玩家3点饥饿值和1点饱和度：
```
/
give
 @s sponge[food={can_always_eat:true,nutrition:3,saturation:1},consumable={}]
```

## glider

此组件存在时，物品被穿戴后可以让生物滑翔。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:glider：空标签，此组件存在时若被生物装备则可以滑翔，且滑翔时此物品每1秒消耗1耐久度。

示例
给予一个铁胸甲，穿戴后可以滑翔：
```
/
give
 @s iron_chestplate[glider={}]
```

## instrument

此组件负责保存山羊角的数据。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:instrument：玩家吹奏山羊角时使用的山羊角乐器。命名空间ID或内联定义均可。 - - 山羊角乐器，见Template:Nbt inherit/instrument component/source

## intangible_projectile

此组件负责箭被射出后是否只能被创造模式玩家捡起。默认情况下，只有多重射击的弩额外装填的箭会具有此组件。

此组件会为物品提示框提供内容：“不可回收”。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:intangible_projectile：空标签，此组件存在时若作为箭射出，则射出后只能被创造模式玩家捡起。

## interact_animation

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:interact_animation：使用此物品交互时的动画。 - [图:字符串]type：（默认为 ``` whack ``` ）摇摆动画类型。取值只能为 ``` whack ``` （默认攻击动画）、 ``` stab ``` （矛的戳刺攻击动画，部分人形生物持有时还有戳刺攻击的第三人称手部姿势）。 - [图:整型]duration：（默认为6）动画播放的周期刻数。

## item_model

此组件控制了物品使用的物品模型映射。物品模型映射会根据命名空间ID解析为
```
assets/<
命名空间
>/items/<
路径
>.json
```

。若对应的物品模型映射不存在或无法解析则使用无效模型。此组件不存在时什么也不会渲染。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:item_model：（命名空间ID）为当前物品绑定一个物品模型映射。

## item_name

此组件控制了物品的默认名称。该名称无法通过铁砧修改，不能在物品展示框中显示名称，带有该组件的旗帜在充当地图标记时也不会显示名称。此组件对物品名称的控制等级永远最低，会被其他所有影响物品名称的组件覆盖。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]minecraft:item_name：（文本组件）物品的默认名称。

## jukebox_playable

此组件负责保存音乐唱片的数据。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:jukebox_playable：（命名空间ID）唱片机曲目。此组件存在时物品可插进唱片机中播放。

示例
给予一个可以放进唱片机并播放cat的唱片残片：
```
/
give
 @a minecraft:disc_fragment_5[minecraft:jukebox_playable=cat]
```

## kinetic_weapon

此组件负责决定物品是否可触发冲锋攻击，其也会影响一系列与冲锋攻击判定的行为，部分生物的生物AI和手持物品的动作等。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:kinetic_weapon：设置物品的冲锋攻击。 - [图:整型]delay_ticks：（值≥0，默认为0）武器生效前的时间，单位为游戏刻。 - [图:单精度浮点数]forward_movement：（默认为0）动画期间脱离手的距离。 - [图:单精度浮点数]damage_multiplier：（默认为1）攻击轴相对速度的最终伤害倍率。此处及下文的“攻击轴速度”定义为：上个游戏刻的速度向量（对于玩家）或位置改变量（对于非生物实体，等于[图:NBT列表/JSON数组]Motion）对攻击者视角向量的投影，是一个向量；“攻击轴相对速度”即攻击者攻击轴速度与被攻击者攻击轴速度之差，如果此差值小于0则游戏认为是0。 - [图:字符串][图:NBT复合标签/JSON对象]sound：使用此武器时播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]hit_sound：此武器攻击到生物时播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:NBT复合标签/JSON对象]* *dismount_conditions：将目标强制脱离骑乘的条件。 - [图:整型]* *max_duration_ticks：不再检查条件的时间，单位为刻，从[图:整型]delay_ticks开始计算。 - [图:单精度浮点数]min_speed：（默认为0）攻击者的最低攻击轴速度。对于非玩家实体，实际最小速度为规定值的20%。 - [图:单精度浮点数]min_relative_speed：（默认为0）最小攻击轴相对速度。对于非玩家实体，实际最小速度为规定值的20%。 - [图:NBT复合标签/JSON对象]* *knockback_conditions：将目标击退的条件。 - 格式同[图:NBT复合标签/JSON对象]dismount_conditions。 - [图:NBT复合标签/JSON对象]* *damage_conditions：对目标造成伤害的条件。 - 格式同[图:NBT复合标签/JSON对象]dismount_conditions。 - [图:整型]contact_cooldown_ticks：（值>0，默认为10）攻击的冷却时间，在此时间内无法与任何实体交互。

示例
给予一个可以蓄力攻击的下界合金剑，无法将目标强制脱离骑乘：
```
/
give
 @s minecraft:netherite_sword[minecraft:kinetic_weapon={dismount_conditions:{max_duration_ticks:0},knockback_conditions:{max_duration_ticks:2147483647},damage_conditions:{max_duration_ticks:2147483647}}]
```

## lock

此组件负责保存可上锁的方块实体数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:lock：容器方块的上锁数据。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source

示例
给予一个箱子，此箱子放置后玩家仅能手持名为“密码”的物品来打开它：
```
/
give
 @s chest[lock={components:{custom_name:"密码"}}]
```

## lodestone_tracker

此组件负责保存磁石指针的数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:lodestone_tracker：若指南针拥有此组件，则指南针将变为磁石指针。 - [图:NBT复合标签/JSON对象]target：磁石指针指向的位置。 - [图:字符串]* *dimension：磁石指针指向位置的所在维度。 - [图:整型数组]* *pos：磁石指针指向的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:布尔型]tracked：（默认为 ``` true ``` ）表示磁石指针是否追踪绑定的磁石。为false时，当磁石被破坏后此组件不会被移除，磁石指针仍然指向对应位置。

示例
给予一个指南针，其始终指向主世界X=1、Y=2、Z=3处，无论磁石是否存在：
```
/
give
 @s compass[lodestone_tracker={target:{pos:[I;1,2,3],dimension:"overworld"},tracked:false}]
```

## lore

 “Lore”重定向至此。关于1.20.5前的Lore标签，请见“物品格式/Java版1.20.5前 § 通用标签”。

此组件负责保存物品的自定义提示框描述文本。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:lore：物品的自定义描述信息，共计不允许超过256行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）一行描述信息。

示例
给予一根木棍，描述信息为第一行“Hello Minecraft”、第二行“Hello World”的木棍：
```
/
give
 @s stick[minecraft:lore=["Hello Minecraft", "Hello World"]]
```

## map_color

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

此组件负责保存地图着色层的颜色。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:map_color：（默认为4603950）物品栏内地图纹理上的颜色，在二进制形式下，只使用后24位，每个颜色通道占用8位，按RGB依次存储。

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

## map_decorations

此组件负责保存地图图标，这些图标属于物品数据的一部分，而不是全局地图数据保存的图标。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:map_decorations：地图图标数据。 - [图:NBT复合标签/JSON对象]<图标名称>：一个图标的信息。 - [图:单精度浮点数]* *rotation：图标的旋转角度，按顺时针角度计。游戏并不能真正显示所有角度，每经过22.5°，在地图上才会有区别。与图标纹理中的外观相比，旋转角度为0所显示的图标上下颠倒。 - [图:字符串]* *type：（命名空间ID）此图标显示的地图图标类型。 - [图:双精度浮点数]* *x：图标在世界上所在的X坐标。如果超出地图所展示的范围且图标类型不是玩家，则图标无法添加到地图中。如果图标类型是玩家，位置超出显示范围但地图可以无限追踪玩家，那么图标类型会被修改为 ``` player_off_limits ``` ，且位置会显示在对应边；如果距离显示范围较近，则图标类型会被修改为 ``` player_off_map ``` ，且位置会显示在对应边；如果距离显示范围很远，则移除此图标。 - [图:双精度浮点数]* *z：图标在世界上所在的Z坐标。如果超出地图所展示的范围且图标类型不是玩家，则图标无法添加到地图中。如果图标类型是玩家，位置超出显示范围但地图可以无限追踪玩家，那么图标类型会被修改为 ``` player_off_limits ``` ，且位置会显示在对应边；如果距离显示范围较近，则图标类型会被修改为 ``` player_off_map ``` ，且位置会显示在对应边；如果距离显示范围很远，则移除此图标。

## map_id

此组件负责存储地图编号。具有此组件的所有物品均会尝试读取相应编号的地图内容，且能被玩家展开，在物品展示框上铺开，作为地图被复制、锁定或扩展。提示框中会显示地图的缩放信息等数据。但是，只有地图物品可以主动要求游戏获取地图内容。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:map_id：地图编号。

## max_damage

此组件负责存储物品的最大耐久度，和
```
damage
```

组件一起控制物品能否被损坏。此组件不存在时若物品被损坏则游戏将最大耐久度视为0。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:max_damage：（值>0）物品的最大耐久度。

示例
给予一个耐久上限999点的金剑：
```
/
give
 @s golden_sword[max_damage=999]
```

## max_stack_size

此组件负责物品的最大堆叠数，如果此组件不存在，则视为1。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:max_stack_size：（0≤值≤99）物品的最大堆叠数量。如果此组件不存在，则游戏默认为1。

示例
给予99个最大堆叠99个的雪球：
```
/
give
 @s snowball[max_stack_size=99] 99
```

## minimum_attack_charge

此组件负责玩家使用物品攻击时，需要多少攻击冷却完成度才可发动攻击，此组件不存在时游戏会视为0。

- [图:NBT复合标签/JSON对象]components - [图:单精度浮点数]minecraft:minimum_attack_charge：（0≤值≤1）玩家使用此物品进行近战攻击或穿刺攻击所需要攻击冷却完成度的最小值。若添加了该组件，并且值大于0，则会影响魔咒效果组件 ``` post_piercing_attack ``` 的触发间隔。

## mob_visibility

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:mob_visibility：此物品被装备时对此实体的生物探测半径的范围的影响。 - [图:字符串][图:NBT列表/JSON数组]*targeting_entity_types：受影响的生物。可以是单个实体类型ID、一个实体类型ID的列表或一个实体类型的标签。 - [图:单精度浮点数]*visibility：（0.0≤值≤10.0）对装备了此物品的实体的生物探测半径的影响倍数。即使此值为0.0，最终的生物探测半径也不会小于2格；即使有多个被装备物品同时具有此组件，最终的生物探测半径也不会超过原本的10倍。

## note_block_sound

此组件负责保存玩家的头放置在音符盒上播放的自定义音效。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:note_block_sound：玩家的头被放置在音符盒上时播放的声音。应为一个来自资源包 ``` sounds.json ``` 内定义的声音事件。

示例
给予一个被放在音符盒上时会播放声音“玩家：升级”的玩家的头：
```
/
give
 @s player_head[note_block_sound="entity.player.levelup"]
```

## ominous_bottle_amplifier

控制物品被消耗使用后，玩家获得的不祥之兆状态效果倍率。要让物品能被玩家消耗使用，物品需要同时拥有
```
consumable
```

组件。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:ominous_bottle_amplifier：（0≤值≤4）玩家使用物品后获得的不祥之兆状态效果倍率。

## piercing_weapon

此组件负责物品是否会发动戳刺攻击。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:piercing_weapon：设置物品的戳刺攻击，并使玩家手持此物品时不会触发对方块的破坏行为。该组件也是触发魔咒效果组件 ``` post_piercing_attack ``` 的条件之一。 - [图:字符串][图:NBT复合标签/JSON对象]sound：使用此武器时播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]hit_sound：此武器攻击到生物时播放的声音。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:布尔型]deals_knockback：（默认为 ``` true ``` ）攻击是否造成击退。 - [图:布尔型]dismounts：（默认为 ``` false ``` ）攻击是否将目标强制脱离骑乘。

## pot_decorations

此组件负责保存饰纹陶罐的陶片数据，物品提示框中会显示其合成物品。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:pot_decorations：饰纹陶罐的陶片数据。此列表应仅有四个元素，依次代表饰纹陶罐背面、左面、右面和前面的物品。默认每个面均为红砖。 - [图:字符串]：（命名空间ID）饰纹陶罐这一个面的陶片物品。 - [图:NBT复合标签/JSON对象]minecraft:pot_decorations：饰纹陶罐各个面的陶片物品。如果对应面的物品不存在provides_pottery_pattern组件，则此面在渲染上没有额外样式。 - [图:字符串][图:NBT复合标签/JSON对象]back：背面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]left：左面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]right：右面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:字符串][图:NBT复合标签/JSON对象]front：正面陶片样式。 - - 物品模板，见Template:Nbt inherit/item template/source

## potion_contents

存储药水效果和状态效果信息。影响物品的名称和状态效果，提示框中会显示药水信息。下文的
```
<
药水物品类型
>
```

只对药水、喷溅药水、滞留药水和药箭有效。要让物品能被玩家消耗使用，物品需要同时拥有
```
consumable
```

组件。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:potion_contents：物品的药水和自定义状态效果数据。如果设置此组件为字符串，则等价于只设置复合标签形式中的[图:字符串]potion，游戏在保存时只会保存为复合标签形式。 - [图:整型]custom_color：物品渲染中，药水部分使用的颜色。只使用后24位，每个颜色通道占用8位，按RGB依次存储。 - [图:NBT列表/JSON数组]custom_effects：当前物品所含有的自定义状态效果。 - [图:NBT复合标签/JSON对象]：一项状态效果。 - - 状态效果，见Template:Nbt inherit/effect/source - [图:字符串]custom_name：覆盖物品的默认名称，游戏将以 ``` < 药水物品名称翻译键 >.effect.< 此值 > ``` 翻译键作为物品的名称，对于原版的药水物品而言就是 ``` item.minecraft.< 药水物品类型 >.effect.< 此值 > ``` 。 - [图:字符串]potion：（命名空间ID）药水效果，也会影响物品的名称和纹理。

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

示例
给予一瓶药水，药水颜色为紫色，药水的状态效果为持续1102游戏刻（55.1秒）的122倍率（即123级）的发光效果：
```
/
give
 @s potion[potion_contents={custom_color:8388863,custom_effects:[{amplifier:122,duration:1102,id:"glowing"}]}]
```

## potion_duration_scale

此组件负责
```
potion_contents
```

组件的状态效果的缩放倍率。

- [图:NBT复合标签/JSON对象]components - [图:单精度浮点数]minecraft:potion_duration_scale：（值≥0）控制 ``` potion_contents ``` 组件存储的状态效果时长缩放倍率。此组件不存在时默认为1。

## profile

此组件负责游戏档案数据。任何与游戏档案相关的物品、方块实体和实体均使用此解析方式。

游戏会优先使用玩家档案获取皮肤等数据，然后再根据玩家皮肤指定的纹理模型等进行更改。例如游戏渲染玩家的头
```
player_head[profile={name:"jeb_", texture:"missingno"}]
```

时，会先获取玩家jeb_的皮肤，再使用无效纹理进行覆盖。

如果设置了[图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]properties，则游戏直接使用此游戏档案数据，不会因为对应玩家档案的更改而更改。

在未设置[图:NBT列表/JSON数组][图:NBT复合标签/JSON对象]properties的条件下，如果设置了[图:字符串]name，则游戏会将其视作玩家名称解析游戏档案。如果设置了[图:整型数组]id，则游戏会将其视作UUID解析游戏档案，解析的优先级高于[图:字符串]name。游戏并不会将获取的游戏档案数据存储，而是实时获取，尽管需要客户端重新启动才能更改渲染效果。此时物品提示框也会显示“实时显示”，以与静态游戏档案相区分。

无论是静态档案还是动态档案，只有[图:字符串]name会影响玩家的头的物品名称。

如果设置此组件为字符串，则等价于只设置复合标签形式中的[图:字符串]name，游戏在保存时只会保存为复合标签形式。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:profile：玩家档案数据。 - - 游戏档案，见Template:Nbt inherit/resolvable profile/source

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。MinecraftWiki
游戏档案属性通常包括
```
textures
```

用于保存玩家的皮肤数据。在此属性的数据被Base64解码后具有如下结构：

- [图:NBT复合标签/JSON对象] JSON数据根元素 - [图:字符串]* *profileId：游戏档案的UUID，不带连字符。 - [图:字符串]* *profileName：游戏档案名称。 - [图:布尔型]signatureRequired：代表此纹理属性是否已被签名。如果[图:字符串]signature存在，则此项也存在并为true。 - [图:NBT复合标签/JSON对象]* *textures：纹理数据。 - [图:NBT复合标签/JSON对象]CAPE：披风纹理。如果此游戏档案不包含披风，此项不存在。 - [图:字符串]* *url：披风纹理的URL链接。 - [图:NBT复合标签/JSON对象]SKIN：皮肤纹理。如果此游戏档案不包含自定义皮肤，此项不存在。 - [图:NBT复合标签/JSON对象]metadata：皮肤的元数据。 - [图:字符串]model：固定值 ``` slim ``` 。当皮肤模型手臂为3像素时存在，否则不存在。 - [图:字符串]* *url：皮肤纹理的URL链接。 - [图:整型]* *timestamp：Unix时间戳，以毫秒为单位，时间为请求玩家游戏档案数据的时间。

## provides_banner_patterns

此组件负责物品被置于织布机旗帜图案槽位时提供的旗帜图案。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:provides_banner_patterns：控制物品能否放进织布机的旗帜图案槽位，以及可以制作的图案。可以为一个旗帜图案ID、一个旗帜图案标签，或一个旗帜图案ID的列表。

## provides_pottery_pattern

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此组件负责存储物品的陶片样式，影响饰纹陶罐的渲染。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:provides_pottery_pattern：（命名空间ID）饰纹陶罐图案。游戏在渲染饰纹陶罐时，会读取 ``` pot_decorations ``` 组件内部物品的此组件来决定渲染样式。

## provides_trim_material

此组件负责物品被作为锻造原材料时提供的盔甲纹饰材料。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:provides_trim_material：控制物品在锻造台上使用盔甲纹饰配方时为输出物品提供的盔甲纹饰材料。命名空间ID或内联定义均可。 - - 纹饰材料，见Template:Nbt inherit/trim material/source

## rarity

此组件负责物品的基础稀有度。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:rarity：物品的基础稀有度。可以为 ``` common ``` （常见）、 ``` uncommon ``` （少见）、 ``` rare ``` （稀有）、 ``` epic ``` （史诗）。

## recipes

此组件负责知识之书的数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:recipes：知识之书保存的配方数据。 - [图:字符串]：（命名空间ID）一个配方ID。

## repair_cost

此组件负责保存物品在铁砧操作中的累计惩罚。

- [图:NBT复合标签/JSON对象]components - [图:整型]minecraft:repair_cost：（值≥0）物品在铁砧上修理、合并或重命名时在基础经验等级消耗之上额外增加的累积惩罚。

示例
给予当前实体一个累计惩罚值为30的下界合金剑：
```
/
give
 @s netherite_sword[repair_cost=30]
```

## repairable

此组件负责物品可使用何种物品在铁砧上进行原料修复。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:repairable：物品被铁砧进行原材料修复的有效物品。不论此值为何，物品永远可以被合并物品修复。 - [图:字符串][图:NBT列表/JSON数组]* *items：可用于修复的物品。可以为一个 ``` # ``` 开头的物品标签、一个物品ID、或一个物品ID的列表。

示例
给予当前实体一个只能被橡木木板或下界合金剑修复的下界合金剑：
```
/
give
 @s netherite_sword[repairable={items:"oak_planks"}]
```

## sign_text_front 和 sign_text_back

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:sign_text_front：存储告示牌和悬挂式告示牌正面的文本。 - [图:NBT列表/JSON数组]*messages：告示牌或悬挂式告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌或悬挂式告示牌内的一行文字。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌或悬挂式告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。如果存在，则必须和[图:NBT列表/JSON数组]messages具有一样多的元素。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌或悬挂式告示牌内的一行文字。 - [图:字符串]color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:布尔型]has_glowing_text：（默认为 ``` false ``` ）表示文字是否发光。 - [图:NBT复合标签/JSON对象]minecraft:sign_text_back：存储告示牌和悬挂式告示牌背面的文本。 - [图:NBT列表/JSON数组]*messages：告示牌或悬挂式告示牌的文字，共含有四个元素，代表了文字的第一到第四行。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌或悬挂式告示牌内的一行文字。 - [图:NBT列表/JSON数组]filtered_messages：被过滤的告示牌或悬挂式告示牌的文字，共含有四个元素，代表了被过滤文字的第一到第四行。当文本没有被过滤时此项不存在。如果存在，则必须和[图:NBT列表/JSON数组]messages具有一样多的元素。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）告示牌或悬挂式告示牌内的一行文字。 - [图:字符串]color：文字的颜色。此项不存在或无效时游戏默认为 ``` black ``` （黑色）。 - [图:布尔型]has_glowing_text：（默认为 ``` false ``` ）表示文字是否发光。

## sulfur_cube_content

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:sulfur_cube_content：表示硫方怪吸收的物品。 - - 物品模板，见Template:Nbt inherit/item template/source

## suspicious_stew_effects

存储谜之炖菜的状态效果信息。要让物品能被玩家消耗使用，物品需要同时拥有
```
consumable
```

组件。

- [图:NBT复合标签/JSON对象]components - [图:NBT列表/JSON数组]minecraft:suspicious_stew_effects：谜之炖菜的状态效果信息。 - [图:NBT复合标签/JSON对象]：一项状态效果信息。 - [图:整型]duration：（默认为160）状态效果的时长，单位为刻。 - [图:字符串]* *id：（命名空间ID）状态效果。

## swing_animation

本段落包含会在下一次更新中移除的内容。
这些特性在Java版26.3的开发版本中移除。

此组件负责物品的挥动动画。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:swing_animation：使用此物品攻击时的动画。 - [图:字符串]type：（默认为 ``` whack ``` ）摇摆动画类型。取值只能为 ``` none ``` （切换物品时的垂直移动动画，玩家第三人称下为轻微水平摇摆）、 ``` whack ``` （默认攻击动画）、 ``` stab ``` （矛的戳刺攻击动画，部分人形生物持有时还有戳刺攻击的第三人称手部姿势）。 - [图:整型]duration：（默认为6）动画播放的周期刻数。

## tool

此组件负责物品作为挖掘工具的行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:tool：物品的挖掘工具属性。 - [图:布尔型]can_destroy_blocks_in_creative：（默认为 ``` true ``` ）创造模式玩家能否使用此物品破坏方块。 - [图:整型]damage_per_block：（值≥0，默认为1）破坏硬度非0的方块时物品损失的耐久度。 - [图:单精度浮点数]default_mining_speed：（值≥0，默认为1）挖掘方块时的速度。 - [图:NBT列表/JSON数组]* *rules：物品与对应可以挖掘的方块的映射列表。 - [图:NBT复合标签/JSON对象]：一项物品与方块列表的挖掘配置数据。 - [图:字符串][图:NBT列表/JSON数组]* *blocks：此配置指定的有效方块。可以为一个 ``` # ``` 开头的方块标签、一个方块ID、或一个方块ID的列表。 - [图:布尔型]correct_for_drops：此物品是否是所有上方指定方块的合适挖掘工具。 - [图:单精度浮点数]speed：覆盖所有上方指定方块的使用此物品挖掘时的挖掘速度。

示例
给予一把木锹，且这把木锹属于石头的适合挖掘工具：
```
/
give
 @s wooden_shovel[tool={rules:[{blocks:["stone"],correct_for_drops:True}]}]
```

## tooltip_display

此组件控制由组件产生的提示框文本可见性和提示框可见性。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:tooltip_display：物品提示框的显示数据。 - [图:布尔型]hide_tooltip：（默认为 ``` false ``` ）物品提示框是否总是隐藏。 - [图:NBT列表/JSON数组]hidden_components：（默认为空列表）一个物品组件ID列表，列表内的所有组件提供的提示框文本都会被隐藏。如果组件不提供提示框文本，则对其没有效果。 - [图:字符串]：（命名空间ID）一个物品组件。

示例
给予一个不显示提示框的金斧：
```
/
give
 @s golden_axe[tooltip_display={hide_tooltip:true}]
```

## tooltip_style

此组件负责物品的提示框外观。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:tooltip_style：（命名空间ID）物品提示框外观。提示框外观分为两部分：背景由 ``` < 命名空间 >:tooltip/< 路径 >_background ``` 精灵图渲染，边框由 ``` < 命名空间 >:tooltip/< 路径 >_frame ``` 精灵图渲染。这两个精灵图都属于GUI纹理，默认会被解析为 ``` assets/< 命名空间 >/textures/gui/sprites/tooltip/< 路径 >_background.png ``` 和 ``` assets/< 命名空间 >/textures/gui/sprites/tooltip/< 路径 >_frame.png ``` 。

## trim

此组件负责保存物品的盔甲纹饰数据。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:trim：物品的盔甲纹饰信息。 - [图:字符串][图:NBT复合标签/JSON对象]* *material：此盔甲纹饰的材料，命名空间ID或内联定义均可。 - - 纹饰材料，见Template:Nbt inherit/trim material/source - [图:字符串][图:NBT复合标签/JSON对象]* *pattern：此盔甲纹饰的图案，命名空间ID或内联定义均可。 - - 纹饰图案，见Template:Nbt inherit/trim pattern/source

## unbreakable

此组件存在时，物品没有耐久度属性，不会减少耐久度，提示框中会显示“无法破坏”。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:unbreakable：空标签，此组件存在时物品无法破坏，不存在耐久度。

示例
给予一把无法破坏的钻石镐：
```
/
give
 @s diamond_pickaxe[unbreakable={}]
```

## use_cooldown

此组件负责物品的使用冷却行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:use_cooldown：设置物品的使用冷却行为。冷却时间会作用在一个“冷却组”上。 - [图:字符串]cooldown_group：（命名空间ID）设置物品冷却组。同冷却组的物品会同时受到同一个物品冷却影响，在冷却时间内所有同冷却组的物品都无法使用。如果此值不存在，游戏将以物品的命名空间ID作为冷却组ID使用。 - [图:单精度浮点数]* *seconds：（值>0）物品使用后的冷却时间，单位为秒。

示例
给予16个每使用一次冷却一秒的雪球：
```
/
give
 @s snowball[use_cooldown={seconds:1}] 16
```

## use_effects

此组件负责使用物品时的部分行为。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:use_effects：设置物品被使用时的部分行为。 - [图:布尔型]can_sprint：（默认为 ``` false ``` ）玩家在使用此物品时是否可以疾跑。 - [图:布尔型]interact_vibrations：（默认为 ``` true ``` ）生物使用此物品时是否会发出 ``` item_interact_finish ``` 和 ``` item_interact_start ``` 游戏事件。此值为 ``` false ``` 或者此组件不存在时使用此物品不会发出这两个游戏事件。 - [图:单精度浮点数]speed_multiplier：（0≤值≤1，默认为0.2）玩家使用此物品时的速度倍率。

## use_remainder

此组件负责物品被消耗使用后返还的物品。

- [图:NBT复合标签/JSON对象]components - [图:字符串][图:NBT复合标签/JSON对象]minecraft:use_remainder：控制物品在消耗使用且物品数量减少后游戏返还的物品。如果玩家物品栏在欲返还物品时已满，则掉落成为物品实体。 - - 物品模板，见Template:Nbt inherit/item template/source

示例
给予16个能在使用后返回1个普通雪球的雪球：
```
/
give
 @s snowball[use_remainder={id:"snowball"}] 16
```

## villager_food

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:villager_food：物品作为村民的食物时的行为。 - [图:整型]*nutrition：（值≥0）此物品提供的食物点数，也即村民消耗该物品后增加的食物等级。

## waxed

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

此段落仍需完善。
你可以帮助我们加入更多信息。
说明：补充简介与示例

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:waxed：空标签，此组件存在时表示物品被涂蜡。

## weapon

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:weapon：设置物品的武器数据。此组件存在时物品使用次数统计信息会在用此物品攻击时增加。 - [图:单精度浮点数]disable_blocking_for_seconds：（值≥0，默认为0）攻击成功禁用目标盾牌的秒数。 - [图:整型]item_damage_per_attack：（值≥0，默认为1）每次攻击对此物品造成的损伤值，即损耗的耐久度。

示例
给予一个下界合金剑，当攻击成功时禁用目标盾牌60秒，且每次攻击损耗0耐久度：
```
/
give
 @s netherite_sword[weapon={disable_blocking_for_seconds:60,item_damage_per_attack:0}]
```

## writable_book_content

存储书与笔的数据。当玩家使用拥有此组件的书与笔或成书时会显示编辑界面，在讲台上打开拥有此组件的任意物品时游戏会显示每页的文本信息。此组件的优先级低于
```
written_book_content
```

组件。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:writable_book_content：书与笔的数据。 - [图:NBT列表/JSON数组]pages：（最多100个元素）书与笔内存储的页信息，必须为以下格式之一。 - [图:字符串]：（长度不超过1024）书与笔内一页的文本信息。如果开启过滤，则代表文本信息与原信息一致。 - [图:NBT复合标签/JSON对象]：书与笔内一页的信息。 - [图:字符串]filtered：（长度不超过1024）已过滤的文本信息。在开启过滤时，此字符串的优先级高于原始文本。被开启过滤的玩家更新时会删除原始文本并将此过滤文本作为原始文本，而被未开启过滤的玩家更新时会被移除。 - [图:字符串]* *raw：（长度不超过1024）未过滤的文本原始信息。

## written_book_content

存储成书的数据。当玩家使用拥有此组件的书与笔或成书，或在讲台上打开拥有此组件的任意物品时游戏会显示每页的文本信息。此组件的
```
title
```

字段也被视为物品的自定义名称。

所有拥有此组件的物品可以使用成书复制配方在工作台上进行复制。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:written_book_content：成书的数据。 - [图:字符串]* *author：成书的作者。 - [图:整型]generation：（默认为 ``` 0 ``` ）决定成书的复制程度。可以为 ``` 0 ``` （原稿）， ``` 1 ``` （原稿的副本）， ``` 2 ``` （副本的副本）， ``` 3 ``` （破烂不堪）。 - [图:NBT列表/JSON数组]pages：成书内存储的页信息，必须使用以下格式之一。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：（文本组件）成书内一页的信息。如果开启过滤，则代表过滤后文本信息与原信息一致。 - [图:NBT复合标签/JSON对象]：成书页内信息的另一种格式。如果采用复合标签定义文本组件，则只要存在 ``` raw ``` 字段就会以此格式解析。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]filtered：（文本组件）已过滤的文本信息。在开启过滤时，此文本的优先级高于原始文本。被开启过滤的玩家更新时会删除原始文本并将此过滤文本作为原始文本，而被未开启过滤的玩家更新时会被移除。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *raw：（文本组件）未过滤的原始信息。 - [图:布尔型]resolved：（默认为 ``` false ``` ）表示这本成书是否已经被解析，决定是否在打开成书时进行成书内文本的解析。 - [图:字符串][图:NBT复合标签/JSON对象]* *title：（长度不超过32）成书的标题信息。为[图:字符串]格式时，如果开启过滤，则代表此标题过滤后与原标题一致。 - [图:字符串]filtered：（长度不超过32）已过滤的标题信息。在开启过滤时，此字符串优先级高于[图:字符串]raw。 - [图:字符串]* *raw：（长度不超过32）未过滤的标题原始信息。

## 实体变种组件

这些数据组件都可以作为实体组件，且专用于控制实体变种。若物品可以生成对应的实体（例如刷怪蛋、鸡蛋、画等）则使用这些物品生成实体时会生成指定的变种。例如，若棕色鸡蛋的
```
chicken/variant
```

组件值为
```
minecraft:cold
```

，则投掷后会生成寒带鸡而不是热带鸡。

### axolotl/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:axolotl/variant：美西螈的变种。取值只能为 ``` lucy ``` （粉红色）、 ``` wild ``` （棕色）、 ``` gold ``` （金色）、 ``` cyan ``` （青色）或 ``` blue ``` （蓝色）。

### cat/collar

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cat/collar：猫的项圈颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### cat/sound_variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cat/sound_variant：（命名空间ID）猫的音效变种。

### cat/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cat/variant：（命名空间ID）猫的变种。

### chicken/sound_variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:chicken/sound_variant：（命名空间ID）鸡的音效变种。

### chicken/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:chicken/variant：（命名空间ID）鸡的变种。

### cow/sound_variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cow/sound_variant：（命名空间ID）牛的音效变种。

### cow/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cow/variant：（命名空间ID）牛的变种。

### cushion/color

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:cushion/color：坐垫的颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### fox/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:fox/variant：狐狸的变种。取值只能为 ``` red ``` （红色）、 ``` snow ``` （白色）。

### frog/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:frog/variant：（命名空间ID）青蛙的变种。

### horse/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:horse/variant：马的基础毛色。取值只能为 ``` white ``` （白色）、 ``` creamy ``` （奶油色）、 ``` chestnut ``` （栗色）、 ``` brown ``` （褐色）、 ``` black ``` （黑色）、 ``` gray ``` （灰色）或 ``` dark_brown ``` （深褐色）。

### llama/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:llama/variant：羊驼的变种。取值只能为 ``` creamy ``` （沙褐色）、 ``` white ``` （白色）、 ``` brown ``` （棕色）或 ``` gray ``` （灰色）。行商羊驼也使用此组件。

### mooshroom/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:mooshroom/variant：哞菇的变种。取值只能为 ``` red ``` （红色）或 ``` brown ``` （棕色）。

### painting/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:painting/variant：（命名空间ID）画的变种。

### parrot/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:parrot/variant：鹦鹉的变种。取值只能为 ``` red_blue ``` （红色）、 ``` blue ``` （蓝色）、 ``` green ``` （绿色）、 ``` yellow_blue ``` （青色）或 ``` gray ``` （灰色）。

### pig/sound_variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:pig/sound_variant：（命名空间ID）猪的音效变种。

### pig/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:pig/variant：（命名空间ID）猪的变种。

### rabbit/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:rabbit/variant：兔子的变种。取值只能为 ``` brown ``` （褐色）、 ``` white ``` （白色）、 ``` black ``` （黑色）、 ``` white_splotched ``` （黑白相间）、 ``` gold ``` （金色）、 ``` salt ``` （胡椒盐色）或 ``` evil ``` （杀手兔）。

### salmon/size

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:salmon/size：鲑鱼的体型尺寸。取值只能为 ``` small ``` （小型）、 ``` medium ``` （中型）或 ``` large ``` （大型）。

### sheep/color

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:sheep/color：绵羊的毛色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### shulker/color

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:shulker/color：潜影贝的外壳颜色，如果此组件不存在，则潜影贝使用默认的颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### tropical_fish/base_color

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:tropical_fish/base_color：热带鱼的基础颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### tropical_fish/pattern

此组件会为物品提示框提供内容：根据其他热带鱼相关的组件，显示热带鱼变种信息。

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:tropical_fish/pattern：热带鱼的花纹类型。取值只能为 ``` kob ``` （石首类）、 ``` sunstreak ``` （日纹类）、 ``` snooper ``` （窥伺类）、 ``` dasher ``` （速跃类）、 ``` brinely ``` （咸水类）、 ``` spotty ``` （多斑类）、 ``` flopper ``` （飞翼类）、 ``` stripey ``` （条纹类）、 ``` glitter ``` （闪鳞类）、 ``` blockfish ``` （方身类）、 ``` betty ``` （背蒂类）或 ``` clayfish ``` （陶鱼类）。

### tropical_fish/pattern_color

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:tropical_fish/pattern_color：热带鱼的花纹颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### villager/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:villager/variant：（命名空间ID）村民类型，取值可以为 ``` desert ``` （沙漠）、 ``` jungle ``` （丛林）、 ``` plains ``` （默认）、 ``` savanna ``` （热带草原）、 ``` snow ``` （雪原）、 ``` swamp ``` （沼泽）和 ``` taiga ``` （针叶林）。

### wolf/collar

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:wolf/collar：狼的项圈颜色。取值为染料颜色，即 ``` white ``` 、 ``` orange ``` 、 ``` magenta ``` 、 ``` light_blue ``` 、 ``` yellow ``` 、 ``` lime ``` 、 ``` pink ``` 、 ``` gray ``` 、 ``` light_gray ``` 、 ``` cyan ``` 、 ``` purple ``` 、 ``` blue ``` 、 ``` brown ``` 、 ``` green ``` 、 ``` red ``` 或 ``` black ``` 。

### wolf/sound_variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:wolf/sound_variant：（命名空间ID）狼的音效变种。

### wolf/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:wolf/variant：（命名空间ID）狼的变种。

### zombie_nautilus/variant

- [图:NBT复合标签/JSON对象]components - [图:字符串]minecraft:zombie_nautilus/variant：（命名空间ID）僵尸鹦鹉螺的变种。

## 临时组件

这些数据组件仅网络同步，不会被保存也不会被加载。玩家只能判断组件是否存在，而不能主动设置或获取其组件信息。

### additional_trade_cost

村民生成交易时收购物品的基础增加量，当交易选项生成时会立刻被移除。

同步格式

- - [图:整型]minecraft:additional_trade_cost：村民收购物品的增加量。

### creative_slot_lock

阻止玩家在物品栏内与此物品交互。默认附加到创造模式物品栏“已保存的快捷栏”中表示此快捷栏未保存的纸上。

同步格式

- - [图:NBT复合标签/JSON对象]minecraft:creative_slot_lock：空标签，此组件存在时此物品若在创造模式物品栏内则玩家无法与其交互。

### map_post_processing

同步地图的缩放等级和锁定信息。默认附加到进行地图缩小或地图锁定操作的制图台的输出槽位或进行地图缩小配方的工作台的输出槽位的物品上，暂时提供输出物品的地图缩放信息或锁定信息。当物品从输出槽位取下时其组件会被立刻移除。

同步格式

- - [图:整型]minecraft:map_post_processing：为0时使 ``` map_id ``` 组件额外增加“已锁定”行；为1时使 ``` map_id ``` 组件使用“[图:字节型]scale+1”而不是[图:字节型]scale显示地图比例缩放信息。

# 历史

## 已移除的组件

### fire_resistant

控制物品是否无法在熔岩或火中燃烧，且装备时是否不会因为受到火焰伤害而消耗耐久度。

此组件已被
```
damage_resistant
```

组件替代。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:fire_resistant：空标签，此组件存在时物品不受火焰伤害影响。

### hide_additional_tooltip

隐藏物品的提示框文本信息。部分由组件产生的提示框文本由对应组件的[图:布尔型]show_in_tooltip决定。

此组件已被
```
tooltip_display
```

组件替代。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:hide_additional_tooltip：空标签，此组件存在时提示框不会显示附加信息。

### hide_tooltip

隐藏物品的提示框。

此组件已被
```
tooltip_display
```

组件替代。

- [图:NBT复合标签/JSON对象]components - [图:NBT复合标签/JSON对象]minecraft:hide_tooltip：空标签，此组件存在时不会渲染提示框。

# 参考

1. ↑ Minecraft Snapshot 24w39a — Minecraft.net。
1. ↑ Minecraft Snapshot 24w09a — Minecraft.net。
1. ↑ MC-269629 — 漏洞状态为“不予修复”。
1. ↑ MC-269631 — 漏洞状态为“不予修复”。
1. ↑ MC-269655 — 漏洞状态为“不予修复”。
1. ↑ MC-269640 — 漏洞状态为“不予修复”。
1. ↑ MC-269648 — 漏洞状态为“不予修复”。
1. ↑ MC-269658 — 漏洞状态为“不予修复”。
1. ↑ MC-269722 — 漏洞状态为“不予修复”。
1. ↑ MC-269723 — 漏洞状态为“不予修复”。
1. ↑ MC-268510 — 漏洞状态为“已修复”。
1. ↑ MC-269677 — 漏洞状态为“已修复”。
1. ↑ MC-269983 — 漏洞状态为“已修复”。
1. ↑ MC-275917 — 漏洞状态为“已修复”。

# 导航

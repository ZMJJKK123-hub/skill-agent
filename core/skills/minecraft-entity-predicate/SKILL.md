---
name: minecraft-entity-predicate
description: |
  实体谓词（Minecraft Wiki 中文版全量正文）。
  
  【概述】实体谓词（Entity predicate）是一种关于实体的谓词，用于判定某个实体是否满足条件，在进度准则等中使用。
  
  【涵盖内容】
  - entity_type
  - location
  - stepping_on
  - movement_affected_by
  - distance
  - movement
  - effects
  - nbt
  - flags
  - equipment
  - periodic_tick
  - vehicle
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 实体谓词 的完整规范时
---

本条目所述内容仅适用于Java版。

实体谓词（Entity predicate）是一种关于实体的谓词，用于判定某个实体是否满足条件，在进度准则等中使用。

# 数据格式

类似于数据组件映射，实体谓词的结构为多个“实体子谓词-值”的映射。即：

- [图:NBT复合标签/JSON对象] 实体谓词根节点 - [图:任意类型]<实体子谓词类型>：要检查的内容。

目前游戏中有下列实体子谓词：

以下为总格式预览。

- [图:NBT复合标签/JSON对象] 实体谓词根节点 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## entity_type

检查实体的实体类型。

- - [图:字符串][图:NBT复合标签/JSON对象]minecraft:entity_type：要检查的实体类型。可以为单个实体类型ID、一个实体类型ID的列表或一个带 ``` # ``` 前缀的实体类型标签。若指定的实体类型包含待检查实体的实体类型，则检查成功。

## location

检查实体所在的位置。

- - [图:NBT复合标签/JSON对象]minecraft:location：检查实体所在的位置。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source

## stepping_on

检查实体站立的位置。

- - [图:NBT复合标签/JSON对象]minecraft:stepping_on：检查实体脚下站立的位置。如果实体没有站在某个平面上则直接检查失败。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source

## movement_affected_by

检查影响实体运动的位置。

- - [图:NBT复合标签/JSON对象]minecraft:movement_affected_by：检查影响实体移动速度的方块位置，此位置最低不超过实体位置0.5格以下。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source

## distance

检查实体到执行位置的距离。

- - [图:NBT复合标签/JSON对象]minecraft:distance：检查实体到执行位置的距离。执行位置在伤害来源谓词中为对应的实体的位置，在进度中为玩家的位置，在其他场景中检查会直接失败。 - - 距离谓词，见Template:Nbt inherit/distance predicate/source

## movement

检查实体的运动状况。

- - [图:NBT复合标签/JSON对象]minecraft:movement：检查实体的运动状况，所有速度单位均为米每秒。 - [图:双精度浮点数][图:NBT复合标签/JSON对象]fall_distance：检查摔落高度。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]horizontal_speed：检查水平速度分量。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]speed：检查速度。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]vertical_speed：检查垂直速度分量绝对值。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]x：检查X轴运动向量分量。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]y：检查Y轴运动向量分量。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]z：检查Z轴运动向量分量。匹配一个精确值，或者检测数值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source

## effects

检查实体的状态效果。

- - [图:NBT复合标签/JSON对象]minecraft:effects：检查实体的状态效果。 - - 状态效果谓词，见Template:Nbt inherit/mob effects predicate/source

## nbt

检查实体的NBT数据。

- - [图:字符串][图:NBT复合标签/JSON对象]minecraft:nbt：匹配实体的任意NBT数据。可以为复合标签或字符串包裹的SNBT，格式参见NBT格式 § 测试NBT标签和NBT格式 § 转换。

## flags

检查实体的某些特质，其也被称为标志谓词。

- - [图:NBT复合标签/JSON对象]minecraft:flags：检查实体特质。 - [图:布尔型]is_baby：检查该实体是否是幼体。如果该实体是盔甲架，则以是否是小型盔甲架来判断。 - [图:布尔型]is_flying：检查该实体是否正在飞行。 - [图:布尔型]is_on_ground：检查该实体是否正立在地面上。 - [图:布尔型]is_on_fire：检查该实体是否正在着火。 - [图:布尔型]is_sneaking：检查该实体是否正在潜行。 - [图:布尔型]is_sprinting：检查该实体是否正在疾跑。 - [图:布尔型]is_swimming：检查该实体是否正在游泳。 - [图:布尔型]is_in_water：检查该实体是否正在接触水。对气泡柱等方块也有效。 - [图:布尔型]is_fall_flying：检查该实体是否正在用鞘翅滑翔。

## equipment

检查实体装备槽位内的物品。

- - [图:NBT复合标签/JSON对象]minecraft:equipment：检查实体身上的装备。 - [图:NBT复合标签/JSON对象]body：检查动物身体槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]chest：检查胸甲槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]feet：检查靴子槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]head：检查头盔槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]legs：检查护腿槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]mainhand：检查主手槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象]offhand：检查副手槽位物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source

## periodic_tick

约束实体检查成功的频率。

- - [图:整型]minecraft:periodic_tick：（值≥0，单位为刻）根据实体已经加载的时间，以此值为周期，一个周期内只可能检查成功一次。

## vehicle

检查实体的坐骑。

- - [图:NBT复合标签/JSON对象]minecraft:vehicle：检查此实体正在骑乘的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## passenger

检查实体的乘客。

- - [图:NBT复合标签/JSON对象]minecraft:passenger：检查正在骑乘此实体的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## targeted_entity

检查实体正要瞄准攻击的实体。

- - [图:NBT复合标签/JSON对象]minecraft:targeted_entity：检查实体正要瞄准攻击的实体。如果本实体不是除玩家、玩家模型和盔甲架外的生物，或不存在攻击目标，则检查直接失败。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## team

检查实体的队伍。

- - [图:字符串]minecraft:team：检查实体属于的队伍。

## slots

检查实体某个槽位范围内的物品。

- - [图:NBT复合标签/JSON对象]minecraft:slots：检查实体某些槽位内的物品。 - [图:NBT复合标签/JSON对象]<槽位范围>：检查对应槽位范围内的物品。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source

## components

检查实体的数据组件。

- - [图:NBT复合标签/JSON对象]minecraft:components：检查实体的数据组件。当从实体获取的组件内容与检测内容完全相同时测试成功。 - [图:任意类型]<数据组件ID>：一项组件及检测内容。

## predicates

测试实体的数据组件是否满足某项条件。

- - [图:NBT复合标签/JSON对象]minecraft:predicates：检查实体的某个数据组件是否满足某种条件。 - [图:任意类型]<数据组件谓词类型ID>：一个组件的检查。具体格式详见数据组件谓词。

## entity_tags

检查实体的计分板标签。

- - [图:NBT复合标签/JSON对象]minecraft:entity_tags：检查实体的记分板标签。 - [图:NBT列表/JSON数组]any_of：如果指定，则要匹配的实体必须至少有其中一个标签。 - [图:字符串]：一个字符串，表示要测试的实体标签。 - [图:NBT列表/JSON数组]all_of：如果指定，则要匹配的实体必须有其中的全部标签。 - [图:字符串]：一个字符串，表示要测试的实体标签。 - [图:NBT列表/JSON数组]none_of：如果指定，则要匹配的实体必须不具有其中任何一个标签。 - [图:字符串]：一个字符串，表示要测试的实体标签。

## type_specific/lightning

闪电束谓词，检查闪电束。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/lightning：检查闪电束。如果实体不是闪电束则检查直接失败。 - [图:整型][图:NBT复合标签/JSON对象]blocks_set_on_fire：检查被该闪电束点燃的方块数。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]entity_struck：检查被该闪电束击中的实体。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## type_specific/fishing_hook

浮漂谓词，检查浮漂。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/fishing_hook：检查浮漂。 - [图:布尔型]in_open_water：检查浮漂是否位于开阔水域。如果实体不是浮漂，则检查失败。

## type_specific/player

玩家谓词，检查玩家。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/player：检查玩家。如果实体不是玩家则检查直接失败。 - [图:整型][图:NBT复合标签/JSON对象]level：检查玩家的经验等级。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]food：食物谓词，检查玩家的食物数据。 - [图:整型][图:NBT复合标签/JSON对象]level：检查玩家的饥饿度等级。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:双精度浮点数][图:NBT复合标签/JSON对象]saturation：检查玩家的饱和度。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:NBT列表/JSON数组]gamemode：检查玩家的游戏模式，当玩家当前的游戏模式在此列表中时测试成功。 - [图:字符串]：一个游戏模式。必须是 ``` survival ``` （生存模式）、 ``` adventure ``` （冒险模式）、 ``` creative ``` （创造模式）或 ``` spectator ``` （旁观模式）。 - [图:NBT列表/JSON数组]stats：检查玩家的统计信息。 - [图:NBT复合标签/JSON对象]：要检查的一项统计。统计类型与统计名称的取值及意义参见统计信息 § 命名空间ID。 - [图:字符串]*type：统计类型。 - [图:字符串]*stat：统计名称。 - [图:整型][图:NBT复合标签/JSON对象]value：检查此项统计的值。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]recipes：检查玩家获得的配方。 - [图:布尔型]<配方ID>：检查玩家是否获得此配方。 - [图:NBT复合标签/JSON对象]advancements：匹配玩家获得的进度。 - [图:布尔型][图:NBT复合标签/JSON对象]<进度ID>：可以为[图:布尔型]布尔值以直接检查此进度是否获得，也可以为[图:NBT复合标签/JSON对象]对象格式检查此进度内部准则的达成情况。 - [图:布尔型]<进度准则ID>：检查此项进度准则是否已达成。 - [图:NBT复合标签/JSON对象]looking_at：检查玩家正在观察的实体，需要其可见且在100个方块内。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source - [图:NBT复合标签/JSON对象]input：检查玩家是否按下相应的控制按键。 - [图:布尔型]forward：向前移动。 - [图:布尔型]backward：向后移动。 - [图:布尔型]left：向左移动。 - [图:布尔型]right：向右移动。 - [图:布尔型]jump：跳跃。 - [图:布尔型]sneak：潜行。 - [图:布尔型]sprint：疾跑。

## type_specific/cube_mob

史莱姆谓词，检查史莱姆、岩浆怪和硫方怪的部分信息。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/cube_mob：检查史莱姆、岩浆怪或硫方怪。如果实体不是上述实体则检查直接失败。 - [图:整型][图:NBT复合标签/JSON对象]size：检查史莱姆或岩浆怪的大小。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source

## type_specific/raider

袭击者谓词，检查袭击者的部分信息。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/raider：检查袭击者（卫道士、唤魔者、幻术师、掠夺者、女巫或劫掠兽）。如果实体不属于上述实体则检查直接失败。 - [图:布尔型]has_raid：（默认为false）检查袭击者是否正处于一场袭击中。 - [图:布尔型]is_captain：（默认为false）检查袭击者是否是袭击队长。

## type_specific/sheep

绵羊谓词，检查绵羊的部分信息。

- - [图:NBT复合标签/JSON对象]minecraft:type_specific/sheep：检查绵羊。如果实体不是绵羊则检查直接失败。 - [图:布尔型]sheared：检查绵羊是否已被修剪羊毛。

# 历史

# 导航

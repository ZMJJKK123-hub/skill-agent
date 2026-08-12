---
name: minecraft-predicate
description: |
  谓词（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是用于战利品表等的单独的技术性JSON文件。关于更多谓词，请见“谓词（消歧义）”。
  
  【涵盖内容】
  - 文件夹结构
  - 文件格式
  - 通过命令
  - 通过其他战利品表谓词
  - 通过其他文件中的战利品表谓词
  - 加载
  - all_of
  - any_of
  - block_state_property
  - damage_source_properties
  - enchantment_active_check
  - entity_properties
  
  【关键定义】
  - 数据包路径：data/1/爆炸半径
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 谓词 的完整规范时
---

本条目介绍的是用于战利品表等的单独的技术性JSON文件。关于更多谓词，请见“谓词（消歧义）”。

本条目所述内容仅适用于Java版。

谓词（Predicate）也即战利品表谓词（Loot Predicate），用于判定某些对象或参数是否满足某种特性或条件。在数据包中，谓词可通过位于
```
data/<
命名空间
>/predicate/
```

下的JSON文件来定义，下文称此类文件为谓词文件。

# 定义

玩家可通过向数据包添加谓词文件等方式来定义谓词，从而在命令中利用所定义的谓词进行较复杂的逻辑判断。

## 文件夹结构

以下为包含谓词的数据包文件夹结构（尖括号仅用于指示文件或目录名的大致含义）：

- [图:File archive.png：Minecraft中archive的精灵图]/[图:File directory.png：Minecraft中directory的精灵图] ``` < 数据包名称 > ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 命名空间 > ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` predicate ``` - [图:File file.png：Minecraft中file的精灵图] ``` <谓词名称>.json ``` - 查看更多目录…

以上数据包文件夹结构定义了一个命名空间ID为
```
<命名空间>:<谓词名称>
```

的谓词。

原版数据包中默认不包含任何谓词文件。

## 文件格式

谓词文件中的文本必须使用JSON格式书写。若要直接表示单个谓词，则最外层为一对花括号；若要表示多个谓词，最外层应使用一对方括号：

```
{

 
...

}
```

```
[

  
{
 
...
 
},
 
{
 
...
 
},
 
...

]
```

以上两种格式分别对应§ 数据格式中的[图:NBT复合标签/JSON对象]对象和[图:NBT列表/JSON数组]数组形式。

# 调用

战利品表谓词以及战利品表谓词文件可以从数据包中以几种不同的方式调用：

## 通过命令

在命令中，除调用由谓词文件定义的谓词外，也可直接使用SNBT定义谓词，这样的谓词称为内联谓词。要使用命令或者函数调用战利品表谓词，有两种方法：

- 目标选择器：为了筛选实体，目标选择器参数 ``` predicate= ``` 将检查战利品表谓词文件，此时战利品表谓词文件便成为一个过滤器。对每个要过滤的实体，战利品表谓词文件都会被调用一次，每次调用都在实体所处位置。
- ``` / execute ``` ：其子命令 ``` /execute if predicate ``` 可以调用一个战利品表谓词文件或内联战利品表谓词。命令执行后，将返回一个执行结果或者判定是否继续执行后续子命令。在当前命令环境的执行位置，战利品表谓词文件会被调用一次。

## 通过其他战利品表谓词

```
minecraft:reference
```

条件类型的谓词会调用一个战利品表谓词文件，同时返回其结果给调用者。

## 通过其他文件中的战利品表谓词

除了战利品表谓词文件外，战利品表谓词也在其他的数据包文件中存在，比如进度和战利品表。

# 行为

在Minecraft中可通过多种方式调用谓词，以检查世界中的各种情况。在内部，谓词会返回“通过”或者“失败”给调用者。一般情况下，仅当谓词满足其所描述的特征时才会返回“通过”。在利用谓词时也一般仅判定其是否返回“通过”——仅当谓词“通过”时才执行后续逻辑。若一个文件中定义了多个谓词，则内部的所有谓词都必须通过以返回“通过”。

## 加载

在正在运行的存档中，如果对谓词文件的内容或位置进行了修改，则可以使用
```
/
reload
```

来重新从硬盘加载。

在每次打开存档或打开服务器时，游戏也会尝试加载数据包中的谓词。

# 数据格式

当谓词以谓词文件的形式表示时，应使用JSON格式；当谓词数据直接内联于命令中时，应使用SNBT格式。

战利品表谓词的数据格式有两种形式：

- [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组] - - 若根节点的类型为[图:NBT复合标签/JSON对象]，则为对象形式： - [图:字符串]condition：一个命名空间ID，表示谓词类型。 - 该战利品表谓词的其他部分，指定的部分在下面列出。 - - 若根节点的类型为[图:NBT列表/JSON数组]，则为列表形式： - [图:NBT复合标签/JSON对象]：一个战利品表谓词对象 - [图:字符串]condition：一个命名空间ID，表示谓词类型。 - 该战利品表谓词的其他部分，指定的部分在下面列出。

在列表形式下，可一次性指定多个战利品表谓词对象。当内部所有谓词通过时才被认为此列表谓词通过，效果等效于
```
all_of
```

型的战利品表谓词对象。

以下为各类型的战利品表谓词对象的数据格式：

## all_of

评估一系列战利品表谓词，若它们都通过检查，则评估通过。可从任何上下文调用。

- - [图:字符串]condition： ``` all_of ``` - [图:NBT列表/JSON数组]terms：要评估的战利品表谓词所组成的列表，其中的每个战利品表谓词都必须为一个对象。 - [图:NBT复合标签/JSON对象]：一个战利品表谓词，其结构也可如此递归排布。

## any_of

评估一系列战利品表谓词，若其中任意一个通过检查，则评估通过。可从任何上下文调用。

- - [图:字符串]condition： ``` any_of ``` - [图:NBT列表/JSON数组]terms：要评估的战利品表谓词所组成的列表，其中的每个战利品表谓词都必须为一个对象。 - [图:NBT复合标签/JSON对象]：一个战利品表谓词，其结构也可如此递归排布。

## block_state_property

检查方块以及其方块状态。需要战利品上下文提供的
```
block_state
```

作为待检查的方块状态来进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` block_state_property ``` - [图:字符串]block：一个方块ID。当方块不匹配时，测试不通过。 - [图:NBT复合标签/JSON对象]properties：方块状态。 - [图:字符串][图:NBT复合标签/JSON对象]<方块属性>：（可选）检查指定方块属性。如果方块不满足条件，那么测试会失败。可以为字符串或以两个数字字符串表示的数值区间。 - [图:字符串]min：数值的最小允许值。 - [图:字符串]max：数值的最大允许值。

## damage_source_properties

检查伤害来源的属性。需要战利品上下文提供的
```
origin
```

和
```
damage_source
```

作为伤害位置和伤害来源进行检测，若未提供则测试失败。

- - [图:字符串]condition： ``` damage_source_properties ``` - [图:NBT复合标签/JSON对象]predicate：应用于伤害来源的谓词。 - - 伤害来源谓词，见Template:Nbt inherit/damage source predicate/source

## enchantment_active_check

检查魔咒的生效情况。需要战利品上下文提供的
```
enchantment_active
```

进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` enchantment_active_check ``` - [图:布尔型]active：检查魔咒是否已经生效。

## entity_properties

测试实体的属性。可从任何上下文调用。

- - [图:字符串]condition： ``` entity_properties ``` - [图:字符串]entity：要检查的实体。从战利品上下文指定目标实体。设置成 ``` this ``` 表示实体自身， ``` attacker ``` 表示进行伤害的实体， ``` direct_attacker ``` 表示进行直接伤害的实体， ``` attacking_player ``` 表示进行伤害的玩家， ``` target_entity ``` 表示交互行为中的目标实体， ``` interacting_entity ``` 表示交互行为的执行实体。 - [图:NBT复合标签/JSON对象]predicate：要应用于实体的谓词。 - - 实体谓词，见Template:Nbt inherit/entity predicate/source

## entity_scores

测试实体的记分板分数。需要战利品上下文提供的任一实体目标进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` entity_scores ``` - [图:字符串]entity：要检查的实体。从战利品上下文指定目标实体。设置成 ``` this ``` 表示实体自身， ``` attacker ``` 表示进行伤害的实体， ``` direct_attacker ``` 表示进行直接伤害的实体， ``` attacking_player ``` 表示进行伤害的玩家， ``` target_entity ``` 表示交互行为中的目标实体， ``` interacting_entity ``` 表示交互行为的执行实体。 - [图:NBT复合标签/JSON对象]scores：待检查的分数。所有指定的分数通过测试时，条件通过。 - [图:整型][图:NBT复合标签/JSON对象]<记分项>：将记分项名称作为键名，分数刚好达到一个整数值或符合下面的最大值和最小值的范围时，条件通过。 - [图:整型][图:NBT复合标签/JSON对象]min：最小分数。 - - 数值提供器，见战利品表/数值提供器 - [图:整型][图:NBT复合标签/JSON对象]max：最大分数。 - - 数值提供器，见战利品表/数值提供器

## environment_attribute_check

测试环境属性的具体值。如果环境属性可以随位置变化，则需要战利品上下文提供的
```
origin
```

作为来源位置进行检测，若未提供则总是不通过；如果环境属性不随位置变化，则直接获取整个维度的值进行检测，可从任何上下文调用。

- - [图:字符串]condition： ``` environment_attribute_check ``` - [图:字符串]*attribute：（命名空间ID）要测试的环境属性。 - [图:任意类型]*value：一个与环境属性对应数据类型的值，测试环境属性是否为此值。

## inverted

把参数项中条件的判断结果取反。可从任何上下文调用。

- - [图:字符串]condition： ``` inverted ``` - [图:NBT复合标签/JSON对象]term：谓词，表示待取反的条件。这里允许进行递归定义。

## killed_by_player

检查当前战利品上下文是否存在战利品上下文参数
```
last_damage_player
```

。此参数通常代表击杀实体的最后玩家。

- - [图:字符串]condition： ``` killed_by_player ```

## location_check

检查当前位置。需要战利品上下文提供的
```
origin
```

作为来源位置进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` location_check ``` - [图:整型]offsetX：（可选）检测位置与原位置在X轴上的偏移。 - [图:整型]offsetY：（可选）检测位置与原位置在Y轴上的偏移。 - [图:整型]offsetZ：（可选）检测位置与原位置在Z轴上的偏移。 - [图:NBT复合标签/JSON对象]predicate：应用在检测位置上的谓词。 - - 位置信息谓词，见Template:Nbt inherit/location predicate/source

## match_tool

检查工具。需要战利品上下文提供的
```
tool
```

作为待检查的物品进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` match_tool ``` - [图:NBT复合标签/JSON对象]predicate：应用在物品上的谓词。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source

## random_chance

生成一个取值范围为0.0–1.0之间的随机数，并检查其是否小于指定值。可从任何上下文调用。

- - [图:字符串]condition： ``` random_chance ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]chance：成功率。 - - 数值提供器，见战利品表/数值提供器

## random_chance_with_enchanted_bonus

生成一个取值范围为0.0–1.0之间的随机数，并检查其是否小于指定值。此过程受
```
attacking_entity
```

实体身上的指定魔咒等级影响。需要战利品上下文提供的
```
attacking_entity
```

实体进行检测，若未提供则总是失败。

- - [图:字符串]condition： ``` random_chance_with_enchanted_bonus ``` - [图:字符串]enchantment：提供魔咒等级的魔咒命名空间ID。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]enchanted_chance：当魔咒存在时条件成功的概率。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数]unenchanted_chance：（不小于0且不大于1）当此魔咒不存在时条件成功的概率。

## reference

调用另一个战利品表谓词文件并返回其结果。可从任何上下文调用。

- - [图:字符串]condition： ``` reference ``` - [图:字符串]name：待调用谓词的命名空间ID。循环引用会导致解析失败。

## survives_explosion

以
```
1/爆炸半径
```

的概率返回成功。需要战利品上下文提供的
```
explosion_radius
```

作为爆炸半径进行检测，若未提供则总是通过。

- - [图:字符串]condition： ``` survives_explosion ```

## table_bonus

以魔咒等级为索引，从列表中挑选概率通过。需要战利品上下文提供的
```
tool
```

作为提供魔咒的物品进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` table_bonus ``` - [图:字符串]enchantment：魔咒的命名空间ID。 - [图:NBT列表/JSON数组]chances：从0开始索引，获取相应魔咒等级的概率表。 - [图:单精度浮点数]：在某一魔咒等级下的通过概率。

## time_check

将当前的游戏时间（更确切地来说，为
```
24000 * 天数 + 当天时间
```

）和给定值进行比较。可从任何上下文调用。

- - [图:字符串]condition： ``` time_check ``` - [图:字符串]clock：（命名空间ID）指定要检查的世界时钟。 - [图:整型][图:NBT复合标签/JSON对象]value：要比较的时间值，以刻为单位。 - [图:整型][图:NBT复合标签/JSON对象]max：最大值。 - - 数值提供器，见战利品表/数值提供器 - [图:整型][图:NBT复合标签/JSON对象]min：最小值。 - - 数值提供器，见战利品表/数值提供器 - [图:长整型]period：若存在，则会先将游戏时间模除该值，再使用该结果和value比较。例如，若period被设置为24000，则要检查时间将等于当前世界的当天时间。

## value_check

将一个数与另一个数或范围进行比较。可从任何上下文调用。

- - [图:字符串]condition： ``` value_check ``` - [图:整型][图:NBT复合标签/JSON对象]value：待测试的数值。 - - 数值提供器，见战利品表/数值提供器 - [图:整型][图:NBT复合标签/JSON对象]range：用来与value进行比较的数值范围。 - [图:整型][图:NBT复合标签/JSON对象]min：最小值。 - - 数值提供器，见战利品表/数值提供器 - [图:整型][图:NBT复合标签/JSON对象]max：最大值。 - - 数值提供器，见战利品表/数值提供器

## weather_check

检查当前游戏的天气状态。可从任何上下文调用。

- - [图:字符串]condition： ``` weather_check ``` - [图:布尔型]raining：如果为真，则仅在降雨或雷暴时通过检查。 - [图:布尔型]thundering：如果为真，则仅在雷暴时通过检查。

# 历史

## 已移除的谓词

### random_chance_with_looting

生成一个取值范围为0.0–1.0之间的随机数，并检查其是否小于指定值。此过程受
```
killer
```

实体身上的抢夺等级影响。需要战利品表上下文提供的
```
killer
```

实体进行检测，若未提供则总是不通过。

- - [图:字符串]condition： ``` random_chance_with_looting ``` - [图:单精度浮点数]chance：基础成功率。 - [图:单精度浮点数]looting_multiplier：对基础成功率的调整，公式是 ``` chance + ( 抢夺等级 * looting_multiplier) ``` 。

# 导航

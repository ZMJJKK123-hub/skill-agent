---
name: minecraft-java-tags
description: |
  Java版标签（Minecraft Wiki 中文版全量正文）。
  
  【概述】关于基岩版的标签，请见“基岩版标签”。
  
  【涵盖内容】
  - 目录结构
  - 命名空间ID
  - 文件格式
  - 加载行为
  - 原版标签
  - 示例
  
  【关键定义】
  - 数据包路径：data/example/tags/block/my_logs.json、data/example/tags/block/logs_and_tnt.json、data/example/tags/item/my_items.json、data/minecraft/tags/block/sword_efficient.json、data/minecraft/tags/block/beacon_base_blocks.json
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签 的完整规范时
---

关于基岩版的标签，请见“基岩版标签”。

本条目所述内容仅适用于Java版。
标签（Tag）允许玩家使用JSON文件将游戏资源分组。

# 定义

## 目录结构

标签定义文件的文件路径与其定义的标签类型相关。

标签位于数据包的
```
data/<
命名空间
>/tags/<
数据包路径
>
```

目录下。除进度和配方外，所有的注册表内容都可以定义相应的标签（尽管游戏并非为每种注册表标签提供调用方法）。例如方块标签的文件路径为
```
data/<
命名空间
>/tags/block
```

。

函数不属于注册表内容，但其目录仍位于同一层级。

- [图:File archive.png：Minecraft中archive的精灵图]/[图:File directory.png：Minecraft中directory的精灵图] ``` <数据包名称> ``` - [图:File file.png：Minecraft中file的精灵图] ``` pack.mcmeta ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` <命名空间> ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` tags ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` < 某注册表的数据包路径 > ``` - [图:File file.png：Minecraft中file的精灵图] ``` <注册表标签名>.json ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` - [图:File file.png：Minecraft中file的精灵图] ``` <函数标签名>.json ``` - 更多目录...

## 命名空间ID

标签的ID也遵守命名空间ID的格式。为了与非标签元素作区分，在游戏中使用标签时，通常会在其ID前加上“
```
#
```

”前缀。例如，对于方块注册表的元素而言，
```
minecraft:air
```

代表了一个方块，而
```
#minecraft:air
```

代表了一个方块标签。

## 文件格式

标签定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] 根标签。 - [图:布尔型]replace：（默认为 ``` false ``` ）此标签是否完全覆盖较低优先级数据包同命名空间下的同名标签。为 ``` false ``` 时则为此标签进行补充。 - [图:NBT列表/JSON数组]*values：一个游戏资源的列表，代表此标签的内容。 - [图:字符串]：一项游戏资源，格式应为 ``` < 命名空间 >:< 路径 > ``` 。 - [图:字符串]：一项游戏资源的标签，格式应为 ``` #< 命名空间 >:< 路径 > ``` 。循环引用会导致标签加载失败。 - [图:NBT复合标签/JSON对象]：带有附加选项的格式。 - [图:字符串]*id：一个游戏资源的ID或其标签ID，格式同上。 - [图:布尔型]required：（默认为 ``` true ``` ）[图:字符串]*id指定的游戏资源是否是必须的。为 ``` false ``` 时，即使[图:字符串]*id所述内容不存在，游戏也只会静默忽略，而不会使标签加载失败。

## 加载行为

不同数据包可能会对同一标签重复定义。游戏会自下而上加载标签：

- 如果标签的某个必要元素不存在，或标签出现循环引用，则此标签加载无效。
- 如果标签的某个非必要元素（[图:布尔型]required为 ``` false ``` ）不存在，则游戏静默忽略，否则正常添加到标签列表中。
- 如果上层数据包定义的标签的[图:布尔型]replace为 ``` true ``` ，则此丢弃下层数据包的数据。即使下层数据包定义的标签无效，游戏也会正常加载上层数据包的标签。
- 如果上层数据包定义的标签的[图:布尔型]replace为 ``` false ``` ，则合并上层和下层的数据。但如果下层数据包定义的标签无效，则此标签加载无效。

# 使用

在不同的场合调用标签会有不同的效果。其广泛的使用方式是测试某资源对象是否在某标签内，只要资源对象符合标签内定义的任意一个资源对象，测试就会成功。

每个原版标签都可能在游戏源码中作为某些执行和调用行为的限定条件，故标签可直接影响其所包含对象的行为。例如，原版方块标签可用于控制和判断各种方块的行为（比如方块是否能被攀爬），原版物品标签可用于控制和判断物品的行为（比如物品是否能被染料染色），原版实体类型标签可用于控制和判断各种生物的行为（比如是否被视为节肢生物，继而影响节肢杀手魔咒）。原版的进度和配方等文件也使用标签从而实现某些条件判断。

原版游戏中不存在函数，默认也不存在函数标签，不过数据包定义的函数文件可以被游戏正常读取。

## 原版标签

有关原版标签的列表及详细说明，请相应点击以下目录图标旁的链接，链接点击后会跳转到相应的详细页面。

- - [图:File directory.png：Minecraft中directory的精灵图] ``` data ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` minecraft ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` tags ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` banner_pattern ``` ：旗帜图案标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` block ``` ：方块标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` damage_type ``` ：伤害类型标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` dialog ``` ：对话框标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` enchantment ``` ：魔咒标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` entity_type ``` ：实体类型标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` fluid ``` ：流体标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` function ``` ：函数标签。注意：游戏并不会在 ``` client.jar ``` 等文件中预置函数标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` game_event ``` ：游戏事件标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` instrument ``` ：山羊角乐器标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` item ``` ：物品标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` painting_variant ``` ：画变种标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` point_of_interest_type ``` ：兴趣点类型标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` potion ``` ：药水效果标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` timeline ``` ：时间线标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` villager_trade ``` ：村民交易标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` worldgen ``` - [图:File directory.png：Minecraft中directory的精灵图] ``` biome ``` ：生物群系标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` configured_feature ``` ：已配置的地物标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` feature ``` ：已配置的地物标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` flat_level_generator_preset ``` ：超平坦世界生成预设标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` structure ``` ：结构标签。 - [图:File directory.png：Minecraft中directory的精灵图] ``` world_preset ``` ：世界预设标签。 - - 下列标签游戏不再使用： - [图:File directory.png：Minecraft中directory的精灵图] ``` cat_variant ``` ：猫变种标签。

## 示例

定义新标签

[图:File file.png：Minecraft中file的精灵图] 
```
data/example/tags/block/my_logs.json
```

json

```
{

  
"values"
:
 
[

    
"minecraft:oak_log"
,

    
"minecraft:birch_log"
,

    
"minecraft:spruce_log"

  
]

}
```

在命令中通过
```
#example:my_logs
```

来使用。例如使用
```
/
fill
 ~-5 ~-5 ~-5 ~5 ~5 ~5 air replace #example:my_logs
```

将玩家周围5格的这些方块替换为空气。

在标签中引用另外的标签

[图:File file.png：Minecraft中file的精灵图] 
```
data/example/tags/block/logs_and_tnt.json
```

json

```
{

  
"values"
:
 
[

    
"#minecraft:logs"
,

    
"minecraft:tnt"

  
]

}
```

此标签文件同时包括
```
#logs
```

方块标签和
```
tnt
```

方块。

标签中的可选项

[图:File file.png：Minecraft中file的精灵图] 
```
data/example/tags/item/my_items.json
```

json

```
{

  
"values"
:
 
[

    
{
 
"id"
:
 
"example:custom_item"
,
 
"required"
:
 
false
 
}

  
]

}
```

这使得
```
example:custom_item
```

不存在时（比如，在不同的模组环境下时），不会出现加载错误。

扩展原版标签

[图:File file.png：Minecraft中file的精灵图] 
```
data/minecraft/tags/block/sword_efficient.json
```

json

```
{

  
"values"
:
 
[

    
"#minecraft:wool"

  
]

}
```

在
```
#sword_efficient
```

的基础上添加了
```
#minecraft:wool
```

标签中的所有内容，使得羊毛可被剑更快地破坏。

替换原版标签

[图:File file.png：Minecraft中file的精灵图] 
```
data/minecraft/tags/block/beacon_base_blocks.json
```

json

```
{

  
"replace"
:
 
true
,

  
"values"
:
 
[

    
"minecraft:lodestone"

  
]

}
```

这将完全覆盖低优先级数据包下的同名文件
```
#beacon_base_blocks
```

，使得信标基座只能用磁石搭建。

# 历史

# 参见

- 基岩版标签

# 导航

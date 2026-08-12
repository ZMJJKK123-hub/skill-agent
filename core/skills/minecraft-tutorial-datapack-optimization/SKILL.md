---
name: minecraft-tutorial-datapack-optimization
description: |
  Tutorial:优化数据包（Minecraft Wiki 中文版全量正文）。
  
  【概述】本教程所述内容仅适用于Java版。
  
  【涵盖内容】
  - 减少运行的命令
  - 使用schedule命令
  - 使用实体周期谓词
  - 在玩家身上使用进度
  - 在生物身上使用魔咒
  - 优化NBT操作
  - 用 / execute if items 替换物品匹配
  - 用 谓词 替换匹配操作
  - 用 物品修饰器 替换物品操作
  - 用命令存储缓存NBT
  - 减少execute子命令
  - 优化目标选择器
  
  【关键定义】
  - 数据包路径：data/server/profiling.txt
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Tutorial:优化数据包 的完整规范时
---

本教程所述内容仅适用于Java版。
本教程将介绍如何优化命令和数据包。

# 性能分析

主条目：性能分析报告文件 § 性能转储数据
如果你不确定要优化哪些命令，务必运行性能分析。

在专用服务器上使用
```
/
perf
```

命令，或在单人游戏使用F3 + L进行性能分析，可以获取服务器性能分析数据。

分析之后，打开
```
<
服务端根目录
>/debug/profiling/<
时间
>-<
存档名称
>-<
游戏版本
>.zip
```

（也可通过点击聊天栏访问），解压
```
server/profiling.txt
```

。

其中
```
tick
```

下的
```
commandFunctions
```

和
```
tick/levels/ServerLevel[<
世界名
>] <
维度ID
>/tick
```

下的
```
scheduledFunctions
```

就是函数性能数据。

# 最佳方案

Minecraft是一个复杂的游戏，没有总是适用的规则，并且命令的行为可能偏离预期。如果你不确定如何优化命令，可以反复尝试。

## 减少运行的命令

这似乎显而易见，但它是优化命令的最佳途径之一。

对于一部分命令，你不必每刻都要运行它们。试着延长这些命令的运行周期，或是使用不依赖刻循环的方式实现。

### 使用schedule命令

将
```
/
schedule
 function
```

指向自身可产生间隔循环执行的效果。将这个函数添加至
```
#minecraft:load
```

标签（或相关逻辑）而非
```
#minecraft:tick
```

标签。

[图:File file.png：Minecraft中file的精灵图] 
```
example:loop/2t
```

mcfunction

```
+ schedule function example:loop/2t 2t

execute as @e run ...
```

### 使用实体周期谓词

如果命令周期集中运行的效果不佳（如同时在玩家周围实体播放声音，使得声音叠加），可以尝试实体谓词 § 实体谓词格式的
```
periodic_tick
```

。

相对于
```
/
schedule
```

性能更差，因为还是会运行目标选择器，只是会检测实体的出现时间是否是
```
periodic_tick
```

的倍数。

### 在玩家身上使用进度

如果仅匹配玩家，使用进度避免命令选中
```
@a
```

的性能损耗。

在进度内设置触发条件，在函数末尾添加要运行的命令。

[图:File file.png：Minecraft中file的精灵图] 
```
example:player/score
```

advancement

...

```
{

  
"criteria"
:
 
{

    
"example"
:
 
{

      
"trigger"
:
 
"minecraft:tick"
,

      
"conditions"
:
 
{

        
"player"
:
 
[

          
{

            
"condition"
:
 
"minecraft:entity_scores"
,

            
"entity"
:
 
"this"
,

            
"scores"
:
 
{

              
"example.score"
:
 
{

                
"min"
:
 
1

              
}

            
}

          
}

        
]

      
}

    
}

  
},

  
"rewards"
:
 
{

    
"function"
:
 
"example:triggered"

  
}

}
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:triggered
```

mcfunction

```
advancement
 
revoke
 
@s
 
only
 
example:player/score
```

### 在生物身上使用魔咒

相比于进度，魔咒适用于几乎所有的生物。然而魔咒能够应用的场景相对有限。当你需要在非玩家身上应用命令时优先考虑魔咒是否可用。

一个值得在这里提出的技巧是：即便一个槽位看似不被某个生物应用，在该槽位上仍能设置物品且魔咒往往也能生效。例如，你可以在僵尸身上应用鞍槽位。

[图:File file.png：Minecraft中file的精灵图] 
```
example:example
```

enchantment

...

```
{

    
"description"
:
"example"
,

    
"anvil_cost"
:
1
,

    
"max_level"
:
1
,

    
"weight"
:
1
,

    
"min_cost"
:{

        
"base"
:
1
,

        
"per_level_above_first"
:
3

    
},

    
"max_cost"
:{

        
"base"
:
2
,

        
"per_level_above_first"
:
3

    
},

    
"supported_items"
:
"minecraft:paper"
,

    
"slots"
:[

        
"saddle"

    
],

    
"effects"
:{

        
"minecraft:tick"
:[

            
{

                
"effect"
:{

                    
"type"
:
"run_function"
,

                    
"function"
:
"example:foo"

                
}

            
}

        
]

    
}

}
```

## 优化NBT操作

访问或修改NBT数据是高开销行为，对玩家更是如此。这是因为游戏实际上会先将实体数据保存到硬盘，再对数据进行操作；如果是对NBT数据进行修改，还要再读取回来并创建一个新的实体。

### 用 / execute if items 替换物品匹配

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @a[nbt={SelectedItem:{id:"minecraft:apple"}}] run ...

+ execute if items entity @s weapon.mainhand apple run ...
```

### 用 谓词 替换匹配操作

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @a[nbt={RootVehicle:{id:"minecraft:pig"}}] run ...

+ execute as @a[predicate=example:riding_pig] run ...
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:riding_pig
```

predicate

```
+ {

+   "condition": "minecraft:entity_properties",

+   "entity": "this",

+   "predicate": {

+     "vehicle": {

+       "type": "minecraft:pig"

+     }

+   }

+ }
```

### 用 物品修饰器 替换物品操作

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/set_count
```

mcfunction

```
- data modify entity @s Item.count set value 10

+ item modify entity @s contents {function:"set_count",count:10}
```

### 用命令存储缓存NBT

如果在使用上述方法优化后，仍有三条以上操作实体或方块NBT的命令，可以使用命令存储缓存NBT。

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/custom_data
```

mcfunction

```
data
 
modify
 
storage
 
example:temp
 
custom_data
 
set
 
from
 
entity
 
@s
 
item.components.minecraft:custom_data

# 你的代码……

data
 
modify
 
entity
 
@s
 
item.components.minecraft:custom_data
 
set
 
from
 
storage
 
example:temp
 
custom_data
```

## 减少execute子命令

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @a[tag=hider] run effect give @s glowing

+ effect give @a[tag=hider] glowing
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @a[tag=hider] if score @s timer matches 0.. run ...

+ execute as @a[tag=hider,scores={timer=0..}] run ...
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/hi
```

mcfunction

```
- execute run say hi

+ say hi
```

## 优化目标选择器

 参见：Tutorial:目标选择器 § 选择器差异 

### 为选择器添加类型判断

除非你意在检测所有的实体种类，否则你可以在选择器内加入
```
type
=
```

参数。这样做可以排除不需要检测的实体，优化选择器性能。

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @e[tag=special_altar] run ...

+ execute as @e[type=marker,tag=special_altar] run ...
```

### 减少@e选择器

寻找世界上所有匹配的实体是高开销行为。如果你有多个使用重复或相似选择器的命令，请考虑将它们合并为单个函数，然后使用开销更低的
```
@s
```

代替多余的选择器。

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @e[type=item] if items entity @s contents apple run ...

- execute as @e[type=item] if items entity @s contents cobblestone run ...

+ execute as @e[type=item] run function example:f/process_item
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/process_item
```

mcfunction

```
+ execute if items entity @s contents apple run ...

+ execute if items entity @s contents cobblestone run ...
```

### 为选择器添加距离限制

Minecraft以区块为单位加载和读取实体。因此若你知晓想要选中的实体就在上下文当前位置，应当尽量使用
```
distance
=
```

做距离限制，以减少被影响的区块。

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @e[type=marker,tag=test] run ...

+ execute as @e[type=marker,tag=test,distance=..1] run ...
```

## 优化宏函数

 参见：宏函数 

### 减少不必要的宏函数

调用宏函数具有开销。请考虑仅在绝对必要时使用它们。

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/set_age
```

mcfunction

```
- $scoreboard players set @s example $(Age)

+ execute store result score @s example run data get entity @s Age
```

### 使用宏函数缓存

游戏将尝试缓存8个在调用中被使用过的参数。

所以，如果你的宏函数有16个参数，考虑创建两个输入8个参数的宏函数，以显著提升性能。

# 备选方案

以下方案有错误使用的风险，或优化效果一般。

## 判断玩家距离

 参见：目标选择器 § 距离 
如果一个性能损耗较大的功能在玩家附近才有效，考虑判断玩家距离。

### 在实体处匹配

[图:File file.png：Minecraft中file的精灵图] 
```
example:tick
```

mcfunction

```
- execute as @e[type=item] at @s run ...

+ execute as @e[type=item] at @s if entity @a[distance=..24] run ...
```

### 在玩家处匹配

如果实体数量很多（或选中实体多次），匹配距离可能会有较大的损耗，这时可以先使用
```
/
tag
```

命令为玩家周围的实体打上标签，再选中
```
tag
=
```

进行执行。只需标记一次就可在各处使用。还可搭配§ 减少运行的命令方法。

[图:File file.png：Minecraft中file的精灵图] 
```
optimize:loop/2t
```

mcfunction

```
schedule
 
function
 
optimize:loop/2t
 
2
t

execute
 
at
 
@a
 
run
 function
 
optimize:f/tagging_active_entity
```

[图:File file.png：Minecraft中file的精灵图] 
```
optimize:f/tagging_active_entity
```

mcfunction

```
tag
 
@e
[
tag
=!
active.64
,
distance
=
..
64
]
 
add
 
active.64

tag
 
@e
[
tag
=
active.64
,
distance
=
64
..
]
 
remove
 
active.64
```

## 优化匹配逻辑

### 使用return run结束函数

如果匹配到一种情况后，后面的情况都不会发生，可使用
```
/
return
 run
```

结束当前函数。如果逻辑上没有先后关系，可以将更容易出现的放在前面。

注意：

- ``` / return run ``` 会立即结束函数。应该在一个单独的，处理各种分支匹配情况函数中使用这个方法。
- 如果有多个命令分支（如选中多个实体 ``` / execute as @e ``` ），只会执行第一个分支。

[图:File file.png：Minecraft中file的精灵图] 
```
example:f/match
```

mcfunction

```
- execute if predicate some:1 run function some:1

- execute if predicate some:2 at @s run function some:2

- execute if predicate some:3 in minecraft:overworld run function some:3

+ execute if predicate some:1 run return run function some:1

+ execute if predicate some:2 run return run execute at @s run function some:2

+ execute if predicate some:3 run return run execute in minecraft:overworld run function some:3
```

### 使用二叉树

如遇极端情况（无法使用宏函数且分支数量巨大），可使用二叉树。

[图:File file.png：Minecraft中file的精灵图] 
```
example:root
```

mcfunction

```
execute
 
if
 
score
 
#0
 
example
 
matches
 
0
..
127
 
run
 return
 
run
 function
 
example:node/0..127

execute
 
if
 
score
 
#0
 
example
 
matches
 
128
..
255
 
run
 return
 
run
 function
 
example:node/128..255
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:node/0..127
```

mcfunction

```
execute
 
if
 
score
 
#0
 
example
 
matches
 
..
63
 
run
 return
 
run
 function
 
example:node/0..63

execute
 
if
 
score
 
#0
 
example
 
matches
 
64
..
 
run
 return
 
run
 function
 
example:node/64..127
```

[图:File file.png：Minecraft中file的精灵图] 
```
example:node/128..255
```

mcfunction

```
execute
 
if
 
score
 
#0
 
example
 
matches
 
..
191
 
run
 return
 
run
 function
 
example:node/128..191

execute
 
if
 
score
 
#0
 
example
 
matches
 
192
..
 
run
 return
 
run
 function
 
example:node/192..255
```

# 导航

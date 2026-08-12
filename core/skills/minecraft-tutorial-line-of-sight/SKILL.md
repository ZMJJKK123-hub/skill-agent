---
name: minecraft-tutorial-line-of-sight
description: |
  Tutorial:制作数据包/实例：视线魔法（Minecraft Wiki 中文版全量正文）。
  
  【概述】本教程所述内容仅适用于Java版。
  
  【涵盖内容】
  - 数据包实现
  - 胡萝卜钓竿开关
  
  【关键定义】
  - 数据包路径：data/generic/function/raycast/shoot.mcfunction、data/generic/function/raycast/check_entity.mcfunction、data/generic/function/raycast/end.mcfunction、data/generic/tags/function/raycast.json、data/generic/tags/function/raycast/start.mcfunction、data/generic/advancement/event/right_click.json
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Tutorial:制作数据包/实例：视线魔法 的完整规范时
---

本教程所述内容仅适用于Java版。

此教程介绍一个数据包制作的实例，阅读此教程前可先阅读Tutorial:制作数据包和Tutorial:制作资源包。

本教程适用于Java版1.21.2以上版本。低于该版本的实际效果请自行评估。

# 预期效果

在本实例中，我们将利用Tutorial:制作数据包/实例：射线投射中所讲述的一些知识，使得玩家右键物品后能在其视线所指处发生以下事件：

- 爆炸。
- 若为蜂巢或蜂箱，则输出其中的成年和幼年蜜蜂数量。

# 对射线投射的改进

在之前的射线投射实例中，我们设计了一个非常基础的射线投射算法。接下来我们将让其拥有更强大的兼容性。首先我们改进一下shoot部分：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/shoot.mcfunction
```

mcfunction

```
# particle minecraft:end_rod ~ ~ ~ 0 0 0 0 0

# execute positioned ~ ~-0.5 ~ run summon interaction ^ ^ ^ {Tags:["test","source_entity"]}

scoreboard
 
players
 
add
 
#raycast_check_times
 
var
 
1

execute
 
if
 
score
 
#raycast_check_times
 
var
 
>=
 
#raycast_max_check_times
 
var
 
run
 return
 
run
 function
 
generic:raycast/end

# 检测当前位置是否有可穿过的方块，没有就停止

execute
 
unless
 
block
 
~
 
~
 
~
 
#generic:raycast/can_pass
 
run
 return
 
run
 function
 
generic:raycast/end

# 如果射到实体就停止

execute
 
if
 
score
 
#raycast_pass_entity
 
var
 
matches
 
0
 
positioned
 
~
-0.5
 
~
-0.5
 
~
-0.5
 
if
 
entity
 
@n
[
dx
=
0
,
dy
=
0
,
dz
=
0
,
tag
=!
source_entity
]
 
positioned
 
~
0.5
 
~
0.5
 
~
0.5
 
if
 
function
 
generic:raycast/check_entity
 
run
 return
 
run
 function
 
generic:raycast/end

# 每次的步长从0.1改为0.5，减少递归次数

execute
 
positioned
 
^
 
^
 
^
0.5
 
run
 function
 
generic:raycast/shoot
```

以上代码新增了检测实体的部分，这使得我们的射线在碰撞到实体后也会执行终止函数。考虑到检测实体可能不是所有系统都必须的，所以我们通过判断
```
#raycast_pass_entity
```

的分数来对检测实体的功能进行开关控制，为0时表示不忽略实体，为1时即默认状态下忽略实体。

考虑到我们的步长是0.5，为了更加精确的检测到实体，我们采取先检测以当前位置为中心1×1×1正方体范围内有无实体，若有则执行另一个步长为0.1的递归检测：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/check_entity.mcfunction
```

mcfunction

```
# particle minecraft:end_rod ~ ~ ~ 0 0 0 0 0

# execute positioned ~ ~-0.5 ~ run summon interaction ^ ^ ^ {Tags:["test","source_entity"]}

# 制造一个非常小的正方体检测区域

execute
 
positioned
 
~
-0.995
 
~
-0.995
 
~
-0.995
 
as
 
@e
[
dx
=
0
,
dy
=
0
,
dz
=
0
,
tag
=!
source_entity
]
 
positioned
 
~
0.99
 
~
0.99
 
~
0.99
 
if
 
entity
 
@s
[
dx
=
0
,
dy
=
0
,
dz
=
0
]
 
run
 return
 
1

scoreboard
 
players
 
add
 
#raycast_check_entity_times
 
var
 
1

execute
 
if
 
score
 
#raycast_check_entity_times
 
var
 
matches
 
10
..
 
run
 return
 
fail

execute
 
positioned
 
^
 
^
 
^
0.1
 
run
 function
 
generic:raycast/check_entity
```

这里的
```
#raycast_check_entity_times
```

类似于之前shoot中的
```
#raycast_check_times
```

，用来记录当前已经递归过的次数。由于之前已经检测到了以当前位置为中心的1×1×1正方体范围内存在实体，故我们直接设定最大检测次数为10即可。

递归结束后，我们将原来的单个分配函数变为一个函数标签：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/end.mcfunction
```

mcfunction

```
# particle minecraft:dust{color:[0, 0, 1], scale:1.0} ~ ~ ~ 0.1 0.1 0.1 0 50 force

function
 
#generic:raycast

scoreboard
 
players
 
set
 
#raycast_max_check_times
 
var
 
0

scoreboard
 
players
 
set
 
#raycast_pass_entity
 
var
 
1

tag
 
@s
 
remove
 
source_entity
```

函数标签可以被理解为一个函数接口。因为数据包之间都可以直接在对应的命名空间下添加该标签，以直接将射线射出后的终端执行环境接入到自身的逻辑中。这里我们先留空以备用：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/tags/function/raycast.json
```

json

```
{

  
"values"
:
 
[]

}
```

最后，我们在start函数中也对
```
#raycast_check_entity_times
```

设定初始值0：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/tags/function/raycast/start.mcfunction
```

mcfunction

```
# /execute as @s anchored eyes run 

scoreboard
 
players
 
set
 
#raycast_check_times
 
var
 
0

scoreboard
 
players
 
set
 
#raycast_check_entity_times
 
var
 
0

tag
 
@s
 
add
 
source_entity

execute
 
positioned
 
^
 
^
 
^
0.5
 
run
 function
 
generic:raycast/shoot
```

现在，只需要编写并执行以下函数就能完整使用该射线投射模块：

```
# 设定最大递归次数为1000

scoreboard
 
players
 
set
 
#raycast_max_check_times
 
var
 
1000

# 不忽略实体

scoreboard
 
players
 
set
 
#raycast_pass_entity
 
var
 
0

# 从当前执行者的眼睛位置开始执行

execute
 
anchored
 
eyes
 
run
 function
 
generic:raycast/start
```

# 右键检测

所需的主要知识：

- 命令/execute
- 命令/give
- SNBT格式
- 物品堆叠组件
- 参数类型#item_stack
- 参数类型#item_predicate
- Java版函数
- 标签
- 记分板

## 数据包实现

这里我们主要使用1.21.2的新增组件来实现右键检测。首先，利用进度检测玩家消耗了物品：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/advancement/event/right_click.json
```

json

```
{

  
"criteria"
:
 
{

    
"generic:right_click_event"
:
 
{

      
"trigger"
:
 
"minecraft:consume_item"
,

      
"conditions"
:
 
{

        
"item"
:
 
{

          
"predicates"
:
 
{

            
"custom_data"
:
 
"{listen_event:'right_click'}"

          
}

        
}

      
}

    
}

  
},

  
"rewards"
:
 
{

    
"function"
:
 
"generic:event/right_click"

  
}

}
```

我们不希望物品消失，所以我们必须要通过一些方法来恢复被消耗的物品：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/event/right_click.mcfunction
```

mcfunction

```
advancement
 
revoke
 
@s
 
only
 
generic:event/right_click

# 模拟协程，将当前执行者和执行者手持物寄存，待1t时间后再恢复其手持物

data
 
modify
 
entity
 
0-0-0-0-0
 
Thrower
 
set
 
from
 
entity
 
@s
 
UUID

data
 
modify
 
storage
 
generic:event
 
right_click.last_selected_item
 
set
 
from
 
entity
 
@s
 
SelectedItem

schedule
 
function
 
generic:event/right_click/delay_1t
 
1
t

function
 
#generic:right_click
```

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/event/right_click/delay_1t.mcfunction
```

mcfunction

```
function
 
generic:event/right_click/regain_item
 
with
 
storage
 
generic:event
 
right_click.last_selected_item
```

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/event/right_click/regain_item.mcfunction
```

mcfunction

```
$execute
 
as
 
0-0-0-0-0
 
on
 
origin
 
run
 item
 
modify
 
entity
 
@s
 
weapon.mainhand
 
{
"function"
:
 
"set_components"
,
 
components
:
$(components)
}
```

创建函数标签
```
#generic:right_click
```

：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/tags/function/right_click.json
```

json

```
{

  
"values"
:
 
[]

}
```

上面函数中的
```
0-0-0-0-0
```

是预先召唤的具有指定UUID的物品实体，用于全局存放数据，像这样的实体在数据包开发中通常称为世界实体。

之后其他系统只需要使用函数标签即可“继承”右键触发后的执行环境。

以上实现的直接利用进度触发，在性能上较好，同时直接利用了函数标签来方便其他函数承接，在扩展性方面也更胜一筹。由于新版组件可以单独设定动画效果和冷却时间，故在功能设计上也更加灵活。

# 视线爆炸魔法

为了达到爆炸的目的，我们可以在视线所指处召唤一个瞬间爆炸的TNT或者苦力怕。

所需知识：

- 相对坐标
- 局部坐标
- 目标选择器
- 记分板
- 命令/execute
- 命令/summon
- 命令/particle
- 数据包
- Java版函数

在Tutorial:制作数据包/实例：射线投射中我们已经较为清楚地描述了“raycast”的实现，该章节的主要思路即借助之前所创建的函数来实现在所指位置召唤爆炸实体。

## 数据包实现

在右键检测函数中添加要接入的函数（添加函数接口）：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/tags/function/right_click.json
```

json

```
{

  
"values"
:
 
[

    
"test:sight_magic/extender/right_click"

  
]

}
```

承接右键检测函数标签（实现右键检测接口）：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/sight_magic/extender/right_click.mcfunction
```

mcfunction

```
# 断开非属sight_magic的执行源

execute
 
unless
 
items
 
entity
 
@s
 
weapon.mainhand
 
*
[
custom_data
~
{
id
:
'sight_magic'
}]
 
run
 return
 
fail

# 使用一对used_sight_magic来传递该域的上下文标志

tag
 
@s
 
add
 
used_sight_magic

# 模拟条件分支，根据手持物品的不同执行不同的函数。这里意为产生一个射线，并在射线终止处发生爆炸

execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
*
[
custom_data
~
{
cause_event
:
'explosion'
}]
 
run
 function
 
test:sight_magic/explosion/start

# 域闭合

tag
 
@s
 
remove
 
used_sight_magic
```

玩家右键后，在当前玩家的眼睛位置产生射线，然后在射线终止处发生爆炸：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/sight_magic/explosion/start.mcfunction
```

mcfunction

```
tag
 
@s
 
add
 
explosion

scoreboard
 
players
 
set
 
#raycast_max_check_times
 
var
 
500

scoreboard
 
players
 
set
 
#raycast_pass_entity
 
var
 
0

execute
 
at
 
@s
 
anchored
 
eyes
 
run
 function
 
generic:raycast/start

tag
 
@s
 
remove
 
explosion
```

然后只需实现射线投射接口：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/tags/function/raycast.json
```

json

```
{

  
"values"
:
 
[

    
"test:sight_magic/extender/raycast_end"

  
]

}
```

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/sight_magic/extender/raycast_end.mcfunction
```

mcfunction

```
# 排除其他执行源

execute
 
if
 
entity
 
@s
[
tag
=!
used_sight_magic
]
 
run
 return
 
fail

# 在射线终止处爆炸

execute
 
if
 
entity
 
@s
[
tag
=
explosion
]
 
run
 function
 
test:sight_magic/explosion/do_at
```

召唤一个[图:短整型]fuse标签为0的TNT来实现爆炸：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/sight_magic/explosion/do_at.mcfunction
```

mcfunction

```
summon
 
tnt
 
~
 
~
 
~
 
{
fuse
:
0
}
```

现在，如果你获得了一个这样的木棍：

```
summon
 
item
 
~
 
~
 
~
 
{
Item
:{
components
:{
"minecraft
:
consumable
":{animation:"
block
",consume_seconds:0.0f,has_consume_particles:0b,on_consume_effects:[{sound:"
minecraft:entity.player.attack.crit
",type:"
minecraft:play_sound
"}],sound:"
minecraft:entity.player.attack.crit
"},"
minecraft:custom_data
":{cause_event:"
explosion
",id:"
sight_magic
",listen_event:"
right_click
"},"
minecraft:use_cooldown
":{seconds:0.1f},"
minecraft:use_remainder
":{count:1,id:"
minecraft:stick
"}},count:1,id:"
minecraft:stick
"}}
```

按下右键后，由于食用时间为0，故会在一瞬间触发右键检测进度，继而通过右键检测函数标签调用我们的视线魔法相关函数。最终效果即在视线所指的方块或实体处产生爆炸。

# 蜂巢探视魔法

蜂巢探视魔法将允许玩家通过右键使用手中的物品来获取其所指蜂巢中的成年和幼年蜜蜂数量。

我们继续创建相关函数。在我们的
```
test
```

命名空间下的
```
sight_magic
```

文件夹中，创建
```
bee_finder
```

目录，以制作新的蜂巢探视魔法。接下来，我们仿照前文的视线爆炸魔法，首先实现右键触发功能：

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/extender/right_click.mcfunction
```

mcfunction

```
# ...（这里省略了一些命令）

tag
 
@s
 
add
 
used_sight_magic

execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
*
[
custom_data
~
{
cause_event
:
'explosion'
}]
 
run
 function
 
test:sight_magic/explosion/start

# 这是新增的命令，该命令意为，当玩家右键使用带有cause_event:'get_bees'自定义标签值的主手物品后触发bee_finder/end函数

execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
*
[
custom_data
~
{
cause_event
:
'get_bees'
}]
 
run
 function
 
test:sight_magic/bee_finder/start

tag
 
@s
 
remove
 
used_sight_magic
```

右键触发后，就发射一条射线：

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/bee_finder/start
```

mcfunction

```
tag
 
@s
 
add
 
get_bees

scoreboard
 
players
 
set
 
#raycast_max_check_times
 
var
 
100

execute
 
anchored
 
eyes
 
run
 function
 
generic:raycast/start

tag
 
@s
 
remove
 
get_bees
```

随后直接转到射线终点位置，在extender/raycast_end中新增一条命令：

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/extender/raycast_end.mcfunction
```

mcfunction

```
execute
 
if
 
entity
 
@s
[
tag
=!
used_sight_magic
]
 
run
 return
 
fail

execute
 
if
 
entity
 
@s
[
tag
=
explosion
]
 
run
 function
 
test:sight_magic/explosion/do_at

# 新增的命令：（用来实现bee_finder）

execute
 
if
 
entity
 
@s
[
tag
=
get_bees
]
 
run
 function
 
test:sight_magic/bee_finder/do_at
```

将教程“射线投射”中bee_finder的相关主要代码复制过来并稍作修改：

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/explosion/do_at.mcfunction
```

mcfunction

```
execute
 
unless
 
block
 
~
 
~
 
~
 
#beehives
 
run
 return
 
run
 function
 
test:sight_magic/bee_finder/fail/invalid_block

data
 
modify
 
storage
 
generic:data
 
queue.value
 
set
 
from
 
block
 
~
 
~
 
~
 
bees

execute
 
unless
 
data
 
storage
 
generic:data
 
queue.value
[]
 
run
 return
 
run
 function
 
test:sight_magic/bee_finder/fail/no_bees

function
 
test:sight_magic/bee_finder/counter/init

function
 
test:sight_magic/bee_finder/counter/run

tellraw
 
@s
 
[{
"text"
:
 
"成年蜜蜂数："
},
 
{
"score"
:
 
{
"name"
:
 
"#bee_finder_adult_number"
,
 
"objective"
:
 
"var"
}},
 
{
"text"
:
" 幼年蜜蜂数："
},
 
{
"score"
:
 
{
"name"
:
 
"#bee_finder_baby_number"
,
 
"objective"
:
 
"var"
}}]
```

其余相关函数文件也一并复制过来并修改一些细节：

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/bee_finder/fail/invalid_block.mcfunction
```

mcfunction

```
tellraw
 
@s
 
{
"text"
:
 
"目标方块不是蜂巢或蜂箱！"
,
 
"color"
:
 
"red"
}
```

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/bee_finder/fail/no_bees.mcfunction
```

mcfunction

```
tellraw
 
@s
 
{
"text"
:
 
"目标方块没有蜜蜂！"
,
 
"color"
:
 
"red"
}
```

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/bee_finder/counter/init.mcfunction
```

mcfunction

```
scoreboard
 
players
 
set
 
#bee_finder_baby_number
 
var
 
0

scoreboard
 
players
 
set
 
#bee_finder_adult_number
 
var
 
0
```

[图:File file.png：Minecraft中file的精灵图] 
```
test/sight_magic/bee_finder/counter/run.mcfunction
```

mcfunction

```
function
 
generic:data/queue/fetch_head

scoreboard
 
players
 
reset
 
#bee_finder_bee_age
 
var

execute
 
store
 
result
 
score
 
#bee_finder_bee_age
 
var
 
run
 data
 
get
 
storage
 
generic:data
 
queue.output.entity_data.Age

execute
 
if
 
score
 
#bee_finder_bee_age
 
var
 
matches
 
..
-1
 
run
 scoreboard
 
players
 
add
 
#bee_finder_baby_number
 
var
 
1

execute
 
if
 
score
 
#bee_finder_bee_age
 
var
 
matches
 
0
..
 
run
 scoreboard
 
players
 
add
 
#bee_finder_adult_number
 
var
 
1

execute
 
if
 
data
 
storage
 
generic:data
 
queue.value
[]
 
run
 function
 
test:sight_magic/bee_finder/counter/run
```

现在执行以下命令（将之前木棍中的cause_event:'explosion'改为cause_event:'get_bees'）：

```
summon
 
item
 
~
 
~
 
~
 
{
Item
:{
components
:{
"minecraft
:
consumable
":{animation:"
block
",consume_seconds:0.0f,has_consume_particles:0b,on_consume_effects:[{sound:"
minecraft:entity.player.attack.crit
",type:"
minecraft:play_sound
"}],sound:"
minecraft:entity.player.attack.crit
"},"
minecraft:custom_data
":{cause_event:"
get_bees
",id:"
sight_magic
",listen_event:"
right_click
"},"
minecraft:use_cooldown
":{seconds:0.1f},"
minecraft:use_remainder
":{count:1,id:"
minecraft:stick
"}},count:1,id:"
minecraft:stick
"}}
```

就能获得一根右键后可以获取目标方块中的蜜蜂数量的木棍。

## 胡萝卜钓竿开关

此段落需要更新。
段落中某些信息已经不符合当前版本情况。

上面提到了函数
```
nuke:entities/player
```

，下面会给出所有和这个胡萝卜钓竿开关相关的函数：

```
nuke:entities/player
```

```
execute
 
as
 
@s
[
scores
={
nukeUseCSt
=
1
..
}]
 
at
 
@s
 
run
 function
 
nuke:use_carrot_on_a_stick/type
```

```
nuke:use_carrot_on_a_stick/type
```

```
execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
carrot_on_a_stick
 
run
 function
 
nuke:use_carrot_on_a_stick/mainhand

execute
 
if
 
items
 
entity
 
@s
 
weapon.offhand
 
carrot_on_a_stick
 
run
 function
 
nuke:use_carrot_on_a_stick/offhand

scoreboard
 
players
 
reset
 
@s
 
nukeUseCSt
```

```
nuke:use_carrot_on_a_stick/mainhand
```

```
execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
carrot_on_a_stick
{
id
:
'nuke:remote'
}
 
run
 function
 
nuke:use_carrot_on_a_stick/items/remote

execute
 
unless
 
entity
 
@s
[
tag
=
nuke_used
]
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
carrot_on_a_stick
{
id
:
'nuke:remote_off'
}
 
run
 function
 
nuke:use_carrot_on_a_stick/items/remote_off

tag
 
@s
 
remove
 
nuke_used
```

```
nuke:use_carrot_on_a_stick/items/remote_off
```

```
execute
 
if
 
items
 
entity
 
@s
 
weapon.offhand
 
carrot_on_a_stick
 
run
 loot
 
replace
 
entity
 
@s
 
weapon.offhand
 
1
 
loot
 
nuke:remote

execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
carrot_on_a_stick
 
run
 loot
 
replace
 
entity
 
@s
 
weapon.mainhand
 
1
 
loot
 
nuke:remote

function
 
nuke:start
```

```
nuke:use_carrot_on_a_stick/items/remote
```

```
execute
 
if
 
items
 
entity
 
@s
 
weapon.offhand
 
carrot_on_a_stick
 
run
 loot
 
replace
 
entity
 
@s
 
weapon.offhand
 
1
 
loot
 
nuke:remote_off

execute
 
if
 
items
 
entity
 
@s
 
weapon.mainhand
 
carrot_on_a_stick
 
run
 loot
 
replace
 
entity
 
@s
 
weapon.mainhand
 
1
 
loot
 
nuke:remote_off

function
 
nuke:stop

tag
 
@s
 
add
 
nuke_used
```

```
nuke:start
```

```
scoreboard
 
players
 
set
 
@s
 
nukePerson
 
1
```

```
nuke:stop
```

```
scoreboard
 
players
 
set
 
@s
 
nukePerson
 
0
```

为了和普通的胡萝卜钓竿区别开来，我们会在物品的
```
custom_data
```

中嵌入自己的
```
id
```

标签（如果你不希望这个标签被其他的数据包占用，你也可以命名为类似
```
nuke_id
```

），并把关闭状态的遥控器的
```
id
```

的值设定为
```
nuke:remote_off
```

，开启的设定为
```
nuke:remote
```

。

```
/
execute
 if items
```

用来检测玩家的主手和副手上的物品是否为胡萝卜钓竿。此处我们检测
```
custom_data
```

，就是为了区分玩家手上是遥控器还是普通的钓竿。

同时，还可以通过
```
custom_model_data
```

来重新指定遥控器的纹理。

新建一个资源包，填写好
```
pack.mcmeta
```

，在
```
assets/minecraft/models/item/carrot_on_a_stick.json
```

写入以下内容：

```
{

    
"parent"
:
 
"item/handheld_rod"
,

    
"textures"
:
 
{

        
"layer0"
:
 
"item/carrot_on_a_stick"

    
},

    
"overrides"
:
 
[

        
{
 
"predicate"
:
 
{
 
"custom_model_data"
:
 
13400000
 
},
 
"model"
:
 
"nuke:item/remote"
},

        
{
 
"predicate"
:
 
{
 
"custom_model_data"
:
 
13400001
 
},
 
"model"
:
 
"nuke:item/remote_off"
}

    
]

}
```

其中的
```
overrides
```

就是来指定
```
custom_model_data
```

的。我们指定了两个物品标签谓词，分别指定了一个
```
custom_model_data
```

和它对应的模型：
```
13400000
```

（对应
```
nuke:item/remote
```

）和
```
13400001
```

（对应
```
nuke:item/remote_off
```

）。

```
assets/nuke/models/item/remote.json
```

```
{

    
"parent"
:
 
"item/handheld"
,

    
"textures"
:
 
{

        
"layer0"
:
 
"nuke:item/remote"

    
}

}
```

其中
```
nuke:item/remote
```

对应纹理
```
assets/nuke/textures/item/remote.png
```

，也就是开启的状态的纹理。

另一个模型文件同理。

为了获取物品的方便，我们使用战利品表来预定义物品。此处以关闭的遥控器为例。

```
nuke:remote_off.json
```

```
{

  
"pools"
:
 
[

    
{

      
"rolls"
:
 
1
,

      
"entries"
:
 
[

        
{

          
"type"
:
 
"minecraft:item"
,

          
"name"
:
 
"minecraft:carrot_on_a_stick"
,

          
"functions"
:
 
[

            
{

              
"function"
:
 
"minecraft:set_components"
,

              
"components"
:
 
{

                
"custom_data"
:
 
"{id:'nuke:remote_off'}"
,

                
"custom_model_data"
:
 
13400001
,

                
"custom_name"
:
 
"{\"translate\":\"item.nuke.remote_off\"}"

              
}

            
}

          
]

        
}

      
]

    
}

  
]

}
```

掉落一份该战利品表就会获得关闭状态的遥控器。除了定义
```
components
```

中的
```
custom_data
```

，我们也自定义了物品的
```
custom_model_data
```

和显示名称。显示名称和实例：蜜蜂助手的多语言一样去写就行。此处在简体中文中显示的名称为“遥控器 (关闭)”。

同理，定义一份开启的。

总结：基本思路是，循环检测胡萝卜钓竿，如果有玩家用了遥控器就切换遥控器的状态，并且根据遥控器的状态决定是开始爆炸还是停止爆炸。

切换遥控器的状态，可以直接替换玩家对应的槽位，比如像上方一样使用
```
/
loot
 replace
```

，然后调用定义好的战利品表，十分方便。

# 参见

- ruhuasiyu的数据包制作教程
- ruhuasiyu的更多的合成数据包，其中包含大量可学习借鉴的地方

# 导航

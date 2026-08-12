---
name: minecraft-tutorial-raycasting
description: |
  Tutorial:制作数据包/实例：射线投射（Minecraft Wiki 中文版全量正文）。
  
  【概述】本教程所述内容仅适用于Java版。
  
  【涵盖内容】
  - 数据包实现
  - 使用第三方包
  - 筛选玩家
  - 多语言
  - 更进一步？
  
  【关键定义】
  - 数据包路径：data/generic/function/raycast/start.mcfunction、data/generic/function/raycast/shoot.mcfunction、data/generic/function/raycast/end.mcfunction、data/test/tags/block/raycast/can_pass.json、data/test/function/load.mcfunction、data/minecraft/tags/function/load
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Tutorial:制作数据包/实例：射线投射 的完整规范时
---

本教程所述内容仅适用于Java版。
本教程包含Java版1.21.5至最新预览版内容
若发现版本内容不匹配等问题，请帮助我们扩充或修改

本教程建议学习者事先具备数据包基础
在不熟悉数据包基础用法的情况下学习可能会遇到很多额外问题

此教程介绍一个数据包制作的实例，阅读此教程前最好先阅读Tutorial:制作数据包和Tutorial:制作资源包。了解命令（尤其是扁平化后的命令/execute、命令/data）、记分板、文本组件等内容也会有所帮助。

本教程适用于Java版1.21以上版本。低于该版本的实际效果请自行评估。

# 基本方法

为了获取到玩家准星所指方块，我们需要建立一条模拟玩家视线的“射线”。

提示
本教程中的所有文件路径均从数据包的
```
data
```

目录中开始。

前置知识：

- 相对坐标
- 局部坐标
- 数据包
- Java版函数

射线投射的基本思路就是从玩家眼睛的位置不断向玩家的视线“前”偏移，该偏移过程就形成了一条射线，过程中如果遇到像空气，草丛这样的方块则可以前进，否则就停下。如果运行的次数过多，也应停下，防止函数一直运行造成资源浪费。

## 数据包实现

首先创建一个射线启动函数：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/start.mcfunction
```

mcfunction

```
# /execute anchored eyes run 

scoreboard
 
players
 
set
 
#raycast_check_times
 
var
 
0

# 这里使用return run使得在上一层函数中可以检测到函数返回值

return
 
run
 function
 
generic:raycast/shoot
```

- 该函数应该接在 ``` /execute anchored eyes run ``` 之后，以便从玩家的眼睛处的坐标执行。
- 变量 ``` #raycast_check_times ``` 用于记录步进检测次数。执行前的值必须是0。

然后编写射线步进函数：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/shoot.mcfunction
```

mcfunction

```
# 粒子效果用于可视化射线

particle
 
minecraft:end_rod
 
^
 
^
 
^
 
0
 
0
 
0
 
0
 
0

# 设置最大步进次数，这里设置为超过100后就结束执行

execute
 
if
 
score
 
#raycast_check_times
 
var
 
matches
 
100
..
 
run
 
\

    
return
 
run
 function
 
generic:raycast/end

# 保证第一次进入该函数运行到上一行之前，射线步进次数#raycast_check_times var为0

scoreboard
 
players
 
add
 
#raycast_check_times
 
var
 
1

# 步长为0.1，即每次都前进0.1格，前进过程中检测当前位置是否有可以穿过的方块，若不可以穿过，即代表达到了玩家视线所指的方块处然后停止执行。否则一直检测，直到超过最大步进次数。

execute
 
positioned
 
^
 
^
 
^
0.1
 
\

    
unless
 
block
 
~
 
~
 
~
 
#test:raycast/can_pass
 
run
 
\

        
return
 
run
 function
 
generic:raycast/end

execute
 
positioned
 
^
 
^
 
^
0.1
 
\

    
if
 
block
 
~
 
~
 
~
 
#test:raycast/can_pass
 
run
 
\

        
function
 
generic:raycast/shoot
```

编写射线结束函数：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/end.mcfunction
```

mcfunction

```
# 可视化射线终点

particle
 
minecraft:dust
{
color
:[
0
,
 
0
,
 
1
],
 
scale
:
1.0
}
 
~
 
~
 
~
 
0.1
 
0.1
 
0.1
 
0
 
50

# 用于将射线终点的执行上下文分配到后续其他函数中

function
 
generic:raycast/dispatcher
```

- ``` generic/function/raycast/dispatcher.mcfunction ``` 代表一个分配器，其中将根据某条件来执行不同的函数。该函数目前还没有什么用。

基本逻辑已经完成。接下来完善其中的细节。

定义可被射线穿过的方块（配置方块标签）：

[图:File file.png：Minecraft中file的精灵图] 
```
test/tags/block/raycast/can_pass.json
```

json

```
{

    
"values"
:
 
[

        
"#minecraft:air"
,

        
"#minecraft:replaceable"

    
]

}
```

定义记分项
```
var
```

（该函数在原版
```
load
```

标签的影响下被调用）：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/load.mcfunction
```

mcfunction

```
scoreboard
 
objectives
 
add
 
var
 
dummy
```

[图:File file.png：Minecraft中file的精灵图] 
```
minecraft/tags/function/load
```

json

```
{

    
"values"
:
 
[

        
"test:load"

    
]

}
```

注意：
```
load
```

标签文件必须位于
```
minecraft
```

命名空间下，否则无法被游戏正常驱动。

然后在游戏聊天框输入：

```
/
execute
 
anchored
 
eyes
 
run
 function
 
generic:raycast/start
```

即可看到射线发射情况。

## 使用第三方包

射线投射是一个基础的机制，但是内部隐藏了众多的技术细节和难点。为了方便开发，我们可以直接使用其他人写好的数据包。

进入Bookshelf的下载页面，找到“Raycast”模块，点击页面右上方的“Download”下载。

你可以直接参照其文档中的介绍Bookshelf文档 - Raycast。以下即是其给出的射线投射用例：

```
# 从眼睛位置开始到一定距离或触碰到方块后结束，如果没有触碰到则返回0

execute
 
anchored
 
eyes
 
positioned
 
^
 
^
 
^
 
run
 function
 
#bs.raycast:run
 
{
with
:{}}

# 获取最近一次射线投射到的坐标

data
 
get
 
storage
 
bs:out
 
raycast.hit_point
```

# 获取蜂巢中蜜蜂数量

我们想看到蜂巢中的蜜蜂情况，就必须先清楚蜂巢内部是如何存储蜜蜂数据的。一般可通过查看方块实体数据格式获悉各种方块实体的数据结构。

方块实体数据
 参见：方块实体数据格式 

- [图:NBT复合标签/JSON对象] 方块实体数据 - [图:NBT列表/JSON数组]* *bees：巢内目前存在的蜜蜂信息。此项方块实体数据会被视为数据组件bees。 - [图:NBT复合标签/JSON对象]：一只蜜蜂的数据。 - [图:NBT复合标签/JSON对象]entity_data：蜜蜂的部分实体数据。如果保存的实体数据不是带有 ``` #beehive_inhabitors ``` 的实体（默认为蜜蜂），则尝试放出此实体时实体不会被生成，其数据会被删除。 - [图:字符串]* *id：实体类型。 - 见实体数据格式。下列标签不会被保存，也不会被加载：[图:短整型]Air、[图:NBT复合标签/JSON对象]drop_chances、[图:NBT复合标签/JSON对象]equipment、[图:NBT复合标签/JSON对象]Brain、[图:布尔型]CanPickUpLoot、[图:短整型]DeathTime、[图:单精度浮点数]fall_distance、[图:布尔型]FallFlying、[图:短整型]Fire、[图:整型]HurtByTimestamp、[图:短整型]HurtTime、[图:布尔型]LeftHanded、[图:NBT列表/JSON数组]Motion、[图:布尔型]NoGravity、[图:布尔型]OnGround、[图:整型]PortalCooldown、[图:NBT列表/JSON数组]Pos、[图:NBT列表/JSON数组]Rotation、[图:整型数组]sleeping_pos、[图:整型]CannotEnterHiveTicks、[图:整型]TicksSincePollination、[图:整型]CropsGrownSincePollination、[图:整型数组]hive_pos、[图:NBT列表/JSON数组]Passengers、[图:整型数组][图:NBT复合标签/JSON对象]leash、[图:整型数组]UUID。 - [图:整型]* *min_ticks_in_hive：蜜蜂会在巢内滞留的最短时间。 - [图:整型]* *ticks_in_hive：蜜蜂在巢内已滞留的时间。 - [图:整型数组]flower_pos：储存花的位置，以便其他蜜蜂能够找到。内部的三个整数分别代表了位置的XYZ坐标值。

观察到，蜂巢内的蜜蜂数据都保存在一个[图:NBT列表/JSON数组]bees列表里面。列表中的每一个
```
{}
```

就代表一只蜜蜂，其中的
```
entity_data
```

就是蜜蜂的实体数据。

实体数据
 参见：实体数据格式 
蜜蜂有与之相联系的包含许多该生物属性的存档数据。

- [图:NBT复合标签/JSON对象] 实体数据 - - 实体共通标签，见Template:Nbt inherit/entity/source - - 生物共通标签，见Template:Nbt inherit/living entity/source - - AI生物共通标签，见Template:Nbt inherit/mob/source - - 可成长生物共通标签，见Template:Nbt inherit/breedable/source - - 动物共通标签，见Template:Nbt inherit/animal/source - - 中立的生物共通标签，见Template:Nbt inherit/angerable/source - [图:整型]* *CannotEnterHiveTicks：离蜜蜂能再次进入蜂箱的刻数。 - [图:整型]* *CropsGrownSincePollination：蜜蜂一共促进了多少作物的生长。此值用来限制蜜蜂促进生长作物的次数，当此值大于10时蜜蜂不会再促进生长作物。 - [图:整型数组]flower_pos：储存其盘旋的花的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:布尔型]* *HasNectar：表示蜜蜂是否携带花粉。 - [图:布尔型]* *HasStung：表示蜜蜂是否蜇过玩家或生物。 - [图:整型数组]hive_pos：其蜂箱的坐标。内部的三个整数分别代表了位置的XYZ坐标值。 - [图:整型]* *TicksSincePollination：蜜蜂离开蜂箱后未携带花粉的时间。如果[图:NBT复合标签/JSON对象]FlowerPos存在，当此值超过2400游戏刻（2分）时，蜜蜂会尝试飞向对应坐标。

在“可成长生物共通标签”中，我们可以发现，[图:整型]Age标签决定了这只蜜蜂是成年还是幼年，大于等于0为成年，小于0为幼年。

## 数据包实现

现在编写具体函数。首先需要获取玩家所指方块的位置。我们之前预留了
```
generic:raycast/dispatcher
```

函数，可以把它当作一个接口以将其执行环境接入到我们现在的逻辑中：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/raycast/dispatcher.mcfunction
```

mcfunction

```
execute
 
if
 
entity
 
@s
[
tag
=
used_bee_finder
]
 
run
 function
 
test:bee_finder/extender/raycast_end
```

- ``` test:bee_finder/extender ``` 是 ``` bee_finder ``` 的接入器，作用是利用接入的执行环境来执行后续逻辑。
- ``` used_bee_finder ``` 是一个判别标识，限定执行者必须被标记为“使用了蜜蜂搜索器”。该判别标识可以在玩家刚刚触发射线时添加。

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/bee_finder/extender/raycast_end.mcfunction
```

mcfunction

```
# 移除判别标志，防止影响下次使用时的判断

tag
 
@s
 
remove
 
used_bee_finder

# 如果当前方块不是蜂巢或者蜂箱，就发出异常提醒“非法方块”，并跳出当前函数

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
 
test:bee_finder/fail/invalid_block

# 获取当前位置处方块的bees标签数据到generic:data的queue.value中，如果queue.value为空列表则发出异常提醒“没有蜜蜂”，并跳出当前函数

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
 
test:bee_finder/fail/no_bees

# 此时满足了前提条件，先初始化计数器，然后再运行计数器以统计蜜蜂数量

function
 
test:bee_finder/counter/init

function
 
test:bee_finder/counter/run

# 反馈统计结果到聊天栏

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

- 蜂巢的蜜蜂数据是一个列表，为了根据列表中每一个元素的 ``` Age ``` 标签值判断蜜蜂是幼年还是成年，需要先将数据暂存到命令存储 ``` generic:data ``` 中，以便后续遍历处理。

用来暂存数据的
```
generic:data
```

的数据结构如下：

- [图:NBT复合标签/JSON对象] - [图:NBT复合标签/JSON对象]queue - [图:NBT列表/JSON数组]value - [图:NBT复合标签/JSON对象]output

我们使用以下函数来初始化这个结构：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/data/load.mcfunction
```

mcfunction

```
data
 
modify
 
storage
 
test:test
 
queue
 
set
 
value
 
{
output
:{},
 
value
:[]}
```

从
```
load
```

函数接入，以便在加载时进行初始化：

[图:File file.png：Minecraft中file的精灵图] 
```
minecraft/tags/function/load.json
```

json

```
{

    
"values"
:
 
[

        
"test:load"
,

        
"generic:load"

    
]

}
```

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/load.mcfunction
```

mcfunction

```
function
 
generic:data/queue/load
```

要遍历[图:NBT列表/JSON数组]value，由于Minecraft没有现成的循环逻辑，所以其中一个常见思路就是不断取出列表第一个元素，直到列表为空。

以下函数实现了取出一个首元素，并将取出的元素输出到[图:NBT复合标签/JSON对象]output：

[图:File file.png：Minecraft中file的精灵图] 
```
generic/function/data/fetch_first.mcfunction
```

mcfunction

```
data
 
modify
 
storage
 
generic:data
 
queue.output
 
set
 
from
 
storage
 
generic:data
 
queue.value
[
0
]

data
 
remove
 
storage
 
generic:data
 
queue.value
[
0
]
```

以上，数据操纵函数基本完成。接下来具体实现计数器中的数据遍历：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/bee_finder/counter/run.mcfunction
```

mcfunction

```
# 取出一个首元素

function
 
generic:data/queue/fetch_head

# 先重置#bee_finder_bee_age的值，防止当queue.output.entity_data.Age标签不存在时也存有数据

scoreboard
 
players
 
reset
 
#bee_finder_bee_age
 
var

# 获取generic:data的queue.output.entity_data.Age，也即之前bees列表中一个蜜蜂的Age

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

# 如果获取到的Age值小于等于-1，就增加幼年蜜蜂数量

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

# 否则如果在小于等于0范围就增加成年蜜蜂数量

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

# 如果当前列表不为空，就继续递归地获取下一个元素，直到列表为空。

execute
 
if
 
data
 
storage
 
generic:data
 
queue.value
[]
 
run
 function
 
test:bee_finder/counter/run
```

- 在通过 ``` Age ``` 的值判断时蜜蜂数量时，前提条件是 ``` Age ``` 这个标签被成功获取。而我们实际是判断的 ``` #bee_finder_bee_age ``` 在 ``` var ``` 记分项中的值，所以必须保证 ``` Age ``` 标签无法获取时， ``` #bee_finder_bee_age ``` 的值不存在，而不是0。

当然，在计数之前，我们必须保证是从0开始计数的：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/bee_finder/counter/init.mcfunction
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

我们把异常提示加上：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/bee_finder/fail/invalid_block.mcfunction
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
test/function/bee_finder/fail/no_bees.mcfunction
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

最后，我们编写一个函数以让玩家启动bee_finder系统：

[图:File file.png：Minecraft中file的精灵图] 
```
test/function/bee_finder/get_bees.mcfunction
```

mcfunction

```
tag
 
@s
 
add
 
used_bee_finder

execute
 
anchored
 
eyes
 
run
 function
 
generic:raycast/start
```

现在，你可以在聊天栏执行以下命令以尝试获取你所指方块中的蜜蜂数量：

```
/
function
 
test:bee_finder/get_bees
```

# 润色与改进

此段落需要更新。
段落中某些信息已经不符合当前版本情况。

目前这个数据包在加载地图后便会一直检测所有玩家有没有盯着蜂巢，有时这会导致极大的服务器计算资源浪费。而如果你在一个有多语需求的服务器使用这个数据包，也只有会中文的人能使用。下面介绍一下谓词和文本组件。

## 筛选玩家

上面说运用选择器参数可以筛选玩家。如果不是一直检测所有玩家的话，那么就只能检测有需要使用的人了。很容易想到，通常我们会使用玻璃瓶对蜂巢收集蜂蜜，因此可以只检测手（以副手为例）中拿着玻璃瓶的玩家。

建立
```
data/beeutility/predicates/hold_glass_bottle.json
```

谓词文件，内容如下：

```
{

    
"condition"
:
 
"minecraft:entity_properties"
,

    
"entity"
:
 
"this"
,

    
"predicate"
:
 
{

        
"equipment"
:{

            
"offhand"
:{

                
"item"
:
 
"minecraft:glass_bottle"

            
}

        
}

    
}

}
```

此谓词会检测应用该谓词的实体是否在副手拿着玻璃瓶。通过目标选择器参数，我们可以应用该谓词，筛选出有需要使用该数据包的玩家。

将
```
beeutility:tick
```

函数前面改为：

```
execute as @a[predicate=beeutility:hold_glass_bottle] at @s anchored eyes ...
```

就可以筛选了。

## 多语言

你也许用
```
/
data
```

获取过不祥旗帜的数据，这个物品的名字是一个文本组件，里面含有[图:字符串]translate属性，值为
```
"block.minecraft.ominous_banner"
```

。这样的值称为本地化键名（旧称翻译关键字或者翻译标识符）。如果你解压原版游戏的
```
.jar
```

文件，你会发现上面的值就是
```
assets/lang/en_us.json
```

里的键。游戏在解析[图:字符串]translate的时候先将值在资源包和外置资源文件的
```
assets/lang/<当前语言的语言代码>.json
```

的键中寻找，再将对应的值（也就是实际的文本）实际显示出来。如果当前语言没有，就去
```
en_us.json
```

里找。若都没有，就只能直接输出标识符。

文本组件页面还提到了一个[图:NBT列表/JSON数组]with属性，就是和[图:字符串]translate搭配使用的。如果你自己翻过语言文件，你就会发现一些文本中含有
```
%s
```

、
```
%n$s
```

之类的变量。这个时候，[图:NBT列表/JSON数组]with属性里面的文本就会按顺序替代这些变量。

新建一个资源包，填写好
```
pack.mcmeta
```

，建立
```
assets/beeutility/lang
```

文件夹，在文件夹下建立语言文件，以下以
```
zh_cn.json
```

和
```
en_us.json
```

为例。

```
en_us
```

```
json
```

```
{
    "beeutility.actionbar": "%s %s", 
    "beeutility.beeutility": "[Bee utility]",
    "beeutility.result": "%d bee(s), %d adult bee(s), %d baby bee(s)"
}
```

```
zh_cn.json
```

```
{
    "beeutility.actionbar": "%s %s", 
    "beeutility.beeutility": "[蜜蜂助手]",
    "beeutility.result": "%d 只蜜蜂，成年的 %d 只，幼年的 %d 只"
}
```

其中的
```
"%s %s"
```

是因为有的语言可能需要调整显示顺序，对于这些语言我们可以将其设为
```
%2$s %1$s
```

来改变顺序。

现在，将上述
```
/
title
```

命令的文本组件写成这样：

```
{

    
"translate"
:
 
"beeutility.actionbar"
,

    
"with"
:
 
[

        
{

            
"translate"
:
 
"beeutility.beeutility"
,

            
"color"
:
"gold"

        
},

        
{

            
"translate"
:
 
"beeutility.result"
,

            
"with"
:
 
[

                
{
"score"
:{
"name"
:
"*"
,
"objective"
:
"bu_beeamount"
}},

                
{
"score"
:{
"name"
:
"*"
,
"objective"
:
"bu_beeadult"
}},

                
{
"score"
:{
"name"
:
"*"
,
"objective"
:
"bu_beebaby"
}}

            
]

        
}

    
]
 

}
```

现在，将资源包通过服务器资源包分发出去就可以了。

## 更进一步？

既然已经用上资源包了，那么我们也可以另做一个调用
```
CustomModelData
```

的物品模型并把
```
CustomModelData
```

应用到一个不可用原版方法获得的自定义NBT的物品上，让查看蜂巢的人进一步减少。同样的，上述谓词也得做出相应的改变来检测。

或者，你也可以不仅仅只读取蜜蜂个数，可以顺便展示一些其他数据，等等。

# 下一步

这个数据包甚至没有用到一个盔甲架和区域效果云，也没有用到任何战利品表和结构。试着在数据包中应用这些功能也许是个好选择。

同样，你也可以尝试着和资源包结合，尝试把上文的玻璃瓶做成一个自定义物品。

你也可以学习其他已经做成的数据包，或者自己定好一个目标，并把它做出来。

# 导航

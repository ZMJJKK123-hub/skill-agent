---
name: minecraft-example-datapack
description: |
  示例数据包（Minecraft Wiki 中文版全量正文）。
  
  【概述】示例数据包是由Slicedlime创建的用于展示游戏更新的数据包，目前共有两个数据包：
  
  【涵盖内容】
  - 宏函数
  - set_time.mcfunction
  - eval.mcfunction
  - concat.mcfunction
  - 函数返回值
  - fails.mcfunction
  - fails2.mcfunction
  - succeeds.mcfunction
  - get_player_health.mcfunction
  - 换行承接
  - line_continuation.mcfunction
  - Curse of Annoyance
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 示例数据包 的完整规范时
---

示例数据包是由Slicedlime创建的用于展示游戏更新的数据包，目前共有两个数据包：

- 第16版（23w31a）数据包演示数据包
- 数据驱动魔咒数据包

# 第16版数据包演示数据包

此数据包共含有8个函数，用于展示在23w31a里添加的新内容。

## 宏函数

### set_time.mcfunction

```
# 将时间设定为 $(time)

$time
 
set
 
$(
time
)
```

### eval.mcfunction

```
# 运行储存于 $(command) 的命令

$$
(
command
)
```

注：
```
$(command)
```

是函数的一部分，所以存储的命令不带前导正斜杠
```
/
```

。

### concat.mcfunction

```
# 连接 $(string1) 和 $(string2)，将结果储存至存储 $(id) 的 $(path) 

$data
 
modify
 
storage
 
$(
id
)
 
$(
path
)
 
set
 
value
 
"$(string1)$(string2)"
```

## 函数返回值

### fails.mcfunction

```
# 无返回值的函数会返回失败

setblock
 
~
 
~
-1
 
~
 
stone
```

注：此函数可以正常执行；实际表现为无返回值，不改变已有的数据。

### fails2.mcfunction

```
# 返回值为 0 的函数会返回失败

return
 
0
```

### succeeds.mcfunction

```
# 返回值不为 0 的函数会返回成功

return
 
1
```

### get_player_health.mcfunction

```
# 如果目标是玩家，返回生命值

execute
 
if
 
entity
 
@s
[
type
=
player
]
 
run
 return
 
run
 data
 
get
 
entity
 
@s
 
Health

# 为非玩家返回 0

return
 
0
```

## 换行承接

### line_continuation.mcfunction

```
scoreboard
 
players
 
operation
 
@a
 
result
 
\

    
+=
 
@e
[
type
=
marker
,
limit
=
1
,
tag
=
source
]
 
value
```

用于展示使用反斜杠
```
\
```

承接命令的功能。

# 数据驱动魔咒数据包

此数据包共含有14个魔咒，用于展示在24w18a里添加的魔咒数据驱动支持。

## Curse of Annoyance

Curse of Annoyance

Curse of Annoyance是一种使持有者在击中方块时有概率收到“猫的事实（Cat Facts）”的诅咒型魔咒。

持有者主手持有附有此魔咒的物品时，每次击中方块都有20%的概率从11条消息中选择一条发送给持有者。所有消息如下：

- Cat Facts: Thanks for signing up for Cat Facts! You now will receive fun daily facts about CATS! >o<
- Cat Facts: Cats use their tails for balance and have nearly 30 individual bones in them! <To cancel Daily Cat Facts, reply ‘cancel’>
- Cat Facts: In ancient Egypt, killing a cat was a crime punishable by death. Thank you for choosing Cat Facts!
- Cat Facts: Did you know that the first cat show was held in 1871 at the Crystal Palace in London? Mee-wow!
- Cat Facts: Did you know there are about 100 distinct breeds of domestic cat? Plenty of furry love!
- Cat Facts: Cats bury their feces to cover their trails from predators. <To cancel Cat Facts, reply catfactscancel>
- Cat Facts: A cat has two vocal chords, and can make over 100 sounds.
- Cat Facts: <Command not recognized> To unsubscribe, please reply ‘catfactscancel’
- Cat Facts: A cat will spend nearly 30% of her life grooming herself. <To cancel Cat Facts, reply catfactscancel>
- Cat Facts: Recent studies have shown that cats can see blue and green. There is disagreement as to whether they can see red.
- Cat Facts: A domestic cat can sprint at about 31 miles per hour. <To cancel Cat Facts, reply catfactscancel>

## Boom Boom

Boom Boom

Boom Boom是一种使射出的箭在击中方块时产生半径为2的爆炸的魔咒。

魔咒等级不影响实际效果。

## Claw

Claw

Claw是一种增加方块交互距离的魔咒。

每级魔咒增加2点方块交互距离。

## Cowbow

Cowbow

Cowbow是一种使弩的装填音效变为牛的音效的魔咒。

附有该魔咒时，弩的装填时音效变为牛的空闲音效；装填完毕的音效变为牛的受伤音效。

## Diminishing

Diminishing

Diminishing是一种使穿戴者变小的魔咒。

每级魔咒增加20%的缩小比例。

## Fire Walker

Fire Walker

Fire Walker是一种在熔岩上行走可以产生黑曜石的魔咒。

在地上行走（不处于掉落、跳跃或飞行状态）时，以当前方块位置为圆心，等级+2为半径的区域内的所有暴露在空气下，且与玩家站着的方块高度相同的熔岩源方块都会变为黑曜石，其中有10%的概率变为哭泣的黑曜石。等级达到14时覆盖范围达到最大，更高的等级将不会提升其覆盖范围。如果将要替换的熔岩源方块中有生物、船或玩家等实体，则该方块不会变成黑曜石。

此魔咒能消除细雪造成的伤害。

## Fishy

Fishy

Fishy是一种手持时有概率生成蠹虫的魔咒。

手持附有该魔咒的物品时，每刻以0.1%的概率尝试在使用者的位置生成1只蠹虫。

## Curse of Fragility

Curse of Fragility

Curse of Fragility是一种有概率额外消耗物品耐久度的诅咒型魔咒，可以缩短物品的使用寿命。

每次击中方块、进行攻击或受到攻击时有3%的概率触发效果。触发效果后，若为击中方块和受到攻击则损失64点耐久度；若为进行攻击则损失256点耐久度。

## Galaxy Brain

Galaxy Brain

Galaxy Brain是一种在击杀生物后额外获得100点经验的魔咒。

魔咒等级不影响实际效果。

## Multi-Multishot

Multi-Multishot

Multi-Multishot是一种能够一次射出大量箭的魔咒。

其效果与多重射击类似，但每级魔咒会额外装填20只箭。

## Curse of Pollen Allergy

Curse of Pollen Allergy

Curse of Pollen Allergy是一种在森林类生物群系时有概率伤害自己的诅咒型魔咒。

穿戴附有该魔咒的物品时，若穿戴者位于森林类生物群系，每刻以0.5%的概率尝试对穿戴者造成1（[图:♥]）点荆棘伤害。

魔咒等级不影响实际效果。

## Roulette

Roulette

Roulette是一种以小概率损毁工具为代价，使工具不消耗耐久的魔咒。

使用附有该魔咒的工具不消耗耐久；每次使用有1%的概率额外消耗2000点耐久，这会使得除下界合金质工具（会剩余31点耐久）外的所有满耐久物品直接损毁。

## Sparkles!

Sparkles!

Sparkles!是一种使穿戴者持续生成粒子的魔咒。

生成的粒子为
```
ominous_spawning
```

。

## Thor

Thor

Thor是一种使持有者在雷暴天气对伤害免疫的魔咒。

# 外部链接

- https://github.com/slicedlime/examples/tree/master/datapacks

# 导航

---
name: minecraft-enchantment
description: |
  魔咒定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】魔咒定义文件是魔咒（Enchantment）在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - 值效果型组件
  - 普通值效果型
  - 带谓词的值效果型
  - 带目标和谓词的值效果型
  - 实体效果型组件
  - 带谓词的实体效果型
  - 带目标和谓词的实体效果型
  - 位置依赖效果型组件
  - 伤害免疫组件
  - 其他魔咒效果组件
  - 属性效果组件
  - 弩装载声音组件
  
  【关键定义】
  - 注册表：ENCHANTMENT
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 魔咒定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。

魔咒定义文件是魔咒（Enchantment）在数据包中的数据驱动定义文件。

# 定义格式

魔咒在游戏内使用
```
ENCHANTMENT
```

注册表，数据包路径为
```
enchantment
```

，即所有魔咒提供器定义文件都需要在
```
data/<
命名空间
>/enchantment
```

目录内定义，魔咒标签则需要在
```
data/<
命名空间
>/tags/enchantment
```

目录内定义。

魔咒定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*description：（文本组件）物品提示框中显示的魔咒名称。 - [图:整型]*anvil_cost：（值≥0）合并魔咒时每一级魔咒对消耗经验等级的增加量。若魔咒来自附魔书，则消耗经验等级会变为一半（向下取整且至少为1）。 - [图:整型]*max_level：（1≤值≤255）魔咒的最大等级。 - [图:整型]*weight：（0<值≤1024）魔咒的挑选权重。 - [图:NBT复合标签/JSON对象]*min_cost：魔咒的最小修正附魔等级。 - 见下文§ 修正附魔等级范围。 - [图:NBT复合标签/JSON对象]*max_cost：魔咒的最大修正附魔等级。 - 见下文§ 修正附魔等级范围。 - [图:字符串][图:NBT列表/JSON数组]*supported_items：通过铁砧机制可以添加此魔咒的物品。可以为一个物品的命名空间ID或一个物品标签，或一个物品ID的数组。 - [图:字符串][图:NBT列表/JSON数组]primary_items：通过附魔机制可以添加此魔咒的物品。可以为一个物品的命名空间ID或一个物品标签，或一个物品ID的数组。必须为 ``` supported_items ``` 的子集，默认与 ``` supported_items ``` 相同。 - [图:NBT列表/JSON数组]*slots：魔咒的有效槽位，物品在指定的装备槽位上时魔咒才会生效。但并非所有的魔咒效果组件都考虑此字段，详见下文。 - [图:字符串]：一个装备槽位组。 - [图:字符串][图:NBT列表/JSON数组]exclusive_set：（默认为空）魔咒的排斥集，指定与此魔咒不兼容的魔咒。可以为一个魔咒的命名空间ID或一个魔咒标签，或一个魔咒ID的数组。 - [图:NBT复合标签/JSON对象]effects：（默认为空）构成该魔咒的魔咒效果组件。 - 见下文§ 魔咒效果组件。

例如，以下为原版数据包中
```
silk_touch.json
```

（精准采集）魔咒文件的内容：

```
{

  
"anvil_cost"
:
 
8
,

  
"description"
:
 
{

    
"translate"
:
 
"enchantment.minecraft.silk_touch"

  
},

  
"effects"
:
 
{

    
"minecraft:block_experience"
:
 
[

      
{

        
"effect"
:
 
{

          
"type"
:
 
"minecraft:set"
,

          
"value"
:
 
0.0

        
}

      
}

    
]

  
},

  
"exclusive_set"
:
 
"#minecraft:exclusive_set/mining"
,

  
"max_cost"
:
 
{

    
"base"
:
 
65
,

    
"per_level_above_first"
:
 
0

  
},

  
"max_level"
:
 
1
,

  
"min_cost"
:
 
{

    
"base"
:
 
15
,

    
"per_level_above_first"
:
 
0

  
},

  
"slots"
:
 
[

    
"mainhand"

  
],

  
"supported_items"
:
 
"#minecraft:enchantable/mining_loot"
,

  
"weight"
:
 
1

}
```

# 定义行为

魔咒定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使魔咒定义被重新加载，而必须重启服务端。

魔咒定义只定义了魔咒最基本的数据，而魔咒的出现条件、不在下方列出的魔咒行为等请参见魔咒标签对魔咒的控制。

# 修正附魔等级范围

魔咒的最大和最小修正附魔等级由[图:NBT复合标签/JSON对象]max_cost和[图:NBT复合标签/JSON对象]min_cost控制，它们具有下列格式：

- [图:NBT复合标签/JSON对象] 根节点 - [图:整型]*base：魔咒为I级时的附魔等级。 - [图:整型]*per_level_above_first：魔咒每增加1级，附魔等级增长的数值。

如果一个魔咒为n级，[图:整型]base为b，[图:整型]per_level_above_first为p，则附魔等级为b+p(n−1)。如果一个魔咒在某一个等级时最大修正附魔等级小于最小修正附魔等级，则这一等级的魔咒无法通过附魔台、物品修饰器或其他自然方式产生。

# 魔咒效果组件

魔咒所产生的实际影响主要由若干个魔咒效果组件控制。魔咒效果组件可以修改一些数值，或在特定条件下触发若干个魔咒效果。

以下列出其数据格式。

## 值效果型组件

值效果型的魔咒效果组件，是对物品涉及的某些数值进行修改的组件。其命名空间ID指明了要修改的数值，使用值效果对数值进行修改。

大部分的值效果型组件所修改的物品的数值只有在物品使用时才发挥作用（例如
```
block_experience
```

在使用此物品破坏方块时才生效），而不是在装备了此物品时。因此大部分的值效果型组件会忽略魔咒定义中的有效装备槽位（[图:NBT列表/JSON数组]slots字段）。详见下方各表。

### 普通值效果型

普通值效果型组件的取值必须为一个值效果。

- [图:NBT复合标签/JSON对象]<普通值效果型组件的命名空间ID（在下表中列出）>：一个普通值效果型组件，及其使用的值效果。 - 该值效果的子标签。

普通值效果型的组件如下表：

### 带谓词的值效果型

带谓词的值效果型的组件指定多个值效果，且可以为每个值效果指定一个生效条件，仅当这个约束条件满足时此效果才会发生。

- [图:NBT列表/JSON数组]<带谓词的值效果型组件命名空间ID（在下表中列出）>：该组件可设定多个值效果，每个值效果都可以设定一个谓词充当该效果的触发条件。 - [图:NBT复合标签/JSON对象]：一个封装了谓词的值效果。 - [图:NBT复合标签/JSON对象]*effect：一个值效果。 - 该值效果的子标签。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

带谓词的值效果型组件如下表：

### 带目标和谓词的值效果型

带目标和谓词的值效果型的组件不仅可以为每个值效果指定一个生效条件，还可以为每个值效果指定在攻击时还是被攻击时生效。

带目标和条件的值效果型组件只有一个：
```
equipment_drops
```

，影响被杀死的实体的物品掉落概率。

- [图:NBT列表/JSON数组]minecraft:equipment_drops - [图:NBT复合标签/JSON对象]：一个封装了目标和谓词的值效果。 - [图:NBT复合标签/JSON对象]*effect：一个值效果。 - 该值效果的子标签。 - [图:字符串]*enchanted：指定该效果在攻击时还是被攻击时生效，即该物品所在的实体为攻击者（ ``` attacker ``` ）还是被攻击者（ ``` victim ``` ）时才生效。值必须为： ``` attacker ``` ——主动进行攻击的源发实体，意味着装备有此物品并直接或间接攻击而杀死一个实体时，该效果生效； ``` victim ``` ——被攻击而受伤的实体，意味着装备有此物品并被其他实体杀死时，该效果生效。必须在有效槽位（[图:NBT列表/JSON数组]slots）内装备此物品，该效果才生效。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

## 实体效果型组件

实体效果型的魔咒效果组件，由实体在特定场景中触发后会执行若干个实体效果。其命名空间ID指明了触发场景。

有些实体效果型组件是装备此物品时对生物造成影响，只有当装备在了有效装备槽位（[图:NBT列表/JSON数组]slots字段）时才发挥作用；有些实体效果型组件是在使用此物品时对生物造成影响，忽略[图:NBT列表/JSON数组]slots字段。详见下方各表。

### 带谓词的实体效果型

带谓词的实体效果型组件指定多个实体效果，且可以为每个实体效果指定一个生效条件，仅当这个约束条件满足时此效果才会发生。

- [图:NBT列表/JSON数组]<带谓词的实体效果型组件命名空间ID（在下表中列出）>：该组件可设定多个实体效果，每个实体效果都可设定其生效所必须要满足的谓词。 - [图:NBT复合标签/JSON对象]：一个封装了谓词的实体效果。 - [图:NBT复合标签/JSON对象]*effect：一个实体效果。 - 该实体效果的子标签。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

带谓词的实体效果型组件如下表：

### 带目标和谓词的实体效果型

带目标和谓词的实体效果型组件不仅可以为每个实体效果指定一个谓词，还可以为每个实体效果指定附有此魔咒的物品在谁身上触发、在谁身上生效。

带目标和谓词的实体效果型组件只有一个：
```
post_attack
```

。

- [图:NBT列表/JSON数组]minecraft:post_attack - [图:NBT复合标签/JSON对象]：一个封装了目标和谓词的实体效果。 - [图:NBT复合标签/JSON对象]*effect：一个实体效果。 - 该实体效果的子标签。 - [图:字符串]*affected：指定该效果的作用对象，可以为 ``` attacker ``` （伤害的源发实体）、 ``` damaging_entity ``` （伤害的直接实体）、 ``` victim ``` （受伤实体）。 - [图:字符串]*enchanted：指定该效果在攻击时还是被攻击时触发，即使用该物品的实体为攻击者（ ``` attacker ``` ）还是被攻击者（ ``` victim ``` ）时才触发。值必须为： ``` attacker ``` ——意味着伤害的源发实体若为生物，使用此物品攻击一个实体时触发此效果（箭或三叉戟伤害实体时，只触发箭和三叉戟上的此效果组件，而非触发弓上的；其他弹射物伤害实体时，只触发主手上的，而非此弹射物上的），前提是[图:NBT列表/JSON数组]slots字段必须包含主手； ``` victim ``` ——意味着生物装备有此物品并被攻击时，此效果被触发，前提条件是此物品必须在有效槽位（[图:NBT列表/JSON数组]slots）内。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

## 位置依赖效果型组件

位置依赖效果型组件当生物所在的方块位置发生变动时触发，执行若干个位置依赖效果。位置依赖效果可以是一个实体效果，也可以是一个属性效果。

位置依赖效果型组件是装备此物品时对生物造成影响，只有当装备在了有效装备槽位（[图:NBT列表/JSON数组]slots字段）时才发挥作用。

位置依赖效果型组件只有一个：
```
location_changed
```

。

- [图:NBT列表/JSON数组]minecraft:location_changed - [图:NBT复合标签/JSON对象]：一个封装了谓词的位置依赖效果。 - [图:NBT复合标签/JSON对象]*effect：一个位置依赖效果。 - 该位置依赖效果的子标签。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

## 伤害免疫组件

伤害免疫组件使生物对伤害免疫。可指定多个生效条件，只要有一个条件满足即可生效。

伤害免疫组件是装备此物品时对生物造成影响，只有当装备在了有效装备槽位（[图:NBT列表/JSON数组]slots字段）时才发挥作用。

伤害免疫组件只有一个：
```
damage_immunity
```

。

- [图:NBT列表/JSON数组]minecraft:damage_immunity - [图:NBT复合标签/JSON对象]：一个条件。 - [图:NBT复合标签/JSON对象]*effect： ``` {} ``` 。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]requirements：此效果生效需满足的谓词，不能引用单独的谓词文件和使用位置信息谓词语法检查所处的结构片段。各组件使用的战利品上下文在下方表格中列出。 - 见战利品表谓词。

## 其他魔咒效果组件

### 属性效果组件

属性效果组件用于为装备此物品的生物提供临时性的属性修饰符，物品需装备在[图:NBT列表/JSON数组]slots中才生效。

属性效果组件只有一个：
```
attributes
```

。

- [图:NBT列表/JSON数组]minecraft:attributes - [图:NBT复合标签/JSON对象]：一个属性效果。 - 见属性效果。

### 弩装载声音组件

弩装载声音组件用于修改弩装载过程中的3种声音。

弩装载声音组件只有一个：
```
crossbow_charging_sounds
```

。

- [图:NBT列表/JSON数组]minecraft:crossbow_charging_sounds：按照数组的顺序，第一个元素代表等级I时的声音，第二个元素代表等级II的声音，如果等级超过数组大小则使用数组的最后一个元素。若多个魔咒均有此组件，魔咒等级高的优先生效。 - [图:NBT复合标签/JSON对象]：一项装载声音集合。 - [图:字符串][图:NBT复合标签/JSON对象]start：弩装载过程超过20%时发出的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]mid：弩装载过程超过50%时发出的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串][图:NBT复合标签/JSON对象]end：弩发射时发出的声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source

### 单元组件

单元组件是没有额外数据的魔咒效果组件，只要魔咒定义中存在此组件即可生效。

- [图:NBT复合标签/JSON对象]<单元组件命名空间ID>： ``` {} ```

### 声音事件组件

声音事件组件是修改声音事件的组件。

声音事件组件只有一个：
```
trident_sound
```

，用于修改三叉戟发射时的声音。

- [图:NBT列表/JSON数组]minecraft:trident_sound：按照数组的顺序，第一个元素代表等级I时的声音，第二个元素代表等级II的声音，如果等级超过数组大小则使用数组的最后一个元素。若多个魔咒均有此组件，魔咒等级高的优先生效。 - [图:字符串][图:NBT复合标签/JSON对象]：一个声音事件。 - - 声音事件，见Template:Nbt inherit/sound event/source

# 魔咒效果

不同的魔咒效果组件所修改的对象不同，有些是比较纯粹的“数值”，有些是“实体”等，故魔咒效果根据修改对象不同可分为几个大类，每类效果又有自己的“行为类型”——对同一种对象可以有不同的处理方式。

所有魔咒效果的数据格式可以概括为：

- [图:NBT复合标签/JSON对象]：魔咒效果根节点 - [图:字符串]*type：（命名空间ID）该魔咒效果的类型。魔咒效果类型决定了该魔咒效果所发生的具体行为。 - 与该类魔咒效果具体行为相关的字段。由[图:字符串]type的值所决定。见下文。

## 值效果

这类魔咒效果都有一个输入值，并输出一个计算值。

以下，设valueEffectOutput(x)表示输入值为x的值效果的输出值，levelFunction(level)表示输入魔咒等级为level的等级依赖函数的输出值。

### all_of

依次执行每个值效果最后输出。即：valueEffectOutput(x)=valueEffectOutputn(…valueEffectOutput1(valueEffectOutput0(x)))。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` all_of ``` - [图:NBT列表/JSON数组]*effects：（不能为空）按照顺序依次执行各个值效果。将输入值作为第一个值效果的输入，再使上一个值效果的输出作为下一个值效果的输入，并输出最后值效果的输出。 - [图:NBT复合标签/JSON对象]：其中一个值效果。 - 值效果子标签，形成递归结构。

### add

使用指定值与输入值相加后输出。即：valueEffectOutput(x)=x+levelFunction(level)。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` add ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*value：与输入值相加的值。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### multiply

使用指定值与输入值相乘后输出。即：valueEffectOutput(x)=x×levelFunction(level)。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` multiply ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*factor：与输入值相乘的值。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### set

不使用输入值直接输出指定值。即：valueEffectOutput(x)=levelFunction(level)。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` set ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*value：输出值。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### remove_binomial

使用二项分布减少输入值。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` remove_binomial ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*chance：每次独立的概率运算时，有多大的概率对输入值减1。如果此值为c，输入值为i，则输出的数学期望为i−c⌈i⌉。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### exponential

将输入值与幂指函数形式的等级依赖函数相乘后输出。即：valueEffectOutput(x)=x×base(level)exponent(level)，其中base(level)代表作为底数的等级依赖函数，exponent(level)代表作为指数的等级依赖函数。

- [图:NBT复合标签/JSON对象]：值效果根节点 - [图:字符串]type： ``` exponential ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*base：作为底数的等级依赖函数。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*exponent：作为指数的等级依赖函数。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

## 实体效果

### all_of

按照顺序依次应用各个实体效果。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` all_of ``` - [图:NBT列表/JSON数组]*effects：（不能为空）按照顺序依次执行各个实体效果。 - [图:NBT复合标签/JSON对象]：其中一个实体效果。 - 实体效果子标签，形成递归结构。

### apply_exhaustion

增加玩家的消耗度。只对玩家有实际作用。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` apply_exhaustion ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*amount：消耗度的值。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### apply_impulse

为目标实体施加一个冲量。该冲量将被直接添加到当前实体的移动变化量Delta Movement（[图:NBT列表/JSON数组]Motion）上，这意味着可通过多次应用该魔咒效果叠加移动速度。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` apply_impulse ``` - [图:NBT列表/JSON数组]*direction：（元素数量为3）冲量在局部坐标上的方向。三个元素依次代表冲量在实体左方、上方和前方方向上的大小。 - [图:双精度浮点数]：这一个方向上的缩放大小。 - [图:NBT列表/JSON数组]*coordinate_scale：（元素数量为3）冲量在世界坐标上的方向。三个元素依次代表冲量在X轴、Y轴和Z轴方向上的大小。 - [图:双精度浮点数]：这一个方向上的缩放大小。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*magnitude：冲量级别。此值将经过局部坐标和世界坐标两次缩放后作为最终冲量的分量。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### apply_mob_effect

若作用实体为生物，对其施加随机倍率、随机时长的状态效果。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` apply_mob_effect ``` - [图:字符串][图:NBT列表/JSON数组]*to_apply：一个或多个状态效果（可以用 [图:字符串]字符串指定一个状态效果的命名空间ID；若要指定多个状态效果，可以用 [图:字符串]字符串指定一个带有 ``` # ``` 前缀的标签，或指定一个 [图:NBT列表/JSON数组]数组，数组中的元素应为 [图:字符串] 命名空间ID字符串）表示要施加的状态效果。如果状态效果不止一个，则施加时会随机挑选一个。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*min_amplifier：状态效果的最小倍率。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*max_amplifier：状态效果的最大倍率。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*min_duration：状态效果的最短持续时间，以秒为单位。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*max_duration：状态效果的最长持续时间，以秒为单位。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### change_item_damage

修改当前物品的耐久度。计算结果为正值时将减少物品耐久度，为负值时将增加物品耐久度。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` change_item_damage ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*amount：要修改的耐久度。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### damage_entity

对作用实体进行随机大小的伤害。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` damage_entity ``` - [图:字符串]*damage_type：（命名空间ID）此伤害使用的伤害类型。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*max_damage：最大伤害。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*min_damage：最小伤害。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### explode

根据作用位置发生爆炸。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` explode ``` - [图:NBT复合标签/JSON对象]*large_particle：爆炸产生的大型粒子。如果爆炸威力大于等于2，并且爆炸会影响方块，则生成该粒子。 - 见粒子数据格式。 - [图:NBT复合标签/JSON对象]*small_particle：爆炸产生的小型粒子。如果爆炸威力小于2，或者爆炸不影响方块，则生成该粒子。 - 见粒子数据格式。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*radius：爆炸威力。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:字符串][图:NBT复合标签/JSON对象]*sound：爆炸产生的声音。可以为声音事件的命名空间ID或实例化声音事件的详细数据。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:字符串]*block_interaction：爆炸与方块之间的交互模式。可以为 ``` none ``` （不进行任何交互行为）、 ``` block ``` （类似床类的方块爆炸行为）、 ``` mob ``` （类似苦力怕类的实体爆炸行为）、 ``` tnt ``` （类似TNT类的爆炸行为）或 ``` trigger ``` （类似风弹的触发方块行为）。 - [图:布尔型]attribute_to_user：（默认为 ``` false ``` ）是否将此效果的作用实体设为爆炸来源实体。若为 ``` false ``` ，则爆炸无来源实体。 - [图:布尔型]create_fire：（默认为 ``` false ``` ）爆炸是否在周围创造火方块。 - [图:字符串]damage_type：（命名空间ID）此爆炸使用的伤害类型。如果指定，则使用爆炸来源实体作为伤害来源的源发实体和直接实体；若爆炸无来源实体则伤害不来源于实体，而有伤害来源位置。如果不指定，则使用默认伤害来源，即，若爆炸来源实体作为直接实体，其所有者作为源发实体；若存在爆炸来源实体及其所有者，则使用 ``` player_explosion ``` 伤害类型，否则使用 ``` explosion ``` 伤害类型；若无爆炸来源实体，则伤害不来源于实体，且也没有伤害来源位置。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]knockback_multiplier：（默认为1）被爆炸击退的实体的击退速度乘数。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:字符串][图:NBT列表/JSON数组]immune_blocks：一个或多个方块（可以用 [图:字符串]字符串指定一个方块的命名空间ID；若要指定多个方块，可以用 [图:字符串]字符串指定一个带有 ``` # ``` 前缀的标签，或指定一个 [图:NBT列表/JSON数组]数组，数组中的元素应为 [图:字符串] 命名空间ID字符串）。不受此次爆炸影响的方块——它们的爆炸抗性会被视为3600000。 - [图:NBT列表/JSON数组]offset：（默认为 ``` [0, 0, 0] ``` ）爆炸相对于效果作用位置的偏移。 - [图:双精度浮点数]：在X轴上的相对偏移。 - [图:双精度浮点数]：在Y轴上的相对偏移。 - [图:双精度浮点数]：在Z轴上的相对偏移。 - [图:NBT列表/JSON数组]block_particles：指定爆炸时生成的方块粒子。 - [图:NBT复合标签/JSON对象] - [图:整型]*weight：（值≥1）选择此粒子的权重。 - [图:NBT复合标签/JSON对象]*particle：要生成的粒子。 - 见粒子数据格式。 - [图:单精度浮点数]scaling：（默认为1）指定粒子渲染区域的缩放。默认为距爆炸中心爆炸半径距离的区域，值越小粒子可出现的区域越小。 - [图:单精度浮点数]speed：（默认为1）指定粒子的初速度。

### ignite

使作用实体着火。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` ignite ``` - [图:单精度浮点数][图:NBT复合标签/JSON对象]*duration：设置实体的剩余着火时间，以秒为单位。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source

### play_sound

在作用位置处，以作用实体确定声音来源类型（用于选项中的音量控制），播放声音事件。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` play_sound ``` - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*sound：要播放的声音。可以为单个声音，也可以为一个声音的列表。如果指定一个列表，则根据魔咒等级选取声音，超出列表上限的等级使用列表的最后一个元素。 - - 声音事件，见Template:Nbt inherit/sound event/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*pitch：（0.00001≤值≤2）声音的音高。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*volum：（0.00001≤值≤10）声音的音量。 - - 浮点提供器，见Template:Nbt inherit/float provider/source

### replace_block

替换一个方块。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` replace_block ``` - [图:NBT复合标签/JSON对象]*block_state：要替换成的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT列表/JSON数组]offset：（默认为 ``` [0, 0, 0] ``` ）方块相对于作用位置的偏移。 - [图:整型]：在X轴上的相对偏移。 - [图:整型]：在Y轴上的相对偏移。 - [图:整型]：在Z轴上的相对偏移。 - [图:NBT复合标签/JSON对象]predicate：若指定本字段，则检查指定位置上的方块是否满足条件，满足条件时进行替换。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:字符串]trigger_game_event：替换方块时产生的游戏事件。游戏会将使用此魔咒的实体视为创造此游戏事件的实体。

### replace_disk

替换实体周围的一个圆柱形状内的所有方块。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` replace_disk ``` - [图:NBT复合标签/JSON对象]*block_state：要替换成的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*height：圆柱的高度。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:NBT列表/JSON数组]offset：（默认为 ``` [0, 0, 0] ``` ）圆柱底面中心方块相对于作用位置的偏移。 - [图:整型]：在X轴上的相对偏移。 - [图:整型]：在Y轴上的相对偏移。 - [图:整型]：在Z轴上的相对偏移。 - [图:NBT复合标签/JSON对象]predicate：若指定本字段，则检查指定位置上的方块是否满足条件，满足条件时进行替换。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*radius：圆柱的半径。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:字符串]trigger_game_event：替换每个方块时产生的游戏事件。游戏会将使用此魔咒的实体视为创造此游戏事件的实体。

### run_function

运行指定的函数，以作用实体为命令执行者，以作用位置为命令执行位置，以作用实体的朝向为执行朝向，权限等级为2级。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` run_function ``` - [图:字符串]*function：（命名空间ID）要运行的函数。

### set_block_properties

设置一个方块的方块属性。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` set_block_properties ``` - [图:NBT列表/JSON数组]offset：（默认为 ``` [0, 0, 0] ``` ）目标方块相对于作用位置的偏移。 - [图:整型]：在X轴上的相对偏移。 - [图:整型]：在Y轴上的相对偏移。 - [图:整型]：在Z轴上的相对偏移。 - [图:NBT复合标签/JSON对象]*properties：要设置的方块属性和对应的值。 - [图:字符串]<方块属性>：设置指定的方块属性。 - [图:字符串]trigger_game_event：设置方块属性时产生的游戏事件。游戏会将使用此魔咒的实体视为创造此游戏事件的实体。

### spawn_particles

生成单个粒子。

实际上，[图:NBT复合标签/JSON对象]horizontal_velocity、[图:NBT复合标签/JSON对象]vertical_velocity和[图:单精度浮点数][图:NBT复合标签/JSON对象]speed并非粒子的初速度，而是将计算的“初速度”结果作为传入粒子的三个参数，即，将X轴的[图:NBT复合标签/JSON对象]horizontal_velocity、Y轴的[图:NBT复合标签/JSON对象]vertical_velocity、Z轴的[图:NBT复合标签/JSON对象]horizontal_velocity三个值分别乘上[图:单精度浮点数][图:NBT复合标签/JSON对象]speed后作为三个参数传入粒子。这相当于
```
<count>
```

设为0的
```
/
particle
```

命令，三个参数的影响详见
```
/
particle
```

命令。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` spawn_particles ``` - [图:NBT复合标签/JSON对象]*particle：要生成的粒子。 - 见粒子数据格式。 - [图:NBT复合标签/JSON对象]*horizontal_position：粒子生成的水平位置。 - [图:字符串]*type：位置来源类型，设置位置的计算方式。可以为 ``` entity_position ``` （位于作用位置上）或 ``` in_bounding_box ``` （假设作用实体碰撞箱的底面中心在作用位置，在实体碰撞箱内随机选点）。 - [图:单精度浮点数]scale：（值>0，默认为1）放缩实体碰撞箱大小。当[图:字符串]type为 ``` entity_position ``` 时无效果。 - [图:单精度浮点数]offset：（默认为0）在位置来源计算后，对结果进行偏移。 - [图:NBT复合标签/JSON对象]*vertical_position：粒子生成的垂直位置。 - [图:字符串]*type：位置来源类型，设置位置的计算方式。可以为 ``` entity_position ``` （位于作用位置上）或 ``` in_bounding_box ``` （假设作用实体碰撞箱的底面中心在作用位置，在实体碰撞箱内随机选点）。 - [图:单精度浮点数]scale：（值>0，默认为1）放缩实体碰撞箱大小。当[图:字符串]type为 ``` entity_position ``` 时无效果。 - [图:单精度浮点数]offset：（默认为0）在位置来源计算后，对结果进行偏移。 - [图:NBT复合标签/JSON对象]*horizontal_velocity：粒子的水平初速度。X和Z轴的值分别计算，相互独立。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]base：（默认为0）基础初速度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]movement_scale：（默认为0）初速度受作用实体的速度的影响，当为0时实体速度不影响初速度，此值不为0时初速度会加上实体速度与此值的乘积。 - [图:NBT复合标签/JSON对象]*vertical_velocity：粒子的垂直初速度。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]base：（可默认为0）基础初速度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]movement_scale：（默认为0）初速度受作用实体的速度的影响，当为0时实体速度不影响初速度，此值不为0时初速度会加上实体速度与此值的乘积。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]speed：（默认为0）粒子初速度的乘数。 - - 浮点提供器，见Template:Nbt inherit/float provider/source

### summon_entity

在作用位置生成一个实体。如果是闪电束且使魔咒生效的实体为玩家，则此闪电能够触发
```
channeled_lightning
```

进度准则。

X或Z轴坐标若超过[-30000000, 30000000)区间，Y轴坐标若超过[-20000000, 20000000)区间，则无法生成实体。

- [图:NBT复合标签/JSON对象]：实体效果根节点 - [图:字符串]type： ``` summon_entity ``` - [图:字符串][图:NBT列表/JSON数组]*entity：一个或多个实体类型（可以用 [图:字符串]字符串指定一个实体类型的命名空间ID；若要指定多个实体类型，可以用 [图:字符串]字符串指定一个带有 ``` # ``` 前缀的标签，或指定一个 [图:NBT列表/JSON数组]数组，数组中的元素应为 [图:字符串] 命名空间ID字符串）指定要生成的实体类型。当指定的实体类型不止一个时，会随机挑选一个进行生成。 - [图:字符串]：实体的命名空间ID。 - [图:布尔型]join_team：（默认为 ``` false ``` ）实体生成时是否加入此效果的作用实体的队伍。

## 位置依赖效果

位置依赖效果是用于位置依赖效果型组件的魔咒效果，位置依赖效果包括实体效果和属性效果。

- [图:NBT复合标签/JSON对象]：位置依赖效果根节点 - [图:字符串]*type：位置依赖效果类型。可以为 ``` all_of ``` 、 ``` attribute ``` 或实体效果类型。 - - 如果[图:字符串]type为 ``` all_of ``` ，则执行多个位置依赖效果，各个位置依赖效果按照顺序依次应用。 - [图:NBT列表/JSON数组]*effects：（不能为空）按照顺序依次执行各个位置依赖效果。 - [图:NBT复合标签/JSON对象]：其中一个位置依赖效果。 - 位置依赖效果子标签，形成递归结构。 - - 如果[图:字符串]type为一个实体效果类型，则执行实体效果。 - 对应的实体效果的附加字段，见上文。 - - 如果[图:字符串]type为 ``` attribute ``` ，则执行属性效果。 - 与属性效果内容相同，见下文。

## 属性效果

属性效果可以为生物添加临时属性修饰符，即可以生效但无法导出的属性修饰符。

其中[图:字符串]id定义的属性修饰符并不是游戏计算属性时使用的修饰符，设此值填写为
```
<
命名空间
>:<
标识符
>
```

，游戏真正使用的属性修饰符为
```
<
命名空间
>:<
标识符
>/<
装备槽位
>
```

，即不同的有效槽位的物品提供的属性修饰效果可以叠加。

- [图:NBT复合标签/JSON对象]：属性效果根节点 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*amount：计算中修饰符调整基础值的数值。 - - 等级依赖函数，见Template:Nbt inherit/level based value/source - [图:字符串]*attribute：（命名空间ID）一个属性。 - [图:字符串]*id：（命名空间ID）此属性效果使用的属性修饰符。 - [图:字符串]*operation：此属性修饰符的运算模式。可以为 ``` add_value ``` （增量操作，Op0）、 ``` add_multiplied_base ``` （倍率操作，Op1）或 ``` add_multiplied_total ``` （最终倍乘操作，Op2）。

# 历史

# 参考

1. ↑ MC-273376

# 导航

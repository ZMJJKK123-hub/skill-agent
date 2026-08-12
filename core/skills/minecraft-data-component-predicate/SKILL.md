---
name: minecraft-data-component-predicate
description: |
  数据组件谓词（Minecraft Wiki 中文版全量正文）。
  
  【概述】数据组件谓词（Data Component Predicate），也称组件谓词（Component Predicate），是用于测试数据组件是否满足某种条件的谓词。
  
  【涵盖内容】
  - 进度
  - 命令
  - 物品模型
  - attribute_modifiers
  - bundle_contents
  - container
  - custom_data
  - damage
  - enchantments
  - firework_explosion
  - fireworks
  - jukebox_playable
  
  【关键定义】
  - 数据包路径：data/villager/variant
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 数据组件谓词 的完整规范时
---

本条目所述内容仅适用于Java版。
数据组件谓词（Data Component Predicate），也称组件谓词（Component Predicate），是用于测试数据组件是否满足某种条件的谓词。

# 使用

游戏为数据组件谓词定义了多种格式，但不论是哪种格式，都需要指定数据组件谓词类型和谓词内容。本文以进度及谓词相关数据包文件中的格式展示语法。

## 进度

在进度谓词系统中，数据组件谓词可以用来测试物品、方块实体和实体的数据组件。其格式为多个
```
<
数据组件谓词ID
>: <
检测内容
>
```

键值对的集合。

- [图:NBT复合标签/JSON对象] 准则谓词根节点 - [图:NBT复合标签/JSON对象]predicates - [图:任意类型]<数据组件谓词ID>： ``` < 检测内容 > ```

## 命令

数据组件谓词可以在
```
minecraft:item_predicate
```

参数类型中测试物品，此参数类型的测试项可以是
```
<
数据组件谓词ID
>~<
检测内容
>
```

。详见参数类型 § item_predicate。

## 物品模型

数据组件谓词可以在物品模型映射中使用，为物品提供模型选择。此时谓词类型和谓词内容单独存在。

- [图:NBT复合标签/JSON对象]model - [图:字符串]predicate： ``` < 数据组件谓词ID > ``` - [图:任意类型]value： ``` < 检测内容 > ```

# 数据格式

数据组件谓词可以分为测试组件自身的存在性和测试组件的值是否满足某种条件两类谓词。

对于测试组件存在性的谓词，其标签名可以是所有数据组件的ID。由于目前数据组件谓词类型的ID和数据组件的ID重合，对于同名的谓词，游戏会优先将其推断为数据组件谓词类型的ID以测试具体的值，再尝试以数据组件的ID测试组件的存在性，而如果组件谓词本身无法接受这种格式则无法以这种格式测试组件的存在性。

- [图:NBT复合标签/JSON对象]<数据组件ID>：空标签，测试此组件是否存在。

例如：
```
{"predicates": {"minecraft:instrument": {}}}
```

可以测试物品是否具有
```
instrument
```

组件，不需要关注此组件及其值是否能序列化，也不需要关注此组件的具体值。而
```
{"predicates": {"minecraft:potion_contents": {}}}
```

不允许，因为
```
potion_contents
```

是已有的数据组件谓词ID，因此无法测试存在性；而且此谓词也不接受这种格式。

游戏共定义了下列测试数据组件具体值的数据组件谓词：

## attribute_modifiers

检查
```
attribute_modifiers
```

组件中的属性修饰符。

- [图:NBT复合标签/JSON对象]minecraft:attribute_modifiers - [图:NBT复合标签/JSON对象]modifiers：属性修饰符的集合谓词。 - [图:NBT列表/JSON数组]contains：检查是否有属性修饰符符合特定谓词。要求每个谓词都有至少一个属性修饰符符合，一个属性修饰符不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - 属性修饰符集合内容谓词 - [图:整型][图:NBT复合标签/JSON对象]size：检查属性修饰符的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的属性修饰符的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - 属性修饰符集合内容谓词

- - [图:双精度浮点数][图:NBT复合标签/JSON对象]amount：匹配修饰值，或者检测修饰值是否在范围之间。 - - 浮点数界限范围，见Template:Nbt inherit/minmax bounds doubles/source - [图:字符串][图:NBT列表/JSON数组]attribute：匹配的属性。可以为以 ``` # ``` 开头的属性标签、一个属性ID的字符串、或以多个属性ID组成的字符串列表。 - [图:字符串]id：匹配属性修饰符的命名空间ID。 - [图:字符串]operation：匹配属性修饰符操作方法。取值必须从 ``` add_value ``` 、​ ``` add_multiplied_base ``` 和​ ``` add_multiplied_total ``` 中任选其一。 - [图:字符串]slot：匹配属性修饰符生效的装备槽位组。

## bundle_contents

检查
```
bundle_contents
```

组件中的物品堆叠。

- [图:NBT复合标签/JSON对象]minecraft:bundle_contents - [图:NBT复合标签/JSON对象]items：物品堆叠的集合谓词。 - [图:NBT列表/JSON数组]contains：检查是否有物品堆叠符合特定谓词。要求每个谓词都有至少一个物品堆叠符合，一个物品堆叠不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - 物品堆叠谓词 - [图:整型][图:NBT复合标签/JSON对象]size：检查物品堆叠的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的物品堆叠的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - 物品堆叠谓词

- - [图:NBT复合标签/JSON对象]components：检查物品的物品堆叠组件。当物品的组件内容与检测内容完全相同时测试成功。 - [图:任意类型]<物品堆叠组件ID>：一项组件及检测内容。 - [图:整型][图:NBT复合标签/JSON对象]count：检查物品堆叠的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:字符串][图:NBT列表/JSON数组]items：匹配的物品。可以为以 ``` # ``` 开头的物品标签、一个物品ID的字符串、或以多个物品ID组成的字符串列表。 - [图:NBT复合标签/JSON对象]predicates：检查物品的某个物品堆叠组件是否满足某种条件。 - [图:任意类型]<数据组件谓词类型ID>：一个组件的检查。具体格式详见数据组件谓词。

## container

检查
```
container
```

组件中的物品堆叠。

- [图:NBT复合标签/JSON对象]minecraft:container - [图:NBT复合标签/JSON对象]items：物品堆叠的集合谓词。 - [图:NBT列表/JSON数组]contains：检查是否有物品堆叠符合特定谓词。要求每个谓词都有至少一个物品堆叠符合，一个物品堆叠不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - 物品堆叠谓词 - [图:整型][图:NBT复合标签/JSON对象]size：检查物品堆叠的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的物品堆叠的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - 物品堆叠谓词

- - [图:NBT复合标签/JSON对象]components：检查物品的物品堆叠组件。当物品的组件内容与检测内容完全相同时测试成功。 - [图:任意类型]<物品堆叠组件ID>：一项组件及检测内容。 - [图:整型][图:NBT复合标签/JSON对象]count：检查物品堆叠的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:字符串][图:NBT列表/JSON数组]items：匹配的物品。可以为以 ``` # ``` 开头的物品标签、一个物品ID的字符串、或以多个物品ID组成的字符串列表。 - [图:NBT复合标签/JSON对象]predicates：检查物品的某个物品堆叠组件是否满足某种条件。 - [图:任意类型]<数据组件谓词类型ID>：一个组件的检查。具体格式详见数据组件谓词。

## custom_data

检查
```
custom_data
```

组件的自定义数据。

可以为一个JSON对象或NBT复合标签，也可以为字符串。如果是字符串，则将此字符串视为SNBT，游戏将在解析时自动将字符串转换为对应的NBT数据。

- [图:字符串][图:NBT复合标签/JSON对象]minecraft:custom_data：测试格式参见NBT格式 § 测试NBT标签和NBT格式 § 转换。

## damage

检查
```
damage
```

和
```
max_damage
```

组件，即物品的剩余耐久度或损坏值。损坏值来自
```
damage
```

组件，剩余耐久度来自
```
max_damage
```

组件减去
```
damage
```

组件。
```
max_damage
```

组件不存在时被视为0。

- [图:NBT复合标签/JSON对象]minecraft:damage - [图:整型][图:NBT复合标签/JSON对象]damage：检查物品的损坏值。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:整型][图:NBT复合标签/JSON对象]durability：检查物品的剩余耐久度。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source

## enchantments

检查
```
enchantments
```

组件的魔咒。

- [图:NBT列表/JSON数组]minecraft:enchantments：条件的数组。其中的每一个条件都必须满足。 - [图:NBT复合标签/JSON对象]：一个条件。 - [图:字符串][图:NBT列表/JSON数组]enchantments：要检查的魔咒。可以为单个魔咒ID、一个魔咒ID的列表或一个魔咒标签。若指定了多个魔咒，只需有其中一个魔咒存在即测试成功。 - [图:整型][图:NBT复合标签/JSON对象]levels：检查魔咒的同时检查对应魔咒的等级。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。若指定了多个魔咒，存在其中一个魔咒的等级符合即可成功。如果[图:字符串][图:NBT列表/JSON数组]enchantments字段不存在，则该物品存在任一魔咒的等级符合即可成功。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source

## firework_explosion

检查
```
firework_explosion
```

组件的烟火之星爆裂效果。

- [图:NBT复合标签/JSON对象]minecraft:firework_explosion - [图:NBT列表/JSON数组]contains：检查是否有烟火之星爆裂符合特定谓词。要求每个谓词都有至少一个烟火之星爆裂符合，一个烟火之星爆裂不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - 烟火谓词 - [图:整型][图:NBT复合标签/JSON对象]size：检查烟火之星爆裂的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的烟火之星爆裂的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - 烟火谓词

- - [图:布尔型]has_trail：检测烟火是否有拖曳痕迹（使用钻石合成时）。 - [图:布尔型]has_twinkle：检测烟火是否出现闪烁效果（使用荧石粉合成时）。 - [图:字符串]shape：检测烟火的爆裂形状是否为指定形状。可以为 ``` small_ball ``` 、​ ``` large_ball ``` 、​ ``` star ``` 、​ ``` creeper ``` 和​ ``` burst ``` 。

## fireworks

检查
```
fireworks
```

组件的烟花火箭数据。

- [图:NBT复合标签/JSON对象]minecraft:fireworks - [图:NBT复合标签/JSON对象]explosions：烟火之星爆裂效果的集合谓词。 - [图:NBT列表/JSON数组]contains：检查是否有烟火之星爆裂符合特定谓词。要求每个谓词都有至少一个烟火之星爆裂符合，一个烟火之星爆裂不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - 烟火谓词 - [图:整型][图:NBT复合标签/JSON对象]size：检查烟火之星爆裂的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的烟火之星爆裂的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - 烟火谓词 - [图:整型][图:NBT复合标签/JSON对象]flight_duration：检测烟花火箭的飞行的时间，单位为“火药”（即表现为和在工作台上合成烟花火箭时所用的火药数相等）。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source

- - [图:布尔型]has_trail：检测烟火是否有拖曳痕迹（使用钻石合成时）。 - [图:布尔型]has_twinkle：检测烟火是否出现闪烁效果（使用荧石粉合成时）。 - [图:字符串]shape：检测烟火的爆裂形状是否为指定形状。可以为 ``` small_ball ``` 、​ ``` large_ball ``` 、​ ``` star ``` 、​ ``` creeper ``` 和​ ``` burst ``` 。

## jukebox_playable

检查
```
jukebox_playable
```

组件的音乐唱片音乐信息。

- [图:NBT复合标签/JSON对象]minecraft:jukebox_playable - [图:字符串][图:NBT列表/JSON数组]song：要测试的唱片机曲目。可以为一个唱片机曲目ID、一个唱片机曲目的列表或一个唱片机曲目标签。若指定的唱片机曲目包含物品的唱片机曲目，则测试成功。

## potion_contents

检查
```
potion_contents
```

组件的药水效果。仅检查[图:字符串]potion和[图:NBT列表/JSON数组]custom_effects字段，其余数据不会被检测。

Java版26.3前：

- [图:字符串][图:NBT列表/JSON数组]minecraft:potion_contents：要测试的药水效果。可以为一个药水效果ID、一个药水效果的列表或一个药水效果标签。若指定的药水效果包含 ``` potion_contents ``` 组件的[图:字符串]potion字段的药水效果，则测试成功。

Java版26.3起：

- [图:NBT复合标签/JSON对象]minecraft:potion_contents - [图:字符串][图:NBT列表/JSON数组]potions：要检查的药水效果。可以为单个药水效果ID、一个药水效果ID的列表或一个药水效果标签。若指定了多个药水效果，只需有其中一个药水效果存在即测试成功。 - [图:NBT复合标签/JSON对象]effects：要检查的状态效果。 - [图:NBT列表/JSON数组]contains：检查是否有状态效果符合特定谓词。要求每个谓词都有至少一个状态效果符合，一个状态效果不必符合所有谓词。 - [图:NBT复合标签/JSON对象]：一个谓词。 - - - 状态效果谓词，见Template:Nbt inherit/mob effects predicate/source - [图:整型][图:NBT复合标签/JSON对象]size：检查状态效果的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的状态效果的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT复合标签/JSON对象]test：一个谓词。 - - - 状态效果谓词，见Template:Nbt inherit/mob effects predicate/source

## stored_enchantments

检查
```
stored_enchantments
```

组件的魔咒。

- [图:NBT列表/JSON数组]minecraft:stored_enchantments：条件的数组。其中的每一个条件都必须满足。 - [图:NBT复合标签/JSON对象]：一个条件。 - [图:字符串][图:NBT列表/JSON数组]enchantments：要检查的魔咒。可以为单个魔咒ID、一个魔咒ID的列表或一个魔咒标签。若指定了多个魔咒，只需有其中一个魔咒存在即可测试成功。 - [图:整型][图:NBT复合标签/JSON对象]levels：检查魔咒的同时检查对应魔咒的等级。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。若指定了多个魔咒，存在其中一个魔咒的等级符合即可成功。如果[图:字符串][图:NBT列表/JSON数组]enchantments字段不存在，则该物品存在任一魔咒的等级符合即可成功。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source

## trim

检查
```
trim
```

组件的盔甲纹饰数据。此检查只检测命名空间ID，内联数据永远测试失败。

- [图:NBT复合标签/JSON对象]minecraft:trim - [图:字符串][图:NBT列表/JSON数组]material：要检查的盔甲纹饰材料。可以为单个盔甲纹饰材料ID、一个盔甲纹饰材料ID的列表或一个盔甲纹饰材料标签。若指定的盔甲纹饰材料包含所检测物品的盔甲纹饰材料，则测试成功。 - [图:字符串][图:NBT列表/JSON数组]pattern：要检查的盔甲纹饰图案。可以为单个盔甲纹饰图案ID、一个盔甲纹饰图案ID的列表或一个盔甲纹饰图案标签。若指定的盔甲纹饰图案包含所检测物品的盔甲纹饰图案，则测试成功。

## villager/variant

检查
```
villager/variant
```

组件的村民类型。

- [图:字符串][图:NBT列表/JSON数组]minecraft:villager/variant：要检查的村民类型。可以为单个村民类型ID、一个村民类型ID的列表或一个村民类型标签。若指定的村民类型包含所检测对象的村民类型，则测试成功。

## writable_book_content

检查
```
writable_book_content
```

组件的书与笔书页信息。若开启过滤，则以未过滤的文本原始信息为准。

- [图:NBT复合标签/JSON对象]minecraft:writable_book_content - [图:NBT复合标签/JSON对象]pages：书页的集合谓词。 - [图:NBT列表/JSON数组]contains：检查是否有书页符合特定谓词。要求每个谓词都有至少一个书页符合，一个书页不必符合所有谓词。 - [图:字符串]：一个谓词。完整匹配一页书的内容，以未过滤的书页原始信息为准。 - [图:整型][图:NBT复合标签/JSON对象]size：检查书页的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的书页的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:字符串]test：一个谓词。完整匹配一页书的内容，以未过滤的书页原始信息为准。

## written_book_content

检查
```
written_book_content
```

组件的成书数据。

- [图:NBT复合标签/JSON对象]minecraft:written_book_content - [图:NBT复合标签/JSON对象]pages：书页的集合谓词。检测书页信息，若开启过滤，则以未过滤的文本原始信息为准。 - [图:NBT列表/JSON数组]contains：检查是否有书页符合特定谓词。要求每个谓词都有至少一个书页符合，一个书页不必符合所有谓词。 - [图:任意类型]：一个谓词。文本组件，完整匹配一页书的内容，以未过滤的书页原始信息为准。 - [图:整型][图:NBT复合标签/JSON对象]size：检查书页的数量。匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:NBT列表/JSON数组]count：统计并检查符合特定谓词的书页的数量。 - [图:NBT复合标签/JSON对象]：一个谓词及要求匹配的数量。 - [图:整型][图:NBT复合标签/JSON对象]count：匹配一个精确值，或者检测数值是否在范围之间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:任意类型]test：一个谓词。文本组件，完整匹配一页书的内容，以未过滤的书页原始信息为准。 - [图:字符串]author：完整匹配书的作者。 - [图:字符串]title：完整匹配书的标题，以未过滤的文本原始信息为准。 - [图:整型][图:NBT复合标签/JSON对象]generation：检测书是否为副本。可以为 ``` 0 ``` （原稿）， ``` 1 ``` （原稿的副本）， ``` 2 ``` （副本的副本）， ``` 3 ``` （破烂不堪）。可匹配单个整型值，也可匹配两个整型值所形成的闭区间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:布尔型]resolved：检测这本成书是否已经被解析，即检测组件中[图:布尔型]resolved的值是否为 ``` true ``` 。

# 历史

# 参考

1. ↑ https://www.minecraft.net/article/minecraft-java-edition-1-21-11

# 导航

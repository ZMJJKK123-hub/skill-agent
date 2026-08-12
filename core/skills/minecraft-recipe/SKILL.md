---
name: minecraft-recipe
description: |
  配方（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是配方系统。关于具体的合成配方，请见“合成 § 完整配方列表”；关于烧炼配方，请见“烧炼 § 配方”；关于药水配方，请见“药水酿造 § 配方”；关于命令，请见“命令/recipe”。
  
  【涵盖内容】
  - 合成配方
  - 有序配方
  - 无序配方
  - 类型转化配方
  - 染色配方
  - 药染配方
  - 定制配方
  - 饰纹陶罐配方
  - 旗帜复制配方
  - 成书复制配方
  - 烟花火箭配方
  - 烟火之星合成配方
  
  【关键定义】
  - 注册表：RECIPE
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 配方 的完整规范时
---

本条目介绍的是配方系统。关于具体的合成配方，请见“合成 § 完整配方列表”；关于烧炼配方，请见“烧炼 § 配方”；关于药水配方，请见“药水酿造 § 配方”；关于命令，请见“命令/recipe”。

此页面被建议拆分为配方和​配方定义格式。 
请勿在中文Wiki的讨论达成共识前进行拆分。

“> 在原版生存模式中，配方的运作方式是这样的：当你手动合成一个配方，或者游戏认为“好了，现在你有了木棍，我们来教你怎么做镐”时，你就“发现”了这个配方。配方一经“发现”就会出现在配方书中，你可以选择在合成界面点击查看它。在那里你可以查看所有已发现的配方以及它们的合成方法，这样就不用再去查询合成形状和材料了。
> 
> 
> 1. ↑ 我之所以说是原版生存模式，是因为这个功能是可以自定义的。例如，自定义地图可以要求你只能合成地图中提供的物品，其他的都不能做。在原版生存模式中，这个功能纯粹是为了帮助你记住不常用的配方，或者教你一些你可能不知道的新配方。

”——Dinnerbone评论于使用配方
 Wiki上有与该主题相关的教程！
见教程:配方。

 Wiki上有与该主题相关的教程！
见教程:配方。

 
配方（Recipe）是一种引导新玩家游玩Minecraft的方式，通过帮助玩家了解合成、烧炼以及其他的方块和物品转化方式来使玩家熟悉游戏。

所有的合成、烧炼、冶炼、营火烹饪、烟熏、锻造、切石、酿造配方都使用配方系统。在基岩版中，制图也使用配方系统。配方大多数是数据驱动的，可被数据包或附加包配置。

# 获取

配方可通过多种方式获得。使用一个配方会使玩家自动发现它。命令
```
/
recipe
```

可以直接给予玩家配方。当玩家达成某些条件，如获取到特定的物品时，也会解锁相应的配方。在Java版中，使用知识之书也可以直接解锁配方。

配方的条件解锁在Java版中由进度控制，待达成进度后通过进度奖励赋予玩家配方；在基岩版中则由配方本身控制。

一旦配方被发现，就将被加入玩家的配方书。已发现的配方储存在玩家的[图:NBT复合标签/JSON对象]recipeBook或[图:NBT复合标签/JSON对象]recipe_unlocking标签中。

# 用途

主条目：配方书
已发现的配方可在玩家的配方书中找到。然而，玩家并不需要发现配方来使用配方，除非开启游戏规则“合成需要配方”（
```
limited_crafting
```

或
```
doLimitedCrafting
```

）。

配方只会在玩家使用与当前配方类型所匹配的方块时显示。例如，烧炼配方将只在熔炉的界面中显示。当在背包中使用配方书时，只有能在玩家的2×2背包合成栏内使用的配方才会显示。

# Java版

配方在游戏中使用
```
RECIPE
```

注册表，数据包路径为
```
recipe
```

，即所有配方定义文件都需要在
```
data/<
命名空间
>/recipe
```

目录下定义。与其他注册项不同，不存在“配方标签”，游戏不会加载
```
data/<
命名空间
>/tags/recipe
```

目录下的文件。

配方定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type：配方类型。 - 依配方类型的额外字段，见下文。

## 合成配方

### 有序配方

代表合成的有序配方（Shaped Recipe）。游戏会自动认为左右对称的排列方式有效。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_shaped ``` 。 - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` building ``` （建筑）、 ``` redstone ``` （红石）、 ``` equipment ``` （装备）和 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:NBT复合标签/JSON对象]*key：一个映射表，用于将字符与合成材料建立关联。字符将用于在[图:NBT列表/JSON数组]*pattern中指定合成图案。 - [图:字符串][图:NBT列表/JSON数组]<键>：表示 ``` < 键 > ``` 所对应的合成材料，可以为单个物品ID、物品ID的列表或一个物品标签。 ``` < 键 > ``` 只能为除了空格 ``` ``` 以外的单字符。 - [图:NBT列表/JSON数组]*pattern：（最大长度为3，不允许空数组，其中所有字符串的长度应一致）合成方格中物品要摆放成的合成图案。其中的每个字符串代表合成方格中的一横行。 - [图:字符串]：（最大长度为3）一个字符串，字符串中的每个字符都应为之前所指定的一个 ``` < 键 > ``` ，可以使用空格 ``` ``` 来表示一个空的合成槽位。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

示例：

```
{

  
"type"
:
 
"minecraft:crafting_shaped"
,

  
"category"
:
 
"misc"
,

  
"key"
:
 
{

    
"A"
:
 
"minecraft:milk_bucket"
,

    
"B"
:
 
"minecraft:sugar"
,

    
"C"
:
 
"minecraft:wheat"
,

    
"E"
:
 
"#minecraft:eggs"

  
},

  
"pattern"
:
 
[

    
"AAA"
,

    
"BEB"
,

    
"CCC"

  
],

  
"result"
:
 
{

    
"count"
:
 
1
,

    
"id"
:
 
"minecraft:cake"

  
}

}
```

### 无序配方

代表合成的无序配方（Shapeless Recipe）。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_shapeless ``` 。 - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` building ``` （建筑）、 ``` redstone ``` （红石）、 ``` equipment ``` （装备）和 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:NBT列表/JSON数组]*ingredients：（1≤数组长度≤9）该配方的原料物品。 - [图:字符串][图:NBT列表/JSON数组]：一项原料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

若无序配方包含9个相同的原料，则游戏内部会认为它等同于一个有序配方，尽管此机制不会对游戏行为有明显影响。

示例：

```
{

  
"type"
:
 
"minecraft:crafting_shapeless"
,

  
"category"
:
 
"equipment"
,

  
"ingredients"
:
 
[

    
"minecraft:iron_ingot"
,

    
"minecraft:flint"

  
],

  
"result"
:
 
{

    
"count"
:
 
1
,

    
"id"
:
 
"minecraft:flint_and_steel"

  
}

}
```

### 类型转化配方

[[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的类型转化配方（Transmute Recipe）。类型转化配方改变物品类型，保留其原有的组件修订，且可以对输出物品继续进行组件修订。

- 当该配方匹配合成原料后，会先复制输入物品，然后修改其物品类型，以在输出中保留相应组件修订。
- 如果指定了输出数量，则修改输出物品的数量。
- 如果指定了组件修订，则在原有组件修订的基础上继续修订。
- 当输入物品与输出物品相同时不生效。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_transmute ``` 。 - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` building ``` （建筑）、 ``` redstone ``` （红石）、 ``` equipment ``` （装备）和 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]*input：输入物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*material：转变时所消耗的辅助材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:整型][图:NBT复合标签/JSON对象]material_count：（默认为 ``` [1,1] ``` ）辅助材料的数量范围。需为 ``` [1,8] ``` 的子区间。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:布尔型]add_material_to_result_count：（默认为 ``` false ``` ）如为 ``` true ``` ，将输出物品的堆叠数增加包含辅助物品的槽位的数目。

### 染色配方

代表合成的染色配方（Dye Recipe），用于给物品染色。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格至少需要有2个物品，否则什么也不会输出。 - 依据合成方格的顺序，第一个 ``` target ``` 原料作为此配方的输入物品。如果有多个 ``` target ``` 原料，则什么也不会输出。 - 合成方格中的其他物品必须符合 ``` dye ``` 原料的物品类型，且具有 ``` dye ``` 组件。
- 合成行为： - 游戏先将 ``` target ``` 原料作为输入物品，并经过类型转化配方的处理方式转化为 ``` result ``` 指定的物品。 - 转化完成后，根据既有的颜色和输入的染料颜色设置新的 ``` dyed_color ``` 组件，作为染色结果。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_dye ``` 。 - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` building ``` （建筑）、 ``` redstone ``` （红石）、 ``` equipment ``` （装备）和 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]*target：表示将要被染色的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*dye：表示作为染料的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 药染配方

[[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]]
[[|]]8888888888888888888888888888888888888888888888
查看JSON文件示例

代表合成的药染配方（Imbue Recipe），用于复制物品的药水效果和自定义状态效果。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格的中心必须是 ``` source ``` 原料，周围一圈8个物品必须是 ``` material ``` 原料。
- 合成行为： - 将 ``` source ``` 原料的 ``` potion_contents ``` 组件复制到 ``` result ``` 结果物品。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_imbue ``` 。 - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` building ``` （建筑）、 ``` redstone ``` （红石）、 ``` equipment ``` （装备）和 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]*source：表示提供药水效果的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*material：表示配方的辅助材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

## 定制配方

定制配方（Custom Recipe），亦作特殊合成配方（Crafting Special Recipe），是部分行为受游戏内部代码直接处理的配方，配方文件只能有限地修改这些配方的合成行为。这些配方不会显示在配方书中，不能被解锁，不受游戏规则“合成需要配方”（
```
limited_crafting
```

）影响。

### 饰纹陶罐配方

[[|]][[|]][[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的饰纹陶罐配方（Decorated Pot Recipe），用于根据饰纹陶罐合成的规则合成物品。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 原料物品必须在合成方格指定的位置上。
- 合成行为： - 游戏先获取 ``` result ``` 指定的物品，然后设置新的 ``` pot_decorations ``` 组件，组件的值来源于原料。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_decorated_pot ``` - [图:字符串][图:NBT列表/JSON数组]*back：表示饰纹陶罐背面的物品，必须在合成方格第一行第二列的位置。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*left：表示饰纹陶罐左侧的物品，必须在合成方格第二行第一列的位置。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*right：表示饰纹陶罐右侧的物品，必须在合成方格第二行第三列的位置。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*front：表示饰纹陶罐前面的物品，必须在合成方格第三行第二列的位置。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 旗帜复制配方

[[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的旗帜复制配方（Banner Duplicate Recipe），用于根据旗帜复制的规则复制图案。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格只能有2个物品堆叠，否则什么也不会输出。 - 依据合成方格的顺序，第一个原料作为提供旗帜图案的物品，第二个原料作为辅助材料。 - 如果原料不是旗帜物品，则什么也不会输出。 - 如果提供旗帜图案的旗帜颜色和辅助材料的旗帜颜色不同，则什么也不会输出。 - 从提供旗帜图案的物品获取 ``` banner_patterns ``` 组件，如果此组件超过6层图案，则什么也不会输出。
- 合成行为： - 游戏会根据类型转化配方的合成规则，将提供旗帜图案的物品视为输入物品，转化为 ``` result ``` 指定的输出物品。 - 提供旗帜图案的原料被合成后会留在合成方格中而不会被消耗，但如果此原料存在合成后返还物品，则依旧会变成对应的物品。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_bannerduplicate ``` - [图:字符串][图:NBT列表/JSON数组]*banner：表示配方原料。尽管所有物品都可以指定，但事实上只有旗帜物品才可以使此配方工作。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 成书复制配方

[[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]]
[[|]]2345678
查看JSON文件示例

代表合成的成书复制配方（Book Cloning Recipe），用于根据成书复制的规则复制成书内容。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格至少有2个物品堆叠，否则什么也不会输出。 - 依据合成方格的顺序，第一个 ``` source ``` 原料作为提供成书内容的物品，此物品必须具有 ``` written_book_content ``` 组件，否则什么也不会输出。
- 合成行为： - 游戏先将 ``` source ``` 原料作为输入物品，并经过类型转化配方的处理方式转化为 ``` result ``` 指定的物品。 - 转化完成后，设置新的 ``` written_book_content ``` 组件。 - 此组件的多数内容来自 ``` source ``` 原料，但[图:整型]generation会增加1。 - 合成消耗掉的 ``` material ``` 原料的数量会增加到输出物品数量上。 - 提供成书内容的 ``` source ``` 原料被合成后会留在合成方格中而不会被消耗，但如果此原料存在合成后返还物品，则依旧会变成对应的物品。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_bookcloning ``` - [图:字符串][图:NBT列表/JSON数组]*source：表示提供成书内容的材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*material：表示配方消耗的辅助材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:整型][图:NBT复合标签/JSON对象]*allowed_generations：（默认为 ``` [0, 1] ``` ，必须是 ``` [0, 2] ``` 的子区间）对提供成书内容物品复制程度的检查。如果检查失败，则配方什么也不会输出。参考值： ``` 0 ``` （原稿）， ``` 1 ``` （原稿的副本）， ``` 2 ``` （副本的副本）， ``` 3 ``` （破烂不堪）。 - - 整数界限范围，见Template:Nbt inherit/minmax bounds ints/source - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 烟花火箭配方

[[|]][[|]][[|]][[|]][[|]]
[[|]]3
查看JSON文件示例

代表合成的烟花火箭配方（Firework Rocket Recipe），用于根据烟花火箭合成的规则合成物品。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格至少有2个物品堆叠，否则什么也不会输出。 - 必须有且只有一个 ``` shell ``` 原料作为烟花火箭的外壳。 - 必须有数量不超过3的 ``` fuel ``` 原料作为烟花火箭的燃料，燃料数量控制了烟花火箭的飞行时间。
- 合成行为： - 游戏先获取 ``` result ``` 指定的物品，然后设置新的 ``` fireworks ``` 组件。 - 此组件的值取决于对应的原料，其中[图:NBT列表/JSON数组]explosions由 ``` star ``` 原料的 ``` firework_explosion ``` 组件提供，根据合成方格的顺序拼接，不存在此组件时静默忽略。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_firework_rocket ``` - [图:字符串][图:NBT列表/JSON数组]*shell：表示提供烟花火箭外壳的材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*fuel：表示增加烟花火箭飞行时间的材料，每有一个物品就会使[图:字节型]flight_duration增加1。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*star：表示提供烟火之星的材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 烟火之星合成配方

[[|]][[|]][[|]][[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的烟火之星合成配方（Firework Star Recipe），用于根据烟火之星合成的规则合成物品。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格至少有2个物品堆叠，否则什么也不会输出。 - 所有调整烟火之星效果的原料和 ``` fuel ``` 原料最多只能出现一次。 - 符合 ``` dye ``` 原料的物品必须具有 ``` dye ``` 组件。
- 合成行为： - 游戏先获取 ``` result ``` 指定的物品，然后设置新的 ``` firework_explosion ``` 组件。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_firework_star ``` - [图:字符串][图:NBT列表/JSON数组]*trail：表示增加踪迹效果的物品。此原料不存在时游戏会正常输出物品，但不会设置踪迹效果。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*twinkle：表示增加闪烁效果的物品。此原料不存在时游戏会正常输出物品，但不会设置闪烁效果。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*fuel：表示一种原料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*dye：表示作为染料的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:NBT复合标签/JSON对象]*shapes：（默认为小型球状）表示烟火之星的形状。 - [图:字符串][图:NBT列表/JSON数组]small_ball：表示设置为小型球状的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]large_ball：表示设置为大型球状的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]burst：表示设置为喷发状的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]star：表示设置为星形的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]creeper：表示设置为苦力怕状的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 烟火之星色彩淡化配方

[[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的烟火之星色彩淡化配方（Firework Star Fade Recipe），用于根据烟火之星色彩淡化的规则合成物品。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格至少有2个物品堆叠，否则什么也不会输出。 - 依据合成方格的顺序，第一个 ``` target ``` 原料物品将作为输入物品。如果有多个 ``` target ``` 原料，则什么也不会输出。 - 合成方格中的其他物品必须符合 ``` dye ``` 原料的物品类型，且具有 ``` dye ``` 组件。
- 合成行为： - 游戏先将 ``` target ``` 原料作为输入物品，并经过类型转化配方的处理方式转化为 ``` result ``` 指定的物品。 - 转化完成后，根据既有的颜色和输入的染料颜色设置 ``` firework_explosion ``` 组件的[图:整型数组]fade_colors数据。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_firework_star_fade ``` - [图:字符串][图:NBT列表/JSON数组]*target：表示将要被染色淡化的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*fuel：表示作为染料的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 地图缩小配方

[[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]][[|]]
[[|]]
查看JSON文件示例

代表合成的地图缩小配方（Map Extending Recipe），用于缩小地图。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格的中心必须是 ``` map ``` 原料，周围一圈8个物品必须是 ``` material ``` 原料。 - ``` map ``` 原料物品必须具有 ``` map_id ``` 组件。 - ``` map_id ``` 组件对应的地图数据必须存在，且不能是探险家地图（依据地图图标判定），缩放等级不能是4。
- 合成行为： - 游戏先将 ``` map ``` 原料作为输入物品，并经过类型转化配方的处理方式转化为 ``` result ``` 指定的物品。 - 转化完成后，设置 ``` map_post_processing ``` 组件的值为1。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_mapextending ``` - [图:字符串][图:NBT列表/JSON数组]*map：表示将要被缩小的地图物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*material：表示辅助材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 物品修复配方

[[|]][[|]]
[[|]]

查看JSON文件示例

代表合成的物品修复配方（Repair Item Recipe），用于物品修复。

此配方需要两个物品，且这两个物品的物品类型必须相同，且均具有
```
damage
```

和
```
max_damage
```

组件。输出物品的最大耐久度取最大值，剩余耐久度取二者耐久度之和并额外增加5%。输出物品会保留两个原料的诅咒魔咒，所有魔咒取最高等级。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_repairitem ```

### 盾牌装饰配方

[[|]][[|]]
[[|]]

查看JSON文件示例

代表合成的盾牌装饰配方（Shield Decoration Recipe），用于根据给盾牌添加图案的配方的规则合成物品。

此配方拥有复杂的有效性检查和合成行为：

- 有效性检查： - 合成方格有且只有2个物品堆叠，否则什么也不会输出。 - ``` banner ``` 原料物品必须是旗帜物品。 - ``` target ``` 原料物品的 ``` banner_patterns ``` 组件要么不存在，要么为空。
- 合成行为： - 游戏先将 ``` target ``` 原料作为输入物品，并经过类型转化配方的处理方式转化为 ``` result ``` 指定的物品。 - 转化完成后，根据旗帜物品设置新的 ``` base_color ``` 和 ``` banner_patterns ``` 组件。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` crafting_special_shielddecoration ``` - [图:字符串][图:NBT列表/JSON数组]*banner：表示提供盾牌底色和图案的物品。尽管所有物品都可以指定，但事实上只有旗帜物品才可以使此配方工作。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*target：表示要设置图案的物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

## 烧炼配方

烧炼配方使用了相似的格式，区别在与何种方块可接受此配方处理物品。

- [图:NBT复合标签/JSON对象] 烧炼配方共通字段

- - [图:字符串]group：（默认为空字符串）一个字符串，表示该配方的分组。同一组的合成配方将在配方书中合并显示。 - [图:字符串]category：（默认为 ``` misc ``` ）决定该配方出现在配方书中的哪个标签栏。有效值为： ``` food ``` （食物）、 ``` blocks ``` （方块）或 ``` misc ``` （杂项）。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:单精度浮点数]experience：（默认为0）该配方产生的经验值。 - [图:整型]cookingtime：（对于 ``` smelting ``` ，默认为200；对于 ``` blasting ``` 、 ``` smoking ``` 和 ``` campfire_cooking ``` ，默认为100）以刻为单位的该配方的烧炼时间。 - [图:字符串][图:NBT列表/JSON数组]*ingredient：表示要被烧炼或烹饪的原料物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

### 高炉配方

代表高炉配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` blasting ``` 。 - - 烧炼配方共通字段

示例：

```
{

  
"type"
:
 
"minecraft:blasting"
,

  
"category"
:
 
"misc"
,

  
"cookingtime"
:
 
100
,

  
"experience"
:
 
0.1
,

  
"group"
:
 
"coal"
,

  
"ingredient"
:
 
"minecraft:coal_ore"
,

  
"result"
:
 
{

    
"id"
:
 
"minecraft:coal"

  
}

}
```

### 营火配方

代表营火配方。对灵魂营火也有效。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` campfire_cooking ``` 。 - - 烧炼配方共通字段

默认烧炼时间是100刻，即5秒。但所有的原版营火配方都将烧炼时间修改为了600刻，即30秒。

营火配方不会触发
```
recipe_unlocked
```

进度触发器。

### 熔炉配方

代表熔炉配方，也即熔炼（Smelting）配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` smelting ``` 。 - - 烧炼配方共通字段

### 烟熏炉配方

代表烟熏炉配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` smoking ``` 。 - - 烧炼配方共通字段

## 切石机配方

代表切石机配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` stonecutting ``` 。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]*ingredient：表示该配方的原料物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

示例：

```
{

  
"type"
:
 
"minecraft:stonecutting"
,

  
"ingredient"
:
 
"minecraft:cobbled_deepslate"
,

  
"result"
:
 
{

    
"count"
:
 
1
,

    
"id"
:
 
"minecraft:cobbled_deepslate_stairs"

  
}

}
```

## 酿造台配方

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

代表酿造台配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` brewing ``` 。 - [图:NBT复合标签/JSON对象]*input：表示该配方的输入物品。 - [图:字符串][图:NBT列表/JSON数组]*item：可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:NBT复合标签/JSON对象]potion_contents：物品具有的potion_contents物品堆叠组件。 - [图:字符串][图:NBT复合标签/JSON对象]*output：该配方的输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source - [图:NBT复合标签/JSON对象]*reagent：表示该配方的原料物品。 - [图:字符串][图:NBT列表/JSON数组]*item：可以为单个物品ID、物品ID的列表或一个物品标签。

示例：

```
{

  
"type"
:
 
"minecraft:brewing"
,

  
"input"
:
 
{

    
"item"
:
 
"minecraft:potion"
,

    
"potion_contents"
:
 
{

      
"potions"
:
 
"minecraft:awkward"

    
}

  
},

  
"output"
:
 
{

    
"components"
:
 
{

      
"minecraft:potion_contents"
:
 
{

        
"potion"
:
 
"minecraft:night_vision"

      
}

    
},

    
"id"
:
 
"minecraft:potion"

  
},

  
"reagent"
:
 
{

    
"item"
:
 
"minecraft:golden_carrot"

  
}

}
```

## 锻造配方

#### 锻造升级配方

代表锻造升级配方，也即锻造转化（Smithing Transform）配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` smithing_transform ``` 。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]template：表示基础物品升级时所需的锻造模板。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*base：表示要被锻造升级的基础物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]addition：表示升级基础物品时所需的锻造原材料。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT复合标签/JSON对象]*result：该配方的输出物品。游戏会根据类型转化配方的合成规则，将基础物品视为输入物品，转化为此输出物品。 - - 物品模板，见Template:Nbt inherit/item template/source

示例：

```
{

  
"type"
:
 
"minecraft:smithing_transform"
,

  
"addition"
:
 
"#minecraft:netherite_tool_materials"
,

  
"base"
:
 
"minecraft:diamond_axe"
,

  
"result"
:
 
{

    
"id"
:
 
"minecraft:netherite_axe"

  
},

  
"template"
:
 
"minecraft:netherite_upgrade_smithing_template"

}
```

#### 盔甲纹饰配方

代表盔甲纹饰配方，也即锻造纹饰（Smithing Trim）配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type： ``` smithing_trim ``` 。 - [图:布尔型]show_notification：（默认为 ``` true ``` ）当前配方解锁后是否弹出弹窗提示。 - [图:字符串][图:NBT列表/JSON数组]*template：表示为基础物品添加盔甲纹饰时所需的锻造模板。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*base：表示要被添加盔甲纹饰的基础物品。可以为单个物品ID、物品ID的列表或一个物品标签。 - [图:字符串][图:NBT列表/JSON数组]*addition：表示为基础物品添加盔甲纹饰时所需的锻造原材料，可以为单个物品ID、物品ID的列表或一个物品标签。将由此物品的 ``` provides_trim_material ``` 物品堆叠组件确定添加到基础物品上的盔甲纹饰材料。 - [图:字符串][图:NBT复合标签/JSON对象]*pattern：添加到基础物品上的盔甲纹饰图案。 - - 纹饰图案，见Template:Nbt inherit/trim pattern/source

# 基岩版

配方定义文件全部位于行为包的
```
recipes
```

目录下，且均为JSON文件。格式随配方类型不同而不同。大部分配方是数据驱动的，少部分配方是硬编码的。

- - [图:字符串]item：表示一个原料物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串]tag：表示一个物品标签，该标签的所有物品都可作为原料。

- - [图:字符串]item：表示输出物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:整型]count：输出物品的数量。

## recipe_shaped

代表有序合成配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]* *minecraft:recipe_shaped：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` crafting_table ``` 。 - [图:字符串]group：未知。 - [图:NBT复合标签/JSON对象]* *key：一个映射表，用于将字符与合成材料建立关联。字符将用于在[图:NBT列表/JSON数组]pattern中指定合成图案。 - [图:字符串][图:NBT复合标签/JSON对象]<键>：表示 ``` < 键 > ``` 所对应的合成材料。 ``` < 键 > ``` 只能为除了空格 ``` ``` 以外的单字符。 - - 输入物品 - [图:NBT列表/JSON数组]* *pattern：合成方格中物品要摆放成的合成图案。其中的每个字符串代表合成方格中的一横行。 - [图:字符串]：一个字符串，字符串中的每个字符都应为之前所指定的一个 ``` < 键 > ``` ，可以使用空格 ``` ``` 来表示一个空的合成槽位。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *result：该配方的输出物品。可以为单个物品，也可以为一个物品的列表。 - - 输出物品 - [图:布尔型]assume_symmetry：（默认为 ``` true ``` ）此配方是否可以左右对称排列。 - [图:整型]priority：此配方的优先级，值越低优先级越大。未指定时将默认为0。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]unlock：此配方的解锁条件。 - - 若类型为[图:NBT列表/JSON数组]： - [图:NBT复合标签/JSON对象]：检查要获得的物品，必须至少包含一个物品或物品标签。 - [图:字符串]item：一个物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串]tag：一个物品标签。 - - 若类型为[图:NBT复合标签/JSON对象]： - [图:字符串]context：取值可以为 ``` AlwaysUnlocked ``` （默认解锁）、 ``` PlayerInWater ``` （入水后解锁）或 ``` PlayerHasManyItems ``` （物品栏有超过10个物品时解锁）。

## recipe_shapeless

代表无序合成配方。切石机也使用此系统。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]* *minecraft:recipe_shapeless：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` crafting_table ``` 、 ``` stonecutter ``` 和 ``` cartography_table ``` 。 - [图:字符串]group：未知。 - [图:NBT列表/JSON数组]* *ingredients：此配方的原料。 - [图:字符串][图:NBT复合标签/JSON对象]：一个原料物品。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]* *result：该配方的输出物品。必须只有一个输出物品。 - - 输出物品 - [图:整型]priority：此配方的优先级，值越低优先级越大。未指定时将默认为0。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]unlock：此配方的解锁条件。 - - 若类型为[图:NBT列表/JSON数组]： - [图:NBT复合标签/JSON对象]：检查要获得的物品，必须至少包含一个物品或物品标签。 - [图:字符串]item：一个物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串]tag：一个物品标签。 - - 若类型为[图:NBT复合标签/JSON对象]： - [图:字符串]context：取值可以为 ``` AlwaysUnlocked ``` （默认解锁）、 ``` PlayerInWater ``` （入水后解锁）或 ``` PlayerHasManyItems ``` （物品栏有超过10个物品时解锁）。

## recipe_furnace

代表烧炼配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]* *minecraft:recipe_furnace：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` furnace ``` 、 ``` blast_furnace ``` 、 ``` smoker ``` 、 ``` campfire ``` 和 ``` soul_campfire ``` 。 - [图:字符串]group：未知。 - [图:字符串][图:NBT复合标签/JSON对象]* *input：该配方的原料物品。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象]* *output：该配方的输出物品。 - - 输出物品

## recipe_brewing_container

代表酿造配方，用于转化物品类型。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]* *minecraft:recipe_brewing_container：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` brewing_stand ``` 。 - [图:字符串][图:NBT复合标签/JSON对象]* *input：该配方的原料物品。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象]* *output：该配方的输出物品。 - - 输出物品 - [图:字符串][图:NBT复合标签/JSON对象]* *reagent：要添加的酿造材料。 - - 输入物品

## recipe_brewing_mix

代表酿造配方，用于转化药水效果。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]* *minecraft:recipe_brewing_mix：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` brewing_stand ``` 。 - [图:字符串]* *input：输入的药水效果。 - [图:字符串]* *output：输出的药水效果。 - [图:字符串][图:NBT复合标签/JSON对象]reagent：要添加的酿造材料。 - - 输入物品

## recipe_smithing_transform

代表锻造升级配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]minecraft:recipe_smithing_transform：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` smithing_table ``` 。 - [图:字符串][图:NBT复合标签/JSON对象]template：表示锻造模板物品。物品必须具有 ``` minecraft:trim_templates ``` 标签才能被放置到锻造台中。 - [图:字符串]item：表示一个原料物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串][图:NBT复合标签/JSON对象]base：表示锻造的基础物品。物品必须具有 ``` minecraft:trimmable_armors ``` 标签才能被放置到锻造台中。 - [图:字符串]item：表示一个原料物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串][图:NBT复合标签/JSON对象]addition：表示锻造原材料物品。物品必须具有 ``` minecraft:trim_materials ``` 标签才能被放置到锻造台中。但唯一有效的物品只有下界合金锭。 - [图:字符串]item：表示一个原料物品。 - [图:整型][图:字符串]data：物品的数据值。可以为一个Molang表达式。 - [图:字符串][图:NBT复合标签/JSON对象]result：该配方的输出物品。 - - 输出物品

## recipe_smithing_trim

代表盔甲纹饰配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]minecraft:recipe_smithing_trim：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` smithing_table ``` 。 - [图:字符串][图:NBT复合标签/JSON对象]template：表示锻造模板物品。物品必须具有 ``` minecraft:trim_templates ``` 标签才能被放置到锻造台中。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象]base：表示锻造的基础物品。物品必须具有 ``` minecraft:trimmable_armors ``` 标签才能被放置到锻造台中。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象]addition：表示锻造原材料物品。物品必须具有 ``` minecraft:trim_materials ``` 标签才能被放置到锻造台中。 - - 输入物品

## recipe_material_reduction

此段落描述的是教育版相关特性。
该特性仅在教育版和开启了“Education Edition”选项的基岩版世界中可用。

代表材料分解器配方。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]format_version：此配方文件的运行版本。 - [图:NBT复合标签/JSON对象]minecraft:recipe_material_reduction：配方的详细信息。 - [图:NBT复合标签/JSON对象]description - [图:字符串]identifier：此配方的标识符，用于区分不同的配方。 - [图:字符串][图:NBT列表/JSON数组]tags：此配方的标签。原版游戏下有效值只有 ``` material_reducer ``` 。 - [图:字符串][图:NBT复合标签/JSON对象]input：该配方的原料物品。 - - 输入物品 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]output：该配方的输出物品。可以为单个物品，也可以为一个物品的列表。输出物品不能超过9个。 - - 输出物品

# 历史

# 参考

1. ↑ https://www.reddit.com/r/Minecraft/comments/61n196/new_mob_idea_the_pillager/dfvhcex?context=1
1. ↑ MC-269268 — 漏洞状态为“已修复”。
1. ↑ MC-279257 — 漏洞状态为“已修复”。

# 导航

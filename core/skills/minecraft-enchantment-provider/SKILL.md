---
name: minecraft-enchantment-provider
description: |
  魔咒提供器定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】魔咒提供器（Enchantment Provider）是游戏为物品添加魔咒的一种方式。魔咒提供器定义文件是魔咒提供器在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：ENCHANTMENT_PROVIDER
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 魔咒提供器定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
魔咒提供器（Enchantment Provider）是游戏为物品添加魔咒的一种方式。魔咒提供器定义文件是魔咒提供器在数据包中的数据驱动定义文件。

# 定义格式

魔咒提供器在游戏内使用
```
ENCHANTMENT_PROVIDER
```

注册表，数据包路径为
```
enchantment_provider
```

，即所有魔咒提供器定义文件都需要在
```
data/<
命名空间
>/enchantment_provider
```

目录内定义，魔咒提供器标签则需要在
```
data/<
命名空间
>/tags/enchantment_provider
```

目录内定义。

魔咒提供器定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type：魔咒提供器类型。 - - 如果[图:字符串]type为 ``` by_cost ``` ，则根据附魔等级进行附魔。 - [图:字符串][图:NBT列表/JSON数组]*enchantments：这次附魔过程中可选的魔咒。可以为一个魔咒的命名空间ID或一个魔咒标签，或一个魔咒ID的数组。 - [图:整型][图:NBT复合标签/JSON对象]*cost：这次附魔过程使用的附魔等级。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果[图:字符串]type为 ``` by_cost_with_difficulty ``` ，则根据难度计算附魔等级进行附魔。 - [图:字符串][图:NBT列表/JSON数组]*enchantments：这次附魔过程中可选的魔咒。可以为一个魔咒的命名空间ID或一个魔咒标签，或一个魔咒ID的数组。 - [图:整型]*max_cost_span：（0≤值≤10000）由难度影响的附魔等级调节值。 - [图:整型]*min_cost：（1≤值≤10000）最小附魔等级。设 ``` min_cost ``` 为n，当前副区域难度为d， ``` max_cost_span ``` 为m，则最大附魔等级为n+md。 - - 如果[图:字符串]type为 ``` single ``` ，则直接添加指定魔咒，等级随机。 - [图:字符串]*enchantment：（命名空间ID）要添加的魔咒。 - [图:整型][图:NBT复合标签/JSON对象]*level：魔咒的等级。 - - 整数提供器，见Template:Nbt inherit/int provider/source

# 定义行为

魔咒提供器定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使魔咒提供器定义被重新加载，而必须重启服务端。

魔咒提供器是游戏选取魔咒附加到物品上的一种方式。在某些游戏场合，游戏会使用魔咒提供器为物品附魔。

魔咒提供器的调用是硬编码的，游戏只会使用下列内置魔咒提供器，由数据包定义的其他魔咒提供器没有任何用处：

部分魔咒提供器并不总是生效，游戏会额外增加一层概率限制：

- ``` enderman_loot_drop ``` ：总是生效。
- ``` mob_spawn_equipment ``` ：作用于骷髅陷阱时总是生效，作用于自然生成的生物时概率生效。
- ``` pillager_spawn_crossbow ``` ：概率生效。
- ``` raids/* ``` ：概率生效，与袭击之兆等级相关。

# 历史

# 导航

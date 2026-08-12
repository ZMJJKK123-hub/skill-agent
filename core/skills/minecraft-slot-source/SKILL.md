---
name: minecraft-slot-source
description: |
  槽位源（Minecraft Wiki 中文版全量正文）。
  
  【概述】你可以帮助我们加入更多信息。
  
  【涵盖内容】
  - group
  - filtered
  - limit_slots
  - slot_range
  - contents
  - reference
  - empty
  
  【关键定义】
  - 注册表：SLOT_SOURCE
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 槽位源 的完整规范时
---

此条目仍需完善。
你可以帮助我们加入更多信息。

本条目所述内容仅适用于Java版。
槽位源（Slot Source）允许游戏从指定的方块实体或实体等具有槽位的游戏对象中获取特定的槽位。其在战利品表和命令参数中均有使用。

# 定义格式

Java版26.3前，槽位源仅可以在战利品表中使用。

Java版26.3起，槽位源在游戏内使用
```
SLOT_SOURCE
```

注册表，数据包路径为
```
slot_source
```

，即所有槽位源定义文件都需要在
```
data/<
命名空间
>/slot_source
```

目录内定义，槽位源则需要在
```
data/<
命名空间
>/tags/slot_source
```

目录内定义。

槽位源定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组] 槽位源/JSON文件根节点 - - 如果类型为[图:NBT复合标签/JSON对象]对象：则表示单个槽位源，格式如下： - [图:字符串]：槽位源类型。 - 其他字段与槽位源类型相关。 - - 如果类型为[图:NBT列表/JSON数组]列表：则为多个槽位源组成的数组，行为同槽位源类型 ``` group ``` 的行为。 - [图:NBT复合标签/JSON对象]：单个槽位源，递归定义。

# 槽位源类型

## group

将多个槽位源合并为一个槽位源。此槽位源会提供一个槽位源列表，游戏会按列表顺序拼接合并槽位源。即使出现了相同的槽位，游戏也会照常拼接，而不是只出现一次。

例如，若列表内的两个槽位源的槽位分别是
```
[a, b]
```

和
```
[a, c]
```

，则拼接后的槽位源是
```
[a, b, a, c]
```

。

实际上，对于所有列表格式指定的多个槽位源，游戏都会拼接合并为一个槽位源。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` group ``` - [图:NBT列表/JSON数组]terms：槽位源列表。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]：一个槽位源，递归定义。

## filtered

对目标槽位进行过滤，过滤掉所有测试失败的槽位。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` filtered ``` - [图:NBT复合标签/JSON对象]*item_filter：测试每个槽位的物品谓词。如果某个槽位的物品测试失败，则丢弃此槽位。 - - 物品堆叠谓词，见Template:Nbt inherit/item predicate/source - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*slot_source：一个槽位源，递归定义。表示即将进行过滤的槽位。

## limit_slots

限制槽位的数量。按照槽位源提供槽位的顺序，任何在限制数量之外的槽位都将被丢弃。

例如，如果限制数量为3，则
```
[a, b, c, d]
```

将限制为
```
[a, b, c]
```

。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` limit_slots ``` - [图:整型]*limit：槽位的最大数量。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*slot_source：一个槽位源，递归定义。表示即将限制数量的槽位。

## slot_range

从实体或方块实体的槽位范围里选择槽位。

Java版26.3起，此类型的槽位源也是参数类型
```
slot_source
```

直接指定槽位范围时，游戏将其转化为槽位源而使用的槽位源类型——[图:字符串]source来自命令提供的
```
container
```

战利品上下文参数，[图:字符串]slots来自命令提供的槽位范围。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` slot_range ``` - [图:字符串]*source：作为来源的实体或方块实体，从战利品上下文获取。取值可以为 ``` block_entity ``` 、 ``` this ``` 、 ``` attacking_entity ``` 、 ``` last_damage_player ``` 、 ``` direct_attacker ``` 、 ``` target_entity ``` 或 ``` interacting_entity ``` 。 - [图:字符串]source：（默认为 ``` container ``` ）作为来源的实体或方块实体等槽位对象，从战利品上下文获取。取值可以为 ``` block_entity ``` 、 ``` this ``` 、 ``` attacking_entity ``` 、 ``` last_damage_player ``` 、 ``` direct_attacker ``` 、 ``` target_entity ``` ， ``` interacting_entity ``` 或 ``` container ``` 。 - [图:字符串]*slots：槽位范围，见槽位 § 命令参数。格式为 ``` < 槽位类型 > ``` 或 ``` < 槽位类型 >.< 槽位编号 > ``` ，例如 ``` armor.chest ``` 和 ``` container.* ``` 。

## contents

从容器组件中选择槽位。

游戏会获取输入的槽位源中槽位的物品，再从这些物品中获取容器组件的槽位。如果输入槽位源中的槽位不存在物品、物品不存在对应的组件，或对应的组件内部没有任何物品，则视为没有槽位。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` contents ``` - [图:字符串]*component：（命名空间ID）要获取槽位的容器组件。取值可以为 ``` bundle_contents ``` 、 ``` charged_projectiles ``` 或 ``` container ``` 。 - [图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*slot_source：一个槽位源，递归定义。游戏将从这些槽位的物品的容器组件中获取槽位。

Java版26.3起，当
```
/
item
```

命令需要获取容器组件的槽位时，对于目标槽位源
```
<slots>
```

，即使输入槽位源中的槽位不存在物品或物品不存在对应的组件，游戏也会先对物品设置对应的组件，然后再获取槽位源；当选择到空气时，命令即使无法产生实质性更改，也会正常设置组件并计数。如果修改物品的是
```
/
item
 (fill|override)
```

子命令，则目标槽位源
```
<slots>
```

会获取组件内所有可用的槽位。
```
bundle_contents
```

组件会自动按照槽位顺序塞入物品，当下一个槽位的物品塞入会导致收纳袋容量溢出时，物品塞入终止。

## reference

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

引用一个槽位源文件，循环引用会导致解析失败。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` reference ``` - [图:字符串]*name：（命名空间ID）要引用的槽位源。

## empty

不选择任何槽位。

- [图:NBT复合标签/JSON对象] 槽位源根节点 - [图:字符串]*type： ``` empty ```

# 历史

# 导航

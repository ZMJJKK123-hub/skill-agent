---
name: minecraft-waypoint-style
description: |
  路径点样式（Minecraft Wiki 中文版全量正文）。
  
  【概述】路径点样式（Waypoint Style）是生物的路径点在定位栏上显示的指示器图标样式。
  
  【涵盖内容】
  - （自动提取章节）
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 路径点样式 的完整规范时
---

本条目所述内容仅适用于Java版。
路径点样式（Waypoint Style）是生物的路径点在定位栏上显示的指示器图标样式。

# 定义格式

路径点样式定义文件都在资源包
```
assets/<
命名空间
>/waypoint_style
```

目录内，且均为JSON文件。

此文件的格式如下：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]near_distance：（0≤值≤60000000，默认为128）路径点样式使用[图:NBT列表/JSON数组]*sprites第一个纹理的距离的最大值。 - [图:整型]far_distance：（0≤值≤60000000，默认为332）路径点样式使用[图:NBT列表/JSON数组]*sprites最后一个纹理的距离的最小值，值必须大于[图:整型]near_distance。 - [图:NBT列表/JSON数组]*sprites：（不能为空）路径点样式可用的纹理列表。 - [图:字符串]：（命名空间ID）一个纹理。

# 定义行为

路径点样式使用的纹理属于GUI纹理，由纹理图集
```
minecraft:gui
```

生成，游戏在渲染时将纹理解析为
```
assets/<
命名空间
>/textures/gui/sprites/hud/locator_bar_dot/<
路径
>.png
```

。

路径点样式定义了指示器使用的图标纹理与距离变化的关系。假设玩家可以接收到路径点，且距离此路径点的距离为d，纹理列表[图:NBT列表/JSON数组]*sprites共n个元素。

- 如果d小于[图:整型]near_distance，则使用纹理列表的第一个纹理。
- 如果d大于[图:整型]far_distance，则使用纹理列表的最后一个纹理。
- 如果d在[图:整型]near_distance与[图:整型]far_distance之间，则进行线性插值保证纹理随距离均匀变化，即使用纹理列表的第（⌊(d−neardistancefardistance−neardistance)⌋×(n−2)+1）个纹理。除非纹理列表的元素个数小于3，否则此距离区间永远不会使用纹理列表的第一个和最后一个纹理。

# 内置样式

游戏内置了一些路径点样式。其中
```
default
```

为默认样式，即不指定路径点样式或使用命令
```
/
waypoint
 ... style reset
```

时使用的样式。

如果路径点样式不存在或加载失败，则游戏自动使用无效样式。无效样式是固定使用无效纹理的路径点样式，其被硬编码于游戏中且未分配ID。

# 历史

# 导航

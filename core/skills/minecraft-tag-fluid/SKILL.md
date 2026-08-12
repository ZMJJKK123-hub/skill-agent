---
name: minecraft-tag-fluid
description: |
  Java版标签/流体（Minecraft Wiki 中文版全量正文）。
  
  【概述】理由：需要检查目前的行为是否还是由对应的流体标签负责。
  
  【涵盖内容】
  - bubble_column_can_occupy
  - lava
  - supports_frogspawn
  - supports_lily_pad
  - supports_sugar_cane_adjacently
  - water
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Java版标签/流体 的完整规范时
---

本条目所述内容仅适用于Java版。此条目需要更新。
理由：需要检查目前的行为是否还是由对应的流体标签负责。

流体标签（Fluid Tags）是流体的组合。

# 使用

流体标签被游戏用来控制各种涉及到流体的游戏行为。

流体标签也可以在方块谓词和进度谓词中使用，用来判断某个位置是否为指定流体。

# 标签列表

## bubble_column_can_occupy

- 可被气泡柱占据的流体。

- #bubble_column_can_occupy（1项） - ``` water ```

## lava

- 这种流体会使相邻的仙人掌破碎。
- 用于在流体上实现熔岩纹理效果。
- 用于在雨中生成烟雾粒子而非常规的降雨粒子。
- 用于实现类似熔岩迷雾的雾效果。
- 物品和经验球在接触这种流体时会燃烧。
- 使用装有这种流体的水桶时将播放熔岩的声音效果。
- 表示熔岩（LAVA）路径节点。
- 用于形成石头、圆石或玄武岩。
- 用于炽足兽的各种寻路过程。
- 炽足兽浸入到这些流体中时将不能被骑乘。

- #lava（2项） - ``` lava ``` - ``` flowing_lava ```

## supports_frogspawn

- 青蛙卵可以放置在这些流体上。

- #supports_frogspawn（1项） - ``` water ```

## supports_lily_pad

- 睡莲可以放置并存活在这些流体上。

- #supports_lily_pad（1项） - ``` water ```

## supports_sugar_cane_adjacently

- 甘蔗可以放置并存活在这些流体毗邻的方块上。

- #supports_sugar_cane_adjacently（1项） - ``` #water ```

## water

- 珊瑚必须确保至少一面接触该流体，否则可能失活。
- 珊瑚扇必须放置在该流体中。
- 农田通过该流体来确定土壤的干湿。
- 海绵可以吸收这种流体。
- 一些粒子会使用这种物质来决定它们是否应该持续存在（ ``` bubble ``` 、​ ``` bubble_column_up ``` 、​ ``` current_down ``` 和​ ``` underwater ``` ）。
- 滴落粒子内部会使用这种流体来确定其颜色。
- 用于启用水下迷雾效果。
- 决定实体的移动是否表现为水中的移动行为。
- 表示一个水（WATER）寻路节点。某些生物会朝着这个节点移动。
- 船会检查此流体。
- 混凝土会在此流体中固化。
- 物品和经验球会在此流体中漂浮。
- 守卫、乌贼和海龟会检查此流体是否存在。
- 渔钓浮标在此液体中会上下浮动。
- 玻璃瓶可通过该液体被装满。
- 在下界中不能用桶放置这种液体。

- #water（2项） - ``` water ``` - ``` flowing_water ```

# 历史

# 导航

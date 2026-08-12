---
name: minecraft-configured-feature
description: |
  已配置的地物（Minecraft Wiki 中文版全量正文）。
  
  【概述】理由：26.2，以及26.3注册表改名应如何处理此页面
  
  【涵盖内容】
  - bamboo
  - basalt_columns
  - basalt_pillar
  - block_blob
  - block_column
  - block_pile
  - blue_ice
  - bonus_chest
  - chorus_plant
  - coral_claw
  - coral_mushroom
  - coral_tree
  
  【关键定义】
  - 注册表：CONFIGURED_FEATURE、FEATURE
  - 数据包路径：data/worldgen/configured_feature、data/worldgen/feature
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 已配置的地物 的完整规范时
---

本条目所述内容仅适用于Java版。此条目需要更新。
理由：26.2，以及26.3注册表改名应如何处理此页面

已配置的地物（Configured Feature），或简称为地物（Feature），是构成地物的基本单元。已配置的地物定义文件是已配置的地物在数据包中的数据驱动定义文件。

# 定义格式

Java版26.3前，已配置的地物在游戏中使用
```
CONFIGURED_FEATURE
```

注册表，数据包路径为
```
worldgen/configured_feature
```

，即所有的已配置的地物定义文件都需要在
```
data/<
命名空间
>/worldgen/configured_feature
```

目录下定义，已配置的地物标签则需要在
```
data/<
命名空间
>/tags/worldgen/configured_feature
```

目录下定义。

Java版26.3起，已配置的地物在游戏中使用
```
FEATURE
```

注册表，数据包路径为
```
worldgen/feature
```

，即所有的已配置的地物定义文件都需要在
```
data/<
命名空间
>/worldgen/feature
```

目录下定义，已配置的地物标签则需要在
```
data/<
命名空间
>/tags/worldgen/feature
```

目录下定义。

已配置的地物定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type：（命名空间ID）地物类型。 - [图:NBT复合标签/JSON对象]*config：此地物的配置。 - 依地物类型的额外字段，见下文。

# 定义行为

已配置的地物定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以使已配置的地物定义被重新加载，而必须重启服务端。

已配置的地物是游戏使用地物所有的基本单位。每一个已配置的地物都包括地物类型和配置数据，地物类型决定了地物的基本内容，而配置项会为地物添加详细的配置数据。

一些地物类型自身已提供了足够完整的地物信息，这类地物的配置项为空标签。剩余的地物类型均需要在配置项指定详细数据。

# 地物类型

地物类型（Feature Type）决定了地物的基本内容。游戏共定义了如下地物类型：

# 配置格式

## bamboo

生成竹子。要求放置点必须属于方块标签
```
#bamboo_plantable_on
```

。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:单精度浮点数]*probability：（0.0≤值≤1.0）表示在竹子下放置灰化土的概率。

## basalt_columns

生成玄武岩石柱林。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型][图:NBT复合标签/JSON对象]*height：（1≤值≤10）影响玄武岩柱簇的平均高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*reach：（0≤值≤3）影响玄武岩柱簇的最大半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## basalt_pillar

生成一个玄武岩柱。要求放置点为空且放置处上方不能为空，游戏会以放置点向下生成玄武岩柱。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## block_blob

生成一个方块团，大小随机，X、Y、Z方向各占3格。要求放置点必须在世界底部之上3格之上。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*state：方块团要使用的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:NBT复合标签/JSON对象]*can_place_on：方块谓词，测试方块团是否可以放置。从起始生成点开始测试，如果测试失败则检查下面一格，若一直失败则直到世界底部之上3格时才停止检查。 - - 方块谓词，见Template:Nbt inherit/block test/source

## block_column

生成一个方块柱。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*allowed_placement：方块谓词，决定方块在此处是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:字符串]*direction：方块柱的方向。取值只能为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - [图:NBT列表/JSON数组]*layers：（可以为空）方块柱每层的方块。 - [图:NBT复合标签/JSON对象]：方块柱一层的方块信息。 - [图:整型][图:NBT复合标签/JSON对象]*height：（值≥0）这一层的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:NBT复合标签/JSON对象]*provider：这一层要放置的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:布尔型]*prioritize_tip：决定方块柱是从头开始放置还是从尾开始放置。

## block_pile

生成一个方块堆。要求放置点必须高于世界底部5格。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*state_provider：组成该方块堆的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source

## blue_ice

生成一堆蓝冰。要求放置点不高于海平面下一格，放置点和放置点下方一格至少有一格水，且东南西北上5个方向至少有一格浮冰。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## bonus_chest

生成一个奖励箱。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## chorus_plant

生成一个紫颂植株。要求放置点下方为末地石。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## coral_claw

生成一个爪形珊瑚礁。要求放置点在水中。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## coral_mushroom

生成一个蘑菇形珊瑚礁。要求放置点在水中。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## coral_tree

生成一个树形珊瑚礁。要求放置点在水中。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## delta_feature

生成一个三角洲。要求放置点不能为三角洲主体方块（由配置字段[图:NBT复合标签/JSON对象]contents决定），且放置点上方为空的同时其他五个方向都不是空气。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*contents：三角洲的主体方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*rim：三角洲的边缘方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:整型][图:NBT复合标签/JSON对象]*rim_size：（0≤值≤16）三角洲边缘的大小。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*size：（0≤值≤16）三角洲的大小。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## desert_well

生成一个沙漠水井。要求放置点下方为沙子。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## disk

生成一个圆盘。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*half_height：（0≤值≤4）圆盘的半高。 - [图:整型][图:NBT复合标签/JSON对象]*radius：（0≤值≤8）圆盘的半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:NBT列表/JSON数组]*rules：（可以为空）可放置的方块的规则列表。 - [图:NBT复合标签/JSON对象]：一条规则。 - [图:NBT复合标签/JSON对象]*if_true：方块谓词，决定方块在此处是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]*then：此谓词通过时使用的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*state_provider：圆盘使用的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*target：方块谓词，决定方块在此处是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*floor_to_ceiling_search_range：（1≤值≤512）搜索地板和天花板的最大垂直范围。 - [图:整型][图:NBT复合标签/JSON对象]*height：（1≤值≤128）滴水石簇的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*radius：（1≤值≤128）滴水石簇的半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]*max_stalagmite_stalactite_height_diff：（1≤值≤64）石笋与钟乳石的最大高度差。 - [图:整型]*height_deviation：（1≤值≤64）高度偏差。 - [图:整型][图:NBT复合标签/JSON对象]*dripstone_block_layer_thickness：（0≤值≤128）滴水石块层的厚度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*density：（0.0≤值≤2.0）密度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*wetness：（0.0≤值≤2.0）湿度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]*chance_of_dripstone_column_at_max_distance_from_center：（0.0≤值≤1.0）在边缘上生成滴水石块的概率。 - [图:整型]*max_distance_from_edge_affecting_chance_of_dripstone_column：（1≤值≤64）影响滴水石锥生成概率的离边缘的最大距离。 - [图:整型]*max_distance_from_center_affecting_height_bias：（1≤值≤64）影响高度偏差的离中心的最大距离。

## end_gateway

生成一个末地折跃门。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:布尔型]*exact：此末地折跃门是否进行精准传送。 - [图:整型数组]exit：此末地折跃门传送后的坐标，内部的三个整数依次对应X、Y、Z坐标。

## end_island

生成一个末地岛屿。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## end_platform

生成一个黑曜石平台。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## end_spike

生成一个黑曜石柱。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:布尔型]crystal_invulnerable：（默认为 ``` false ``` ）生成在黑曜石柱上的末地水晶是否为无敌的。 - [图:NBT列表/JSON数组]*spikes：黑曜石柱的配置。 - [图:NBT复合标签/JSON对象]：一个黑曜石柱。 - [图:整型]centerX：（默认为0）黑曜石柱中心的X坐标。 - [图:整型]centerZ：（默认为0）黑曜石柱中心的Z坐标。 - [图:整型]radius：（默认为0）黑曜石柱的半径。 - [图:整型]height：（默认为0）黑曜石柱的高度。 - [图:布尔型]guarded：（默认为 ``` false ``` ）黑曜石柱是否有铁栅栏。 - [图:整型数组]crystal_beam_target：末地水晶光柱指向的方块位置，内部的三个整数依次对应X、Y、Z坐标。此项不指定时不会显示光柱。

## fallen_tree

生成一棵倒下的树。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*trunk_provider：作为树干和树桩的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:整型][图:NBT复合标签/JSON对象]*log_length：（0≤值≤16）倒下的树干的长度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:NBT列表/JSON数组]*stump_decorators：在树桩上生成的装饰。 - [图:NBT复合标签/JSON对象]：一个装饰。 - - 树木装饰器 - [图:NBT列表/JSON数组]*log_decorators：在树干上生成的装饰。 - [图:NBT复合标签/JSON对象]：一个装饰。 - - 树木装饰器

## fill_layer

生成一个填充层，填充16×1×16方块范围内的所有方块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*height：（0≤值≤4032）填充层的高度。 - [图:字符串][图:NBT复合标签/JSON对象]*state：填充的方块。 - - 方块状态，见Template:Nbt inherit/block state/source

## fossil

使用结构模板生成化石。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*fossil_structures：一个化石结构模板的列表，此列表不能为空，且列表长度必须与[图:NBT列表/JSON数组]overlay_structures相同。 - [图:字符串]：（命名空间ID）一个结构模板。 - [图:NBT列表/JSON数组]*overlay_structures：一个延伸结构模板的列表，此列表不能为空，且列表长度必须与[图:NBT列表/JSON数组]fossil_structures相同。 - [图:字符串]：（命名空间ID）一个结构模板。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*fossil_processors：处理化石结构模板的方块处理器。需为一个处理器列表，命名空间ID或内联定义均可。 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*overlay_processors：处理延伸结构模板的方块处理器。需为一个处理器列表，命名空间ID或内联定义均可。 - [图:整型]*max_empty_corners_allowed：（0≤值≤7）允许化石结构角落裸露在空气中的最大数量。

## freeze_top_layer

遍历所有位于高度图
```
MOTION_BLOCKING
```

的方块，将满足温度条件的方块上放置雪、将水结冰、设置草方块为覆雪状态。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## geode

生成一个晶洞。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*blocks：晶洞使用的方块集合。 - [图:NBT复合标签/JSON对象]*filling_provider：晶洞内部的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*inner_layer_provider：晶洞内层的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*alternate_inner_layer_provider：晶洞内层交替使用的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*middle_layer_provider：晶洞中层的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*outer_layer_provider：晶洞外层的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT列表/JSON数组]*inner_placements：（不能为空）晶洞内层放置的方块集合。 - [图:字符串][图:NBT复合标签/JSON对象]：一个方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT列表/JSON数组]*cannot_replace：晶洞不能替换的方块。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:字符串][图:NBT列表/JSON数组]*invalid_blocks：晶洞的无效方块，其中空气被硬编码为无效方块。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:NBT复合标签/JSON对象]*layers：晶洞内各层方块的厚度。值越大，对应的方块层越厚。 - [图:双精度浮点数]filling：（0.01≤值≤50.0，默认为1.7）晶洞内部。 - [图:双精度浮点数]inner_layer：（0.01≤值≤50.0，默认为2.2）晶洞内层。 - [图:双精度浮点数]middle_layer：（0.01≤值≤50.0，默认为3.2）晶洞中层。 - [图:双精度浮点数]outer_layer：（0.01≤值≤50.0，默认为4.2）晶洞外层。 - [图:NBT复合标签/JSON对象]*crack：晶洞生成裂缝的位置。 - [图:双精度浮点数]generate_crack_chance：（0.0≤值≤1.0，默认为1.0）产生裂缝的概率。 - [图:双精度浮点数]base_crack_size：（0.0≤值≤5.0，默认为2.0）裂缝的基础大小。 - [图:整型]crack_point_offset：（0≤值≤10，默认为2）裂缝生成点的偏移。 - [图:双精度浮点数]use_potential_placements_chance：（0.0≤值≤1.0，默认为0.35）在晶洞内部生成[图:NBT列表/JSON数组]inner_placements的方块的概率。 - [图:双精度浮点数]use_alternate_layer0_chance：（0.0≤值≤1.0，默认为0.0）晶洞内层方块为[图:NBT复合标签/JSON对象]alternate_inner_layer_provider的方块的概率。 - [图:布尔型]placements_require_layer0_alternate：（默认为 ``` true ``` ）内部放置物是否只能生成在[图:NBT复合标签/JSON对象]alternate_inner_layer_provider提供的方块上。 - [图:整型][图:NBT复合标签/JSON对象]outer_wall_distance：（1≤值≤20，默认为4到5的均匀分布整数）决定中心相对于地物起始点的各轴上的距离。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]distribution_points：（1≤值≤20，默认为3到4的均匀分布整数）检测无效方块的分布点的数量。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]*invalid_blocks_threshold：无效方块的最大限值。游戏将在晶洞的中心附近进行[图:整型][图:NBT复合标签/JSON对象]distribution_points次检测，发现的无效方块数量超过此数字则不生成此晶洞。 - [图:整型][图:NBT复合标签/JSON对象]point_offset：（1≤值≤10，默认为1到2的均匀分布整数）偏移。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]min_gen_offset：（默认为-16）方块距离中心点的最小切比雪夫距离。 - [图:整型]max_gen_offset：（默认为16）方块距离中心点的最大切比雪夫距离。 - [图:双精度浮点数]noise_multiplier：（0.0≤值≤1.0，默认为0.05）噪声乘数。

## glowstone_blob

生成一个荧石堆。要求放置点为下界岩、玄武岩或黑石。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## huge_brown_mushroom

生成一个巨型棕色蘑菇。要求放置点属于
```
#dirt
```

或
```
#mushroom_grow_block
```

标签、且放置点上方三格内不能有除空气和属于方块标签
```
#leaves
```

外的方块、放置点上方第四格起至少有一层以放置点水平坐标为中心、边长为
```
foliage_radius
```

的长方体区域不能有除空气和属于方块标签
```
#leaves
```

外的方块。在总高度不超过14时，放置点上方四格起的长方体区域限制了巨型棕色蘑菇的最大高度。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*cap_provider：组成巨型蘑菇伞盖的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*stem_provider：组成巨型蘑菇伞柄的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:整型]*foliage_radius：（默认为2）巨型蘑菇伞帽的大小。 - [图:NBT复合标签/JSON对象]*can_place_on：方块谓词，决定方块在此处是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source

## huge_fungus

生成一个巨型下界菌。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*valid_base_block：巨型下界菌下方的有效方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*stem_state：组成菌柄的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*hat_state：组成菌盖的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*decor_state：用于点缀的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:布尔型]planted：（默认为 ``` false ``` ）代表此下界菌是否是被种植的。如果为 ``` false ``` ，则游戏不允许此地物放置后的最高Y坐标超过此维度区块生成器定义的地形生成总高度，且替换符合[图:NBT复合标签/JSON对象]replaceable_blocks指定的方块时不会使其产生掉落物。 - [图:NBT复合标签/JSON对象]*replaceable_blocks：可以替换的方块。 - - 方块谓词，见Template:Nbt inherit/block test/source

## huge_red_mushroom

生成一个巨型红色蘑菇。要求放置点属于
```
#dirt
```

或
```
#mushroom_grow_block
```

标签。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*cap_provider：组成巨型蘑菇伞盖的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*stem_provider：组成巨型蘑菇伞柄的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:整型]*foliage_radius：（默认为2）巨型蘑菇伞帽的大小。 - [图:NBT复合标签/JSON对象]*can_place_on：方块谓词，决定方块在此处是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source

## iceberg

生成一个冰山。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*state：此地物的组成方块。 - - 方块状态，见Template:Nbt inherit/block state/source

## kelp

生成海带。要求放置点为水。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## lake

生成一个湖。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*fluid：湖使用的流体方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*barrier：湖周围的阻挡方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*can_place_feature：湖泊可以替换的方块。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]*can_replace_with_air_or_fluid：湖泊可以放置流体和空气的方块。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]*can_replace_with_barrier：湖泊可以放置阻挡方块的方块。 - - 方块谓词，见Template:Nbt inherit/block test/source

## large_dripstone

生成一个大型滴水石锥。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT列表/JSON数组]*replaceable_blocks：大型滴水石锥可以替换哪些方块生成。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:整型]floor_to_ceiling_search_range：（1≤值≤512，默认为30）起始点与地板和天花板的最大垂直距离。 - [图:整型][图:NBT复合标签/JSON对象]*column_radius：（1≤值≤60）半径的最小值和最大值。注意：此整数提供器不提供单个整数，而是提供它的最小值和最大值，请参阅该图表。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*height_scale：（0.0≤值≤20.0）值越大，高度越高。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]*max_column_radius_to_cave_height_ratio：（0.0≤值≤1.0）最大半径与洞穴高度之比。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*stalactite_bluntness：（0.1≤值≤10.0）截断钟乳石的尖端。值越大高度越低。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*stalagmite_bluntness：（0.1≤值≤10.0）截断石笋的尖端。值越大高度越低。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*wind_speed：（0.0≤值≤2.0）风速。值越大，倾角越大。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:整型]*min_radius_for_wind：（0≤值≤100）风生效的最小半径。 - [图:单精度浮点数]*min_bluntness_for_wind：（0.0≤值≤5.0）风生效的最小钝度。

## monster_room

生成一个刷怪房。要求以放置点下方一格为中心的9x9水平区域与上方第四格为中心的9x9水平区域只存在固体方块，且以放置点为中心的7x7/7x9/9x9的水平环上有1-4个方块及它上方的方块不是固体方块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## multiface_growth

生成一个方块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]block：（命名空间ID，默认为 ``` glow_lichen ``` ）要放置的方块。取值只能为 ``` glow_lichen ``` （发光地衣）或 ``` sculk_vein ``` （幽匿脉络）。 - [图:整型]search_range：（1≤值≤64，默认为10）搜索范围。 - [图:布尔型]can_place_on_floor：（默认为 ``` false ``` ）方块是否可以放置在地板上。 - [图:布尔型]can_place_on_ceiling：（默认为 ``` false ``` ）方块是否可以放置在天花板上。 - [图:布尔型]can_place_on_wall：（默认为 ``` false ``` ）方块是否可以放置在墙上。 - [图:单精度浮点数]chance_of_spreading：（0.0≤值≤0.5，默认为10）传播概率。 - [图:字符串][图:NBT列表/JSON数组]*can_be_placed_on：方块可以放置在什么方块上。可以为一个方块ID、一个方块标签、或一个方块ID的列表。

## nether_forest_vegetation

生成一堆方块。要求放置点属于
```
#nylium
```

标签。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*state_provider：组成该方块堆的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:整型]*spread_width：（值>0）影响方块堆扩散的最大水平宽度，公式为 ``` spread_width * 2 -1 ``` 。 - [图:整型]*spread_height：（值>0）影响方块堆扩散的最大高度，公式为 ``` spread_height * 2 -1 ``` 。

## netherrack_replace_blobs

用一个方块替换特定半径内的所有目标方块。若放置失败，则向下移动，直到找到目标方块后再生成。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*target：要替换的方块。此处的[图:NBT复合标签/JSON对象]Properties会被忽略。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*state：替换后的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:整型]*radius：（0≤值≤12）替换方块的半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## no_op

什么也不操作。通常用于覆盖现有已配置的地物。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## ore

生成一个球形矿团。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*targets：一个方块放置测试与放置的方块的列表。 - [图:NBT复合标签/JSON对象] - [图:NBT复合标签/JSON对象]*target：决定方块是否可以放置的测试。 - - 规则测试，见Template:Nbt inherit/rule test/source - [图:字符串][图:NBT复合标签/JSON对象]*state：放置的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:整型]*size：（0≤值≤64）矿团的生成规模。 - [图:单精度浮点数]*discard_chance_on_air_exposure：（0.0≤值≤1.0）若矿石暴露于空气，则不放置此矿石的概率。

## random_boolean_selector

从两个已放置的地物间随机选择一个生成。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*feature_false：若随机的布尔值为假，则放置此地物。需为一个已放置的地物，命名空间ID或内联定义均可。 - [图:字符串][图:NBT复合标签/JSON对象]*feature_true：若随机的布尔值为真，则放置此地物。需为一个已放置的地物，命名空间ID或内联定义均可。

## random_selector

从一个已放置的地物列表间按顺序尝试生成一个。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*features：一个已放置地物与概率的列表，游戏按序依次尝试生成，将放置首个测试成功的地物。 - [图:NBT复合标签/JSON对象] - [图:单精度浮点数]*chance：（0.0≤值≤1.0）放置此地物的概率。 - [图:字符串][图:NBT复合标签/JSON对象]*feature：一个已放置的地物，命名空间ID或内联定义均可。 - [图:字符串][图:NBT复合标签/JSON对象]*default：若上述列表的地物均测试失败，则生成此地物。需为一个已放置的地物，命名空间ID或内联定义均可。

## replace_single_block

替换一个方块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*targets：一个方块放置测试与放置的方块的列表。 - [图:NBT复合标签/JSON对象] - [图:NBT复合标签/JSON对象]*target：决定方块是否可以放置的测试。 - - 规则测试，见Template:Nbt inherit/rule test/source - [图:字符串][图:NBT复合标签/JSON对象]*state：放置的方块。 - - 方块状态，见Template:Nbt inherit/block state/source

## root_system

生成一个带有地下根系的地物。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*feature：代表此地物生成的地表地物。需为一个已放置的地物，命名空间ID或内联定义均可。 - [图:NBT复合标签/JSON对象]*allowed_tree_position：方块谓词，决定树木是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]*root_state_provider：作为根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:字符串][图:NBT列表/JSON数组]*root_replaceable：根可以替换的方块。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:NBT复合标签/JSON对象]*hanging_root_state_provider：作为垂根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:整型]*required_vertical_space_for_tree：（1≤值≤64）预留给树木生长的垂直空间。 - [图:整型]*allowed_vertical_water_for_tree：（1≤值≤64）树生成允许的最大水深。 - [图:整型]*root_radius：（1≤值≤64）根系生长的半径。 - [图:整型]*root_column_max_height：（1≤值≤256）根系最大高度。 - [图:整型]*root_placement_attempts：（1≤值≤4096）根尝试放置的次数。 - [图:整型]*hanging_root_radius：（1≤值≤64）垂根生成半径。 - [图:整型]*hanging_root_placement_attempts：（1≤值≤256）垂根尝试放置的次数。

## scattered_ore

生成一个分散的矿团。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*targets：一个方块放置测试与放置的方块的列表。 - [图:NBT复合标签/JSON对象] - [图:NBT复合标签/JSON对象]*target：决定方块是否可以放置的测试。 - - 规则测试，见Template:Nbt inherit/rule test/source - [图:字符串][图:NBT复合标签/JSON对象]*state：放置的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:整型]*size：（0≤值≤64）矿团的生成规模。 - [图:单精度浮点数]*discard_chance_on_air_exposure：（0.0≤值≤1.0）若矿石暴露于空气，则不放置此矿石的概率。

## sculk_patch

生成一个幽匿斑块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*charge_count：（1≤值≤32）信号的数量。 - [图:整型]*amount_per_charge：（1≤值≤500）每条信号的初始能量。 - [图:整型]*spread_attempts：（1≤值≤64）进行传播的尝试次数。 - [图:整型]*growth_rounds：（1≤值≤8）进行生成的次数。 - [图:整型]*spread_rounds：（1≤值≤8）进行传播的次数。 - [图:整型][图:NBT复合标签/JSON对象]*extra_rare_growths：（1≤值≤64）额外生成幽匿尖啸体的数量。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数]*catalyst_chance：（0.0≤值≤1.0）生成幽匿催发体的概率。

## seagrass

生成海草。要求放置点为水。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:单精度浮点数]*probability：（0.0≤值≤1.0）表示放置高海草而不是普通海草的概率。

## sea_pickle

生成海泡菜。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型][图:NBT复合标签/JSON对象]*count：（0≤值≤256）生成方块的最大数量。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## sequence

根据地物列表中的顺序依次生成地物。如果生成期间存在生成失败的地物则停止生成。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*features：可供放置的地物。可以为一个已放置的地物的ID，或一个已放置的地物标签（不能为空标签），或一个已放置的地物的ID的列表（不能为空列表），或一个已放置的地物对象，或一个已放置的地物对象的列表（不能为空列表）。

## simple_block

生成一个方块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*to_place：要放置的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:布尔型]schedule_tick：（默认为 ``` false ``` ）此方块是否是否添加1计划刻。

## simple_random_selector

从一个已放置的地物列表间随机选择一个生成。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象][图:NBT列表/JSON数组]*features：可供选择的地物。可以为一个已放置的地物的ID，或一个已放置的地物标签（不能为空标签），或一个已放置的地物的ID的列表（不能为空列表），或一个已放置的地物对象，或一个已放置的地物对象的列表（不能为空列表）。

## speleothem

生成一个钟乳石地物，如滴水石锥。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*base_block：钟乳石的基础方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*pointed_block：钟乳石的柱部方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT列表/JSON数组]*replaceable_blocks：钟乳石可以替换哪些方块生成。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:单精度浮点数]chance_of_taller_generation：（0.0≤值≤1.0，默认为0.2）生成两格高的柱部方块的概率。 - [图:单精度浮点数]chance_of_directional_spread：（0.0≤值≤1.0，默认为0.7）柱部方块向某一个水平方向扩散的概率。 - [图:单精度浮点数]chance_of_spread_radius2：（0.0≤值≤1.0，默认为0.5）水平扩散两格的概率。 - [图:单精度浮点数]chance_of_spread_radius3：（0.0≤值≤1.0，默认为0.5）水平扩散两格后再扩散第三格的概率。

## speleothem_cluster

生成一个由钟乳石类方块组成的簇状地物，如滴水石簇。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*base_block：钟乳石簇的基础方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]*pointed_block：钟乳石簇的柱部方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT列表/JSON数组]*replaceable_blocks：钟乳石簇可以替换哪些方块生成。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:整型]*floor_to_ceiling_search_range：（1≤值≤512）搜索地板和天花板的最大垂直范围。 - [图:整型][图:NBT复合标签/JSON对象]*height：（1≤值≤128）钟乳石簇的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*radius：（1≤值≤128）钟乳石簇的半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]*max_stalagmite_stalactite_height_diff：（1≤值≤64）石笋与钟乳石的最大高度差。 - [图:整型]*height_deviation：（1≤值≤64）高度偏差。 - [图:整型][图:NBT复合标签/JSON对象]*speleothem_block_layer_thickness：（0≤值≤128）基础方块层的厚度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*density：（0.0≤值≤2.0）密度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*wetness：（0.0≤值≤2.0）湿度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]*chance_of_speleothem_at_max_distance_from_center：（0.0≤值≤1.0）在边缘上生成基础方块的概率。 - [图:整型]*max_distance_from_edge_affecting_chance_of_speleothem：（1≤值≤64）影响柱部方块生成概率的离边缘的最大距离。 - [图:整型]*max_distance_from_center_affecting_height_bias：（1≤值≤64）影响高度偏差的离中心的最大距离。

## spike

生成一个刺状地物。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*state：刺状地物要使用的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:NBT复合标签/JSON对象]*can_place_on：方块谓词，测试刺状地物的方块是否可以放置。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]*can_replace：方块谓词，测试刺状地物的方块是否可以替换当前方块。除此之外，空气永远被认为可被替换。 - - 方块谓词，见Template:Nbt inherit/block test/source

## spring_feature

生成一个涌泉。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*state：生成涌泉的液体。 - [图:字符串]*Name：流体的命名空间ID。 - [图:NBT复合标签/JSON对象]Properties：组成此流体状态的流体属性。只有本流体具有的流体属性才有实际效果，而未指定的流体属性使用默认值。 - [图:字符串]<流体属性>：一个流体属性的键值对。 - [图:布尔型]requires_block_below：（默认为 ``` true ``` ）涌泉下方的方块是否是有效方块。 - [图:整型]rock_count：（默认为4）涌泉毗邻的有效方块的数量。 - [图:整型]hole_count：（默认为4）涌泉毗邻的空方块的数量。 - [图:字符串][图:NBT列表/JSON数组]*valid_blocks：用于涌泉生成判定的有效方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。

## template

从一个列表中随机选择选择结构模板并进行生成。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*templates：可供选择的结构模板列表。 - [图:NBT复合标签/JSON对象] - [图:字符串]*id：（命名空间ID）要放置的结构模板。 - [图:NBT列表/JSON数组]rotations：（默认为随机旋转）结构模板的旋转方式。 - [图:字符串]：一种可能的旋转方式。取值只能为 ``` none ``` （不旋转）、 ``` clockwise_90 ``` （以Y轴为旋转轴，俯瞰顺时针旋转90度）、 ``` 180 ``` （以Y轴为旋转轴，俯瞰顺时针旋转180度）和 ``` counterclockwise_90 ``` （以Y轴为旋转轴，俯瞰顺时针旋转270度）。

## tree

生成一棵树。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:布尔型]ignore_vines：（默认为 ``` false ``` ）树木是否忽略藤蔓。 - [图:NBT复合标签/JSON对象]*trunk_provider：作为树干的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*foliage_provider：作为树叶的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]below_trunk_provider：作为树下泥土的方块。默认为 ``` {"type": "minecraft:rule_based_state_provider", "rules": [{"if_true": {"type": "minecraft:not", "predicate": {"type": "minecraft:matching_block_tag", "tag": "minecraft:cannot_replace_below_tree_trunk"}}, "then": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:dirt"}}}]} ``` 。此值不存在时游戏不会替换树下泥土位置的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]*trunk_placer：树干的生成方式。 - - 树干放置器 - [图:NBT复合标签/JSON对象]*foliage_placer：树叶的生成方式。 - - 树叶放置器 - [图:NBT复合标签/JSON对象]root_placer：树根的生成方式。不指定时不生成树根。 - - 树根放置器 - [图:NBT复合标签/JSON对象]*minimum_size：树木生长的最小空间要求。 - [图:整型]min_clipped_height：（0≤值≤80）最小剪裁高度。泥土上方一格的高度记为0，即使满足最小空间要求的最大高度小于h+1（h是树干基础高度），只要满足最小空间要求的最大高度大于此字段的值，树木依旧会生成。如果未指定，只要满足最小空间要求的最大高度小于h+1（h是树干基础高度），树就不会生成。 - [图:字符串]*type：（命名空间ID）最小空间的类型，取值只能为 ``` two_layers_feature_size ``` （两层分段）或 ``` three_layers_feature_size ``` （三层分段）。 - - 如果 ``` type ``` 是 ``` two_layers_feature_size ``` ，附加参数如下： - [图:整型]limit：（0≤值≤81，默认为1）泥土上方一格的高度记为0。等于或高于此高度则最小空间为(2u+1)*(2u+1)，其中u为 ``` upper_size ``` 。反之则使用 ``` lower_size ``` 。 - [图:整型]lower_size：（0≤值≤16，默认为0）低于 ``` limit ``` 高度的最小空间尺寸。 - [图:整型]upper_size：（0≤值≤16，默认为1）等于或高于 ``` limit ``` 高度的最小空间尺寸。 - - 如果 ``` type ``` 是 ``` three_layers_feature_size ``` ，附加参数如下： - [图:整型]limit：（0≤值≤80，默认为1）泥土上方一格的高度记为0。低于此高度则最小空间为(2l+1)*(2l+1)，其中l为[图:整型]lower_size。 - [图:整型]upper_limit：（0≤值≤80，默认为1）泥土上方一格的高度记为0，高度大于等于h−upperLimit，则最小空间为(2u+1)*(2u+1)，其中h为树干基础高度，u为 ``` upper_size ``` 。 - [图:整型]lower_size：（0≤值≤16，默认为0）低于 ``` limit ``` 高度的最小空间尺寸。 - [图:整型]middle_size：（0≤值≤16，默认为1）高于或等于 ``` limit ``` 并低于h−upperLimit高度的最小空间尺寸，其中h为树干基础高度。 - [图:整型]upper_size：（0≤值≤16，默认为1）高于或等于h−upperLimit高度的最小空间尺寸，其中h为树干基础高度。 - [图:NBT列表/JSON数组]*decorators：树木除根枝叶外额外的装饰。 - [图:NBT复合标签/JSON对象]：一个装饰。 - - 树木装饰器

以下为树木配置各字段的格式：

此段内容过长，请通过显示按钮阅读

树干放置器

- [图:NBT复合标签/JSON对象] - [图:整型]*base_height：（0≤值≤32）树干基础高度的基础值。 - [图:整型]*height_rand_a：（0≤值≤24）随机额外高度，将从0（包含）到此值（包含）抽取一个随机整数加在基础值上后作为树干的基础高度。 - [图:整型]*height_rand_b：（0≤值≤24）随机额外高度，将从0（包含）到此值（包含）抽取一个随机整数加在基础值上后作为树干的基础高度。即树的基础高度不会超过80。 - [图:字符串]*type：（命名空间ID）树干放置器的类型，取值只能为 ``` straight_trunk_placer ``` （竖直型）、 ``` giant_trunk_placer ``` （2x2竖直型）、 ``` forking_trunk_placer ``` （单分叉型）、 ``` fancy_trunk_placer ``` （多分叉型）、 ``` mega_jungle_trunk_placer ``` （大丛林木型）, ``` dark_oak_trunk_placer ``` （深色橡木型）、 ``` bending_trunk_placer ``` （弯曲型）或 ``` upwards_branching_trunk_placer ``` （树枝型）。 - - 如果 ``` type ``` 是 ``` bending_trunk_placer ``` ，附加参数如下： - [图:整型][图:NBT复合标签/JSON对象]*bend_length：（0≤值≤24）弯曲长度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]min_height_for_leaves：（值>0）生成树叶的最小高度。 - - 如果 ``` type ``` 是 ``` upwards_branching_trunk_placer ``` ，附加参数如下： - [图:整型][图:NBT复合标签/JSON对象]*extra_branch_steps：（值>0）生成额外树枝的步骤数。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*extra_branch_length：（值≥0）生成额外树枝的长度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数]*place_branch_per_log_probability：（0.0≤值≤1.0）每块原木产生树枝的概率。 - [图:字符串][图:NBT列表/JSON数组]*can_grow_through：树干能生长穿过的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。

- - [图:整型]*base_height：（0≤值≤32）树干基础高度的基础值。 - [图:整型]*height_rand_a：（0≤值≤24）随机额外高度，将从0（包含）到此值（包含）抽取一个随机整数加在基础值上后作为树干的基础高度。 - [图:整型]*height_rand_b：（0≤值≤24）随机额外高度，将从0（包含）到此值（包含）抽取一个随机整数加在基础值上后作为树干的基础高度。即树的基础高度不会超过80。 - [图:字符串]*type：（命名空间ID）树干放置器的类型，取值只能为 ``` straight_trunk_placer ``` （竖直型）、 ``` giant_trunk_placer ``` （2x2竖直型）、 ``` forking_trunk_placer ``` （单分叉型）、 ``` fancy_trunk_placer ``` （多分叉型）、 ``` mega_jungle_trunk_placer ``` （大丛林木型）, ``` dark_oak_trunk_placer ``` （深色橡木型）、 ``` bending_trunk_placer ``` （弯曲型）或 ``` upwards_branching_trunk_placer ``` （树枝型）。 - - 如果 ``` type ``` 是 ``` bending_trunk_placer ``` ，附加参数如下： - [图:整型][图:NBT复合标签/JSON对象]*bend_length：（0≤值≤24）弯曲长度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]min_height_for_leaves：（值>0）生成树叶的最小高度。 - - 如果 ``` type ``` 是 ``` upwards_branching_trunk_placer ``` ，附加参数如下： - [图:整型][图:NBT复合标签/JSON对象]*extra_branch_steps：（值>0）生成额外树枝的步骤数。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*extra_branch_length：（值≥0）生成额外树枝的长度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数]*place_branch_per_log_probability：（0.0≤值≤1.0）每块原木产生树枝的概率。 - [图:字符串][图:NBT列表/JSON数组]*can_grow_through：树干能生长穿过的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。

树叶放置器

- [图:NBT复合标签/JSON对象] - [图:整型][图:NBT复合标签/JSON对象]*radius：（0≤值≤16）树叶生成半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*offset：（0≤值≤16）树叶顶层与树干顶层的间距。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:字符串]*type：（命名空间ID）树叶放置器的类型，取值只能为 ``` acacia_foliage_placer ``` （金合欢型）、 ``` dark_oak_foliage_placer ``` （深色橡木型）、 ``` blob_foliage_placer ``` （橡木/白桦型）、 ``` bush_foliage_placer ``` （金字塔型）、 ``` fancy_foliage_placer ``` （球型）、 ``` jungle_foliage_placer ``` （丛林木型）、 ``` spruce_foliage_placer ``` （云杉型）、 ``` pine_foliage_placer ``` （稀疏云杉型）、 ``` mega_pine_foliage_placer ``` （双层稀疏云杉型）或 ``` random_spread_foliage_placer ``` （随机扩散型）。 - - 如果 ``` type ``` 是 ``` blob_foliage_placer ``` 、 ``` bush_foliage_placer ``` 、 ``` fancy_foliage_placer ``` 或 ``` jungle_foliage_placer ``` ，附加的参数如下： - [图:整型]*height：树叶的高度，取值为0到16的闭区间。 - - 如果 ``` type ``` 是 ``` spruce_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*trunk_height：（0≤值≤24）树干的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` pine_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*height：（0≤值≤24）树叶的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` mega_pine_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*crown_height：（0≤值≤24）树冠的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` random_spread_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*foliage_height：（0≤值≤512）树叶的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]*leaf_placement_attempts：（0≤值≤256）树叶生成尝试次数。

- - [图:整型][图:NBT复合标签/JSON对象]*radius：（0≤值≤16）树叶生成半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*offset：（0≤值≤16）树叶顶层与树干顶层的间距。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:字符串]*type：（命名空间ID）树叶放置器的类型，取值只能为 ``` acacia_foliage_placer ``` （金合欢型）、 ``` dark_oak_foliage_placer ``` （深色橡木型）、 ``` blob_foliage_placer ``` （橡木/白桦型）、 ``` bush_foliage_placer ``` （金字塔型）、 ``` fancy_foliage_placer ``` （球型）、 ``` jungle_foliage_placer ``` （丛林木型）、 ``` spruce_foliage_placer ``` （云杉型）、 ``` pine_foliage_placer ``` （稀疏云杉型）、 ``` mega_pine_foliage_placer ``` （双层稀疏云杉型）或 ``` random_spread_foliage_placer ``` （随机扩散型）。 - - 如果 ``` type ``` 是 ``` blob_foliage_placer ``` 、 ``` bush_foliage_placer ``` 、 ``` fancy_foliage_placer ``` 或 ``` jungle_foliage_placer ``` ，附加的参数如下： - [图:整型]*height：树叶的高度，取值为0到16的闭区间。 - - 如果 ``` type ``` 是 ``` spruce_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*trunk_height：（0≤值≤24）树干的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` pine_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*height：（0≤值≤24）树叶的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` mega_pine_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*crown_height：（0≤值≤24）树冠的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - - 如果 ``` type ``` 是 ``` random_spread_foliage_placer ``` ，附加的参数如下： - [图:整型][图:NBT复合标签/JSON对象]*foliage_height：（0≤值≤512）树叶的高度。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型]*leaf_placement_attempts：（0≤值≤256）树叶生成尝试次数。

树根放置器

- [图:NBT复合标签/JSON对象] - [图:整型][图:NBT复合标签/JSON对象]*trunk_offset_y：与树干垂直方向上的偏移。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:NBT复合标签/JSON对象]*root_provider：作为树根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]above_root_placement：根上的方块的生成。 - [图:NBT复合标签/JSON对象]*above_root_provider：作为根上方的方块。 - [图:单精度浮点数]*above_root_placement_chance：（0.0≤值≤1.0）放置此方块的概率。 - [图:字符串]*type：（命名空间ID）树根放置器的类型，取值只能为 ``` mangrove_root_placer ``` （红树树根型）。 - - 如果 ``` type ``` 是 ``` mangrove_root_placer ``` ，附加的参数如下： - [图:NBT复合标签/JSON对象]*mangrove_root_placement：红树根放置参数。 - [图:整型]*max_root_width：（0≤值≤12）根的最大宽度。 - [图:整型]*max_root_length：（0≤值≤64）根的最大高度。 - [图:单精度浮点数]*random_skew_chance：（0.0≤值≤1.0）根随机偏移的概率。 - [图:字符串][图:NBT列表/JSON数组]*can_grow_through：根可以生长穿过的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。 - [图:字符串][图:NBT列表/JSON数组]*muddy_roots_in：根替换此方块时会变为沾泥根的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。 - [图:NBT复合标签/JSON对象]*muddy_roots_provider：作为沾泥根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source

- - [图:整型][图:NBT复合标签/JSON对象]*trunk_offset_y：与树干垂直方向上的偏移。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:NBT复合标签/JSON对象]*root_provider：作为树根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:NBT复合标签/JSON对象]above_root_placement：根上的方块的生成。 - [图:NBT复合标签/JSON对象]*above_root_provider：作为根上方的方块。 - [图:单精度浮点数]*above_root_placement_chance：（0.0≤值≤1.0）放置此方块的概率。 - [图:字符串]*type：（命名空间ID）树根放置器的类型，取值只能为 ``` mangrove_root_placer ``` （红树树根型）。 - - 如果 ``` type ``` 是 ``` mangrove_root_placer ``` ，附加的参数如下： - [图:NBT复合标签/JSON对象]*mangrove_root_placement：红树根放置参数。 - [图:整型]*max_root_width：（0≤值≤12）根的最大宽度。 - [图:整型]*max_root_length：（0≤值≤64）根的最大高度。 - [图:单精度浮点数]*random_skew_chance：（0.0≤值≤1.0）根随机偏移的概率。 - [图:字符串][图:NBT列表/JSON数组]*can_grow_through：根可以生长穿过的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。 - [图:字符串][图:NBT列表/JSON数组]*muddy_roots_in：根替换此方块时会变为沾泥根的方块。可以为一个方块ID、一个方块标签、或一个方块ID的列表。 - [图:NBT复合标签/JSON对象]*muddy_roots_provider：作为沾泥根的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source

树木装饰器

- [图:NBT复合标签/JSON对象] - [图:字符串]*type：（命名空间ID）树木装饰器的类型。取值只能为 ``` trunk_vine ``` （树干藤蔓）、 ``` leave_vine ``` （树叶藤蔓）、 ``` cocoa ``` （可可果）、 ``` beehive ``` （蜂巢）、 ``` alter_ground ``` （地面方块替换）、 ``` attached_to_leaves ``` （树叶装饰）、 ``` attached_to_logs ``` （树干装饰）、 ``` creaking_heart ``` （嘎枝之心）、 ``` pale_moss ``` （苍白垂须和苔藓）或 ``` place_on_ground ``` （地面放置方块）。 - - 如果 ``` type ``` 是 ``` leave_vine ``` 、 ``` cocoa ``` 、 ``` beehive ``` 或 ``` creaking_heart ``` ，附加参数如下： - [图:单精度浮点数]*probability：（0.0≤值≤1.0）尝试放置此装饰的概率。 - - 如果 ``` type ``` 是 ``` alter_ground ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*provider：用于替换地面的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - - 如果 ``` type ``` 是 ``` attached_to_leaves ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*block_provider：用于装饰的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:单精度浮点数]*probability：（0.0≤值≤1.0）尝试放置此装饰的概率。 - [图:整型]*exclusion_radius_xz：（0≤值≤16）两个装饰物水平距离的最小值。 - [图:整型]*exclusion_radius_y：（0≤值≤16）两个装饰物垂直距离的最小值。 - [图:整型]*required_empty_blocks：（0≤值≤16）装饰物需要的空方块数量。 - [图:NBT列表/JSON数组]*directions：（不能为空）装饰物可以生成的方向。 - [图:字符串]：一个方向。取值只能为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - - 如果 ``` type ``` 是 ``` attached_to_logs ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*block_provider：用于装饰的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:单精度浮点数]*probability：（0≤值≤1）放置装饰物的概率。 - [图:NBT列表/JSON数组]*directions：（不能为空）装饰物可以生成的方向。 - [图:字符串]：一个方向。取值只能为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - - 如果 ``` type ``` 是 ``` pale_moss ``` ，附加参数如下： - [图:单精度浮点数]*probability：（0.0≤值≤1.0）每个下方为空气的树叶在下方生成苍白垂须的概率。 - [图:单精度浮点数]*leaves_probability：（0.0≤值≤1.0）每个下方为空气的树木在下方生成苍白垂须的概率。 - [图:单精度浮点数]*ground_probability：（0.0≤值≤1.0）在随机根部原木处放置 ``` pale_moss_patch ``` 已配置的地物的概率。 - - 如果 ``` type ``` 是 ``` place_on_ground ``` ，附加参数如下： - [图:整型]tries：（默认为128，值>0）尝试生成的次数。 - [图:整型]radius：（默认为2，值≥0）尝试生成位置与树的根部的最大水平距离。 - [图:整型]height：（默认为1，值≥0）尝试生成位置与树的根部的最大垂直距离。 - [图:NBT复合标签/JSON对象]*block_state_provider：作为装饰物的方块。如果生成位置为空气或生成位置为下方与完全固体渲染方块相接的藤蔓，且不是除树叶外的阻止运动方块或流体下方，这个方块就能被放置。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source

- - [图:字符串]*type：（命名空间ID）树木装饰器的类型。取值只能为 ``` trunk_vine ``` （树干藤蔓）、 ``` leave_vine ``` （树叶藤蔓）、 ``` cocoa ``` （可可果）、 ``` beehive ``` （蜂巢）、 ``` alter_ground ``` （地面方块替换）、 ``` attached_to_leaves ``` （树叶装饰）、 ``` attached_to_logs ``` （树干装饰）、 ``` creaking_heart ``` （嘎枝之心）、 ``` pale_moss ``` （苍白垂须和苔藓）或 ``` place_on_ground ``` （地面放置方块）。 - - 如果 ``` type ``` 是 ``` leave_vine ``` 、 ``` cocoa ``` 、 ``` beehive ``` 或 ``` creaking_heart ``` ，附加参数如下： - [图:单精度浮点数]*probability：（0.0≤值≤1.0）尝试放置此装饰的概率。 - - 如果 ``` type ``` 是 ``` alter_ground ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*provider：用于替换地面的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - - 如果 ``` type ``` 是 ``` attached_to_leaves ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*block_provider：用于装饰的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:单精度浮点数]*probability：（0.0≤值≤1.0）尝试放置此装饰的概率。 - [图:整型]*exclusion_radius_xz：（0≤值≤16）两个装饰物水平距离的最小值。 - [图:整型]*exclusion_radius_y：（0≤值≤16）两个装饰物垂直距离的最小值。 - [图:整型]*required_empty_blocks：（0≤值≤16）装饰物需要的空方块数量。 - [图:NBT列表/JSON数组]*directions：（不能为空）装饰物可以生成的方向。 - [图:字符串]：一个方向。取值只能为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - - 如果 ``` type ``` 是 ``` attached_to_logs ``` ，附加参数如下： - [图:NBT复合标签/JSON对象]*block_provider：用于装饰的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:单精度浮点数]*probability：（0≤值≤1）放置装饰物的概率。 - [图:NBT列表/JSON数组]*directions：（不能为空）装饰物可以生成的方向。 - [图:字符串]：一个方向。取值只能为 ``` up ``` （上）、 ``` down ``` （下）、 ``` north ``` （北）、 ``` south ``` （南）、 ``` west ``` （西）或 ``` east ``` （东）。 - - 如果 ``` type ``` 是 ``` pale_moss ``` ，附加参数如下： - [图:单精度浮点数]*probability：（0.0≤值≤1.0）每个下方为空气的树叶在下方生成苍白垂须的概率。 - [图:单精度浮点数]*leaves_probability：（0.0≤值≤1.0）每个下方为空气的树木在下方生成苍白垂须的概率。 - [图:单精度浮点数]*ground_probability：（0.0≤值≤1.0）在随机根部原木处放置 ``` pale_moss_patch ``` 已配置的地物的概率。 - - 如果 ``` type ``` 是 ``` place_on_ground ``` ，附加参数如下： - [图:整型]tries：（默认为128，值>0）尝试生成的次数。 - [图:整型]radius：（默认为2，值≥0）尝试生成位置与树的根部的最大水平距离。 - [图:整型]height：（默认为1，值≥0）尝试生成位置与树的根部的最大垂直距离。 - [图:NBT复合标签/JSON对象]*block_state_provider：作为装饰物的方块。如果生成位置为空气或生成位置为下方与完全固体渲染方块相接的藤蔓，且不是除树叶外的阻止运动方块或流体下方，这个方块就能被放置。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source

## twisting_vines

生成缠怨藤。要求放置点为下界岩、下界疣块或绯红菌岩。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*spread_width：（值>0）地物扩散的水平半径。 - [图:整型]*spread_height：（值>0）地物扩散的最大高度。 - [图:整型]*max_height：（值>0）影响缠怨藤的高度，高度区间为 ``` [1,max_height * 2] ``` 。

## underwater_magma

生成水下岩浆块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*floor_search_range：（0≤值≤512）搜索地面的垂直范围。 - [图:整型]*placement_radius_around_floor：（0≤值≤64）尝试放置的岩浆块的半径。 - [图:单精度浮点数]*placement_probability_per_valid_position：（0.0≤值≤1.0）每个位置上生成岩浆块的概率。

## vegetation_patch

生成一个植物斑块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT列表/JSON数组]*replaceable：斑块可以替换的方块。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:NBT复合标签/JSON对象]*ground_state：斑块替换表面的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:字符串][图:NBT复合标签/JSON对象]*vegetation_feature：组成该斑块的地物。需为一个已放置的地物，命名空间ID或内联定义均可。 - [图:字符串]*surface：覆盖的表面，取值只能为 ``` floor ``` （地板）或 ``` ceiling ``` （天花板）。 - [图:整型][图:NBT复合标签/JSON对象]*xz_radius：斑块生成的水平半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*depth：（0≤值≤128）覆盖表面方块的深度。 - [图:整型]*vertical_range：（0≤值≤256）斑块生成的垂直范围。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数]*extra_bottom_block_chance：（0.0≤值≤1.0）底部额外生成方块的概率。 - [图:单精度浮点数]*extra_edge_column_chance：（0.0≤值≤1.0）边缘额外生成柱子的概率。 - [图:单精度浮点数]*vegetation_chance：（0.0≤值≤1.0）在表面生成斑块的概率。

## vines

生成藤蔓。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## void_start_platform

生成虚空平台。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

## waterlogged_vegetation_patch

生成一个含水的植物斑块。在
```
vegetation_patch
```

的基础上，
```
waterlogged_vegetation_patch
```

会尝试使生成的方块含水，[图:NBT复合标签/JSON对象]ground_state指定的方块会在地形非边缘的表面一层被水取代。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT列表/JSON数组]*replaceable：斑块可以替换的方块。可以为一个方块ID、带 ``` # ``` 前缀的方块标签ID或方块ID的列表。 - [图:NBT复合标签/JSON对象]*ground_state：斑块替换表面的方块。 - - 方块状态提供器，见Template:Nbt inherit/block state provider/source - [图:字符串][图:NBT复合标签/JSON对象]*vegetation_feature：组成该斑块的地物。需为一个已放置的地物，命名空间ID或内联定义均可。 - [图:字符串]*surface：覆盖的表面，取值只能为 ``` floor ``` （地板）或 ``` ceiling ``` （天花板）。 - [图:整型][图:NBT复合标签/JSON对象]*xz_radius：斑块生成的水平半径。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*depth：（0≤值≤128）覆盖表面方块的深度。 - [图:整型]*vertical_range：（0≤值≤256）斑块生成的垂直范围。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:单精度浮点数]*extra_bottom_block_chance：（0.0≤值≤1.0）底部额外生成方块的概率。 - [图:单精度浮点数]*extra_edge_column_chance：（0.0≤值≤1.0）边缘额外生成柱子的概率。 - [图:单精度浮点数]*vegetation_chance：（0.0≤值≤1.0）在表面生成斑块的概率。

## weeping_vines

生成垂泪藤。要求放置点为下界岩或下界疣块。

- [图:NBT复合标签/JSON对象]*config或[图:NBT复合标签/JSON对象] JSON文件根对象： ``` {} ```

# 历史

# 参考

1. ↑ MC-264886 — 漏洞状态为“已修复”。

# 导航

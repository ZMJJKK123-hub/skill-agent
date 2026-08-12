---
name: minecraft-structure
description: |
  结构定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】基岩版的拼图结构请参见官方文档
  
  【涵盖内容】
  - 结构类型
  - jigsaw
  - mineshaft
  - nether_fossil
  - ocean_ruin
  - ruined_portal
  - shipwreck
  
  【关键定义】
  - 注册表：STRUCTURE
  - 数据包路径：data/worldgen/structure
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 结构定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
基岩版的拼图结构请参见官方文档

 Wiki上有与该主题相关的教程！
见教程:自定义结构生成。

 Wiki上有与该主题相关的教程！
见教程:自定义结构生成。

 
结构定义文件是结构（Structure）在数据包中的数据驱动定义文件。本文中的结构均指结构地物（Structure Feature），即创建新的世界界面中可被生成结构（Generated Structure）选项控制的结构。

# 定义格式

结构在游戏中使用
```
STRUCTURE
```

注册表，数据包路径为
```
worldgen/structure
```

，即所有的结构定义文件都需要在
```
data/<
命名空间
>/worldgen/structure
```

目录下定义，结构标签则需要在
```
data/<
命名空间
>/tags/worldgen/structure
```

目录下定义。

结构定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT列表/JSON数组]*biomes：可以生成此结构的生物群系。可以为一个生物群系ID、一个生物群系ID的列表或一个生物群系标签。 - [图:NBT复合标签/JSON对象]*spawn_overrides：覆写结构片段所在生物群系的生物生成设置。 - [图:NBT复合标签/JSON对象]<生成类别>：覆写此生成类别的生物生成。可用值参见生成 § 生成类别。 - [图:字符串]*bounding_box：覆写方式。取值可以为 ``` piece ``` （覆写各结构片段占据的区域）或 ``` full ``` （覆写整个结构所占据的区域）。 - [图:NBT列表/JSON数组]*spawns：（可以为空）一个生物生成数据的列表。此列表为空时表示此不生成此生成类别的生物。 - [图:字符串]*type：实体类型ID。若指定的实体的生成类别为“其他”，则游戏只会生成猪。 - [图:整型]*weight：该生物的生成权重。 - [图:整型]*minCount：（值>0）成群生成时的最低数量。 - [图:整型]*maxCount：（值>0）成群生成时的最高数量。 - [图:字符串]*step：结构所属的生成阶段。在同一阶段内，结构比地物优先生成。取值可以为 ``` raw_generation ``` 、 ``` lakes ``` 、 ``` local_modifications ``` 、 ``` underground_structures ``` 、 ``` surface_structures ``` 、 ``` strongholds ``` 、 ``` underground_ores ``` 、 ``` underground_decoration ``` 、 ``` fluid_springs ``` 、 ``` vegetal_decoration ``` 或 ``` top_layer_modification ``` 。 - [图:字符串]*terrain_adaptation：（默认为 ``` none ``` ）生成结构时对地形的调整方式。取值可以为 ``` none ``` （无调整）、 ``` beard_thin ``` （在结构下方添加地形，并移除结构体内部地形，如掠夺者前哨站、村庄和废弃营地）、 ``` beard_box ``` （ ``` beard_thin ``` 的增强版，如远古城市）、 ``` bury ``` （围绕结构添加地形使其被掩埋，如要塞和古迹废墟）和 ``` encapsulate ``` （ ``` bury ``` 的增强版，如试炼密室）。 - [图:字符串]*type：结构类型。 - 依结构类型的其他附加字段，见下文。

- - [图:字符串][图:NBT列表/JSON数组]*biomes：可以生成此结构的生物群系。可以为一个生物群系ID、一个生物群系ID的列表或一个生物群系标签。 - [图:NBT复合标签/JSON对象]*spawn_overrides：覆写结构片段所在生物群系的生物生成设置。 - [图:NBT复合标签/JSON对象]<生成类别>：覆写此生成类别的生物生成。可用值参见生成 § 生成类别。 - [图:字符串]*bounding_box：覆写方式。取值可以为 ``` piece ``` （覆写各结构片段占据的区域）或 ``` full ``` （覆写整个结构所占据的区域）。 - [图:NBT列表/JSON数组]*spawns：（可以为空）一个生物生成数据的列表。此列表为空时表示此不生成此生成类别的生物。 - [图:字符串]*type：实体类型ID。若指定的实体的生成类别为“其他”，则游戏只会生成猪。 - [图:整型]*weight：该生物的生成权重。 - [图:整型]*minCount：（值>0）成群生成时的最低数量。 - [图:整型]*maxCount：（值>0）成群生成时的最高数量。 - [图:字符串]*step：结构所属的生成阶段。在同一阶段内，结构比地物优先生成。取值可以为 ``` raw_generation ``` 、 ``` lakes ``` 、 ``` local_modifications ``` 、 ``` underground_structures ``` 、 ``` surface_structures ``` 、 ``` strongholds ``` 、 ``` underground_ores ``` 、 ``` underground_decoration ``` 、 ``` fluid_springs ``` 、 ``` vegetal_decoration ``` 或 ``` top_layer_modification ``` 。 - [图:字符串]*terrain_adaptation：（默认为 ``` none ``` ）生成结构时对地形的调整方式。取值可以为 ``` none ``` （无调整）、 ``` beard_thin ``` （在结构下方添加地形，并移除结构体内部地形，如掠夺者前哨站、村庄和废弃营地）、 ``` beard_box ``` （ ``` beard_thin ``` 的增强版，如远古城市）、 ``` bury ``` （围绕结构添加地形使其被掩埋，如要塞和古迹废墟）和 ``` encapsulate ``` （ ``` bury ``` 的增强版，如试炼密室）。

## 结构类型

结构类型（Structure Type）决定了结构生成的方式与内容。游戏内所有的结构类型如下：

带有附加字段的结构类型如下：

### jigsaw

使用结构模板并利用拼图方块生成结构。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` jigsaw ``` - [图:字符串][图:NBT复合标签/JSON对象]*start_pool：拼图结构的起始模板池，将作为结构生成的起点。 - 见模板池。 - [图:字符串]start_jigsaw_name：连接起始模板的拼图方块的名称。 - [图:NBT复合标签/JSON对象]*start_height：结构生成的起始高度。 - - 高度提供器，见Template:Nbt inherit/height provider/source - [图:字符串]project_start_to_heightmap：结构生成时使用的高度图。若指定本字段，则结构生成的起始高度为在高度图的基础上偏移[图:NBT复合标签/JSON对象]*start_height格后的高度。取值只能为 ``` WORLD_SURFACE_WG ``` 、 ``` WORLD_SURFACE ``` 、 ``` OCEAN_FLOOR_WG ``` 、 ``` OCEAN_FLOOR ``` 、 ``` MOTION_BLOCKING ``` 或 ``` MOTION_BLOCKING_NO_LEAVES ``` 。 - [图:布尔型]*use_expansion_hack：是否允许次级拼图结构在基础拼图结构内放置时其Y方向大小超出基础拼图结构。 - [图:整型]*size：（1≤值≤20）拼图结构的生成深度。 - [图:整型][图:NBT复合标签/JSON对象]*max_distance_from_center：拼图的方块距离结构起始点的最大三维切比雪夫距离。当类型为[图:整型]时代表只设置水平边距。 - [图:整型]*horizontal：水平边距，取值为1到128的闭区间。当[图:字符串]terrain_adaptation不为 ``` none ``` 时，取值为1到116的闭区间。 - [图:整型]horizontal：（1≤值≤4096，默认为4096）垂直边距。 - [图:NBT列表/JSON数组]pool_aliases：定义模板池映射。 - [图:NBT复合标签/JSON对象]：一个模板池映射对象。 - [图:字符串]*type：映射类型。可以为 ``` direct ``` （一对一映射）、 ``` random ``` （随机挑选映射）和 ``` random_group ``` （随机挑选一组映射）。 - - 如果 ``` type ``` 是 ``` direct ``` ，附加的参数如下： - [图:字符串]*alias：模板池的映射名称。 - [图:字符串]*target：映射到的目标模板池。 - - 如果 ``` type ``` 是 ``` random ``` ，附加的参数如下： - [图:字符串]*alias：模板池的映射名称。 - [图:NBT列表/JSON数组]*targets：候选的模板池，当解析此映射时将按照权重随机挑选内部定义的模板池。 - [图:NBT复合标签/JSON对象]：一个候选的模板池项。 - [图:字符串]*data：一个模板池的命名空间ID。 - [图:整型]*weight：此模板池项的权重。 - - 如果 ``` type ``` 是 ``` random_group ``` ，附加的参数如下： - [图:NBT列表/JSON数组]*groups：候选的映射。 - [图:NBT复合标签/JSON对象]：一个候选的映射项。 - [图:NBT复合标签/JSON对象]*data：一个模板池映射对象。 - 结构与外层相同。 - [图:整型]*weight：此映射项的权重。 - [图:整型][图:NBT复合标签/JSON对象]dimension_padding：（值≥0，默认为0）指定结构的垂直内边距，防止结构因为太靠近基岩层而切入或穿过基岩层。当类型为[图:整型]时上下内边距都被设定为指定值。 - [图:整型]bottom：（值≥0，默认为0）结构下内边距。 - [图:整型]top：（值≥0，默认为0）结构上内边距。 - [图:字符串]liquid_settings：（默认为 ``` apply_waterlogging ``` ）结构生成时内部的液体将如何处理。可以为 ``` apply_waterlogging ``` （将可含水方块转换为含水方块）和 ``` ignore_waterlogging ``` （直接替代液体方块）。

如果指定了[图:字符串]start_jigsaw_name但对应名称的拼图方块不存在，或模板池中没有任何元素，则结构会直接生成失败。

游戏会从基础拼图结构中的拼图方块的目标池中选择所有和其目标名称相同名称的拼图方块的拼图结构，将两个结构拼接以使两块拼图方块“面对面”连接。拼图方块在世界生成阶段会自动转化为[图:字符串]final_state指定的方块。

在拼接结构时，游戏会读取每一个基础拼图结构内所有的拼图方块的信息，若拼图方块指向结构内，则不允许拼接的次级结构的范围超出基础结构；若拼图方块指向结构外，则不允许结构之间重合或超出结构的垂直内边距。拼图结构会在超出生成深度或最大距离时自动停止生成。

当有多个可以连接的拼图方块时，游戏会优先令选择优先级最大的拼图方块尝试连接；而在连接时也会优先连接放置优先级最大的拼图方块。如果受限于结构模板等限制无法连接或放置时则会使用优先级较低的拼图方块，所有拼图方块均无法连接时则停止生成。

### mineshaft

硬编码生成一个废弃矿井。其结构片段在属于
```
#mineshaft_blocking
```

的生物群系或液体区域时永不生成。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` mineshaft ``` - [图:字符串]*mineshaft_type：废弃矿井的类型。取值可以为 ``` normal ``` （橡木风格）或 ``` mesa ``` （深色橡木风格）。

### nether_fossil

使用结构模板生成下界化石。游戏会在区块内遍历起始高度，在所有海平面以上且与空气接触的方块表面上放置结构，此处的方块只包括灵魂沙或其他上表面完整的方块。结构生成后还有50%概率在结构最底层放置一个失水恶魂。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` nether_fossil ``` - [图:NBT复合标签/JSON对象]*height：生成下界化石的起始高度。 - - 高度提供器，见Template:Nbt inherit/height provider/source

### ocean_ruin

使用结构模板生成海底废墟。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` ocean_ruin ``` - [图:字符串]*biome_temp：海底废墟的类型，取值只能为 ``` cold ``` （寒带）或 ``` warm ``` （热带）。 - [图:单精度浮点数]*large_probability：（0≤值≤1）：生成大型变种的概率。 - [图:单精度浮点数]*cluster_probability：（0≤值≤1）：生成一簇而不是一个废墟的概率。

### ruined_portal

使用结构模板生成废弃传送门。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` ruined_portal ``` - [图:NBT列表/JSON数组]*setups：（不能为空）废弃传送门的生成设置。 - [图:NBT复合标签/JSON对象] - [图:单精度浮点数]*weight：（值>0）该项设置的权重。 - [图:字符串]*placement：控制废弃传送门的放置，可用值及其效果见下文。 - [图:单精度浮点数]*air_pocket_probability：（0≤值≤1）废弃传送门周围带有空气空腔的概率。 - [图:单精度浮点数]*mossiness：（0≤值≤1）废弃传送门生苔的程度，作为 ``` block_age ``` 处理器的参数。 - [图:布尔型]*overgrown：废弃传送门周围是否生成丛林树叶。 - [图:布尔型]*vines：废弃传送门上是否生成藤蔓。 - [图:布尔型]*can_be_cold：为 ``` true ``` 时，若当前生物群系温度足够低，则所有熔岩都会转化为下界岩，而不是通常的以20%概率转化为岩浆块。 - [图:布尔型]*replace_with_blackstone：决定是否把石砖替换成黑石砖，将应用 ``` blackstone_replace ``` 处理器。

废弃传送门放置的Y坐标由[图:字符串]*placement指定的放置方法决定。每种放置方法都定义了生成结构的最高高度和最低高度，如最高高度比最低高度小则返回最高高度，否则在这两个高度之间返回随机值。为便下文表述，规定
```
h0
```

为生成点最高非空气方块的高度，
```
h1
```

为要放置的结构模板的高度。

### shipwreck

使用结构模板生成沉船。

- [图:NBT复合标签/JSON对象] JSON文件根对象 - - 结构共通字段 - [图:字符串]*type： ``` shipwreck ``` - [图:布尔型]*is_beached：控制沉船生成的高度，为 ``` true ``` 时沉船会生成在最高的非空气方块上，否则会生成在最高的阻止运动的方块上。

# 定义行为

结构定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以重新加载结构定义，而必须重启服务端。

每个结构定义文件都定义了一种结构，这些结构既可以被结构集自然放置于开启了“生成结构”的世界，也可以被
```
/
place
 structure
```

直接调用。

# 历史

# 参考

1. ↑ MC-241288 — 漏洞状态为“已修复”。

# 导航

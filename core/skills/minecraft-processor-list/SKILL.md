---
name: minecraft-processor-list
description: |
  处理器列表（Minecraft Wiki 中文版全量正文）。
  
  【概述】基岩版的结构处理器请参见官方文档
  
  【涵盖内容】
  - 处理器类型
  - blackstone_replace
  - block_age
  - block_ignore
  - block_rot
  - capped
  - gravity
  - jigsaw_replacement
  - lava_submerged_block
  - nop
  - protected_blocks
  - rule
  
  【关键定义】
  - 注册表：PROCESSOR_LIST
  - 数据包路径：data/worldgen/processor_list
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 处理器列表 的完整规范时
---

本条目所述内容仅适用于Java版。
基岩版的结构处理器请参见官方文档

处理器列表（Processor List）用于在世界生成过程中按照特定规则替换由结构模板放置的方块，处理器列表定义文件是处理器列表在数据包中的数据驱动定义文件。

# 定义格式

处理器列表在游戏中使用
```
PROCESSOR_LIST
```

注册表，数据包路径为
```
worldgen/processor_list
```

，即所有的处理器列表定义文件都需要在
```
data/<
命名空间
>/worldgen/processor_list
```

目录下定义，处理器列表标签则需要在
```
data/<
命名空间
>/tags/worldgen/processor_list
```

目录下定义。

处理器列表定义文件使用JSON格式，并具有下列结构：

- [图:NBT列表/JSON数组] JSON文件根数组 - [图:NBT复合标签/JSON对象]：一个处理器。 - [图:字符串]*processor_type：处理器类型。 - 依处理器类型的附加字段，见下文。

或：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT列表/JSON数组]*processors：处理器列表。 - [图:NBT复合标签/JSON对象]：一个处理器。 - [图:字符串]*processor_type：处理器类型。 - 依处理器类型的附加字段，见下文。

处理器列表使用数组格式时，根节点将作为处理器列表的列表根节点，类似于对象格式下的[图:NBT列表/JSON数组]processors字段。

## 处理器类型

### blackstone_replace

将各种石质方块替换为黑石变种，铁栅栏替换为铁链。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` blackstone_replace ```

### block_age

做旧方块，使方块看起来更有年代感。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` block_age ``` - [图:单精度浮点数]*mossiness：生苔率。高于1的值相当于1，低于0的值相等于0。

### block_ignore

移除指定的方块。被移除的位置不会被结构生成覆盖，而是保留生成前的方块。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` block_ignore ``` - [图:NBT列表/JSON数组]*blocks：要被移除的方块，游戏不会检查方块状态。 - [图:NBT复合标签/JSON对象]：一个方块。 - - 方块状态，见Template:Nbt inherit/block state/source

### block_rot

随机移除方块。与
```
block_ignore
```

类似，被移除的方块的位置不会被结构覆盖。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` block_rot ``` - [图:单精度浮点数]*integrity：（0≤值≤1）结构的完整度，决定随机移除结构中方块的概率。 - [图:字符串][图:NBT列表/JSON数组]rottable_blocks：可以被移除的方块，不存在时代表所有方块都可以被移除。可以为方块ID、方块ID的数组或一个方块标签。

### capped

限制处理器可以处理的方块数量。如果结构没有足够的方块供处理器处理，则处理所有方块，否则从所有方块中随机选取指定数量的方块进行处理。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` capped ``` - [图:NBT复合标签/JSON对象]*delegate：要使用的处理器。 - 与此结构相同，递归定义。 - [图:整型][图:NBT复合标签/JSON对象]*limit：可以处理的方块的最大数量。 - - 整数提供器，见Template:Nbt inherit/int provider/source

### gravity

根据地形改变结构的高度。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` gravity ``` - [图:字符串]heightmap：（默认为 ``` WORLD_SURFACE_WG ``` ）结构偏移使用的高度图。取值只能为 ``` WORLD_SURFACE_WG ``` 、 ``` WORLD_SURFACE ``` 、 ``` OCEAN_FLOOR_WG ``` 、 ``` OCEAN_FLOOR ``` 、 ``` MOTION_BLOCKING ``` 或 ``` MOTION_BLOCKING_NO_LEAVES ``` 。 - [图:整型]offset：（默认为0）偏移高度。

### jigsaw_replacement

替换拼图方块并移除结构空位。对于世界生成阶段的拼图结构而言不需要额外声明，游戏会自动调用此处理器。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` jigsaw_replacement ```

### lava_submerged_block

当结构替换熔岩时，如果结构内的某方块轮廓箱不完整，则此方块不替换熔岩。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` lava_submerged_block ```

### nop

什么也不操作。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` nop ```

### protected_blocks

指定一些方块，使其无法被结构覆盖放置。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` protected_blocks ``` - [图:字符串][图:NBT列表/JSON数组]value：无法被结构替换的方块。可以为方块ID、方块ID的列表或一个方块标签。

### rule

自定义规则。

- [图:NBT复合标签/JSON对象] 处理器根标签 - [图:字符串]*processor_type： ``` rule ``` - [图:NBT列表/JSON数组]*rules：（可以为空）一个自定义规则列表。此规则将按列表顺序依次应用。 - [图:NBT复合标签/JSON对象]：一条规则。 - [图:NBT复合标签/JSON对象]position_predicate：（默认永远成功）应用到该结构地物起始点到该方块的距离上的测试。 - [图:字符串]*predicate_type：位置规则测试类型。取值可以为 ``` always_true ``` （永远成功）、 ``` linear_pos ``` （概率成功，取决于当前位置到结构起始点的三维曼哈顿距离）或 ``` axis_aligned_linear_pos ``` （概率成功，取决于当前位置到结构起始点的指定坐标轴上的距离）。 - - 如果 ``` predicate_type ``` 是 ``` linear_pos ``` ，附加字段如下： - [图:单精度浮点数]min_chance: （默认为0.0）当方块距结构起始点的距离小于等于[图:整型]min_dist时测试成功的概率。小于0则视为0，大于1则视为1。 - [图:单精度浮点数]max_chance: （可选，默认为0.0）当方块距结构起始点的距离大于等于[图:整型]max_dist时测试成功的概率。若方块的距离在[图:整型]min_dist和[图:整型]max_dist之间，则概率由 ``` min_chance ``` 和 ``` max_chance ``` 经线性插值而得，即概率为 ``` ( 距离 - min_dist ) / ( max_dist - min_dist ) * ( max_chance - min_chance ) + min_chance ``` ，得到的概率小于0则视为0，大于1则视为1。 - [图:整型]min_dist：（默认为0）达到最小概率时的距离。 - [图:整型]max_dist：（默认为0）达到最大概率时的距离。必须大于[图:整型]min_dist。 - - 若 ``` predicate_type ``` 为 ``` axis_aligned_linear_pos ``` ，附加的参数如下： - [图:字符串]axis: （默认为 ``` y ``` ）要检查的方向，距离全部以正数计算。取值可以为 ``` x ``` 、 ``` y ``` 或 ``` z ``` 。 - [图:单精度浮点数]min_chance: （默认为0.0）当方块距结构起始点的距离小于等于[图:整型]min_dist时测试成功的概率。小于0则视为0，大于1则视为1。 - [图:单精度浮点数]max_chance: （可选，默认为0.0）当方块距结构起始点的距离大于等于[图:整型]max_dist时测试成功的概率。若方块的距离在[图:整型]min_dist和[图:整型]max_dist之间，则概率由 ``` min_chance ``` 和 ``` max_chance ``` 经线性插值而得，即概率为 ``` ( 距离 - min_dist ) / ( max_dist - min_dist ) * ( max_chance - min_chance ) + min_chance ``` ，得到的概率小于0则视为0，大于1则视为1。 - [图:整型]min_dist：（默认为0）达到最小概率时的距离。 - [图:整型]max_dist：（默认为0）达到最大概率时的距离。必须大于[图:整型]min_dist。 - [图:NBT复合标签/JSON对象]*input_predicate：应用到被放置的方块上的测试。 - - 规则测试，见Template:Nbt inherit/rule test/source - [图:NBT复合标签/JSON对象]*location_predicate：应用到该结构生成前的该位置方块上的测试。 - - 规则测试，见Template:Nbt inherit/rule test/source - [图:NBT复合标签/JSON对象]*output_state：要放置的方块。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:NBT复合标签/JSON对象]block_entity_modifier：放置方块时要应用的方块实体修饰器。 - [图:字符串]*type：方块实体修饰器类型。 - - 如果[图:字符串]type是 ``` passthrough ``` ，则不修改方块实体原有字段。此项也为默认值。 - - 如果[图:字符串]type是 ``` clear ``` ，则移除方块实体原有字段。 - - 如果[图:字符串]type是 ``` append_static ``` ，则向方块实体添加静态字段。 - [图:NBT复合标签/JSON对象]*data：要添加的NBT数据，格式见NBT格式 § JSON。 - - 如果[图:字符串]type是 ``` append_loot ``` ，则向方块实体添加战利品表，同时也会添加基于方块位置的战利品表种子。 - [图:字符串]*loot_table：要添加的战利品表。

# 定义行为

处理器列表定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以重新加载处理器列表定义，而必须重启服务端。

当游戏调用处理器列表时，会按照列表的顺序依次调用处理器。由于游戏通常对结构模板的方块调用处理器列表，因而单个处理器也被称为方块处理器（block processors）、结构后处理器（Structure post-processors）或结构处理器（Structure Processors）。

对于模板池拼图元素而言，游戏会先调用处理器，然后再对结构片段进行地形调整。因此结构实际放置的位置可能并不是调用处理器计算时的位置。

# 历史

# 参考

1. ↑ Minecraft Snapshot 20w28a — Minecraft.net。
1. ↑ Minecraft Snapshot 23w12a — Minecraft.net。
1. ↑ Minecraft 26.2 Snapshot 1 — Minecraft.net。
1. ↑ MC-264622

# 导航

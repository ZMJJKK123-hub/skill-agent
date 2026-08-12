---
name: minecraft-surface-rule
description: |
  表面规则（Minecraft Wiki 中文版全量正文）。
  
  【概述】材料规则（Material Rule），亦作表面规则（Surface Rule），是一系列替换规则，为游戏决定生成初始地形后如何替换原先的初始方块。表面规则造就了各个生物群系不同的外观，将地表替换为各个生物群系应有的地表，如替换为草方块或沙…
  
  【涵盖内容】
  - bandlands
  - block
  - condition
  - sequence
  - above_preliminary_surface
  - biome
  - hole
  - noise_threshold
  - not
  - steep
  - stone_depth
  - temperature
  
  【关键定义】
  - 注册表：MATERIAL_RULE、MATERIAL_CONDITION
  - 数据包路径：data/worldgen/material_rule、data/worldgen/material_condition
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 表面规则 的完整规范时
---

本条目所述内容仅适用于Java版。
材料规则（Material Rule），亦作表面规则（Surface Rule），是一系列替换规则，为游戏决定生成初始地形后如何替换原先的初始方块。表面规则造就了各个生物群系不同的外观，将地表替换为各个生物群系应有的地表，如替换为草方块或沙子。虽然名称为表面规则，但实际上它也负责了基岩层和深板岩层的放置。

# 表面规则

Java版26.3起，材料规则在游戏内使用
```
MATERIAL_RULE
```

注册表，数据包路径为
```
worldgen/material_rule
```

，即所有材料规则定义文件都需要在
```
data/<
命名空间
>/worldgen/material_rule
```

目录内定义，材料规则标签则需要在
```
data/<
命名空间
>/tags/worldgen/material_rule
```

目录内定义。

材料规则定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] 表面规则根节点 - [图:字符串]*type：（命名空间ID）表面规则类型。 - 其他字段见下文。

表面规则可由数据包中的噪声设置指定。其相当于一种决策树，通过给定的条件和序列在指定的位置上放置指定的方块。

## bandlands

放置恶地类生物群系的陶瓦条带。

- [图:NBT复合标签/JSON对象] 表面规则根节点 - [图:字符串]*type： ``` bandlands ```

## block

放置指定的方块。

- [图:NBT复合标签/JSON对象] 表面规则根节点 - [图:字符串]*type： ``` block ``` - [图:字符串][图:NBT复合标签/JSON对象]*result_state：要放置的方块。 - - 方块状态，见Template:Nbt inherit/block state/source

## condition

根据指定的表面规则条件，检查当前位置是否测试成功，若成功则应用表面规则，否则不做处理。

- [图:NBT复合标签/JSON对象] 表面规则根节点 - [图:字符串]*type： ``` condition ``` - [图:NBT复合标签/JSON对象]*if_true：要判定的表面规则条件。 - [图:字符串]*type：（命名空间ID）表面规则条件类型。 - 其他字段见下文表面规则条件。 - [图:NBT复合标签/JSON对象]*then_run：条件通过后应用的表面规则。此节点将作为表面规则的根节点。 - 与本结构相同，递归定义。

## sequence

根据指定的序列，按照列表顺序依次应用表面规则，每个方块将应用第一个成功的表面规则。

- [图:NBT复合标签/JSON对象] 表面规则根节点 - [图:字符串]*type： ``` sequence ``` - [图:NBT列表/JSON数组]*sequence：（可以为空）一个表面规则的序列。 - [图:NBT复合标签/JSON对象]：一个表面规则。此节点将作为表面规则的根节点。 - 与本结构相同，递归定义。 - [图:字符串][图:NBT复合标签/JSON对象]：一个材料规则，可以为命名空间ID，也可以内联定义。 - 与本结构相同，递归定义。

# 表面规则条件

Java版26.3起，材料条件在游戏内使用
```
MATERIAL_CONDITION
```

注册表，数据包路径为
```
worldgen/material_condition
```

，即所有材料条件定义文件都需要在
```
data/<
命名空间
>/worldgen/material_condition
```

目录内定义，材料条件标签则需要在
```
data/<
命名空间
>/tags/worldgen/material_condition
```

目录内定义。

材料条件定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type：（命名空间ID）表面规则条件类型。 - 其他字段见下文。

## above_preliminary_surface

检查当前位置是否高于初步地表高度。初步地表高度由噪声设置[图:字符串][图:双精度浮点数][图:NBT复合标签/JSON对象]noise_router.preliminary_surface_level产生的地表高度插值后，向下偏移8格，再加上表面厚度后的值。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` above_preliminary_surface ```

## biome

检查当前位置是否在某生物群系内。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` biome ``` - [图:NBT列表/JSON数组]*biome_is：（可以为空）一个生物群系ID的列表。如果当前位置属于此列表内的生物群系，则检查成功。

## hole

检查当前位置的表面厚度是否小于0。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` hole ```

## noise_threshold

检查当前位置的噪声值是否位于指定的区间内。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` noise_threshold ``` - [图:字符串]*noise：（命名空间ID）要使用的噪声。 - [图:双精度浮点数]*min_threshold：闭区间的下限。 - [图:双精度浮点数]*max_threshold：闭区间的上限。 - [图:布尔型]is_3d：（默认为 ``` false ``` ）决定噪声采样的高度。为 ``` false ``` 时将使用Y=0处的噪声值，为 ``` true ``` 时将使用当前方块坐标处的噪声值。

## not

检查当前位置是否不满足指定的表面规则条件。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` not ``` - [图:NBT复合标签/JSON对象]*invert：指定不应满足的表面规则条件。此节点将作为表面规则条件的根节点。 - 与此结构相同，递归定义。 - [图:字符串][图:NBT复合标签/JSON对象]*invert：指定不应满足的材料条件。可以为命名空间ID，也可以内联定义。 - 与此结构相同，递归定义。

## steep

检查当前位置是否为背阳（朝向北或朝东）且高度差大于4格的陡峭斜坡。使用的高度图为
```
WORLD_SURFACE_WG
```

。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` steep ```

## stone_depth

检查当前位置与与地表或洞穴表面的距离是否小于等于指定距离。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` stone_depth ``` - [图:整型]*offset：用于检查的最大距离。此值可以与下列参数的距离分别叠加。 - [图:布尔型]*add_surface_depth：是否受表面厚度的影响。若是，则用于测试的距离还会加上表面厚度。 - [图:整型]*secondary_depth_range：表示受表面厚度附加噪声（ ``` surface_secondary ``` ）影响的程度。用于测试的距离还会加上 ``` secondary_depth_range × 噪声值 ``` 格。 - [图:字符串]*surface_type：取值只能为 ``` floor ``` （到上方地板的距离）或 ``` ceiling ``` （到下方天花板的距离）。如果是 ``` ceiling ``` ，则检测的距离为此坐标与正下方最近的液体或空气方块的距离；如果是 ``` floor ``` ，则检测的距离为此坐标与正上方最近的空气方块之间的距离再减一。

侧视图，
```
stone_depth
```

条件检查所用的各个方块的距离，左侧的[图:字符串]surface_type为
```
ceiling
```

，右侧的为
```
floor
```

注：这是应用表面规则阶段的距离，雕刻器阶段的距离始终为1。

## temperature

检查当前位置的生物群系温度是否可下雪。此温度由当前生物群系定义的[图:单精度浮点数]temperature、[图:字符串]temperature_modifier和当前Y轴高度决定。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` temperature ```

## vertical_gradient

根据给定的高度，低于某高度时始终成功，高于某高度时始终失败，而高度区间内形成渐变过渡。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` vertical_gradient ``` - [图:字符串]*random_name：命名空间ID，只用作随机数的种子。 - [图:NBT复合标签/JSON对象]*false_at_and_above：第一步检查，等于或高于此Y坐标则永远失败。 - - 垂直锚点，见Template:Nbt inherit/vertical anchor/source - [图:NBT复合标签/JSON对象]*true_at_and_below：第二步检查，等于或低于此Y坐标则永远成功。位于两坐标之间的成功的概率为 ``` (false_at_and_above - Y) / (false_at_and_above - true_at_and_below) ``` ，以形成渐变效果。 - - 垂直锚点，见Template:Nbt inherit/vertical anchor/source

## water

检查当前位置在流体下方的厚度。由于厚度的计算方式是以当前高度减去上方流体的高度，因此用于判断的数值为负数。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` water ``` - [图:整型]*offset：相对于上方液面的最大相对高度，此值可以与下列参数的距离分别叠加。相对高度为方块底面高度减去液面高度，液面高度在应用表面规则阶段为液体方块的顶面高度，在雕刻器阶段为液体方块的底面高度。在应用表面规则阶段时只要方块的上方存在液体方块则此相对高度即小于-2。因此若设为大于-1的值，则只有当与上方最近空气方块之间没有液体时条件成功；若设为-1，在应用表面规则阶段时与大于-1的值效果一样，在雕刻器阶段时永远成功。 - [图:整型]*surface_depth_multiplier：（-20≤值≤20）表示受表面厚度的影响程度，用于测试的距离还会加上表面厚度乘上此值。 - [图:布尔型]*add_stone_depth：是否检测当前方块的相对于液体表面的距离加上“该Y平面与正上方空气方块之间的非液体方块的数量”而不是当前方块相对于液体表面的距离。例如Y=2处为空气，Y=1处为水，Y=0处为石头，在该石头处应用此条件，则该Y平面（此时为Y=0平面）与正上方空气方块（此时为Y=2的空气）之间的非液体方块的数量为1（即坐标为Y=0的这个石头），游戏对这个石头测试的距离将是-1而不是-2。

侧视图，
```
water
```

条件检查所用的各个方块的距离，左侧图的[图:布尔型]add_stone_depth为
```
false
```

，右侧图为
```
true
```

；数字列左侧为应用地表规则阶段，右侧为雕刻器阶段

## y_above

检查当前位置是否位于指定的Y坐标上方。

- [图:NBT复合标签/JSON对象] 表面规则条件根节点 - [图:字符串]*type： ``` y_above ``` - [图:NBT复合标签/JSON对象]*anchor：方块通过测试的最小Y坐标。 - - 垂直锚点，见Template:Nbt inherit/vertical anchor/source - [图:整型]*surface_depth_multiplier：（-20≤值≤20）表示受表面厚度的影响程度，条件成功的最小Y坐标为[图:NBT复合标签/JSON对象]anchor加上表面厚度与此值之积。 - [图:布尔型]*add_stone_depth：是否检测当前方块的Y坐标加上“该Y平面与正上方空气方块之间的非液体方块的数量”而不是当前方块的Y坐标。

# 定义行为

本段落包含会在下一次更新中出现的内容。
这些特性在Java版26.3的开发版本中加入。

材料规则和材料条件定义数据仅在服务端启动时被加载一次，使用
```
/
reload
```

命令不可以使饰纹材料规则或材料条件定义被重新加载，而必须重启服务端。

# 应用表面规则

主条目：世界生成 § 应用表面规则和世界生成 § 地形雕刻
游戏在应用表面规则时，会创建一个“表面规则上下文”来记录数据。而实际计算中，游戏大致按照如下顺序应用表面规则：

- 检查当前位置是否是生物群系 ``` eroded_badlands ``` ，检查的Y坐标在噪声设置[图:布尔型]legacy_random_source为 ``` true ``` 时是高度图 ``` WORLD_SURFACE_WG ``` 的高度加1，为 ``` false ``` 时是固定高度Y=0，若是则放置陶瓦岩柱。
- 根据噪声设置中指定的表面规则应用表面规则。
- 检查当前位置是否是生物群系 ``` frozen_ocean ``` 或 ``` deep_frozen_ocean ``` （检查的位置与 ``` eroded_badlands ``` 相同），若是则放置冰山。至此表面规则执行完毕。

# 历史

# 注释

1. ↑ 表面厚度由表层噪声（ ``` surface ``` ）在 ``` [X, 0 ,Z] ``` 处的计算值s、基于位置相关的随机数r（取值范围为[0,1)）计算而来，计算公式为⌊2.75s+0.25r+3⌋。
1. ↑ 在雕刻器阶段时，此值总是为1。

# 参考

1. ↑ MC-278389

# 导航

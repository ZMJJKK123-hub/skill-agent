---
name: minecraft-placed-feature
description: |
  已放置的地物（Minecraft Wiki 中文版全量正文）。
  
  【概述】已放置的地物（Placed Feature）决定了游戏生成地物时的位置细节。已放置的地物定义文件是已放置的地物在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - biome
  - block_predicate_filter
  - count
  - count_on_every_layer
  - environment_scan
  - fixed_placement
  - height_range
  - heightmap
  - in_square
  - noise_based_count
  - noise_threshold_count
  - random_offset
  
  【关键定义】
  - 注册表：PLACED_FEATURE
  - 数据包路径：data/worldgen/placed_feature
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 已放置的地物 的完整规范时
---

本条目所述内容仅适用于Java版。
已放置的地物（Placed Feature）决定了游戏生成地物时的位置细节。已放置的地物定义文件是已放置的地物在数据包中的数据驱动定义文件。

# 定义格式

已放置的地物在游戏中使用
```
PLACED_FEATURE
```

注册表，数据包路径为
```
worldgen/placed_feature
```

，即所有已放置的地物定义文件都需要在
```
data/<
命名空间
>/worldgen/placed_feature
```

目录内定义，已放置的地物标签则需要在
```
data/<
命名空间
>/tags/worldgen/placed_feature
```

目录内定义。

已放置的地物定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串][图:NBT复合标签/JSON对象]*feature：一个已配置的地物，命名空间ID或内联定义均可。 - [图:NBT列表/JSON数组]*placement：一个放置修饰器的列表，列表中的放置修饰器会被按顺序依次调用。 - [图:NBT复合标签/JSON对象]：一个放置修饰器。 - 见§ 放置修饰器。

# 定义行为

已放置的地物定义数据只在服务端启动时加载一次，使用
```
/
reload
```

命令不可以使已放置的地物定义被重新加载，而必须重启服务端。

已放置的地物用于定义已配置的地物应该被放置在世界的何处。

# 地物放置机制

已配置的地物只定义了游戏可以使用的地物信息，而没有定义这个地物应该被游戏放置在何处。游戏会给地物赋予一个初始坐标进行放置。

当地物在世界生成阶段生成时，初始坐标为此区块的西北下角；当地物被另外的地物（例如
```
random_selector
```

和
```
random_patch
```

）、结构池等调用生成时，初始坐标为被调用的坐标。

游戏使用放置修饰器（Placement Modifiers）修改地物生成的坐标。在已放置的地物中，游戏会按[图:NBT列表/JSON数组]placement的顺序依次运行放置修饰器，这意味着交换此列表内部元素顺序会导致地物放置结果不同。

在世界生成阶段，以当前正在生成地物的区块为中心，周围3×3范围的区块都是这个区块内所有地物可以生成的范围。由于地物可以跨区块生成，一个地物生成后修改的地形可能干扰其他地物生成，所以世界最终放置的地物除生物群系固有的生成顺序外，还和玩家行进路线不同导致的区块加载顺序不同相关。

# 放置修饰器

放置修饰器可以接收一个输入坐标以返回输出坐标，也可以直接修改输出坐标，每个输出坐标都代表一次地物在此处的生成尝试。放置修饰器可以修改输入坐标的位置，或返回多个相同的输出坐标以增加尝试次数，或返回多个不同的输出坐标以进行多次不同的尝试，或返回空以取消这次尝试。

对于放置修饰器的列表[图:NBT列表/JSON数组]placement而言，除首个放置修饰器将初始坐标视作输入坐标外，每一个放置修饰器都会将上一个放置修饰器的输出坐标视为输入坐标。

放置修饰器的格式如下：

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type：（命名空间ID）放置修饰器类型。 - 其他字段见下文。

## biome

如果输入坐标属于的生物群系可以生成此地物，则返回输入坐标，否则返回空。

使用此放置修饰器类型的已放置的地物不能被其他的地物调用，否则游戏在世界生成阶段会抛出致命性的错误并立刻断开客户端连接。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` biome ```

## block_predicate_filter

如果输入坐标的方块满足指定的方块谓词，则返回输入坐标，否则返回空。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` block_predicate_filter ``` - [图:NBT复合标签/JSON对象]*predicate：指定输入坐标需满足的方块谓词。 - - 方块谓词，见Template:Nbt inherit/block test/source

## count

返回多个相同的坐标。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` count ``` - [图:整型][图:NBT复合标签/JSON对象]*count：（0≤值≤4096）重复返回的次数。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## count_on_every_layer

以输入坐标为准，在（0，0）到（16，16）的水平相对坐标内，搜索满足任意高度被空气、水或熔岩隔离的每一层非基岩方块，返回指定数量的此方块上方一格的坐标。

对于区块西北角的初始坐标而言，此搜索范围相当于整个区块。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` count_on_every_layer ``` - [图:整型][图:NBT复合标签/JSON对象]*count：（0≤值≤256）返回坐标的数量。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## environment_scan

从输入坐标开始，向上或向下依次检查方块，直到找到满足生成位置的坐标，返回此坐标。如果在最大步数内没有找到，则返回空。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` environment_scan ``` - [图:字符串]*direction_of_search：搜索方向。取值只能为 ``` up ``` （向上搜索）或 ``` down ``` （向下搜索）。 - [图:整型]*max_steps：（0≤值≤32）搜索的最大步数。 - [图:NBT复合标签/JSON对象]*target_condition：指定生成位置需满足的方块谓词。 - - 方块谓词，见Template:Nbt inherit/block test/source - [图:NBT复合标签/JSON对象]allowed_search_condition：若指定本字段，那么每一步检查的位置都必须满足该方块谓词，如果遇到不满足谓词的方块则立刻返回空。 - - 方块谓词，见Template:Nbt inherit/block test/source

## fixed_placement

直接指定输出坐标。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` fixed_placement ``` - [图:NBT列表/JSON数组]*positions：一个列表，列出了所有可能的输出坐标。 - [图:NBT列表/JSON数组]：一个坐标。 - [图:整型]：X坐标。 - [图:整型]：Y坐标。 - [图:整型]：Z坐标。

## height_range

修改输入坐标的Y坐标作为输出坐标。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` height_range ``` - [图:NBT复合标签/JSON对象]*height：新的Y轴坐标。 - - 高度提供器，见Template:Nbt inherit/height provider/source

## heightmap

修改输入坐标的Y坐标为指定的高度图上方一格作为输出坐标。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` height_range ``` - [图:字符串]*heightmap：使用的高度图。取值只能为 ``` MOTION_BLOCKING ``` 、 ``` MOTION_BLOCKING_NO_LEAVES ``` 、 ``` OCEAN_FLOOR ``` 、 ``` OCEAN_FLOOR_WG ``` 、 ``` WORLD_SURFACE ``` 或 ``` WORLD_SURFACE_WG ``` 。

## in_square

将输入坐标的X和Z轴坐标独立增加一个0到15内随机数作为输出坐标。

此放置修饰器类型相当于
```
random_offset
```

类型的简化形式——指定
```
y_spread
```

为0，
```
xz_spread
```

为0到15的均匀分布。

对于区块西北角的初始坐标而言，这相当于在整个区块内随机选择一个坐标作为输出。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` in_square ```

## noise_based_count

将输入坐标根据指定噪声返回一个或多个相同的坐标，或返回空。

对于某输入坐标而言，游戏会将此处的噪声值结果向下取整作为返回次数。噪声值大于0时返回多次，小于0时返回空。噪声值计算公式：
```
ceil((noise(x / noise_factor, z / noise_factor) + noise_offset) * noise_to_count_ratio)
```

。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` noise_based_count ``` - [图:双精度浮点数]*noise_factor：水平缩放噪声图。 - [图:双精度浮点数]noise_offset：（默认为0）噪声的垂直偏移。 - [图:整型]*noise_to_count_ratio：数量与噪声值间的比率。

## noise_threshold_count

将输入坐标根据指定噪声返回指定次数。

对于某输入坐标而言，游戏会将此处的噪声值与
```
noise_level
```

比较，高于此值时使用
```
below_noise
```

，否则使用
```
above_noise
```

。噪声值计算公式：
```
noise(x / 200, z / 200)
```

。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` noise_threshold_count ``` - [图:双精度浮点数]*noise_level：阈值。 - [图:整型]*below_noise：低于阈值时的返回数量。低于0时视为0。 - [图:整型]*above_noise：高于阈值时的返回数量。低于0时视为0。

## random_offset

将输入坐标进行随机偏移作为输出坐标。X轴和Z轴使用不同的随机源。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` random_offset ``` - [图:整型][图:NBT复合标签/JSON对象]*xz_spread：（-16≤值≤16）用于X和Z轴的偏移值。 - - 整数提供器，见Template:Nbt inherit/int provider/source - [图:整型][图:NBT复合标签/JSON对象]*y_spread：（-16≤值≤16）用于Y轴的偏移值。 - - 整数提供器，见Template:Nbt inherit/int provider/source

## rarity_filter

以
```
1 / chance
```

的概率返回输入坐标，否则返回空。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` rarity_filter ``` - [图:整型]*chance：（值>0）指定概率计算的分母，此值越大生成概率越低。

## surface_relative_threshold_filter

若输入坐标的Y坐标在指定的高度区间内，则返回输入坐标，否则返回空。

高度区间为
```
[地表高度 + min_inclusive, 地表高度 + max_inclusive]
```

，地表高度由高度图指定。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` surface_relative_threshold_filter ``` - [图:字符串]*heightmap：计算地表高度使用的高度图。取值只能为 ``` MOTION_BLOCKING ``` 、 ``` MOTION_BLOCKING_NO_LEAVES ``` 、 ``` OCEAN_FLOOR ``` 、 ``` OCEAN_FLOOR_WG ``` 、 ``` WORLD_SURFACE ``` 或 ``` WORLD_SURFACE_WG ``` 。 - [图:整型]min_inclusive：（默认为-2147483648）相对于地表高度的最小值。 - [图:整型]max_inclusive：（默认为2147483647）相对于地表高度的最大值。

## surface_water_depth_filter

若输入坐标所在的竖直方向上最高的非空气方块与最高的阻止运动的方块的高度差不大于给定值，则返回输入坐标，否则返回空。

两个高度分别使用高度图
```
WORLD_SURFACE
```

和
```
OCEAN_FLOOR
```

计算，此高度差通常来自最高固体方块上方的液体厚度。

- [图:NBT复合标签/JSON对象] 放置修饰器 - [图:字符串]*type： ``` surface_water_depth_filter ``` - [图:整型]*max_water_depth：最大深度。

# 历史

# 导航

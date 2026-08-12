---
name: minecraft-carver
description: |
  雕刻器定义格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】已配置的雕刻器（Configured Carver），或简称为雕刻器（Carver），是游戏进行地形雕刻时使用的基本单元。已配置的雕刻器定义文件是已配置的雕刻器在数据包中的数据驱动定义文件。
  
  【涵盖内容】
  - 雕刻器类型
  
  【关键定义】
  - 注册表：CONFIGURED_CARVER
  - 数据包路径：data/worldgen/configured_carver、data/worldgen/carver
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 雕刻器定义格式 的完整规范时
---

本条目所述内容仅适用于Java版。
已配置的雕刻器（Configured Carver），或简称为雕刻器（Carver），是游戏进行地形雕刻时使用的基本单元。已配置的雕刻器定义文件是已配置的雕刻器在数据包中的数据驱动定义文件。

# 定义格式

已配置的雕刻器在游戏中使用
```
CONFIGURED_CARVER
```

注册表。

26.3前，数据包路径为
```
worldgen/configured_carver
```

，即所有的已配置的雕刻器定义文件都需要在
```
data/<
命名空间
>/worldgen/configured_carver
```

目录下定义，已配置的雕刻器标签则需要在
```
data/<
命名空间
>/tags/worldgen/configured_carver
```

目录下定义。

26.3后，数据包路径为
```
worldgen/carver
```

，即所有的已配置的雕刻器定义文件都需要在
```
data/<
命名空间
>/worldgen/carver
```

目录下定义，已配置的雕刻器标签则需要在
```
data/<
命名空间
>/tags/worldgen/carver
```

目录下定义。

雕刻器定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:字符串]*type：（命名空间ID）雕刻器类型。 - [图:NBT复合标签/JSON对象]*config：此雕刻器的配置。 - [图:单精度浮点数]*probability：（0.0≤值≤1.0）每个区块尝试生成此雕刻器的概率。 - [图:字符串][图:NBT列表/JSON数组]*replaceable：雕刻器可以雕刻的方块。可以为一个方块ID或一个方块标签，或一个方块ID的列表。 - [图:NBT复合标签/JSON对象]*y：雕刻器尝试生成的高度。 - - 高度提供器，见Template:Nbt inherit/height provider/source - [图:NBT复合标签/JSON对象]*lava_level：低于或等于此Y坐标的雕刻区域将尝试填充熔岩。 - - 垂直锚点，见Template:Nbt inherit/vertical anchor/source - [图:NBT复合标签/JSON对象]debug_settings：雕刻器的调试设置。 - [图:布尔型]debug_mode：（默认为 ``` false ``` ）是否启用雕刻器的调试模式。 - [图:字符串][图:NBT复合标签/JSON对象]air_state：替换空气方块。默认为金合欢木按钮的默认方块状态。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]water_state：替换水。默认为蜡烛的默认方块状态，若指定的方块能含水则会含水。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]lava_state：替换熔岩。默认为橙色染色玻璃板的默认方块状态。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:字符串][图:NBT复合标签/JSON对象]barrier_state：替换含水层的隔离方块。默认为玻璃的默认方块状态。 - - 方块状态，见Template:Nbt inherit/block state/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*yScale：垂直缩放雕刻器洞穴。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - 依雕刻器类型的额外字段，见§ 雕刻器类型。

## 雕刻器类型

雕刻器类型（Carver Type），也可简称为雕刻器，决定了雕刻器的行为。游戏共有三种雕刻器类型：

- ``` cave ``` - 洞穴雕刻，雕刻出环状内庭和洞穴隧道，生成最常见的小型洞穴。
- ``` canyon ``` - 峡谷雕刻，雕刻出一条峡谷。
- ``` nether_cave ``` - 洞穴雕刻，类似于 ``` cave ``` ，但洞穴的竖直方向更大，不会计算含水层与表面规则，固定于 ``` bottom_y + 32.0 ``` 高度下填充熔岩。

洞穴雕刻配置如下：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*config - [图:单精度浮点数][图:NBT复合标签/JSON对象]*horizontal_radius_multiplier：水平缩放洞穴的隧道。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*vertical_radius_multiplier：垂直缩放洞穴的隧道。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*floor_level：（0.0≤值≤1.0）改变洞穴水平地板的形状。如果为0.0，使用椭球体进行雕刻。若为1.0，使用上半椭球体进行雕刻，以得到水平的地面。 - - 浮点提供器，见Template:Nbt inherit/float provider/source

峡谷雕刻配置如下：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:NBT复合标签/JSON对象]*config - [图:单精度浮点数][图:NBT复合标签/JSON对象]*vertical_rotation：峡谷延伸垂直角度。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:NBT复合标签/JSON对象]*shape：峡谷形状配置。 - [图:单精度浮点数][图:NBT复合标签/JSON对象]*distance_factor：缩放峡谷长度，值越大越长。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*thickness：缩放峡谷长宽。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数][图:NBT复合标签/JSON对象]*horizontal_radius_factor：缩放峡谷宽度，值越大越宽。 - - 浮点提供器，见Template:Nbt inherit/float provider/source - [图:单精度浮点数]*vertical_radius_default_factor：垂直缩放峡谷。值越大越深。 - [图:单精度浮点数]*vertical_radius_center_factor：根据到峡谷中心的距离缩放高度，值越大使峡谷中心越深。 - [图:整型]*width_smoothness：（值≥1）值越高，峡谷的墙壁在垂直方向上越平滑。

# 定义行为

已配置的雕刻器定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以重新加载已配置的雕刻器定义，而必须重启服务端。

在世界生成阶段，已配置的雕刻器会在指定位置上生成雕刻器洞穴。详细的生成方式参见世界生成 § 地形雕刻。

# 历史

# 导航

---
name: minecraft-noise
description: |
  噪声（Minecraft Wiki 中文版全量正文）。
  
  【概述】本条目介绍的是用于世界生成的技术性概念。关于在简体中文字幕中被称为“怪异的噪声”的环境音效，请见“洞穴音效”。
  
  【涵盖内容】
  - （自动提取章节）
  
  【关键定义】
  - 注册表：NOISE
  - 数据包路径：data/worldgen/noise
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 噪声 的完整规范时
---

本条目介绍的是用于世界生成的技术性概念。关于在简体中文字幕中被称为“怪异的噪声”的环境音效，请见“洞穴音效”。

本条目所述内容仅适用于Java版。

噪声（Noise）是游戏用于将一个坐标转换为一个数值的技术性概念。噪声定义文件是噪声在数据包中的数据驱动定义文件。

# 定义格式

噪声在游戏内使用
```
NOISE
```

注册表，数据包路径为
```
worldgen/noise
```

，即所有噪声定义文件都需要在
```
data/<
命名空间
>/worldgen/noise
```

目录中定义，噪声标签则需要在
```
data/<
命名空间
>/tags/worldgen/noise
```

目录中定义。

噪声定义文件使用JSON格式，并具有下列结构：

- [图:NBT复合标签/JSON对象] JSON文件根对象 - [图:整型]*firstOctave / [图:整型]*base_octave：主倍频。如果噪声设置里的[图:布尔型]legacy_random_source为true，必须为小于等于1的整数，否则取值范围不限。 - [图:NBT列表/JSON数组]*amplitudes / [图:NBT列表/JSON数组]amplitude_modifiers：振幅列表。将此列表记为{a0,a1,a2,⋯,an}，则列表中第i项（从0开始数）的子噪声的频率为2i+o，其中o为[图:整型]firstOctave的值；此子噪声的振幅（与值域相关）为2n−iai2n+1−1。各频率的子噪声值相加以得到总噪声值，取值上下限为±10r(l+1)∑i=0n2n−iai3(l+2)(2n+1−1)，其中l是非零振幅子噪声的最大与最小编号之差，r为3维改进版柏林噪声的最大值，此值为常数，大于1且小于1.5，可以取为1.036353811211803。如果噪声设置里的[图:布尔型]legacy_random_source为true，则此列表长度必须小于等于1−o，否则长度不限。应用于每个倍频程的缩放因子。列表中的元素数量必须与 ``` octave_count ``` 相同。如果未指定，则默认为 ``` 1.0 ``` 。 - [图:双精度浮点数]：此倍频下的值。 - [图:单精度浮点数]base_amplitude：应用于噪声输出的比例因子，不能为负数。 - [图:整型]octave_count：要采样的倍频程数量，取值范围为1至32（含边界）。 - [图:布尔型]normalize：控制输出幅度的归一化方式。如果为 ``` true ``` ，则 ``` base_amplitude ``` 表示输出的期望幅度，即99.7%的样本位于 ``` [-base_amplitude;base_amplitude] ``` 内。如果为 ``` false ``` ，则基础幅度表示第一个倍频程的幅度。如果为 ``` "legacy" ``` ，则采用上一格式所表达的相同归一化行为。如果未指定，则默认为 ``` true ``` 。

# 定义行为

噪声定义数据仅在服务端启动时加载一次，使用
```
/
reload
```

命令不可以使噪声定义被重新加载，而必须重启服务端。

噪声可以被密度函数或表面规则调用，以提供基于坐标的随机值。

除了被密度函数或表面规则调用之外，一些噪声还有着特定的、硬编码的其他用途，包括但不限于：

- ``` minecraft:surface ``` ：表面规则计算使用的表层厚度。
- ``` minecraft:surface_secondary ``` ：表面规则计算使用的附加表层厚度。
- ``` minecraft:clay_bands_offset ``` ：用以生成 ``` bandlands ``` 表面规则中的恶地陶瓦条带。
- ``` minecraft:badlands_pillar ``` 、 ``` minecraft:badlands_pillar_roof ``` 、 ``` minecraft:badlands_surface ``` ：硬编码在 ``` minecraft:eroded_badlands ``` 生物群系生成岩柱。
- ``` minecraft:iceberg_pillar ``` 、 ``` minecraft:iceberg_pillar_roof ``` 、 ``` minecraft:iceberg_surface ``` ：硬编码在 ``` minecraft:frozen_ocean ``` 和 ``` minecraft:deep_frozen_ocean ``` 生物群系生成冰山。

# 历史

# 参见

- 噪声生成器

# 参考

1. ↑ https://www.gamedev.net/forums/topic/285533-2d-perlin-noise-gradient-noise-range--/?page=3

# 外部链接

- 柏林噪声
- misode.github.io网站上的噪声生成器

# 导航

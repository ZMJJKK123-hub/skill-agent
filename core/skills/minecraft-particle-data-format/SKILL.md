---
name: minecraft-particle-data-format
description: |
  粒子数据格式（Minecraft Wiki 中文版全量正文）。
  
  【概述】本页面主要介绍粒子的数据格式。粒子的格式在
  
  【涵盖内容】
  - 带粒子选项的粒子类型
  - 简单粒子类型
  - RGB颜色
  - ARGB颜色
  - 方块粒子选项
  - 粉末粒子选项
  - 粉末颜色过渡选项
  - 颜色粒子选项
  - 物品粒子选项
  - Power Particle Option
  - 幽匿块充能粒子选项
  - 尖啸粒子选项
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 粒子数据格式 的完整规范时
---

本条目所述内容仅适用于Java版。
本页面主要介绍粒子的数据格式。粒子的格式在
```
/
particle
```

等命令中时应遵循SNBT格式，在生物群系和魔咒等数据包文件时应遵循JSON格式。

# 数据格式

所有粒子均具有下列格式：

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:字符串]*type：粒子类型，参见Java版粒子 § 类型。 - 其他标签与粒子类型而定，见下文。

游戏中的粒子可以简要地分为两类：带粒子选项的粒子类型和简单粒子类型。

## 带粒子选项的粒子类型

带粒子选项的粒子类型需要在其数据格式中指定粒子选项，否则游戏解析失败。目前所有带粒子选项的粒子类型如下：

## 简单粒子类型

简单粒子类型（Simple Particle Type）是不带粒子选项的粒子类型，其数据格式仅需指定粒子类型。所有非上表列出的粒子类型都是简单粒子类型。

# 通用结构

粒子选项使用了一些通用的结构，主要表示粒子的颜色。

## RGB颜色

表示一个RGB颜色。如果采用列表格式，但取值超出了范围，则粒子的颜色为未定义行为。

- [图:整型][图:NBT列表/JSON数组] RGB颜色

- - - 若为[图:整型]整型，则以十进制数字表示RGB颜色，每个通道占用8位。除最高8位外，从高到低依次为红色通道、绿色通道、蓝色通道。 - 即：Red<<16 + Green<<8 + Blue，最高8位对RGB颜色没有任何作用。 - - 若为[图:NBT列表/JSON数组]列表，则以3个浮点数表示RGB颜色，依次代表红色通道、绿色通道、蓝色通道。游戏在保存为整数时始终认为最高8位为255。 - [图:单精度浮点数]：颜色的R通道分量。取值为 ``` [0, 1] ``` 的闭区间。 - [图:单精度浮点数]：颜色的G通道分量。取值为 ``` [0, 1] ``` 的闭区间。 - [图:单精度浮点数]：颜色的B通道分量。取值为 ``` [0, 1] ``` 的闭区间。

正在加载互动小工具。如果加载失败，请您刷新本页面并检查JavaScript是否已启用。

## ARGB颜色

表示一个ARGB颜色。如果采用列表格式，但取值超出了范围，则粒子的颜色为未定义行为。

- [图:整型][图:NBT列表/JSON数组] ARGB颜色

- - - 若为[图:整型]整型，则以十进制数字表示ARGB颜色，每个通道占用8位。从高到低依次为透明通道、红色通道、绿色通道、蓝色通道。 - 即：Alpha<<24 + Red<<16 + Green<<8 + Blue。 - - 若为[图:NBT列表/JSON数组]列表，则以4个浮点数表示ARGB颜色，依次代表红色通道、绿色通道、蓝色通道、透明通道。 - [图:单精度浮点数]：颜色的R通道分量。取值为 ``` [0, 1] ``` 的闭区间。 - [图:单精度浮点数]：颜色的G通道分量。取值为 ``` [0, 1] ``` 的闭区间。 - [图:单精度浮点数]：颜色的B通道分量。取值为 ``` [0, 1] ``` 的闭区间。 - [图:单精度浮点数]：颜色的A通道分量。取值为 ``` [0, 1] ``` 的闭区间。

# 粒子选项

## 方块粒子选项

方块粒子选项（Block Particle Option）需要指定粒子使用的方块状态，不同的方块状态可能具有不同的方块纹理及方块粒子纹理。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:字符串][图:NBT复合标签/JSON对象]*block_state：粒子要使用的方块状态。 - - 若类型为[图:字符串]字符串，则直接指定一个方块的命名空间ID，其方块属性均使用默认值。 - - 若类型为[图:NBT复合标签/JSON对象]对象，则表示一个完整的方块状态： - - 方块状态，见Template:Nbt inherit/block state/source

示例：

- ``` /particle block{block_state: "minecraft:diamond_block"} ``` 会创建一个钻石块的粒子。
- ``` /particle block{block_state: {Name: "minecraft:grass_block", Properties: {snowy: "true"}}} ``` 会创建一个覆雪草方块的粒子。

## 粉末粒子选项

粉末粒子选项（Dust Particle Options）是一种可缩放粒子选项（Scalable Particle Options）。简而言之，不仅需指定粒子颜色，还需指定粒子大小。且其大小还影响粒子的寿命。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型][图:NBT列表/JSON数组]*color：粒子颜色，使用RGB颜色指定。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:单精度浮点数]*scale：（0.01≤值≤4.0）粒子的尺寸缩放倍率和寿命倍率。粒子的寿命为8到40游戏刻的随机数乘上此缩放值，最小不会低于1。

示例：

- ``` /particle dust{color: [0.0, 0.0, 1.0], scale: 1.0} ``` 会创建一个大小为1.0的蓝色粒子。

## 粉末颜色过渡选项

粉末颜色过渡选项（Dust Color Transition Options）也是一种可缩放粒子选项。该类粒子的特殊之处在于可以产生颜色渐变，渐变由起始颜色向结束颜色变化。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型][图:NBT列表/JSON数组]*from_color：粒子渐变起始时的颜色，使用RGB颜色指定。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:整型][图:NBT列表/JSON数组]*to_color：粒子渐变结束时的颜色，使用RGB颜色指定。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:单精度浮点数]*scale：（0.01≤值≤4.0）粒子的尺寸缩放倍率和寿命倍率。粒子的寿命为8到40游戏刻的随机数乘上此缩放值，最小不会低于1。

示例：

- ``` /particle dust_color_transition{from_color: [0.0, 0.0, 1.0], scale: 1.0, to_color: [1.0, 0.0, 0.0]} ``` 会创建一个大小为1.0的蓝色粒子，然后该粒子在消散过程中会逐渐转变为红色。

## 颜色粒子选项

颜色粒子选项（Color Particle Option）为粒子提供带一个透明通道的ARGB颜色。与普通的RGB颜色相比，ARGB颜色多出一个A值以表示透明通道（即Alpha通道）。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型][图:NBT列表/JSON数组]*color：粒子的颜色，使用ARGB颜色指定。 - - ARGB颜色，见Template:Nbt inherit/argb color/source

示例：

- ``` /particle entity_effect{color: [1, 1, 1, 1]} ``` 会创建一个白色的完全不透明的粒子。以下两个示例效果相同，但使用数字来表示颜色。 - ``` /particle entity_effect{color: -1} ``` - ``` /particle entity_effect{color: 4294967295L} ```

## 物品粒子选项

物品粒子选项（Item Particle Option）需指定粒子要显示的物品堆叠，不同的物品堆叠可能具有不同的物品纹理和物品粒子纹理。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:字符串][图:NBT复合标签/JSON对象]*item：一个物品堆叠。 - - 物品模板，见Template:Nbt inherit/item template/source

示例：

- ``` /particle item{item: "minecraft:apple"} ``` 和 ``` /particle item{item: {id: "minecraft:apple"}} ``` 会创建一个苹果物品的粒子。

## Power Particle Option

Power Particle Option指定了粒子的速度。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:单精度浮点数]power：（默认为1）粒子的速度。在初始随机数计算完毕后粒子的初始速度将乘上此值。

## 幽匿块充能粒子选项

幽匿块充能粒子选项（Sculk Charge Particle Options）指定了幽匿块充能粒子在摄像机视角下的显示方向。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:单精度浮点数]*roll：以弧度制表示的粒子的显示角度。

示例：

- ``` /particle sculk_charge{roll: 3.14} ``` 会在当前视角下产生一个近似于向下“冒泡”的粒子。

## 尖啸粒子选项

尖啸粒子选项（Shriek Particle Option）指定了尖啸粒子产生的延迟时间。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型]*delay：粒子出现的延迟时间，以游戏刻为单位。

示例：

- ``` /particle shriek{delay: 100} ``` 会在100游戏刻后显示 ``` shriek ``` 粒子。

## 药水粒子选项

药水粒子选项（Spell Particle Option）指定了粒子的颜色和速度。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型][图:NBT列表/JSON数组]color：（默认为 ``` 0xFFFFFF ``` ）粒子的颜色，使用RGB颜色指定。 - - RGB颜色，见Template:Nbt inherit/rgb color/source - [图:单精度浮点数]power：（默认为1）粒子的速度。在初始随机数计算完毕后粒子的初始速度将乘上此值。

## 振动粒子选项

振动粒子选项（Vibration Particle Option）指定了振动粒子的目标位置。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:NBT复合标签/JSON对象]*destination：目标位置。仅能使用 ``` block ``` 类型的位置源。 - [图:字符串]type：位置源类型。取值只能为 ``` block ``` 或 ``` entity ``` 。 - - 如果 ``` type ``` 是 ``` block ``` ，则以某个方块作为位置源： - [图:整型数组]*pos：方块坐标。 - - 如果 ``` type ``` 是 ``` entity ``` ，则以某个实体作为位置源： - [图:整型数组]*source_entity：UUID，将获取此UUID的实体坐标。 - [图:单精度浮点数]y_offset：（默认为0.0）相对于实体脚部坐标的Y轴偏移。 - [图:整型]*arrival_in_ticks：移动持续时间，也是粒子的寿命。以游戏刻为单位。

示例：

- ``` /particle vibration{destination:{type: "block", pos:[5, 64, 0]}, arrival_in_ticks: 200} ``` 将会创建一个从当前的执行坐标移动到 ``` 5.5 64.5 0.5 ``` ，耗时200游戏刻的 ``` vibration ``` 粒子。

## 目标颜色粒子选项

目标颜色粒子选项（Target Color Particle Option）指定了粒子颜色和一个目标位置，粒子将移动到该目标位置，同时形成一条粒子轨迹。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型][图:NBT列表/JSON数组]*color：粒子的颜色，使用ARGB颜色指定。 - - ARGB颜色，见Template:Nbt inherit/argb color/source - [图:整型]*duration：粒子从原点飞到目标位置所需的时间，单位为刻。 - [图:NBT列表/JSON数组]*target：粒子所指向的位置。 - [图:双精度浮点数]：X坐标。 - [图:双精度浮点数]：Y坐标。 - [图:双精度浮点数]：Z坐标。

示例：

- ``` /particle trail{target:[5, 64, 0], color: 428499001,duration:5} ``` 将会创建一个从当前的执行坐标移动到 ``` 5.5 64.5 0.5 ``` 的粒子。

## 间歇泉粒子选项

间歇泉粒子选项（Geyser Particle Option）指定了间歇泉的粒子寿命和上升高度。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型]*water_blocks：对于 ``` geyser_plume ``` ：控制粒子寿命（ ``` water_blocks ``` ×25游戏刻）和上升高度（ ``` water_blocks ``` ×5格）；对于 ``` geyser ``` ：将该值传递给子粒子。

示例：

- ``` /particle geyser_plume{water_blocks:4} ``` 将会创建一个持续100游戏刻（5秒）的20格的间歇泉上升水柱。

## 间歇泉底部粒子选项

间歇泉底部粒子选项（Geyser Base Particle Option）指定了间歇泉底部的粒子大小和速度增量。

- [图:NBT复合标签/JSON对象] 粒子选项 - [图:整型]*water_blocks：控制粒子大小（3.0+ ``` water_blocks ``` ×0.125）和速度基数（ ``` water_blocks ``` ×0.25）。 - [图:单精度浮点数]burst_impulse_base：速度增量，与速度基数相加。

示例：

- ``` /particle minecraft:geyser_base{water_blocks:5, burst_impulse_base:3} ``` 将会创建一个粒子大小为3.625，速度增量为4.25的间歇泉底部粒子。

# 历史

# 参见

- 生物群系数据格式
- 魔咒数据格式

# 导航

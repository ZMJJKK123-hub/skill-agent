---

name: minecraft-custom-world-generation
description: "Minecraft Custom World Generation 自定义世界生成概述：World Presets 世界预设（控制世界维度、chunk generator 噪声/调试/平坦）、Dimensions 维度（噪声生成器定义噪声设置/生物群系/生物群系分布）、Noise Settings 噪声设置（地形形状、噪声洞穴、地形生成方块）、Density Functions 密度函数（提供坐标依赖值给噪声路由器）、Noise 噪声（坐标依赖值、密度函数/表面规则引用）、Biomes 生物群系（独特特性/雕刻器/气候/生物生成/环境/颜色）、Carvers 雕刻器（洞穴和峡谷雕刻、噪声洞穴来自噪声设置）、Features 特性（每区块生成的装饰方块结构、配置特性和放置特性）、Structures 结构（结构特性生成结构、jigsaw 结构高度自定义、结构模板/定义/结构集/模板池/处理器列表）、Surface Builders 表面构建器（已移除 21w41a 后由噪声设置控制表面方块）。"
whenToUse: "Use when creating custom world generation via datapacks."

---

# Custom World Generation

This content applies only to Java Edition. This article covers datapack-controlled custom worlds (see "Custom" for JSON-driven worlds, and "Custom/Java Edition before 1.13" for legacy world types).

Custom world generation lets datapacks change how worlds generate.

## World presets and dimensions

World presets and dimensions control which dimensions a world has. Every dimension defines its chunk generator (noise, debug, or flat); noise generators additionally define noise settings, biomes, and biome distribution. See the world preset definition format and dimension definition format.

## Noise settings

Noise settings define the shapes of terrain and noise caves plus the blocks attached during terrain generation; used via the dimension's noise generator. See noise settings.

## Density functions

Density functions provide coordinate-dependent values to the noise router of noise settings. See density functions.

## Noise

Noise produces coordinate-dependent values, referenced by density functions or surface rules. See noise.

## Biomes

Biomes are regions within a dimension with unique features, carvers, climate, mob spawning, ambience, and colors. See the biome definition format.

## Carvers

Carvers carve caves and canyons. Note: noise caves come from noise settings, not carvers. See the carver definition format.

## Features

Features are decorative block structures generated per chunk after terrain. See configured features and placed features.

## Structures

Structures (structure features) generate structures; jigsaw structures offer extensive customization. See structure templates, structure definitions, structure sets, template pools, and processor lists.

## Surface builders (removed)

Since 21w41a, surface blocks are controlled by noise settings. Surface builders were removed from Java Edition.

---
name: minecraft-custom-world-generation
description: Custom world generation overview: presets, dimensions, noise, biomes, features, structures.
whenToUse: Use when creating custom world generation via datapacks.
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

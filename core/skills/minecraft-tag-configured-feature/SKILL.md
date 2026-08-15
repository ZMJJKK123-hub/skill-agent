---
name: minecraft-tag-configured-feature
description: Configured feature tags referenced from biomes for feature generation.
whenToUse: Use when writing or understanding configured feature tags (e.g. can_spawn_from_bone_meal).
---

# Configured Feature Tags

This content applies only to Java Edition.

Configured feature tags are groups of configured features.

## Usage

Configured feature tags can be referenced in biomes to indicate that the biome can generate features of that group. The game also defines some tags with special purposes.

## Tag list

### `#can_spawn_from_bone_meal` (8 entries)

If these features are defined in a biome, using bone meal on grass blocks in that biome has a chance to generate these features instead of short or tall grass:

- `flower_default`
- `flower_flower_forest`
- `flower_meadow`
- `wildflower`
- `flower_pale_garden`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

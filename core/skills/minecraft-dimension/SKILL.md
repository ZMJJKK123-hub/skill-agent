---
name: minecraft-dimension
description: Dimension definition JSON: LEVEL_STEM registry, chunk generators, biome sources.
whenToUse: Use when writing datapack dimension definitions or custom world generation dimensions.
---

# Dimension Definitions

This content applies only to Java Edition.

Dimension definition files are the data-driven definitions of dimensions in datapacks.

## Definition format

Dimensions use the `LEVEL_STEM` registry; the datapack path is `dimension` (definitions in `data/<namespace>/dimension`, tags in `data/<namespace>/tags/dimension`).

Definition files use JSON with the following structure:

- JSON file root object
  - `type` (string/compound, required): dimension type; inline definitions are parsed but fail datapack verification (no namespace ID) and interrupt connection.
  - `generator` (compound, required): chunk generator.
    - `type` (string, required): chunk generator type; extra fields per type (below).

### Chunk generators

The chunk generator decides how terrain generates, plus the dimension's sea level, min build height, and total height. Noise generators read these from noise settings; the other two hardcode min height 0 and height 384 (flat sea level −64, debug 63).

- `debug`: generates the debug mode grid of blocks; no other terrain; fixed plains biome.
- `flat`: generates superflat worlds. `settings` (compound, required): flat generator settings.
- `noise`: generates complex terrain with a noise generator. Fields:
  - `biome_source` (compound, required): biome distribution (below).
  - `settings` (string/compound, required): noise settings.

### Biome sources

Only noise generators can set a biome source; others use a fixed source.

- `checkerboard`: places biomes in a checkerboard. `biomes` (string/list, required: ID, tag, or list), `scale` (int, 0≤v≤62, default 2; each increment doubles the cell size; 0 = one chunk per cell).
- `fixed`: always uses one biome. `biome` (string, required).
- `multi_noise`: places biomes by biome noise; used by the Overworld and Nether. Either `preset` (string/compound, required) referencing a parameter list, or a non-empty `biomes` list of parameter points, each `biome` (string, required) + `parameters` (compound, required).
- `the_end`: used by the End dimension.

## Multi-noise parameter lists

Stored in `data/<namespace>/worldgen/multi_noise_biome_source_parameter_list`; root object: `preset` (string, required): a biome parameter (vanilla provides `overworld` and `nether`). These lists only reference hardcoded parameters; vanilla uses them to temporarily modify Overworld biome distribution for experimental biomes.

## Definition behavior

Dimension data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. All available dimensions load dynamically when the save loads; disabling the providing datapack removes the dimension (adding/removing dimensions after world creation is discouraged — it may corrupt saves). Vanilla defines no dimension files; it registers dimensions via world presets, but dimension files override world preset definitions.

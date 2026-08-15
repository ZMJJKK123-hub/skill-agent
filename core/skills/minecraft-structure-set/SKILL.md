---

name: minecraft-structure-set
description: "Structure set definition JSON: STRUCTURE_SET registry, placement types."
whenToUse: "Use when writing datapack worldgen structure_set definitions."

---

# Structure Sets

This content applies only to Java Edition.

Structure sets determine how structures generate during world generation. Definition files are their data-driven definitions in datapacks.

## Definition format

Structure sets use the `STRUCTURE_SET` registry; the datapack path is `worldgen/structure_set` (definitions in `data/<namespace>/worldgen/structure_set`, tags in `data/<namespace>/tags/worldgen/structure_set`).

Definition files use JSON with the following structure:

- JSON file root object
  - `structures` (list, may be empty): placeable structure features.
    - `structure` (string/compound, required): a structure; inline definitions fail chunk saving (no namespace ID).
    - `weight` (int, required): (≥1) selection weight.
  - `placement` (compound, required): placement behavior.
    - `salt` (int, required): random seed salt (non-negative).
    - `frequency` (float, default 1.0): (0.0≤v≤1.0) attempt probability when other conditions hold.
    - `frequency_reduction_method` (string, default `default`): `default` (world seed + coords + salt), `legacy_type_1` (seed + coords only), `legacy_type_2` (like default with fixed salt 10387320), `legacy_type_3` (seed + coords only).
    - `exclusion_zone` (compound): structures of this set cannot generate near another set; `chunk_count` (int, required, 1–16) + `other_set` (string, required).
    - `locate_offset` (list, default [0,0,0]): `/locate structure` offset in chunks; each −16..16.
    - `type` (string, required): placement type (below).

### Placement types

- `concentric_rings` (vanilla strongholds): fixed count per dimension in concentric rings around the world center.
  - `distance` (int, required): (0≤v≤1023) ring width + gap, in 6-chunk units.
  - `count` (int, required): (1≤v≤4095) total attempts in the dimension.
  - `spread` (int, required): (0≤v≤1023) attempts in the central ring.
  - `preferred_biomes` (string/list, required): biomes the structure prefers.
- `random_spread` (vanilla ocean monuments, swamp huts): the dimension is divided into `spacing`-chunk cells, each attempting once; structures generate only inside a `separation`-chunk inner area (extra strips never generate).
  - `spread_type` (string, default `linear`): `linear` or `triangular` (fewer extremes).
  - `spacing` (int, required): (1≤v≤4096) average distance in chunks.
  - `separation` (int, required): (0≤v<spacing) minimum distance; max distance = 2×spacing − separation.
- `dimension_origin` (upcoming, Java 26.3): places at the dimension origin — for noise generators, preferably from `spawn_target`; otherwise chunk (0,0).

## Definition behavior

Structure set data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. During generation each dimension evaluates available sets; a structure is placed only if the probability, biome, and terrain checks pass, recording structure pieces to generate on chunk load.

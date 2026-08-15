---

name: minecraft-template-pool
description: "Template pool (jigsaw pool) format — elements, generation rules, fallback."
whenToUse: "Use when authoring template pools for jigsaw structures."

---

# Template Pool

Template pools (structure pools / jigsaw pools) are the basic units for picking sub-structures during jigsaw generation. Java Edition only.

## Definition Format

Registry `TEMPLATE_POOL`, data pack path `worldgen/template_pool` (files in `data/<namespace>/worldgen/template_pool/`; tags in `tags/worldgen/template_pool/`).

- `fallback` (required) — the fallback pool: one element is picked from it to terminate the jigsaw structure.
- `elements` (required) — list of `{element, weight (1–150)}`.

### Element Types

- `empty_pool_element` — generates nothing.
- `feature_pool_element` — generates a placed feature: `projection` (`rigid` — no adjustment; `terrain_matching` — offset to match terrain) + `feature` (placed feature). Placement assumes the feature has a jigsaw block named `minecraft:bottom`, rollable joint, `final_state` air, block state `orientation=down_south`.
- `list_pool_element` — places the `elements` (recursive) in order, overlapping.
- `single_pool_element` — places a structure template: `projection`, `location` (template ID), `override_liquid_settings` (default `apply_waterlogging`; `ignore_waterlogging` replaces liquids directly), `processors` (processor list ID or inline, applied before placement). Placement order: convert jigsaw blocks, remove structure void, handle liquids, apply processors — then place. Removed void/air positions keep their pre-existing blocks.
- `legacy_single_pool_element` — like `single_pool_element` but additionally removes air.

## Behavior

Definitions load once at server startup (restart required). Pools serve `jigsaw` structures (each jigsaw block names its target pool); only structures with matching jigsaw blocks can connect. Pools are also callable via `/place jigsaw`.

Generation picks a random element. In the start pool, a named start jigsaw must exist (else generation fails). In non-start pools, success requires:

1. A jigsaw block with matching name and matching orientation exists (horizontal↔horizontal, up↔down).
2. The element's 3D Chebyshev distance from the structure start ≤ the structure's `max_distance_from_center` (128 for commands/jigsaw-GUI generation).
3. No overlap with already-generated jigsaws (unless the jigsaw points inside the current piece).
4. If the jigsaw points inside the current piece, the element and everything after must stay fully inside that piece.

On failure the next element is tried; if none works, the fallback pool is used. The fallback generates (a) at the end of the last layer when the generation depth is reached, or (b) when no element of the target pool could generate. If the fallback pool's element also fails, nothing generates.

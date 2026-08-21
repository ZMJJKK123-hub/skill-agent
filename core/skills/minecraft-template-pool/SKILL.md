---

name: minecraft-template-pool
description: "Minecraft Template Pool 模板池（拼图池）格式：TEMPLATE_POOL 注册表、data/<namespace>/worldgen/template_pool/ 数据包路径、tags/worldgen/template_pool/ 标签、JSON 格式（fallback 回退池 终止拼图结构、elements 元素列表 element+weight 1-150）、Element Types 元素类型（empty_pool_element 无生成、feature_pool_element 生成放置特性 projection rigid/terrain_matching + feature 放置特性 假设jigsaw方块名minecraft:bottom 可滚动接头 final_state air orientation=down_south、list_pool_element 按顺序放置elements 递归 重叠、single_pool_element 放置结构模板 projection+location 模板ID+override_liquid_settings+processors 处理器列表 放置顺序：转换拼图方块→移除结构虚空→处理液体→应用处理器→放置、legacy_single_pool_element 同single但额外移除空气）、Behavior 行为（服务器启动加载一次、为jigsaw结构服务 每个拼图方块命名目标池、仅匹配拼图方块的结构可连接、可通过/place jigsaw调用）、Generation Rules 生成规则（随机选择元素、起始池必须存在命名起始拼图、非起始池成功条件：匹配名称和方向的拼图方块、3D切比雪夫距离≤结构max_distance_from_center、无重叠 除非拼图指向当前片段内部、指向内部时元素及后续必须完全在片段内）、Fallback 回退（失败时尝试下一个元素、无元素可用时使用回退池、在生成深度到达时或目标池无元素可生成时使用回退池、回退池元素也失败则无生成）。"
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

---

name: minecraft-placed-feature
description: "Minecraft Placed Feature 放置特性格式：Definition Format 定义格式（PLACED_FEATURE 注册表、data/<namespace>/worldgen/placed_feature/ 数据包路径、tags/worldgen/placed_feature/ 标签、feature 配置特性ID或内联、placement 放置修改器列表 顺序执行 交换改变结果）、Placement Mechanics 放置机制（初始坐标 装饰期间区块西北下角/其他特性调用时调用坐标、修改器接收输入坐标产生输出坐标 每个输出=一次放置尝试、可能移动/重复/发射多个坐标/返回无内容取消、装饰期间特性可跨3×3区块区域生成 跨区块干扰+区块加载顺序使放置依赖）、Placement Modifiers 放置修改器列表（biome 输入坐标生物群系能托管此特性则传递 否则无内容 不能被其他特性调用致命错误、block_predicate_filter 块谓词过滤 predicate、count 计数 0-4096 重复坐标、count_on_every_layer 每层计数 0-256 查找非基岩层 返回该层上方坐标、environment_scan 环境扫描 direction_of_search up/down max_steps 0-32 target_condition allowed_search_condition、fixed_placement 固定放置 positions 坐标列表、height_range 高度范围 替换Y为高度提供器 height、heightmap 高度图 设置Y=高度图+1 MOTION_BLOCKING/MOTION_BLOCKING_NO_LEAVES/OCEAN_FLOOR/OCEAN_FLOOR_WG/WORLD_SURFACE/WORLD_SURFACE_WG、in_square 方形内 X和Z添加随机0-15偏移 等同random_offset xz_spread uniform 0-15、noise_based_count 基于噪声计数 ceil((noise(x/factor,z/factor)+offset)×ratio)、noise_threshold_count 噪声阈值计数 noise(x/200,z/200) vs noise_level below/above counts、random_offset 随机偏移 xz_spread/y_spread int provider -16..16、rarity_filter 稀有度过滤 概率 1/chance、surface_relative_threshold_filter 表面相对阈值过滤 Y∈[surface+min_inclusive,surface+max_inclusive]、surface_water_depth_filter 表面水深过滤 (WORLD_SURFACE-OCEAN_FLOOR)≤max_water_depth）。"
whenToUse: "Use when authoring placed feature JSON files in data/worldgen/placed_feature/."

---

# Placed Feature

Placed features decide where configured features generate. Java Edition only.

## Definition Format

Registry `PLACED_FEATURE`, data pack path `worldgen/placed_feature` (files in `data/<namespace>/worldgen/placed_feature/`; tags in `tags/worldgen/placed_feature/`).

```json
{
  "feature": "<configured feature ID or inline>",
  "placement": [ { "type": "...", ... }, ... ]
}
```

Placement modifiers run **in order** — swapping them changes results. Definitions load once at server startup (restart required).

## Placement Mechanics

A feature gets an initial coordinate (the chunk's NW-lower corner during decoration; the calling coordinate when invoked by another feature/structure pool). Modifiers take input coordinates and produce output coordinates (each output = one placement attempt): they may move the coordinate, repeat it (more attempts), emit several distinct coordinates, or return nothing (cancel). Each modifier receives the previous one's outputs.

During decoration, features may generate across the 3×3 chunk area around the generating chunk; cross-chunk interference plus chunk loading order (player path) makes final placement order-dependent.

## Placement Modifiers

- `biome` — pass if the input coordinate's biome can host this feature (its configured feature's biomes); else nothing. **Placed features using this modifier cannot be called by other features** (fatal error/disconnect during worldgen).
- `block_predicate_filter` — `predicate` (block predicate); pass if the block at the input passes.
- `count` — `count` (int provider, 0–4096): repeat the same coordinate that many times.
- `count_on_every_layer` — `count` (int provider, 0–256): within the (0,0)–(16,16) horizontal range, find each non-bedrock layer separated by air/water/lava and return that many coordinates one block above those blocks.
- `environment_scan` — scan up/down from the input until the target is found: `direction_of_search` (`up`/`down`), `max_steps` (0–32), `target_condition` (block predicate for the result position), `allowed_search_condition` (each checked position must pass, else return nothing).
- `fixed_placement` — `positions` (list of `[x,y,z]`): all output coordinates.
- `height_range` — replace the Y with a height provider: `height`.
- `heightmap` — set Y to the heightmap + 1: `heightmap` = `MOTION_BLOCKING`, `MOTION_BLOCKING_NO_LEAVES`, `OCEAN_FLOOR`, `OCEAN_FLOOR_WG`, `WORLD_SURFACE`, `WORLD_SURFACE_WG`. (Note: the wiki lists the type as `height_range` in the example — the actual type is `heightmap`.)
- `in_square` — add independent random 0–15 offsets to X and Z (equivalent to `random_offset` with y_spread 0 and xz_spread uniform 0–15); for a chunk-corner input this picks a random position in the chunk.
- `noise_based_count` — return count = ceil((noise(x/factor, z/factor) + offset) × ratio) copies (empty when ≤ 0): `noise_factor`, `noise_offset` (default 0), `noise_to_count_ratio`.
- `noise_threshold_count` — noise(x/200, z/200) vs `noise_level`: `below_noise` / `above_noise` counts (negative → 0).
- `random_offset` — `xz_spread` and `y_spread` (int providers, −16..16; X and Z use different random sources).
- `rarity_filter` — pass with probability 1/`chance` (>0).
- `surface_relative_threshold_filter` — pass if Y ∈ [surface + `min_inclusive`, surface + `max_inclusive`] (heightmap; defaults −2147483648/2147483647).
- `surface_water_depth_filter` — pass if (WORLD_SURFACE − OCEAN_FLOOR) ≤ `max_water_depth` (fluid thickness above the highest solid block).

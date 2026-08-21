---

name: minecraft-density-function
description: "Minecraft Density Function 密度函数格式：Definition Format 定义格式（DENSITY_FUNCTION 注册表、data/<namespace>/worldgen/density_function/ 数据包路径、tags/worldgen/density_function/ 标签、文件根对象浮点常量或对象 type 字段、支持 ID/常量/内联密度函数）、Marker Functions 标记函数（interpolated 插值 flat_cache Y=0缓存 cache_2d 二维缓存 cache_once 一次缓存 cache_all_in_cell 单元格缓存 blend_density 区块混合密度）、Univariate Functions 一元函数（abs绝对值/square平方/cube立方/sqrt平方根/half_negative/quarter_negative/invert倒数/negate取反/squeeze挤压/log对数/sign符号/rounding 取整 floor/round/ceil/truncate）、Binary Functions 二元函数（add/sub/mul/div/min/max left/right 参数）、Other Functions 其他函数（blend_alpha/blend_offset 区块混合/beardifier 结构地形适应/old_blended_noise 旧噪声算法/lerp 线性插值/noise 噪声采样/end_islands 末地岛屿/shifted_noise 偏移噪声/range_choice 范围选择/interval_select 区间选择/shift_a/shift_b/shift 偏移噪声采样/clamp 钳制/pow 幂运算/spline 三次样条/constant 常量/slice 切片/gradient 梯度/distance_to_point 点距离/find_top_surface 找顶面）、Removed Functions 已移除函数（slide/terrain_shaper_spline/weird_scaled_sampler）。"
whenToUse: "Use when authoring density function JSON files for world generation noise settings."

---

# Density Function

Density functions are mathematical expressions mapping coordinates to values, used by noise settings. Java Edition only. The page tracks 26.3 changes (renames/removals marked below).

## Definition Format

Registry `DENSITY_FUNCTION`, data pack path `worldgen/density_function` (files in `data/<namespace>/worldgen/density_function/`; tags in `tags/worldgen/density_function/`).

The file root is either a float constant (range −1000000.0..1000000.0) or an object:

```json
{ "type": "<namespace id>", ... }
```

Fields expecting a density function accept an ID, a constant number, or an inline density function JSON. Definitions load once at server startup; `/reload` does not reload them — restart the server.

## Marker Functions

- `interpolated` — interpolates the input per cell (cell size = `size_horizontal × 4` / `size_vertical × 4`).
- `flat_cache` — caches the input's Y=0 value at cell scale.
- `cache_2d` — caches the input until the current coordinates change.
- `cache_once` — caches the input until the next interpolation pass.
- `cache_all_in_cell` — internally used for `final_density`; caches per cell in the chunk's memory.
- `blend_density` — used for blending between old and new chunks.

## Univariate Functions

- `abs` — |x|.
- `square` — x².
- `cube` — x³.
- `sqrt` (26.3) — √x.
- `half_negative` — x if x > 0, else x/2.
- `quarter_negative` — x if x > 0, else x/4.
- `invert` (removed in 26.3) → `reciprocal` (26.3) — 1/x.
- `negate` (26.3) — −x.
- `squeeze` — clamp x to [−1, 1], then x/2 − x³/24.
- `log` (26.3) — natural logarithm.
- `sign` (26.3) — −1/0/1 by sign.
- Rounding (26.3): `floor`, `round`, `ceil`, `truncate` — each with `input` and optional `multiple` (rounds to a multiple of the given function's value; default constant 1).

## Binary Functions

- `add` / `sub` (26.3) / `mul` / `div` (26.3) / `min` / `max` — two arguments (`left`/`right`; older aliases `argument1`/`argument2`).

## Other Functions

- `blend_alpha` — 1 in fully-new-chunk regions (chunk blending).
- `blend_offset` — 0 in fully-new-chunk regions (chunk blending).
- `beardifier` — adds terrain around structures per their `terrain_adaptation`; called automatically during generation, no need to declare it.
- `old_blended_noise` — legacy noise algorithm: `xz_scale`, `y_scale`, `xz_factor`, `y_factor` (0.001–1000.0), `smear_scale_multiplier` (1.0–8.0); sampling step = scale × 684.412 per block.
- `lerp` (26.3) — unclamped linear interpolation `first×(1−alpha) + second×alpha`.
- `noise` — samples a noise: `noise` (ID), `xz_scale`, `y_scale`.
- `end_islands` (removed in 26.3) → `end_outer_islands` (26.3) — End outer-island noise over XZ (Y unused), range −0.84375..0.5625.
- `shifted_noise` — like `noise` but with shifted input coordinates: `noise`, `xz_scale`, `y_scale`, `shift_x`/`shift_y`/`shift_z` density functions.
- `range_choice` — `input`, `min_inclusive`, `max_exclusive`, `when_in_range`, `when_out_of_range`.
- `interval_select` — `input`, `thresholds` (ascending, non-empty), `functions` (count = thresholds length − 1, ≥2): picks the function for the interval the input falls into.
- `shift_a` / `shift_b` / `shift` — noise sampled at (x/4, 0, z/4) / (z/4, x/4, 0) / (x/4, y/4, z/4), ×4.
- `clamp` — `input`, `min`, `max`.
- `pow` (26.3) — `base`^`exponent`.
- `spline` — cubic spline: `spline` (number or object), `coordinate` (density function for the coordinate), `points` (non-empty list of `{location, value (number or nested spline), derivative}`).
- `constant` — a constant (`value`).
- `slice` (26.3) — removes one dimension: `axis` (x/y/z), `coordinate` (fixed value), `input`.
- `gradient` (26.3) — maps a clamped coordinate range to an output range: `axis`, `tiling` (`clamp_to_edge`/`repeat`/`mirrored_repeat`), `from_coordinate`, `to_coordinate`, `from_value`, `to_value`.
- `distance_to_point` (26.3) — distance to a fixed `coordinate` `[x,y,z]` with `metric` = `euclidean` (√(dx²+dy²+dz²)), `euclidean_squared`, `manhattan`, `chebyshev`.
- `y_clamped_gradient` (removed in 26.3) — clamps Y (`from_y`/`to_y`, −4064..4062) and maps linearly to `from_value`/`to_value`.
- `find_top_surface` — scans from `upper_bound` (2D density function) down to `lower_bound` to find the negative-to-positive transition: `density`, `upper_bound`, `lower_bound`, `cell_height` (>0).

## Removed Functions

- `slide` — old top/bottom slide curves from noise settings (targets outside the offset ranges, smooth transitions of `size × size_vertical`).
- `terrain_shaper_spline` — computed terrain shaper splines (`offset`/`factor`/`jaggedness`) from `continentalness`/`erosion`/`weirdness` density functions with `min_value`/`max_value`.
- `weird_scaled_sampler` — scaled/abs'd noise sampling: `rarity_value_mapper` (`type_1`: 0.75–2.0, `type_2`: 0.5–3.0), `noise`, `input`.

Source acknowledgment: parts of this page derive from Misode's JSON format documentation.

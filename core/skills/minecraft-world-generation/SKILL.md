---

name: minecraft-world-generation
description: "Minecraft World Generation 世界生成：Generation Phases 生成阶段（12个阶段：Empty 空、Structure Starts 结构开始 计算可放置结构/范围/片段/起点、Structure References 结构引用 计算引用片段 持久化到区块数据、Biomes 生物群系 计算所有生物群系单元 持久化、Noise 噪声 密度函数填充初始方块 含水层放置流体 矿脉生成 第一个有方块的阶段、Surface 表面 表面规则覆盖地形 基岩/深板岩层生成、Carvers 雕刻器 雕刻地形 替换方块为空气、Features 特性 结构和特性按固定顺序放置 高度图完成 装饰、Initialize Light 初始化光照 注册光源、Light 光照 计算天空/方块光照传播、Spawn 生成 初始动物生成、Full 完整 原始区块转换为级别区块 应用延迟方块更新）、Randomization 随机化（PRNG：Java标准LCG 仅48位 Xoroshiro128++ 更充分使用种子 相似种子不同结果；Noise：主要是Perlin噪声 梯度填充 平滑插值、simplex噪声、分形叠加）、Biome Generation 生物群系生成（按4×4×4区块的生物群系单元检查/放置/保存、更细操作放大到每个块；Biome sources 生物群系源：Checkerboard 棋盘格、Fixed 固定、The End 末地 5种生物群系、Multi-noise 多噪声 主世界和地狱使用；Multi-noise使用6个密度函数：temperature/humidity_vegetation/continentalness/erosion/weirdness/depth；放置选择最小化b²+Σdistance(mᵢ,nᵢ,vᵢ)²）、Initial Terrain 初始地形（Final Density 最终密度 >0默认方块 否则空气/流体；Aquifers 含水层 处理所有流体 preliminary_surface_level 初步表面层扫描 基础选择器 lava at -54/海平面 默认流体 流体状态计算 最终流体状态/级别；Veins 矿脉 控制 vein_toggle T/vein_ridged R/vein_gap G 铜矿脉Y 0-50 铁矿脉Y -60--8 30%随机移除）、Overworld Initial Terrain 主世界初始地形（含水层+矿脉启用 海平面63 默认方块石头 默认流体水 地形样条线 地形偏移/因子/锯齿 噪声洞穴：cheese/spaghetti/noodle/pillars）、Nether Initial Terrain 地狱初始地形（含水层+矿脉禁用 海平面32 默认方块地狱岩 默认流体岩浆 最大高度128）、End Initial Terrain 末地初始地形（含水层+矿脉禁用 海平面32 默认方块末地石 默认流体空气 侵蚀密度）、Surface Rules 表面规则（替换方块 基岩/深板岩 上下文：biome/surface noise/surface depth/water height/stone depth above/below/min surface level；条件：above/below/at height/gradient/surface/biome/noise/cold_warm/basin/steep slope/underwater/floor/ceiling/max_min surface level/nearest surface height）、Terrain Carving 地形雕刻（雕刻器运行在表面规则后 17×17区块检查 cave carvers/canyon carvers 替换方块为空气）、Structure Generation 结构生成（结构集 随机扩散 spacing/separation 同心环 2.5d环宽 频率过滤 排除区域）、Feature and Structure Placement 特性和结构放置（11个装饰阶段：Raw Generation/Lakes/Local Modifications/Underground Structures/Surface Structures/Strongholds/Underground Ores/Underground Decoration/Fluid Springs/Vegetal Decoration/Top Layer Modification）、Lighting 光照（Initialize Light 注册光源 Light 传播光照）、Initial Entity Spawn 初始实体生成（生成动物 7%/10%概率 生物群系生成 每区块计数）。"
whenToUse: "Use when understanding or customizing how the world is generated (dimensions, biomes, terrain)."

---

# World Generation

World generation (worldgen/levelgen) places biomes, terrain features, structures, and initial mobs step by step. Java Edition data pack customization is covered by "Custom world generation". Java Edition only unless noted.

## Generation Phases

Chunks generate progressively; chunks the player hasn't reached stay at lower phases (proto chunks) until needed, then upgrade to level chunks. Phases:

1. **Empty** — nothing generated.
2. **Structure Starts** — no blocks yet; computes which structures can place here, their ranges, pieces, and start points.
3. **Structure References** — computes referenced pieces so structures aren't lost/truncated; persisted in chunk data.
4. **Biomes** — computes all biome cells; persisted. Still no blocks.
5. **Noise** — density functions fill initial blocks, aquifers place fluids, veins generate. First phase with blocks.
6. **Surface** — surface rules cover the terrain; bedrock and deepslate layers generate here.
7. **Carvers** — carve terrain, replacing blocks with air.
8. **Features** — structures and features place in fixed order; heightmaps complete (decoration).
9. **Initialize Light** — registers light sources.
10. **Light** — computes sky/block light propagation.
11. **Spawn** — initial animal spawns.
12. **Full** — converts the proto chunk to a level chunk; applies deferred block updates.

## Randomization

- **PRNGs**: the Java standard LCG (only 48 bits used) and **Xoroshiro128++** (uses seeds more fully; similar seeds give dissimilar results). Same seed → same world.
- **Noise**: mostly Perlin noise (gradient-filled via PRNG for seed dependence, interpolated for smoothness), plus simplex noise and combinations. All game noise uses fractal stacking, and two similar noises are combined for variety.

## Biome Generation

Biomes are checked/placed/saved per **biome cell** of 4×4×4 blocks. For finer operations (rendering, per-position carving) the biome is "magnified" to each block by picking the nearest cell (distance + position-dependent random).

Biome sources:

- **Checkerboard** — square-ish biomes repeating along diagonals.
- **Fixed** — one biome everywhere.
- **The End** (Java) — five biomes: The End (within ~1024 blocks of (0,0)), Small End Islands, End Barrens, End Midlands, End Highlands placed by erosion density gradient.
- **Multi-noise** — used by the Overworld and the Nether by default.

Multi-noise uses 6 density functions: **temperature**, **humidity/vegetation**, **continentalness** (low = ocean, very low = mushroom fields), **erosion** (low = rugged/mountains, high = flat), **weirdness** (variants, e.g. sunflower plains), and **depth** (which height a biome occupies). All 6 are visible in the debug screen's "NoiseRouter" line.

Placement: for each biome cell, compute the 6 density values; the chosen biome is the one minimizing `b² + Σ distance(mᵢ,nᵢ,vᵢ)²` over all placement intervals `[mᵢ,nᵢ]` (offset `b`; distance = 0 inside, else distance to the nearer bound).

- **Overworld** uses all 6 functions with offsets 0. Levels: temperature −2.22..2.22 in 5 bands; humidity −1.69..1.69 in 5 bands; continentalness −3.66..3.66 in 7 bands (mushroom fields < −1.05, deep ocean, ocean, coast, near inland, inland, far inland > 0.3); erosion −2.42..2.42 in 7 bands. **Ridginess** p = 1 − |3|w| − 2| from weirdness w, in 5 bands (rivers < −0.85, lowlands, low hills, high hills, peaks > 0.7). Placement proceeds: compute depth (rises 0.03125 per 4-block cell downward) → ocean vs land by continentalness → land subdivided by ridginess/erosion/continentalness → beach/badlands/low hills/plateaus/windswept classes refined by temperature/humidity/weirdness. (Caves in depth 0.2–0.9 can overlap and confuse `/locate biome`.) Full tables: see the Minecraft Wiki "World generation" page or `worldgen/` JSON files in the source.
- **Nether** uses only temperature, humidity, and offsets (other four functions fixed 0).

## Initial Terrain

The terrain generator decides air/fluid/vein/default block per position.

### Final Density

A position gets the dimension's default block iff the final density function `n(x,y,z) > 0`; otherwise air or fluid.

### Aquifers

Aquifers handle all fluids (and air) where the final density ≤ 0. First the **preliminary surface level** is computed: scan down from the top until the initial density (without jaggedness, debug "AS") > 0.390625.

Per-position fluid status + fluid surface level:

1. Base selector: below −54 and below sea level → lava at level −54 (hardcoded); else dimension default fluid at sea level.
2. More than 20 blocks above the preliminary surface → use the base selector result.
3. Compare with helper positions' preliminary surface levels (min `s`); under specific conditions borrow a nearby position's fluid status (8+ blocks below sea level cases).
4. Final fluid state: below −54 and below sea level → lava; ≥ −10 → default fluid; in between → lava noise (per 64×40×64 region, |noise| > 0.3 → lava).
5. Final fluid level: eroded (e < −0.225) & deep (d > 0.9) → none; otherwise clamp flood noise f to −1..1, compute thresholds from `s` (mapped 1→0 over 0..64), flood threshold maps to −0.3..0.8, fluid threshold to −0.8..0.4; f > flood threshold → base selector level; f > fluid threshold → level = min(40⌊h/140⌋ + 3⌊hf/10⌋ + 20, s) using spread noise (16×40×16 regions); else none.

Placement (per position): lava directly; else split world into 16×12×16 regions, sample 12 candidate regions (offset +1 Y, −5 XZ), find the 3 nearest sample positions with squared distances; similarity s = 1 − 0.04|d1−d2|; pressure function from fluid levels + barrier noise; combine similarities × pressure with the final density to decide default block vs fluid vs air (block updates scheduled as flagged).

If aquifers are disabled, the fluid status is used directly.

### Veins

Placed after aquifers (skipped where aquifers placed air/fluid). Controlled by **vein toggle** T, **vein ridged** R, and **vein gap** G densities:

1. T > 0 → copper vein, else iron vein (hardcoded).
2. Copper only at Y 0–50; iron at Y −60–−8.
3. Height clamp check: need |T| + min(0.01·min(hmax−h, h−hmin) − 0.2, 0) < 0.4 to place (copper: |T| + (−0.005(|h−20|+|h−30|) + 0.05); iron: |T| + (−0.005(|h+40|+|h+28|) + 0.06)).
4. 30% of vein blocks randomly removed (random > 0.7 → skip).
5. R ≥ 0 → skip; 6. G ≤ −0.3 → vein filler block (granite for copper, tuff for iron); 7. random ≥ min(|T|−0.3, 0.3) → filler; else 2% raw metal block, 98% ore. (≥70% filler, ≤0.6% raw metal blocks.)

### Overworld Initial Terrain

Aquifers and veins enabled; sea level 63; default block stone; default fluid water.

- **Terrain splines** (depend only on continentalness c, erosion e, weirdness w → ridginess pv): terrain offset spline (the depth density's Y=128 slice; controls heights — oceans slightly below sea level, deep oceans lower, mushroom fields raised above water), terrain factor spline (vertical stretching), and jaggedness (height offsets combined with jagged noise; not in the initial density). Low erosion → rugged/high; high erosion → flat/low; high ridginess → peaks; river-level ridginess → valleys slightly below sea level; extreme weirdness can carve ultra-deep pits with lava.
- **Noise caves** — four components: cheese caves (un-abs'd noise → round bubbles), spaghetti caves (abs'd noise near 0 → winding tunnels), noodle caves (same but thin; density fixed 64 in some spots), noise pillars (pillar frequency × thickness noise). Final density: `sloped_cheese` (split at 1.5625: surface vs underground) → surface: `caves/entrances`; underground: min(entrances, cheese, noodle) + max with pillars; density fixed toward −0.078125 above 240 (256) and +0.1171875 below −40 (−64) to cap terrain and protect bedrock; finally min with noodle caves (which ignore the deep clamp, so deep underground favors noodles).

### Nether Initial Terrain

Aquifers and veins disabled; sea level 32; default block netherrack; default fluid lava (all air pockets below 32 fill with lava). Final density is a "smeared" noise; fixed toward 0.9375 at Y 104–128 and 2.5 at Y −8–24 to cap the bedrock layers; terrain max height 128.

### End Initial Terrain

Aquifers/veins disabled; sea level 32; default block end stone; default fluid air. Smeared noise + End erosion density (erodes terrain so the main island is separate from outer islands); fixed toward −23.4375 at Y 56–312 and −0.234375 at Y 4–32 — the lowest initial block is Y 4 and high terrain is rare.

## Surface Rules

After initial terrain, surface rules replace blocks per biome (grass, sand, etc.) and also place bedrock/deepslate. The surface rule context contains: biome, surface noise, **surface depth** (⌊2.75s + 0.25r + 3⌋), surface secondary noise, **water height** (1 above nearest fluid surface; differs when invoked by carvers), **stone depth above** (non-fluid blocks to nearest air above), **stone depth below**, and **min surface level** (interpolated neighbor-chunk terrain min + surface depth − 8; at/above = surface).

Scanning: per horizontal position at the `WORLD_SURFACE_WG` heightmap; the **eroded badlands rule** (hardcoded, un-disableable, badlands only) places terrain pillars when `badlandsSurfaceNoise` and `badlandsPillarNoise` are both > 0, height from `badlandsPillarRoofNoise` (skips water); then surface rules apply top-down; the **frozen ocean rule** (hardcoded, frozen ocean/deep frozen ocean only) builds icebergs (snow cap, packed ice body, water inside) when `icebergSurfaceNoise` and `icebergPillarNoise` > 1.8, height from `icebergPillarRoofNoise`, melting by biome temperature.

Surface rule conditions (first match wins; no match keeps the initial block): above/below/at height y; height gradient b→t (probability ramps); surface; biome; noise n (Y=0 slice); cold/warm (biome snow temperature); basin (surface depth < 0); steep slope (≥4 block height difference east–west or north–south on WORLD_SURFACE_WG); underwater n blocks / not underwater (carver-context differs); floor / ceiling (with n-block depth variants); max/min surface level (± surface depth); nearest surface height (nearest air above − 1). Some conditions are affected by surface secondary noise (marked `*` on the wiki). The Overworld's rule table is on the wiki tutorial page; the Nether's likewise; the End has a single rule: everything → end stone.

## Terrain Carving

Carvers run after surface rules. The game checks 17×17 chunks around the current chunk; chunks marked as a carver's start chunk (random, configurable probability) carve the current chunk. Carvers: **cave carvers** (up to 15 loop iterations, 25% chance of a ring chamber per iteration; 1–4 tunnels otherwise, tunnels may fork if wide enough) and **canyon carvers** (giant fissure of ellipsoid carvings with platforms at some heights). Carving per position: skip if already carved (caving mask) or not replaceable; compute carved state — below carver lava level → lava; else aquifer function at final density 0 decides lava/water/air (no carve if it returns default block); if the pre-carve block was grass/mycelium with dirt below, re-run surface rules on the dirt (carver context: stone depths 1, water height = position height — the reason water checks differ from surface phase).

- **Overworld**: cave carver (start 15%, Y −56..180), cave carver (start 7%, Y −56..47), canyon carver (start 1%, Y 10..67); all replace `#overworld_carver_replaceables`.
- **Nether**: one cave carver (start 20%, Y 0..126), replaces `#nether_carver_replaceables`.

## Structure Generation

Structure placement works per **structure set** (a group of structures). Two placement types:

- **Random spread** — `spacing` (grid cell size; at most one start per cell) and `separation` (exclusion ring east/south). E.g. spacing 27, separation 4: cells where x%27 or z%27 ≥ 23 can never host a start.
- **Concentric rings** — ring width 2.5d chunks, gaps 3.5d, first ring 2.75d from origin (d = distance multiplier); per-ring count caps c1 = s (spread), cₙ = cₙ₋₁ + ⌊2cₙ₋₁/n⌋; starts placed evenly by random start angle (random distance within the ring); preferred-biome sets try to shift placement.

Then frequency filters starts (spacing out dense ones) and exclusion zones keep structures away from specified structures. A chunk at the Structure Starts phase checks all structure sets: if it's a start chunk, pick a structure from the set, find a placeable position (biome + height requirements); if none, try the next structure; if at least one fits, create the structure start, compute all pieces, and derive the bounding box. At Structure References, each chunk collects all structures in 17×17 chunks around it and stores references for intersecting bounding boxes (avoids duplicating data). Consequence: a structure's horizontal span cannot exceed 17 chunks — starts and farthest pieces beyond 8 chunks get truncated.

Overworld structure sets and their distributions (random spread vs concentric rings), Nether sets (all random spread), and End sets (all random spread): see the Minecraft Wiki "World generation" page for full tables.

## Feature and Structure Placement

Decoration has 11 stages (structure pieces always place before features within the same stage; order otherwise by definition):

1. **Raw Generation** — raw terrain features (only End floating islands).
2. **Lakes** — lava lakes only (water lakes were replaced by aquifers).
3. **Local Modifications** — icebergs, mossy boulders, large dripstone, basalt pillars, amethyst geodes.
4. **Underground Structures** — fossils, dungeons.
5. **Surface Structures** — desert wells, deltas, end gateways, blue ice, ice spikes.
6. **Strongholds** — does nothing (strongholds are not placed here).
7. **Underground Ores** — ores and disks.
8. **Underground Decoration** — non-ore clusters (incl. Nether ore clusters), sculk patches.
9. **Fluid Springs** — springs.
10. **Vegetal Decoration** — vegetation: trees, bamboo, random patches.
11. **Top Layer Modification** — frozen top layer only.

Structure pieces are placed strictly within the current chunk (parts outside are truncated and placed by other chunks); pieces keep their data for later placement. Features may modify the 3×3 chunk area around the generating chunk — this makes feature placement **order-dependent**: two chunks generating in different orders can produce different results with the same seed (and concurrent generation may interleave blocks). Player paths influence which order wins.

## Lighting

After decoration: **Initialize Light** registers light sources without propagation (prevents truncated edge lighting), then **Light** propagates sky and block light (max level 15; neighboring chunks at least reached Initialize, so correctness is guaranteed).

## Initial Entity Spawn

Java Edition. After lighting, the chunk spawns an initial animal (category "animal"): chance 7% in snowy plains/ice spikes, 10% elsewhere; a random animal from the biome's spawns; per-chunk count computed; up to 4 wandering attempts (each attempt re-snaps to the highest block position, staying inside the chunk); basic spawn rules apply (no collision). Mob caps are ignored. Some entities (e.g. structure-attached) are placed with structure pieces instead.

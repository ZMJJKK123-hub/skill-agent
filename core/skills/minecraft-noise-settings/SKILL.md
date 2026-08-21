---

name: minecraft-noise-settings
description: "Minecraft Noise Settings 噪声设置定义：NOISE_SETTINGS 注册表、data/<namespace>/worldgen/noise_settings/ 数据包路径、tags/noise_settings/ 标签、JSON 格式（sea_level 海平面 int、aquifers_enabled 含水层生成 bool、ore_veins_enabled 矿脉生成 bool、disable_mob_generation 禁用初始动物生成 bool、legacy_random_source 使用pre-1.18随机源 bool、default_block 默认方块状态、default_fluid 默认流体状态、spawn_target 玩家生成条件 生物群系参数范围 采样2560方块内点 计算距离指数）、Noise 世界噪声参数（min_y 最低地形高度 -2032..2031、height 总地形高度、size_horizontal 水平单元格大小 1-4、size_vertical 垂直单元格大小 1-4、noise_router 噪声路由器 绑定密度函数到世界生成：preliminary_surface_level 初步表面高度、final_density 最终密度 >0默认方块 <0空气、barrier 含水层屏障方块概率、fluid_level_floodedness 流体洪水概率 0-1、fluid_level_spread 流体扩散、lava 岩浆放置条件 Y=-58到海平面 |value|>0.3、vein_toggle 矿脉类型切换、vein_ridged 矿脉块、vein_gap 矿脉放置控制、temperature/vegetation/continents/erosion/depth/ridges/initial_density/final_density 标准噪声路由函数）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载）、Terrain Generation 地形生成（final_density >0默认方块 <0空气、默认方块被矿脉和表面规则替换、Y=-58以下海平面上方空气被含水层替换、Y=-58以下空气总是岩浆）、Built-in Noise Settings 内置噪声设置（minecraft:overworld/amplified/large_biomes/nether/caves/end/floating_islands）。"
whenToUse: "Use when writing datapack worldgen noise_settings definitions or custom terrain generation."

---

# Noise Settings

This content applies only to Java Edition.

Noise settings (noise generator settings) define the base terrain and surface rules of noise-generator worlds. Definition files are their data-driven definitions in datapacks.

## Definition format

Noise settings use the `NOISE_SETTINGS` registry; the datapack path is `worldgen/noise_settings` (definitions in `data/<namespace>/worldgen/noise_settings`, tags in `data/<namespace>/tags/worldgen/noise_settings`).

Definition files use JSON with the following structure:

- JSON file root object
  - `sea_level` (int, required): the dimension's sea level.
  - `aquifers_enabled` (bool, required): whether aquifers generate.
  - `ore_veins_enabled` (bool, required): whether ore veins generate.
  - `disable_mob_generation` (bool, required): whether initial animal spawning is disabled.
  - `legacy_random_source` (bool, required): use the pre-1.18 random source.
  - `default_block` (string/compound, required): the dimension's default block (block state).
  - `default_fluid` (string/compound, required): the dimension's default fluid (block state).
  - `spawn_target` (list, may be empty): biome parameter ranges for player spawn conditions. The game samples points within 2560 blocks of (0,0), computes `(x2+z2)/2390625 + Σdi²` (di = parameter distance to the range), and spawns near the best position.
  - `noise` (compound, required): world noise parameters.
    - `min_y` (int, required): (−2032≤v≤2031, multiple of 16) lowest terrain height.
    - `height` (int, required): (0≤v≤2032−min_y, multiple of 16) total terrain height.
    - `size_horizontal` (int, required): (1≤v≤4) horizontal cell size.
    - `size_vertical` (int, required): (1≤v≤4) vertical cell size.
    - `noise_router` (compound, required): binds density functions to world generation. Each function may be a namespace ID, constant, or inline density function:
      - `preliminary_surface_level`: 2D density function for preliminary surface height; affects aquifers and surface rules.
      - `final_density`: final density; >0 → default block (replaced by surface rules), <0 → air (replaced by aquifers).
      - `barrier`: chance that aquifers place barrier blocks between fluid and air.
      - `fluid_level_floodedness`: probability of aquifers placing fluid (clamped 0–1).
      - `fluid_level_spread`: affects aquifer fluid height; lower = fewer aquifers.
      - `lava`: aquifers place lava instead of the default fluid between Y=−58 and sea level when |value|>0.3.
      - `vein_toggle`: >0 → copper veins, else iron veins.
      - `vein_ridged`: <0 → no vein blocks.
      - `vein_gap`: controls actual vein placement (ore blocks vs. stone).
      - `temperature` / `vegetation` / `continents` / `erosion` / `depth` / `ridges` / `initial_density` / `final_density`: the standard noise router functions (see the density function article).

## Definition behavior

Noise settings data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

During terrain generation, the game first decides per coordinate whether `final_density` > 0 (default block) or < 0 (air). Default blocks are replaced by ore veins and surface rules; air above Y=−58 below sea level or the surface is replaced by aquifers; air below Y=−58 is always lava.

## Built-in noise settings

- `minecraft:overworld`, `minecraft:amplified`, `minecraft:large_biomes`, `minecraft:nether`, `minecraft:caves`, `minecraft:end`, `minecraft:floating_islands`.

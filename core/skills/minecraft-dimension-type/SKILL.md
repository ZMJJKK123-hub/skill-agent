---

name: minecraft-dimension-type
description: "Minecraft Dimension Type 维度类型定义：DIMENSION_TYPE 注册表、data/<namespace>/dimension_type/ 数据包路径、tags/dimension_type/ 标签、JSON 格式（has_fixed_time 固定时间、has_skylight 天空光、has_ceiling 天花板、has_ender_dragon_fight 末影龙战斗、ambient_light 环境光、coordinate_scale 坐标缩放、infiniburn 无限燃烧方块、min_y 最低建造高度、height 总建造高度、logical_height 逻辑高度、monster_spawn_block_light_limit 怪物生成方块光照限制、monster_spawn_light_level 怪物生成光照等级 int provider、attributes 维度环境属性映射、timelines 时间线、skybox 天空盒 none/end/overworld、cardinal_light 方向光照 default/nether、default_clock 世界时钟）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载、内联维度类型支持但无法加载）、Dimension Behaviors 维度行为（has_fixed_time 禁用昼夜逻辑/沉溺者敌对/商队停止/巡逻生成/末影人/狐狸/僵尸围城/亡灵避光、has_skylight 控制天空光/幻翼生成/天气、has_ceiling 控制动物生成/玩家生成偏好看重力映射/天气缺失）、Hardcoded Behaviors 硬编码行为（玩家总是生成在主世界、下界传送门维度缩放、末地传送门、霜冰融化、末地无天气、下界地图玩家图标随机旋转）、Built-in Dimension Types 内置维度类型（overworld/the_nether/the_end/overworld_caves）。"
whenToUse: "Use when writing datapack dimension_type definitions or custom dimension behaviors."

---

# Dimension Types

This content applies only to Java Edition.

Dimension types control a dimension's environmental lighting, build height, and many other behaviors. Definition files are their data-driven definitions in datapacks.

## Definition format

Dimension types use the `DIMENSION_TYPE` registry; the datapack path is `dimension_type` (definitions in `data/<namespace>/dimension_type`, tags in `data/<namespace>/tags/dimension_type`).

Definition files use JSON with the following structure:

- JSON file root object
  - `has_fixed_time` (bool, default `false`): whether the dimension logically has day/night (see below).
  - `has_skylight` (bool, required): whether the dimension has skylight (see below).
  - `has_ceiling` (bool, required): whether the dimension has a ceiling (see below).
  - `has_ender_dragon_fight` (bool, required): whether the ender dragon fight can start.
  - `ambient_light` (float, required): ambient light (0–1 under vanilla shaders).
  - `coordinate_scale` (double, required): (0.00001≤v≤30000000.0) coordinate scaling, affects nether portal travel and `/execute in`.
  - `infiniburn` (string/list, required): blocks on which fire burns indefinitely (block ID, tag, or list).
  - `min_y` (int, required): (−2032≤v≤2031, multiple of 16) lowest buildable height.
  - `height` (int, required): (16≤v≤2032−min_y, multiple of 16) total buildable height.
  - `logical_height` (int, required): (0≤v≤height) max height for chorus fruit teleportation and generated nether portals.
  - `monster_spawn_block_light_limit` (int, required): (0≤v≤15) max block light for monster spawns.
  - `monster_spawn_light_level` (int/compound, required): (0≤v≤15) max light for monster spawns using internal sky light (sky −10 during thunderstorms); a range is sampled per spawn attempt (int provider).
  - `attributes` (compound): dimension environment attribute map; duplicate attributes use the last value.
  - `timelines` (string/list): active timelines (ID, tag, or list); duplicate timeline-defined attribute changes use the last.
  - `skybox` (string, default `overworld`): `none` / `end` (periodic end flashes using world clock time) / `overworld` (sun, moon, stars, day/night).
  - `cardinal_light` (string, default `default`): block lighting type `default` or `nether` (shade=false blocks get 10% less brightness on top/bottom instead of 0/50%; fluids and shade=true blocks get 10% less on all faces).
  - `default_clock` (string): (namespace ID) world clock used in this dimension; absent = no world clock.

## Definition behavior

Dimension type data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Inline dimension types in datapacks and `level.dat` are supported but dimensions using them cannot be loaded.

### Dimension behaviors

`has_fixed_time` does not control visual day/night; it disables day/night logic for some behaviors: sleeping at any game time, Drowned always hostile, wandering traders stop drinking invisibility potions/milk, patrols always spawn, endermen never increase random teleport chance, foxes never head to villages or sleep, zombie sieges always spawn, some undead stop avoiding sunlight.

`has_skylight` controls: skylight existence (daylight sensors), phantom spawning, and weather.

`has_ceiling` controls: initial animal spawn search, player spawn preference (Y=64 instead of highest block, except superflat), some map updates, and weather absence.

### Hardcoded behaviors

Players always spawn in the Overworld. Nether portals teleport with dimension scaling to/from the Nether; end portals to/from the End. Frosted ice melts by block light (not skylight) in the End. The End never has weather. Nether map player icons rotate randomly.

## Built-in dimension types

- `overworld`, `the_nether`, `the_end`, `overworld_caves` (unused directly; for legacy cave worlds).

---

name: minecraft-structure-template
description: "Minecraft Structure Template 结构模板格式：Storage Locations 存储位置（游戏数据 data/minecraft/structure/ client.jar内、玩家导出 生成目录 generated/<namespace>/structure/<name>.nbt、数据包 data/<namespace>/structure/、放置时查找顺序 保存根目录→数据包→内置、文件GZip压缩NBT）、NBT Format NBT格式（根标签 DataVersion 数据版本、blocks 方块列表 pos相对坐标 nbt方块实体数据 state调色板索引、entities 实体列表 blockPos块坐标 pos精确双精度坐标 nbt实体数据 UUID忽略/Pos覆写/Passengers无效、palette/palettes 调色板映射索引到方块状态 palettes随机选择一个、size 维度 [x,y,z]）、SNBT Format SNBT格式（数据生成器可转换为特殊SNBT形式 块相关标签不遵循正常NBT↔SNBT规则、data blocks pos+state+可选nbt、palette 调色板字符串、palettes 键列表）、Vanilla Structures 原版结构（abandoned_camp/ancient_city/bastion/empty.nbt/end_city/fossil/igloo/nether_fossils/pillager_outpost/ruined_portal/shipwreck/trail_ruins/trial_chambers/underwater_ruin/village/woodland_mansion）、Placement Behavior 放置行为（结构保存/加载通过结构方块和测试实例方块、部分结构作为片段放置后处理 结构方块和拼图方块替换、部分放置被阻止以保留现有方块：冰屋/下界化石/海洋废墟/废弃传送门/沉船修改模板内容、数据模式结构方块 metadata 匹配后处理：末地城市/冰屋/海洋废墟/沉船/林地宅邸 特殊战利品箱/实体生成、拼图方块替换为final_state、单池元素/旧单池元素扩展拼图到池结构、处理器列表后处理块）。"
whenToUse: "Use when authoring structure NBT files, debugging structure placement, or reading vanilla structure data."

---

# Structure Template

Structure storage files (structure templates) store block structures. They back world generation and can be saved by players. Java Edition only.

## Storage Locations

- Game data: `/data/minecraft/structure/` inside client.jar.
- Player-exported: `<save root>/generated/<namespace>/structure/<name>.nbt`.
- Data packs: `data/<namespace>/structure/`.

Lookup order when placing: save root → data pack → built-in. Files are GZip-compressed NBT.

## NBT Format

Root tag:

- `DataVersion` (required) — the data version the file was saved with; if absent, assumed 500 (between 1.9.4 and 1.10).
- `blocks` (required) — blocks in the structure:
  - `pos` (required) — `[x, y, z]` relative to the structure origin (minimum corner).
  - `nbt` — block entity data (see the block-entity-data-format skill; excludes `x`/`y`/`z`).
  - `state` (required) — index into the palette selecting the block state.
- `entities` (required) — entities in the structure, placed with structure generation rules:
  - `blockPos` (required) — block coordinates relative to the origin; used only to check the entity is inside the structure bounds (entities outside cannot be placed).
  - `pos` (required) — exact double coordinates relative to the origin.
  - `nbt` (required) — entity data (see entity data format; `UUID` ignored, `Pos` overwritten, `Passengers` invalid).
- `palette` (one of `palette`/`palettes` required) — palette mapping indices to block states (see the block-state-data skill for the state format).
- `palettes` — list of palettes; the game picks one randomly when placing. Mutually exclusive with `palette`; `palettes` takes priority.
- `size` (required) — `[x, y, z]` dimensions.

## SNBT Format

The data generator can convert NBT structure templates to a special SNBT form (block-related tags don't follow normal NBT↔SNBT rules; `DataVersion`, `entities`, `size` convert normally). SNBT structure templates currently serve no gameplay purpose — the in-game export methods are all disabled.

- `data` (required) — the blocks, each with `pos`, `state` as `<block id>{<property>:<value>,...}`, optional `nbt` (block entity data).
- `palette` — palette strings in `<block id>{<property>:<value>,...}` form.
- `palettes` — a list where each entry's keys are the actual `<block id>{...}` used by the entries of `data` under that palette.

## Vanilla Structures

All built-in structures live under `/data/minecraft/structure/` in client.jar (also mirrored under `data/minecraft/structure/` in mc_java_sources). Complete file listings per structure: see those directories or the Minecraft Wiki page "Structure file".

- `abandoned_camp` — campsite pieces (barrel/chest/special variants) per biome: bamboo_jungle, birch_forest, cherry_grove, dappled_forest, default, flower_forest, old_growth_taiga, snowy_taiga, sparse_jungle, taiga, etc. (`campsite_<biome>_<n>.nbt`, `campsite_default_<type>_<n>.nbt`).
- `ancient_city` — city entrance paths, city center (walls, chambers, barracks, camps, statues, ruins...), and outer walls.
- `bastion` — `blocks/` (air.nbt, gold.nbt), `bridge/`, `hoglin_stable/`, `housing/`, `treasure/`, `units/` — the five bastion piece groups plus connectors, legs, ramparts, starting pieces, and stairs.
- `empty.nbt` — an empty template used as a default/no-op.
- `end_city` — End city floors, roofs, towers, bridges, and the ship (`ship.nbt`).
- `fossil` — Overworld fossils: skull_1..4 and spine_1..4, each with a `_coal` variant.
- `igloo` — `bottom.nbt`, `middle.nbt`, `top.nbt`.
- `nether_fossils` — Nether fossil pieces `fossil_1..14.nbt`.
- `pillager_outpost` — watchtower, cages, tent, logs, targets, base plate, overgrown variant.
- `ruined_portal` — `portal_1..10.nbt` plus three `giant_portal` variants.
- `shipwreck` — rightsideup/sideways/upsidedown × full/fronthalf/backhalf × normal/degraded, plus `with_mast`.
- `trail_ruins` — buildings (group_full/hall/lower/room/upper, large_room, one_room), decor, roads, and tower pieces.
- `trial_chambers` — chamber pieces (addon, assembly, eruption, pedestal, slanted, spiral, staircases, dispensers, rewards, corridors, intersections, spawners...).
- `underwater_ruin` — big/brick/cracked/mossy/warm ruin pieces `*_1..8.nbt`.
- `village` — `common/` (animals: cat variants, cows, horses, pigs, sheep; well_bottom; grass patches) and per-biome `houses/`: desert, plains, savanna, snowy, taiga (houses, farms, temples, toolsmiths, shepherds...).
- `woodland_mansion` — 1x1/1x2/2x2 room pieces (`1x1_a1..5`, `1x2_*`, `2x2_*`), corridors, carpets, stairs, entrances, etc.

## Placement Behavior

Structures are saved/loaded via structure blocks and test instance blocks. Some structures are placed as pieces and post-processed (structure blocks and jigsaw blocks are replaced; some placements are blocked to preserve existing blocks):

- Igloo, Nether fossils, underwater ruins, ruined portals, and shipwrecks modify template contents (positions, blocks) when placed.
- Structures with data-mode structure blocks whose `metadata` matches are post-processed:
  - **End city** — `Chest<...>` → chest below with loot `chests/end_city_treasure`; `Elytra<...>` → item frame with elytra; `Sentry<...>` → Shulker.
  - **Igloo** — `chest` → chest below with loot `chests/igloo_chest`.
  - **Underwater ruins** — `chest` → waterlogged chest with `chests/underwater_ruin_big` (big) or `chests/underwater_ruin_small` (small); `drowned` → a Drowned (above sea level replaced with air, else water).
  - **Shipwreck** — `map_chest` → `chests/shipwreck_map`; `supply_chest` → `chests/shipwreck_supply`; `treasure_chest` → `chests/shipwreck_treasure`.
  - **Woodland mansion** — `Chest<...>` → north-facing chest with `chests/woodland_mansion`; `ChestEast/North/South/West` → chest facing that direction, re-rotated by the piece; `Group of Allays` → 1–3 Allays; `Mage` → Evoker; `Warrior` → Vindicator.
- For End city, igloo, Nether fossils, underwater ruins, ruined portals, shipwrecks, and woodland mansions, jigsaw blocks are replaced with their `final_state`.
- All structure-placed structures prevent structure blocks from being placed.
- Templates used via `legacy_single_pool_element` prevent air placement.
- Templates used via `single_pool_element` or `legacy_single_pool_element` expand jigsaws into their pool structures.
- A processor list (`processors`) can post-process blocks inside the template (see the processor-list skill).

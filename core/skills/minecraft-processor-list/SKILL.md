---

name: minecraft-processor-list
description: "Minecraft Processor List 处理器列表格式：Definition Format 定义格式（PROCESSOR_LIST 注册表、data/<namespace>/worldgen/processor_list/ 数据包路径、tags/worldgen/processor_list/ 标签、根数组处理器列表或对象 processors 列表、每个处理器 processor_type+字段）、Processor Types 处理器类型（blackstone_replace 替换石头类型为黑石变体 铁栏杆替换为锁链、block_age 老化方块 mossiness 0-1、block_ignore 忽略方块 blocks 列表 不检查状态 移除方块 保留预存方块、block_rot 随机移除方块 integrity 0-1 移除概率 rottable_blocks 可腐烂方块、capped 限制处理方块数量 delegate 递归处理器 limit 数量提供器、gravity 重力按地形垂直移动方块 heightmap 高度图 offset 偏移、jigsaw_replacement 替换拼图方块 移除结构虚空 世界生成自动应用无需声明、lava_submerged_block 结构方块替换岩浆时 碰撞箱不完整方块不替换岩浆、nop 无操作、protected_blocks 受保护方块 value 不能被结构覆盖、rule 自定义规则 position_predicate 位置谓词 always_true/linear_pos/axis_aligned_linear_pos、input_predicate 输入谓词 规则测试已放置方块、location_predicate 位置谓词 规则测试生成前位置方块、output_state 输出状态 要放置的方块、block_entity_modifier 方块实体修改器 passthrough/clear/append_static/append_loot）、Behavior 行为（处理器按列表顺序运行每个模板方块、也称为方块处理器/结构后处理器、模板池拼图元素 处理器在地形适应前运行 实际放置位置可能与处理位置不同、服务器启动加载一次）。"
whenToUse: "Use when authoring structure processor lists in data/worldgen/processor_list/."

---

# Processor List

Processor lists replace blocks placed from structure templates during world generation per rules. Java Edition only.

## Definition Format

Registry `PROCESSOR_LIST`, data pack path `worldgen/processor_list` (files in `data/<namespace>/worldgen/processor_list/`; tags in `tags/worldgen/processor_list/`). A file is either a root array of processors or an object with a `processors` list. Each processor:

```json
{ "processor_type": "<namespace id>", ... }
```

## Processor Types

- `blackstone_replace` — replaces stone-type blocks with blackstone variants and iron bars with chains.
- `block_age` — ages blocks: `mossiness` (0–1 clamped).
- `block_ignore` — `blocks` (list of block states; states not checked): removes those blocks; their positions keep the pre-existing blocks (not overwritten).
- `block_rot` — randomly removes blocks: `integrity` (0–1; removal chance), `rottable_blocks` (ID/array/tag; absent = all blocks).
- `capped` — caps the number of processed blocks: `delegate` (recursive processor), `limit` (int provider; if the structure has fewer blocks, all are processed, else a random subset).
- `gravity` — shifts the structure vertically per terrain: `heightmap` (default `WORLD_SURFACE_WG`; one of the six standard heightmaps), `offset` (default 0).
- `jigsaw_replacement` — replaces jigsaw blocks and removes structure void; auto-applied for worldgen jigsaw structures (no need to declare).
- `lava_submerged_block` — when a structure block replaces lava, blocks with incomplete collision boxes don't replace the lava.
- `nop` — does nothing.
- `protected_blocks` — `value` (ID/list/tag): these blocks can't be overwritten by the structure.
- `rule` — custom rules, applied in list order:
  - `position_predicate` (default always true) — test on the distance from the structure start: `predicate_type` = `always_true`, `linear_pos` (3D Manhattan distance; `min_chance`/`max_chance` with linear interpolation between `min_dist`/`max_dist`; probabilities clamped 0–1), or `axis_aligned_linear_pos` (same but on one `axis` = x/y/z, default y, distances positive).
  - `input_predicate` (required) — rule test applied to the placed block (see the rule-test skill).
  - `location_predicate` (required) — rule test applied to the block at the position before generation.
  - `output_state` (required) — the block to place.
  - `block_entity_modifier` (optional) — modifies the block entity on placement: `passthrough` (default, keep fields), `clear` (remove fields), `append_static` (`data` NBT added), `append_loot` (`loot_table` added, with a seed based on the block position).

## Behavior

Processors run in list order per template block; they're also called block processors / structure post-processors. For template pool jigsaw elements, processors run BEFORE terrain adaptation — the actual placement position may differ from the processed position. Definitions load once at server startup (restart required).

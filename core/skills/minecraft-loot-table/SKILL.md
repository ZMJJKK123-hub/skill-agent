---

name: minecraft-loot-table
description: "Minecraft Loot Table 战利品表格式：Vanilla Uses 原版用途（容器内容、可疑方块、方块掉落、实体死亡掉落、钓鱼、猪灵以物易物、不控制经验/无掉落实体）、Built-in Tables 内置表（archaeology/考古、blocks/方块破坏、brush/刷、carve/雕刻、charged_creeper/苦力怕击杀、chests/结构容器、dispensers/发射器、entities/生物死亡、equipment/装备、gameplay/游戏玩法、pots/装饰罐、harvest/收获、shearing/剪切、spawners/生成器胜利奖励）、Custom Invocation 自定义调用（容器 LootTable+LootTableSeed NBT、Trial spawner normal_config/ominous_config、Vault config.loot_table、Mobs DeathLootTable+DeathLootTableSeed、Spawner spawn_data.equipment.loot_table、Advancement rewards、/loot 命令）、Definition Format 定义格式（LOOT_TABLE 注册表、data/<namespace>/loot_table/、JSON type/random_sequence/functions/pools）、Pools 池（rolls 基础抽取数 number provider、bonus_rolls 幸运额外抽取 玩家幸运+附魔等级×值、conditions 谓词、functions 修改器、entries 条目 独立抽取有放回）、Entries 条目（Common fields 通用字段 functions/weight/quality/conditions；Singleton 单项：item 单物品栈、loot_table 从另一表抽取、dynamic 动态（decorated pot shulker box）、empty 无生成、slots 槽源生成、tag 物品标签 expand false单例/true展开；Composite 复合条目：alternatives 选择第一个条件通过的、group 包含所有条件通过的、sequence 从头遍历直到失败）、Item Modifiers and Predicates 修改器和谓词、Loot Context 战利品上下文（生成时创建 持有当前参数）。"
whenToUse: "Use when authoring loot table JSON files for data packs."

---

# Loot Table

Loot tables decide which items generate in which situations. Java Edition only (Bedrock: official docs).

## Vanilla Uses

Vanilla uses loot tables for: naturally generated container contents, suspicious block contents, block drop loot, entity death drops, fishing, and piglin bartering. They do not control XP drops or entities that drop nothing (e.g. slime splits, silverfish from infested blocks).

Built-in tables live under `data/minecraft/loot_table/` in client.jar, grouped by purpose:

- `archaeology/` — brushing from suspicious blocks (desert_pyramid, desert_well, ocean_ruin_cold/warm, trail_ruins_common/rare).
- `blocks/` — block break drops (one table per block ID).
- `brush/` — brush results (armadillo).
- `carve/` — carved results (pumpkin).
- `charged_creeper/` — charged Creeper kills (creeper, piglin, root, skeleton, wither_skeleton, zombie; the `root` table drops extra items once per kill — only one victim per kill rolls it).
- `chests/` — structure containers (abandoned_mineshaft, ancient_city(_ice_box), bastion_bridge/hoglin_stable/other/treasure, buried_treasure, desert_pyramid, end_city_treasure, igloo_chest, jungle_temple(_dispenser), nether_bridge, pillager_outpost, ruined_portal, shipwreck_map/supply/treasure, simple_dungeon, spawn_bonus_chest, stronghold_corridor/crossing/library, trial_chambers/* (corridor, entrance, intersection, reward & variants), underwater_ruin_big/small, village & villager profession houses).
- `dispensers/` — trial chambers dispensers.
- `entities/` — mob death drops (per entity ID; sheep has per-color wool tables).
- `equipment/` — trial chamber mob equipment (trial_chamber_melee/ranged).
- `gameplay/` — armadillo_shed, cat_morning_gift, chicken_lay, fishing (fish/junk/treasure + main table), hero_of_the_village gifts, panda_sneeze, piglin_bartering, sniffer_digging, turtle_grow.
- `pots/` — trial chamber decorated pots.
- `harvest/` — block harvesting (beehive, cave_vine, sweet_berry_bush).
- `shearing/` — shearing interactions (bogged, mooshroom, sheep, snow_golem).
- `spawners/` — trial spawner victory rewards (consumables, key, items_to_drop_when_ominous).

Notes: unbreakable blocks (bedrock, end portal) have no loot tables; wall/floor variants share tables (e.g. white banner and white wall banner); the Wither's nether star drop is not loot-table-controlled.

## Custom Invocation

- Containers (chests, minecarts with chest/hopper, decorated pots, suspicious blocks): NBT `LootTable` (namespace ID; a double chest only rolls for the half carrying the tag) + `LootTableSeed` (0/absent = world random sequence). Tags are removed once the container is interacted with, and only then does loot appear.
- Trial spawner: `normal_config`/`ominous_config` with `items_to_drop_when_ominous` and `loot_tables_to_eject` (weighted list of `{data, weight}`).
- Vault: `config.loot_table` (default `chests/trial_chambers/reward`) and `override_loot_table_to_display`.
- Mobs: `DeathLootTable` + `DeathLootTableSeed`.
- Spawner spawn equipment: `spawn_data.equipment.loot_table`.
- Advancement rewards can grant loot tables; `/loot` invokes tables directly (existing or inline SNBT).

## Definition Format

Registry `LOOT_TABLE`, data pack path `loot_table` (files in `data/<namespace>/loot_table/`).

```json
{
  "type": "generic",
  "random_sequence": "minecraft:...",
  "functions": [ ... ],
  "pools": [ ... ]
}
```

- `type` (default `generic`) — used to validate the loot context parameter set (warns on missing required parameters).
- `random_sequence` — the random sequence used; sharing a sequence between tables makes their results interdependent.
- `functions` — item modifiers applied to every stack (in order).
- `pools` — loot pools drawn in order.

### Pools

- `rolls` (required) — base draw count (number provider).
- `bonus_rolls` (default 0) — extra draws from luck: (player luck attribute + `fishing_luck_bonus` enchantment level) × value, floored. Luck only applies for opening loot containers, unlocking vaults, fishing, killing mobs, and brushing suspicious blocks.
- `conditions` — loot predicates; all must pass for the pool to be used.
- `functions` — item modifiers applied to every stack this pool produces.
- `entries` (required) — the pool entries; draws are independent (with replacement).

### Entries

Common fields (singleton): `functions` (modifiers), `weight` (default 1), `quality` (default 0; adjusted weight = max(⌊weight + quality·luck⌋, 0) when luck applies), `conditions` (entries failing conditions are removed before drawing).

- `item` — a single item stack (default count 1): `name` (item ID).
- `loot_table` — draws from another table: `value` (table ID or inline; cycles not allowed).
- `dynamic` — depends on the broken block: `name` = `sherds` (decorated pot: drops its 4 sherds) or `contents` (shulker box: contents drop into the world).
- `empty` — generates nothing.
- `slots` — generates stacks from item slots: `slot_source` (see the slot-source skill).
- `tag` — item tag entry: `name` (item tag), `expand` — false: a singleton that generates one stack per item in the tag (default count 1); true: expands into equally-weighted `item`-like entries (no item modifiers allowed).

Composite entries (expand into entries, no direct weight): `children` + `conditions`:

- `alternatives` — picks the first child whose conditions pass.
- `group` — includes all children whose conditions pass.
- `sequence` — walks children from the start until one fails its conditions.

After expansion, only singleton entries remain (condition-failing ones removed), and one is drawn by weight.

## Item Modifiers and Predicates

Loot tables use item modifiers and loot predicates; see the item-modifier and predicate skills for the full lists.

## Loot Context

Generating loot creates a loot context holding current parameters, used by predicates/modifiers. The `type` field in the file is only for validation, not for actual generation.

External tool: [Loot Table Generator](https://misode.github.io) on misode.github.io.

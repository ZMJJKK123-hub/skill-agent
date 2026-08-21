---

name: minecraft-entity-predicate
description: "Minecraft Entity Predicate 实体谓词：Format 格式（实体子谓词映射→测试内容）、Sub-predicates 子谓词（entity_type 实体类型ID/列表/标签、location 位置谓词、stepping_on 脚下位置谓词、movement_affected_by 影响移动速度位置谓词、distance 距离谓词 双重边界、movement 运动检查 fall_distance/horizontal_speed/speed/vertical_speed/x/y/z、effects 状态效果谓词、nbt NBT匹配、flags 布尔标志 is_baby/is_flying/is_on_ground/is_on_fire/is_sneaking/is_sprinting/is_swimming/is_in_water/is_fall_flying、equipment 装备槽物品栈谓词 body/chest/feet/head/legs/mainhand/offhand、periodic_tick 周期性刻检查、vehicle 骑乘实体谓词、passenger 乘坐实体谓词、targeted_entity 攻击目标谓词、team 队伍名称、slots 物品槽范围谓词、components 数据组件精确匹配、predicates 数据组件谓词、entity_tags 记分板标签 any_of/all_of/none_of）、Type-specific Sub-predicates 类型特定子谓词（lightning 闪电方块点燃/实体击中、fishing_hook 钓鱼钩 开放水域、player 玩家检查 level/food/gamemode/stats/recipes/advancements/looking_at/input、cube_mob 史莱姆/岩浆立方体/硫磺立方体 size、raider 袭击者 has_raid/is_captain、sheep 羊 sheared）。"
whenToUse: "Use when writing entity predicates in advancements, loot predicates, or target selectors."

---

# Entity Predicate

An entity predicate tests whether an entity satisfies conditions (used in advancement criteria etc.). Java Edition only.

## Format

A map of entity sub-predicate → test content:

```json
{ "minecraft:entity_type": "minecraft:zombie", "minecraft:flags": { "is_on_fire": true } }
```

## Sub-predicates

- `entity_type` — entity type ID / ID list / `#` tag (inclusion test).
- `location` — location predicate on the entity's position.
- `stepping_on` — location predicate on the block underfoot (fails if not standing on a surface).
- `movement_affected_by` — location predicate on the position affecting movement speed (no lower than 0.5 blocks below the entity).
- `distance` — distance predicate from the entity to the execution position (damage sources: the involved entity's position; advancements: the player's position; other contexts fail).
- `movement` — motion checks (m/s): `fall_distance`, `horizontal_speed`, `speed`, `vertical_speed` (absolute), `x`, `y`, `z` (motion vector components) — double bounds.
- `effects` — mob effects predicate.
- `nbt` — matches NBT (compound or SNBT string).
- `flags` — booleans: `is_baby` (armor stands: small), `is_flying`, `is_on_ground`, `is_on_fire`, `is_sneaking`, `is_sprinting`, `is_swimming`, `is_in_water` (incl. bubble columns), `is_fall_flying`.
- `equipment` — item stack predicates per slot: `body`, `chest`, `feet`, `head`, `legs`, `mainhand`, `offhand`.
- `periodic_tick` — int ≥ 0: at most one success per period (based on loaded time).
- `vehicle` — entity predicate on the ridden entity.
- `passenger` — entity predicate on entities riding this entity.
- `targeted_entity` — entity predicate on the attack target (fails for players/player models/armor stands or when no target).
- `team` — the entity's team name.
- `slots` — item stack predicates per slot range.
- `components` — exact data component match on the entity.
- `predicates` — data component predicates on the entity's components.
- `entity_tags` — scoreboard tags: `any_of`, `all_of`, `none_of` (string lists).
- `type_specific/lightning` — lightning bolts: `blocks_set_on_fire` (int bounds), `entity_struck` (entity predicate).
- `type_specific/fishing_hook` — `in_open_water` (bool).
- `type_specific/player` — player checks:
  - `level` (XP level int bounds),
  - `food` (`level` hunger int bounds, `saturation` double bounds),
  - `gamemode` (list of `survival`/`adventure`/`creative`/`spectator`),
  - `stats` (list of `{type, stat, value (int bounds)}`),
  - `recipes` (recipe ID → bool),
  - `advancements` (advancement ID → bool or per-criterion map),
  - `looking_at` (entity predicate on the visible entity within 100 blocks),
  - `input` (bools: `forward`, `backward`, `left`, `right`, `jump`, `sneak`, `sprint`).
- `type_specific/cube_mob` — slimes/magma cubes/sulfur cubes: `size` (int bounds).
- `type_specific/raider` — vindicator/evoker/illusioner/pillager/witch/ravager: `has_raid`, `is_captain` (defaults false).
- `type_specific/sheep` — `sheared` (bool).

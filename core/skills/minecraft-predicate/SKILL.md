---

name: minecraft-predicate
description: "Minecraft Predicate 谓词（战利品谓词）格式：Definition 定义（data/<namespace>/predicate/ JSON文件、单个对象 condition+字段 或谓词对象列表 所有必须通过 等同all_of、命令内联SNBT）、Invocation 调用（Target selectors predicate= 过滤实体 每个实体调用一次、/execute if predicate 执行位置调用、reference 谓词类型 谓用谓词文件返回结果、其他数据包文件内使用）、Predicate Types 谓词类型（all_of/any_of terms 所有/任一 必须通过 任何上下文可调用、block_state_property 检查block_state上下文 block+properties 属性值或范围、damage_source_properties 检查damage_source+origin 上下文 predicate 伤害源谓词、enchantment_active_check 检查enchantment_active上下文 active bool、entity_properties entity this/attacker/direct_attacker/attacking_player/target_entity/interacting_entity+predicate 实体谓词、entity_scores entity+scores 目标→范围 所有必须通过、environment_attribute_check attribute+value 精确类型值 origin上下文 非维度范围、inverted term 取反、killed_by_player last_damage_player上下文存在、location_check offsetX/Y/Z+offset+predicate 位置谓词 origin+偏移、match_tool predicate 工具上下文、random_chance chance 0-1 随机<chance、random_chance_with_enchanted_bonus attacking_entity enchantment+enchanted_chance+unenchanted_chance、reference name 谓词ID、survives_explosion explosion_radius上下文 概率1/爆炸半径、table_bonus enchantment+chances 按工具附魔等级选择概率、time_check clock+value+period 游戏时间模运算、value_check value vs range、weather_check raining/thundering bool）、Removed Predicates 已移除谓词（random_chance_with_looting killer上下文 1.20.5移除 替换为random_chance_with_enchanted_bonus）。"
whenToUse: "Use when writing predicate JSON files or inline loot predicates in commands."

---

# Predicate

Predicates (loot predicates) test whether objects/parameters satisfy conditions. Java Edition only. Standalone predicates are JSON files in `data/<namespace>/predicate/` (vanilla ships none).

## Definition

A predicate file is either one object `{ "condition": "<namespace id>", ... }` or a list of predicate objects (list form = all must pass, equivalent to `all_of`). When inlined in commands, SNBT is used.

## Invocation

- **Target selectors**: the `predicate=` selector argument filters entities (the predicate file is called once per entity at its position).
- **`/execute if predicate`** — calls a predicate file or inline predicate at the execution position.
- **`reference`** — a predicate type that calls a predicate file and returns its result.
- Predicates also appear inside other datapack files (advancements, loot tables).

Predicates return "pass"/"fail"; a file with multiple predicates passes only when all pass. `/reload` reloads predicate files in a running save.

## Predicate Types

- `all_of` / `any_of` — `terms` (list of predicate objects, recursive): all / any must pass. Callable from any context.
- `block_state_property` — checks the `block_state` context (fails without it): `block` (block ID) and `properties` (map of property → value or `{min, max}` string range).
- `damage_source_properties` — checks the `damage_source` + `origin` context: `predicate` (damage source predicate).
- `enchantment_active_check` — checks `enchantment_active` context: `active` (bool).
- `entity_properties` — `entity` (this/attacker/direct_attacker/attacking_player/target_entity/interacting_entity) + `predicate` (entity predicate).
- `entity_scores` — `entity` (same targets) + `scores` (map of objective → `{min, max}` number providers); all must pass.
- `environment_attribute_check` — `attribute` (environment attribute ID) + `value` (exact typed value); position-variant attributes need the `origin` context, dimension-wide ones don't.
- `inverted` — `term` (recursive): negated result.
- `killed_by_player` — passes if the `last_damage_player` context exists.
- `location_check` — `offsetX/Y/Z` (optional ints) + `predicate` (location predicate) applied at `origin` + offset (fails without `origin`).
- `match_tool` — `predicate` (item stack predicate) applied to the `tool` context (fails without it).
- `random_chance` — `chance` (number provider, 0–1): random < chance.
- `random_chance_with_enchanted_bonus` — needs `attacking_entity`: `enchantment` (ID), `enchanted_chance` (level-based function), `unenchanted_chance` (0–1, used when the enchantment is absent).
- `reference` — `name` (predicate ID); cycles fail parsing.
- `survives_explosion` — passes with probability 1/explosion radius using the `explosion_radius` context (passes if absent).
- `table_bonus` — `enchantment` + `chances` (list indexed by enchantment level): picks the probability for the `tool` context's enchantment level (fails without `tool`).
- `time_check` — `clock` (world clock ID), `value` (`{min, max}` or exact, number providers), `period` (optional; game time modded first — e.g. 24000 = time of day).
- `value_check` — `value` (number provider) vs `range` (`{min, max}`).
- `weather_check` — `raining` / `thundering` (bools).

## Removed Predicates

- `random_chance_with_looting` — used the removed `killer` context: chance + looting level × `looting_multiplier` (removed in 1.20.5, replaced by `random_chance_with_enchanted_bonus`).

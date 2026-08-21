---

name: minecraft-slot-source
description: "Minecraft Slot Source 槽源格式：Definition Format 定义格式（26.3前仅战利品表使用、26.3后 SLOT_SOURCE 注册表 data/<namespace>/slot_source/、对象 type+字段 或槽源列表 列表=group行为）、Types 类型列表（group 分组 terms 递归列表 顺序连接槽列表 保留重复、filtered 过滤 item_filter 物品栈谓词+slot_source 递归 丢弃失败槽、limit_slots 限制 limit 最大数量+slot_source 保留前limit个槽、slot_range 槽范围 source 战利品上下文来源 block_entity/this/attacking_entity/last_damage_player/direct_attacker/target_entity/interacting_entity 默认container + slots 槽范围如armor.chest/container.* 26.3可直接指定槽范围转换为此类型）、contents 内容 component bundle_contents/charged_projectiles/container+slot_source 递归 获取输入槽物品的容器组件槽 空/缺失物品或组件无槽、reference 引用 26.3 name 槽源ID 循环解析失败、empty 空 无槽）。"
whenToUse: "Use when writing slot sources in loot tables or /item commands."

---

# Slot Source

Slot sources select specific slots from slot-holding objects (block entities, entities). Java Edition only. Used in loot tables and (from 26.3) command parameters.

## Definition Format

Before 26.3, slot sources are loot-table-only. From 26.3: registry `SLOT_SOURCE`, data pack path `slot_source` (files in `data/<namespace>/slot_source/`; tags in `tags/slot_source/`).

A slot source is an object `{type, ...}` or a list of slot sources (list = `group` behavior).

## Types

- `group` — `terms` (recursive list): concatenates the slot lists in order, duplicates included (`[a,b]` + `[a,c]` → `[a,b,a,c]`).
- `filtered` — `item_filter` (item stack predicate) + `slot_source` (recursive): drops slots whose item fails the test.
- `limit_slots` — `limit` (max count) + `slot_source`: keeps only the first `limit` slots in order.
- `slot_range` — picks slots from a source's slot range: `source` (from the loot context: `block_entity`, `this`, `attacking_entity`, `last_damage_player`, `direct_attacker`, `target_entity`, `interacting_entity`; default `container`) and `slots` (slot range like `armor.chest`, `container.*`). From 26.3, directly specifying a slot range in the `slot_source` command parameter converts to this type (source = the command's `container` context parameter).
- `contents` — gets slots from container components of the input slots' items: `component` (`bundle_contents`, `charged_projectiles`, or `container`) + `slot_source` (recursive). Empty/missing items or components yield no slots. From 26.3, `/item` targeting component slots first sets the component on the item when missing; `(fill|override)` gets all available component slots; `bundle_contents` fills in slot order, stopping when the bundle would overflow.
- `reference` (26.3) — `name` (slot source ID); cycles fail parsing.
- `empty` — no slots.

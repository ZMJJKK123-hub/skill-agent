---

name: minecraft-attribute
description: "Minecraft 属性系统：Attribute 属性定义（generic.max_health/generic.attack_damage/generic.movement_speed/generic.scale 等、范围/类型/适用实体/默认值）、Per-entity 属性数据（base 基础值 + modifiers 修饰符）、Modifiers 修饰符（id、type 属性、operation 操作、amount 数量）、Modifier Sources 来源（items 物品、enchantments 附魔、status effects 状态效果、location 位置、entity data 实体数据）、Modifier Persistence 持久化（非持久化 enchantment/item modifiers、持久化 status effect modifiers）、Operations 操作类型（Op0 add_value 加值、Op1 add_multiplied_base 基础乘算、Op2 add_multiplied_total 总乘算、计算公式 base + ΣOp0 × (1 + ΣOp1) × ∏(1 + Op2)）、Tooltip Display 工具提示显示（attribute_modifiers 组件、2位小数、base_attack_damage/base_attack_speed 深绿色渲染）、Buffs Buffs 系统（Bedrock 瞬时/临时 buff）、/attribute 命令、/summon attributes NBT、attribute_modifiers 物品组件。"
whenToUse: "Use when working with attributes and attribute modifiers (items, enchantments, /attribute, /summon attributes)."

---

# Attribute

Attributes are the buff/debuff system for mobs, with modifiers adjusting their strength. Java Edition unless noted.

## Attributes

Each attribute controls an ability (attack damage, speed, ...); values are doubles (Java). Java attributes have: a **range** (computed values clamp to it), a **type** (positive/negative/neutral — determines modifier tooltip color: blue for improving positive attributes, red for worsening, gray for neutral), **applicable mobs** (the attribute doesn't exist on others), and a **default value** (base default).

Per-entity attribute data: **base** (value before modifiers) + **modifiers**. The final **computed value** takes effect.

## Known Attributes (Java)

The full attribute list (generic.max_health, generic.follow_range, generic.attack_damage, generic.attack_speed, generic.armor, generic.movement_speed, generic.scale, generic.step_height, player.*, zombie.*, horse.*, ...): see the Minecraft Wiki "Attribute" page. Bedrock attributes additionally have redefinition modes, sync flags, current min/max/current values, and buffs.

## Modifiers

Java modifiers have an `id` (its name/effect is irrelevant — the effect comes from `type` (attribute), `operation`, and `amount`). Bedrock modifiers carry a UUID, name, operation, operand, and amount. Modifier amounts are unlimited but the final computed value still clamps to the attribute's range.

### Sources

Modifiers come from items (in valid slots; zero-durability items' modifiers stop working), enchantments, status effects, location, and entity data. Two modifiers with the same id (Java) or identical base attributes (Bedrock) on the same attribute replace each other — they don't stack.

### Persistence

Non-persistent modifiers (all enchantment attribute effects, item modifiers) exist only in memory and can't be fetched by `/data` (only `/attribute`); persistent ones (status effect modifiers) save with the entity. Effects on computed values are identical.

### Operations

Applied in fixed order to base (and min/max in Bedrock):

- **Op0 add_value**: Result0 = base + ΣOp0ᵢ (e.g. 3 + 2 + 4 = 9).
- **Op1 add_multiplied_base**: Result1 = Result0 × (1 + ΣOp1ⱼ) (e.g. 9 × (1+3+6) = 90).
- **Op2 add_multiplied_total**: Result2 = Result1 × ∏(1 + Op2ₖ) (e.g. 90 × 3 × 5 = 1350).

Total: (base + ΣOp0ᵢ) × (1 + ΣOp1ⱼ) × ∏(1 + Op2ₖ). Bedrock additionally applies the redefinition mode and a **cap (Op3)** clamp: clamp(Result2_current, currentMin, min(currentMax, Op3ᵢ)).

### Tooltip Display (Java)

Tooltips show item-granted modifiers (from `attribute_modifiers` component, enchantment attribute effects, active status effects); 2 decimals; zero amounts hidden; `base_attack_damage`/`base_attack_speed` modifier IDs render dark green (offset, no "+", showing the sum with the attribute base); Infinity shows "∞".

## Buffs (Bedrock)

Instantaneous (apply once, not persistent) and temporal (per-tick, removed after their lifetime) buffs add to the current values (addition; negatives subtract — e.g. health: positive = heal, negative = damage). They may be blocked (damage_sensor), redirected (absorption), or altered (totem sets health to 1.0).

## Examples

```mcfunction
attribute @s minecraft:scale modifier add scale_bonus 0.25 add_value
give @s diamond_sword[attribute_modifiers=[{type:"attack_damage", id:"minecraft:base_attack_damage", slot:"mainhand", amount:20, operation:"add_value"}]]
summon zombie ~ ~ ~ {attributes:[{id:"follow_range",base:100.0d}]}
```

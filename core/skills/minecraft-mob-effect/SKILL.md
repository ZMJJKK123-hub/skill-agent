---

name: minecraft-mob-effect
description: "Minecraft Mob Effect 药水效果：Potion Effects 药水效果基础数据（药水/喷溅药水/滞留药水/箭矢/区域效果云 使用、药水物品和实体存储药水效果数据、未指定或未识别ID使用不可合成药水或水瓶效果）、效果属性（名称、颜色、应用状态效果 等级和持续时间、其他行为）、Duration Notes 持续时间说明（喷溅药水按距离缩短、滞留药水和区域效果云 1/4持续时间、箭矢 1/8持续时间）、Potion Color 药水颜色（Java混合算法计算 非预定义）、Bedrock 数字ID（药水数据值 箭矢+1）、Effect Names 效果名称（部分与状态效果名称不同、部分药水效果无状态效果 如乌龟大师药水应用多个）、Full Effect List 完整效果列表（Minecraft Wiki）。"
whenToUse: "Use when understanding potion effect data, potion colors, names, and their linked status effects."

---

# Potion Effects

This content applies only to Java Edition.

Potion effects are the base data used by potions, splash potions, lingering potions, tipped arrows, and area effect clouds. Potion items and the splash potion / lingering potion / arrow / area effect cloud entities store a potion effect in their data. If no potion effect is specified, or the ID is unrecognized, the uncraftable potion or water bottle effect is used.

A potion effect determines the potion's name, color, the status effects it applies (with level and duration), and other behaviors. Some effect names differ from their status effect names; a few potion effects have no status effect (e.g. the Turtle Master potion applies several).

## Potion effect list

Duration notes: splash potions apply duration scaled down with distance from the break point; lingering potions and area effect clouds apply 1⁄4 duration; tipped arrows apply 1⁄8 duration. The "potion color" column is computed by the Java mixing algorithm, not predefined. Bedrock numeric IDs are the data values of potions (arrows +1 each).

For the full effect list (name, ID, color, linked status effects), see Minecraft Wiki.

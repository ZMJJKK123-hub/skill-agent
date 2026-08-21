---

name: minecraft-cow
description: "Minecraft Cow 牛：Spawning 生成（grass blocks/light≥7/2 air blocks/5% babies、biome variants 温带/寒冷/温暖、平原/沼泽/风袭山丘/森林/干旱生物群系自然生成、村庄牛栏生成）、Mooshroom Conversion 蘑菇牛转换（剪切蘑菇牛变成牛 总是温带变体）、Sound Variants 声音变体（Classic 和 Moody 各50%）、Drops 掉落（生牛肉 烧死时变熟/Fire Aspect、皮革、1-3 XP 成年牛）、Behavior 行为（漫游/哞叫/避免悬崖/岩浆/火焰/受伤逃跑、桶挤奶成年牛获得牛奶桶）、Breeding 繁殖（小麦跟随 10/16方块、爱心模式、1只幼崽 1-7 XP、5分钟冷却、20分钟成长、每条小麦减少10%剩余时间、幼崽继承父母变体、金蒲公英控制生长）、Data Values 数据（sound_variant 声音变体、variant 变体 温带/寒冷/温暖）。"
whenToUse: "Use when working with cows (breeding, milking, variants)."

---

# Cow

Cows are common friendly mobs in the Overworld — the main source of leather, beef, and milk buckets. (Mushroom-covered variants: mooshrooms.)

## Spawning

Periodic + pack spawns on grass blocks with light ≥ 7 and 2 air blocks above; 5% babies. Biome variants exist; natural spawns only in plains, sunflower plains, swamp, windswept hills/forest/gravelly hills, forest-type biomes (except pale garden), and dry biomes (except desert). Cows also spawn in village cow pens. Shearing a mooshroom turns it into a cow — always the temperate variant regardless of biome.

### Sound Variants

**Classic** and **Moody** (50% each, independent of the biome variant) — idle, death, and hurt sounds.

## Drops

Raw beef (cooked when killed while on fire; Java: also Fire Aspect unless not on fire) and leather; 1–3 XP (player/tamed wolf kill). Babies drop nothing.

## Behavior

Wander, moo, avoid cliffs/lava/fire, flee when hurt. Using a bucket on an adult cow yields a milk bucket.

### Breeding

Cows follow players holding wheat within 10/16 blocks. Feed two adults (within 7 blocks) wheat → love mode → 1 baby (1–7 XP; 5-min/1-min cooldown). Babies grow in 20 minutes (each wheat −10% remaining); variant = random parent's. Golden dandelions halt/restart growth (halted babies accept only golden dandelions).

## Data Values

- ID: `minecraft:cow`.
- NBT: entity/living/mob/breedable/animal common tags plus:
  - `sound_variant` (invalid → `classic`; → component `cow/sound_variant`).
  - `variant` (invalid → `temperate`; → component `cow/variant`).

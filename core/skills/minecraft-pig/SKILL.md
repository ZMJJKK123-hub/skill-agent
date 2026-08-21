---

name: minecraft-pig
description: "Minecraft Pig 猪：Spawning 生成（grass blocks/light≥7/2 air blocks/5% babies、biome variants 温带/寒冷/温暖、平原/沼泽/风袭山丘/森林/干旱生物群系自然生成、村庄猪栏生成）、Sound Variants 声音变体（Big/Classic/Mini 各33.3%）、Drops 掉落（生猪肉 烧死时变熟/Fire Aspect、鞍、1-3 XP）、Behavior 行为（漫游/避免悬崖/岩浆/受伤逃跑、闪电将猪变成僵尸猪灵）、Breeding 繁殖（胡萝卜/马铃薯/甜菜根 爱心模式 1只幼崽 1-7 XP 5分钟冷却、20分钟成长、金蒲公英控制生长）、Riding 骑乘（鞍+胡萝卜钓竿控制、自动跳过1方块高度、闪电移除鞍、速度2.42方块/秒 胡萝卜钓竿加速 1+1.15×sin(t/t0·π)×base）、Data Values 数据（sound_variant 变体 variant 变体 温带/寒冷/温暖）。"
whenToUse: "Use when working with pigs (breeding, riding, variants)."

---

# Pig

Pigs are common friendly mobs in the Overworld — the main source of raw/cooked porkchops.

## Spawning

Periodic + pack spawns on grass blocks with light ≥ 7 and 2 blocks of air above. Biome variants exist (temperate, cold, warm...); natural spawns only in plains, sunflower plains, swamp, cherry grove, windswept hills/forest/gravelly hills, forest-type biomes (except pale garden), and dry biomes (except desert). Pigs also spawn in village pig pens, huts, and butcher backyards. 5% of natural spawns are babies.

### Sound Variants

**Big**, **Classic**, **Mini** (33.3% each, independent of the biome variant) — used for idle, eating, death, and hurt sounds.

## Drops

Raw porkchop (cooked when killed while on fire; Java: also with Fire Aspect unless not on fire), the saddle (if saddled), 1–3 XP (player/tamed wolf kill). Babies drop nothing.

## Behavior

Like other passive mobs: wander, avoid lava/falling cliffs, flee when hurt. Lightning turns pigs into zombified piglins (non-peaceful). Pigs follow players holding carrots, carrot-on-a-stick, potatoes, or beetroot within 10/16 blocks.

### Breeding

Feed two adults carrots, potatoes, or beetroot → love mode → 1 baby (1–7 XP; 5-min/1-min cooldown). Babies grow in 20 minutes (each feed −10% remaining); variant = random parent's. Golden dandelions halt/restart growth (halted babies accept only golden dandelions).

### Riding

Saddle an adult pig to ride it (leashable); a carrot on a stick steers it. Pigs auto-step over 1-block heights; only the pig takes fall damage. Lightning turning a saddled pig into a zombified piglin removes the saddle (Java: riders don't dismount); leashes don't break on conversion (Java).

Speed: 2.42 blocks/s normally. Using a carrot on a stick boosts speed (7 or 2 durability lost) for 7–49 s or 3 s, to 1 + 1.15×sin(t/t0·π) × base.

## Data Values

- ID: `minecraft:pig`.
- NBT: entity/living/mob/breedable/animal common tags plus:
  - `sound_variant` (invalid → `classic`; → component `pig/sound_variant`).
  - `variant` (invalid → `temperate`; → component `pig/variant`).

## Trivia

Pigs in minecarts behave specially (speed boost, stop only by collision); Notch accidentally made the pig's body dimensions swapped and reused the model for creepers; temperate pigs resemble Yorkshire pigs, tropical pigs resemble red river hogs; deadmau5's songs reference pig minecarts; pre-24w33a, riding a pig into a minecart increased its speed.

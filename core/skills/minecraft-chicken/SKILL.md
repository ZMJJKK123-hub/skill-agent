---

name: minecraft-chicken
description: "Minecraft Chicken 鸡：Spawning 生成（biome-based variants 温带/寒冷/温暖、自然生成 grass blocks/2 blocks air/light≥9、森林/干旱/平原/沼泽/风袭山丘生物群系）、Chicken Jockeys 鸡骑士（幼年僵尸/溺尸/尸壳/僵尸村民/僵尸猪灵骑乘鸡）、Egg Spawning 鸡蛋生成（1/8 概率1只小鸡、1/32 概率额外4只）、Sound Variants 声音变体（Classic 和 Picky 各50%）、Drops 掉落（鸡肉 生/熟、羽毛、1-3 XP 鸡骑士10 XP）、Behavior 行为（漫游/游泳/拍翅膀减速下落、成年鸡5-10分钟下1蛋、鸡骑士不下蛋、小麦/甜菜/南瓜/西瓜种子/仙人掌种子/豌豆荚跟随和繁殖、10/16方块跟随距离）、Breeding 繁殖（爱心模式、1只幼崽、1-7 XP、5分钟冷却、幼崽继承父母变体、20分钟成长、金蒲公英控制生长）、Data Values 数据（EggLayTime 下蛋倒计时6000-12000、IsChickenJockey 鸡骑士标志 10 XP、sound_variant/variant 组件）。"
whenToUse: "Use when working with chickens (breeding, egg farms, jockeys, variants)."

---

# Chicken

Chickens are common friendly mobs — sources of chicken meat, feathers, and eggs.

## Spawning

Chickens have biome-based variants (temperate, cold, warm...). Natural spawning (Java): periodic + pack spawns on grass blocks with 2 blocks of air above and light level ≥ 9 (Bedrock: light ≥ 7). They spawn in forest-type biomes (except pale garden), dry biomes (except desert), plains, sunflower plains, swamp, windswept hills/forest/gravelly hills. 5% of periodic spawns are babies.

### Chicken Jockeys

Baby zombies, baby drowned, baby husks, baby zombie villagers, and baby zombified piglins can spawn riding chickens; the chicken's spawn conditions follow the passenger's.

### Egg Spawning

Thrown eggs that break have a 1/8 chance to spawn 1 baby chicken; if successful, a further 1/32 chance spawns 4 more. Babies can spawn inside walls (suffocation).

## Sound Variants

**Classic** and **Picky** (50% each, independent of the biome variant) — affect idle, death, and hurt sounds.

## Drops

Adult chickens drop chicken meat (raw; cooked only when killed while on fire), and feathers (Java: not when killed on fire with a non-Fire Aspect weapon). 1–3 XP when killed by a player or tamed wolf (10 XP in Java if spawned as part of a chicken jockey). Babies drop nothing.

## Behavior

Chickens wander, swim, and flap their wings to slow falls (still avoid cliffs). In loaded chunks, adults lay 1 egg every 5–10 minutes (6000–12000 ticks); jockey chickens never lay; dying chickens can still lay; babies can't. Shared "livestock" behavior: flee when hurt, swim (visible flapping), follow players holding wheat seeds, beetroot seeds, melon seeds, pumpkin seeds, torchflower seeds, or pitcher pods within 10/16 blocks, and breed with those seeds. Babies follow adults. Attacked by ocelots and foxes (Java: also player-trusted foxes after rejoin). Swimming requires 2 air blocks above or the chicken drowns. Chickens jump up stairs instead of walking around them.

### Breeding

Feed two adults (wheat/beetroot/melon/pumpkin seeds, torchflower seeds, pitcher pods) → love mode → 1 baby (1–7 XP; 5-min/1-min cooldown). The baby's variant is a random parent's (biome-independent). Babies grow in 20 minutes; each feed reduces remaining growth ~10%. Golden dandelions halt/restart growth (halted babies accept only golden dandelions).

## Data Values

- ID: `minecraft:chicken`.
- NBT: entity/living/mob/breedable/animal common tags plus:
  - `EggLayTime` — ticks until the next egg (lays at 0, resets to 6000–12000; absent → reset on load).
  - `IsChickenJockey` — true for jockey mounts: can be naturally despawned, never lays eggs, drops 10 XP; the baby zombie controls the chicken regardless.
  - `sound_variant` (invalid → `classic`; → component `chicken/sound_variant`).
  - `variant` (invalid → `temperate`; → component `chicken/variant`).

## Trivia

Cold chickens are based on Polish chickens; chickens can hide in hoppers/cauldrons; Notch's "chicken → duck" tweet was a joke; April Fools Java 2.0 had diamond/lapis chickens; chickens spawn more often in sparse jungles (Java).

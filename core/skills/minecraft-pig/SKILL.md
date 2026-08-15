---
name: minecraft-pig
description: Pig — spawning, variants, sound variants, drops, breeding, riding (carrot on a stick speed), NBT.
whenToUse: Use when working with pigs (breeding, riding, variants).
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

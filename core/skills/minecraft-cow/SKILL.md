---

name: minecraft-cow
description: "Cow — spawning, mooshroom conversion, sound variants, drops, milking, breeding, NBT."
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

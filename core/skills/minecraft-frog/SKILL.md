---
name: minecraft-frog
description: Frog — spawning, tadpoles, skin variants, hunting (slimes, magma cubes, froglight), breeding, NBT.
whenToUse: Use when working with frogs and tadpoles (breeding, froglight farming, variants).
---

# Frog

Frogs are friendly mobs spawning in swamps and mangrove swamps.

## Spawning

- Temperate frogs spawn in swamps; warm frogs in mangrove swamps (Java: `#spawns_warm_variant_frogs` / `#spawns_cold_variant_frogs` biome tags; anything else → temperate). Bedrock: no light requirement, 2×2×2 space check.
- **Tadpoles** grow into frogs after 20 minutes — the only way to get cold frogs in survival. Feeding slime balls speeds growth (−10% remaining each).

## Skin Variants

Cold (green), warm (white), temperate (orange) — determined by the biome at generation (including tadpole growth).

## Drops

1–3 XP when killed by a player or tamed wolf.

## Behavior

Slow hopping on land, fast swimming (usually toward the surface, staying at the waterline), limbs spread in mid-air, throat pouch inflation. Frogs jump up to 8 blocks high; like goats they take 5 less fall damage. They prefer jumping onto big dripleaves and lily pads; walk up 1-block steps; leashable; never drown.

### Hunting

Frogs hunt small slimes (speed up, tongue snap → 1 slime ball) and small magma cubes — the variant determines the dropped froglight: cold → verdant, warm → ochre, temperate → pearlescent. Java: base attack damage 10 until death, no death animation; Bedrock: prey vanishes instantly.

### Breeding

Frogs follow players holding slime balls within 10/16 blocks. Feed two frogs slime balls → love mode (1–7 XP; 5-min/1-min cooldown). One parent becomes pregnant and searches (Manhattan ≤ 8 blocks) for land adjacent to water; it lays frogspawn above a water block with air above, re-searching every 40 ticks until successful.

## Data Values

- ID: `minecraft:frog`.
- NBT: entity/living/mob/animal common tags plus `variant` (namespace ID: `temperate`/`warm`/`cold`; invalid → `temperate`; → component `frog/variant`).

## Trivia

Warm frogs model the African gray tree frog; temperate frogs the bullfrog. Froglight was originally planned from eating fireflies, dropped after the real-world toxicity discovery. In Java, editing `frog_food.json` can make frogs attack most mobs (armor stands and the Ender Dragon get attacked without damage).

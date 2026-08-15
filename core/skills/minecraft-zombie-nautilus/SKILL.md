---
name: minecraft-zombie-nautilus
description: Zombie Nautilus — spawning, taming, equipment, riding, undead traits.
whenToUse: Use when working with zombie nautiluses (taming, riding, nautilus armor).
---

# Zombie Nautilus

Zombie nautiluses are friendly mobs spawning with drowned — the undead variant of nautiluses.

## Spawning

Java: when a drowned spawns naturally or via structures (ocean ruins) in a non-river/frozen-river biome, is not a baby, and holds a trident in the main hand, there is a 50% chance a zombie nautilus spawns as its mount. That's the only natural spawning. Bedrock: ocean biomes rarely spawn 2–4 extra drowned, one adult riding a zombie nautilus. In warm oceans the coral zombie nautilus variant replaces it (Java: `/summon zombie_nautilus ~ ~ ~ {variant:warm}`).

## Drops

1–3 XP (player/tamed-wolf kill), the equipped saddle and nautilus armor (Bedrock).

## Behavior

Saddled zombie nautiluses wander within 16 blocks, unsaddled within 32. Immune to poison. Friendly but counts toward the monster mob cap. Bedrock: drowned mount nearby untamed ones; iron golems/snow golems attack them; rabbits flee them.

### Attacks

Untamed zombie nautiluses attack anything that hurt them: back off, then dash, dealing damage + strong knockback (hitting others along the way), hostility auto-ending after ~20 s. They occasionally attack nearby pufferfish. Holding fish or fish buckets stops them attacking a hostile player. Tamed ones never become hostile. They cannot attack on land.

### Dehydration

Fully out of water they can't move on their own (still rideable/controllable); unlike nautiluses they take no dehydration damage.

### Taming

Feed pufferfish or pufferfish buckets (1/3 chance per feed; bucket → water bucket). Tamed zombie nautilus deaths show a death message.

### Equipment

Two inventory slots: **nautilus armor** (zombie-nautilus-only armor) and **saddle**. Both removable with shears (armor first).

### Riding

With a saddle: direction + jump keys control it; dismount like a horse; use items/interact while riding; no slow sinking. Water speed 7.15 m/s (10% faster than nautilus, faster than Depth Strider III sprint-swimming). The XP bar becomes the **dash charge bar**: hold jump to charge; release to dash. Max charge at 10 ticks (0.5 s; bar reaches the orange zone) → 26.40 m/s for ~11 blocks; charging longer shrinks the bar and weakens the dash. Speed affected by Speed/Slowness. After dashing: 55-tick (2.75 s) cooldown. A nautilus-style health bar shows while riding. Riding grants the **Nautilus' Breath** effect freezing the oxygen bar (Java: every 40 ticks for 60 ticks; Bedrock: constant 40-tick effect, saddled only). Control on land is possible but much slower.

### Feeding

Feed any fish or fish bucket to heal a damaged tamed adult (bucket → water bucket). Java: full-health tamed adults enter love mode (but they can't breed).

## Creature Family

**Undead**: extra damage from Smite melee, healed by Instant Damage, hurt by Instant Health, immune to Regeneration and Poison, no drowning, no dehydration, not attacked by Withers. Unlike most undead they can swim (don't sink). Burn in sunlight unless wearing nautilus armor. **Aquatic** (Java): extra damage from Impaling melee attacks and Impaling trident projectiles.

## Data Values

- ID: `minecraft:zombie_nautilus`.
- NBT: entity/living/mob/animal/tameable common tags plus `variant` (invalid/absent → `temperate`).

## Trivia

The design was inspired by French escargot (per Sarah Boeving).

---

name: minecraft-example-datapack
description: "Slicedlime's example datapacks: macros, return values, data-driven enchantments."
whenToUse: "Use as reference when learning datapack macros, function return values, or data-driven enchantments."

---

# Example Datapacks

The example datapacks by Slicedlime demonstrate game updates. There are two: the 16th-version (23w31a) demo datapack and the data-driven enchantment datapack. Source: <https://github.com/slicedlime/examples/tree/master/datapacks>.

## 16th-version demo datapack

Contains 8 functions demonstrating 23w31a additions.

### Macro functions

`set_time.mcfunction` — sets the time to `$(time)`:

```mcfunction
# Set the time to $(time)
$time set $(time)
```

`eval.mcfunction` — runs the command stored in `$(command)` (without leading slash):

```mcfunction
# Run the command stored in $(command)
$$(command)
```

`concat.mcfunction` — concatenates `$(string1)` and `$(string2)` into storage `$(id)` path `$(path)`:

```mcfunction
# Concatenate $(string1) and $(string2), store result to storage $(id) at $(path)
$data modify storage $(id) $(path) set value "$(string1)$(string2)"
```

### Function return values

`fails.mcfunction` — a function with no return value returns failure (the `setblock` executes normally but nothing is returned).

`fails2.mcfunction` — `return 0` returns failure.

`succeeds.mcfunction` — `return 1` returns success.

`get_player_health.mcfunction` — returns the player's health, or 0 for non-players:

```mcfunction
# Return health if the target is a player
execute if entity @s[type=player] run return run data get entity @s Health
# Return 0 for non-players
return 0
```

### Line continuation

`line_continuation.mcfunction` — demonstrates backslash (`\`) line continuation in commands.

## Data-driven enchantment datapack

Contains 14 enchantments demonstrating the 24w18a data-driven enchantment support:

- **Curse of Annoyance**: curse; each time the holder hits a block with the enchanted item in the main hand, 20% chance to send one of 11 "Cat Facts" messages.
- **Boom Boom**: arrows explode with radius 2 when hitting a block; level has no effect.
- **Claw**: +2 block interaction reach per level.
- **Cowbow**: crossbow load sounds become cow sounds (load = cow idle, loaded = cow hurt).
- **Diminishing**: shrinks the wearer 20% per level.
- **Fire Walker**: walking on the ground converts lava sources within radius level+2 into obsidian (10% crying obsidian); caps at level 14; skips lava with entities; also negates powder snow damage.
- **Fishy**: 0.1% chance per tick while held to spawn a silverfish at the user's position.
- **Curse of Fragility**: 3% chance per block hit / attack / damage taken to lose 64 durability (256 when attacking).
- **Galaxy Brain**: +100 XP on mob kill; level has no effect.
- **Multi-Multishot**: like Multishot, but loads 20 extra arrows per level.
- **Curse of Pollen Allergy**: in forest biomes, 0.5% chance per tick to deal 1 thorns damage to the wearer; level has no effect.
- **Roulette**: tools use no durability, but each use has 1% chance to consume 2000 durability (destroying most tools; netherite tools keep 31).
- **Sparkles!**: wearer continuously emits `ominous_spawning` particles.
- **Thor**: holder immune to damage during thunderstorms.

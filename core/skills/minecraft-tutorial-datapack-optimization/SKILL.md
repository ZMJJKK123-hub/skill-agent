---

name: minecraft-tutorial-datapack-optimization
description: "Tutorial — optimizing datapacks: profiling, selectors, NBT, macros."
whenToUse: "Use when optimizing command-heavy datapacks or debugging performance."

---

# Tutorial: Optimizing Data Packs

Java Edition only. How to optimize commands and datapacks.

## Profiling

Run `/perf` on a dedicated server (or F3+L in single-player), then open `<server root>/debug/profiling/<time>-<world>-<version>.zip` (clickable in chat) and read `server/profiling.txt`. Function performance data: `tick > commandFunctions` and `tick > levels > ServerLevel[<world>] <dimension> > tick > scheduledFunctions`.

## Best Practices

Minecraft is complex; no rule always applies — experiment.

### Reduce Running Commands

The single best optimization: don't run commands every tick. Extend periods or avoid tick loops.

- **`/schedule`**: self-scheduling loops (`schedule function example:loop/2t 2t` inside the function) instead of `#minecraft:tick`; hook the start into `#minecraft:load`.
- **Entity `periodic_tick` predicate**: if global scheduling is bad (e.g. stacking sounds), the `periodic_tick` entity predicate gates per-entity frequency (still runs a selector, so slightly worse than schedule).
- **Advancements on players**: avoid `@a` scans by using an advancement (e.g. `minecraft:tick` trigger with entity_scores/location conditions) whose reward function runs only when conditions change; remember to revoke it (`advancement revoke @s only example:player/score`).
- **Enchantments on mobs**: for non-player entities, enchantment effects (e.g. `minecraft:tick` + `run_function`) run server-side per entity; even "unused" slots like the saddle slot on zombies work.

### Optimize NBT Operations

NBT access/modification is expensive (the game saves the entity, modifies, and reloads it; a new entity is created on writes). Prefer:

- `/execute if items entity @s weapon.mainhand apple run ...` over `@a[nbt={SelectedItem:{...}}]`.
- Predicates over NBT matching: `@a[predicate=example:riding_pig]` with an `entity_properties` predicate (`vehicle.type`) instead of `@a[nbt={RootVehicle:{id:"minecraft:pig"}}]`.
- Item modifiers over data commands: `item modify entity @s contents {function:"set_count",count:10}` instead of `data modify entity @s Item.count set value 10`.
- **Command storage caching**: if ≥3 NBT commands remain, copy the NBT to storage once (`data modify storage example:temp custom_data set from entity @s item.components.minecraft:custom_data`), work on it, then write it back once.

### Reduce execute Subcommands

- `effect give @a[tag=hider] glowing` instead of `execute as @a[tag=hider] run effect give @s glowing`.
- Move conditions into selector args: `execute as @a[tag=hider,scores={timer=0..}] run ...` instead of `execute as @a[tag=hider] if score @s timer matches 0.. run ...`.
- Drop useless `execute run`: `say hi` instead of `execute run say hi`.

### Optimize Target Selectors

- Add `type=` unless every entity type matters: `@e[type=marker,tag=special_altar]`.
- Reduce `@e` usage: merge repeated selectors into one function using `@s`: `execute as @e[type=item] run function example:f/process_item`, then use `execute if items entity @s contents ...` inside.
- Add `distance=` when entities are near: `@e[type=marker,tag=test,distance=..1]` (entities load per chunk).

### Optimize Macro Functions

- Avoid macros when unnecessary: `execute store result score @s example run data get entity @s Age` instead of `$scoreboard players set @s example $(Age)`.
- The game caches ~8 used argument sets per macro function — split a 16-argument macro into two 8-argument ones for a significant speedup.

## Alternatives (risky or mediocre gains)

- **Player-distance gating**: at the entity: `execute as @e[type=item] at @s if entity @a[distance=..24] run ...`; with many entities, tag them once per interval: `tag @e[tag=!active.64,distance=..64] add active.64` / `tag @e[tag=active.64,distance=64..] remove active.64`, run from a `schedule` loop.
- **`return run` matching**: when cases are mutually exclusive, `execute if predicate some:1 run return run function some:1` ends the function early (only for single-branch execution contexts; `as @e` multi-branch runs only the first branch). Put more likely cases first.
- **Binary trees**: for extreme case counts (no macros possible), split by score ranges: root checks `0..127` / `128..255`, nodes halve recursively (`..63`, `64..127`, ...) — O(log n) matching.

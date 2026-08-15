---

name: minecraft-entity-predicate
description: "Entity predicate — sub-predicates: type, location, movement, effects, flags, type-specific."
whenToUse: "Use when writing entity predicates in advancements, loot predicates, or target selectors."

---

# Entity Predicate

An entity predicate tests whether an entity satisfies conditions (used in advancement criteria etc.). Java Edition only.

## Format

A map of entity sub-predicate → test content:

```json
{ "minecraft:entity_type": "minecraft:zombie", "minecraft:flags": { "is_on_fire": true } }
```

## Sub-predicates

- `entity_type` — entity type ID / ID list / `#` tag (inclusion test).
- `location` — location predicate on the entity's position.
- `stepping_on` — location predicate on the block underfoot (fails if not standing on a surface).
- `movement_affected_by` — location predicate on the position affecting movement speed (no lower than 0.5 blocks below the entity).
- `distance` — distance predicate from the entity to the execution position (damage sources: the involved entity's position; advancements: the player's position; other contexts fail).
- `movement` — motion checks (m/s): `fall_distance`, `horizontal_speed`, `speed`, `vertical_speed` (absolute), `x`, `y`, `z` (motion vector components) — double bounds.
- `effects` — mob effects predicate.
- `nbt` — matches NBT (compound or SNBT string).
- `flags` — booleans: `is_baby` (armor stands: small), `is_flying`, `is_on_ground`, `is_on_fire`, `is_sneaking`, `is_sprinting`, `is_swimming`, `is_in_water` (incl. bubble columns), `is_fall_flying`.
- `equipment` — item stack predicates per slot: `body`, `chest`, `feet`, `head`, `legs`, `mainhand`, `offhand`.
- `periodic_tick` — int ≥ 0: at most one success per period (based on loaded time).
- `vehicle` — entity predicate on the ridden entity.
- `passenger` — entity predicate on entities riding this entity.
- `targeted_entity` — entity predicate on the attack target (fails for players/player models/armor stands or when no target).
- `team` — the entity's team name.
- `slots` — item stack predicates per slot range.
- `components` — exact data component match on the entity.
- `predicates` — data component predicates on the entity's components.
- `entity_tags` — scoreboard tags: `any_of`, `all_of`, `none_of` (string lists).
- `type_specific/lightning` — lightning bolts: `blocks_set_on_fire` (int bounds), `entity_struck` (entity predicate).
- `type_specific/fishing_hook` — `in_open_water` (bool).
- `type_specific/player` — player checks:
  - `level` (XP level int bounds),
  - `food` (`level` hunger int bounds, `saturation` double bounds),
  - `gamemode` (list of `survival`/`adventure`/`creative`/`spectator`),
  - `stats` (list of `{type, stat, value (int bounds)}`),
  - `recipes` (recipe ID → bool),
  - `advancements` (advancement ID → bool or per-criterion map),
  - `looking_at` (entity predicate on the visible entity within 100 blocks),
  - `input` (bools: `forward`, `backward`, `left`, `right`, `jump`, `sneak`, `sprint`).
- `type_specific/cube_mob` — slimes/magma cubes/sulfur cubes: `size` (int bounds).
- `type_specific/raider` — vindicator/evoker/illusioner/pillager/witch/ravager: `has_raid`, `is_captain` (defaults false).
- `type_specific/sheep` — `sheared` (bool).

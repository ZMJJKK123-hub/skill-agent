---

name: minecraft-enchantment
description: "Enchantment definition format — root fields, cost ranges, effect components."
whenToUse: "Use when authoring enchantment JSON files in data packs."

---

# Enchantment Definition

Enchantment definitions are data-driven JSON files. Java Edition only.

## Definition Format

Registry `ENCHANTMENT`, data pack path `enchantment` (files in `data/<namespace>/enchantment/`; tags in `data/<namespace>/tags/enchantment/`).

```json
{
  "description": { "translate": "enchantment.minecraft.silk_touch" },
  "anvil_cost": 8,
  "max_level": 1,
  "weight": 1,
  "min_cost": { "base": 15, "per_level_above_first": 0 },
  "max_cost": { "base": 65, "per_level_above_first": 0 },
  "supported_items": "#minecraft:enchantable/mining_loot",
  "slots": [ "mainhand" ],
  "exclusive_set": "#minecraft:exclusive_set/mining",
  "effects": { "minecraft:block_experience": [ { "effect": { "type": "minecraft:set", "value": 0.0 } } ] }
}
```

- `description` (required) — text component shown in tooltips.
- `anvil_cost` (required, ≥0) — XP level cost added per level when combining on an anvil (half, floored, min 1 when from an enchanted book).
- `max_level` (required, 1–255).
- `weight` (required, 0 < w ≤ 1024) — selection weight.
- `min_cost` / `max_cost` (required) — modified enchantment level range: `{base, per_level_above_first}` → level n costs `base + per_level_above_first × (n−1)`. If max < min at some level, that level cannot be produced by tables/modifiers/natural means.
- `supported_items` (required) — items enchantable via the anvil (item ID / item tag / list).
- `primary_items` — items enchantable via the enchanting table; must be a subset of `supported_items`; defaults to it.
- `slots` (required) — equipment slots where the enchantment takes effect (`mainhand`, `offhand`, `head`, `chest`, `legs`, `feet`, `body`, `armor`, `hand`, `any`...). Not all effect components honor it.
- `exclusive_set` (default empty) — incompatible enchantments (ID/tag/list).
- `effects` (default empty) — the enchantment's effect components.

Definitions load once at server startup; `/reload` does not reload them — restart the server.

## Effect Components

### Value-Effect Components

Modify numeric values (mostly while *using* the item, not equipping it — most ignore `slots`):

- **Plain** — value must be a single value effect. Component IDs (table on the wiki; examples): `block_experience`, `damage`, `knockback`, `projectile_damage`, `sweeping_damage`, `smash_damage_per_fallen_block`, `mob_experience`, `fishing_time_reduction`, `fishing_luck_bonus`, `repair_with_xp`, `repair_cost`...
- **With predicates** — list of `{effect, requirements (loot predicates; no predicate files, no structure-piece location syntax)}`. Examples: `post_attack`-independent ones like `projectile_piercing`, `trident_return_acceleration`...
- **With target and predicates** — only `equipment_drops`: list of `{effect, enchanted (attacker — the item's wielder killed an entity; victim — the wielder was killed; item must be in a valid slot), requirements}`; affects the killed entity's equipment drop chance.

### Entity-Effect Components

Trigger entity effects in specific situations:

- **With predicates** — list of `{effect, requirements}`. Examples: `on_hit_block` (trident), `on_death`, `post_attack` uses, `tick`, `projectile_spawned`...
- **With target and predicates** — only `post_attack`: list of `{effect, affected (attacker | damaging_entity | victim), enchanted (attacker — fires when the wielder attacks; arrows/tridents trigger only their own components, other projectiles trigger the main hand's; requires mainhand in slots; victim — fires when the wielder is attacked, item in a valid slot), requirements}`.

### Location-Dependent Component

- `location_changed` — list of `{effect (a location-dependent effect: entity effect or attribute effect), requirements}`; triggers when the mob's block position changes; requires the item in a valid slot.

### Damage Immunity

- `damage_immunity` — list of conditions `{effect: {}, requirements}`; any condition passing makes the mob immune to that damage; valid slot required.

### Other Components

- `attributes` — list of attribute effects (temporary modifiers; valid slot required).
- `crossbow_charging_sounds` — array (index = level I, II, ...; out of range uses the last; higher enchantment level wins): each entry `{start (charging >20%), mid (>50%), end (on fire)}` sound events.
- **Unit components** — `{}` presence is enough (e.g. `soul_speed_height`, `frost_walker`, `mending`, `vanishing_curse`, `binding_curse`, `wind_burst`, `channeling`, `multishot`, `piercing`, `infinity`...).
- `trident_sound` — array of sound events for trident throwing (level-indexed like crossbow sounds).

## Enchantment Effects

Format: `{type: <namespace id>, ...}`. Categories:

### Value Effects

Input value → output value (level-dependent functions use the enchantment level):

- `all_of` — applies `effects` in sequence (chained input/output).
- `add` — x + `value`.
- `multiply` — x × `factor`.
- `set` — output `value` (ignores input).
- `remove_binomial` — binomial reduction with `chance` c: expected output i − c·⌈i⌉.
- `exponential` — x × `base`^`exponent` (both level functions).

### Entity Effects

- `all_of` — applies effects in order.
- `apply_exhaustion` — adds `amount` exhaustion (players only).
- `apply_impulse` — adds an impulse to the entity's `Motion`: `direction` (3 local axes: left, up, forward), `coordinate_scale` (world X/Y/Z), `magnitude` (level function; applied after both scalings).
- `apply_mob_effect` — applies a random effect: `to_apply` (effect ID/tag/list, random pick), `min_amplifier`/`max_amplifier`, `min_duration`/`max_duration` (seconds), all level functions.
- `change_item_damage` — modifies the current item's durability: positive `amount` reduces durability, negative repairs.
- `damage_entity` — random damage: `damage_type`, `min_damage`/`max_damage`.
- `explode` — explosion at the position: `radius`, `sound`, `block_interaction` (`none`/`block` (bed-like)/`mob` (creeper-like)/`tnt`/`trigger` (wind-charge-like)), `attribute_to_user` (default false — no source entity), `create_fire` (default false), `damage_type` (default: `player_explosion` when the source has an owner, else `explosion`), `knockback_multiplier` (default 1), `immune_blocks` (blast resistance treated as 3600000), `offset` (default [0,0,0]), `large_particle` (radius ≥2 and affects blocks) / `small_particle`, `block_particles` (weighted list with `scaling` default 1, `speed` default 1).
- `ignite` — sets fire: `duration` seconds (level function).
- `play_sound` — `sound` (single or level-indexed list), `pitch` (0.00001–2), `volum` (0.00001–10) float providers.
- `replace_block` — replaces a block: `block_state`, `offset` (default [0,0,0]), optional `predicate`, `trigger_game_event`.
- `replace_disk` — replaces a cylinder around the entity: `block_state`, `height`, `radius`, `offset`, `predicate`, `trigger_game_event`.
- `run_function` — runs `function` with the effect entity as executor at its position/facing, permission level 2.
- `set_block_properties` — sets block properties: `offset`, `properties` (map), `trigger_game_event`.
- `spawn_particles` — spawns a single particle: `particle`, `horizontal_position`/`vertical_position` (`entity_position` or `in_bounding_box` with `scale`, `offset`), `horizontal_velocity`/`vertical_velocity` (`base` float provider, `movement_scale` — adds entity velocity × value), `speed` (multiplier; the three velocity values × speed are passed as the particle's three parameters, like `/particle` with count 0).
- `summon_entity` — summons an entity: `entity` (type ID/tag/list, random pick), `join_team` (default false). Lightning summoned by a player triggers the `channeled_lightning` criterion. Coordinates out of X/Z ±30000000 or Y ±20000000 fail.

### Location-Dependent Effects

`type` = `all_of` (nested list), an entity effect type, or `attribute`.

### Attribute Effects

Temporary (non-exportable) attribute modifiers: `amount` (level function), `attribute`, `id`, `operation` (`add_value`/`add_multiplied_base`/`add_multiplied_total`). The actual modifier ID used in computation is `<id>/<equipment slot>`, so multiple valid slots stack.

Complete component ID tables (e.g. `block_experience`, `damage`, `knockback`, `mending`, `soul_speed_height`, ...): see the Minecraft Wiki "Enchantment definition" page or vanilla `data/minecraft/enchantment/*.json`.

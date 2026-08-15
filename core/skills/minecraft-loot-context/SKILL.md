---
name: minecraft-loot-context
description: Loot context — parameters and every parameter set (table and predicate-only).
whenToUse: Use when choosing the loot table `type` field or knowing which parameters are available in predicates/modifiers.
---

# Loot Context

The loot context is the set of parameters available to loot tables, predicates, item modifiers, and number providers. Despite the name, it is also used outside loot tables (advancements, enchantments, commands). Java Edition only.

## Parameters

15/16 parameters, present depending on the context type:

- `this_entity` — the entity causing loot generation.
- `interacting_entity` — the entity performing an interaction.
- `target_entity` — the interaction's target entity.
- `last_damage_player` — the last player who damaged the entity.
- `attacking_entity` — the source entity causing damage/death.
- `direct_attacking_entity` — the direct entity causing damage/death.
- `damage_source` — the damage source.
- `origin` — the source position.
- `block_state` — the interacted block state.
- `block_entity` — the interacted block entity.
- `tool` — the item stack used.
- `explosion_radius` — distance from the explosion center.
- `enchantment_active` — whether the enchantment is active.
- `enchantment_level` — the enchantment level.
- `additional_cost_component_allowed` — whether additional-cost components may apply (villager trades).
- `container` — a slot provider (block entity or entity).

Predicate/modifier target aliases: `this` → `this_entity`; `target_entity`, `interacting_entity`, `attacking_player` → `last_damage_player`, `attacker` → `attacking_entity`, `direct_attacker` → `direct_attacking_entity` (entities); `tool` (item stacks); `block_entity` (block entities).

The context also controls luck sources/computation (see the loot-table skill).

## Parameter Sets

The `type` field of a loot table selects its parameter set, letting the pack validate parameter usage at load time. Non-loot-table systems use hardcoded sets.

### Loot Table Types

- `empty` — no parameters. Used: trial spawner reward generation, ominous item spawner contents.
- `generic` — `this_entity`, `last_damage_player`, `attacking_entity`, `direct_attacking_entity`, `block_entity`, `block_state`, `damage_source`, `explosion_radius`, `origin`, `tool`, `additional_cost_component_allowed`, `container`. Default for tables without a type.
- `advancement_reward` — `this_entity` (the player), `origin`. Advancement rewards.
- `archaeology` — `this_entity` (brushing entity), `origin` (suspicious block center), `tool` (brush). Brushing suspicious blocks.
- `barter` — `this_entity` (the piglin). Piglin bartering.
- `block` — `block_state`, `origin`, `tool`; possible: `this_entity` (breaking player or explosion source), `block_entity`, `explosion_radius`. Block breaking, `/loot mine`, Enderman death with a carried block (tool = enchanted diamond axe with `enderman_loot_drop` → Silk Touch I).
- `block_interact` — `block_state`; possible: `interacting_entity`, `block_entity`, `tool`. Carving pumpkins, shearing hives/nests, picking glow berries/sweet berries, (26.3) filling composters.
- `chest` — `origin`; possible: `this_entity` (opener). Opening loot containers (barrel, chest, trapped chest, hopper, minecarts, dispensers/droppers/crafter, shulker boxes, decorated pots), `/loot loot`.
- `entity` — `this_entity`, `damage_source`, `origin`; possible: `direct_attacking_entity`, `last_damage_player`, `attacking_entity`. Mob death; `/loot kill` (damage source = `magic`).
- `entity_interact` — `target_entity`, `tool`; possible: `interacting_entity`. Brushing armadillos.
- `equipment` — `this_entity`, `origin`. Spawner-equipped mobs.
- `fishing` — `origin`, `tool`; possible: `this_entity` (bobber). Fishing, `/loot fish`.
- `gift` — `this_entity`, `origin`. Cat/villager gifts, sniffer digging, chicken lay, armadillo scute, panda sneeze, baby turtle growth.
- `shearing` — `this_entity`, `origin`, `tool`. Shearing bogged/mooshroom/sheep/snow golem.
- `vault` — `origin`; possible: `this_entity` (opening player), `tool` (key item). Vault display/rewards.

### Predicate-Only Sets (invalid as loot table `type`)

- `advancement_entity` — `this_entity`, `tool`. Advancement entity conditions (origin = the player's position).
- `advancement_location` — `this_entity`, `block_state`, `origin`, `tool`. Advancement location conditions (`allay_drop_item_on_block`, `any_block_use`, `item_used_on_block`, `placed_block`).
- `block_use` — `this_entity`, `block_state`, `origin`. `default_block_use` advancement.
- `command` — `origin`; possible `this_entity`. `/execute if|unless predicate`, `/item`.
- `command_slot_source` (26.3) — `origin`, `container`; possible `this_entity`. Commands reading slot sources.
- `enchanted_damage` — `this_entity`, `damage_source`, `origin`, `enchantment_level`; possible: `attacking_entity`, `direct_attacking_entity`. Enchantment components `armor_effectiveness`, `damage`, `damage_immunity`, `damage_protection`, `equipment_drops`, `knockback`, `post_attack`, `smash_damage_per_fallen_block`.
- `enchanted_entity` — `this_entity`, `origin`, `enchantment_level`. Components `fishing_luck_bonus`, `fishing_time_reduction`, `mob_experience`, `post_piercing_attack`, `projectile_count`, `projectile_spawned`, `projectile_spread`, `tick`, `trident_return_acceleration` (this_entity = the relevant entity per component).
- `enchanted_item` — `tool`, `enchantment_level`. Components `ammo_use`, `block_experience`, `item_damage`, `projectile_piercing`, `repair_with_xp`.
- `enchanted_location` — `this_entity`, `origin`, `enchantment_active`, `enchantment_level`. Component `location_changed`.
- `hit_block` — `this_entity`, `block_state`, `origin`, `enchantment_level`. Component `hit_block`.
- `selector` — `this_entity`, `origin`. Target selector predicates.
- `villager_trade` — `this_entity`, `origin` (+ `additional_cost_component_allowed` in the possible list). Villager trade generation.

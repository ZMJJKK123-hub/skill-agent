---

name: minecraft-tag-damage-type
description: "Damage type tags and their members, for custom damage, game rules, and datapacks."
whenToUse: "Use when writing datapacks or understanding damage reduction rules via damage type tags (#is_fire, #bypasses_armor etc.)."

---

# Damage Type Tags

This content applies only to Java Edition.

Damage type tags are groups of damage types.

## Usage

Damage type tags group damage types; for example, all fire damage belongs to the `#is_fire` tag. When the game tests a damage type against a tag, the test succeeds if the damage type is in the tag.

## Tag list

### `#always_hurts_ender_dragons` (1 entry)

Damage of these types always hurts the ender dragon:

- `#is_explosion`

### `#always_kills_armor_stands` (5 entries)

Damage of these types always fully kills armor stands:

- `arrow`
- `trident`
- `fireball`
- `wither_skull`
- `wind_charge`

### `#always_most_significant_fall` (1 entry)

When a mob dies to damage of this type, the death message always assumes a fall of more than 15 blocks:

- `out_of_world`

### `#always_triggers_silverfish` (1 entry)

Damage of this type always triggers silverfish breaking nearby infested blocks, even without a damage source:

- `magic`

### `#avoids_guardian_thorns` (3 entries)

Damage of these types does not trigger the Guardian or Elder Guardian thorns effect:

- `magic`
- `thorns`
- `#is_explosion`

### `#burn_from_stepping` (3 entries)

Damage of these types is negated by wearing Frost Walker boots:

- `campfire`
- `hot_floor`
- `sulfur_cube_hot`

### `#burns_armor_stands` (1 entry)

Damage of this type reduces an armor stand's health by 4:

- `on_fire`

### `#bypasses_armor` (19 entries)

Damage of these types ignores the damage reduction of armor:

- `on_fire`
- `in_wall`
- `cramming`
- `drown`
- `starve`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#bypasses_cooldown`

Damage of this type ignores post-hit damage immunity. Vanilla does not include this file.

### `#bypasses_effects` (1 entry)

Damage of this type ignores the damage reduction of Resistance and enchantments:

- `starve`

### `#bypasses_enchantments` (1 entry)

Damage of this type ignores the damage reduction of Protection:

- `sonic_boom`

### `#bypasses_invulnerability` (2 entries)

Damage of these types ignores damage immunity, including entities with the `Invulnerable` NBT, creative/spectator players, charging withers, and burrowing wardens. Dying to these damage types does not trigger the Totem of Undying:

- `out_of_world`
- `generic_kill`

### `#bypasses_resistance` (2 entries)

Damage of these types ignores all damage reduction and damage immunity:

- `out_of_world`
- `generic_kill`

### `#bypasses_shield` (12 entries)

Damage of these types ignores shield blocking:

- `#bypasses_armor`
- `cactus`
- `falling_anvil`
- `lava`
- `sweet_berry_bush`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#bypasses_wolf_armor` (12 entries)

Damage of these types ignores wolf armor mitigation:

- `#bypasses_invulnerability`
- `cramming`
- `drown`
- `freeze`
- `thorns`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#can_break_armor_stand` (2 entries)

Damage of these types can break an armor stand in one hit:

- `player_explosion`
- `#is_player_attack`

### `#damages_helmet` (3 entries)

Damage of these types heavily consumes helmet durability:

- `falling_anvil`
- `falling_block`
- `falling_stalactite`

### `#ignites_armor_stands` (2 entries)

Damage of these types sets an armor stand's remaining burn time to 100 game ticks (5 seconds):

- `in_fire`
- `campfire`

### `#is_drowning` (1 entry)

Damage of this type is negated for players when the "drowning damage" game rule (`drowning_damage`) is `false`:

- `drown`

### `#is_explosion` (4 entries)

Damage of these types is reduced by Blast Protection:

- `fireworks`
- `explosion`
- `player_explosion`
- `bad_respawn_point`

### `#is_fall` (3 entries)

Damage of these types is reduced by Feather Falling. It is negated for cats, ocelots, snow golems, iron golems, magma cubes, bats, blazes, the ender dragon, ghasts, parrots, vexes, the wither, chickens, shulkers, and for players when the "fall damage" game rule (`fall_damage`) is `false`:

- `fall`
- `ender_pearl`
- `stalagmite`

### `#is_fire` (8 entries)

Damage of these types is reduced by Fire Protection. It is negated for zombie piglins, ghasts, wither skeletons, blazes, striders, magma cubes, zoglins, wardens, the ender dragon, the wither, mobs with Fire Resistance, and for players when the "fire damage" game rule (`fire_damage`) is `false`:

- `in_fire`
- `campfire`
- `on_fire`
- `lava`
- `hot_floor`
- `sulfur_cube_hot`
- `unattributed_fireball`
- `fireball`

### `#is_freezing` (1 entry)

Damage of this type is negated for players when the "freeze damage" game rule (`freeze_damage`) is `false`:

- `freeze`

### `#is_lightning` (1 entry)

Turtles killed by damage of this type drop a bowl:

- `lightning_bolt`

### `#is_player_attack` (3 entries)

Attack damage types caused by players:

- `player_attack`
- `spear`
- `mace_smash`

### `#is_projectile` (8 entries)

Damage of these types is reduced by Projectile Protection:

- `arrow`
- `trident`
- `mob_projectile`
- `unattributed_fireball`
- `fireball`
- `wither_skull`
- `thrown`
- `wind_charge`

### `#mace_smash` (1 entry)

Used by related advancement files:

- `mace_smash`

### `#no_anger` (1 entry)

Damage of this type does not make the damaged entity retaliate against the attacker:

- `mob_attack_no_aggro`

### `#no_impact` (1 entry)

Damage of this type does not make the server send a position/velocity sync packet after the entity is hurt:

- `drown`

### `#no_knockback` (30 entries)

Damage of these types causes no knockback:

- `explosion`
- `lightning_bolt`
- `fall`
- `magic`
- `wither`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#no_wolf_retaliation`

This section contains content from an upcoming update (Java Edition 26.3 development versions).

Damage of this type to a tamed wolf's owner does not make the wolf retaliate:

- `sulfur_cube_hot`

### `#panic_causes` (20 entries)

Damage of these types makes passive animals panic (try to flee):

- `#panic_environmental_causes`
- `arrow`
- `explosion`
- `magic`
- `#is_player_attack`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#panic_environmental_causes` (8 entries)

Damage of these types makes conditionally hostile animals panic (fight back):

- `cactus`
- `freeze`
- `hot_floor`
- `sulfur_cube_hot`
- `in_fire`
- `lava`
- `lightning_bolt`
- `on_fire`

### `#sulfur_cube_with_block_immune_to` (24 entries)

Damage of these types is negated by sulfur cubes absorbing blocks:

- `arrow`
- `cactus`
- `fall`
- `mob_attack`
- `#is_explosion`

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#witch_resistant_to` (4 entries)

Damage of these types is affected by the witch's 85% damage reduction:

- `magic`
- `indirect_magic`
- `sonic_boom`
- `thorns`

### `#wither_immune_to` (1 entry)

Damage of this type is negated by the wither:

- `drown`

## Removed tags

### `#breeze_immune_to`

Added in 23w45a, removed in 24w21a:

- `arrow`
- `trident`

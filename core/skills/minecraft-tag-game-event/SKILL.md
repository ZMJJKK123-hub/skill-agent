---

name: minecraft-tag-game-event
description: "Game event tags: #vibrations (56 entries) detectable by Sculk Sensor and Calibrated Sculk Sensor, #warden_can_listen (57 entries), #allay_can_listen (1 entry: note_block_play), #shrieker_can_listen (1 entry), and #ignore_vibrations_sneaking (6 entries for sneaking entities)."
whenToUse: "Use when referencing game event tags (vibration system, Allay and Warden listening conditions)."

---

# Game Event Tags

This content applies only to Java Edition.

Game event tags are groups of game events.

## Usage

Game event tags cannot be invoked directly; the game uses them to control detection conditions in the vibration system.

## Tag list

### `#allay_can_listen` (1 entry)

Game events the Allay can detect. Adding other game events does not affect the Allay's AI; removing the default event makes the Allay no longer attracted to note blocks:

- `note_block_play`

### `#ignore_vibrations_sneaking` (6 entries)

Game events produced by sneaking entities that vibration listeners do not detect:

- `hit_ground`
- `projectile_shoot`
- `step`
- `swim`
- `item_interact_start`
- `item_interact_finish`

### `#shrieker_can_listen` (1 entry)

Game events the Sculk Shrieker can detect:

- `sculk_sensor_tendrils_clicking`

### `#vibrations` (56 entries)

Game events detectable by the Sculk Sensor and Calibrated Sculk Sensor. Game events can only be removed; the game does not detect non-default game events. Representative members: `block_attach`, `block_destroy`, `block_place`, `entity_die`, `step`, etc. For the complete list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#warden_can_listen` (57 entries)

Game events the Warden can detect. References `#shrieker_can_listen`; representative members: `block_attach`, `entity_die`, `shriek`, `step`, `swim`, etc. For the complete list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

## Removed tags

### `#dampenable_vibrations`

Added in 22w13a, removed in 22w17a:

- `hit_ground`
- `step`

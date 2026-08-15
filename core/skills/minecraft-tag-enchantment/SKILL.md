---
name: minecraft-tag-enchantment
description: Enchantment tags: acquisition, exclusivity, loot, villager trades.
whenToUse: Use when handling enchantment acquisition, exclusivity, loot, or villager trades via enchantment tags (#treasure, #non_treasure etc.).
---

# Enchantment Tags

This content applies only to Java Edition.

Enchantment tags are groups of enchantments.

## Usage

Enchantment tags control the conditions under which enchantments appear and some basic functions.

## Tag list

### `#curse` (2 entries)

Enchantments shown in red in tooltips and not removable by grinding:

- `binding_curse` (Curse of Binding)
- `vanishing_curse` (Curse of Vanishing)

### `#double_trade_price` (1 entry)

Enchantments costing double emeralds in trades:

- `#treasure`

### `#exclusive_set/armor` (4 entries)

Enchantments that cannot coexist on armor:

- `protection` (Protection)
- `blast_protection` (Blast Protection)
- `fire_protection` (Fire Protection)
- `projectile_protection` (Projectile Protection)

### `#exclusive_set/boots` (2 entries)

Enchantments that cannot coexist on boots:

- `frost_walker` (Frost Walker)
- `depth_strider` (Depth Strider)

### `#exclusive_set/bow` (2 entries)

Enchantments that cannot coexist on bows:

- `infinity` (Infinity)
- `mending` (Mending)

### `#exclusive_set/crossbow` (2 entries)

Enchantments that cannot coexist on crossbows:

- `multishot` (Multishot)
- `piercing` (Piercing)

### `#exclusive_set/damage` (6 entries)

Damage-increasing enchantments that cannot coexist:

- `sharpness` (Sharpness)
- `smite` (Smite)
- `bane_of_arthropods` (Bane of Arthropods)
- `impaling` (Impaling)
- `density` (Density)
- `breach` (Breach)

### `#exclusive_set/mining` (2 entries)

Mining enchantments that cannot coexist:

- `fortune` (Fortune)
- `silk_touch` (Silk Touch)

### `#exclusive_set/riptide` (2 entries)

Enchantments that cannot coexist with Riptide:

- `loyalty` (Loyalty)
- `channeling` (Channeling)

### `#in_enchanting_table` (1 entry)

Enchantments appearing in the enchanting table:

- `#non_treasure`

### `#non_treasure` (36 entries)

Non-treasure enchantments:

- `protection` (Protection)
- `sharpness` (Sharpness)
- `efficiency` (Efficiency)
- `fortune` (Fortune)
- `power` (Power)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#on_mob_spawn_equipment` (1 entry)

Enchantments appearing on equipment of randomly spawned mobs:

- `#non_treasure`

### `#on_random_loot` (5 entries)

Enchantments appearing on loot in loot chests:

- `#non_treasure`
- `binding_curse` (Curse of Binding)
- `vanishing_curse` (Curse of Vanishing)
- `frost_walker` (Frost Walker)
- `mending` (Mending)

### `#on_traded_equipment` (1 entry)

Enchantments appearing on traded enchanted equipment:

- `#non_treasure`

### `#prevents_bee_spawns_when_mining` (1 entry)

Enchantments that prevent angry bees from spawning when mining beehives and bee nests:

- `silk_touch` (Silk Touch)

### `#prevents_decorated_pot_shattering` (1 entry)

Enchantments that prevent decorated pots from shattering:

- `silk_touch` (Silk Touch)

### `#prevents_ice_melting` (1 entry)

Enchantments that prevent ice from melting into water when mined:

- `silk_touch` (Silk Touch)

### `#prevents_infested_spawns` (1 entry)

Enchantments that allow mining infested blocks without spawning the mob inside:

- `silk_touch` (Silk Touch)

### `#smelts_loot` (1 entry)

Enchantments that smelt dropped loot:

- `fire_aspect` (Fire Aspect)

### `#tooltip_order` (43 entries)

Affects the order of enchantments shown in item tooltips:

- `binding_curse` (Curse of Binding)
- `sharpness` (Sharpness)
- `protection` (Protection)
- `fortune` (Fortune)
- `efficiency` (Efficiency)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#tradeable` (5 entries)

Enchantments appearing on traded enchanted books:

- `#non_treasure`
- `binding_curse` (Curse of Binding)
- `vanishing_curse` (Curse of Vanishing)
- `frost_walker` (Frost Walker)
- `mending` (Mending)

### `#treasure` (7 entries)

Treasure enchantments:

- `binding_curse` (Curse of Binding)
- `vanishing_curse` (Curse of Vanishing)
- `swift_sneak` (Swift Sneak)
- `soul_speed` (Soul Speed)
- `frost_walker` (Frost Walker)
- `mending` (Mending)
- `wind_burst` (Wind Burst)

## Villager trade balancing

This section contains experimental content: these features require the "villager trade rebalancing" option to be enabled.

### `#trades/desert_common` (3 entries)

Common enchantments on enchanted books sold by desert librarians:

- `fire_protection`
- `thorns`
- `infinity`

### `#trades/jungle_common` (3 entries)

Common enchantments on enchanted books sold by jungle librarians:

- `feather_falling`
- `projectile_protection`
- `power`

### `#trades/plains_common` (3 entries)

Common enchantments on enchanted books sold by plains librarians:

- `punch`
- `smite`
- `bane_of_arthropods`

### `#trades/savanna_common` (3 entries)

Common enchantments on enchanted books sold by savanna librarians:

- `knockback`
- `binding_curse`
- `sweeping_edge`

### `#trades/snow_common` (3 entries)

Common enchantments on enchanted books sold by snowy librarians:

- `aqua_affinity`
- `looting`
- `frost_walker`

### `#trades/swamp_common` (3 entries)

Common enchantments on enchanted books sold by swamp librarians:

- `depth_strider`
- `respiration`
- `vanishing_curse`

### `#trades/taiga_common` (3 entries)

Common enchantments on enchanted books sold by taiga librarians:

- `blast_protection`
- `fire_aspect`
- `flame`

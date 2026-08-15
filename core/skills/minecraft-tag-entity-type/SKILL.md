---
name: minecraft-tag-entity-type
description: Entity type tags and their members, used in entity predicates, target selectors, and game behavior.
whenToUse: Use when writing entity predicates, target selectors, or datapacks via entity type tags (#undead, #skeletons etc.).
---

# Entity Type Tags

This content applies only to Java Edition.

Entity type tags are groups of entity types.

## Usage

Entity type tags can be used by entity predicates and target selectors to test entity types: the test succeeds if the entity type is in the tag. Entity type tags also control game behaviors related to specific entities, described per tag below.

## Tag list

### `#accepts_iron_golem_gift` (1 entry)

Entities that wear the iron golem's gift on their head:

- `copper_golem` (Copper Golem)

### `#aquatic` (14 entries)

Entities considered aquatic:

- `turtle` (Turtle)
- `axolotl` (Axolotl)
- `guardian` (Guardian)
- `cod` (Cod)
- `dolphin` (Dolphin)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#arrows` (2 entries)

Used by the "Sniper duel" advancement:

- `arrow` (Arrow)
- `spectral_arrow` (Spectral Arrow)

### `#arthropod` (5 entries)

Entities considered arthropods:

- `bee` (Bee)
- `endermite` (Endermite)
- `silverfish` (Silverfish)
- `spider` (Spider)
- `cave_spider` (Cave Spider)

### `#axolotl_always_hostiles` (3 entries)

Entities axolotls are always hostile toward:

- `drowned` (Drowned)
- `guardian` (Guardian)
- `elder_guardian` (Elder Guardian)

### `#axolotl_hunt_targets` (7 entries)

Entities axolotls "hunt" on a cooldown:

- `tropical_fish` (Tropical Fish)
- `pufferfish` (Pufferfish)
- `salmon` (Salmon)
- `cod` (Cod)
- `squid` (Squid)
- `glow_squid` (Glow Squid)
- `tadpole` (Tadpole)

### `#beehive_inhabitors` (1 entry)

Entities that can enter beehives:

- `bee` (Bee)

### `#boat` (11 entries)

Used by the "Smooth Sailing" advancement:

- `oak_boat` (Oak Boat)
- `spruce_boat` (Spruce Boat)
- `acacia_boat` (Acacia Boat)
- `bamboo_raft` (Bamboo Raft)
- `poplar_boat` (Poplar Boat)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#burn_in_daylight` (10 entries)

Entities that catch fire in sunlight:

- `skeleton` (Skeleton)
- `stray` (Stray)
- `zombie` (Zombie)
- `drowned` (Drowned)
- `phantom` (Phantom)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#can_breathe_under_water` (16 entries)

Entities with this tag do not drown:

- `#undead`
- `axolotl` (Axolotl)
- `guardian` (Guardian)
- `turtle` (Turtle)
- `armor_stand` (Armor Stand)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#can_equip_harness` (1 entry)

Entities that can equip a harness:

- `happy_ghast` (Happy Ghast)

### `#can_equip_saddle` (11 entries)

Entities that can equip a saddle:

- `horse` (Horse)
- `skeleton_horse` (Skeleton Horse)
- `pig` (Pig)
- `strider` (Strider)
- `camel` (Camel)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#can_float_while_ridden` (6 entries)

Controls whether a ridden mob floats/swims on water instead of sinking:

- `horse` (Horse)
- `zombie_horse` (Zombie Horse)
- `mule` (Mule)
- `donkey` (Donkey)
- `camel` (Camel)
- `camel_husk` (Camel Husk)

### `#can_turn_in_boats` (1 entry)

Mobs with this tag can turn direction in boats:

- `breeze` (Breeze)

### `#can_wear_horse_armor` (2 entries)

Mobs with this tag show the horse armor slot in their horse inventory:

- `horse` (Horse)
- `zombie_horse` (Zombie Horse)

### `#can_wear_nautilus_armor` (2 entries)

Entities that can equip nautilus armor:

- `nautilus` (Nautilus)
- `zombie_nautilus` (Zombie Nautilus)

### `#candidate_for_iron_golem_gift` (2 entries)

Entities that receive poppies from iron golems:

- `villager` (Villager)
- `#accepts_iron_golem_gift`

### `#cannot_be_age_locked` (3 entries)

Growable mobs that cannot be stopped from aging with golden dandelions:

- `zombie_horse` (Zombie Horse)
- `skeleton_horse` (Skeleton Horse)
- `villager` (Villager)

### `#cannot_be_dismounted_by_item_usage`

This section contains content from an upcoming update (Java Edition 26.3 development versions).

Mobs do not dismount after using an item on these entities:

- `interaction` (Interaction)

### `#cannot_be_pushed_onto_boats` (14 entries)

Entities that cannot be pushed onto boats:

- `player` (Player)
- `elder_guardian` (Elder Guardian)
- `dolphin` (Dolphin)
- `creaking` (Creaking)
- `sulfur_cube` (Sulfur Cube)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#deflects_projectiles` (1 entry)

Mobs with this tag can deflect projectiles:

- `breeze` (Breeze)

### `#dismounts_underwater` (13 entries)

These entities force their riders to dismount when entering water:

- `camel` (Camel)
- `horse` (Horse)
- `llama` (Llama)
- `ravager` (Ravager)
- `strider` (Strider)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#fall_damage_immune` (18 entries)

Entities immune to fall damage:

- `iron_golem` (Iron Golem)
- `shulker` (Shulker)
- `bat` (Bat)
- `phantom` (Phantom)
- `wither` (Wither)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#followable_friendly_mobs` (25 entries)

Non-baby entities that happy ghasts follow:

- `villager` (Villager)
- `horse` (Horse)
- `cat` (Cat)
- `wolf` (Wolf)
- `sniffer` (Sniffer)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#freeze_hurts_extra_types` (3 entries)

Entities with this tag take extra damage in powder snow:

- `strider` (Strider)
- `blaze` (Blaze)
- `magma_cube` (Magma Cube)

### `#freeze_immune_entity_types` (4 entries)

Entities with this tag are immune to freezing damage:

- `stray` (Stray)
- `polar_bear` (Polar Bear)
- `snow_golem` (Snow Golem)
- `wither` (Wither)

### `#frog_food` (2 entries)

Entities frogs prey on (only mob entities are effective):

- `slime` (Slime)
- `magma_cube` (Magma Cube)

### `#ignores_poison_and_regen` (1 entry)

Entities immune to Poison and Regeneration effects:

- `#undead`

### `#illager` (4 entries)

Entities considered illagers:

- `evoker` (Evoker)
- `illusioner` (Illusioner)
- `pillager` (Pillager)
- `vindicator` (Vindicator)

### `#illager_friends` (1 entry)

Entities illagers treat as allies (excluding those in other teams):

- `#illager`

### `#immune_to_infested` (1 entry)

Entities immune to the Infested effect:

- `silverfish` (Silverfish)

### `#immune_to_oozing` (1 entry)

Entities immune to the Oozing effect:

- `slime` (Slime)

### `#impact_projectiles` (11 entries)

Determines which entities can break chorus flowers and decorated pots. Entities can be removed from this tag; adding other entities only works if the target block can respond:

- `#arrows`
- `firework_rocket` (Firework Rocket)
- `snowball` (Snowball)
- `trident` (Trident)
- `wind_charge` (Wind Charge)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#inverted_healing_and_harm` (1 entry)

Entities on which Instant Health and Instant Damage have inverted effects:

- `#undead`

### `#nautilus_hostiles` (1 entry)

Entities untamed nautiluses and zombie nautiluses are hostile toward by default:

- `pufferfish` (Pufferfish)

### `#no_anger_from_wind_charge` (9 entries)

Entities not angered by wind charges:

- `breeze` (Breeze)
- `skeleton` (Skeleton)
- `zombie` (Zombie)
- `spider` (Spider)
- `slime` (Slime)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#non_controlling_rider` (3 entries)

Entities that cannot control vehicle movement:

- `slime` (Slime)
- `magma_cube` (Magma Cube)
- `sulfur_cube` (Sulfur Cube)

### `#not_affected_by_geysers` (1 entry)

Entities unaffected by the upward impulse of geyser eruptions:

- `ender_dragon` (Ender Dragon)

### `#not_scary_for_pufferfish` (14 entries)

Entities that do not inflate pufferfish:

- `turtle` (Turtle)
- `guardian` (Guardian)
- `pufferfish` (Pufferfish)
- `dolphin` (Dolphin)
- `sulfur_cube` (Sulfur Cube)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

### `#powder_snow_walkable_mobs` (4 entries)

Entities with this tag can walk on top of powder snow:

- `rabbit` (Rabbit)
- `endermite` (Endermite)
- `silverfish` (Silverfish)
- `fox` (Fox)

### `#raiders` (6 entries)

Determines which entities get the glowing effect when a bell rings. Entities in this tag do not override the ravager's AI when riding one. Used by the "Self-Exile" advancement:

- `evoker` (Evoker)
- `pillager` (Pillager)
- `ravager` (Ravager)
- `vindicator` (Vindicator)
- `illusioner` (Illusioner)
- `witch` (Witch)

### `#redirectable_projectile` (3 entries)

Projectiles that can be hit by player attacks and projectiles, deflecting with the player's view direction or projectile direction:

- `fireball` (Fireball)
- `wind_charge` (Wind Charge)
- `breeze_wind_charge` (Wind Charge)

### `#sensitive_to_bane_of_arthropods` (1 entry)

Entities taking extra damage from the Bane of Arthropods enchantment:

- `#arthropod`

### `#sensitive_to_impaling` (1 entry)

Entities taking extra damage from the Impaling enchantment:

- `#aquatic`

### `#sensitive_to_smite` (1 entry)

Entities taking extra damage from the Smite enchantment:

- `#undead`

### `#skeletons` (6 entries)

Creepers drop music discs when killed by these entities:

- `skeleton` (Skeleton)
- `stray` (Stray)
- `wither_skeleton` (Wither Skeleton)
- `skeleton_horse` (Skeleton Horse)
- `bogged` (Bogged)
- `parched` (Parched)

### `#undead` (4 entries)

Entities with this tag are undead:

- `#skeletons`
- `#zombies`
- `wither` (Wither)
- `phantom` (Phantom)

### `#wither_friends` (1 entry)

Entities not targeted by the wither and unable to damage it:

- `#undead`

### `#zombies` (9 entries)

Entities with this tag are zombie-type mobs:

- `zombie` (Zombie)
- `zombie_villager` (Zombie Villager)
- `drowned` (Drowned)
- `husk` (Husk)
- `zoglin` (Zoglin)

For the complete member list, see the tag definition under `data/minecraft/tags/` in mc_java_sources/, or Minecraft Wiki.

## Removed tags

### `#axolotl_tempted_hostiles`

Replaced by `#axolotl_always_hostiles`. Added in 20w51a, removed in 21w13a:

- `drowned`
- `guardian`

### `#deflects_arrows`

Replaced by `#deflects_projectiles`. Added in 23w45a, removed in 24w03a:

- `breeze`

### `#deflects_tridents`

Replaced by `#deflects_projectiles`. Added in 23w45a, removed in 24w03a:

- `breeze`

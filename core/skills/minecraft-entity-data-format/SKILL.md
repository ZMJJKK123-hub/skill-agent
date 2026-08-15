---

name: minecraft-entity-data-format
description: "Java entity NBT formats: common tags plus per-entity fields for all mobs."
whenToUse: "Use when writing or parsing entity NBT data (summon commands, datapacks, saves)."

---

# Entity Data Format

This content applies only to Java Edition. For the Bedrock entity format, see the Bedrock article.

Each entity type has its own data format on top of the common tags. For complete field lists, see mc_java_sources/ or Minecraft Wiki.

## Common entity tags (entity data root tags)

- **id** (string): (namespace ID) entity type. Only present in persistent storage (chunk files, structure templates, beehives, passengers). Cannot be read/modified via `/data`.
- **Air** (short): remaining air value (−20 ≤ v ≤ entity max); +4 per tick in air, decreases in suffocating environments; at −20 the entity takes damage and resets to 0. Default: entity max air.
- **CustomName** (text component): custom name; shown in death messages, trading UIs, and above the entity. Treated as the `custom_name` data component.
- **CustomNameVisible** (bool): always render the name. Default false.
- **data** (any NBT): arbitrary data; string form only for loading, saves use compound. Treated as the `custom_data` data component.
- **fall_distance** (double): accumulated fall distance. Default 0.
- **Fire** (short): ticks remaining on fire; negative = ticks immune while standing in fire. Unlit: −20 for players, −1 otherwise. Default 0.
- **Glowing** (bool): glowing outline. Default false.
- **HasVisualFire** (bool): visually on fire. Default false.
- **Invulnerable** (bool): immune to most damage; only creative damage and `#bypasses_invulnerability` apply. Default false.
- **invulnerable_time** (int): remaining invulnerability ticks; not stored when ≤0.
- **Motion** (list of 3 doubles): velocity (−10 ≤ v ≤ 10 per axis; out-of-range resets to 0; NaN loads normally).
- **NoGravity** (bool). Default false.
- **OnGround** (bool). Default false.
- **Passengers** (list): riding entities (recursive); only effective via `/summon`, spawners, and trial spawners.
- **PortalCooldown** (int): ticks until the next nether portal use. Default 0.
- **Pos** (list of 3 doubles): coordinates; X/Z −30000512–30000512, Y −20000000–20000000; out-of-range clamped, NaN causes load errors.
- **Rotation** (list of 2 floats): yaw/pitch in degrees; non-finite values reset to 0.
- **Silent** (bool). Default false.
- **Tags** (list of strings): scoreboard tags, ≤1024.
- **TicksFrozen** (int): freezing time. Default 0.
- **UUID** (int array): cannot be modified via `/data`.

## Mobs

Mob tags store health, states, and effects on top of the common tags. Inheritance chain (parent→child): entity → living → mob → breedable → animal → tameable; common branches: horse, angerable, raidable, zombie. The entries below list representative fields only.

- **Allay**: `DuplicationCooldown` (long; 6000 ticks on duplication), `Inventory` (list, ≤1 stack, itemnoslot), `listener` (vibration listener).
- **Armadillo**: `scute_time` (int; drops scute at <1, resets to 6000–12000), `state` (string: `idle`/`rolling`/`scared`).
- **Armor Stand**: `DisabledSlots` (int, bitmask; 16191/4144896 disable all), `Invisible` (bool), `Marker` (bool, default false), `NoBasePlate` (bool), `Pose` (compound: Body/Head/LeftArm/LeftLeg/RightArm/RightLeg float lists, defaults `[0,0,0]` etc.), `ShowArms` (bool), `Small` (bool).
- **Axolotl**: `FromBucket` (bool), `Variant` (int → `axolotl/variant` component).
- **Bat**: `BatFlags` (bool, hanging).
- **Bee**: `CannotEnterHiveTicks`, `CropsGrownSincePollination` (>10 stops growing crops), `HasNectar`, `HasStung`, `TicksSincePollination` (>2400 flies to `flower_pos` if present), `flower_pos`/`hive_pos` (int arrays).
- **Blaze**: none.
- **Breeze**: none.
- **Camel**: `LastPoseTick` (long; negative = sitting).
- **Cat**: `CollarColor` (byte, 0–15, default 14; → `cat/collar`), `sound_variant` (string, default `classic`), `variant` (string, default `black`).
- **Cave Spider**: none.
- **Chicken**: `EggLayTime` (int), `IsChickenJockey` (bool), `variant` (default `temperate`), `sound_variant` (default `classic`).
- **Cod**: `FromBucket`.
- **Copper Golem**: `next_weather_age` (long, default −1; −2 when waxed), `weather_state` (string: `unaffected`/`exposed`/`weathered`/`oxidized`).
- **Cow**: `sound_variant`, `variant` (default `temperate`).
- **Creaking**: none.
- **Creeper**: `ExplosionRadius` (byte, default 3), `Fuse` (short, default 30), `ignited` (bool), `powered` (bool).
- **Dolphin**: `GotFish`, `Moistness` (int, default 2400; ≤0 → 1 damage/tick out of water).
- **Donkey**: `ChestedHorse` (bool), `Items` (15 slots when chested).
- **Drowned**: none.
- **Elder Guardian**: none.
- **Ender Dragon**: `DragonDeathTime` (int, default 0; removed at >200), `DragonPhase` (int 0–10), `sitting_damage_received` (float).
- **Enderman**: `carriedBlockState` (block state).
- **Endermite**: `Lifetime` (int; removed at ≥2400).
- **Evoker**: `SpellTicks`.
- **Frog**: `variant` (default `temperate`; `temperate`/`warm`/`cold`).
- **Fox**: `Crouching`, `Sleeping`, `Sitting`, `Trusted` (≤2 player UUIDs), `Type` (`red`/`snow`).
- **Ghast**: `ExplosionPower` (byte, default 1).
- **Giant**: none.
- **Glow Squid**: `DarkTicksRemaining`.
- **Goat**: `HasLeftHorn`, `HasRightHorn` (default true), `IsScreamingGoat`.
- **Guardian**: none.
- **Happy Ghast**: `still_timeout` (int; control restored at 0).
- **Hoglin**: `CannotBeHunted`, `IsImmuneToZombification`, `TimeInOverworld` (>300 → zombified).
- **Horse**: `Variant` (int; low 8 bits type, next 8 bits markings; → `horse/variant`).
- **Husk**: none.
- **Illusioner**: `SpellTicks`.
- **Iron Golem**: `PlayerCreated`.
- **Llama**: `ChestedHorse`, `Items` (3×Strength slots), `Strength` (1–5), `Variant` (0–3: `creamy`/`white`/`brown`/`gray`).
- **Magma Cube**: `Size` (0–126), `wasOnGround`.
- **Mannequin (player model)**: `description` (text component), `hidden_layers` (list: `cape`/`jacket`/`left_sleeve`/`right_sleeve`/`left_pants_leg`/`right_pants_leg`/`hat`), `main_hand` (`left`/`right`), `pose` (`standing`/`crouching`/`swimming`/`fall_flying`/`sleeping`), `profile` (→ `profile` component), `hide_description` (default false), `immovable` (default false).
- **Mooshroom**: `stew_effects` (brown variant), `Type` (`red`/`brown`).
- **Mule**: `ChestedHorse`, `Items` (15 slots).
- **Nautilus**: none.
- **Ocelot**: `Trusting`.
- **Panda**: `HiddenGene`, `MainGene`.
- **Parrot**: `Variant` (0–4: red/blue/green/cyan/gray).
- **Phantom**: `anchor_pos` (int array, circling center), `size` (0–64; +1 damage per size).
- **Pig**: `sound_variant`, `variant` (default `temperate`).
- **Piglin**: `Inventory` (≤8 stacks), `IsBaby`, `IsImmuneToZombification`, `TimeInOverworld` (>300 → zombified), `CannotHunt`.
- **Piglin Brute**: `IsImmuneToZombification`, `TimeInOverworld`.
- **Pillager**: `Inventory` (≤5 stacks).
- **Polar Bear**: none.
- **Pufferfish**: `FromBucket`, `PuffState` (0–2).
- **Rabbit**: `MoreCarrotTicks`, `RabbitType` (0 brown, 1 white, 2 black, 3 white-splotched, 4 gold, 5 salt, 99 killer).
- **Ravager**: `AttackTick`, `RoarTick`, `StunTick`.
- **Salmon**: `FromBucket`, `type` (`small`/`medium`/`large`).
- **Sheep**: `Color` (byte, dye index), `Sheared` (bool).
- **Shulker**: `AttachFace` (0–5), `Color` (0–16, default 16), `Peek` (byte, 0–100).
- **Silverfish**: none.
- **Skeleton**: `StrayConversionTime` (int; −1 when not converting; converts at ≤0).
- **Skeleton Horse**: `SkeletonTrap`, `SkeletonTrapTime` (removed at 18000).
- **Slime**: `Size` (0–126), `wasOnGround`.
- **Snow Golem**: `Pumpkin` (bool, default true).
- **Sniffer**: none.
- **Spider**: none.
- **Squid**: none.
- **Stray**: none.
- **Strider**: none.
- **Sulfur Cube**: `Size` (0–126), `pickup_timer` (default 0), `FromBucket`, `fuse` (default −1; <0 disables explosion), `wasOnGround`.
- **Tadpole**: `Age` (≥24000 → frog), `AgeLocked`, `FromBucket`.
- **Trader Llama**: `ChestedHorse`, `Strength` (1–5), `Variant` (0–3), `DespawnDelay` (default 47999), `Items`.
- **Tropical Fish**: `FromBucket`, `Variant` (int: low bytes = body size (0 large/1 small), pattern, color, pattern color; → `tropical_fish/base_color`/`pattern`/`pattern_color` components).
- **Turtle**: `has_egg`.
- **Vex**: `bound_pos` (int array, roaming center 15×11×15), `life_ticks` (damage countdown, 1 hunger damage at 0), `owner` (UUID of summoner).
- **Villager**: `FoodLevel` (byte, default 0; breed willingness >12 with inventory food), `Inventory` (≤8 stacks), `Offers` (trades; see below), `Gossips` (list: `Target` UUID, `Type` `major_negative`/`minor_negative`/`major_positive`/`minor_positive`/`trading`, `Value` >0, `LastGossipDecay`), `VillagerData` (compound: `level` default 1, `profession` default `minecraft:none`, `type` default `minecraft:plains`; → `villager/variant`), `AssignProfessionWhenSpawned`, `LastRestock`, `RestocksToday`, `Xp`.
- **Vindicator**: `Johnny` (bool).
- **Wandering Trader**: `DespawnDelay` (default 0; ≤0 = never despawns), `Inventory`, `Offers`, `wander_target` (int array).
- **Warden**: `anger` (compound: `suspects` list with `anger` 0–150 and `uuid`), `listener`.
- **Witch**: none.
- **Wither**: `Invul` (int; invulnerability ticks).
- **Wither Skeleton**: none.
- **Wolf**: `CollarColor` (byte, 0–15, default 14), `sound_variant` (default `classic`), `variant` (default `pale`).
- **Zombie**: none.
- **Zombie Horse**: none.
- **Zombie Nautilus**: `variant` (default `temperate`).
- **Zombified Piglin**: none.
- **Zombie Villager**: `ConversionPlayer` (UUID array), `ConversionTime` (int; −1 = not converting), `Offers`, `Gossips`, `VillagerData`.

### Trade offer (`Offers.Recipes` entry)

- `buy` (compound): first buy item; count = n + max(0,⌊ndm⌋) + s (d=demand, m=priceMultiplier, s=specialPrice); internal `id` (never `air`), `components`, `count` (>0, default 1).
- `buyB` (compound, default empty): second buy item.
- `sell` (compound, itemnoslot): sold item.
- `demand` (int, default 0; updated to d′=d+2u−m on restock).
- `maxUses` (int, default 4), `priceMultiplier` (float, default 0), `rewardExp` (bool, default true), `specialPrice` (int, default 0), `uses` (int, default 0), `xp` (int, default 1).

## Projectiles

Inheritance: entity → projectile → arrow / fireball / item projectile.

- **Arrow**: none.
- **Dragon Fireball**: none.
- **Egg**: none.
- **Ender Pearl**: none.
- **Experience Bottle**: none.
- **Fireball**: `ExplosionPower` (byte, default 1), `Item` (itemnoslot, default fire charge).
- **Fishing Bobber**: none.
- **Lingering Potion**: none.
- **Llama Spit**: none.
- **Splash Potion**: none.
- **Shulker Bullet**: `Dir` (int 0–5), `Steps` (int), `Target` (UUID array), `TXD`/`TYD`/`TZD` (doubles).
- **Small Fireball**: `Item`.
- **Snowball**: none.
- **Spectral Arrow**: `Duration` (int, default 200).
- **Trident**: `DealtDamage` (bool; enables Loyalty return).
- **Wind Charge**: none.
- **Wither Skull**: `dangerous` (bool; blue skull).

## Vehicles

- **Boat**: `leash` (int array fence position or compound with `UUID`).
- **Chest Boat**: `leash` (same as boat).
- **Minecart**: none.
- **Chest Minecart**: none.
- **Command Block Minecart**: `Command`, `CustomName`, `LastOutput` (when `TrackOutput`), `SuccessCount`, `TrackOutput` (default true), `UpdateLastExecution` (default true).
- **Furnace Minecart**: `Fuel` (short), `PushX`, `PushZ` (doubles).
- **Hopper Minecart**: `Enabled` (bool, default true).
- **Spawner Minecart**: none (spawner common tags).
- **TNT Minecart**: `explosion_power` (float, default 4), `explosion_speed_factor` (float, default 1; final power in [b, b+1.5sa)), `fuse` (int, default 80 when lit, −1 unlit).

## Other entities

### Area Effect Cloud
`Age`, `Duration` (default −1; −1 = never despawns), `Radius` (float 0–32), `RadiusOnUse`, `RadiusPerTick`, `WaitTime`, `potion_contents` (→ `potion_contents` component), `DurationOnUse`, `Owner`, `custom_color`, `custom_effects`, `custom_name`, `potion`, `potion_duration_scale`, `ReapplicationDelay`, `custom_particle`.

### Display entities (item/block/text)
- **billboard** (string, default `fixed`): `fixed`/`vertical`/`horizontal`/`center`
- **brightness** (compound: `block` 0–15, `sky` 0–15)
- **glow_color_override** (int, default −1; RGB)
- **height** / **width** (floats, default 0; culling box; 0 = never culled)
- **shadow_radius** (float, default 0), **shadow_strength** (float, default 1)
- **start_interpolation** (int, load-only), **interpolation_duration** (int, default 0), **teleport_duration** (int, default 0)
- **transformation** (16-float row-major matrix, or decomposition: `right_rotation`, `scale`, `left_rotation`, `translation`; all sub-tags required)
- **view_range** (float, default 1)
- Item display: **item**, **item_display** (`none`/`thirdperson_lefthand`/`thirdperson_righthand`/`firstperson_lefthand`/`firstperson_righthand`/`head`/`gui`/`ground`/`fixed`/`on_shelf`)
- Block display: **block_state**
- Text display: **alignment** (`center`/`left`/`right`), **background** (int ARGB, default 0x40000000; A<26 transparent), **default_background** (bool), **line_width** (int, default 200), **see_through** (bool), **shadow** (bool), **text** (text component), **text_opacity** (byte, default 255; values >127 as value−256; 4–25 invisible)

### End Crystal
`beam_target` (int array), `ShowBottom` (bool; false when placed by item).

### Evoker Fangs
`Owner` (UUID array), `Warmup` (int; −8 damages; removed after 22 ticks).

### Experience Orb
`Age` (short; removed at 6000), `Count` (int; remaining pickups), `Health` (short), `Value` (short).

### Eye of Ender
`Item` (itemnoslot; rendering + drop item).

### Falling Block
`BlockState` (block state; air removes the entity; default sand), `CancelDrop` (bool), `DropItem` (bool, default true), `HurtEntities` (bool, default true for `#anvil`), `TileEntityData` (block entity data without id/x/y/z), `Time` (int; removed at >600, or >100 outside build height), `FallHurtAmount` (default 0), `FallHurtMax` (default 40).

### Firework Rocket
`FireworksItem` (itemnoslot), `Life`, `LifeTime` (10(f+1)+rand(6)+rand(7)), `ShotAtAngle` (bool, default false).

### Interaction
`attack` (compound: `player` UUID, `timestamp` long), `interaction` (same), `height`/`width` (floats, default 1), `response` (bool, default false).

### Item (entity)
`Age` (short, default 0; −32768 = never despawns/merges), `Health` (short, default 5), `Item` (itemnoslot; air removes the entity), `Owner` (UUID array; only owner can pick up), `PickupDelay` (short, default 40; 32767/negative = never), `Thrower` (UUID array).

### Item Frame
`Facing` (byte 0–5), `Fixed` (bool), `Invisible` (bool), `Item`, `ItemDropChance` (float, default 1), `ItemRotation` (byte 0–7).

### Leash Knot
None. **Lightning Bolt**: none. **Marker**: none.

### Ominous Item Spawner
`item` (itemnoslot; projectiles spawn as projectiles), `spawn_item_after_ticks` (long).

### Painting
`facing` (byte 0–3: south/west/north/east), `variant` (string, default `alban`; → `painting/variant`).

### Primed TNT
`block_state` (display state, default TNT), `explosion_power` (float 0–128, default 4), `fuse` (short, default 80), `owner` (UUID array).

## Storage format

Entity data files are region files under `<dimension root>/entities` (e.g. `<save>/dimensions/minecraft/overworld/entities`). Per chunk: `DataVersion` (int; −1 if absent), `Position` (int array, chunk X/Z), `Entities` (list; passengers are stored within the root entity's `Passengers`, not separately).

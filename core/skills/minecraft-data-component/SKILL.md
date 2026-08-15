---

name: minecraft-data-component
description: "Data component formats: item stacks, block entities, entities; /give syntax."
whenToUse: "Use when writing or parsing data components for items, block entities, or entities (custom item properties, component patches, /give component syntax)."

---

# Data Components

This content applies only to Java Edition.

Data components (components for short) are structured data defining and storing item/entity properties. Because item stacks fully use this format, they are also called item stack components or item components.

## Behavior

Each component has its own encoding; invalid component data fails parsing immediately, invalidating the command or file. Unlike plain NBT tags (validated only when serialized to program objects), components are validated from the moment the game loads them — faster loading and earlier error detection.

Each component has two basic properties: whether it **persists** and whether it **syncs**. Non-persistent components are network-only, removed after computation or memory unload, and never saved to disk (forcing load/save fails). Unless stated otherwise, components below are persistent.

### Loading behavior

Item stacks, block entities, and entities can hold data components.

Block entities and entities still store data as unstructured NBT. To apply/read components, the game binds components to matching NBT tags; such components are called **implicit components**. The game applies them when placing blocks/entities with items and reads them via predicates or when breaking blocks.

Example: placing a named chest applies the item's `custom_name` component to the chest's block entity, which stores it as the `CustomName` block entity data; reading the `custom_name` component reads `CustomName` back.

### Item stacks

Item stacks fully use data components. Each item type defines default components computed in memory only (never saved). Saves store the item's **component patch** data: patched components override defaults; a `!`-prefixed component removes that item's default component.

Most components affect the item itself (stackability, damageability, etc.). An item cannot have both a `damage` component and a `max_stack_size` patch greater than 1 — an item cannot be both stackable and damageable.

Item stack data (compound):
- `id` (string, required): (namespace ID) the item type. If absent, the item becomes air when chunks load or items generate.
- `components` (compound): the item's component patch.
- `<component ID>` (any): one component and its data. The namespace may be omitted when setting; the game adds `minecraft:` on export.
- `!<component ID>` (compound): invalidates a component; content does not affect behavior.
- `count` (int): (0<value≤max stack size) stack count. Defaults to 1 when absent/invalid.

### Block entities

Block entities partially use data components: some stored as-is, some as implicit components in NBT. Removing components from block entities is currently unsupported. The `block_state` and `block_entity_data` components are never saved to block entities when placing.

Block entity data (compound):
- `x`, `y`, `z` (int, required): coordinates.
- `id` (string, required): (namespace ID) block entity type.
- `components` (compound): component data; extra non-inherited components from the placing item are copied here.
- `<component ID>` (any): one component and its data.

### Entities

Entity data components are all stored as implicit components in non-component NBT. If an item has `bucket_entity_data`, `entity_data`, and other entity components, application priority is `bucket_entity_data` → `entity_data` → other components.

## Data component types

Type annotations below: compound=compound tag/JSON object, list=list/JSON array, string, int, float, double, long, short, byte, int[]=int array, bool, any; text components (string/compound/list) are JSON text components.

Dye color enum (referenced repeatedly): `white`, `orange`, `magenta`, `light_blue`, `yellow`, `lime`, `pink`, `gray`, `light_gray`, `cyan`, `purple`, `blue`, `brown`, `green`, `red`, `black`.

Item templates, sound events, mob effects, block predicates, and game profiles follow formats on Minecraft Wiki / mc_java_sources; not repeated below.

### `attack_animation` (Java 26.3)
Animation used when attacking with this item:
- `type` (string, default `whack`): `whack` (default) or `stab` (spear thrust animation).
- `duration` (int, default 6): animation period in ticks.

### `attack_range`
Overrides the attack reach for mobs using this item to attack:
- `min_reach` (float, 0≤v≤64, default 0): minimum valid distance (from attacker eye along view direction to target hitbox).
- `max_reach` (float, 0≤v≤64, default 3): maximum valid distance.
- `min_creative_reach` (float, default 0), `max_creative_reach` (float, default 5): same for creative players.
- `hitbox_margin` (float, 0≤v≤1, default 0.3): expands the entity collision box to form the attack hitbox.
- `mob_factor` (float, 0≤v≤2, default 1.0): reach multiplier for non-player mobs.

### `attribute_modifiers`
Attribute modifiers applied while the item is in the specified slot; provides tooltip content:
- A modifier (compound):
  - `amount` (double, required)
  - `display` (compound): `type` (string, required): `default` / `hidden` / `override` (with required `value` text component).
  - `id` (string, required): (namespace ID) modifier ID.
  - `operation` (string, required): `add_value` (Op0), `add_multiplied_base` (Op1), `add_multiplied_total` (Op2).
  - `slot` (string, default `any`): slot group.
  - `type` (string, required): (namespace ID) attribute ID.

Example (stick that scales the holder to 5x while held):
```mcfunction
/give @s stick[attribute_modifiers=[{type:"scale",slot:"hand",id:"example:grow",amount:4,operation:"add_multiplied_base"}]]
```

### `banner_patterns`
Banner/shield patterns; shown in the tooltip in order:
- One layer (compound): `color` (string, required, dye enum), `pattern` (string/compound, required): pattern ID or inline definition.

### `base_color`
Shield base color (also affects shield name):
- `minecraft:base_color` (string, dye enum).

Example:
```mcfunction
/give @s shield[base_color=lime]
```

### `bees`
Bee data for beehives/bee nests:
- One bee (compound):
  - `entity_data` (string/compound): partial bee entity data; SNBT string form is loaded then saved as compound. `Air`, `Motion`, `Pos`, `Rotation`, `UUID` etc. are not saved/loaded.
  - `min_ticks_in_hive` (int, required), `ticks_in_hive` (int, required).

### `block_entity_data`
Block entity data applied when placing the block. Non-op players cannot set entity data when placing command blocks, lecterns, signs, hanging signs, spawners, or trial spawners with extra data (tooltip shows a safety warning).
- `minecraft:block_entity_data` (string/compound): NBT applied to the placed block entity; `id` (string, required) + block entity tags.

Example (spider spawner; requires op):
```mcfunction
/give @s spawner[block_entity_data={id:"mob_spawner",SpawnData:{entity:{id:"spider"}}}]
```

### `block_state`
Block states applied when placing; unspecified properties use defaults; invalid properties are ignored.
- `minecraft:block_state` (compound): `<block property>` (string): property value.

Example:
```mcfunction
/give @s bamboo_slab[block_state={type:"top"}]
```

### `block_transformer` (Java 26.3)
Block interaction transformation behavior (up to 200 effects):
- One effect (compound):
  - `block_state_provider` (compound, required): resulting block state.
  - `block_sound` (string/compound, default empty), `particle` (string, default `none`): `none`/`scrape`/`wax_on`/`wax_off`.
  - `disallowed_faces` (list, default empty): `up`/`down`/`north`/`south`/`west`/`east`.
  - `loot` (string): (namespace ID) loot table for drops.
  - `drop_strategy` (string, default `from_middle`): `clicked_face` or `from_middle`.
  - `update_from_neighbors` (bool, default `true`).
  - `transform_type` (string, default `single_block`): `single_block` or `copper_chest` (affects both parts of large copper chests).
  - `consume_on_use` (bool, default `true`), `item_damage_per_use` (int, ≥0, default 0).

### `blocks_attacks`
Blocking behavior while using the item:
- `block_delay_seconds` (float, ≥0, default 0)
- `block_sound` (string/compound)
- `bypassed_by` (string/list): damage types that bypass blocking.
- `damage_reductions` (list): per entry `base` (float, required) + `factor` (float, required); blocked damage = `clamp(base + factor * attack damage, 0, attack damage)`.
- `horizontal_blocking_angle` (float, >0, degrees, default 90).
- `type` (string/list): blockable damage types.
- `disable_cooldown_scale` (float, ≥0, default 1); 0 = cannot be disabled by attacks.
- `disabled_sound` (string/compound).
- `item_damage` (compound): `base` (default 0), `factor` (default 1), `threshold` (default 1): durability loss `floor(base + factor * attack damage)` when attack ≥ threshold.

Example (bow that blocks all frontal attacks and cannot be disabled):
```mcfunction
/give @s bow[blocks_attacks={disable_cooldown_scale:0}]
```

### `break_sound`
Sound played when item durability runs out:
```mcfunction
/give @a minecraft:golden_shovel[minecraft:break_sound={sound_id:block.amethyst_block.break}]
```

### `brewing_fuel` (Java 26.3)
Brewing stand fuel behavior: `uses` (float/string, required, number provider) and `speed_multiplier` (float/string, required).

### `bucket_entity_data`
Mob bucket data; set when capturing and applied when releasing (other NBT ignored): `Glowing`, `Health`, `Invulnerable`, `NoAI`, `NoGravity`, `Silent`; tadpoles additionally `Age`/`AgeLocked`; axolotls `Age`/`AgeLocked`/`HuntingCooldown`; sulfur cubes `age`/`age_locked` (unused by vanilla).

### `bundle_contents`
Bundle contents; released when the item entity is destroyed; shows the capacity bar:
- One item (string/compound, item template); later-added items are at the front.

Example:
```mcfunction
/give @s bundle[bundle_contents=[{id:"copper_ingot"},{id:"iron_ingot"},{id:"gold_ingot"}]]
```

### `can_break` / `can_place_on`
Adventure-mode block interaction restrictions (block predicates, see Wiki). With the component but unsatisfied/unspecified predicates, the tooltip block shows "Unknown" and the item interacts with any block. Block entity components are not tested. `can_break` also triggers redstone ore/dragon egg/note block start-mine effects. Lists cannot be empty; a single element is saved as compound.
- `minecraft:can_break` / `minecraft:can_place_on` (compound/list).

Examples:
```mcfunction
/give @s golden_pickaxe[can_break={blocks:['copper_ore','coal_ore','iron_ore','gold_ore','diamond_ore','emerald_ore']}]
/give @s stone[can_place_on={blocks:'sandstone'}]
```

### `charged_projectiles`
Crossbow loaded projectiles (≤1024); shown in tooltip; fireworks display "loaded with a firework rocket":
- One item (string/compound, item template).

### `compostable` (Java 26.3)
Composting behavior: `layers` (float/string, required, number provider).

### `consumable`
Whether the item has consume-use behavior and its effects. Cannot be consumed: boats, chest boats; minecarts (when placeable); written books; tridents; brushes; all buckets; sulfur cube buckets; bows, crossbows; fireworks; all spawn eggs.
- `animation` (string, default `eat`): `none`/`eat`/`drink`/`block`/`bow`/`brush`/`crossbow`/`spear`/`trident`/`spyglass`/`toot_horn`/`bundle`.
- `consume_seconds` (float, ≥0, default 1.6): 0 = instant use.
- `has_consume_particles` (bool, default `true`).
- `on_consume_effects` (list): effect entries with `type` (string, required): `apply_effects` (`effects` list required, `probability` default 1), `clear_all_effects`, `play_sound` (`sound` required), `remove_effects` (`effects` string/list required), `teleport_randomly` (`diameter` default 16, `sound` default `entity.generic.eat`).

Example (iron pickaxe eaten with 16-level Haste for 6000 ticks):
```mcfunction
/give @s minecraft:iron_pickaxe[minecraft:consumable={animation:"eat",consume_seconds:1.6,on_consume_effects:[{type:"apply_effects",effects:[{amplifier:15,duration:6000,id:"haste",show_icon:true,show_particles:false}]}],sound:"block.anvil.land"}]
```

### `container`
Container block inventory (shulker-box-style tooltip); released when destroyed:
- One slot (compound): `item` (string/compound, required, item template), `slot` (int, required, 0≤v≤255).

Example:
```mcfunction
/give @s barrel[container=[{slot:0,item:{id:apple}}]]
```

### `container_loot`
Loot container data: `loot_table` (string, required) + `seed` (long, default 0).

Example:
```mcfunction
/give @s chest[container_loot={loot_table:"chests/trial_chambers/reward_ominous"}]
```

### `cooking_fuel` (Java 26.3)
Furnace/blast furnace/smoker fuel: `burn_time` (float/string, required) + `speed_multiplier` (float/string, required).

### `custom_data`
Arbitrary custom data (string SNBT or compound).

### `custom_model_data`
Custom model data for item model mappings: `colors` (list), `flags` (list), `floats` (list), `strings` (list).

### `custom_name`
Custom name (default italic):
```mcfunction
/give @s stick[custom_name="Magic Wand"]
```

### `damage`
Item damage value (together with `max_damage`); absent = full durability:
```mcfunction
/give @s netherite_pickaxe[damage=50]
```

### `damage_resistant`
Damage types the item is immune to (item entity not destroyed; equipped item does not lose durability): `types` (string/list, required).

Example:
```mcfunction
/give @s minecraft:iron_chestplate[minecraft:damage_resistant={types:"#is_fire"}]
```

### `damage_type`
Damage type used when attacking with this item (defaults to `player_attack`/`mob_attack`):
```mcfunction
/give @s diamond_sword[damage_type=arrow]
```

### `death_protection`
Totem-like behavior: prevents death from non-`#bypasses_invulnerability` lethal damage, sets health to 1, consumes the item. `death_effects` (list): same effect types as `consumable`'s `on_consume_effects`.

### `debug_stick_state`
Debug stick data: `<block namespace ID>` (string): block → property key-value pairs.

### `dye`
Dye color making the item usable as dye in recipes, `#loom_dyes`, `#cat_collar_dyes`, `#wolf_collar_dyes`, sheep wool, and sign text coloring:
- `minecraft:dye` (string, dye enum).

### `dyed_color`
Dyed color (only the low 24 bits, RGB):
- `minecraft:dyed_color` (int/list).

### `enchantable`
Enchantability for the enchanting table:
- `value` (int, required, ≥1).

Example:
```mcfunction
/give @s shears[enchantable={value:2}]
```

### `enchantment_glint_override`
Whether the item shows the glint; overrides everything else:
- `minecraft:enchantment_glint_override` (bool).

### `enchantments` / `stored_enchantments`
`enchantments`: active enchantments (effects apply). `stored_enchantments`: inactive (enchanted books); when applied, limited to the max level obtainable in survival (e.g. Sharpness VI book applies Sharpness V).
- `minecraft:enchantments` / `minecraft:stored_enchantments` (compound): `<enchantment ID>` (int, 1≤v≤255): level.

Examples:
```mcfunction
/give @s wooden_sword[enchantments={sharpness:3,knockback:2}]
/give @s enchanted_book[stored_enchantments={efficiency:5,unbreaking:3}]
```

### `entity_data`
Entity data applied when the item spawns an entity (merged). Non-op players cannot set data for falling blocks, command block minecarts, or spawner minecarts with extra data:
- `minecraft:entity_data` (string/compound): `id` (string, required) + entity data tags.

Example:
```mcfunction
/give @s armor_stand[entity_data={id:"armor_stand",Small:1b}]
```

### `equippable`
Wearable equipment behavior:
- `allowed_entities` (string/list, default all)
- `asset_id` (string): equipment asset.
- `camera_overlay` (string): first-person overlay texture; overlays stack (main hand, off hand, head, chest, legs, feet order).
- `can_be_sheared` (bool, default `false`), `damage_on_hurt` (bool, default `true`)
- `equip_on_interact` (bool, default `false`), `equip_sound` (default `item.armor.equip_generic`)
- `dispensable` (bool, default `true`), `shearing_sound` (default `item.shears.snip`)
- `slot` (string, required), `swappable` (bool, default `true`).

### `firework_explosion`
Firework star data: `colors` (int[], RGB), `fade_colors` (int[]), `has_trail` (bool), `has_twinkle` (bool), `shape` (string, required): `small_ball`/`large_ball`/`star`/`creeper`/`burst`.

### `fireworks`
Firework rocket data: `flight_duration` (byte, gunpowder units), `explosions` (list, ≤256, same format as `firework_explosion`).

### `food`
Food properties (requires `consumable` to be edible): `can_always_eat` (bool, default false), `nutrition` (int, required, ≥0), `saturation` (float, required).

Example:
```mcfunction
/give @s sponge[food={can_always_eat:true,nutrition:3,saturation:1},consumable={}]
```

### `glider`
Empty tag: equipping allows gliding; consumes 1 durability per second while gliding:
```mcfunction
/give @s iron_chestplate[glider={}]
```

### `instrument`
Goat horn instrument (namespace ID or inline):
- `minecraft:instrument` (string/compound).

### `intangible_projectile`
Empty tag: when shot as an arrow, only creative players can pick it up (default for multishot extra arrows).

### `interact_animation` (Java 26.3)
Same format as `attack_animation` (`type`/`duration`).

### `item_model`
Item model mapping bound to the item (`assets/<ns>/items/<path>.json`); invalid → invisible:
- `minecraft:item_model` (string).

### `item_name`
Default item name (lowest priority, overridden by everything else; not shown in item frames):
- `minecraft:item_name` (text component).

### `jukebox_playable`
Jukebox song reference; presence allows inserting into a jukebox:
```mcfunction
/give @a minecraft:disc_fragment_5[minecraft:jukebox_playable=cat]
```

### `kinetic_weapon`
Charge attack behavior: `delay_ticks` (≥0, default 0), `forward_movement` (default 0), `damage_multiplier` (default 1), `sound`, `hit_sound`, `dismount_conditions` / `knockback_conditions` / `damage_conditions` (each: `max_duration_ticks` required, `min_speed` default 0, `min_relative_speed` default 0; non-player minimums at 20%), `contact_cooldown_ticks` (>0, default 10).

Example:
```mcfunction
/give @s minecraft:netherite_sword[minecraft:kinetic_weapon={dismount_conditions:{max_duration_ticks:0},knockback_conditions:{max_duration_ticks:2147483647},damage_conditions:{max_duration_ticks:2147483647}}]
```

### `lock`
Lockable container data (item stack predicate):
```mcfunction
/give @s chest[lock={components:{custom_name:"password"}}]
```

### `lodestone_tracker`
Lodestone compass data: `target` (compound: `dimension` string required, `pos` int[] required), `tracked` (bool, default true). With `tracked:false`, the compass keeps pointing even if the lodestone is destroyed:
```mcfunction
/give @s compass[lodestone_tracker={target:{pos:[I;1,2,3],dimension:"overworld"},tracked:false}]
```

### `lore`
Custom tooltip lines (≤256):
```mcfunction
/give @s stick[minecraft:lore=["Hello Minecraft", "Hello World"]]
```

### `map_color` (removed in Java 26.3)
Map texture color (int, RGB low 24 bits, default 4603950).

### `map_decorations`
Map icons (item data, not global map data): per icon (compound): `rotation` (float, required, every 22.5° visible; 0 appears upside down), `type` (string, required, icon type ID), `x`/`z` (double, required; out-of-range player icons become `player_off_limits`/`player_off_map` or are removed).

### `map_id`
Map ID: items with this component read/expand/copy/lock the map; tooltip shows scale info:
- `minecraft:map_id` (int).

### `max_damage`
Max durability (with `damage`): `minecraft:max_damage` (int, >0):
```mcfunction
/give @s golden_sword[max_damage=999]
```

### `max_stack_size`
Max stack size (default 1): `minecraft:max_stack_size` (int, 0≤v≤99):
```mcfunction
/give @s snowball[max_stack_size=99] 99
```

### `minimum_attack_charge`
Minimum attack cooldown completion required to attack (default 0; affects `post_piercing_attack` trigger interval when >0):
- `minecraft:minimum_attack_charge` (float, 0≤v≤1).

### `mob_visibility` (Java 26.3)
Equipped effect on mob detection radius: `targeting_entity_types` (string/list, required), `visibility` (float, required, 0.0–10.0 multiplier; final radius ≥2 and ≤10x original).

### `note_block_sound`
Sound played when the player head is placed on a note block:
```mcfunction
/give @s player_head[note_block_sound="entity.player.levelup"]
```

### `ominous_bottle_amplifier`
Bad Omen amplifier after consuming (requires `consumable`): int, 0≤v≤4.

### `piercing_weapon`
Spear thrust attack behavior (also disables block breaking while held; enables `post_piercing_attack`): `sound`, `hit_sound`, `deals_knockback` (default true), `dismounts` (default false).

### `pot_decorations`
Decorated pot sherds (back/left/right/front; default brick each). List form (4 elements) or compound form (`back`/`left`/`right`/`front` item templates). Faces without `provides_pottery_pattern` render plain.

### `potion_contents`
Potion + custom effects; affects name/texture/tooltip (requires `consumable` to drink): `custom_color` (int), `custom_effects` (list), `custom_name` (string), `potion` (string). String form = only `potion`.

Example:
```mcfunction
/give @s potion[potion_contents={custom_color:8388863,custom_effects:[{amplifier:122,duration:1102,id:"glowing"}]}]
```

### `potion_duration_scale`
Duration multiplier for `potion_contents` effects (default 1): float ≥0.

### `profile`
Game profile data (skins): `name` resolves the profile live (tooltip shows "Live"); `id` (UUID) takes priority; `properties` pins a static profile. The `textures` property (Base64-decoded): `profileId`, `profileName`, `signatureRequired`, `textures` (`CAPE`/`SKIN` with `url` + `metadata.model` = `slim`), `timestamp`. Only `name` affects the player head's item name.

### `provides_banner_patterns`
Loom banner pattern slot behavior: pattern ID, tag, or list.

### `provides_pottery_pattern` (Java 26.3)
Pottery pattern for decorated pot rendering: `minecraft:provides_pottery_pattern` (string).

### `provides_trim_material`
Smithing trim material provided (namespace ID or inline).

### `rarity`
Base rarity: `common`/`uncommon`/`rare`/`epic`.

### `recipes`
Knowledge book recipes: list of recipe IDs.

### `repair_cost`
Cumulative anvil penalty:
```mcfunction
/give @s netherite_sword[repair_cost=30]
```

### `repairable`
Anvil repair materials (items are always repairable by merging): `items` (string/list, required: tag/ID/list):
```mcfunction
/give @s netherite_sword[repairable={items:"oak_planks"}]
```

### `sign_text_front` / `sign_text_back` (Java 26.3)
Sign/hanging sign text: `messages` (list, required, 4 text components), `filtered_messages` (list), `color` (string, default `black`), `has_glowing_text` (bool, default false).

### `sulfur_cube_content`
Absorbed item of a sulfur cube: string/compound item template.

### `suspicious_stew_effects`
Suspicious stew effects (requires `consumable`): per entry `duration` (int, default 160) + `id` (string, required).

### `swing_animation` (removed in Java 26.3)
`type` (`none`/`whack`/`stab`) + `duration` (default 6).

### `tool`
Mining tool behavior: `can_destroy_blocks_in_creative` (bool, default true), `damage_per_block` (int, ≥0, default 1), `default_mining_speed` (float, ≥0, default 1), `rules` (list, required): per rule `blocks` (string/list, required), `correct_for_drops` (bool), `speed` (float).

Example:
```mcfunction
/give @s wooden_shovel[tool={rules:[{blocks:["stone"],correct_for_drops:True}]}]
```

### `tooltip_display`
Tooltip visibility: `hide_tooltip` (bool, default false), `hidden_components` (list of component IDs):
```mcfunction
/give @s golden_axe[tooltip_display={hide_tooltip:true}]
```

### `tooltip_style`
Tooltip appearance: `<ns>:tooltip/<path>_background` and `_frame` sprites under `assets/<ns>/textures/gui/sprites/tooltip/`.

### `trim`
Armor trim: `material` (string/compound, required), `pattern` (string/compound, required).

### `unbreakable`
Empty tag: no durability, cannot break:
```mcfunction
/give @s diamond_pickaxe[unbreakable={}]
```

### `use_cooldown`
Use cooldown on a cooldown group: `cooldown_group` (string, default = item ID), `seconds` (float, required, >0):
```mcfunction
/give @s snowball[use_cooldown={seconds:1}] 16
```

### `use_effects`
Use behavior: `can_sprint` (bool, default false), `interact_vibrations` (bool, default true), `speed_multiplier` (float, 0≤v≤1, default 0.2).

### `use_remainder`
Item returned after consumption (drops if inventory full):
```mcfunction
/give @s snowball[use_remainder={id:"snowball"}] 16
```

### `villager_food` (Java 26.3)
Villager food: `nutrition` (int, required, ≥0).

### `waxed` (Java 26.3)
Empty tag: item is waxed.

### `weapon`
Weapon data (use stats increment on attack): `disable_blocking_for_seconds` (float, ≥0, default 0), `item_damage_per_attack` (int, ≥0, default 1):
```mcfunction
/give @s netherite_sword[weapon={disable_blocking_for_seconds:60,item_damage_per_attack:0}]
```

### `writable_book_content`
Book and quill data (≤100 pages): each page a string (≤1024 chars) or compound (`filtered`, `raw` required, ≤1024). Priority below `written_book_content`.

### `written_book_content`
Written book data: `author` (string, required), `generation` (int, default 0: original/copy of original/copy of copy/tattered), `pages` (list: text components or compounds with `filtered`/`raw`), `resolved` (bool, default false), `title` (string/compound, required, ≤32 chars, with optional `filtered`/`raw`).

## Entity variant components

These components can be entity components controlling entity variants; items that spawn entities (spawn eggs, eggs, paintings) produce the specified variant. Format: `minecraft:<path>` (string, namespace ID); fixed values where noted:

- `axolotl/variant`: `lucy`/`wild`/`gold`/`cyan`/`blue`
- `cat/collar`: dye enum
- `cat/sound_variant`, `cat/variant`, `chicken/sound_variant`, `chicken/variant`, `cow/sound_variant`, `cow/variant`: namespace IDs
- `cushion/color` (Java 26.3): dye enum
- `fox/variant`: `red`/`snow`
- `frog/variant`: namespace ID
- `horse/variant`: `white`/`creamy`/`chestnut`/`brown`/`black`/`gray`/`dark_brown`
- `llama/variant`: `creamy`/`white`/`brown`/`gray`
- `mooshroom/variant`: `red`/`brown`
- `painting/variant`: namespace ID
- `parrot/variant`: `red_blue`/`blue`/`green`/`yellow_blue`/`gray`
- `pig/sound_variant`, `pig/variant`: namespace IDs
- `rabbit/variant`: `brown`/`white`/`black`/`white_splotched`/`gold`/`salt`/`evil`
- `salmon/size`: `small`/`medium`/`large`
- `sheep/color`: dye enum
- `shulker/color`: dye enum (default when absent)
- `tropical_fish/base_color`: dye enum
- `tropical_fish/pattern`: `kob`/`sunstreak`/`snooper`/`dasher`/`brinely`/`spotty`/`flopper`/`stripey`/`glitter`/`blockfish`/`betty`/`clayfish`
- `tropical_fish/pattern_color`: dye enum
- `villager/variant`: `desert`/`jungle`/`plains`/`savanna`/`snow`/`swamp`/`taiga`
- `wolf/collar`: dye enum
- `wolf/sound_variant`, `wolf/variant`: namespace IDs
- `zombie_nautilus/variant`: namespace ID

## Temporary components (network-only, never saved/loaded)

- `additional_trade_cost` (int): added to villager buy price when the trade offer generates; removed immediately.
- `creative_slot_lock`: empty tag; item cannot be interacted with in the creative inventory.
- `map_post_processing` (int): syncs map scale/lock info on cartography/table output slots; 0 adds the "Locked" line to `map_id`, 1 shows "scale+1".

## Removed components

- `fire_resistant` → replaced by `damage_resistant`. Empty tag.
- `hide_additional_tooltip` → replaced by `tooltip_display`. Empty tag.
- `hide_tooltip` → replaced by `tooltip_display`. Empty tag.

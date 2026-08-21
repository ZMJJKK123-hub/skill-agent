---

name: minecraft-game-event
description: "Minecraft Game Event 游戏事件：Game Events and Vibrations 游戏事件与振动（事件记录位置+上下文实体/方块、创建振动 源为事件位置、投射物源实体为射击者、振动频率 红石信号强度）、Monitoring 监测（Non-vibration systems 非振动系统：sculk catalysts 检测 entity_die 8/10方块扩散sculk、allays 检测 jukebox_play/jukebox_stop_play 10方块跳舞；Vibration system 振动系统：保存到区块数据 渲染振动粒子、vibration listeners 振动监听器 检测半径+可听事件列表、Receivers 接收器：sculk sensor 半径8 几乎所有事件 步入强制接收 step/sculk_patch 忽略自身 block_place/block_destroy、calibrated sculk sensor 半径16 红石输入限制、sculk shrieker 半径8 监听 sculk_sensor_tendrils_clicking、allay 半径16 监听 note_block_play、warden 半径16 几乎所有事件）、Detection Rules 检测规则（源在监听器半径内、事件可听、源实体非Warden/非旁观者/非潜行 hit_ground/projectile_shoot/step/swim/item_interact_start/item_interact_finish/非含羊毛地毯物品实体、源方块非羊毛地毯、无羊毛阻挡线）、Vibration Selection 振动选择（最近距离优先 然后最高频率、延迟 floor(distance) 刻）、Game Event List 事件列表（block_activate/block_attach/block_change/block_close/block_deactivate/block_destroy/block_detach/block_open/block_place/bounce/container_close/container_open/dispense_fail/drink/eat/elytra_glide/entity_act/entity_action/entity_damage/entity_die/entity_dismount/entity_interact/entity_mount/entity_move/entity_place/entity_roar/equip/explode/flap/fluid_pickup/fluid_place/hit_ground/instrument_play/item_interact_finish/item_interact_start/jukebox_play/jukebox_stop_play/lightning_strike/multi_item_swap/note_block_play/piston_contract/piston_extend/prime_fuse/projectile_land/projectile_shoot/sculk_patch/sculk_sensor_tendrils_clicking/shear/shriek/single_item_swap/splash/step/swim/teleport/unequip）。"
whenToUse: "Use when working with game events, sculk sensors, or vibration-based mechanics."

---

# Game Event

Game events are produced by world activities; their vibrations can mostly be detected by sculk sensors.

## Game Events and Vibrations

A game event records its position plus context entity (source entity) and context block (source block) — either may be absent (e.g. doors opened by redstone have no context entity). Each event creates a **vibration** with the event position as the source; if the source entity is a projectile, the vibration's source entity becomes the projectile's shooter.

Every game event has a **vibration frequency**, visible as the redstone signal strength of a sculk sensor hooked to a comparator (the table below gives the frequencies).

## Monitoring

- **Non-vibration systems** (not saved to chunks; lost on unload): sculk catalysts detect `entity_die` within 8/10 blocks to spread sculk; allays detect `jukebox_play` / `jukebox_stop_play` within 10 blocks (Java) for dancing.
- **Vibration system** (saved to chunk data; renders vibration particles): managed by **vibration listeners**, each with a detection radius and listenable game events; receivers add further restrictions. Receivers:
  - **Sculk sensor** — radius 8, almost all events. Stepping on it (by a non-Warden entity) forces it to receive the `step`/`sculk_patch` event; it ignores `block_place`/`block_destroy` of itself.
  - **Calibrated sculk sensor** — radius 16, restricted by its redstone input signal.
  - **Sculk shrieker** — radius 8, listens to `sculk_sensor_tendrils_clicking`.
  - **Allay** — radius 16, listens to `note_block_play`.
  - **Warden** — radius 16, almost all events.

A vibration is detectable when: the source is within the listener's radius; the event is listenable; the source entity is not a Warden, not a spectator player, not sneaking (for `hit_ground`, `projectile_shoot`, `step`, `swim`, `item_interact_start`, `item_interact_finish`), and not an item entity containing wool/carpet; the source block is not wool/carpet; and no wool blocks the line between source and listener.

When a listener receives, it records the game time, source, distance, event, and source entity. One vibration per listener; simultaneous candidates are resolved by a vibration selector: nearest distance first, then highest frequency. The received vibration has a delay of ⌊distance⌋ ticks before taking effect, matching the particle travel time.

## Game Event List

(Java: block sources at block center; entity sources usually at the feet. Bedrock: sources always at block coordinates of the entity's current block — head block while eating, foot block while walking. Contexts may be absent when executed by dispensers/redstone or wind bursts. Frequencies were fully reset in 23w12a.)

- `block_activate` (10) — block activation.
- `block_attach` (10) — block attachment.
- `block_change` (11) — block change (waxing/unwaxing a large copper chest fires once per half).
- `block_close` (9) — block closing.
- `block_deactivate` (9) — block deactivation.
- `block_destroy` (12) — block destroyed (not by water flow; support-requiring blocks like redstone wire destroyed by support removal don't fire).
- `block_detach` (9) — block detachment.
- `block_open` (10) — block opening.
- `block_place` (13) — block placed.
- `bounce` (2) — entity collides with a block/collidable entity without losing all velocity.
- `container_close` (9) / `container_open` (10) — container closing/opening.
- `dispense_fail` (10, Bedrock) — dispenser failure.
- `drink` (8) — drinking (any item with a `consumable` component using the drink animation, Java).
- `eat` (8) — eating (consumable with non-drink animation).
- `elytra_glide` (4) — gliding.
- `entity_act` (6, Bedrock) / `entity_action` (6, Java) — mob actions.
- `entity_damage` (7) — entity damaged.
- `entity_die` (15) — entity death.
- `entity_dismount` (5) — dismounting.
- `entity_interact` (6) — player-entity interactions (allay item give/take, feeding, mob buckets, iron golem repair, golden apples on zombie villagers, trading, shearing, equipping, mounting, commanding wolves/cats, name tags).
- `entity_mount` (6) — mounting.
- `entity_move` (1, Bedrock) — entity movement on a surface.
- `entity_place` (14) — entity placed.
- `entity_roar` (6, Bedrock) — ravager roar.
- `equip` (5) — equipping (Java: only slots replaced by items with the `equippable` component; other equips fire only unequip; includes villager trade display, witch potions, wandering trader potions/milk, allay held items, panda bamboo/cake, fox held items, piglin examining, dolphin pushing items; Bedrock: also fires on retrieving).
- `explode` (15) — explosion.
- `flap` (1) — airborne movement (chickens, allays, parrots, phantoms, the Ender Dragon, bees, bats, vexes).
- `fluid_pickup` (12) — fluid collected.
- `fluid_place` (13) — fluid placed.
- `hit_ground` (2) — landing on a surface.
- `instrument_play` (3, Java) — goat horn playing.
- `item_interact_finish` (3) — finishing item use (depends on the `use_effects` component; tridents don't; totem `death_protection` also fires it).
- `item_interact_start` (3) — starting item use (same `use_effects` rule).
- `jukebox_play` (—, Java) — jukebox playing (fires every tick).
- `jukebox_stop_play` (—, Java) — jukebox stops.
- `lightning_strike` (14) — lightning strike.
- `multi_item_swap` (6, Bedrock) — swapping inventory items with a shelf.
- `note_block_play` (10) — note block plays.
- `piston_contract` (9, Bedrock) — piston retracts.
- `piston_extend` (10, Bedrock) — piston extends.
- `prime_fuse` (10) — priming (TNT).
- `projectile_land` (2) — projectile hits something.
- `projectile_shoot` (3) — projectile fired.
- `sculk_patch` (1, Bedrock) — stepping on a sculk sensor (default only detectable by the stepped sensor).
- `sculk_sensor_tendrils_clicking` (—) — sensor activation (default only by shriekers).
- `shear` (6) — shearing.
- `shriek` (—) — shrieker activation (Java default only by Wardens).
- `single_item_swap` (3, Bedrock) — single item swap with a shelf.
- `splash` (2) — moving from air into water.
- `step` (1, Java) — stepping.
- `swim` (1) — swimming.
- `teleport` (14) — teleporting (`/tp` and ender pearls do NOT fire it).
- `unequip` (4) — unequipping (Java: same detection as `equip`; Bedrock: armor only).

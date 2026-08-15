---

name: minecraft-entity-type
description: "Entities — behavior, riding, movement physics (Motion, drag, terminal speed), NBT."
whenToUse: "Use when working with entities in general — spawning, riding, movement mechanics, or common entity NBT."

---

# Entity

Entities are all dynamic, moving objects in Minecraft. This page covers general behavior and movement physics (not block entities).

## General Behavior

Most entities: occupy a fixed-size 3D bounding box (not rotated visually); take damage or vanish when on fire (showing a fire effect); can have status effects (mostly from potions); can be renamed with name tags. Entities are lit by the light level at their position (e.g. a minecart jammed diagonally into solid blocks turns black).

### Details

- Item frames, glow item frames, paintings, leash knots, and saddles (carpets?) are entities but align to the block grid and cannot move.
- **Boats and minecarts** regenerate health over time — they can only be destroyed by rapid attacks, not by evenly spaced bare-hand hits. Wobble indicates remaining health.
- **Falling blocks** (sand, gravel, suspicious sand/gravel, red sand, pointed dripstone, sulfur spikes, scaffolding, anvils, dragon egg, concrete powder, snow): when support disappears they become entities falling until landing on support; they then convert back to the block in the nearest grid cell — if that cell is occupied by a non-solid block (torch, slab), they drop as items. Trajectories can be altered by explosions, slime-block pistons, bubble columns, fishing rods (dripstone only), commands, or third-party tools. They despawn if they haven't settled after 600 ticks (30 s), or after 100 ticks (5 s) outside the build height — normally dropping as items. During world generation, sand above newly carved caves floats until a block update collapses it.
- **Interaction**: some entities (baby villagers, tamed wolves, zombies, minecarts, boats) do not block the interaction with the item in hand — e.g. a water bucket used on a tamed wolf makes it sit/stand and also pours the water.
- **Riding**: lower/outer entities collide and control movement. Common combinations: boats/minecarts with passengers; saddled pigs/horses/donkeys/mules/zombie horses/skeleton horses/camels; saddled striders (ridden by players or zombified piglins); llamas, parrots on shoulders; chicken jockeys; spider jockeys (skeletons on spiders); skeleton trap horses; ravagers with illagers. `/ride` mounts entities; `/summon` can nest passengers (e.g. a spider with a `Passengers:[{id:"skeleton",...}]` skeleton = spider jockey). The topmost entity of a stack cannot teleport (it gets teleported back onto its mount; smooth movement may show it at several intermediate positions).

## Movement

All entities (except marker entities in Java) have velocity, position, and orientation. Most non-projectile entities' hitboxes cannot pass through solid blocks (projectile trajectories don't either, but their hitbox may partially clip). Most entities block block placement except items and XP orbs, which yield.

### Motion Data (Java)

- `Motion` (required) — `[x, y, z]` velocity in meters/tick; components must be in −10..10 (out of range resets to 0 on load; NaN loads normally).
- `Pos` (required) — `[x, y, z]` coordinates; X/Z in −30000512..30000512, Y in −20000000..20000000 (out of range is forced back; NaN causes a load error).

### Physics

Movement per tick is determined by three data: acceleration `a` (m/tick²; the Y axis is gravity), "drag" `f` (velocity multiplier, may differ horizontally/vertically), and position `s`. Derived: velocity `v`, terminal velocity `v∞`, horizontal max-displacement multiplier `k∞` (max distance = k∞ × v0).

- **Acceleration**: horizontal acceleration is 0 for non-mobs; the player's is `a = a1·a2·a3 + a4` with a1 = 0.1 (ground) / 0.02 (air), a2 = 1 (walking) / 1.3 (sprinting), a3 = 0.98 (one key) / 1 (two keys), a4 = 0.2 (sprinting jump straight) / 0.
- **Drag**: for mobs on the ground with block drag coefficient FB, mob friction F, air resistance A: vertical fv = 1 − 0.09A, horizontal fh = (1−0.09A)(1−(1−FB)·F). In air, FB = 0. Non-mobs use fixed values (see the wiki table).
- **Velocity** (no collision), order-dependent:
  - drag then acceleration: vt = v(t−1)·f + a, closed form vt = (v0 − a/(1−f))·fᵗ + a/(1−f).
  - acceleration then drag: vt = (v(t−1) + a)·f, closed form vt = (v0 − af/(1−f))·fᵗ + af/(1−f).
- **Jump**: initial vertical velocity v0 = p·j·f + vl + vs where j = jump strength, f = jump multiplier, p = charge factor (rabbits 50/21; horses/mules/donkeys/llamas from the jump charge bar 0–1; others 1); Jump Boost l adds vl = 0.1·l; magma cube of size s adds vs = 0.1·s.
- **Bounciness**: non-mobs always bounce 0 and block elasticity is reduced by 20%; mobs use the `bounciness` attribute.
- **Position** formulas: the six order permutations ("position/drag/acceleration" etc.) with recurrence/closed forms and inverse-time solutions (using the Lambert W function for the inverse) — see the Minecraft Wiki "Entity" page for the full formulas and the per-entity table (gravity, drag, order, float precision, terminal velocity, max horizontal distance). Notable values: minecart X/Z max speed 0.4 (reset before position update); projectiles in Bedrock cannot move more than 16 blocks/tick; thrown-item order changed in 1.21.2.
- **Terminal velocity**: drag-first: v∞ = −a/(1−f); acceleration-first: v∞ = −af/(1−f).
- **Horizontal max displacement multiplier**: position-before-drag: k∞ = 1/(1−f); drag-before-position: k∞ = f/(1−f).

## Entity List

The complete list of all entities with their bounding box sizes: see the Minecraft Wiki "Entity" page (sizes in meters; the hitbox does not rotate with the visual). Entity IDs: see the entity-type tag lists and entity data format skill.

## Entity Type Tags

Entities are categorized into entity type tags usable by entity predicates and target selectors; see the java-tags skill and `data/minecraft/tags/entity_type/` in the source.

## Common Entity NBT (Java)

- `id` (required for persistence only; not readable/writable via `/data`) — entity type namespace ID. Present when saved to chunks, structure templates, beehives, or as passengers.
- `Air` (−20..max air) — remaining air; +4/tick in breathable environments, decreases in suffocating ones; at −20 the entity takes damage and resets to 0 (loop). Absent = max.
- `CustomName` (text component; → `custom_name` component) — shown in death messages, villager trades, and above the entity when pointed at.
- `CustomNameVisible` (default false) — always render the name above the entity.
- `data` — arbitrary NBT (string form load-only; → `custom_data` component).
- `fall_distance` — fallen distance (fall damage).
- `Fire` — positive = ticks until fire goes out; negative = ticks the entity can stand in fire (players −20, others −1). Absent = 0.
- `Glowing` (default false) — glowing outline.
- `HasVisualFire` (default false) — render as on fire without actually being on fire.
- `Invulnerable` (default false) — resists almost all damage (only creative players and `#bypasses_invulnerability` damage affect it).
- `invulnerable_time` (default 0; not stored when ≤ 0) — remaining ticks of damage resistance.
- `Motion` — see above.
- `NoGravity` (default false).
- `OnGround` (default false).
- `Passengers` — recursive passenger data; only settable via `/summon`, spawners, and trial spawner spawn data.
- `PortalCooldown` — ticks until the entity can use a nether portal again (−1/tick while not touching a portal).
- `Pos` — see above.
- `Rotation` — `[yaw, pitch]` (yaw 0 = +Z (north), negative pitch = looking up).
- `Silent`, `Tags` (list of strings), `Team` (team name), `TicksFrozen`/`FrozenTicks` (powder snow), `UUID` (int array, not persisted in saves), `Vehicle`, `CustomName`... — the full common-tag list is in the entity-data-format skill.

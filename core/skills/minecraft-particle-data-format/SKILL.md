---

name: minecraft-particle-data-format
description: "Minecraft Particle Data Format 粒子数据格式：Format 格式（JSON type 粒子类型+选项、SNBT /particle 命令 JSON 生物群系/附魔文件）、Common Structures 常见结构（RGB color int Red<<16+Green<<8+Blue 或 float[3] [0,1]、ARGB color int Alpha<<24+Red<<16+Green<<8+Blue 或 float[4] [0,1]）、Particle Options 粒子选项（Block block/block_marker/dust_pillar block_state 方块ID或完整方块状态、Dust dust color RGB+scale 0.01-4.0 生命周期乘数、Dust color transition dust_color_transition from_color+to_color+scale、Color entity_effect color ARGB、Item item item模板物品、Power power 初始速度乘数、Sculk charge sculk_charge roll 弧度显示角度、Shriek shriek delay 刻延迟、Spell spell/instant_effect/entity_effect color RGB+power、Vibration vibration destination 位置源 block类型+pos+arrival_in_ticks 行程时间、Trail trail color ARGB+duration+target 目标坐标 轨迹、Geyser plume geyser_plume water_blocks 生命周期=water_blocks×25刻 上升高度=water_blocks×5方块、Geyser base geyser_base water_blocks 尺寸=3.0+water_blocks×0.125 基础速度=water_blocks×0.25 burst_impulse_base 速度增量）。"
whenToUse: "Use when specifying particles in commands (/particle), biomes, or enchantments."

---

# Particle Data Format

The data format of particles. Java Edition only. SNBT in `/particle` commands; JSON in biome/enchantment files.

## Format

```json
{ "type": "<particle type>", ... }
```

Particles are either **simple** (type only) or **with particle options** (must specify the option fields or parsing fails).

## Common Structures

- **RGB color** — int (Red<<16 + Green<<8 + Blue; top 8 bits ignored) or list of 3 floats [0,1] (R,G,B). Out-of-range lists are undefined behavior.
- **ARGB color** — int (Alpha<<24 + Red<<16 + Green<<8 + Blue) or list of 4 floats [0,1] (R,G,B,A).

## Particle Options

- **Block** (`block`, `block_marker`, `dust_pillar`) — `block_state` (block ID string with default properties, or a full `{Name, Properties}` block state). Example: `/particle block{block_state:"minecraft:diamond_block"}`; `{block_state:{Name:"minecraft:grass_block",Properties:{snowy:"true"}}}`.
- **Dust** (`dust`) — `color` (RGB) + `scale` (0.01–4.0; also a lifetime multiplier: lifetime = random 8–40 ticks × scale, min 1). Example: `dust{color:[0.0,0.0,1.0],scale:1.0}`.
- **Dust color transition** (`dust_color_transition`) — `from_color`, `to_color` (RGB), `scale` (same scaling).
- **Color** (`entity_effect`) — `color` (ARGB). Examples: `entity_effect{color:[1,1,1,1]}`, `entity_effect{color:-1}`, `entity_effect{color:4294967295L}`.
- **Item** (`item`) — `item` (item template). Examples: `item{item:"minecraft:apple"}`, `item{item:{id:"minecraft:apple"}}`.
- **Power** — `power` (default 1): initial velocity multiplier after the random base.
- **Sculk charge** (`sculk_charge`) — `roll` (radians; display angle relative to the camera). Example: `sculk_charge{roll:3.14}`.
- **Shriek** (`shriek`) — `delay` (ticks until shown). Example: `shriek{delay:100}`.
- **Spell** (`spell`, `instant_effect`, `entity_effect`...) — `color` (RGB, default 0xFFFFFF) + `power` (default 1).
- **Vibration** (`vibration`) — `destination` (position source; only `block` type allowed here: `{type:"block",pos:[x,y,z]}`), `arrival_in_ticks` (travel time = lifetime). Example: `vibration{destination:{type:"block",pos:[5,64,0]},arrival_in_ticks:200}` moves to 5.5 64.5 0.5.
- **Trail** (`trail`) — `color` (ARGB), `duration` (ticks), `target` ([x,y,z] destination), leaving a trail.
- **Geyser plume** (`geyser_plume`) — `water_blocks`: lifetime = water_blocks × 25 ticks, rise height = water_blocks × 5 blocks; `geyser` passes the value to child particles.
- **Geyser base** (`geyser_base`) — `water_blocks` (size = 3.0 + water_blocks × 0.125; base velocity = water_blocks × 0.25), `burst_impulse_base` (velocity increment added to the base).

---

name: minecraft-environment-attributes
description: "Environment attributes — sources, modifiers, interpolation, full attribute list."
whenToUse: "Use when defining environment attributes in dimension types, biomes, or timelines (fog, sky, clouds, music, gameplay rules)."

---

# Environment Attributes

Environment attributes control visual effects and gameplay mechanics per environment. Java Edition only (flagged for 26.3 updates).

## Sources and Modifiers

There are four environment attribute sources, applied in order: **dimension**, **biome**, **timeline**, and **weather**. Dimensions and weather provide global attributes; timelines provide time-based ones; biomes provide position-based ones.

When several sources provide the same attribute, **modifiers** decide how they combine. All attributes support `override` (only the last-applied value counts). Example: Overworld dimension sets sky color blue, plains biome sets green → green in plains, blue elsewhere.

## Interpolation

Interpolatable attributes transition smoothly when moving between different values. Interpolation applies in: camera-position attributes (biomes within a 10-block radius contribute by occupied volume) and timeline attribute tracks (interpolated by track and time). Example: cloud height 100 (dimension) vs 1700 (plains) → smooth blend at the border.

## Technical Details

Three independent systems:

- **Server world environment attributes** — the normal system (dimension/biome/timeline/weather).
- **Client world environment attributes** — same sources; plus with lightning (when "hide sky flash" off, within 2 ticks): `visual/sky_color` linearly interpolates toward `#CCF0FF` with factor 0.22, and `visual/sky_light_factor` becomes 1.0.
- **Environment attributes in unfinished chunks** — empty before 26.3; from 26.3 only dimension and biome sources.

## Definition Format

Two forms:

- **Attribute map** — in the `attributes` field of dimension type and biome definitions: `{ <attribute ID>: value }` (implicit `override`) or `{ <attribute ID>: {modifier: <type>, argument: ...} }`.
- **Attribute track** — in timeline definition files (see the time-line skill).

Weather attributes are hardcoded and unmodifiable (see Weather below).

## Common Types

- **RGB color** — string `#rrggbb` (case-insensitive, exactly 6 hex chars after `#`), int (Red<<16 + Green<<8 + Blue; top 8 bits ignored), or list of 3 floats [0,1].
- **ARGB color** — string `#aarrggbb` (8 chars), int (Alpha<<24 + Red<<16 + Green<<8 + Blue), or list of 4 floats [0,1] (R,G,B,A).

## Attribute List

### Visual

- `visual/fog_color` — fog color (also affected by time of day, effects). RGB, default `#000000`. Interpolatable at camera.
- `visual/fog_start_distance` — fog start distance in blocks (negative = fog starts behind the camera). Float, default 0.0.
- `visual/fog_end_distance` — fog end (view) distance; final value never < 96 blocks. Float > 0, default 1024.0.
- `visual/sky_fog_end_distance` — sky fog end distance. Float > 0, default 512.0.
- `visual/cloud_fog_end_distance` — cloud fog end distance. Float > 0, default 2048.0.
- `visual/water_fog_color` — underwater fog color. RGB, default `#050533`.
- `visual/water_fog_start_distance` — Float, default −8.0.
- `visual/water_fog_end_distance` — Float > 0, default 96.0 (also depends on time underwater).
- `visual/sky_color` — sky color. RGB, default `#000000`.
- `visual/sunrise_sunset_color` — sunrise/sunset tint (rendered only in the `overworld` skybox; transparent = not rendered). ARGB, default `#00000000`.
- `visual/cloud_color` — cloud color (transparent = no clouds rendered, entities not "in clouds"). ARGB, default `#00000000`.
- `visual/cloud_height` — cloud height (entities within cloud height..+4 consider themselves in clouds when opacity ≠ 0). Float, default 192.33.
- `visual/sun_angle` / `visual/moon_angle` / `visual/star_angle` — celestial body elevation angles in degrees (0 = directly above, clockwise from east; rendered only in the `overworld` skybox). Sun angle also affects clocks and daylight detectors. Float, default 0.0; interpolation jumps directly when the 360-modulo'd difference exceeds 90.
- `visual/moon_phase` — moon phase (rendering, moonlight, item models). Enum, default `full_moon`: `full_moon`, `waning_gibbous`, `third_quarter`, `waning_crescent`, `new_moon`, `waxing_crescent`, `first_quarter`, `waxing_gibbous`. Override only, not interpolatable.
- `visual/star_brightness` — star brightness (vanilla: 0.5 at night, 0 day). Float 0–1, default 0.0.
- `visual/block_light_tint` — block light tint (gray at low light, tinted mid, white at high). RGB, default `#FFD88C`. Provides lightmap shader uniform `BlockLightTint`.
- `visual/sky_light_color` — sky light visual color. RGB, default `#FFFFFF`. Provides `SkyLightColor`.
- `visual/sky_light_factor` — sky light visual brightness (multiplies sky light color). Float 0–1, default 0.0. Provides `SkyFactor`.
- `visual/night_vision_color` — night vision light color (per-channel max with `visual/ambient_light_color`). RGB, default `#999999`. Provides `NightVisionColor`.
- `visual/ambient_light_color` — ambient light color. RGB, default `#FFFFFF`. Provides `AmbientColor`.
- `visual/default_dripstone_particle` — dripstone default dripping particle when no liquid above. Particle options, default `{"type": "minecraft:dripping_dripstone_water"}`. Override only.
- `visual/ambient_particles` — ambient particles attempted every tick around the camera on incomplete-collision blocks. List of `{particle (particle data), probability (0–1)}`, default empty. Override only.

### Audio

- `audio/background_music` — background music (category `music`, follows the player; music popup key = sound path with `/` → `.`): `default` (`sound`, `min_delay`, `max_delay` (capped at 24000 ticks by the music frequency option), `replace_current_music`), optional `underwater`, `creative`. Default empty object; override only.
- `audio/music_volume` — background music volume. Float 0–1, default 1.0. Interpolatable.
- `audio/ambient_sounds` — ambient sounds (category `ambient`): `loop` (loops while in the biome, fades in/out), `mood` (`sound`, `tick_delay`, `block_search_extent` (cube half-side ×2), `offset`), `additions` (list of `{sound, tick_chance}`). Default empty; override only.
- `audio/firefly_bush_sounds` — whether firefly bushes can produce ambient sounds/particles (still need open sky etc.). Bool, default false.

### Gameplay

- `gameplay/sky_light_level` — sky light intensity for behavior (Phantom spawns, daylight detectors, mob spawn light); does NOT affect brightness rendering. Float 0–15, default 15.0. Dimension-wide (not position-based).
- `gameplay/can_start_raid` — whether Ominous players can start raids (not synced to client). Bool, default true.
- `gameplay/water_evaporates` — water evaporates: buckets (via `#water` fluids) cannot place, ice cannot make water, wet sponges dry instantly, dripstone cannot turn mud into clay. Bool, default false.
- `gameplay/bed_rule` — bed behavior (not synced): `can_sleep` / `can_set_spawn` = `always` / `when_dark` (internal sky light ≤ 11; always passes when the dimension has `has_fixed_time`) / `never`; `explodes` (default false — bed explodes on use); `destroy_on_leave` (no effect); `error_message` (text component; only for sleep/spawn failures). Default: sleep `when_dark`, spawn `always`.
- `gameplay/respawn_anchor_works` — whether respawn anchors work (else they explode). Bool, default false.
- `gameplay/straw_bed_rule` (Java 26.3 dev) — like bed_rule for straw beds: `can_sleep`/`can_set_spawn` conditions, `destroy_on_use` (default false), `destroy_on_leave` (default false), `error_message`.
- `gameplay/nether_portal_spawns_piglin` — whether nether portals spawn zombified piglins. Bool, default false.
- `gameplay/fast_lava` — lava flows faster/farther and pushes harder. Bool, default false. Dimension-wide.
- `gameplay/increased_fire_burnout` — fire burns out faster with higher chance to burn blocks (not synced). Bool, default false.
- `gameplay/eyeblossom_open` — eyeblossom conversion (potted too): `open`, `close`, `default` (never converts). Enum, default `default`.
- `gameplay/turtle_egg_hatch_chance` — per-random-tick hatch progress chance. Float 0–1, default 0.002.
- `gameplay/piglins_zombify` — whether piglins, piglin brutes, and hoglins zombify. Bool, default true.
- `gameplay/snow_golem_melts` — snow golems take 1 fire damage per tick. Bool, default false.
- `gameplay/creaking_active` — creaking hearts activate (true) or stay dormant (false). Bool, default false.
- `gameplay/surface_slime_spawn_chance` — base surface slime spawn chance in `#allows_surface_slime_spawns` biomes (moonlight also matters). Float 0–1, default 0.0.
- `gameplay/cat_waking_up_gift_chance` — cat morning gift chance. Float 0–1, default 0.0.
- `gameplay/bees_stay_in_hive` — bees always return to hives and don't leave. Bool, default false.
- `gameplay/monsters_burn` — mobs burn in daylight (not synced). All must hold: not player/player-model/armor stand and in `#burn_in_daylight`; attribute true at position; not in water/rain/powder snow; eye-position sky light 15; the internal light formula (60a−4ai+i)/(60−3i) > 0.5; empty helmet slot (zombie horses/zombified nautiluses check body armor). Bool, default false.
- `gameplay/can_pillager_patrol_spawn` — whether pillager patrols can spawn. Bool, default true.
- `gameplay/villager_activity` / `gameplay/baby_villager_activity` — adult/baby villager schedule activity, fetched once per second (not synced). Villager activity enum, default `idle`; meaningful: `core`, `hide`, `idle`, `meet`, `panic`, `pre_raid`, `raid`, `rest`, `work` (+ `play` for babies). Override only.

## Modifiers

Modifiers take input value (automatic) + argument value + modifier type.

- **override** — replace with the argument. Implicit when mapping an attribute ID directly to a value.
- **Boolean** (`and`, `nand`, `or`, `nor`, `xor`, `xnor`) — boolean logic with the argument.
- **Float** — `add`, `subtract`, `multiply`, `minimum`, `maximum`, `alpha_blend` (linear interpolation between input and `value` with sample point `alpha` 0–1, default 1 — alpha 1 = override).
- **Color** (RGB and ARGB variants; per-channel results clamped to [0,255]) — `add`, `subtract`, `multiply`; `alpha_blend` (result per channel K: K×(1 + A/255), all four channels; A=255 = override); `blend_to_gray` (gray = brightness×(0.3R+0.59G+0.11B), output = lerp(factor, channel, gray)).

## Weather Attributes

The weather source is hardcoded and applies only when the dimension allows weather (`has_skylight` true, `has_ceiling` false, not The End).

## Other Uses

- Loot predicate `environment_attribute_check` — checks a server-side environment attribute against an exact value.
- Number provider `environment_attribute` — reads numeric server-side attributes (floats and celestial angles, not colors) for loot and villager trade computations.
- Both fetch at the loot context's `origin` position.

---
name: minecraft-time-line
description: Timeline definition format — tracks, keyframes, easing, time markers.
whenToUse: Use when authoring timeline JSON files or referencing time-based environment attributes.
---

# Timeline Definition

Timelines are the time-based environment attribute source and provide time markers for world clocks. Java Edition only.

## Definition Format

Registry `TIMELINE`, data pack path `timeline` (files in `data/<namespace>/timeline/`; tags in `tags/timeline/`).

- `clock` (required) — the world clock ID this timeline uses (ticks).
- `period_ticks` (>0) — the timeline's period; absent = non-periodic.
- `time_markers` — time markers: `<marker ID>: {ticks (≥0; < period when periodic), show_in_commands (default false)}` (int shorthand = ticks only; marker IDs unique per timeline). Markers register on the bound world clock.
- `tracks` — environment attribute tracks: per attribute ID: `modifier` (default `override`) + `keyframes` (non-empty, sorted by `ticks` ascending; at most two keyframes at the same tick):
  - `ticks` (≥0; ≤ period when periodic),
  - `value` (modifier argument value per attribute type),
  - `ease` (default `linear`): a built-in easing function name or `{cubic_bezier: [x1, y1, x2, y2]}` (control points x ∈ [0,1]).

Definitions load once at server startup (restart required). Timelines are used via dimension types, affecting the whole dimension's attributes with **higher priority than biomes**.

## Interpolation

Between keyframes, values interpolate (for interpolatable attributes) per the easing type:

- Non-interpolatable attributes: always the previous keyframe's value.
- Single-keyframe tracks: fixed value.
- Two keyframes at the same tick: instant switch to the later frame.
- Non-periodic: the first keyframe's value before it, the last one's after it. Periodic: keyframes wrap across periods.

Example: period 24000, sky_color red at 0, red at 1000, magenta at 6000 → red for 0–1000, red→magenta for 1000–6000, magenta→red for 6000–24000. Moon angle example: keyframes at tick 6000 with 540.0 and 180.0 → the moon rotates west-to-east over the day (0 = up, 90 = west, 180 = down, 270 = east, mod 360).

## Easing Functions

`constant` (y=0, always previous value) and `linear` (y=x) have no prefix. The rest follow the `in_`/`out_`/`in_out_` naming (in = slow start, out = slow end, in_out = both; out(x) = 1−f(1−x); in_out splits at 0.5):

- `in_back` (2.70158x³−1.70158x²), `in_bounce`/`out_bounce` (piecewise 7.5625x² style), `in_circ` (1−√(1−x²)), `in_cubic` (x³), `in_elastic` (sinusoidal overshoot), `in_expo` (2^(10x−10)), `in_quad` (x²), `in_quart` (x⁴), `in_quint` (x⁵), `in_sine` (1−cos((1−x)·1.5707964)) — each with in/out/in_out variants.

## Built-in Timelines

- `day` — Overworld only; period 1 game day; drives day/night rendering, fog/sky color changes, light intensity, monster burning; also shows `day_count` in the debug screen.
- `early_game` — Overworld only; prevents pillager patrols during the first 5 game days.
- `moon` — Overworld only; period 8 game days; moon phases and surface slime spawns.
- `villager_schedule` — all vanilla dimensions; period 1 game day; villager schedules.

External visualizers: easings.net, cubic-bezier.com.

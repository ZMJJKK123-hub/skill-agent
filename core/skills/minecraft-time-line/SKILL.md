---

name: minecraft-time-line
description: "Minecraft Timeline Definition 时间线定义格式：Definition Format 定义格式（TIMELINE 注册表、data/<namespace>/timeline/ 数据包路径、tags/timeline/ 标签、clock 世界时钟ID ticks、period_ticks 周期 非周期时缺失、time_markers 时间标记 marker ID ticks+show_in_commands）、Tracks 环境属性轨迹（每属性ID modifier+keyframes 关键帧列表 按ticks升序排列 同刻最多两个、keyframes 关键帧 ticks+value+ease 缓动函数）、Definition Behavior 定义行为（服务器启动加载一次、通过维度类型使用 影响整个维度属性 优先级高于生物群系）、Interpolation 插值（可插值属性在关键帧间插值 缓动类型；不可插值属性始终为前一关键帧值；单关键帧轨迹固定值；同刻两个关键帧切换到后者；非周期 前帧前使用首帧值 后帧后使用末帧值；周期 关键帧跨周期环绕）、Easing Functions 缓动函数（constant y=0 始终前值、linear y=x、in_/out_/in_out_ 前缀 in慢启动 out慢结束 in_out两者；函数：in_back/in_bounce/in_circ/in_cubic/in_elastic/in_expo/in_quad/in_quart/in_quint/in_sine 各有in/out/in_out变体）、Built-in Timelines 内置时间线（day 主世界仅 1游戏天周期 驱动昼夜渲染/雾/天空颜色/光照强度/怪物燃烧；early_game 主世界仅 前5游戏天阻止劫掠者巡逻；moon 主世界仅 8游戏天周期 月相+表面史莱姆生成；villager_schedule 所有原版维度 1游戏天周期 村民日程）。"
whenToUse: "Use when authoring timeline JSON files or referencing time-based environment attributes."

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

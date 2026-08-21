---

name: minecraft-waypoint-style
description: "Minecraft Waypoint Style 路径点样式：Definition Format 定义格式（assets/<namespace>/waypoint_style/ JSON文件、near_distance 近距离 最大距离使用第一个sprites纹理 0-60000000 默认128、far_distance 远距离 最小距离使用最后一个纹理 0-60000000 默认332 必须大于near_distance、sprites 可用纹理列表 命名空间ID 非空）、Definition Behavior 定义行为（纹理来自minecraft:gui图集 解析为assets/<namespace>/textures/gui/sprites/hud/locator_bar_dot/<path>.png）、距离插值（n个sprite和距离d：d<near→第一个sprite；d>far→最后一个sprite；之间→线性插值 使用sprite floor((d-near)/(far-near))×(n-2)+1 首尾sprite在范围内不使用 除非n<3）、Built-in Styles 内置样式（default 默认样式 未指定或/waypoint ... style reset时使用、缺失/失败样式回退到硬编码无效样式无ID）。"
whenToUse: "Use when writing resource pack waypoint_style definitions (upcoming content)."

---

# Waypoint Styles

This content applies only to Java Edition.

Waypoint styles are the indicator icon styles shown on the locator bar for mob waypoints.

## Definition format

Waypoint style definitions are JSON files under `assets/<namespace>/waypoint_style`:

- JSON file root object
  - `near_distance` (int, 0≤v≤60000000, default 128): max distance using the first `sprites` texture.
  - `far_distance` (int, 0≤v≤60000000, default 332): min distance using the last texture; must exceed `near_distance`.
  - `sprites` (list, required, non-empty): available textures (namespace IDs).

## Definition behavior

Textures are GUI textures from the `minecraft:gui` atlas, resolved to `assets/<namespace>/textures/gui/sprites/hud/locator_bar_dot/<path>.png`.

With n sprites and distance d: d < near → first sprite; d > far → last sprite; between → linear interpolation using sprite ⌊(d−near)/(far−near)⌋×(n−2)+1 (first/last never used in the range unless n<3).

Built-in styles: `default` (used when none specified or via `/waypoint ... style reset`); a missing/failed style falls back to the hardcoded invalid style with no ID.

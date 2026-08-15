---
name: minecraft-waypoint-style
description: Waypoint style JSON: locator icons, distances, interpolation, built-ins.
whenToUse: Use when writing resource pack waypoint_style definitions (upcoming content).
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

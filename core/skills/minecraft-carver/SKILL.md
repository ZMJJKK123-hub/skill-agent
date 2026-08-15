---

name: minecraft-carver
description: "Configured carver definition JSON: CONFIGURED_CARVER registry, carver types and configs."
whenToUse: "Use when writing datapack worldgen carver definitions or custom cave/canyon carving."

---

# Configured Carvers

This content applies only to Java Edition.

Configured carvers (carvers for short) are the basic units the game uses for terrain carving. Definition files are their data-driven definitions in datapacks.

## Definition format

Carvers use the `CONFIGURED_CARVER` registry. Before 26.3 the datapack path is `worldgen/configured_carver` (definitions in `data/<namespace>/worldgen/configured_carver`, tags in `data/<namespace>/tags/worldgen/configured_carver`). From 26.3 the path is `worldgen/carver` (and `tags/worldgen/carver`).

Definition files use JSON with the following structure:

- JSON file root object
  - `type` (string, required): (namespace ID) carver type.
  - `config` (compound, required): the carver's configuration.
    - `probability` (float, required): (0.0≤v≤1.0) chance per chunk to attempt generation.
    - `replaceable` (string/list, required): blocks the carver can carve (block ID, tag, or list).
    - `y` (compound, required): height the carver attempts to generate (height provider).
    - `lava_level` (compound, required): carved areas at or below this Y are filled with lava (vertical anchor).
    - `debug_settings` (compound): debug settings; `debug_mode` (bool, default `false`).
    - `air_state` (block state, default acacia button): replaces air.
    - `water_state` (block state, default candle, waterlogged if possible): replaces water.
    - `lava_state` (block state, default orange stained glass pane): replaces lava.
    - `barrier_state` (block state, default glass): replaces aquifer barrier blocks.
    - `yScale` (float provider, required): vertical scaling of carved caves.

### Carver types

- `cave` — carves circular chambers and cave tunnels; the common small caves.
- `canyon` — carves a canyon.
- `nether_cave` — like `cave`, but vertically larger; ignores aquifers and surface rules; fills lava below `bottom_y + 32.0`.

Cave config: `horizontal_radius_multiplier` (float provider, required), `vertical_radius_multiplier` (float provider, required), `floor_level` (float provider, required, 0.0–1.0; 0 = ellipsoid, 1 = upper half ellipsoid for flat floors).

Canyon config: `vertical_rotation` (float provider, required), `shape` (compound): `distance_factor` (float provider, required), `thickness` (float provider, required), `horizontal_radius_factor` (float provider, required), `vertical_radius_default_factor` (float), `vertical_radius_center_factor` (float), `width_smoothness` (int, ≥1).

## Definition behavior

Carver data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. During world generation, configured carvers carve carver caves at specified positions.

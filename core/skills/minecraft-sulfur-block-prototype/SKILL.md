---
name: minecraft-sulfur-block-prototype
description: Sulfur cube archetype JSON: attributes, buoyancy, explosions, food, sounds.
whenToUse: Use when writing datapack sulfur_cube_archetype definitions (upcoming content).
---

# Sulfur Cube Archetypes

Sulfur cube archetypes are stored as JSON files in the datapack path `data/<namespace>/sulfur_cube_archetype`. Sulfur cubes use archetypes to define their behavior.

## JSON format

- JSON file root object
  - `attribute_modifiers` (list): attribute modifiers applied to sulfur cubes of this archetype. Each: `attribute` (string), `id` (string, unique), `amount` (float), `operation` (string: `add_value` / `add_multiplied_base` / `add_multiplied_total`).
  - `buoyant` (bool): whether the cube floats in liquids.
  - `contact_damage` (compound, optional): damages entities on contact. `amount` (float), `attribute_to_source` (bool), `damage_type` (string).
  - `explosion` (compound, optional): can explode when ignited. `causes_fire` (bool), `fuse` (int, ticks; when ignited by `#is_explosion` damage, fuse becomes random between 1⁄8×fuse and 3⁄8×fuse−1), `power` (int).
  - `items` (string): item or item tag fed to cubes of this archetype.
  - `knockback_modifiers` (compound): `horizontal_power` (float), `vertical_power` (float).
  - `sound_settings` (compound): `hit_sound` (string), `push_sound` (string), and further sound events (see mc_java_sources for the complete field list).

> The Minecraft Wiki page for this topic is incomplete; verify exact fields against mc_java_sources or the wiki when writing definitions.

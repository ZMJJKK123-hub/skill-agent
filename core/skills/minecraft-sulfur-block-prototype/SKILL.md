---

name: minecraft-sulfur-block-prototype
description: "Minecraft Sulfur Cube Archetype 硫磺立方体原型：JSON format（data/<namespace>/sulfur_cube_archetype 数据包路径）、JSON 格式（attribute_modifiers 属性修饰符列表 attribute/id/amount/operation、buoyant 浮力 是否在液体中漂浮、contact_damage 接触伤害 amount/attribute_to_source/damage_type 可选、explosion 爆炸 点燃时爆炸 causes_fire/fuse 点燃时随机fuse时间/power、items 喂养物品或物品标签、knockback_modifiers 击退修饰符 horizontal_power/vertical_power、sound_settings 声音设置 hit_sound/push_sound 及更多声音事件）。"
whenToUse: "Use when writing datapack sulfur_cube_archetype definitions (upcoming content)."

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

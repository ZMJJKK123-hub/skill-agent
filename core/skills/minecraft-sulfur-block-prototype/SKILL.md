---
name: minecraft-sulfur-block-prototype
description: |
  Sulfur cube archetype definition（Minecraft Wiki 中文版全量正文）。
  
  【概述】Sulfur cube archetypes are stored as JSON files within a data pack in the path
  
  【涵盖内容】
  - （自动提取章节）
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Sulfur cube archetype definition 的完整规范时
---

Sulfur cube archetypes are stored as JSON files within a data pack in the path 
```
data/<namespace>/sulfur_cube_archetype
```

.

# Behavior

  

This section is missing information about: ‘Archetypes’ control which behavior exactly? 
Please expand the section to include this information. Further details may exist on the talk page.

Sulfur cubes use 'archetypes' to define their behavior.

# JSON format

- [NBT Compound / JSON Object]: The root object. - [NBT List / JSON Array] attribute_modifiers: A list of attribute modifiers to apply to sulfur cubes of this archetype. - [NBT Compound / JSON Object]: A single attribute modifier. - [String] attribute: The id of the attribute to modify. - [String] id: A unique id for this attribute modifier. - [Float] amount: Amount to modify the attribute by. - [String] operation: One of ``` add_value ``` , ``` add_multiplied_base ``` and ``` add_multiplied_total ``` — The operation to apply, see Attribute § Operations - [Boolean] buoyant: Whether or not a sulfur cube of this archetype floats in liquids. - [NBT Compound / JSON Object] contact_damage: Optional; if present, sulfur cubes of this archetype will damage entities on contact. - [Float] amount: The amount of damage caused. - [Boolean] attribute_to_source: Whether the damage will be attributed to the sulfur cube. - [String] damage_type: The damage type to use. - [NBT Compound / JSON Object] explosion: Optional; if present, sulfur cubes of this archetype can explode when ignited. - [Boolean] causes_fire: Whether the explosion causes fire. - [Int] fuse: The fuse time in game ticks. If the sulfur cube is ignited by ``` #is_explosion ``` damage, the fuse will instead be set to a random value between ``` 1 ⁄ 8 × fuse ``` and ``` 3 ⁄ 8 × fuse − 1 ``` . - [Int] power: The power of the explosion. - [String] items: An item or an item tag containing all items that can be fed to sulfur cubes of this archetype. - [NBT Compound / JSON Object] knockback_modifiers: Modifiers to the knockback received by sulfur cubes of this archetype. - [Float] horizontal_power: A modifier to the horizontal knockback. - [Float] vertical_power: A modifier to the vertical knockback. - [NBT Compound / JSON Object] sound_settings: Sound settings for sulfur cubes of this archetype. - [String] hit_sound: A sound event that is played when a sulfur cube of this archetype is hit. - [String] push_sound: A sound event that is played when a sulfur cube of this archetype is pushed. - [Float] push_sound_cooldown: The cooldown for the push sound for sulfur cubes of this archetype, in seconds. - [Float] push_sound_impulse_threshold: The smallest impulse required to trigger the push sound for sulfur cubes of this archetype.

# History

# Navigation

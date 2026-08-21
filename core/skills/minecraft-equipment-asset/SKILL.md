---

name: minecraft-equipment-asset
description: "Minecraft Equipment Asset 装备资产定义：Definition Format 定义格式（assets/<namespace>/equipment/ JSON 文件、layers 层级 映射预设模型类型→模型层信息列表）、Layer Fields 层字段（dyeable 染色影响 dyed_color 组件、color_when_undyed 未染色时色调 RGB、texture 纹理 assets/<namespace>/textures/entity/equipment/<preset type>/<path>.png、use_player_texture 翅膀 玩家披风纹理、trim_palette_replacements 盔甲装饰调色板替换 映射 palette ID→replacement palette ID）、Definition Behavior 定义行为（装备槽匹配时渲染预设模型类型层、未定义层不渲染、humanoid 和 wings 可同时渲染）、Preset Model Types 预设模型类型（Humanoid armor 人形盔甲：humanoid 头/胸/脚、humanoid_leggings 腿部、humanoid_baby 婴儿人形 不能渲染装饰、wings 翅膀 抑制披风模型；Animal armor 动物盔甲：wolf_body/horse_body/llama_body/happy_ghast_body/nautilus_body；Saddles 鞍：pig_saddle/strider_saddle/camel_saddle/camel_husk_saddle/horse_saddle/donkey_saddle/mule_saddle/skeleton_horse_saddle/zombie_horse_saddle/nautilus_saddle）。"
whenToUse: "Use when defining custom armor/equipment appearance via equipment assets in resource packs."

---

# Equipment Assets

This content applies only to Java Edition.

Equipment assets (formerly equipment models) are the core definition of armor-type equipment appearance.

## Definition format

Equipment asset definitions are JSON files under `assets/<namespace>/equipment`:

- JSON file root object
  - `layers` (compound): models rendered per equipment slot and preset model type.
    - `<preset model type>` (list): model layer info entries.
      - `dyeable` (compound): whether the layer is affected by dyeing (color from the `dyed_color` item stack component). Absent = dyeing has no effect.
      - `color_when_undyed` (int/list): layer tint when undyed (RGB); absent = no tint.
      - `texture` (string, required): (namespace ID) texture; resolved to `assets/<namespace>/textures/entity/equipment/<preset type>/<path>.png`.
      - `use_player_texture` (bool, default `false`): for `wings`, whether to render with the player's cape texture.
      - `trim_palette_replacements` (compound): if the equipment's armor trim palette ID is in this map, the replacement palette is used; `<palette namespace ID>` (string): replacement palette ID.

## Definition behavior

The game renders the model layer of a matching preset model type when the equipment slot matches; layers not defined for a preset are not rendered. `humanoid` and `wings` can render simultaneously.

Preset model types:

**Humanoid armor**

- `humanoid`: head/chest/feet armor for humanoids (players, mannequins, armor stands, giants, piglins, piglin brutes, zombies, skeletons).
- `humanoid_leggings`: leg armor for humanoids.
- `humanoid_baby`: baby humanoid armor (except armor stands); cannot render trims; for babies, only this layer renders.
- `wings`: wing models for players, mannequins, armor stands; coexists with `humanoid` chest; suppresses the cape model.

**Animal armor**

- `wolf_body`, `horse_body` (horse/skeleton horse/zombie horse), `llama_body` (llama/trader llama), `happy_ghast_body`, `nautilus_body` (nautilus/zombie nautilus).

**Saddles**

- `pig_saddle`, `strider_saddle`, `camel_saddle`, `camel_husk_saddle`, `horse_saddle`, `donkey_saddle`, `mule_saddle`, `skeleton_horse_saddle`, `zombie_horse_saddle`, `nautilus_saddle`.

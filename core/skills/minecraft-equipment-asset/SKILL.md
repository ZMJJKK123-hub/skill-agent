---
name: minecraft-equipment-asset
description: Equipment asset definition JSON: preset model types and layer textures.
whenToUse: Use when defining custom armor/equipment appearance via equipment assets in resource packs.
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

# Item Starter

Copy/rename into your mod for any simple registered item.

Required files:
- `items_definition.json.template` -> `src/main/resources/assets/<modid>/items/<item_name>.json`
- `item_model.json.template` -> `src/main/resources/assets/<modid>/models/item/<item_name>.json`
- texture -> `src/main/resources/assets/<modid>/textures/item/<item_name>.png` (use the PNG generator snippet)
- lang -> `src/main/resources/assets/<modid>/lang/en_us.json` and `zh_cn.json`

For tools/staff use parent `minecraft:item/handheld`; for normal items use `minecraft:item/generated`.
Do NOT delete any of: items definition, model, texture. All three are required for rendering.
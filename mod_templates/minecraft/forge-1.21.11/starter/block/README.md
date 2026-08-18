# Block Starter

Copy/rename these into your mod:
- `BlockTemplate.java` -> e.g. `src/main/java/com/<pkg>/BlockTemplate.java` (then use its helpers)
- `blockstate.json.template` -> `src/main/resources/assets/<modid>/blockstates/<block_name>.json`
- `block_model.json.template` -> `src/main/resources/assets/<modid>/models/block/<block_name>.json`
- `item_model.json.template` -> `src/main/resources/assets/<modid>/models/item/<block_name>.json`
- `items_definition.json.template` -> `src/main/resources/assets/<modid>/items/<block_name>.json`
- `recipe.json.template` -> `src/main/resources/data/<modid>/recipe/<block_name>.json`

Replace placeholders: `<modid>`, `<block_name>`.

Also create:
- `assets/<modid>/textures/block/<block_name>.png` (use the PNG generator snippet in the skill)
- lang keys: `block.<modid>.<block_name>`

If this starter is not needed for the current task, delete this folder.
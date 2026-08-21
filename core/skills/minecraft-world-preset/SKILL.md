---

name: minecraft-world-preset
description: "Minecraft World Preset 世界预设定义：WORLD_PRESET 注册表、data/<namespace>/worldgen/world_preset/ 数据包路径、tags/worldgen/world_preset/ 标签、JSON 格式（dimensions 维度集 必须包含overworld 每个值是维度）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载、仅在世界创建前有效、维度集写入level.dat、相同ID的维度定义文件覆盖预设设置）、Two hardcoded presets 两个硬编码预设（flat 超平坦生成器+设置、single_biome_surface 单一生物群系 维度文件仍优先）、Tags 标签（#extended 按住Alt可选、#normal 无Alt可选、标签为空时所有注册预设显示在"世界"屏幕）、Text 文本（翻译键 generator.<namespace>.<path> 按钮显示"World type: generator.<namespace>.<path>"）。"
whenToUse: "Use when writing datapack worldgen world_preset definitions."

---

# World Presets

This content applies only to Java Edition.

World preset definition files are the data-driven definitions of world presets in datapacks.

## Definition format

World presets use the `WORLD_PRESET` registry; the datapack path is `worldgen/world_preset` (definitions in `data/<namespace>/worldgen/world_preset`, tags in `data/<namespace>/tags/worldgen/world_preset`).

Definition files use JSON with the following structure:

- JSON file root object
  - `dimensions` (compound, required): the preset's dimension set; must include the Overworld (`overworld`). Each value is a dimension (see the dimension definition format).

## Definition behavior

World preset data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Presets provide preconfigured dimension sets for the menu screen; they are only effective before world creation. The dimension set is written into `level.dat`; dimension definition files with the same IDs override preset settings.

Two hardcoded presets allow modifying the Overworld: `flat` (superflat generator + settings) and `single_biome_surface` (single biome); dimension files still take precedence.

## Tags

- `#extended`: selectable while holding Alt.
- `#normal`: selectable without Alt.

If the preset tag is empty, all registered presets appear on the "World" screen.

## Text

Translation key: `generator.<namespace>.<path>`; the button shows "World type: generator.<namespace>.<path>".

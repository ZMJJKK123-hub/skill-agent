---

name: minecraft-enchantment-provider
description: "Minecraft Enchantment Provider 附魔提供者定义：ENCHANTMENT_PROVIDER 注册表、data/<namespace>/enchantment_provider/ 数据包路径、tags/enchantment_provider/ 标签、JSON 格式（type 类型）、三种 Provider Types 提供者类型（by_cost 附魔消耗型：enchantments 可选附魔 ID/标签/数组、cost 附魔消耗整数提供器；by_cost_with_difficulty 附魔消耗+难度型：enchantments、max_cost_span 难度调整 0-10000、min_cost 最小消耗 1-10000 最大消耗 n+md；single 单附魔型：enchantment 附魔ID、level 附魔等级整数提供器）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载、内置提供者 硬编码调用 数据包定义提供者永不使用）、Built-in Providers 内置提供者（enderman_loot_drop 总是应用、mob_spawn_equipment 骷髅陷阱总是应用 自然生成概率应用、pillager_spawn_crossbow 概率应用、raids/* 概率应用 按不祥之兆等级缩放）。"
whenToUse: "Use when writing datapack enchantment_provider definitions or understanding the enchanting source mechanism."

---

# Enchantment Providers

This content applies only to Java Edition.

An enchantment provider is a way for the game to add enchantments to items. Enchantment provider definition files are their data-driven definitions in datapacks.

## Definition format

Enchantment providers use the `ENCHANTMENT_PROVIDER` registry; the datapack path is `enchantment_provider`, so all definitions must be in `data/<namespace>/enchantment_provider`, and tags in `data/<namespace>/tags/enchantment_provider`.

Definition files use JSON with the following structure:

- JSON file root object
  - `type` (string): the enchantment provider type.
    - If `type` is `by_cost`, enchantments are added based on an enchantment cost.
      - `enchantments` (string or string array): enchantments selectable in this process — a namespace ID, an enchantment tag, or an array of enchantment IDs.
      - `cost` (integer or compound tag): the enchantment cost used — an integer provider.
    - If `type` is `by_cost_with_difficulty`, the enchantment cost is computed from the difficulty.
      - `enchantments` (string or string array): same as above.
      - `max_cost_span` (integer): (0≤value≤10000) difficulty-influenced enchantment cost adjustment.
      - `min_cost` (integer): (1≤value≤10000) minimum enchantment cost. With `min_cost` = n, current regional difficulty = d, and `max_cost_span` = m, the maximum cost is n + md.
    - If `type` is `single`, the specified enchantment is added directly with a random level.
      - `enchantment` (namespace ID): the enchantment to add.
      - `level` (integer or compound tag): the enchantment level — an integer provider.

## Definition behavior

Enchantment provider data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

The game picks enchantments for items in certain situations through enchantment providers. Provider invocation is hardcoded: the game only uses the following built-in providers; datapack-defined providers are never used. Some providers apply only probabilistically:

- `enderman_loot_drop`: always applies.
- `mob_spawn_equipment`: always applies to skeleton traps; applies probabilistically to naturally spawned mobs.
- `pillager_spawn_crossbow`: applies probabilistically.
- `raids/*`: applies probabilistically, scaled with the Bad Omen level.

---

name: minecraft-enchantment-provider
description: "Enchantment provider definition JSON: the three types and built-in behavior."
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

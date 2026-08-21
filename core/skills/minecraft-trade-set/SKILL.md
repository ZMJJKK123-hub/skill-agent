---

name: minecraft-trade-set
description: "Trade set definition JSON: TRADE_SET registry controlling villager trade generation, with trades (villager trade IDs/tags), amount (number of trades to generate), allow_duplicates, and random_sequence parameters."
whenToUse: "Use when writing datapack trade_set definitions or understanding villager trade generation."

---

# Trade Sets

This content applies only to Java Edition. See the tutorial on data-driven trading for examples.

Trade sets control how villagers and wandering traders draw trade offers. Definition files are their data-driven definitions in datapacks.

## Definition format

Trade sets use the `TRADE_SET` registry; the datapack path is `trade_set` (definitions in `data/<namespace>/trade_set`, tags in `data/<namespace>/tags/trade_set`).

Definition files use JSON with the following structure:

- JSON file root object
  - `trades` (string/list, required): a villager trade ID, list of IDs, or trade tag — the trades this set can draw.
  - `amount` (int/float/compound, required): number of trades to generate (rounded); with duplicates allowed each draw is independent, otherwise drawn trades are removed. A draw may still fail predicate checks and not count. Drawing stops when the amount is reached or nothing is drawable (number provider).
  - `allow_duplicates` (bool, default `false`): whether duplicate trades are allowed.
  - `random_sequence` (string): random sequence used when generating trades.

Villagers draw with the `villager_trade` loot context; parameters: `this_entity` (the villager), `origin` (its feet position), `additional_cost_component_allowed`.

## Definition behavior

Trade set data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Only built-in trade sets are actually used: villagers (except unemployed/nitwit) call `<profession ID>/level_<level>`; wandering traders call `wandering_trader/buying`, `wandering_trader/uncommon`, and `wandering_trader/common` in order.

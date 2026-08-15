---

name: minecraft-number-provider
description: "Number provider format — all types (constant, uniform, binomial, score...)."
whenToUse: "Use when writing number providers in loot tables, predicates, or enchantments."

---

# Number Provider

Number providers generate a number per rules, used in the loot table system. Java Edition only. (The wiki suggests this page may need splitting after 26.3.)

## Definition Format

Before 26.3, number providers are inline only. From 26.3: registry `NUMBER_PROVIDER`, data pack path `number_provider` (files in `data/<namespace>/number_provider/`; tags in `tags/number_provider/`).

A provider is a bare int/float (= `constant`), or an object `{type (default uniform), ...}`. Provider-type fields accept IDs, numbers, or inline providers.

## Types

- `constant` — `value` (exact number).
- `uniform` — uniform random between `min` and `max` (inclusive).
- `binomial` — binomial random: `n` (Bernoulli trials) and `p` (per-trial success probability), both providers.
- `conditional` (26.3) — `predicate` (loot predicate); `on_true` provider; `on_false` (default 0).
- `number_dispatcher` (26.3) — `cases` (list of `{predicate, number_provider}` checked in order; first match wins), `default` (default 0).
- `weighted_list` (26.3) — `distribution` (non-empty list of `{data (provider), weight (positive int)}`); picks a provider by weight.
- `sum` — `summands` (list of providers).
- `score` — reads a score: `target` (a context entity target) or `{type: context, target}` / `{type: fixed, name (UUID or player name), score}`; optional `scale` (default 1.0 multiplier).
- `storage` — `storage` (command storage ID) + `path` (NBT path to a numeric tag).
- `enchantment_level` — `amount` (level-based function using the loot context's enchantment level).
- `environment_attribute` — `attribute` (environment attribute ID; only float/celestial-angle attributes are usable — others fail to parse); position-variant attributes need the `origin` context.

---

name: minecraft-number-provider
description: "Minecraft Number Provider 数字提供器格式：Definition Format 定义格式（26.3前仅内联、26.3后 NUMBER_PROVIDER 注册表 data/<namespace>/number_provider/；提供器=裸int/float constant 或对象 type+字段）、Types 类型列表（constant 精确值 value、uniform 均匀随机 min-max inclusive、binomial 二项随机 n试验 p成功概率、conditional 条件 26.3 predicate+on_true+on_false、number_dispatcher 数字分派 26.3 cases predicate+number_provider 列表+default、weighted_list 加权列表 26.3 distribution data+weight 列表按权重选择、sum 求和 summands 提供器列表、score 读取分数 target 上下文实体 或 fixed 名称+分数 可选scale乘数、storage 命令存储 storage ID+NBT路径 数值标签、enchantment_level 附魔等级 amount 基于等级的函数、environment_attribute 环境属性 attribute ID 仅float/celestial-angle属性可用 origin 上下文）。"
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

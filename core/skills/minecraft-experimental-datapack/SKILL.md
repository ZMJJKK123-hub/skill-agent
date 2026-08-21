---

name: minecraft-experimental-datapack
description: "Minecraft Experimental Content 实验性内容：Enabling 启用方式（创建世界时 Experimental/Datapacks 启用、不能禁用、现有世界不能启用、内置数据包激活硬编码游戏元素+data/<namespace>/datapacks/<experiment ID>/ 内容、服务器 server.properties initial-enabled-packs/initial-disabled-packs）、Warning 警告（可能与未来版本不兼容 崩溃/损坏/无法加载）、Options 选项（Minecart improvements 矿车改进 max_minecart_speed 游戏规则/同步旋转 惯性/铁轨对齐、Redstone experiments 红石实验 红石粉更新顺序变更、Villager trade rebalancing 村民交易重新平衡 铁匠/图书管理员交易）、Feature Flags 功能标志（启用/禁用功能组、过滤器：blocks 方块 /setblock//fill 不识别 不能使用/拾取、entities 实体 /summon 不识别 不生成/加载、items 物品 /give//item//clear 不识别 隐藏在创造模式 红色禁用物品 工具提示、rules 规则 /gamerule 不识别、effects 效果 /effect 不适用、enchantments 附魔 /enchant 不可用、GUIs 不加载、stats 不显示、commands 不解析）、Feature Flag Set 功能标志集（最多64个标志：vanilla 默认开启、trade_rebalance、redstone_experiments、minecart_improvements）、level.dat enabled_features 标签。"
whenToUse: "Use when understanding or enabling experimental content and feature flags in Java Edition."

---

# Experimental Content

This content applies only to Java Edition.

Experiments are built-in datapacks unique to Java Edition. Enabling them lets players try unfinished or in-development features that may ship in future versions.

## Enabling

Experimental options can be enabled at world creation under "Experimental" or "Datapacks"; they cannot be disabled afterwards, and existing worlds cannot enable them. Enabling a built-in datapack activates the hardcoded game elements controlled by feature flags plus the datapack content under `data/<namespace>/datapacks/<experiment ID>/`. On servers, set `initial-enabled-packs` and `initial-disabled-packs` in `server.properties`.

## Warning

Experimental features may be incompatible with future versions, potentially crashing, corrupting, or preventing loading of the world; a warning is shown in both menus.

## Options (as of 26.2)

- **Minecart improvements**: game rule `max_minecart_speed` (default 8, max 1000 blocks/s); "synchronize minecart rotation" accessibility option (default off); minecarts have inertia (keep vertical momentum and tilt off slopes), and align to rails.
- **Redstone experiments**: changes to redstone dust update order.
- **Villager trade rebalancing**: rebalanced armorer and librarian trades.

## Feature flags

Feature flags enable/disable groups of feature elements per world. They filter items, blocks, entities, screen types, potions, and mob effects across registries:

- Filtered blocks: unrecognized by `/setblock`/`/fill`; cannot be used or picked; their properties don't load with entities; block entities don't generate in structures/features.
- Filtered entities: unrecognized by `/summon`; don't spawn/load; spawn eggs (including dispenser use) and spawners don't work.
- Filtered items: unrecognized by `/give`/`/item`/`/clear`; hidden in creative; tooltip shows red "Disabled Item"; unusable; recipes/loot don't produce them (item entities can still exist).
- Filtered game rules: unrecognized by `/gamerule`. Effects: not assignable via `/effect`. Enchantments: not via `/enchant`. GUIs not loaded; stats not shown; commands not parsed. Mechanism-modifying elements only apply when the flag is on.

A feature flag set holds at most 64 flags. Current flags: `vanilla` (default on), `trade_rebalance`, `redstone_experiments`, `minecart_improvements`. Saves with experiments record `enabled_features` in `level.dat`; without experiments the tag is absent.

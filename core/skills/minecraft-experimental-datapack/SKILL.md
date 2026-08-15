---
name: minecraft-experimental-datapack
description: Java experimental content: built-in datapacks, feature flags, their effects.
whenToUse: Use when understanding or enabling experimental content and feature flags in Java Edition.
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

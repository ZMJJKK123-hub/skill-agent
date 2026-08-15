---
name: minecraft-item
description: Items — behavior (stacking, rarity, durability, cooldowns), categories, removed.
whenToUse: Use when working with items in general — behavior, stacking, durability, rarity, remainders.
---

# Item

Items are objects that appear in inventories, with various behaviors and uses. (The entity form outside inventories is the "Item (entity)"; dropped items from mob deaths are "item entities"; this page is a draft.)

## Behavior

- Held items are part of common entity data — every mob can hold items, and displayed items are visible to all players. Item frames hold 1 item; shelves hold 3 stacks; armor stands display armor; item entities use the item's appearance.
- Many items define use behaviors when held/used; some place blocks or entities in the world (boats → entities, iron blocks → blocks). Selecting an item in the hotbar briefly shows its name above the HUD (Bedrock also shows enchantments, longer with more enchantments).
- **Stacking**: most items stack to 64; some (ender pearls, snowballs, eggs...) to 16; tools, armor, potions etc. do not stack. Different NBT/data usually prevents stacking.
- **Rarity** colors the name: Common (most, e.g. oak log), Uncommon (e.g. totem of undying), Rare (e.g. enchanted golden apple), Epic (e.g. mace).
- All items can be renamed on anvils (custom names render italic) and given lore via the `lore` data component.
- Enchantments add effects and a translucent purple glint animation, raising rarity (Java: any item can be enchanted via commands).
- The `repair_cost` component records anvil operations, increasing future anvil costs.
- Some items have durability consumed by various factors; Java: the `unbreakable` component blocks all durability loss. At 0 durability the item breaks. Creative mode never consumes items/durability.
- Some items carry attribute modifiers (tools in the main hand, armor when worn; any item can gain them via commands).
- Some items have cooldowns (semi-transparent white overlay draining from the top; unusable during it): ender pearls, chorus fruit, wind charges, goat horns, shields hit by axes, etc.
- **Crafting remainders** (Java): items left after crafting/smelting/brewing — in crafting the remainder stays in the grid or returns to the inventory; in smelting with a single fuel the remainder appears after fuel consumption; in brewing the ingredient returns after brewing (popped out if the slot is occupied). Buckets (water/lava/milk) return empty buckets; honey bottles and dragon's breath return glass bottles.

## Item List

See the Minecraft Wiki "Item" page for the complete lists:

- **Items producing blocks, liquids, or entities** — boats/rafts (all wood types), armor stands, seeds, eggs, experience bottles, bows, buckets (axolotl/cod/pufferfish/salmon/tadpole/tropical fish/strider-ish), cocoa beans, crossbows, end crystals, ender pearls, eyes of ender, fire charges, firework rockets, fishing rods, flint and steel, glow berries, item frames (glow), kelp, lava buckets, leads, lingering potions, minecarts (all kinds), nether wart, paintings, pitcher pods, potatoes, powder snow buckets, pumpkin seeds, redstone dust, snowballs, splash potions, string, sweet berries, torchflower seeds, tridents, ...
- **Items interacting in the world** — tools, food, swords, armor, ... (the full interactive set).
- **Items used indirectly in the world** — e.g. paper/cartography, dyes, ... (see the wiki).
- **Spawn eggs** — one per mob (see the wiki list).

## Education Edition Items

Education-only (some also in Bedrock with the Education toggle; photo album and camera via creative/`/give` only): agent spawn egg, antidote, balloons (all colors), bleach, chemical (compounds), glow sticks, fireworks sticks (sparklers), large/small/medium blackboards, camera, elixir, eye drops, ice bomb, NPC spawn egg, photo album, notice board, super fertilizer, tonic, photo.

## Removed Items

Copper horn, fish, horse saddle (item), quiver, "restoration potion" (an old-version potion name), custom spawn egg, leather chainmail helmet/chestplate/leggings/boots. See the removed-items pages for details.

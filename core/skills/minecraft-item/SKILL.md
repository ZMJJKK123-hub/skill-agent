---

name: minecraft-item
description: "Minecraft Item 物品系统：Behavior 行为（Held items 持有物品 通用实体数据、use behaviors 使用行为 放置方块/实体、Stacking 堆叠 大多数64 部分16 工具/盔甲/药水不堆叠、Rarity 稀有度 Common/Uncommon/Rare/Epic 颜色名称、Anvil rename 铁砧重命名 自定义名称斜体、Lore lore数据组件、Enchantments 附魔 效果+紫色光泽动画 提高稀有度、repair_cost 铁砧操作记录、Durability 耐久 消耗因素 unbreakable 组件阻止损失 0耐久破坏 创造模式不消耗、Attribute modifiers 属性修饰符 工具主手/盔甲穿戴、Cooldowns 冷却 半透明白色叠加层 末影珍珠/紫颂果/风弹/山羊角/盾牌被斧击中等、Crafting remainders 合成剩余物 熔炼/酿造后剩余 桶返回空桶 蜂蜜瓶/龙息返回玻璃瓶）、Item List 物品列表（Blocks liquids entities 产生方块/液体/实体的物品、World interaction 世界交互物品、Indirect use 间接使用物品、Spawn eggs 刷怪蛋）、Education Edition Items 教育版物品、Removed Items 已移除物品（copper horn/fish/horse saddle/quiver/restoration potion/custom spawn egg/leather chainmail）。"
whenToUse: "Use when working with items in general — behavior, stacking, durability, rarity, remainders."

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

---

name: minecraft-block
description: "Blocks — behavior, block items, heights, textures, technical/Education/removed blocks."
whenToUse: "Use when working with blocks in general (placement, gravity, textures, item forms)."

---

# Block

Blocks are the basic units of the Minecraft world. "Block" redirects here (not Block by Block charity or the C418 music disc "blocks").

## Behavior

- The world is a grid of 1-cubic-meter cells; usually one block per cell (slabs, candles etc. are exceptions).
- **Air** is a special unbreakable, non-blocking block used when a cell is empty. Java Edition has two variants: cave air and void air.
- Blocks emit light from 0 (none) to 15; e.g. torches, glowstone.
- Most blocks ignore gravity; exceptions: sand, red sand, gravel, anvils, dragon egg, concrete powder, unsupported scaffolding, pointed dripstone, sulfur spikes, snow, suspicious sand and suspicious gravel.
- Block breaking emits sounds/particles except: gravity blocks falling to an invalid position; falling/used broken anvils (no particles only); blocks washed away by fluids; blocks replaced by another block; removed support for rails (all kinds), torches, soul torches, redstone wire, repeaters, comparators; withering leaves.

## Block Items

Block items represent blocks as items and can place them in the world (see the item skill / block-item page).

## Block Heights

Most blocks are 1×1×1 cubes; exceptions (slabs, stairs) are "incomplete blocks". A height difference of less than 0.6 (3/5) blocks can be walked up without jumping.

## Textures

Most block textures are 16×16 pixels; most blocks are 1 m³ but models can change that. Animated textures: water, lava, nether portal, end portal/gateway, fire, soul fire, sea lantern, prismarine, magma block, stems, hyphae, seagrass, kelp, lanterns (incl. copper), sculk blocks/sensors/shriekers/veins, lit campfires/soul campfires, heated block, charged respawn anchor, lit blast furnace/smoker, stonecutter, firefly bush, command blocks. Resource packs can change textures/resolution/animations and models (shapes, scaling; powers-of-two sizes usually work best).

## Block List

The complete list of all blocks (bold = not obtainable by normal means but placeable, e.g. fire via flint and steel, water/lava via buckets, crops via items): see the Minecraft Wiki "Block" page. It covers every block including all wood variants, colored variants, and wall/floor pairs.

## Technical Blocks

Technical blocks serve various purposes during events or use separate namespace IDs to avoid unnecessary block state combinations. In Java Edition they usually have no block item, cannot be obtained normally, and mostly not via commands/editors; their texture is usually the missing texture when obtained. Examples: wall signs (all variants), attached stems, wall banners, candle cakes, bubble column, cave/void air, client-request placeholder block, wall heads, chipped anvil, end gateway/end portal blocks, frosted ice, invisible bedrock, kelp plant, lava cauldron, moving piston, nether portal block, piston head, potted plants, snow cauldron, reserved6, unknown block, sticky piston head, twisting/weeping vine plant, wall torches, water cauldron.

## Education Edition Blocks

Bedrock/Education only: blue torch, large blackboard, element constructor, compound creator, green torch, heated block, lab table, material reducer, notice board, purple torch, red torch, small blackboard, underwater TNT, underwater torch, camera. (Elements are not in the list.)

## Removed Blocks

No longer exist in current versions: gear, locked chest, bush, grass bush, infinite water source, infinite lava source, `grass_carried`, `leaves_carried`, smooth stone brick (and more on the removed-blocks pages).

## Trivia

Blocks can be placed in impossible positions via special means: e.g. `/setblock` or bugs can place a sign in mid-air; it stays until broken or a block update makes it check itself.

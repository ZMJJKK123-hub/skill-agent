---
name: minecraft-item-format
description: Item stack storage format: id/count/components, encoding, validation.
whenToUse: Use when understanding item stack data in saves, commands, or datapack item components.
---

# Item Format

This content applies only to Java Edition. (For storage before Java 1.20.5, see the legacy article; for Bedrock, see the Bedrock item format.)

Item stacks are the game's unified way to store items across files: mob inventories, villager trades, item entities, container inventories, etc.

## Data format

Items are stored in two ways: with a `Slot` byte tag (in containers) or without a slot (as property data, e.g. item entities).

Storage format (root tag):

- `id` (string, required): (namespace ID) item type; absent → becomes air when chunks load or items generate.
- `components` (compound): the item's component patch.
  - `<component ID>` (any): one component and its data; the namespace may be omitted when setting, added as `minecraft:` on export.
  - `!<component ID>` (compound): invalidates a component; content has no effect.
- `count` (int): (0<v≤max stack size) stack count; defaults to 1 when absent/invalid.

## Item stacks

Item stacks add item-type-specific data: stack count and component patch. Effective components = default components + patch (the count shown in the F3+H advanced tooltip).

### Encoding formats

- Basic format: item ID required; count and patch optional. The most common format.
- Optional format: can be empty; used only for hotbar slots.

### Strict validation

Validation runs when defining item stacks and patching components (e.g. `/give`, `/item`):

- Component checks: `max_damage` implies max stack size ≤1; `container`, `bundle_contents` (total ≤1 stack), and `charged_projectiles` require every contained item to pass count validation.
- Count check: count must not exceed the max stack size.

In short, an item cannot be both damageable and stackable, and counts cannot exceed the max. Failed validation makes the item invalid — the command fails and the file fails to load.

### Default components

Items obtained without external modification have default components (the components of an item from `/give` without a patch). Default components are not serialized, cannot be fetched via `/data`, and are not stored when a component equals its default. They are strongly tied to the item type and not inherited by other items; on item replacement, only serialized patch components carry over.

In the creative inventory, items may carry extra components. When the item's components exactly match the creative entry, the item shows its category in blue in the tooltip and can stack with the creative item (if stackable). Items have at least 12 default components, varying by type.

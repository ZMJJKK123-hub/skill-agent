---

name: forge-items
description: "Forge items: Item.Properties, registration, creative tabs, BEWLR dynamic rendering."
whenToUse: "Use when creating Forge items or custom item rendering."

---

# Items

Items exist within inventories (blocks make up the world).

## Creating an item

### Basic items

Instantiate `Item` with an `Item$Properties` (chainable):

| Method | Description |
|---|---|
| `requiredFeatures` | Required `FeatureFlag`s to see the item in its creative tab. |
| `durability` | Max damage; >0 adds "damaged"/"damage" item properties. |
| `stacksTo` | Max stack size; an item cannot be both damageable and stackable. |
| `setNoRepair` | Item cannot be repaired even if damageable. |
| `craftRemainder` | Container item returned after crafting (e.g. lava bucket → empty bucket). |

### Advanced items

Subclass `Item` and override methods for custom behavior.

## Creative tabs

Add items via `BuildCreativeModeTabContentsEvent` (mod event bus) with `#accept(ItemLike)`; gate with `FeatureFlag`s or operator permissions.

Custom tabs: register a `CreativeModeTab` built with `CreativeModeTab#builder()` — title (`Component.translatable("item_group.<modid>.example")`), icon, `displayItems` output, plus Forge extras for image/label/slot colors and ordering.

## Registering

Items must be registered (see registries).

# BlockEntityWithoutLevelRenderer (BEWLR)

BEWLR handles dynamic item rendering — simpler than the old `ItemStack` system. Render via `renderByItem(ItemStack, ItemDisplayContext, PoseStack, MultiBufferSource, int combinedLight, int combinedOverlay)`.

Requirements:

- The item's model must return `true` from `BakedModel#isCustomRenderer` (otherwise the default `ItemRenderer#getBlockEntityRenderer` is used).
- Blocks also use a BEWLR when `Block#getRenderShape` is `RenderShape#ENTITYBLOCK_ANIMATED`.
- Set the BEWLR in `Item#initializeClient` by overriding `IClientItemExtensions#getCustomRenderer`:

```java
@Override
public void initializeClient(Consumer<IClientItemExtensions> consumer) {
  consumer.accept(new IClientItemExtensions() {
    @Override
    public BlockEntityWithoutLevelRenderer getCustomRenderer() {
      return myBEWLRInstance;
    }
  });
}
```

> Each mod should have only **one** custom BEWLR instance.

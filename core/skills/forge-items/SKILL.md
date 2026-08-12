---
name: forge-items
description: |
  Forge 物品（Item）完整指南（Minecraft Wiki 中文版全量正文）。
  
  【概述】BlockEntityWithoutLevelRenderer
  
  【涵盖内容】
  - Basic Items
  - Advanced Items
  - Creative Tabs
  - Custom Creative Tabs
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Forge 物品（Item）完整指南 的完整规范时
---

BlockEntityWithoutLevelRenderer
=======================
`BlockEntityWithoutLevelRenderer` is a method to handle dynamic rendering on items. This system is much simpler than the old `ItemStack` system, which required a `BlockEntity`, and did not allow access to the `ItemStack`.

Using BlockEntityWithoutLevelRenderer
--------------------------

BlockEntityWithoutLevelRenderer allows you to render your item using `public void renderByItem(ItemStack itemStack, ItemDisplayContext ctx, PoseStack poseStack, MultiBufferSource bufferSource, int combinedLight, int combinedOverlay)`.

In order to use an BEWLR, the `Item` must first satisfy the condition that its model returns true for `BakedModel#isCustomRenderer`. If it does not have one, it will use the default `ItemRenderer#getBlockEntityRenderer`. Once that returns true, the Item's BEWLR will be accessed for rendering. 

!!! note
    `Block`s also render using a BEWLR if `Block#getRenderShape` is set to `RenderShape#ENTITYBLOCK_ANIMATED`.

To set the BEWLR for an Item, an anonymous instance of `IClientItemExtensions` must be consumed within `Item#initializeClient`. Within the anonymous instance, `IClientItemExtensions#getCustomRenderer` should be overridden to return the instance of your BEWLR:

```java
// In your item class
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

!!! important
    Each mod should only have one instance of a custom BEWLR.

That is it, no additional setup is necessary to use a BEWLR.

---

Items
=====

Along with blocks, items are a key component of most mods. While blocks make up the level around you, items exist within inventories.

Creating an Item
----------------

### Basic Items

Basic items that need no special functionality (think sticks or sugar) do not need custom classes. You can create an item by instantiating the `Item` class with an `Item$Properties` object. This `Item$Properties` object can be made via the constructor and customized by calling its methods. For instance:

|      Method        |                  Description                  |
|:------------------:|:----------------------------------------------|
| `requiredFeatures` | Sets the required `FeatureFlag`s needed to see this item in the `CreativeModeTab` it is added to. |
| `durability`       | Sets the maximum damage value for this item. If it is over `0`, two item properties "damaged" and "damage" are added. |
| `stacksTo`         | Sets the maximum stack size. You cannot have an item that is both damageable and stackable. |
| `setNoRepair`      | Makes this item impossible to repair, even if it is damageable. |
| `craftRemainder`   | Sets this item's container item, the way that lava buckets give you back an empty bucket when they are used. |

The above methods are chainable, meaning they `return this` to facilitate calling them in series.

### Advanced Items

Setting the properties of an item as above only works for simple items. If you want more complicated items, you should subclass `Item` and override its methods.

## Creative Tabs

An item can be added to a `CreativeModeTab` via `BuildCreativeModeTabContentsEvent` on the [mod event bus][modbus]. An item(s) can be added without any additional configurations via `#accept`.

```java
// Registered on the MOD event bus
// Assume we have RegistryObject<Item> and RegistryObject<Block> called ITEM and BLOCK
@SubscribeEvent
public void buildContents(BuildCreativeModeTabContentsEvent event) {
  // Add to ingredients tab
  if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
    event.accept(ITEM);
    event.accept(BLOCK); // Takes in an ItemLike, assumes block has registered item
  }
}
```

You can also enable or disable items being added through a `FeatureFlag` in the `FeatureFlagSet` or a boolean determining whether the player has permissions to see operator creative tabs.

### Custom Creative Tabs

A custom `CreativeModeTab` must be [registered][registering]. The builder can be created via `CreativeModeTab#builder`. The tab can set the title, icon, default items, and a number of other properties. In addition, Forge provides additional methods to customize the tab's image, label and slot colors, where the tab should be ordered, etc.

```java
// Assume we have a DeferredRegister<CreativeModeTab> called REGISTRAR
// Assume we have RegistryObject<Item> and RegistryObject<Block> called ITEM and BLOCK
public static final RegistryObject<CreativeModeTab> EXAMPLE_TAB = REGISTRAR.register("example", () -> CreativeModeTab.builder()
  // Set name of tab to display
  .title(Component.translatable("item_group." + MOD_ID + ".example"))
  // Set icon of creative tab
  .icon(() -> new ItemStack(ITEM.get()))
  // Add default items to tab
  .displayItems((params, output) -> {
    output.accept(ITEM.get());
    output.accept(BLOCK.get());
  })
  .build()
);
```

Registering an Item
-------------------

Items must be [registered][registering] to function.

[modbus]: ../concepts/events.md#mod-event-bus
[registering]: ../concepts/registries.md#methods-for-registering

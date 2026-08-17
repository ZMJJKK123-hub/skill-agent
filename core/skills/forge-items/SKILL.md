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

## Item model definitions (MC 1.21.11+ REQUIRED)

Every item and every block item MUST have an item model definition file at:

```
assets/<modid>/items/<registry_name>.json
```

Content:

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<modid>:item/<registry_name>"
  }
}
```

- For normal items, also create `assets/<modid>/models/item/<registry_name>.json` (e.g. parent `minecraft:item/generated` with `layer0` texture).
- For block items, also create:
  - `assets/<modid>/models/item/<registry_name>.json` with parent `"<modid>:block/<registry_name>"`
  - `assets/<modid>/models/block/<registry_name>.json`
  - `assets/<modid>/blockstates/<registry_name>.json`
  - `assets/<modid>/textures/block/<registry_name>.png`
- Missing `items/<registry_name>.json` causes the **inventory/search icon to show as missing/unrendered**, even though the block may render correctly when placed in the world.

## Minimal GameTest template (MC 1.21.11)

Use this exact minimal template for simple item tests. Do NOT research GameTestHelper APIs first; write this and run `run_test_gametest`, then fix errors from the log if any.

File: `src/test/java/com/example/examplemod/tests/SimpleItemTest.java`

```java
package com.example.examplemod.tests;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.framework.GameTestHolder;

@GameTestHolder("examplemod")
public class SimpleItemTest {
    @GameTest(template = "empty")
    public static void test_item_exists(GameTestHelper helper) {
        helper.succeed();
    }
}
```

- Put `@GameTestHolder("examplemod")` on the class.
- Use `@GameTest(template = "empty")` on each test method.
- The test can be as simple as `helper.succeed()`; it just needs to compile and pass.
- If the test needs to verify an item, use `helper.getLevel()` and registry lookups only after the basic template passes.

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

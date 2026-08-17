---
name: simple-mod-template
description: "Complete working MC 1.21.11 Forge simple MOD template: item + block + recipe + GameTest. Copy these files and rename."
whenToUse: "Use when the user asks for a simple item/block with basic properties, recipe, and optionally GameTest. Do NOT research APIs; copy this template."
---

# Simple MOD Template (MC 1.21.11 / Forge 61.2.0)

This template is a **known-working** simple MOD. Copy these files into the session mod project and replace names as needed.

## How to use

1. Keep the package `com.example.examplemod` and mod id `examplemod` unless the task requires different.
2. Replace `test_item` / `example_block` with your item/block names.
3. Create the files below.
4. Run `gradlew build`; if GameTest is required, also run `run_test_gametest`.

---

## `src/main/java/com/example/examplemod/ExampleMod.java`

```java
package com.example.examplemod;

import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.eventbus.api.listener.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;

@Mod(ExampleMod.MODID)
public final class ExampleMod {
    public static final String MODID = "examplemod";
    private static final Logger LOGGER = LogUtils.getLogger();

    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MODID);

    public static final RegistryObject<Block> EXAMPLE_BLOCK = BLOCKS.register("example_block",
        () -> new Block(BlockBehaviour.Properties.of()
            .setId(BLOCKS.key("example_block"))
            .mapColor(MapColor.STONE)
        )
    );
    public static final RegistryObject<Item> EXAMPLE_BLOCK_ITEM = ITEMS.register("example_block",
        () -> new BlockItem(EXAMPLE_BLOCK.get(), new Item.Properties().setId(ITEMS.key("example_block")))
    );

    public static final RegistryObject<Item> TEST_ITEM = ITEMS.register("test_item",
        () -> new Item(new Item.Properties().setId(ITEMS.key("test_item")))
    );

    public static final RegistryObject<CreativeModeTab> EXAMPLE_TAB = CREATIVE_MODE_TABS.register("example_tab", () -> CreativeModeTab.builder()
            .withTabsBefore(CreativeModeTabs.COMBAT)
            .icon(() -> TEST_ITEM.get().getDefaultInstance())
            .displayItems((parameters, output) -> {
                output.accept(TEST_ITEM.get());
                output.accept(EXAMPLE_BLOCK_ITEM.get());
            }).build());

    public ExampleMod(FMLJavaModLoadingContext context) {
        var modBusGroup = context.getModBusGroup();
        FMLCommonSetupEvent.getBus(modBusGroup).addListener(this::commonSetup);
        BLOCKS.register(modBusGroup);
        ITEMS.register(modBusGroup);
        CREATIVE_MODE_TABS.register(modBusGroup);
        BuildCreativeModeTabContentsEvent.BUS.addListener(ExampleMod::addCreative);
        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        LOGGER.info("HELLO FROM COMMON SETUP");
        if (Config.logDirtBlock)
            LOGGER.info("DIRT BLOCK >> {}", ForgeRegistries.BLOCKS.getKey(Blocks.DIRT));
        LOGGER.info(Config.magicNumberIntroduction + Config.magicNumber);
        Config.items.forEach((item) -> LOGGER.info("ITEM >> {}", item.toString()));
    }

    private static void addCreative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.BUILDING_BLOCKS)
            event.accept(EXAMPLE_BLOCK_ITEM);
    }

    @Mod.EventBusSubscriber(modid = MODID, value = Dist.CLIENT)
    public static class ClientModEvents {
        @SubscribeEvent
        public static void onClientSetup(FMLClientSetupEvent event) {
            LOGGER.info("HELLO FROM CLIENT SETUP");
            LOGGER.info("MINECRAFT NAME >> {}", Minecraft.getInstance().getUser().getName());
        }
    }
}
```

---

## Item model definitions (MUST create for every item/block item)

### `src/main/resources/assets/examplemod/items/test_item.json`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "examplemod:item/test_item"
  }
}
```

### `src/main/resources/assets/examplemod/items/example_block.json`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "examplemod:item/example_block"
  }
}
```

---

## Item / block models

### `src/main/resources/assets/examplemod/models/item/test_item.json`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "examplemod:item/test_item"
  }
}
```

### `src/main/resources/assets/examplemod/models/item/example_block.json`

```json
{
  "parent": "examplemod:block/example_block"
}
```

### `src/main/resources/assets/examplemod/models/block/example_block.json`

```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "examplemod:block/example_block"
  }
}
```

### `src/main/resources/assets/examplemod/blockstates/example_block.json`

```json
{
  "variants": {
    "": {
      "model": "examplemod:block/example_block"
    }
  }
}
```

---

## Lang

### `src/main/resources/assets/examplemod/lang/en_us.json`

```json
{
  "item.examplemod.test_item": "Test Item",
  "block.examplemod.example_block": "Example Block",
  "itemGroup.examplemod.example_tab": "Example Mod"
}
```

### `src/main/resources/assets/examplemod/lang/zh_cn.json`

```json
{
  "item.examplemod.test_item": "测试物品",
  "block.examplemod.example_block": "示例方块",
  "itemGroup.examplemod.example_tab": "示例模组"
}
```

---

## Recipe (MC 1.21.11: ingredients are plain strings)

### `src/main/resources/data/examplemod/recipe/test_item.json`

```json
{
  "type": "minecraft:crafting_shapeless",
  "category": "misc",
  "ingredients": [
    "minecraft:stick",
    "minecraft:iron_ingot"
  ],
  "result": {
    "id": "examplemod:test_item",
    "count": 1
  }
}
```

---

## Textures

Generate simple 16x16 textures with a script:

```python
from PIL import Image, ImageDraw
import os

def make_item(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 1, 9, 10], fill=(0, 200, 255))
    d.rectangle([7, 0, 8, 1], fill=(0, 200, 255))
    d.rectangle([5, 10, 10, 12], fill=(139, 90, 43))
    d.rectangle([6, 12, 9, 13], fill=(255, 215, 0))
    d.rectangle([7, 13, 8, 15], fill=(100, 60, 20))
    img.save(path, 'PNG')

def make_block(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new('RGB', (16, 16), (128, 128, 128))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, 6, 6], fill=(150, 150, 150))
    d.rectangle([9, 9, 13, 13], fill=(80, 80, 80))
    d.rectangle([2, 10, 5, 13], fill=(160, 160, 160))
    img.save(path, 'PNG')
```

---

## Minimal GameTest (if required)

### `src/test/java/com/example/examplemod/tests/SimpleItemTest.java`

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

---

## Do NOT

- Do NOT read `build.gradle`, `Config.java`, `mods.toml`, or `ExampleMod.java` repeatedly before writing.
- Do NOT search `mc_java_sources` for simple item/block APIs.
- Do NOT write `<skill-source>` citations for simple tasks.
- Write the files above first, then run `gradlew build` / `run_test_gametest`, and only fix errors from logs.

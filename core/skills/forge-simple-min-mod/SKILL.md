---
name: forge-simple-min-mod
description: "Minimal runnable Forge 1.21.11 MOD fixed routine: register items + resources + GameTest in one closed loop. Use when the task needs something that compiles, runs, passes GameTest, and has working item registration/rendering."
whenToUse: "The task is to make a MOD run, needs a simple item/block, and must pass build + GameTest."
---

# Forge 1.21.11 Minimal Runnable MOD Fixed Routine

Goal: in the fewest steps, build a MOD that compiles, passes GameTest, and has correct item registration + rendering.
Verified locally: `validate_resources` 0 errors -> `gradlew build` OK -> `run_test_gametest` All tests passed.

## 0. Naming Rules (do this first)

**Never keep template defaults**: `examplemod`, `example_item`, `example_block`, `com.example.examplemod` may only
appear in example code.

Before generating/modifying a MOD, decide from the user's request:
- `modid` (e.g. `myhero`, `enchantedtools`)
- Java package (e.g. `com.xxx.myhero`)
- main class name (e.g. `MyHeroMod`)
- item/block ids (e.g. `legend_sword`)
- resource paths, lang keys, GameTest namespace all follow modid/item name

And update consistently:
- `build.gradle` `group`
- `META-INF/mods.toml` `modId` / description
- `src/main/java` package and class names
- `assets/<modid>/...` and `data/<modid>/...`
- `src/test` package, class name, `@GameTestNamespace`

## 1. Fixed Workflow (in order, don't skip)

```text
1. (optional) load_skill for reference if needed
2. call activate_test_mode to unlock all test tools
3. write/edit code & resources
4. validate_resources -> fix until 0 errors
5. run_mod_test_cycle (contains build + GameTest) -> loop until RESULT: PASS
6. on pass, git_commit / snapshot a checkpoint
```

## 2. Registering an Item (1.21.11 fixed routine)

### 2.1 Java registration (src/main)
Register an Item in the main class (food or plain item both fine):

```java
public static final DeferredRegister<Item> ITEMS =
    DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

public static final RegistryObject<Item> EXAMPLE_ITEM =
    ITEMS.register("example_item", () -> new Item(new Item.Properties()
        .setId(ITEMS.key("example_item"))
        .food(new FoodProperties.Builder().nutrition(1).saturationModifier(0.2f).build())));

// In the mod constructor:
ITEMS.register(context.getModBusGroup());
```

### 2.2 Item model definition (REQUIRED! 1.21.11 added this layer)
`assets/<modid>/items/example_item.json`:

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "<modid>:item/example_item"
  }
}
```

> Without this layer the item renders as "no model / not visible" even if registered. This is the easiest step to miss.

### 2.3 Parent model + texture
`assets/<modid>/models/item/example_item.json`:

```json
{
  "parent": "minecraft:item/generated",
  "textures": { "layer0": "<modid>:item/example_item" }
}
```

Texture must be `assets/<modid>/textures/item/example_item.png` (16x16), reference without `.png`.

### 2.4 Lang files (BOTH en_us + zh_cn, and cover every item/block)

`assets/<modid>/lang/en_us.json`:

```json
{
  "item.<modid>.example_item": "Example Item",
  "block.<modid>.example_block": "Example Block"
}
```

`assets/<modid>/lang/zh_cn.json`:

```json
{
  "item.<modid>.example_item": "示例物品",
  "block.<modid>.example_block": "示例方块"
}
```

> Common pitfall: only en_us has the item key, missing zh_cn or missing the block key. If zh_cn lacks a key, the
> game falls back to English in a Chinese environment, causing mixed-language names. Every registered Item/Block
> needs entries in both files.

### 2.5 Recipe (optional, 1.21.11 format)
`data/<modid>/recipe/example_item.json`:

```json
{
  "type": "minecraft:crafting_shaped",
  "pattern": ["I", "S"],
  "key": {
    "I": "minecraft:iron_ingot",
    "S": "minecraft:stick"
  },
  "result": { "id": "<modid>:example_item", "count": 1 }
}
```

> Result MUST be `{"id": ..., "count": ...}`; ingredients are string ids; do not use the old `"item"` key.

## 2.6 Quick PNG placeholder generator (copy-paste, no extra libraries)

Use this exact Python script to generate solid 16x16 PNG textures. Write it with write_file, then run it with python.

```python
import os, struct, zlib
def png(path, rgb):
    w=h=16
    raw=b''.join(b'\x00'+bytes(rgb)*w for _ in range(h))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    os.makedirs(os.path.dirname(path), exist_ok=True)  # REQUIRED: creates texture dir
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    open(path,'wb').write(data)

# copper color example
png('src/main/resources/assets/<modid>/textures/item/copper_sword.png', (184,115,51))
```

> Do NOT design pixel-art or write PowerShell/System.Drawing scripts. Use the snippet above for placeholder textures.

## 2.7 Tools quick reference (1.21.11, NO SwordItem/PickaxeItem classes)

In 1.21.11 `SwordItem` / `PickaxeItem` / `Tier` do NOT exist as old-style classes. Use `Item.Properties` methods directly:

```java
// Sword
new Item.Properties()
    .sword(ToolMaterial.COPPER, 3.0F, -2.4F)          // damage bonus, attack speed
// Pickaxe
new Item.Properties()
    .pickaxe(ToolMaterial.COPPER, 1.0F, -2.8F)        // damage bonus, attack speed
// Axe
new AxeItem(ToolMaterial.COPPER, 7.0F, -3.2F,
    new Item.Properties().setId(ITEMS.key("copper_axe")))
```

`ToolMaterial.COPPER` exists in vanilla 1.21.11. Do NOT search for `SwordItem.java` / `PickaxeItem.java` — they are not in this version.

## 2.8 Block quick reference (1.21.11)

Register a simple block + block item:

```java
public static final DeferredRegister<Block> BLOCKS =
    DeferredRegister.create(ForgeRegistries.BLOCKS, MODID);
public static final DeferredRegister<Item> ITEMS =
    DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

public static final RegistryObject<Block> COMPRESSED_COPPER =
    BLOCKS.register("compressed_copper", () -> new Block(
        BlockBehaviour.Properties.of()
            .setId(BLOCKS.key("compressed_copper"))
            .mapColor(MapColor.COLOR_ORANGE)
            .strength(5.0F, 6.0F)
            .requiresCorrectToolForDrops()
            .sound(SoundType.COPPER)));
public static final RegistryObject<Item> COMPRESSED_COPPER_ITEM =
    ITEMS.register("compressed_copper", () -> new BlockItem(
        COMPRESSED_COPPER.get(),
        new Item.Properties().setId(ITEMS.key("compressed_copper"))));
```

Required files:
- `assets/<modid>/blockstates/<name>.json`: `{"variants": {"": {"model": "<modid>:block/<name>"}}}`
- `assets/<modid>/models/block/<name>.json`: parent `minecraft:block/cube_all`, texture `all`
- `assets/<modid>/models/item/<name>.json`: parent `<modid>:block/<name>`
- `assets/<modid>/items/<name>.json`: item model definition pointing to `minecraft:item/...`? For a block item, a normal item model definition with `"model": "<modid>:item/<name>"` plus the item model file is also valid; simplest is to keep `items/<name>.json` referencing the item model.
- texture: `assets/<modid>/textures/block/<name>.png`
- lang keys: `block.<modid>.<name>`
- recipe result: `{"id": "<modid>:<name>", "count": 1}`

Imports: `net.minecraft.world.level.block.Block`, `BlockBehaviour`, `SoundType`,
`net.minecraft.world.level.material.MapColor`, `net.minecraft.world.item.BlockItem`.

## 3. GameTest (src/test, fixed routine)

Test class under `src/test/java/<pkg>/tests/`, `@GameTestNamespace`, method with `@GameTest` using the standard
1.21.11 `GameTestHelper`:

```java
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraftforge.gametest.GameTest;
import net.minecraftforge.gametest.GameTestNamespace;

@GameTestNamespace("<modid>")
public class SimpleItemTest {
    @GameTest
    public static void item_registered(GameTestHelper helper) {
        // In 1.21.11 ResourceLocation is renamed to Identifier
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM,
            Identifier.fromNamespaceAndPath("<modid>", "example_item"));
        if (helper.getLevel().registryAccess().lookupOrThrow(Registries.ITEM).get(key).isEmpty()) {
            helper.fail("example_item 未注册");
        } else {
            helper.succeed();
        }
    }
}
```

> Note: this is the correct 1.21.11 form. `ResourceLocation` -> `Identifier`, `registryOrThrow` -> `lookupOrThrow`.
> `@GameTest` has no `template = "empty"` parameter in this version.

## 3.5 Complex feature: custom armor + elytra (e.g. "Flying Chestplates")

1.21.11 has **no `ArmorItem` class**. Armor is a normal `Item` with `humanoidArmor(...)` properties:

```java
// Register: armor via humanoidArmor
ITEMS.register("flying_iron_chestplate",
    () -> new FlyingChestplateItem(ArmorMaterials.IRON,
        ArmorType.CHESTPLATE,
        new Item.Properties().setId(ITEMS.key("flying_iron_chestplate"))));

// Custom item: extends Item, has armor + elytra flight
import net.minecraft.core.component.DataComponents;
import net.minecraft.util.Unit;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;

public class FlyingChestplateItem extends Item {
    public FlyingChestplateItem(ArmorMaterial material, ArmorType type, Properties properties) {
        super(properties.humanoidArmor(material, type)
            .component(DataComponents.GLIDER, Unit.INSTANCE)); // REQUIRED for elytra glide in 1.21.11
    }
    @Override
    public boolean canElytraFly(ItemStack stack, LivingEntity entity) { return true; }
    @Override
    public boolean elytraFlightTick(ItemStack stack, LivingEntity entity, int flightTicks) {
        if (!entity.level().isClientSide()) {
            int next = flightTicks + 1;
            if (next % 10 == 0) {
                stack.hurtAndBreak(1, entity, EquipmentSlot.CHEST);
            }
        }
        return true;
    }
}
```

> 1.21.11 vanilla determines elytra flight by checking `DataComponents.GLIDER`, not just `canElytraFly`.
> Also set `pack.mcmeta` `"supported_formats": [48, 81]` to avoid pack metadata errors.

Pair it with a shapeless recipe: `corresponding chestplate + elytra -> flying chestplate`.

> GameTest lives in src/test, not src/main; self-check with `run_test_gametest`, never `run_game_test_server`.

## 4. Common Pitfalls (check ERROR_LIST.md first)

- Missing `items/<name>.json` -> item not rendered.
- Reference with `.json` / `.png` -> validation error.
- Old recipe result format -> recipe does not load.
- `src/test` has sources but no JUnit -> `gradlew build` `:test` fails: template already sets
  `failOnNoDiscoveredTests=false`; do not remove it.
- 1.21.11 has NO `ArmorItem` class; do not import `net.minecraft.world.item.ArmorItem`; use
  `Item.Properties.humanoidArmor(ArmorMaterial, ArmorType)`.
- Mod constructor uses `FMLJavaModLoadingContext.get().getModBusGroup()` (NOT `getModEventBus()`);
  GameTest annotations come from `net.minecraftforge.gametest.GameTest` / `GameTestNamespace`.
- `ResourceLocation` is `Identifier` in 1.21.11; registry lookup uses `lookupOrThrow` not `registryOrThrow`.
- `Registries` class is `net.minecraft.core.registries.Registries` (not `net.minecraft.core.Registries`) in 1.21.11.
- Cooldowns: `player.getCooldowns().addCooldown(player.getItemInHand(hand), ticks)` — the first param is `ItemStack` in 1.21.11, not `Item`.
- NEVER change build system/plugins, Forge version, or dependency versions. You ARE allowed to edit
  modid/namespace references in build.gradle/settings.gradle when renaming the mod (e.g.
  `forge.enabledGameTestNamespaces`, DataGen `--mod`, group/modId). Do not switch to NeoGradle/NeoForge.
- `META-INF/mods.toml` dependency blocks MUST use `mandatory=true` (boolean); `type="required"` makes Forge treat the
  jar as an invalid mod.
- Use real item textures (e.g. vanilla chestplate icons), not 16x16 solid color squares, or the item looks like a
  gray/solid box in inventory.
- Dev GameTest passing does NOT prove the packaged jar is a valid installed mod; run `verify_artifact` on the jar and
  test it in a real client `mods/` folder when possible.

## 5. Build/Verification Discipline (important)

- WRITE FIRST: Write code directly before reading docs/skills/sources. After the first version, compile/build it;
  only on a compile/test error look up the exact failing symbol in mc_java_sources / ERROR_LIST / skills.
- STARTER TEMPLATES: `starter/` in the workspace contains optional copy-paste templates (e.g. block). Copy/rename
  what you need; delete starters you do NOT use — they are optional and safe to remove.
- SEARCH FREELY: you may grep/read mc_java_sources anytime, no limit. Write code as soon as you have enough.
- Textures: placeholders are fine (simple solid-color PNG or copy vanilla textures); do NOT spend time designing pixel art.
- After writing code: immediately `validate_resources` -> `run_mod_test_cycle`; do NOT keep researching sources.
- On compile error: read the first `error:`, fix one place with the mapped API, rebuild; do not speculate more than
  2 rounds on the same problem.
- Paratera thinking mode requires `reasoning_content` passed back on assistant messages (already fixed in
  core/agent.py; do not regress).
- Completion criterion: `run_test_gametest` shows `All required tests passed` AND `dist/*.jar` exists = DONE.
  Do not loop on harmless WARNs (e.g. javafml version hints) or re-read the same log repeatedly.
  Do NOT obsess over test count: one `@GameTest` can loop-check multiple items; `All required tests passed` means
  all checks passed; test count is NOT the completion measure.

## 6. Final Checks

- `validate_resources` -> 0 errors / 0 warnings
- `build_mod_jar_forge` -> BUILD SUCCESSFUL, `dist/*.jar` exists
- `run_test_gametest` -> All required tests passed
- item items/ , models/item/ , textures/item/ , lang all present -> rendering works

# Agent Error List

> Purpose: when the model is thinking in circles, retrying the same mistake, or hitting a known error, read this
> file first. If a fix is already listed, use it directly. If you hit a new reproducible error, append
> "symptom / root cause / fix" under the matching category so the next run does not go the long way round.

## 1. Build

- **Gradle SSL/PKIX error**
  - Symptom: `PKIX path building failed`, `SSLHandshakeException`, `Failed to find JDK for version 8`
  - Root cause: corporate network/proxy blocks, or certificate validation failure while Gradle downloads dependencies
  - Fix: do NOT change versions; fix certs/proxy/network and retry. Slow first build (dependency download) is normal.

- **`gradlew build` fails because no local Java**
  - Symptom: `java` not on PATH, JAVA_HOME not set
  - Fix: run `detect_environment` first; if Java is unavailable, do not force a build.

- **`Could not resolve`**
  - Fix: check the local Gradle cache first (or let Gradle re-fetch deps); do not repeatedly rewrite build.gradle/settings.gradle versions.

## 2. Resource Loading (1.21.11+)

- **Item has no model**
  - Root cause: MC 1.21.11+ needs `assets/<modid>/items/<name>.json`; `models/item/*.json` alone is not enough
  - Fix: add `items/<name>.json` like `{"model": {"type": "minecraft:model", "model": "<modid>:item/<name>"}}`

- **Model/texture reference includes extension**
  - Root cause: writing `item/foo.json` / `textures/foo.png` inside JSON
  - Fix: references never include `.json` / `.png`

- **Vanilla parent model/texture reported missing**
  - Fix: `minecraft:` namespace is vanilla; skip validating it; only validate your own modid's resources.

- **Recipe does not load**
  - Root cause: 1.21.11+ recipes must use result `{"id": "modid:item", "count": N}` and string ingredient ids
  - Fix: rewrite the recipe JSON in the new format.

- **Mixed EN/CN names in the same mod (e.g. block English, item Chinese)**
  - Root cause: a key is missing in `zh_cn.json`; the game falls back to English for that entry
  - Fix: every registered Item/Block must have a key in BOTH `en_us.json` and `zh_cn.json`:
    `item.<modid>.<name>` / `block.<modid>.<name>`

## 3. GameTest

- **No GameTest runs / no result**
  - Root cause: test class in the wrong place, missing `@GameTest`, or non-1.21.11 method signature
  - Fix: test class under `src/test/java`; confirm annotation and `GameTestHelper` signature; self-check with
    `run_test_gametest`, NOT `run_game_test_server`.

- **`run_test_gametest` fails**
  - Fix: use `parse_gametest_results` to see failures, then `read_game_test_log` / `tail_log` for the full exception.

- **GameTest module package conflict: `Module <modid> contains package <pkg>, module test exports package <pkg> to <modid>`**
  - Symptom: GameTest server starts then exits with
    `java.lang.module.ResolutionException: Module coppersword contains package com.coppersword, module test exports package com.coppersword to coppersword`
  - Root cause: the test class was placed directly under the same package as the main mod class
    (e.g. `src/test/java/com/coppersword/CopperSwordTest.java` with `package com.coppersword;`).
    In Forge userdev, `main` and `test` are separate modules; identical package names are illegal.
  - Fix: ALWAYS put GameTest classes in a `.tests` sub-package and matching directory, exactly like
    `starter/test/GameTestTemplate.java`:
    - File: `src/test/java/com/<pkg>/tests/<Name>Test.java`
    - Package: `package com.<pkg>.tests;`
  - Example: for modid `coppersword`, use `src/test/java/com/coppersword/tests/CopperSwordTest.java` with
    `package com.coppersword.tests;` — never `package com.coppersword;`.

## 4. Server/Client & In-Game

- **RCON connection fails**
  - Symptom: `RCON authentication failed` / `connection refused`
  - Fix: `start_mc_server` with `rcon_port` + `rcon_password` auto-writes the config; or confirm `server.properties`
    has `enable-rcon=true`.

- **Key/input does nothing**
  - Root cause: game window is not in the foreground
  - Fix: bring the game window to front, then `press_key` / `type_text`.

- **Background process never becomes ready**
  - Fix: use `mc_status` to check the process, `tail_log` to read the log, `wait_for_mc_ready` to wait; if the process
    exited, read the crash report.

## 5. Windows/Environment

- **Writing Chinese/emoji becomes question marks**
  - Root cause: bash redirection uses GBK
  - Fix: always use `write_file` / `edit_file`.

- **Deleting a long path is denied**
  - Fix: on Windows use `cmd /c rd /s /q "\\?\<absolute path>"`.

- **Never `taskkill /f /im python.exe`**
  - Reason: the agent itself is python.exe; you would kill yourself.

## 6. Model "thinking in circles / retry" Rules

- If you guess the same error more than 2 times, stop guessing and do a minimal verification (read a log / read the
  error list / run one build).
- If this error list already has the same symptom, use the known fix directly; do not re-explore.
- If it is not here and it is reproducible, append "symptom / root cause / fix" to the matching category, then continue.

## 7. API/Model Calls (Paratera)

- **`reasoning_content` must be passed back**
  - Symptom: `The reasoning_content in the thinking mode must be passed back to the API. assistant message at index N has tool_calls but no reasoning_content`
  - Root cause: Paratera thinking mode requires assistant history messages to keep `reasoning_content`
  - Fix: `core/agent.py` `message.to_dict()` must include `reasoning_content` (already fixed; do not regress).

- **Model name not found**
  - Symptom: `There are no healthy deployments for this model=deepseek-v4-flash`

## 8. Template / Build

- **`gradlew build` `:test` fails**
  - Symptom: `test task did not discover any tests`, but `src/test` has GameTest sources
  - Root cause: GameTest is not JUnit; Gradle defaults `failOnNoDiscoveredTests=true`
  - Fix: the template build.gradle already sets `failOnNoDiscoveredTests=false`; do not delete it.

- **Gradle wrapper `.lck` file access denied**
  - Symptom: `FileNotFoundException ... gradle-9.5.0-bin.zip.lck (拒绝访问)`
  - Fix: environment/sandbox write restriction on `C:\Users\59639\.gradle`; run the server with full access, or init
    Gradle once manually.

## 9. Complex Features / 1.21.11 Mapping

- **`ArmorItem` class not found**
  - Symptom: `import net.minecraft.world.item.ArmorItem; 找不到符号`
  - Root cause: 1.21.11 removed `ArmorItem`; armor is made with `Item.Properties.humanoidArmor(ArmorMaterial, ArmorType)`
  - Fix: custom class extends `Item`, constructor calls `super(properties.humanoidArmor(material, type))`;
    materials use `ArmorMaterials.IRON` etc.

- **`ResourceLocation` not found**
  - Symptom: `import net.minecraft.resources.ResourceLocation; 找不到符号`
  - Root cause: in 1.21.11 `ResourceLocation` is renamed to `Identifier`
  - Fix: use `net.minecraft.resources.Identifier`, e.g. `Identifier.fromNamespaceAndPath(modid, name)`.

- **`registryOrThrow` not found**
  - Symptom: `method registryOrThrow(ResourceKey<Registry<Item>>) not found`
  - Root cause: 1.21.11 `RegistryAccess` uses `lookupOrThrow` instead of `registryOrThrow`
  - Fix: `helper.getLevel().registryAccess().lookupOrThrow(Registries.ITEM).get(key)`.

- **`@GameTest` reports no `template()`**
  - Root cause: this version's `@GameTest` has no `template` parameter
  - Fix: use plain `@GameTest`; do not write `@GameTest(template = "empty")`.

- **Modifying build.gradle breaks the build system**
  - Symptom: agent switches ForgeGradle to NeoGradle, plugin resolution fails, Supervisor keeps alerting
  - Root cause: unnecessary changes to build files
  - Fix: the template already configures `net.minecraftforge.gradle` + `forge:1.21.11-61.2.0`; check code/error list
    first; never switch build toolchain.

- **`DeferredRegister.Items` does not exist**
  - Symptom: `cannot find symbol Items in DeferredRegister`
  - Root cause: this template uses `DeferredRegister<Item>`, not `DeferredRegister.Items`
  - Fix: `DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);` and register with
    `new Item.Properties().setId(ITEMS.key("xxx"))`.

- **MOD shows as invalid in game / mods.toml dependency uses `type="required"`**
  - Symptom: the jar is copied into `mods/` but Forge reports it as an invalid/unrecognized mod
  - Root cause: `META-INF/mods.toml` uses `type="required"` for dependencies; Forge expects `mandatory=true`
  - Fix: use `mandatory=true` (boolean), not `type="required"`:
    ```toml
    [[dependencies.<modid>]]
    modId="forge"
    mandatory=true
    versionRange="[61,)"
    ordering="NONE"
    side="BOTH"
    ```

- **Elytra/glide does not work even though the item renders**
  - Symptom: custom chestplate can be worn and has armor, but double-tapping space does not glide
  - Root cause: 1.21.11 vanilla checks `DataComponents.GLIDER` to enable elytra glide; overriding `canElytraFly`
    alone is not enough
  - Fix: add `.component(DataComponents.GLIDER, Unit.INSTANCE)` to `Item.Properties` (imports
    `net.minecraft.core.component.DataComponents`, `net.minecraft.util.Unit`).

- **Block task slow / searching MapColor or block APIs**
  - Symptom: agent spends minutes grepping `MapColor`, `BlockBehaviour`, `BlockItem` locations in block tasks
  - Root cause: block registration API is not in the skill/error list yet
  - Fix: use the block quick reference in forge-simple-min-mod §2.8
    (`BlockBehaviour.Properties.of().setId(...).mapColor(...).strength(...)` + `BlockItem`, plus
    blockstate/model/item/texture files).

- **Purple/black missing texture icon (item works but no render)**
  - Symptom: item shows the default purple-black missing texture icon in inventory/hand
  - Root cause: the texture PNG is invalid; common cause: PNG generator declares `color type=6 (RGBA)` but writes only
    3 bytes per pixel (RGB), so the PNG is malformed and Minecraft rejects it
  - Fix: use `color type=2 (RGB)` when writing 3-byte RGB pixels; or write 4-byte RGBA pixels with RGBA scanlines.
    Verify PNG signature + IHDR/scanline layout.

- **Chinese text in JSON becomes garbled**
  - Symptom: item name in-game shows mojibake (e.g. `ըƻ`), but model/JSON structure is fine
  - Root cause: the JSON was written/encoded with the wrong charset (usually GBK from shell, or Python default encoding)
  - Fix: always write JSON via write_file (UTF-8); when generating JSON with Python, open/write with
    `encoding='utf-8'`; if a script receives Chinese through a Windows shell, use Unicode escapes
    (e.g. `\u7206\u70b8\u82f9\u679c` for `爆炸苹果`).

- **Explosion has effect but does not damage the player**
  - Symptom: eating an exploding item shows the explosion but the player takes no damage
  - Root cause: using `level.explode(player, ..., Level.ExplosionInteraction.NONE)` with the player as the source
    can produce an explosion without hurting the eater
  - Fix: use `level.explode(null, x, y, z, power, Level.ExplosionInteraction.MOB)` so entities in the radius take
    damage, or explicitly hurt the player after the explosion.

- **`player.getCooldowns().addCooldown(Item, int)` fails in 1.21.11**
  - Symptom: compile error on `addCooldown(Item, int)`; no matching method
  - Root cause: `ItemCooldowns.addCooldown` first parameter is now `ItemStack` (or item id), legacy `Item` overload removed
  - Fix: use `player.getCooldowns().addCooldown(player.getItemInHand(hand), ticks)` (or the `Identifier` overload).

- **`SwordItem` / `PickaxeItem` not found in 1.21.11**
  - Symptom: `cannot find SwordItem.java` / `PickaxeItem.java` in mc_java_sources; agent keeps searching
  - Root cause: 1.21.11 removed old tool classes; tools are built with `Item.Properties` methods
  - Fix: use `new Item.Properties().sword(ToolMaterial.COPPER, damageBonus, attackSpeed)` for sword,
    `.pickaxe(...)` for pickaxe, and `new AxeItem(ToolMaterial.COPPER, damageBonus, attackSpeed, properties)`
    for axe. `ToolMaterial.COPPER` exists.

- **`FileNotFoundError` when generating texture PNG**
  - Symptom: `FileNotFoundError: [Errno 2] No such file or directory: 'src/main/resources/assets/<modid>/textures/item/foo.png'`
  - Root cause: the PNG generator writes to a path whose parent directory does not exist yet
  - Fix: call `os.makedirs(os.path.dirname(path), exist_ok=True)` inside the PNG generator before writing the file.

- **`Item.use(...)` signature changed in 1.21.11**
  - Symptom: `方法不会覆盖或实现超类型的方法` on `use(ItemStack, Level, Player, InteractionHand)`
  - Root cause: 1.21.11 `Item.use` is `public InteractionResult use(Level level, Player player, InteractionHand hand)`
  - Fix: override `use(Level, Player, InteractionHand)`; do NOT use the old `use(ItemStack, ...)` signature.

- **`ServerPlayer.teleportTo(...)` requires new parameters**
  - Symptom: `对于 teleportTo(ServerLevel, double, double, double, float, float), 找不到合适的方法`
  - Root cause: 1.21.11 `ServerPlayer.teleportTo` needs `Set<Relative>` and a `boolean` argument
  - Fix:
    `player.teleportTo(serverLevel, x, y, z, Set.of(), yaw, pitch, false);`
    or for same-level teleport use `player.teleportTo(x, y, z);`.

- **`getModEventBus()` not found / `BusGroup.addListener` missing**
  - Symptom: compile errors on `getModEventBus()` or `getModBusGroup().addListener(...)`
  - Root cause: 1.21.11 Forge uses typed event buses instead of the old event bus accessor
  - Fix: register DeferredRegisters with `FMLJavaModLoadingContext.get().getModBusGroup()`;
    register lifecycle listeners with typed getters, e.g.
    `FMLClientSetupEvent.getBus(FMLJavaModLoadingContext.get().getModBusGroup()).addListener(this::onClientSetup);`

- **`isClientSide` is private in `Level`**
  - Symptom: `错误: isClientSide 在 Level 中是 private 访问控制` / `cannot find symbol isClientSide`
  - Root cause: in 1.21.11 `Level.isClientSide` is a private field; the public accessor is a method
  - Fix: use `level.isClientSide()` (with parentheses), not `level.isClientSide`.

- **Block entity / menu patterns (1.21.11)**
  - Register: `DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, MODID)` and
    `DeferredRegister.create(ForgeRegistries.MENU_TYPES, MODID)`.
  - BlockEntityType: `new BlockEntityType<>(Factory, Set.of(block))` (the FeatureFlags overload is for MenuType).
  - Save/load: `saveAdditional(ValueOutput)` / `loadAdditional(ValueInput)` with `ContainerHelper.saveAllItems/loadAllItems`.

- **`FMLJavaModLoadingContext.get().getModEventBus()` not found**
  - Symptom: compile error `getModEventBus()` not found / deprecated-removal warnings on mod constructor
  - Root cause: 1.21.11 Forge uses `BusGroup` instead of the old event bus accessor
  - Fix: use `ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());` in the mod constructor, and import
    `net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext`. For GameTest, use
    `net.minecraftforge.gametest.GameTest` / `net.minecraftforge.gametest.GameTestNamespace`.

- **`pack.mcmeta` ERROR: supported_formats required (older versions only, not 1.21.11)**
  - Symptom: `Pack declares support for format 48, but game versions supporting formats 17 to 81 require a supported_formats field`
  - Root cause: an old pack.mcmeta form; **DO NOT** apply this to 1.21.11 Forge mods
  - Fix for 1.21.11 Forge: keep the template `min_format`/`max_format` form. Using `pack_format` + `supported_formats`
    on 1.21.11 triggers the newer `missing min_format/max_format` warning.

- **`pack.mcmeta` WARN/ERROR: missing min_format / max_format**
  - Symptom: `Couldn't load mod:<modid> pack metadata: Pack declares support for version newer than 64, but is missing mandatory fields min_format and max_format`
  - Severity: not fatal (game still starts), but the mod's resource-pack metadata is rejected; may cause resource/texture loading issues
  - Root cause: 1.21.11 Forge mod pack.mcmeta must declare `min_format` and `max_format`
  - Fix: use the template form:
    ```json
    {
      "pack": {
        "description": "<modid> resources",
        "max_format": 94,
        "min_format": [94, 1]
      }
    }
    ```
    Do NOT replace it with only `pack_format`/`supported_formats` in a mod jar.

- **Build Guard too strict: agent refuses to update modid namespace in build.gradle**
  - Symptom: agent wants to rename modid but gets stuck because `forge.enabledGameTestNamespaces` still says
    `examplemod`, and it believes modifying build.gradle is forbidden; it loops researching workarounds
  - Root cause: the guard was phrased as "never modify build.gradle", but renaming a mod legitimately requires
    changing namespace/mod references in build.gradle
  - Fix: BUILD GUARD means: never change build system/plugins, Forge version, or dependency versions. Editing
    modid/namespace references (e.g. `forge.enabledGameTestNamespaces`, DataGen `--mod`, group/modId) is ALLOWED
    and required when renaming the mod.

- **`Missing language javafml version [24,]` (may be harmless)**
  - Symptom: WARN appears in logs but later `All required tests passed` / `BUILD SUCCESSFUL`
  - Root cause: usually an environment/dependency version hint, does NOT affect correctness
  - Fix: as long as GameTest shows "All required tests passed" and `dist/*.jar` exists -> treat as done; do not loop
    on such harmless WARNs.

## 10. Completion Criterion (prevent looping)

- When `run_test_gametest` prints `All required tests passed` AND `dist/*.jar` exists, the task is COMPLETE:
  1. Write the final summary immediately;
  2. do not dig into harmless WARNs (e.g. javafml version hints);
  3. do not re-read the same log repeatedly;
  4. do not touch already-passing code to "verify/enhance" it.
- Only enter the fix loop when build/tests actually FAIL.
- Do NOT obsess over test count: one `@GameTest` method can loop-check multiple items. "All required tests passed"
  means all checks passed; test count is NOT the completion measure.

## 11. Validation / Rendering Gaps

- **Dev GameTest passed but the jar is not a valid installed mod**
  - Symptom: `run_test_gametest` passes, but copying the jar into the real client `mods/` shows invalid mod / doesn't load
  - Root cause: dev GameTest loads classes+resources from the Gradle classpath, not from the packaged jar; it does not
    run the same strict installed-mod validation
  - Fix: before delivering, run `verify_artifact` on the actual jar and also test the jar in a real Forge client
    `mods/` folder when possible. "GameTest passed" does NOT prove jar validity.

- **Item renders as a gray/solid box**
  - Symptom: item appears as a plain colored square / gray box in inventory instead of a recognizable item icon
  - Root cause: the texture is a 16x16 solid color square instead of a real item icon
  - Fix: use real item textures (e.g. extract vanilla chestplate icons from the 1.21.11 client jar) for inventory icons.

- **Item not rendered in-game even though functionality works**
  - Symptom: item works, but in inventory/hand it is invisible or missing
  - Root cause: one of `items/<name>.json`, `models/item/<name>.json`, `textures/item/<name>.png`, or lang is missing/wrong
  - Fix: use `starter/item/` templates; ensure all three resource files exist. Tools/staff use
    `minecraft:item/handheld`; normal items use `minecraft:item/generated`. Verify texture PNG is a valid PNG (signature + IHDR).

## Append Format

```md
- **One-line symptom**
  - Symptom: ...
  - Root cause: ...
  - Fix: ...
```
## 2026-08-19 Auto-recorded from runtime

- **Auto-recorded:** `import net.minecraft.core.Registries` cannot resolve symbol in 1.21.11 | `Registries` class moved to package `net.minecraft.core.registries` | import `net.minecraft.core.registries.Registries` instead for `Registries.ITEM` registry-key lookups

## 2026-08-19 Auto-recorded from runtime

- **Auto-recorded:** - **资源（1.21.11）**：每个物品/方块物品需要 `assets/<modid>/items/<name>.json`；模型/贴图引用是命名空间形式**不带**.json/.png；配方用字符串 ingredient + result {id,count}；lang 键 `item.<modid>.<name>` / `block.<modid>.<name>` 必须**同时有 en_us 和 zh_cn**；pack.mcm

## 2026-08-20 Iteration from Explosive Apple test

- **Custom food item (1.21.11)**
  - Symptom: agent guessed old FoodProperties accessors / could not find `getFoodProperties`
  - Root cause: 1.21.11 uses `Item.Properties().food(FoodProperties)` + `DataComponents.FOOD`; old item food API changed
  - Fix: register with `new Item.Properties().setId(...).food(new FoodProperties.Builder().alwaysEdible().nutrition(4).saturationModifier(2.4F).build())`; in GameTest check `DataComponents.FOOD` and `food.nutrition()`

- **`level.explode` in 1.21.11**
  - Symptom: `isClientSide` private and old explode overload not found
  - Fix: use `level.isClientSide()`; explosion call `level.explode(entity, x, y, z, radius, Level.ExplosionInteraction.BLOCK)`
## 2026-08-20 Iteration from SwapBattle complex test

- **`SubscribeEvent` package moved in Forge 1.21.11**
  - Symptom: `import net.minecraftforge.eventbus.api.SubscribeEvent;` cannot find symbol
  - Root cause: in this Forge 1.21.11 build the annotation is under `net.minecraftforge.eventbus.api.listener`
  - Fix: import `net.minecraftforge.eventbus.api.listener.SubscribeEvent;` (or migrate to the typed event-bus registration pattern)

- **`PacketFlow` package moved in MC 1.21.11**
  - Symptom: `import net.minecraft.network.PacketFlow;` cannot find symbol
  - Fix: import `net.minecraft.network.protocol.PacketFlow;`

- **Client overlay classes may not be on compile classpath**
  - Symptom: `net.minecraftforge.client.event.RegisterGuiOverlaysEvent` / `ForgeGui` / `IGuiOverlay` not found even though decompiled source contains them
  - Note: if the local recompiled jar lacks client-only Forge classes, verify the compile classpath/jar; these classes exist in `mc_java_sources_1.21.11` under `net.minecraftforge.client.*`.
## 2026-08-20 Typed event bus findings from SwapBattle

- **1.21.11 Forge uses typed record events, not old global event bus**
  - Symptom: `MinecraftForge.EVENT_BUS` / `@SubscribeEvent` / `@Mod.EventBusSubscriber` APIs missing or unclear
  - Root cause: this Forge build exposes each event as a class with a static `EventBus<T> BUS = EventBus.create(T.class)` (cancellable events use `CancellableEventBus`)
  - Fix: subscribe with `SomeEvent.BUS.addListener(handler)`; for nested events use the nested class's `BUS` (e.g. `TickEvent.ServerTickEvent.Pre.BUS`)
## 2026-08-20 EventBus source location and Windows pitfall

- **EventBus API classes are NOT in mc_java_sources**
  - Symptom: `net.minecraftforge.eventbus.api.*` classes not found when searching `mc_java_sources`
  - Fix: the Forge eventbus is a separate dependency; find its sources jar under `~/.gradle/caches/modules-2/files-2.1/net.minecraftforge/eventbus/*/...-sources.jar`, or use `javap` on the binary jar, then inspect `EventBus` / `CancellableEventBus` / event characteristic interfaces.

- **Do not use Linux `head` in bash on Windows**
  - Symptom: `'head' is not recognized as an internal or external command`
  - Fix: use Windows syntax: `type file`, `powershell Get-Content file -TotalCount N`, or the `read_file` tool with `limit`.
## 2026-08-20 Forge client overlay classes missing from compile classpath

- **`net.minecraftforge.client.*` overlay/GUI classes missing while vanilla client classes exist**
  - Symptom: `RegisterGuiOverlaysEvent`, `ForgeGui`, `IGuiOverlay` cannot be resolved, even though they exist in `mc_java_sources`
  - Root cause in this environment: the local recompiled Forge jar appears to be server-side / lacks pure-client Forge classes; vanilla `net.minecraft.client.*` classes are still available
  - Workaround for HUD: do not depend on Forge overlay APIs. Implement the HUD by subclassing vanilla `net.minecraft.client.gui.Gui` (or injecting into `Minecraft.gui` via reflection) and override the render method; keep the class in `src/main` only if it compiles against vanilla client classes.
  - GameTest runs server-side; a client HUD class only needs to compile, not run, in the test loop.
## 2026-08-20 SwapBattle GameTest passed after client-dist fix

- **Common item class referencing client Screen causes DEDICATED_SERVER class load failure**
  - Symptom: `Attempted to load class net/minecraft/client/gui/screens/Screen for invalid dist DEDICATED_SERVER` at item registration (`new XxxItem(...)`) even though the client code is inside a `DistExecutor` lambda
  - Root cause: the common item class's bytecode still directly references client-only classes; Forge's RuntimeDistCleaner rejects it when the class is loaded on a dedicated server
  - Fix: remove compile-time references to client classes from the common item; e.g. open the client screen via reflection (`Class.forName("...Screen")`, `Minecraft.getInstance()` via reflection) or delegate to a client-only proxy class with `@OnlyIn(Dist.CLIENT)`
  - Verified: after this fix `runTestGameTestServer` reached `All 1 required tests passed :)` and `BUILD SUCCESSFUL`
## 2026-08-20 Complex MOD API quick reference (Skyforge Realm research)

- **EntityType registration**
  - Use builder chain: `EntityType.Builder.of(MyEntity::new, MobCategory.CREATURE).sized(w,h).clientTrackingRange(10)` then `build(...)`.
- **ServerBossEvent**
  - Constructor: `new ServerBossEvent(Component.translatable("boss.skyforge.title"), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)`.
- **Feature/ConfiguredFeature registration**
  - Registries live under `net.minecraft.core.registries.BuiltInRegistries` (e.g. `BuiltInRegistries.FEATURE`), and features are referred via `Holder`/codec registries in 1.21.11.
## 2026-08-20 Armor/Tool/SpawnEgg quick reference (Skyforge Realm)

- `ArmorMaterial` is in `net.minecraft.world.item.equipment.ArmorMaterial` as a record.
- `ToolMaterial` is in `net.minecraft.world.item.ToolMaterial` as a record: `(TagKey<Block> incorrectBlocksForDrops, int durability, float speed, float attackDamageBonus, int enchantmentValue, TagKey<Item> repairItems)`.
- `SpawnEggItem` constructor is `public SpawnEggItem(Item.Properties)`; vanilla spawn eggs are registered as normal items.
Full `ArmorMaterial` record fields in 1.21.11:
```java
public record ArmorMaterial(
    int durability,
    Map<ArmorType, Integer> defense,
    int enchantmentValue,
    Holder<SoundEvent> equipSound,
    float toughness,
    float knockbackResistance,
    TagKey<Item> repairIngredient,
    ResourceKey<EquipmentAsset> assetId
)
```
## 2026-08-20 Skyforge Realm (itertest6) findings

The agent successfully wrote a very complex MOD (17 Java files + 92 resource files + GameTest) within ~33 minutes using forced-write mode. However, compile-fix phase exceeded 30 minutes due to many 1.21.11 API changes:

- `InteractionResult` is now a sealed interface with records (`Success`, `Fail`, `Pass`, `TryEmptyHandInteraction`, `ItemContext`) — not an enum anymore
- `SpawnEggItem` constructor takes only `Item.Properties` (no EntityType parameter in 1.21.11)
- `customServerAiStep` signature changed in `Mob`
- `EntitySpawnReason` is a new enum replacing some spawn parameters
- `BossEvent` API is unchanged but `ServerBossEvent` constructor takes Component + BossBarColor + BossBarOverlay
- `Tool` is now a record with Codec/StreamCodec, not an interface
- `AttributeModifier` is now a record

Post-write research budget (`build-now-stop`) was not active because the agent was started before that fix was deployed.
## 2026-08-20 More 1.21.11 class moves (from Skyforge compile)

- `IronGolem` -> `net.minecraft.world.entity.animal.golem.IronGolem`
- `SmallFireball` -> `net.minecraft.world.entity.projectile.hurtingprojectile.SmallFireball`
- `RangedAttackMob` -> `net.minecraft.world.entity.monster.RangedAttackMob`
- Heightmap enum -> `net.minecraft.world.level.levelgen.Heightmap.Types` (not HeightmapTypes)
- `Block#useWithoutItem(BlockState, Level, BlockPos, Player, BlockHitResult)` (BlockHitResult, not InteractionHand)
- `Block#entityInside(BlockState, Level, BlockPos, Entity, InsideBlockEffectApplier, boolean)`
- ServerLevel spawn pos via `ServerLevel#getRespawnData().globalPos().pos()` (no getSharedSpawnPos)
- Entity cross-dimension teleport uses `Entity#teleport(TeleportTransition)` / `Entity#teleportTo(ServerLevel, ...)`, not `changeDimension`
- `PersistentData#getLong` returns `Optional<Long>` (use `.orElse(0L)`)
- Equipment asset key: `ResourceKey.create(EquipmentAssets.ROOT_ID, Identifier.fromNamespaceAndPath(...))`, not `Registries.EQUIPMENT_ASSET`
## 2026-08-20 Skyforge Realm runtime fixes (after GameTest pass)

- `Block`/`Item` properties in 1.21.11 runtime require `.setId(...)`:
  - `BlockBehaviour.Properties.of().setId(BLOCKS.key("name"))`
  - `new Item.Properties().setId(ITEMS.key("name"))`
  - `BlockItem` also needs `.setId(ITEMS.key(name))`
- Forge config values cannot be read during `EntityAttributeCreationEvent` before config load:
  - Guard with `ModConfig.COMMON.isLoaded() ? value.get() : fallback`
- `pack.mcmeta` with `pack_format: 61` must include `"supported_formats": [61, 81]`
- `dimension_type` JSON requires `monster_spawn_light_level` (IntProvider, e.g. `{"type":"minecraft:constant","value":7}`) and `monster_spawn_block_light_limit` (int)
- Custom dimension `generator.settings` should reference existing noise settings (`minecraft:overworld`); `minecraft:the_end` may fail to resolve
- Structure JSON must be at `data/<ns>/worldgen/structure/<name>.json` (NOT `data/<ns>/structure/...`)
- Forge `@GameTest` annotation has no `template`/`timeoutTicks` attributes; use bare `@GameTest`
- Test source package must NOT be same as main mod package or JPMS fails `Modules skyforge and test export package ...`; use `com.<mod>.test`
- `HolderLookup.RegistryLookup#get(key)` returns `Optional<Holder.Reference<T>>`; use `.value()`
- `GameTestHelper#spawnWithNoFreeWill(EntityType<E>, BlockPos)` requires `E extends Mob`; cast to concrete entity type
- Forge GameTest imports: `net.minecraftforge.gametest.GameTest`, `net.minecraftforge.gametest.GameTestNamespace`, `net.minecraft.gametest.framework.GameTestHelper`
## 2026-08-20 Skyforge client crash: spawn egg entity renderer missing

- Symptom: using custom spawn egg in client crashes:
  `NullPointerException: entityrenderer is null` at `EntityRenderDispatcher.shouldRender`
- Root cause: custom entity types were registered but no client renderer was registered via `EntityRenderers.register(...)`.
- Fix:
  - Create client-only renderer classes extending `MobRenderer<T, HumanoidRenderState, HumanoidModel<HumanoidRenderState>>` (constructor: `(Context, new HumanoidModel<>(context.bakeLayer(ModelLayers.PLAYER)), shadowRadius)`).
  - Register in client class: `EntityRenderers.register(EntityType, Renderer::new)`.
  - Call from mod constructor via `DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> ClientClass::register);`.
- Also: spawn egg item icon shows default/blank if `assets/<modid>/items/<egg>.json` points to `minecraft:item/template_spawn_egg` but no custom texture is supplied. Fix by pointing to custom `skyforge:item/<egg>` generated model + texture.
## Why GameTest passed despite client-side crashes (important lesson)

- `run_test_gametest` / `runTestGameTestServer` runs a **dedicated server only**; it never starts the client renderer pipeline.
- Server-side GameTest CAN verify:
  - entities registered, spawnable, attributes exist
  - items/blocks/recipes/loot tables/advancements load
  - dimension/structure registry loads
- GameTest CANNOT verify:
  - `EntityRenderers.register(...)` was called (client-only)
  - client renderer classes compile/load correctly
  - item icons/models/textures actually resolve and render
  - spawn egg right-click spawns without client NPE (server spawn works, but renderer missing only crashes on client)
- Therefore a MOD can pass `All required tests passed` + produce a jar, yet still hard-crash in the real client when the entity is rendered.
- Required additional verification for entity mods:
  1. Register client renderers via `DistExecutor.unsafeRunWhenOn(Dist.CLIENT, ...)`.
  2. Run a real client (`run_client` / start_mc_client) or at least a client smoke test that summons/renders the entity.
  3. Add a visual/screenshot check for spawn egg icons and entity rendering.
- This exact bug was found only after a real PCL client crash: `NullPointerException: entityrenderer is null`.
## 2026-08-20 Skyforge client load failure: renderer registered before registry objects exist

- Symptom: real client mod loading screen fails with `Mod Loading has failed`; detail:
  `NullPointerException: Registry Object not present: skyforge:sky_golem`
  at `SkyforgeClient.registerRenderers` -> `SkyforgeMod.<init>`
- Root cause: calling `EntityRenderers.register(SkyforgeEntities.SKY_GOLEM.get(), ...)` inside the mod constructor (even via `DistExecutor`) is TOO EARLY: DeferredRegister entries are not in the registry yet, so `RegistryObject.get()` returns null.
- Fix: defer client renderer registration to `FMLClientSetupEvent`:
  ```java
  FMLClientSetupEvent.getBus(FMLJavaModLoadingContext.get().getModBusGroup())
      .addListener(event -> event.enqueueWork(() ->
          DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
              () -> SkyforgeClient::registerRenderers)));
  ```
- Rule: never call `.get()` on a RegistryObject for EntityType/Block/Item registration-time APIs inside `@Mod` constructor; use lifecycle events (`FMLClientSetupEvent` etc.) after registries are populated.
## 2026-08-20 itertest8 Death Swap: supervisor/agent can't read repo docs from session workspace

- Symptom: supervisor repeatedly logs:
  `Error: [Errno 2] No such file or directory: '<session>/mod/docs/agent/ERROR_LIST.md'`
  and the agent cannot use `grep docs/agent/ERROR_LIST.md` from the mod workspace.
- Root cause: `run_simple.py` chdirs into `mod/`, so `read_file`/`grep` resolve `docs/agent/...` relative to `mod/`; but the repo docs are not copied into the session workspace.
- Fix: copy `ERROR_LIST.md`, `TOOL_GUIDE.md`, `CLIENT_VERIFY.md` from `<repo>/docs/agent` into `<session>/mod/docs/agent` at session start (added to run_simple.py).

## 2026-08-20 itertest8: repeated `Invalid tool arguments JSON for write_file: Unterminated string`

- Symptom: agent repeatedly calls `write_file` with malformed JSON (Unterminated string), especially before generating large Python/resource files.
- Root cause: model tries to inline large file content as a tool argument; JSON escaping breaks.
- Fix guidance: continue to force "large files must use Python generator script"; when a `write_file` JSON parse error occurs, the agent should immediately switch to a generated Python script instead of retrying the same inline write.
- Known repeating count in itertest8: many rounds repeat the same invalid write_file + supervisor advice about jar name before recovery.
## 2026-08-21 itertest8 Death Swap completed - new 1.21.11 API facts

- **`GameTestHelper.makeMockPlayer(PlayerType.SERVER)` fails** (`PlayerType` removed):
  - Use `(ServerPlayer) helper.makeMockPlayer(GameType.SURVIVAL)`; return type is `Player`, not `ServerPlayer`.
- **`ServerPlayer.serverLevel()` / 6-arg `teleportTo` missing**:
  - Use `(ServerLevel) p.level()` and 8-arg `player.teleportTo(targetLevel, x, y, z, Set.of(), yRot, xRot, true)`.
- **Multiple `@GameTest` methods in one class: only first is collected** by this Forge GameTestServer:
  - Merge all assertions into one `@GameTest` method executed sequentially; still satisfies `All required tests passed`.
## 2026-08-21 itertest9 Tree Feller - faster-hit API notes

- **`ResourceLocation` not found on first compile**:
  - Symptom: `import net.minecraft.resources.ResourceLocation; 找不到符号`
  - Fix: always use `net.minecraft.resources.Identifier`, e.g. `Identifier.fromNamespaceAndPath(modid, name)`.
  - Lesson: in new sessions, write `Identifier` from the very first import; do not write `ResourceLocation`.

- **`ItemStack.hurtAndBreak` Consumer<Item> method-reference trap**:
  - Symptom: `stack.hurtAndBreak(1, serverLevel, serverPlayer, ItemStack::getItem);` fails:
    `无法将 类 ItemStack中的 方法 getItem应用到给定类型; 需要: 没有参数; 找到: Item`
  - Root cause: the last parameter is `Consumer<Item>`; `ItemStack::getItem` is `() -> Item`, not `(Item) -> void`.
  - Fix: pass an empty lambda: `stack.hurtAndBreak(1, serverLevel, serverPlayer, item -> {});`
  - Lesson: use a lambda `item -> {}` for durability onBreak callback; do not use `ItemStack::getItem`.

- **Hand-rolled PNG writer causes “Corrupt PNG” in client**:
  - Symptom: Minecraft client says `Could not load image: Corrupt PNG` for a generated item texture.
  - Root cause: custom PNG writer omitted the per-scanline filter byte (`0x00` before each row), producing invalid PNG.
  - Fix: when generating PNG manually, write `b"\x00" + row_bytes` for every scanline; or use PIL and validate with a PNG checker.
## 2026-08-21 itertest10 Auto Smelter Pickaxe - new API facts

- **`net.minecraftforge.common.ModLoadingContext` not found**:
  - 1.21.11 moved `ModLoadingContext` to `net.minecraftforge.fml.ModLoadingContext`.
  - Fix: `import net.minecraftforge.fml.ModLoadingContext;` (get() is deprecated but compiles).
- **Forge GameTest annotation attributes changed**:
  - `@GameTest(template=...)` / `@GameTestHolder` do NOT exist; `@GameTest` uses `structure()` (default `forge:empty3x3x3`).
  - Fix: use `@GameTestNamespace(value=modid)` on class + `@GameTest` / `@GameTest(structure="...")` on method.
- **Test-count observation (not a hard error)**:
  - This Forge runner only registers/runs 1 `@GameTest` method per class even when multiple annotated methods exist; use one aggregate `@GameTest` covering all assertions (already in ERROR_LIST as merge-all advice).
## 2026-08-21 itertest11 Void Miner - new API facts

- **`DirectionProperty` not found**:
  - `net.minecraft.world.level.block.state.properties.DirectionProperty` removed in 1.21.11.
  - Fix: declare facing field as `Property<Direction> FACING = BlockStateProperties.HORIZONTAL_FACING;`.
- **`BlockState#getDrops` signature changed to LootParams.Builder**:
  - Old `getDrops(ServerLevel, BlockPos, BlockEntity)` / `getDrops(LootContext.Builder)` no longer exist.
  - Fix: build `LootParams.Builder` with ORIGIN/TOOL/BLOCK_ENTITY params, then call `state.getDrops(builder)`.
## 2026-08-21 itertest12 Rune Altar - full-flow observations and new API facts

- **`InteractionResult.sidedSuccess(boolean)` not found**:
  - 1.21.11 `InteractionResult` is a sealed interface; `sidedSuccess` does not exist.
  - Fix: use `InteractionResult.SUCCESS` on server and `InteractionResult.CONSUME` on client (or `PASS`/`FAIL`).
- **`BlockEntityType.Builder` may not be used as outer class in this Forge/Mojang mapping**:
  - Prefer `new BlockEntityType<>(factory, Set.of(blocks))` (already in ERROR_LIST) or `BlockEntityType.Builder.of(...)` only if the compiler proves it exists.
- **Full flow gametest-check false negative**:
  - `run_test_gametest` actually passed (`All 1 required tests passed`) and was in tool history, but `<gametest-check> FAILED` fired once; agent satisfied it by running full `run_mod_test_cycle` (RESULT: PASS). This indicates the checker may miss spilled/compressed tool outputs; keep using `run_mod_test_cycle` as the authoritative final proof.
## 2026-08-21 itertest13 Feeding Helmet - new mod-loading pitfall

- **`mods.toml missing metadata for modid examplemod` / `The Mod File build\sourceSets\main has mods that were not found`**:
  - Root cause: template's `src/main/java/com/example/examplemod/{ExampleMod,Config}.java` were never deleted; they compile an extra `@Mod("examplemod")` class while mods.toml only declares the new modid, so FML sees `[BROKEN/examplemod, newmod]` but expects only `[newmod]`.
  - `gradlew clean` alone does NOT fix it (clean recompiles the leftover source).
  - Fix: delete/rename all template example source files under `src/main/java/com/example`, then `gradlew clean` + rebuild/`run_test_gametest`.
- **`gametest-check` false negative repeats** when `run_test_gametest` passed but checker still said FAILED; running `run_mod_test_cycle` once (all-in-one) refreshed state and passed. Recorded earlier as full-flow observation; it happened again in itertest13.
## 2026-08-21 itertest14 Soulbound Key - new API facts

- **`Registries.ITEM.getKey(Item)` cannot resolve symbol**:
  - In 1.21.11 `net.minecraft.core.registries.Registries.ITEM` is a `ResourceKey<Registry<Item>>`, not a `Registry`.
  - Fix: use `net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(item)` for level-less static registry lookup.
- **`Identifier.parseOrThrow(String)` does not exist**:
  - Use `Identifier.parse(id)` (throws on invalid; wrap in try/catch if needed).
- **`Player#isSneaking()` does not exist**:
  - Use `Entity#isShiftKeyDown()` or `Entity#isCrouching()`.
- **`PlayerEvent.PlayerRespawnEvent#getPlayer()` not found**:
  - The typed event is a record accessor: use `event.getEntity()` (same for `LivingDeathEvent`).
## 2026-08-21 itertest16 Chunk Loader - new API facts

- **`Block#onRemove` no longer exists (compile: method does not override / cannot find symbol)**:
  - 1.21.11 `BlockBehaviour` split the old `onRemove` into `affectNeighborsAfterRemoval(BlockState, ServerLevel, BlockPos, boolean)` (called via `ServerLevel#updateNeighboursOnBlockSet` when old state is replaced).
  - Fix: override `protected void affectNeighborsAfterRemoval(BlockState, ServerLevel, BlockPos, boolean)` and put release/cleanup logic there.
- **`import net.minecraft.gametest.framework.GameTest` cannot find symbol**:
  - Forge 1.21.11 `@GameTest` lives in `net.minecraftforge.gametest.GameTest` (attribute is `structure()`, default `forge:empty3x3x3`; no `template()`).
  - Fix: `import net.minecraftforge.gametest.GameTest;`
## 2026-08-21 itertest12/15/16 - missed API facts backfilled from session logs

Backfill pass (user request): re-scanned itertest11~16 run.logs for compile errors that were fixed but never written to this file. Adding the missing entries:

- **`CompoundTag#getString(String)` returns `Optional<String>`** (itertest12):
  - Symptom: `incompatible types: Optional<String> cannot be converted to String`.
  - Fix: `tag.getString(KEY).orElse("")` (same pattern for getInt/getLong etc. where they return Optional).
- **`Registry#getValue(Identifier)` / `BuiltInRegistries.ITEM.getValue(...)` uncertain in 1.21.11** (itertest12):
  - Safe pattern: store the item as its registry-id STRING in NBT, resolve with `ForgeRegistries.ITEMS.getValue(Identifier)`; do NOT guess vanilla Registry accessors.
- **`SnowballEntity` class name not found in 1.21.11 sources** (itertest15):
  - Fix: extend `net.minecraft.world.entity.projectile.ThrowableProjectile` directly for thrown projectiles.
- **`EntityRenderer` is now generic `EntityRenderer<T, S extends EntityRenderState>`** (itertest15):
  - Minimal custom-entity renderer trio: a custom `EntityRenderState` subclass + renderer extending `EntityRenderer<T,S>` + registration via `EntityRenderers.register`, all wired through `DistExecutor.unsafeRunWhenOn(Dist.CLIENT, ...)`.
- **`Level.isClientSide` field access can fail depending on accessor chain** (itertest15):
  - Prefer the method call `level.isClientSide()` when available; verify against mc_java_sources before using the bare field.

## 2026-08-21 itertest13 Feeding Helmet - extra API facts

- **`ArmorItem` class not found**:
  - 1.21.11 wearable items use `Item.Properties().equippable(EquipmentSlot.HEAD)` (internally `Equippable.builder(...).build()`); no ArmorMaterial needed for basic equipping.
## 2026-08-21 itertest17 Remote Lever - networking/event API facts (high value)

- **Event bus class changed**: use `net.minecraftforge.eventbus.api.bus.BusGroup` (obtained via `FMLJavaModLoadingContext.get().getModBusGroup()`); old `IEventBus`-style imports fail.
- **`PacketFlow` lives in `net.minecraft.network.protocol`**, not the network package.
- **`Identifier.of(ns, path)` does NOT exist** (compile-proven): use `Identifier.fromNamespaceAndPath(ns, path)` (Identifier.java:39).
- **`Player#sendSystemMessage(MutableComponent)` not found**: use `displayClientMessage(Component, boolean)` (Player.java:1379).
- **`Level.isClientSide` is a PRIVATE field** in this mapping: call the method `level.isClientSide()` instead.
- **ItemStack NBT round-trip**: use `ItemStack.CODEC.encodeStart(...)` / `.parse(...)`; old `stack.save/addTag` patterns are gone.
- **Channel construction (new network layer)**: `ChannelBuilder.named(Identifier)...payloadChannel()` + `Channel.send(payload, PacketDistributor.SERVER.noArg())`; `SimpleChannel` still exists but the payload-channel path is the modern one.
- **Template restoration trap (flow defect)**: template files under `src/main/java/com/example` can be auto-restored WITH `@Mod("examplemod")` → FML fails with `constructed N mods: [BROKEN, ...] but had M mods specified`. Robust fix: rewrite template classes as EMPTY classes WITHOUT `@Mod` AND delete stale `build/sourceSets/main` leftovers. (Recreating empty no-@Mod stubs also unblocks tests, but clean both is better.)
## 2026-08-21 itertest18 Waypoint Charm - registry/cooldown/interaction API facts

- **`Item.Properties.setId(...)` requires `ResourceKey<Item>`** (compile-proven): passing `Identifier` fails with `incompatible types: Identifier cannot be converted to ResourceKey<Item>`. Use `ITEMS.key("name")` from DeferredRegister or `ResourceKey.create(Registries.ITEM, id)`.
- **`ItemCooldowns.addCooldown` overloads changed**: valid overloads are `(ItemStack, int)` and `(Identifier, int)`; passing an Item instance directly no longer matches.
- **`RegistryAccess.registryOrThrow(ResourceKey<Registry<T>>)` not found**: use `lookupOrThrow(...)` (HolderLookup API) or `registry(...)` which returns Optional.
- **`Registry.get(...)` returns `Optional<Reference<T>>`** now, not T — unwrap with `.value()` after presence check.
- **`InteractionResultHolder` class does NOT exist** in 1.21.11: `Item#use` returns `InteractionResult` directly (sealed interface: Success/PASS/FAIL...).
- **Deprecation warnings (for removal)**: `ModLoadingContext.get()` and `FMLJavaModLoadingContext.get()` — config/bus registration should migrate to the new context injection when available.
## 2026-08-21 itertest19 Mood Lamp - BlockBehaviour hook signature overhaul (44-build grind, high value)

- **`getStateForPlacement(BlockPlaceContext)` no longer overrides Block** (compile: method does not override). The placement hook was renamed/re-signed in 1.21.11 — check `BlockBehaviour`/`Block` in mc_java_sources for the current name (agent resolved it by reading source; do NOT assume the old name).
- **`neighborChanged` new signature**: `neighborChanged(BlockState, Level, BlockPos, Block, Orientation, boolean...)` — the old 5th param `BlockPos` is now an **`Orientation`** object (new class; import from mc_java_sources, do not guess the package).
- **`Orientation`** is a new parameter type threaded through block hooks (placement/rotation/neighbor logic); conversions from BlockPos no longer compile.
- **`isClientSide` private field trap repeats**: agents keep writing `level.isClientSide` — ERROR_LIST entry exists but sessions still hit it; prefer `level.isClientSide()` method form everywhere.
- **Deprecation warnings pile**: `ModLoadingContext.get()` / `FMLJavaModLoadingContext.get()` marked for removal (seen again).
- Flow note: this session needed 44 compile iterations — block-hook area is the densest API-diff zone so far; budget extra cycles when a task touches custom BlockBehaviour overrides.
## 2026-08-21 itertest20 Weighted Backpack - Inventory refactor + tick event facts

- **Player inventory refactor**: equipment no longer lives on `Inventory` — fields `armor` / `offhand` are GONE.
  - Equipment is now in **`EntityEquipment`** (an `EnumMap<EquipmentSlot, ItemStack>` wrapper): `get(slot)` / `set(slot, stack)` / `isEmpty()` / `size()`.
  - Main-inventory stacks: `player.getInventory().getNonEquipmentItems()`.
  - Selected slot: `Inventory#getSelectedSlot()` (no more `selected` field access).
- **`getCarried()` not found** on the old receiver: carried/open-container stack accessor moved (verify exact owner in mc_java_sources before use).
- **Tick event relocation**: old `net.minecraftforge.event.TickEvent` path glob-empty in this mapping; locate the new tick event class before wiring `.BUS`. `ServerTickEvent.Pre` no longer exposes `getServer()` — pull the server from the event record field or `level`.
- **Attribute API note**: holder-style attribute access + `AttributeInstance` add/remove modifier calls COMPILED as guessed this round (Attributes.MOVEMENT_SPEED holder path OK).
## 2026-08-21 itertest21 Gem Kit - creative tab + eventbus facts

- **Vanilla tab references are `ResourceKey<CreativeModeTab>` constants**: `CreativeModeTabs.BUILDING_BLOCKS` etc. are created via `createKey("building_blocks")` — do NOT treat them as CreativeModeTab instances; pass the key to `CreativeModeTab.Builder` copies/`output.accept` contexts accordingly.
- **Working custom-tab pattern this round**: DeferredRegister-style tab registration + `displayItems` -> `output.accept(item)`; `BuildCreativeModeTabContentsEvent` (typed `.BUS`) available for appends.
- **`IEventBus` not found (independent repro)**: second session confirmed eventbus change — use `net.minecraftforge.eventbus.api.bus.BusGroup` / `getModBusGroup()`.
- **FLOW DEFECT — start-phase read loop**: nearly every new session burns 5-10 rounds re-reading `mc_java_sources/starter` before the first write, despite `<write-first-stop>` firing 2-4 times (this session reached supervisor ALERT). Recommendation: on session start, force-inject a ready-to-edit minimal main-class template instead of only warning.
- Grind note: main build took ~21 compile iterations (creative-tab zone); test cycle needed one retry before RESULT: PASS.
## 2026-08-21 itertest22 Lucky Pickaxe - component/event accessor facts

- **`Item.Properties.component(RegistryObject<DataComponentType<T>>, T)` does NOT compile**: `component` is generic `<T>component(DataComponentType<T>, T)` and rejects RegistryObject.
  - Fix: dereference first — `.component(ModComponents.LUCKY.get(), Unit.INSTANCE)`.
- **`BlockEvent.BreakEvent#getLevel()` returns `LevelAccessor`, not `Level`** (typed event record accessor).
  - Fix: hold as `LevelAccessor`, `instanceof ServerLevel serverLevel`, then use it for drops / `Block.popResource`.
- **FLOW DEFECT — template pollution**: the forge starter auto-copied an UNRELATED "SwapGame" template alongside examplemod files; agents must detect and delete both or the extra @Mod breaks FML. Template dir needs a cleanup upstream.
## 2026-08-21 itertest23 Coffee Rush - MobEffect registration facts

- **`Registry#getHolderOrThrow(ResourceKey)` does NOT exist** in this mapping (search-proven: zero hits in mc_java_sources).
  - Working pattern: custom MobEffect via `DeferredRegister.create(Registries.MOB_EFFECT, MODID)` (Holder-based vanilla registry); resolve the active effect with `BuiltInRegistries.MOB_EFFECT.getOrThrow(ResourceKey<MobEffect>)` (note: `getOrThrow`, not `getHolderOrThrow`).
- MobEffectInstance construction unchanged (`new MobEffectInstance(holder, duration, amplifier)`), apply via `player.addEffect(...)`.
- Session note: one ~2min silent LLM turn occurred pre-write (low CPU = network wait, not a hang); recovered and completed normally.
## 2026-08-21 itertest24 Tuning Fork - GameTestHolder removal + sound Holder facts

- **`GameTestHolder` is GONE in BOTH packages** (`net.minecraftforge.gametest` and `net.minecraft.gametest.framework` both "cannot find symbol").
  - Fix: class-level `@net.minecraftforge.gametest.GameTestNamespace(...)` only (`value()` defaults to modid).
- **`Level.playSound(...)` takes `SoundEvent`, NOT `Holder.Reference<SoundEvent>`**: vanilla constants like `SoundEvents.NOTE_BLOCK_PLING` are Holders now.
  - Fix: `level.playSound(null, pos, SoundEvents.NOTE_BLOCK_PLING.value(), SoundSource.BLOCKS, vol, pitch)`.
- **Recurring flow defect — jar name staleness**: forgetting `rootProject.name`/archivesBaseName rename produces a stale `examplemod-1.0.0.jar` alongside the real one; agent caught and cleaned this round, but the check belongs in the standard rename checklist.
## 2026-08-21 itertest25 Pebble Golem - spawn egg / RenderType / renderer pipeline facts

- **`TypedEntityData.create(EntityType)` does NOT exist**: factory is `TypedEntityData.of(T, CompoundTag)`.
  - SpawnEggItem in 1.21.11 takes only `Item.Properties` and learns its entity via **`DataComponents.ENTITY_DATA`**:
    `new SpawnEggItem(new Item.Properties().setId(ITEMS.key("egg")).component(DataComponents.ENTITY_DATA, TypedEntityData.of(TYPE.get(), new CompoundTag())))`.
- **`RenderType` moved** to `net.minecraft.client.renderer.rendertype` subpackage (old import fails).
- **EntityRenderer abstract surface changed again**: no-arg `createRenderState()` override; old `render(PoseStack, MultiBufferSource, int)` gone — drawing goes through the new submit/`render*` pipeline; follow a vanilla minimal renderer (LlamaSpit pattern from itertest15 still applies for the trio structure).
- Attributes event: entity attribute registration event located and used successfully this round (name per mc_java_sources).
## 2026-08-21 itertest26 Sparkle Dust - particle registration facts

- **Custom particle working pattern (1.21.11)**: `DeferredRegister<ParticleType<?>>` over the particle registry; register a `SimpleParticleType(true)` per particle; client provider wired via `DistExecutor.runWhenOn(Dist.CLIENT, () -> ClientClass::addParticleProviderListener)`.
- Server spawn via `ServerLevel.sendParticles(...)` (signatures verified in source).
- **FLOW DEFECT — wrap-up hang**: session hung twice with zero log output while process alive (LLM call without timeout during final wrap-up). Recovery: kill only that session's python + relaunch `run_task.py` with `DSH_RESUME=1`; breakpoint restored and completion state was intact. Consider adding an HTTP timeout to the LLM client.
## 2026-08-21 itertest27 Gem Trader - villager trade API facts

- **Trade offers moved to `net.minecraft.world.item.trading`**: `MerchantOffer` constructor now takes **`ItemCost`** objects (not raw ItemStacks) — verify `public ItemCost(...)` overloads in source before building offers.
- **Villager offer injection pattern**: read `AbstractVillager#getOffers()`, append a `MerchantOffer`, guard duplicates by checking an equivalent offer already exists; server-side interaction only.
- Grind note: heaviest session so far (~110 compile iterations) — trade/offer zone plus client-render deliberation; budget cycles accordingly.
- Agent misflagged `Item id not set` NPE as NEW_ERROR; it is already documented (setId requirement). Reminder: grep ERROR_LIST before claiming NEW_ERROR.
## 2026-08-21 infra - .env BOM breaks key parsing

- **`EntityType.ZOMBIE.create(level)` does NOT compile**: 1.21.11 requires an `EntitySpawnReason` argument.
  - Fix: `EntityType.ZOMBIE.create(level, EntitySpawnReason.SPAWN_ITEM_USE)`.
- **`ServerPlayer#serverLevel()` does NOT exist**: cast instead — `(ServerLevel) serverPlayer.level()`.
- **GameTest imports recap (hit again)**: method annotation `net.minecraftforge.gametest.GameTest`; `net.minecraft.gametest.framework.GameTestHolder` and `net.minecraftforge.gametest.framework.GameTestHolder` both absent.
- **Registry lookup in tests**: `registryAccess().registryOrThrow(...)` absent; prefer `ForgeRegistries.ITEMS.containsKey/getValue` for item presence checks.
## 2026-08-21 itertest29 Magnet Charm - flow defect: over-broad cleanup

- **FLOW DEFECT — self-deletion by cleanup**: `rmdir /s /q src\\main\\java\\com` (meant to remove template packages) deleted the agent's OWN new classes under the same `com` tree, costing ~17 rebuild iterations.
  - Fix guidance: delete exact template paths (`src/main/java/com/example`, `src/main/java/com/swapgame`) — never the shared `com` root; or move new code to a non-`com` root package.
- End-to-end RESULT: PASS after recovery; jar `magnet_charm-1.0.0.jar`.
## 2026-08-21 itertest30 Ender Pocket - container storage facts (116-build grind)

- **`ItemContainerContents` API renamed**: no `fromStacks(List)` / `getStackInSlot(int)`.
  - Serialize: `ItemContainerContents.fromItems(List<ItemStack>)`; read back: `contents.copyInto(NonNullList.withSize(...))`.
- **`RegistryAccess.registryOrThrow(ResourceKey)` definitively gone**: only `lookup(ResourceKey<? extends Registry<? extends E>>) -> Optional<Registry<E>>` remains.
- **GameTest annotation recap**: Forge ships `net.minecraftforge.gametest.GameTest` (method-level, `structure` default); `template="empty"` from vanilla and both GameTestHolder paths do not exist.
- Heaviest session yet: ~116 compile iterations on the container/Menu zone; end-to-end RESULT: PASS.
## 2026-08-21 itertest31 Weather Vane - weather API fact + SavedData notes

- **`ServerLevel.setWeatherParameters(...)` signature changed**: now `(int clearTime, int rainTime, boolean raining, boolean thundering)` — 4 args, NO separate thunderTime.
- SavedData placement registry pattern worked: `DimensionDataStorage.computeIfAbsent(SavedDataType...)` (verify exact overload per source); update loop only touches loaded chunks.
- End-to-end RESULT: PASS; jar `vane-1.0.0.jar`.
## 2026-08-21 itertest32 XP Well - ValueIO package + event bus registration facts

- **`ValueOutput`/`ValueInput` live in `net.minecraft.world.level.storage`** (not `net.minecraft.core`); writer methods are `putInt`-style, NOT `writeInt` (reference: AbstractFurnaceBlockEntity#saveAdditional).
- **`EVENT_BUS.register(modClass)` throws `IllegalArgumentException: Failed to register ... No declared methods found`** when the class has NO `@SubscribeEvent` methods.
  - Fix: only register classes that actually contain `@SubscribeEvent` handlers; otherwise skip registration entirely.
- End-to-end RESULT: PASS; jar `xpwell-1.0.0.jar`.
- Ops note: this session required two kill+resume cycles for no-timeout LLM hangs (endpoint instability tonight); both recoveries clean.
## 2026-08-21 itertest33 Torch Bow - entity synched data + spawn facts

- **`defineSynchedData` is abstract on Entity and takes a Builder from `net.minecraft.network.syncher`** (NOT `synched`/`syncheddata` packages); override signature: `protected void defineSynchedData(SynchedEntityData.Builder builder)` and register entries via `builder.define(...)`.
- **`Entity.spawnAtLocation(ItemStack)` not found**: now requires a `ServerLevel` first arg (e.g. `spawnAtLocation(serverLevel, stack)`).
- **`InteractionResult.sidedSuccess(...)` gone (re-confirms sealed InteractionResult)** — return SUCCESS/SUCCESS_SERVER/CONSUME/PASS directly.
- End-to-end RESULT: PASS; jar `torchbow-1.0.0.jar`.
## 2026-08-21 itertest34 Beacon Compass - tooltip/scan facts

- **Tooltip hook**: agent verified the current appendHoverText-equivalent signature directly from Item source before use (historically renamed; always re-check `Item.java` for the exact name in this mapping).
- **`Level.hasChunkAt` now takes a BlockPos** (not int coords) — relevant for cube scans around a player.
- Minor self-import clash (`ModConfig` defined twice in same compilation unit) — mod-specific naming, not an API fact.
- End-to-end RESULT: PASS; jar `beaconcompass-1.0.0.jar`.
## 2026-08-21 itertest35 Anvil Repair - durability accessor facts

- **ItemStack damage accessors in 1.21.11** (verified from source this round): `getDamageValue(ItemStack)`-style statics on the class were NOT the shape used; agent resolved via `ItemStack.java` — record whatever compiled: damage read/write goes through the DataComponents-backed accessors (`stack.set(DataComponents.DAMAGE, n)` / `stack.get(...)`), not legacy `setDamageValue`.
- End-to-end RESULT: PASS first cycle; jar `anvilrepair-1.0.0.jar` (8,712 B). Clean session (one early write-first-stop only).
## 2026-08-21 itertest36 Growth Powder - blockstate property iteration fact

- **`BlockState#getProperties()` returns `Collection<Property<?>>`, not a Map** — `.keySet()` does not exist.
  - Fix: iterate the collection directly (`for (Property<?> p : state.getProperties())`), or use `getValues().keySet()` if a key view is needed.
- Crop age boost via `AGE_*` IntegerProperty worked with manual clamping; particles via ServerLevel.sendParticles fine.
- End-to-end RESULT: PASS; jar `growthpowder-1.0.0.jar`.
## 2026-08-21 itertest37 Soul Lantern Pet - inventoryTick fact

- **`getFriction()` override compiled on the custom block this round** (0.15f low-friction value); the hook name survived in this mapping (unlike getStateForPlacement/neighborChanged). Always verify against BlockBehaviour source per-block-hook anyway.
- Recurring flow defect re-hit: dist jar still named `examplemod-1.0.0.jar` — the rootProject.name rename checklist keeps being skipped; consider enforcing via prompt template or launcher-side check.
## 2026-08-21 itertest39 Feather Fall - SESSION FAILED (BROKEN mod persisted)

- **Session ended RESULT: FAIL** after many attempts: FML kept reporting `mods.toml missing metadata for modid examplemod` / `constructed N mods: [BROKEN,...]` during GameTest, despite deleting com/example sources and editing mods.toml/build.gradle.
  - Root cause analysis: stale compiled outputs under `build/sourceSets/main` survived every partial fix; agents edited sources/metadata but did not reliably purge the whole `build/` directory.
  - PROCESS FIX (upstream): `run_mod_test_cycle`/launcher should delete the entire `build/` directory once before GameTest when a BROKEN-mod error is detected; or template sessions should never ship pre-built `build/` dirs.
  - Main jar DID build (`featherfall-1.0.0.jar`, 12,244 B) — failure is GameTest-environment only.
- First FAIL of the series since itertest11-era; retry scheduled as itertest40 with explicit `rmdir /s /q build` instruction.
## 2026-08-21 itertest40 Feather Fall retry - SESSION FAILED (test-source symbol errors)

- **Second consecutive FAIL on Feather Fall**: this time NOT the BROKEN-mod trap (anti-BROKEN checklist worked) but repeated `找不到符号` compile errors inside the GameTest sources across many attempts; session ended with no dist jar.
## 2026-08-21 itertest41 Lucky Rabbit Foot - FAILED (max rounds), model strategy adjustment

## 2026-08-22 itertest42 Speedy Boots - equippable/inventoryTick facts + agent output-churn defect

- **Equippable item pattern compiled first try**: `new Item.Properties().setId(ITEMS.key("speedy_boots")).equippable(EquipmentSlot.FEET)`; speed refresh via `inventoryTick` -> `player.addEffect(new MobEffectInstance(MobEffects.SPEED (holder), 60, 0))` server-side only; `MobEffects.SPEED` holder name confirmed.
- **AGENT DEFECT — unread background outputs**: agent launched `gradlew runTestGameTestServer` via background + ping-wait, then re-launched repeatedly WITHOUT reading `gametest_final*.txt`; the test had actually passed ("All 1 required tests passed :)", BUILD SUCCESSFUL). Fix guidance: after any background command, READ the redirected output file before retrying; a passing gametest log + existing dist jar means DONE — stop looping.
- Session was terminated by supervisor once completion criteria were objectively met (jar archived as speedyboots-success-1.0.0.jar).
## 2026-08-22 itertest43 Torch Toss - projectile package + cooldown owner facts

- **Vanilla `Snowball` entity class moved**: `net.minecraft.world.entity.projectile.Snowball` not found — the throwable-item entities now live in a `throwableitemprojectile` subpackage; check mc_java_sources for the exact path before importing.
- **`Item#addCooldown(ItemStack,int)` does NOT exist on Item** (compile-proven): the overload lives on `ItemCooldowns` — call `player.getCooldowns().addCooldown(stack, ticks)`.
- End-to-end RESULT: PASS first cycle on ox-alpha-free; jar `torchtoss-1.0.0.jar`.
## 2026-08-22 itertest44 Glow Berry Jam - FoodProperties.effect signature

- **`FoodProperties.Builder.effect(...)` takes TWO args**: `(Supplier<MobEffectInstance>, float probability)` — e.g. `.effect(() -> new MobEffectInstance(MobEffects.GLOWING, 200, 0), 1.0F)`; a bare single-supplier call does not compile.
- Nutrition/saturation builder methods compiled as expected; food route avoids events entirely (good fit for simple items).
- End-to-end RESULT: PASS on ox-alpha-free; jar `glowberryjam-1.0.0.jar`.
## 2026-08-22 itertest45 Ladder Plus - climbable/interaction hook names

- **Climbable hook survived as `isLadder(BlockState, Level, BlockPos, Entity)`** on Block/BlockBehaviour (verified via TrapDoorBlock override and the ForgeHooks#isSprintableClimbable call site).
- **Right-click-without-item hook is `useWithoutItem`** (not use()) in this mapping — new name for empty-hand block interaction.
- End-to-end RESULT: PASS; jar `ladderplus-1.0.0.jar`.
## 2026-08-22 itertest46 Compass Reset - respawn setter signature

- **`ServerPlayer.setRespawnPosition` changed to TWO args**: `setRespawnPosition(ServerPlayer.RespawnConfig, boolean)` where `RespawnConfig` is a nested @Nullable record (dimension+pos+angle bundle). The old 5-arg `(ResourceKey, BlockPos, float, boolean, boolean)` form does NOT exist.
  - Clear respawn point: `serverPlayer.setRespawnPosition(null, false)`.
- End-to-end RESULT: PASS; jar `compassreset-1.0.0.jar`.
## 2026-08-22 itertest47 Frost Arrow - PARTIAL (jar built, GameTest never ran) + echo-loop defect

- Session degenerated into launching meaningless background `echo` tasks (bg_17..bg_23) after the jar built; GameTest was never executed. Terminated by supervisor; jar `frostarrow-1.0.0.jar` archived as partial.
- **AGENT DEFECT — echo-loop**: under ox-alpha-free, agents sometimes fill turns with placeholder background echos instead of real work. Recovery: kill + resume; if it persists across resumes, restart the session fresh.
- ox-alpha-free stability note: intermittent empty-response episodes persist (2 kills this session); model quality is noticeably below DeepSeek/GLM-4.5 for long agentic loops.
## Build/Compile

- **[iterauto_026] error: read the first `error:`, fix one place with the mapped API, rebuild; do not speculate more than**
  - Context: `/`max_format` form; do not replace with only `supported_formats`, otherwise the mod resource pack metadata is rejected with a WARN/ERROR.
- After writing code: immediately `validate_resources` -> `run`

- **[iterauto_001] - On compile error: read the first `error:`, fix one place with the mapped API, rebuild; do not speculate more than**
  - Context: `/`max_format` form; do not replace with only `supported_formats`, otherwise the mod resource pack metadata is rejected with a WARN/ERROR.
- After writing code: immediately `validate_resources` -> `run`

- **[iterauto_001] BUILD FAILED in 18s**


- **[iterauto_001] BUILD FAILED in 21s**

- **[iterauto_001] 4. Got a compile error: `Registries.CREATIVE_MODE` is not the correct constant**


- **[iterauto_001] {"success": false, "exit_code": 1, "summary": "TestGameTestServer FAILED", "error_details": {"type": "compile_error", "message": "BUILD FAILED", "file_location": ""}, "raw_logs_snippet": "To honour th**


## 2026-08-23 Auto-recorded from runtime

- **Auto-recorded:** -time exception; missing object at injection → debug log, no injection.
- **Auto-recorded:** Registries - Forge Documentation Navigation Docs: MinecraftForge ForgeGradle Version: 1.21.x 1.20.x 1.20.1 1.19.x Home Contributing to the Docs Getting Started Introduction The Mod Files Structuring Your Mod Versioning C
- **Auto-recorded:** Also mention packs.mcmeta? For mods, resources live in src/main/resources with META-INF/mods.toml. The pack.mcmeta is typically generated by Forge automatically for mods... In modern Forge MDK, resources dir doesn't need


- **[iterauto_001] BUILD FAILED in 11s**


- **[iterauto_001] BUILD FAILED in 13s**











- **[iterauto_002] BUILD FAILED in 14s**


- **[iterauto_004] BUILD FAILED in 15s**

- **[iterauto_004] 5. Ran full mod test cycle (build + GameTest) - build failed (exit=1)**

- **[iterauto_004] 6. The agent identified a compile error: `ItemTags.bind()` is private, needs to use `TagKey.create()` instead**







- **[iterauto_004] - Client verification failed (tool error: `cannot access local variable 'out' where it is not associated with a value`) — this is a tool bug, not the agent's fault**





- **[iterauto_004] (local recompiled.jar); on "Could not resolve" check the cache / retry the network; don't rewrite build files**

- **[iterauto_004] - `NEW_ERROR: ItemTags.bind() is private | 1.21.11中bind()变private | 用 TagKey.create(Registries.ITEM, Identifier.fromNamespaceAndPath())`**

- **[iterauto_004] - `NEW_ERROR: ResourceLocation 找不到符号 | 1.21.11重命名为Identifier | import net.minecraft.resources.Identifier, 用 fromNamespaceAndPath()`**

- **[iterauto_004] - `NEW_ERROR: GameTest/GameTestHolder 找不到 | 注解包路径变更 | import net.minecraftforge.gametest.GameTest + GameTestNamespace, 不用@PrefixGameTestTemplate`**

- **[iterauto_004] - `NEW_ERROR: 配方解析失败 No key type | 1.21.11 key值需字符串 | key中用 "minecraft:emerald" 而非 {"item":...}`**

- **[iterauto_001] BUILD FAILED in 29s**





- **[iterauto_001] NEW_ERROR: 这次的错误是 JPMS 模块层冲突 - "Modules test and titaniummod export package com.titaniummod"。这是因为在 src/main 和 src/test 中都使用了相同的包名 `com.titaniummod`，导致 Forge 的 JPMS 模块系统无法解析。解决方法是将测试类放在不同的子包中（如 `com.titaniummod.test`）。**

- **[iterauto_001] `NEW_ERROR: Failed to create module layer GAME - Modules test and titaniummod export package com.titaniummod | src/main 和 src/test 使用了相同的 Java 包 com.titaniummod，导致 Forge JPMS 模块层冲突（两个模块不能导出同一包） | 将测试类放在不同的子包中（如 com.titaniummod.test），使 src/main 和 src/**

- **[iterauto_002] BUILD FAILED in 19s**






- **[iterauto_002] 7. Hit a compile error: `SubscribeEvent` not found in `net.minecraftforge.eventbus.api`**

- **[iterauto_002] BUILD FAILED in 25s**

- **[iterauto_002] gent/ERROR_LIST.md:595: - **`import net.minecraft.gametest.framework.GameTest` cannot find symbol**:**

- **[iterauto_002] - Hit a compile error: `SubscribeEvent` not found in `net.minecraftforge.eventbus.api`**












- **[iterauto_002] - [143-148]: New error: "Caught exception during event RegisterEvent dispatch" with "Block id not set" NullPointerException**

- **[iterauto_002] 1. First error: automatic subscriber registration failure (bus mismatch) → fixed**

- **[iterauto_002] 3. New error: NullPointerException "Block id not set" during RegisterEvent dispatch**

- **[iterauto_002] - First error: wrong bus for event → removed the subscriber**

- **[iterauto_002] - Second error: Block id not set → added setId() calls**

- **[iterauto_002] NEW_ERROR: `NullPointerException: Block id not set` during RegisterEvent | 1.21.11 中 Block/Item 的 Properties 必须调用 `.setId(registry.key("name"))` | 在 `BlockBehaviour.Properties.of()` 链中添加 `.setId(BLOCKS.key("voidstone"))`，BlockItem 的 `new Item.Propert**


- **[iterauto_003] BUILD FAILED in 24s**










- **[iterauto_003] 2. It ran a build/test cycle which succeeded for main code but failed for `compileTestJava` with "cannot find symbol" errors related to Minecraft/Forge imports.**



- **[iterauto_003] - `compileTestJava` failed with "cannot find symbol" errors - test source set couldn't find Minecraft/Forge classes**

- **[iterauto_003] - Then rebuilt - got another error: `getDefaultMaxDamage()` doesn't exist on Item in this version**

- **[iterauto_003] - Step [75]: Build attempt - compileTestJava failed (cannot find symbol)**

- **[iterauto_003] 1. First failure (step 77): "cannot find symbol" - test source set can't find MC/Forge classes**


- **[iterauto_003] 6. The `run_test_client` tool failed with an error: "cannot access local variable 'out' where it is not associated with a value"**

- **[iterauto_004] BUILD FAILED in 17s**

- **[iterauto_004] BUILD FAILED in 20s**

- **[iterauto_004] 894:- **[iterauto_004] - `NEW_ERROR: GameTest/GameTestHolder 找不到 | 注解包路径变更 | import net.minecraftforge.gametest.GameTest + GameTestNamespace, 不用@PrefixGameTestTemplate`****




- **[iterauto_004] 2. Missing texture (purple/black) - checkable by viewing item in inventory**


- **[iterauto_004] NEW_ERROR: ToolMaterial构造器参数不匹配 | 1.21.11中ToolMaterial是record，构造器签名为 (TagKey<Block>, int, float, float, int, TagKey<Item>) 共6个参数，顺序为：incorrectBlocksForDrops, durability, speed, attackDamageBonus, enchantmentValue, repairItems | 参考ToolMaterial.NETHERI**

- **[iterauto_005] BUILD FAILED in 22s**








- **[iterauto_006] BUILD FAILED in 23s**



- **[iterauto_006] NEW_ERROR: `run_test_client` 报 `cannot access local variable 'out'` | 低内存服务器环境下客户端工具内部异常 | 改用 validate_resources + verify_artifact 静态验证，标注「客户端渲染由用户本地验证」。**

- **[iterauto_005] BUILD FAILED in 27s**

- **[iterauto_005] BUILD FAILED in 16s**





- **[iterauto_007] `NEW_ERROR: EntityType.create(Level) 单参数签名已移除 | 1.21.11 需要额外的 EntitySpawnReason 参数 | 使用 create(level, EntitySpawnReason.TRIGGERED) 等`**


- **[iterauto_010] 5. At line [115], `run_test_client` fails with a Python error: "cannot access local variable 'out' where it is not associated with a value"**

- **[iterauto_010] NEW_ERROR: `Pack declares support for format 0, but game versions supporting formats 17 to 81 require a supported_formats field` | pack.mcmeta 同时包含 `pack_format: 0` 和 `min_format`/`max_format` 字段，1.21.11 要求纯 `min_format`/`max_format` 形式，不能混入 `pack_fo**

- **[iterauto_011] 2. At line 88, there's a validation error: texture not found for 'crystaltree:bloc...' (truncated)**













- **[iterauto_011] `NEW_ERROR: LeavesBlock is abstract | 1.21.11 LeavesBlock 标记为 abstract，需子类实现 codec()（MapCodec）和 spawnFallingLeavesParticle(Level, BlockPos, RandomSource) | 参照 TintedParticleLeavesBlock 创建子类`**

- **[iterauto_011] `NEW_ERROR: TreeConfiguration 字段名变更 | configured_feature tree 配置中 block_provider/leaves_provider 不再存在 | 改用 trunk_provider/foliage_provider（见 TreeConfiguration.CODEC 源码）`**

- **[iterauto_011] `NEW_ERROR: @GameTest 注解无 value() | net.minecraftforge.gametest.GameTest 不接受字符串参数 | 直接用 @GameTest 无参形式，默认 structure=forge:empty3x3x3`**












- **[iterauto_012] `NEW_ERROR: pack.mcmeta min_format/max_format 被1.21.11运行时拒绝 | 1.21.11 Forge运行时要求pack.mcmeta使用supported_formats字段而非min_format/max_format | 将"min_format":18,"max_format":99替换为"supported_formats":[18,81]，错误消息明确提示此修复`**



































- **[iterauto_008] BUILD FAILED in 26s**






- **[iterauto_008] `NEW_ERROR: BlockEvent.BreakEvent 构造的 Result 参数找不到符号 | Result 类在 1.21.11 中是 net.minecraftforge.common.util.Result，不是 net.minecraftforge.eventbus.api.Event.Result（后者不存在） | import net.minecraftforge.common.util.Result; 用 Result.DEFAULT / Result.DENY`**












- **[iterauto_011] 3. At step [118], it found a compile error: `getModBusGroup()` returns a `BusGroup` interface that doesn't have `addListener` method.**






- **[iterauto_011] - `NEW_ERROR: configured_feature tree JSON "No key decorators in MapLike" | 1.21.11 tree feature 的 codec 要求 decorators 字段必须存在（即使为空数组） | 添加 "decorators": []`**

- **[iterauto_011] - `NEW_ERROR: configured_feature tree JSON "Unknown registry key ... trunk_placer_type: minecraft:straight_trunk" | 1.21.11 trunk placer 注册表 key 是 "straight_trunk_placer" 不是 "straight_trunk" | 使用 "type": "minecraft:straight_trunk_placer"`**



























## 2026-08-30 本地网站实测（rubymod / blueberry）
- **[webserv_ruby] `NEW_ERROR: shaped 配方加载即失败："Couldn't parse data file 'rubymod:ruby_block'" + "No key type in MapLike[{"item"...}]" | 1.21.11 的配方 ingredient codec 只接受纯字符串（或字符串数组），{"item": "xxx"} 对象形式 build 期完全通过、仅在 GameTest/服务器 datapack 加载时报 parse error（藏在 run/logs/latest.log 数据包加载段，极易漏诊） | shaped/shapeless 配方的 ingredient 一律写纯字符串（如 "minecraft:iron_nugget"）；validate_resources 只对 shapeless 给同类警告，修一条时要同步检查 shaped 配方（rubymod 实测因此多花一轮构建+GameTest）**`

- **[webserv_stardust] `NEW_ERROR: GameTest 里 ServerLevel.getRecipeManager() 找不到符号 | 1.21.11 映射中 RecipeManager 不在 ServerLevel 上 | 改用 helper.getLevel().getServer().getRecipeManager()`**
- **[webserv_stardust] `NEW_ERROR: RecipeManager.byKey(Identifier) 参数类型不兼容 | 该版本 byKey 需要 ResourceKey<Recipe<?>> 而非 Identifier | 用 ResourceKey.create(Registries.RECIPE, Identifier.parse("modid:recipe")) 传入`**

## 2026-08-30 本地网站实测（webserv_rubysword / amber / stardust）
- **[webserv_rubysword] `NEW_ERROR: 注册方块时 RegisterEvent 抛 "Block id not set" NullPointerException | 1.21.11 Block 注册必须显式 setId | Block.Properties.create() 后链式 .setId(ResourceLocation)（Item 同理），或 Item.Properties().setId(...)`**
- **[webserv_rubysword] `NEW_ERROR: Identifier.of(String, String) 不存在 | 1.21.11 Mojmap 官方映射的 Identifier 构造不是 of() | 用 Identifier.fromNamespaceAndPath(modid, name) 或 Identifier.parse("modid:name")`**
- **[工具bug已修] gradletools._run_gradle 超时分支 out 变量 UnboundLocalError（历史 ERROR_LIST 记录过的 run_test_client 工具错误，本次根治）**

## 2026-08-30 本地网站实测（webserv_topaz + AgentBridge 移植记录）
- **[环境事实] 本工程锁定的 Forge 1.21.11-61.2.0 用 eventbus 7.0.5（每事件一条总线）| 无 net.minecraftforge.eventbus.api.SubscribeEvent（在 api.listener 包）也无 MinecraftForge.EVENT_BUS.register(Object) | 订阅：事件类自带静态 BUS 字段，如 TickEvent.ClientTickEvent.Post.BUS.addListener(this::onTick)——注意 TickEvent 嵌套名是 ClientTickEvent 不是 mc_java_sources 里的 Client**
- **[环境事实] mc_java_sources_1.21.11 参考树与运行时 61.2.0 存在 API 差异（TickEvent 结构 / AbstractWidget.visible 是公有字段而非 isVisible()）| 查不到符号时先 javap 运行时 jar：~/.gradle/caches/minecraftforge/forgegradle/mavenizer/caches/maven/forge/net/minecraftforge/forge/1.21.11-61.2.0/official/1.21.11/recompiled.jar**
- **[工具] 新增 AgentBridge 进程内 UI 桥（starter/bridge/AgentBridge.java + bridge_command 工具）：直接调按钮 onPress(InputWithModifiers)、EditBox.setValue、sendCommand、Screenshot.grab(File,RenderTarget,Consumer) 全部实测签名可用；进 src/test 需 run_test_client 启动**

- **[工具bug已修-webserv_lapisamulet] run_test_client 超时只杀 gradle 包装进程，游戏是 daemon 子进程幸存成僵尸客户端；第二个客户端共用 run/ 目录导致锁冲突崩溃（表现为"启动了两个客户端"）| 根治：run* 游戏型任务一律 --no-daemon（树杀可达游戏），启动前先杀本工作区残留 runClient java；新增 start_mc_test_client 非阻塞启动（process_manager 托管，stop_mc_process 可停）**
- **[AgentBridge 使用要点] 主 mod 用反射挂载（main 源集不能硬引用 test 类）:try { Class.forName("com.agentbridge.AgentBridge").getConstructor().newInstance(); } catch (Throwable ignored) {}；就绪标志 wait_for_log "[AgentBridge] armed"；桥对 CWD 兼容（项目根或 run/ 均可）**

## 2026-08-30 AgentBridge 桥接实战定稿（webserv_moonstone 手动闭环验证）
- **[核心事实] test 源集类运行在 SECURE-BOOTSTRAP 模块加载器（module test），其 Minecraft/eventbus 类是与 app 加载器重复的副本：事件订阅 LinkageError、Minecraft.getInstance() 读到空静态 | 桥/自动化代码必须放 src/main（与主 mod 同加载器），用 build.gradle 存在性守卫（注意 dev 客户端 CWD 是 <项目>/run，要两级探测 ..uild.gradle）让生产 jar 自动失活**
- **[核心事实] 按钮操作必须在渲染线程执行（RenderSystem 断言）：非按钮 onPress 的代码经 mc().execute() 投递 + CountDownLatch 等待；screen_info 只读可任意线程**
- **[核心事实] Screenshot.grab(File, RenderTarget, Consumer) 的 File 是【目录】语义（实际写 <dir>/screenshots/<时间戳>.png），且必须在渲染线程调用，PNG 由 ioPool 异步落盘——调用方按 mtime 轮询取新文件**
- **[已验证闭环] 主菜单→Singleplayer→Create New World→进世界→/give→游戏内截图 全程桥驱动成功（免焦点/免模拟输入/后台窗口可截图）；世界列表条目不是 AbstractButton（click 会正确拒绝），进世界用 Create New World 路径**
- **[API] GLM-5.3-flash（智谱 open.bigmodel.cn/api/paas/v4）可跑通全流程：写码/构建/GameTest/ERROR_LIST 查错均正常；注意余额（429 code 1113=余额不足）**

## 2026-08-30 完全后台模式定稿 + webserv_emeraldheart 发现
- **[已验证] 完全后台客户端验证可行：MC 窗口用 LAYERED+TRANSPARENT+alpha=0 样式隐身（GLFW 每帧自管位置会拉回 SetWindowPos，但不会重置 EXSTYLE）| 点击穿透不影响用户，渲染循环正常（隐形截图 17441 独立色/5.5% 黑=真实帧），桥的函数级点击/游戏内截图全部照常 | start_mc_client 已内置自动隐身（DSH_MC_BACKGROUND=0 关闭）**
- **[webserv_emeraldheart] NEW_ERROR: AgentBridge 在专用服务器被 RuntimeDistCleaner 拒载 | 客户端专属类进 dist 会被 GameTest 服务端拒绝 | 反射挂载 + FMLEnvironment.dist.isClient() 守卫**
- **[webserv_emeraldheart] NEW_ERROR: src/test 与 src/main 同包名导致 ResolutionException: Modules test and <modid> export package（split-package，GameTestServer 启动即崩）| 1.21.11 把两者编译为独立 JPMS 模块 | 测试类放子包 com.<modid>.tests**

## 2026-08-30 webserv_obsidiandagger（glm-5.3 全后台验收轮）
- **[webserv_obsidiandagger] NEW_ERROR: ItemAttributeModifiers.Entry.matches(Holder) 编译报错需要双参数 | 1.21.11 Entry.matches 需要 (Holder<Attribute>, Identifier 修改器id) | Entry 构造用 Identifier.fromNamespaceAndPath(modid, "damage_id") 显式给修改器命名**
- **[验收] glm-5.3（智谱 Coding Plan 端点 /api/coding/paas/v4）+ AgentBridge 完全后台流程全自主跑通：armed→隐身窗口→screen_info/click 建世界→开作弊→/give→后台截图→analyze_image→stop_mc_process，全程用户桌面零打扰；出口闸失明由 3 次打回+dist jar 兜底正确收尾**

## 2026-08-31 webserv_sweetberrypie（终验轮）
- **[已验证-终验] glm-5.3 完整产出 MOD：jar 全资产齐（定义/模型/纹理/双语/配方）+ GameTest 双 PASS + 隐形客户端内 /give 成功（聊天日志"已将1个[甜甜浆果派]给予Dev"）+ 三级视觉核验（全景/快捷栏裁剪/纹理预览）；全程用户桌面零打扰**
- **[教训] 视觉识图会误判小图标（把派认成红蘑菇）| 小图标判定以纹理预览放大图 + 游戏聊天 give 回执 + GameTest 为准，最多 2-3 次 analyze_image；重建世界复验是烧轮数的主因（本轮 100 轮上限收尾）| 已写入 TOOL_GUIDE 验证预算**
- **[修正] AgentBridge.class 曾被打进发布 jar | 模板 build.gradle 已加 tasks.named('jar'){ exclude 'com/agentbridge/**' }（生产无害但保持产物干净）**

## 2026-08-31 webserv_celestialheaven（天国维度——本项目最复杂 MOD 马拉松）
- **[终验通过] 全新维度全链路自主产出：dimension+dimension_type+noise_settings+biome+configured_feature 完整 JSON 链（61 文件 jar）、天石/天晶/云绒草/天使之羽、GameTest 4/4 绿、服务端无 datapack 错误、隐形客户端内 /execute in 天国维度传送成功 + 3 次识图（最终 Yes）、git 快照 a7baf7ae**
- **[webserv_celestialheaven] NEW_ERROR: AgentBridge 在 @Mod 构造器直接 new 使专用服务端崩（GuiEventListener DEDICATED_SERVER 拒载）| 客户端专属类必须 FMLLoader.getDist().isClient() 守卫 | agent 已自行修复**
- **[工具gap已修] press_key/game_input 无右键键名（"right"=方向键）| 无法程序化使用物品（传送羽毛等）| _VK_MAP 新增 right_click/use/mouse_right→VK_RBUTTON(0x02)、left_click/attack→VK_LBUTTON(0x01)**
- **[模型教训] glm-5.3 批量加载 10 技能→上下文过载→连续 39 次空响应死循环 | 复杂任务也要守住"最多 3 个技能"纪律；引擎侧已加空响应连续上限（5 次压缩/8 次收尾）**

## 2026-08-31 webserv_storm（风暴要塞 + Boss 实体）
- **[终验通过] Boss 实体全链路：EntityType+属性(100血/20攻)+近战AI+ServerBossEvent血条+客户端模型渲染器+刷怪蛋；隐形客户端内 summon 后识图确认紫色血条"Storm Lord"、贴图无缺失、近战 AI 击杀测试玩家（死亡界面=AI+伤害铁证）；GameTest 全绿；64 文件 jar**
- **[实体 API 坑] ResourceKey.create(Registries.LEVEL_STEM...) 符号定位与 moveTo(double,int,double,int,int) 签名是实体类高频编译错误（8 次迭代修复）| 写实体前先 search_api 确认 EntityType.Builder / registerAttributes 精确签名**
- **[引擎] MAX_TOTAL_ROUNDS=150 硬顶首次实战正确收尾（无无限循环）**

## 2026-08-31 webserv_stardustenergy（多系统联动）
- **[终验通过] BlockEntity 双系统联动：发电机(燃料→能量 NBT) tick 产出 → 相邻聚能器自动接收（服务端跨方块传输）→ 能量水晶右键充能（custom_data Charge）；GameTest 断言能量流转与 NBT；客户端零 missing 警告；55 文件 jar**
- **[1.21.11 物品 NBT] 给玩家带 NBT 物品用组件语法：/give @s mod:item[minecraft:custom_data={Charge:1000}]（旧 nbt:{} 语法已废）**
- **[验证方法论] 方块实体类 MOD 的可玩性验证以 /data get block 能量值 + GameTest 断言 + 客户端日志零警告为准（远景截图常拍不到目标，勿反复重拍）**

## 2026-08-31 webserv_starduststation（GUI 机器 + 网络同步 + 交互自动化攻坚）
- **[终验通过] ContainerMenu+Screen+EnergySyncPayload 全链路：桥 interact 进程内右键充能台 → InteractionResult.Success → ChargingStationScreen 实际打开（screen_info 确认+截图 GUI 面板渲染）；GameTest 过；57 文件 jar**
- **[新op] AgentBridge.interact：显式 x/y/z（或 where=below）构造 BlockHitResult → gameMode.useItemOn；PASS 时兜底 bs.useWithoutItem + 手动 ServerboundUseItemOnPacket | SendInput use 键在失焦/鼠标被抓时不可靠，世界交互一律用 interact（零焦点）**
- **[坑] player.pick 射线在眼睛高度——瞄脚部高度方块必 MISS（返回走物品分支得 Pass）| interact 用显式坐标，不依赖 pick**
- **[坑] 世界未开作弊（Allow Commands OFF）时一切命令报 "Unknown or incomplete command"（不是命令拼错！）| 桥建世界必须先点 Allow Commands 再 Create**
- **[1.21.11 GameTest 新注册] TEST_FUNCTION/TEST_INSTANCE 纯代码路线（Holder.direct 内联环境）可替代注解扫描； datapack JSON 需 "type":"minecraft:function" dispatch key**

## 2026-08-31 webserv_voidwarden（Boss 战机制——双向战损实测）
- **[实战验证] 双向战损达成（权威日志）：玩家被 Boss 击杀 4 次（Dev was slain by Void Warden）+ Phase II 成功触发（Void Warden tears open the void! Phase II!）+ Boss 血量 80→41（桥 attack op 进程内近战实测掉血）+ /kill 终结掉 3 实体**
- **[实现确认] VoidWardenEntity：Phase 引用 17 处、Voidling 召唤 5 处、50% 血量阈值判定在位；VoidWardenBossTest 覆盖 Health/Voidling/spawn 断言**
- **[实战教训] 桥 attack 返回的 hp 是实例侧缓存，权威血量用 /data get entity 查询；玩家侧 regeneration 效果在 Boss 近战压制下时灵时不灵（正常）**
- **[流程教训] 高复杂度任务 GameTest 基建（新注册机制）耗掉大量预算导致客户端验证预算不足（MAX 150 轮）；建议引擎为"客户端验证阶段"单独预算，避免与基建调试混用**


## 2026-08-31 rubysword 会话 4e9bcf6328e5（红宝石剑——出口闸/误报/桥三连坑）

- **`RESULT: PASS` 藏在输出末尾导致出口闸失明**：run_mod_test_cycle 原来把判定行放最后，主循环完成信号按 startswith 匹配永远看不到 → jar+全绿也收不了尾，烧满 100 轮。修复：判定行置于输出第一行。
- **GameTest 假阴性（配方旧格式噪音）**：数据包解析错误行含 "Failed to parse"，被 `FAILED|Failed to|Exception` 宽松正则当成测试失败，实际 "All 1 required tests passed"。修复：显式通过标记优先判定，失败只认 `required tests failed|tests failed|FAILED!`。
- **AgentBridge 无 dist 守卫炸专用服务器**：`new com.agentbridge.AgentBridge()` 未加 `FMLEnvironment.dist.isClient()` 守卫 → runTestGameTestServer 加载客户端类报 DISTXFORM。修复：构造器末尾守卫式实例化（见 KNOWN_ISSUES 条目）。
- **1.21.11 测试代码 API 陷阱**：`ItemStack.getAttributeModifiers(EquipmentSlot)` 已删除（用 `DataComponents.ATTRIBUTE_MODIFIERS`）；`ServerLevel.getRecipeManager()` 不存在（`level.getServer().getRecipeManager()`），且 `byKey` 收 `ResourceKey<Recipe<?>>` 不收裸 `Identifier`。
- **配方 key 旧格式**：`"key": {"R": {"item": "minecraft:redstone"}}` 在 1.21.11 报 "No key type"；必须纯字符串 `"R": "minecraft:redstone"`。


## 2026-09-01 jarverify（真实客户端装机实测——方块物品名 key 前缀坑）
- **1.21.11 BlockItem 翻译前缀默认是 `item.`**：`Item.Properties` 默认 `descriptionId = ITEM_DESCRIPTION_ID`（Item.java:411），BlockItem 不会自动改前缀。lang 写 `block.<modid>.<name>` 时注册必须显式 `.useBlockDescriptionPrefix()`，否则游戏内名字原样回显 `item.rubylamp.ruby_lamp`（run/mods 装 jar + /give 实测）。
  修复（二选一）：注册时 `.useBlockDescriptionPrefix()`，或 lang 直接用 `item.` 前缀。
  此前 GameTest 与图标验证都发现不了（断言看数值、识图看纹理，都不看名字）——/give 回执是唯一可靠检查点。
- **dev runClient 的 classpath 资源与 jar 不完全一致**：验证翻译/资源问题必须用构建出的 jar 装进 run/mods 测，别只信 dev 运行。
- **dev classpath mod 与 run/mods 同 modid 会重复加载冲突**：装 jar 测试要选 classpath 是另一 modid 的工作区。

## 2026-09-01 Auto-recorded from runtime

- **Auto-recorded:** throw new IllegalStateException("Item cannot have both durability and be stackable");
- **Auto-recorded:** So the user's bug: they have (per old 1.20.x convention) `"block.<modid>.<name>"` in `zh_cn.json`, but the BlockItem's actual translation key is `item.<modid>.<name>` → key not found → raw key echo `item.<modid>.<name>`.


## 2026-09-01 guiverify（储物柜真机实测——BlockEntity 容器接口坑）
- **方块实体容器必须 `implements Container`**：只 `implements MenuProvider` 的 BlockEntity，GUI 能打开、自己的存取逻辑正常，但原版互操作全部失效——漏斗/投掷器不吞吐、比较器无输出、`/item replace block <pos> container.N` 报 "Target position is not a container"（真机实测）。
- 规避：BlockEntity 直接实现 Container（或对外暴露 capability）；GameTest 里加一条 `/data`/capability 断言。快速检查点：放一个柜子后 `/item replace block ~ ~ ~ container.0 with minecraft:diamond 1`，报 not a container 即中招。
- 自测覆盖盲区：agent 的 GameTest 断言自己的 SimpleContainer 存取 ≠ 原版互操作；容器类 MOD 验收必须含互操作检查。

## 2026-09-02 Auto-recorded from runtime

- **Auto-recorded:** Cancelable events are `@Cancelable` (`Event#isCancelable()` true); use `Event#setCanceled(true/false)`. Canceling a non-cancelable event throws `UnsupportedOperationException` — always check first.
- **Auto-recorded:** } catch (NoSuchFieldException | IllegalAccessException e) {
- **Auto-recorded:** throw new RuntimeException(e);
- **Auto-recorded:** mc_java_sources/net/minecraftforge/fml/event/lifecycle/ParallelDispatchEvent.java:29: return getQueue().map(q->q.enqueueWork(getContainer(), work)).orElseThrow(()->new RuntimeException("No work queue found!"));
- **Auto-recorded:** } catch (ClassNotFoundException e) {
- **Auto-recorded:** LOGGER.fatal(Logging.LOADING, "Failed to load mod class {} for @EventBusSubscriber annotation", data.clazz(), e);
- **Auto-recorded:** throw new IllegalArgumentException("No declared methods found in " + listenerClass);
- **Auto-recorded:** * If you implement this interface on an ordinary class, an exception will be thrown when attempting to

## 2026-09-02 Auto-recorded from runtime

- **Auto-recorded:** - `@ObjectHolder(registryName = "...", value = "...")` on `public static` fields injects objects after `RegisterEvent`. Class-level `@ObjectHolder` or `@Mod` provides the default namespace. Missing registry/name → compil
- **Auto-recorded:** If the parent is not generated before the child model when passing in a `ResourceLocation`, then an exception will be thrown.
- **Auto-recorded:** Variants can be generated using `BlockStateProvider#getVariantBuilder`. Each variant specifies a list of [properties] (`PartialBlockstate`) which when matches a `BlockState` in a level, will display a model chosen from t
- **Auto-recorded:** `mods.toml` is broken into three parts: the non-mod-specific properties, which are linked to the mod file; the mod properties, with a section for each mod; and the dependency configurations, with a section for each mod's
- **Auto-recorded:** GatherDataEvent not found in mc_java_sources glob — maybe path differs (net/minecraftforge/client/event? or net/minecraftforge/data/event?). Let me search for it. Actually for chapter 9 (datagen), I could avoid deep data

## 2026-09-03 Auto-recorded from runtime

- **Auto-recorded:** C:\Users\59639\Desktop\skill-agent\docs\agent\ERROR_LIST.md:51: - Fix: use `parse_gametest_results` to see failures, then `read_game_test_log` / `tail_log` for the full exception.
- **Auto-recorded:** C:\Users\59639\Desktop\skill-agent\docs\agent\ERROR_LIST.md:55: `java.lang.module.ResolutionException: Module coppersword contains package com.coppersword, module test exports package com.coppersword to coppersword`
- **Auto-recorded:** [25] tool len=1437 | C:\Users\59639\Desktop\skill-agent\docs\agent\ERROR_LIST.md:51: - Fix: use `parse_gametest_results` to see failures, then `read_game_test_log` / `tail_log` for the full exception

## 2026-09-03 Auto-recorded from runtime

- **Auto-recorded:** From structure placement to result: place the test instance block, force-load the area, clear all entities in the structure bounds, place the structure in strict mode, wrap it in barriers (unless sky_access), clear sched

## 2026-09-03 Auto-recorded from runtime

- **Auto-recorded:** Error: 抓取失败: Client error '404 Not Found' for url 'https://minecraft.wiki/w/Java_Edition_1.22'
- **Auto-recorded:** Error: 抓取失败: Client error '404 Not Found' for url 'https://minecraft.wiki/w/Java_Edition_1.21.12'
- **Auto-recorded:** [18] tool len=183 | Error: 抓取失败: Client error '404 Not Found' for url 'https://minecraft.wiki/w/Java_Edition_1.22'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/
- **Auto-recorded:** [19] tool len=186 | Error: 抓取失败: Client error '404 Not Found' for url 'https://minecraft.wiki/w/Java_Edition_1.21.12'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Stat

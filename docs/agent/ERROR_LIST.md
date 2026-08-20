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
  - Fix: use `DeepSeek-V4-Flash-0731` (current default).

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
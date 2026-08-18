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

## Append Format

```md
- **One-line symptom**
  - Symptom: ...
  - Root cause: ...
  - Fix: ...
```
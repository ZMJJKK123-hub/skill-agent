# AGENTS.md (agent instructions, read-only)

This file is copied into every session workspace. The agent should read it once and follow it.

## Project facts
- MC 1.21.11 / Forge 1.21.11-61.2.0.
- Mod source under `src/main/java`, tests under `src/test/java`.
- Toolchain: ForgeGradle. Do NOT change build system/plugins/Forge version.
- Renaming a mod requires updating modid/namespace references in build.gradle/settings.gradle/mods.toml/java/assets/data/tests.

## Verification loop
1. Load the most relevant skill first via `load_skill` (e.g. forge-simple-min-mod).
2. Write code/resources directly from the skill. Do NOT read mc_java_sources before writing.
3. Run `validate_resources`.
4. Run `run_mod_test_cycle` (build + GameTest).
5. Fix compile errors by first grepping `docs/agent/ERROR_LIST.md`, then `search_api` in mc_java_sources.
6. When `All required tests passed` + `dist/*.jar` exists, finish immediately.

## Common pitfalls
- For a tool set, copy `starter/tools/CopperToolsMod.java` into `src/main/java` and rename — do not write tool registration from scratch.
- For a simple item, copy `starter/item/RubyMod.java` into `src/main/java` and rename — do not write item registration from scratch.
- 1.21.11 has no `SwordItem`/`ArmorItem`; use `Item.Properties` methods.
- `ResourceLocation` is `Identifier`; `Registries` is `net.minecraft.core.registries.Registries`.
- Mod constructor uses `FMLJavaModLoadingContext.get().getModBusGroup()`.
- mods.toml dependencies use `mandatory=true`.
- PNG generator must use color type 2 (RGB).
- Chinese JSON files must be UTF-8.

If any instruction conflicts with `docs/agent/ERROR_LIST.md` or a loaded skill, the more specific/later source wins.
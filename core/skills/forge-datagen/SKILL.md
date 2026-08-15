---

name: forge-datagen
description: "Forge data generators: runData task, generator modes, ExistingFileHelper, asset/server providers."
whenToUse: "Use when programmatically generating mod assets/data with Forge data generators."

---

# Data Generators

Data generators programmatically generate mod assets and data, defining file contents in code. The system is loaded by `net.minecraft.data.Main`; the generation class is `net.minecraft.data.DataGenerator`. The MDK `build.gradle` adds the `runData` task.

## Existing files

References to non-generated files must exist on disk (for typo checking) via `ExistingFileHelper` (from `GatherDataEvent#getExistingFileHelper`). `--existing <folder>` and `--existing-mod <modid>` add validation sources; by default only vanilla assets/datapack are available.

## Generator modes

- **Client assets** (`--client`, `#includeClient`): files in `assets` — models, blockstates, language files.
- **Server data** (`--server`, `#includeServer`): files in `data` — recipes, advancements, tags.
- **Development tools** (`--dev`, `#includeDev`): SNBT↔NBT conversion etc.
- **Reports** (`--reports`, `#includeReports`): dumps registered blocks/items/commands.
- `--all` includes everything.

## Data providers

All providers implement `DataProvider`. Register them in `GatherDataEvent` via `DataGenerator#addProvider`.

Client assets:

- `LanguageProvider` — `#addTranslations`
- `SoundDefinitionsProvider` — `#registerSounds` (`sounds.json`)
- `ModelProvider<?>` — `#registerModels` (`ItemModelProvider`, `BlockModelProvider`)
- `BlockStateProvider` — `#registerStatesAndModels` (blockstates + models)

Server data (`net.minecraftforge.common.data`): `GlobalLootModifierProvider` (`#start`), `DatapackBuiltinEntriesProvider` (with `RegistrySetBuilder`). (`net.minecraft.data`): `LootTableProvider`, `RecipeProvider` (`#buildRecipes`), `TagsProvider` (`#addTags`), `AdvancementProvider`.

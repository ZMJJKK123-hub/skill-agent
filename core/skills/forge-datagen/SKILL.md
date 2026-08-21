---

name: forge-datagen
description: "Forge 数据生成器：runData 任务、DataGenerator 系统、ExistingFileHelper 文件验证（GatherDataEvent#getExistingFileHelper）、生成器模式（--client/--server/--dev/--reports/--all）、DataProvider 注册、客户端资产提供器（LanguageProvider、SoundDefinitionsProvider、ModelProvider、BlockStateProvider）、服务端数据提供器（GlobalLootModifierProvider、DatapackBuiltinEntriesProvider、LootTableProvider、RecipeProvider、TagsProvider、AdvancementProvider）、RegistrySetBuilder 使用、SNBT↔NBT 转换、注册块/物品/命令转储。"
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

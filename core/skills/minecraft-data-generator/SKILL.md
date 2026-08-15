---
name: minecraft-data-generator
description: Data generator — running it, NBT↔SNBT conversion, exports, report tools.
whenToUse: Use when exporting Minecraft's data-driven files, converting NBT/SNBT, or generating internal reports (blocks, commands, registries, packets).
---

# Data Generator

The data generator exports data-driven files and converts data. Java Edition only. It exists as a runnable main class inside the client and server jars:

- Server data generator (both jars): `net.minecraft.data.Main`.
- Client data generator (client jar only): `net.minecraft.client.data.Main`.

## Launch Arguments

Run via classpath (`java -cp "...;client.jar" net.minecraft.data.Main <args>`) or via bundler (`java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar <args>`).

Server data generator arguments:

- `--help` — help (highest priority).
- `--dev` — NBT→SNBT conversion tool.
- `--reports` — report tool.
- `--server` — SNBT→NBT conversion + server datapack export.
- `--all` — `--dev --reports --server`.
- `--input <dir>` — SNBT/NBT input (repeatable).
- `--output <dir>` — output directory (default `./generated`).
- `--validate` — no real effect (argument validity check).

Client data generator arguments: `--help`, `--client` (= `--all`), `--output <dir>`.

## Export Tools

- **NBT→SNBT** (`--dev` + `--input`): converts `.nbt` files (GZip-compressed only; invalid files are skipped with a log error, path structure preserved). Structure template files convert to their special SNBT form.
- **SNBT→NBT** (`--server` + `--input`): converts `.snbt` files (invalid files skipped, paths preserved; structure SNBT converts back).
- **Server datapack export** (`--server`): writes writable registry entries (worldgen, variants, etc.), advancements, loot tables, recipes, and partial registry tags (blocks, items, biomes, banner patterns, structure types, damage types, entity types, flat world presets, fluids, game events, goat horn instruments, painting variants, POI types, world presets, enchantments, dialogs, timelines, mob effects, villager trades). Built-in datapacks are written under `data/minecraft/datapacks/`.
- **Client resource pack export** (`--client`): texture atlases, equipment models, blockstate mappings, item model definitions, item/block models, waypoint styles.

## Reports (`reports/` directory, `--reports`)

- `blocks.json` — block states: per block `definition` (with `type` from the `BLOCK_TYPE` registry; `properties` currently always empty) and `properties` (state properties + values) and `states` (list of `{default (when default), id (network serialization ID, not used for worldgen/save), properties}`).
- `commands.json` — the command tree: recursive nodes with `type` (`root`/`literal`/`argument`/`unknown`), `children`, `redirect` (alias/recursion; resolves by name from the root, depth-first), `executable`, `parser` (for arguments; with `properties` per parser: `brigadier:double/float/integer/long` → `min`/`max`; `brigadier:string` → `type` (`word`/`phrase`/`greedy`); `minecraft:resource*` → `registry`; `minecraft:entity` → `amount` (`single`/`multiple`) + `type` (`player`/`entities`); `minecraft:score_holder` → `amount`; `minecraft:time` → `min` ticks), and `permissions` (`always_pass` or `require` with a `permission` of `command_level`/atom types). The first node is the root; its children are all commands.
- `datapacks.json` — datapack structure: `others` (non-registry structures: `format` = `structure`/`mcfunction`, `elements`, `stable`, `tags`) and `registries` (same flags for registry entries).
- `json-rpc-api-schema.json` — the server administration JSON-RPC schema (OpenRPC): `components.schemas` (schema nodes with `$ref`/`type`/`enum`/`items`/`properties`), `info` (title "Minecraft Server JSON-RPC", version), `methods` (name, description, params with `name`/`required`/`schema`, `result` for request methods; `notification/`-prefixed names are notifications; `rpc.discover` excluded).
- `packets.json` — network packets: per network phase (`handshake`, `login`, `configuration`, `play`, `status`) and logical side (`clientbound`, `serverbound`): packet name → `protocol_id`.
- `registries.json` — registries: per registry: `default` (fallback entry), `entries` (entry → `protocol_id`), and the registry's own `protocol_id`.
- `biome_parameters/` — per-dimension files: `biomes` list of `{biome, parameters: {continentalness, depth, erosion, humidity, temperature, weirdness (exact or [min,max] ranges in [-2,2]), offset ([0,1])}}`.
- `components/` — default components of registry entries: for entry `<N>:<I>` in registry path `<P>` → `reports/components/<N>/<P>/<I>.json` with a `components` patch (`id` = value, `!id` = removed). Advancements/recipes/loot tables/item modifiers/predicates are excluded; in vanilla only the item registry has default components.
- Obsolete: `items.json` — item registry entries with their default `components` (replaced by the components report).

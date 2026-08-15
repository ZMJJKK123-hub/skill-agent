---
name: minecraft-command-storage
description: Command storage save format: command_storage.dat, NBT structure, access methods.
whenToUse: Use when understanding or accessing command storage (storage <target>) from commands, datapacks, or saves.
---

# Command Storage Format

This content applies only to Java Edition.

Command storage files store the data of command storage.

## Storage format

Files are located at `<save root>/data/<namespace>/command_storage.dat`, in GZip-compressed NBT format:

- Root tag
  - `data` (compound, required): command storage data.
    - `contents` (compound, required): the storage contents; `<name>` (compound) per namespace ID.
  - `DataVersion` (int, required): game data version; absent = 1343 (Java 1.12.2).

## Storage behavior

Command storage lets commands and datapacks save data under namespace IDs directly, without items, block entities, or entities.

Writing:

- `/execute ... store` with target `storage`
- `/data merge|modify|remove` with source `storage <target>`

Reading:

- Text components with type `nbt` and `storage` specified
- `/execute (if|unless) data` with source `storage`
- `/function ... with` with source `storage`
- `/data get` with source `storage <target>`
- Item modifiers of type `copy_custom_data` with `storage` source
- Number providers of type `storage`

Setting storage data to `{}` deletes it. The file is created only when a command writes to storage; files load on demand and stay in memory.

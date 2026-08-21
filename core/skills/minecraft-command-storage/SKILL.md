---

name: minecraft-command-storage
description: "Minecraft Command Storage 命令存储：Storage Format 存储格式（data/<namespace>/command_storage.dat GZip 压缩 NBT、Root tag data.contents 命名空间ID复合标签、DataVersion 数据版本）、Storage Behavior 存储行为（命令和数据包直接保存数据到命名空间ID、无需物品/方块实体/实体）、Writing 写入（/execute ... store storage 目标、/data merge|modify|remove storage <target>）、Reading 读取（text components nbt+storage、/execute (if|unless) data storage、/function ... with storage、/data get storage <target>、item modifiers copy_custom_data storage、number providers storage）、Storage Data Deletion 存储数据删除（{} 删除数据）、File Creation 文件创建（命令写入时创建、按需加载 内存中保留）。"
whenToUse: "Use when understanding or accessing command storage (storage <target>) from commands, datapacks, or saves."

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

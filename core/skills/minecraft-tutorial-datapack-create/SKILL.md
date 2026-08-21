---

name: minecraft-tutorial-datapack-create
description: "Minecraft Tutorial: Making a Data Pack 创建数据包教程：Overview 概述（数据包文件夹或zip 添加/修改函数/战利品表/世界结构/进度/配方/谓词/标签/维度/自定义世界生成、与mod不同 仅向原版固定接口提供数据、驱动原版风格地图和小游戏）、Setup 设置（VS Code 安装扩展 syntax-mcfunction/Datapack Helper Plus Spyglass、DNS问题解决 hosts文件、spyglass.json 配置）、Creating the Data Pack 创建数据包（/datapack create 命令 或手动创建、必需结构 data/ + pack.mcmeta）、pack.mcmeta（pack_format/min_format/max_format 包版本 F3+V查看当前游戏pack_data、不兼容显示但不一定破坏加载、/datapack list 检查）、Adding Content 添加内容（Namespaces 命名空间 data/ 包含多个命名空间 minecraft覆盖/test自定义、Namespace IDs and registries 命名空间ID和注册表 data/<ns>/<registry>/<path>.json 注册<ns>:<path>、Functions 函数、JSON files JSON文件 解压客户端jar浏览原版JSON、Autocomplete DHP自动补全、Structure files .nbt 结构方块保存→复制到包 data/<ns>/structure/、Reference vanilla pack 参考原版包 解压客户端jar 复制调整、With resource packs 结合资源包 "vanilla mods" Beet代码生成工具）、Tools 工具（社区转换器和语法高亮扩展）。"
whenToUse: "Use when creating your first datapack (setup, structure, pack.mcmeta)."

---

# Tutorial: Making a Data Pack

How to make data packs for Java Edition (Bedrock's equivalent: behavior packs). Prerequisites: command blocks, basic JSON and SNBT.

## Overview

A data pack is a folder or zip adding/modifying functions, loot tables, world structures, advancements, recipes, predicates, tags, dimensions, custom worldgen, etc. Unlike mods (which decompile/replace Java code), data packs only feed data into the fixed interfaces the vanilla game defines. Data packs also power vanilla-style maps and minigames, usually combined with resource packs.

## Setup (VS Code)

- Install VS Code, then the extensions: "syntax-mcfunction" and "Datapack Helper Plus by Spyglass" (DHP; requires syntax-mcfunction). The Chinese language pack is optional.
- If Spyglass fails to initialize (connection errors): add DNS-resolved IPs for `raw.githubusercontent.com` and `github.com` to the hosts file (`C:\Windows\System32\drivers\etc\hosts`, save as admin), then reinstall the extension.
- Verify autocomplete works in a `data/<ns>/function/test.mcfunction`; if not, add a `spyglass.json` at the workspace root with an `env` object (see the DHP docs).

## Creating the Data Pack

1. Java 1.21.6+: run `/datapack create my_example "description"` in chat (it creates the folder in the save), then via the world's "Edit" → "Open world folder" → `datapacks/` find it. (1.21.5 and below: create the folder manually.)
2. Required structure: `<pack>/data/` + `<pack>/pack.mcmeta` at the pack root (a zip works too).

### pack.mcmeta

Required so Minecraft recognizes the pack. Example:

```json
{
  "pack": {
    "description": { "text": "Tutorial pack", "color": "gold" },
    "min_format": 88,
    "max_format": 88
  }
}
```

- `pack_format` (deprecated) / `min_format`/`max_format` — the pack version; F3+V shows the current game's `pack_data` number. `supported_formats` (deprecated) sets a version range.
- A mismatched version shows the pack as "incompatible" in the UI but doesn't necessarily break loading — the directory structure and file contents are what really matter.
- Check with `/datapack list`; if your pack is missing, verify pack.mcmeta exists (not empty), is valid JSON (braces/quotes/commas; field names in double quotes — not SNBT), and sits at the pack root.

## Adding Content

- **Namespaces**: `data/` may contain several namespaces (e.g. `minecraft` for overrides, `test` for custom content). Namespace/path/folder/file names allow only `0-9`, `a-z`, `_`, `-`, `/` (not in namespaces), `.`; prefer `lower_case_with_underscores` and keep namespaces unique (your game ID is a safe choice).
- **Namespace IDs and registries**: see the namespaced-id skill; every file in `data/<ns>/<registry>/<path>.json` registers `<ns>:<path>`.
- **Functions**: see the function skill (first function, basic usage/debugging).
- **JSON files**: see the JSON tutorial (extract the jar to browse vanilla JSON, use source to confirm formats).
- **Autocomplete**: DHP provides field completion/descriptions for JSON and SNBT.
- **Structure files (.nbt)**: save structures with structure blocks → files appear under `.minecraft/saves/<save>/generated/<ns>/structures/<name>.nbt`; copy them into your pack's `data/<ns>/structure/`.
- **Reference the vanilla pack**: unzip the client jar — its `data/` has the same layout as your pack; copy and tweak vanilla files for small adjustments.
- **With resource packs**: combine for "vanilla mods" (custom items, trims); see the custom-item and custom-armor-trim tutorials. For large datapacks consider code generation with tools like Beet (Python plugins transform pack files; e.g. the Gamemode4 project).

## Tools

Many community converters and syntax-highlight extensions exist — install third-party tools carefully (not officially monitored).

See also: the data-pack skill, install tutorial, function tutorial, JSON tutorial, input detection tutorial; examples: raycasting, sight magic.

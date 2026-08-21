---

name: minecraft-data-pack
description: "Minecraft Data Pack 数据包：Usage 使用（datapacks 文件夹/.zip 归档、创建世界界面配置顺序/启用/搜索、加载 每次存档加载、/reload 重载进度/配方/函数/战利品表/谓词/物品修改器、服务器启动加载内容 世界生成/附魔/盔甲装饰/唱片等）、Experimental Features 实验性功能（pack 内容标记、警告屏幕）、Directory Structure 目录结构（pack.mcmeta 元数据、pack.png 图标、data/<namespace>/function/.mcfunction、structure/.nbt、JSON 注册表 advancement/banner_pattern/cat_variant/chat_type/chicken_variant/cow_variant/damage_type/dimension/dimension_type/enchantment/...、tags/<registry>/<path>.json # 前缀引用）、pack.mcmeta 格式（description 描述、min_format/max_format 支持版本号 [major, minor]、overlays 子包 directory/min_format/max_format、filter block 命名空间/路径正则忽略、features enabled 实验性功能命名空间ID）、Data Pack Icon 数据包图标（pack.png 根目录、fallback unknown_pack.png）、Data Pack Versions 数据包版本号（pack_format 递增 48→81→88→107）。"
whenToUse: "Use when creating or managing data packs (pack.mcmeta, structure, reloading)."

---

# Data Pack

Data packs customize game content: advancements, recipes, loot tables, enchantments, damage types, mob variants, world generation, and more. Java Edition only.

## Usage

Data packs are folders or `.zip` archives in `<save root>/datapacks/`. New packs can be configured (order, enabled, search) in the "More" tab of the create-world screen; selected packs are cached under the Java temp directory (`mcworld-<id>`).

- Loading: packs load on every save load. `/reload` reloads only advancements, recipes, functions, loot tables, predicates, and item modifiers; other content (worldgen, enchantments, armor trims, jukebox songs, ...) loads once at server startup — re-enter the save. Syntax errors in those files can trigger a "safe mode" screen blocking the save until the pack is disabled.
- Order: the configured order (stored in `level.dat` → `DataPacks`) applies; upper packs override lower ones. `/datapack list` shows the order; `/datapack disable` / `/datapack enable` toggle packs (auto-reload after).

## Experimental Features

Some pack content is flagged experimental; enabling it shows a warning screen when loading the save. Currently all non-hot-reloadable content triggers this whenever the pack content differs from vanilla.

## Directory Structure

```
<pack name>/
├── pack.mcmeta      # metadata
├── pack.png         # icon (optional)
└── data/
    └── <namespace>/
        ├── datapacks/          # built-in experimental packs (internal only)
        ├── function/           # functions (.mcfunction)
        ├── structure/          # structure templates (.nbt)
        └── advancement/ banner_pattern/ cat_variant/ chat_type/ chicken_variant/
            cow_variant/ damage_type/ decorated_pot_pattern/ dialog/ dimension/
            dimension_type/ enchantment/ enchantment_provider/ frog_variant/
            instrument/ item_modifier/ loot_table/ ... (JSON registries)
```

Each `data/<namespace>/<registry>/<path>.json` registers `<namespace>:<path>`; tags live in `data/<namespace>/tags/<registry>/<path>.json` (referenced with a `#` prefix). Functions and structure templates load similarly though they are not registry entries. Structure templates, advancements, and recipes have no tags. When multiple packs define the same file, upper packs win. Overlay directories fully override the pack's own content for matching files (even merge-on-load behaviors load only the last overlay's data).

## pack.mcmeta

Root object with a `pack` object:

- `description` (required) — text component shown in the datapack UI and on hover over `/datapack list` names.
- `min_format` (required) — minimum supported pack version: `[major, minor]` array (a bare int = `[n, 0]`).
- `max_format` (required) — maximum supported pack version (bare int = `[n, 0x7fffffff]`).
- `pack_format` / `supported_formats` — deprecated compatibility fields.
- `overlays` — sub-packs applied on top of the standard content: `entries` (in order) with `directory` (relative path; chars `a-z0-9_-`), `min_format`, `max_format` (or deprecated `formats`).
- `filter` — files to ignore: `block` list of `{namespace (regex), path (regex)}` patterns (omitted fields match everything).
- `features` — experimental features to enable: `enabled` list of namespace IDs. Adding this field requires adding the pack at world creation (or editing an old save's level.dat).

Example (new format):

```json
{ "pack": { "description": "Example pack", "min_format": [88, 0], "max_format": [107, 1] } }
```

## Data Pack Icon

`pack.png` at the pack root shows in the create-world screen's pack list; missing/broken icons fall back to `assets/minecraft/textures/misc/unknown_pack.png`.

## Data Pack Versions

The pack format number rises per release (e.g. 48 → 81 → 88 → 107...); see the Minecraft Wiki "Data pack" page for the version table and history.

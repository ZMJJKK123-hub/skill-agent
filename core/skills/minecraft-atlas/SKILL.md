---

name: minecraft-atlas
description: "Minecraft 纹理图集系统：Atlas 引用（minecraft:<id> 命名空间 ID、assets/minecraft/textures/atlas/<id>.png）、F3+S 转储图集、图集尺寸（2 的幂次方、最大 16384×16384）、Definition Format 定义格式（assets/minecraft/atlases/<name>.json、sources 图集源列表）、Atlas Sources 图集源类型（directory 目录添加、filter 正则过滤移除、paletted_permutations 调色板置换生成、single 单纹理添加、unstitch 区域切割提取）、Vanilla Atlases 原版图集（armor_trims.json/banner_patterns.json/blocks.json/celestials.json/chests.json/decorated_pot.json/gui.json/items.json/map_decorations.json/paintings.json/particles.json/shield_patterns.json/shulker_boxes.json）、Sprite 精灵解析（assets/<namespace>/textures/<id>.png）、Duplicate Sprite 重复精灵警告、palette_key/palette texture 调色板纹理、permutations 置换映射、separator 分隔符。"
whenToUse: "Use when adding or removing textures from vanilla texture atlases via resource packs."

---

# Texture Atlas

Texture atlases merge many textures into one large texture for rendering efficiency; the individual textures are called sprites. Java Edition only (current dynamic-atlas mechanism).

## Usage

- An atlas itself can be referenced by namespace ID: atlas `minecraft:<id>` → `assets/minecraft/textures/atlas/<id>.png` = `minecraft:atlas/<id>`.
- F3+S dumps all atlases plus a mapping file of sprite IDs → atlas locations.
- Atlas dimensions are always powers of two, square or 2:1, max 16384×16384 (precision-safe rendering).
- A texture that fails to load is still recorded but mapped to a random sprite slot; a texture whose metadata fails is not recorded (references become the missing texture).

## Definition Format

New atlases cannot be defined — only vanilla atlases can be modified. Files live in `assets/minecraft/atlases/` (JSON). Sprites resolve to `assets/<namespace>/textures/<id>.png`. Duplicate sprites across atlases warn (`Duplicate sprite <id> from atlas <a>, already defined in atlas <b>. This will be rejected in a future version`; sprite IDs are the criterion, not file content).

Root: `sources` (required) — list of atlas sources, executed in resource pack order and per-pack order:

- `directory` — adds all `.png` files under a `textures` subdirectory: `source` (path from `textures/`), `prefix` (namespace path prefix added to the sprite ID; e.g. source `s`, prefix `p`, file `textures/s/foo/abc.png` in namespace x → sprite `x:p/foo/abc`).
- `filter` — removes already-added sprites by regex: `pattern` with `namespace` (regex, required) and `path` (regex, required); matching sprites are removed.
- `paletted_permutations` — generates textures in memory by palette replacement: `textures` (original textures; they may only use the RGB colors defined by the palette key, alpha is kept), `palette_key` (original palette texture; from 26.3 resolved as `assets/<ns>/textures/palettes/<path>.png`), `permutations` (map of permutation name → palette texture, same dimensions as the palette key, per-pixel color correspondence), `separator` (default `_`; sprite ID = `<original><separator><permutation>`).
- `single` — adds one texture: `resource` (texture location), `sprite` (default = resource ID).
- `unstitch` — cuts regions out of one texture as sprites: `resource` (source texture), `divisor_x`/`divisor_y` (default 1; region coordinates are multiplied by texture size / divisor), `regions` (≥1 of `{sprite (sprite ID), x, y, width, height}`).

## Vanilla Atlases

Definitions in `assets/minecraft/atlases/`:

- `armor_trims.json` — entity-model armor trims (removed in 26.3 dev; pre-26.3 sources: `textures/trims/color_palettes/trim_palette.png` + material palettes, `textures/entity/humanoid[_leggings]/<pattern>.png`; sprite IDs `trims/entity/<equipment model>/<pattern>_<material>`).
- `banner_patterns.json` — banner patterns (`entity/banner_base.png` + all `entity/banner/` pngs).
- `blocks.json` — most block textures (`block/` pngs, `entity/conduit/`, `entity/bell/bell_body.png`, `entity/decorated_pot/decorated_pot_side.png`, `entity/enchantment/enchanting_table_book.png`); has a mipmap version.
- `celestials.json` — celestial textures (`environment/celestial/` pngs; stars are hardcoded; sprite IDs `<ns>:<name>`).
- `chests.json` — chest textures (`entity/chest/`).
- `decorated_pot.json` — decorated pot sherd pattern textures (`entity/decorated_pot/`).
- `gui.json` — GUI textures (`gui/sprites/` → sprite `<ns>:<name>`, `gui/mob_effect/`).
- `items.json` — item textures (`item/` pngs; plus `trims/` — `color_palettes/trim_palette.png` + material palettes and `trims/items/helmet_trim.png`/`chestplate_trim.png`/`leggings_trim.png`/`boots_trim.png` → sprite IDs `minecraft:trims/items/<armor type>_trim_<material>`).
- `map_decorations.json` — map icons (`map/map/decorations/` pngs; sprite `<ns>:<file name>`).
- `paintings.json` — painting textures (`painting/`; sprite `<ns>:<file name>`).
- `particles.json` — particle textures (`particle/`; sprite `<ns>:<file name>`).
- `shield_patterns.json` — shield pattern textures (`entity/shield/`).
- `shulker_boxes.json` — shulker box/shulker textures (`entity/shulker/`).

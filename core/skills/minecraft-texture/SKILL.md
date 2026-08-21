---

name: minecraft-texture
description: "Minecraft Texture 纹理：Directory Structure 目录结构（assets/<namespace>/textures/：colormap/ 生物群系颜色映射、effect/ 后处理输入纹理、entity/ 实体和动态模型方块纹理、environment/ 云/雨/末地天空、font/ 字体、gui/ GUI + gui/sprites/ GUI精灵、item/ 物品、map/ 地图、misc/ 光泽/望远镜覆盖等、mob_effect/ 状态效果、painting/ 画作、particle/ 粒子、trims/ 装饰 color_palettes/entity/items/）、Texture Properties 纹理属性（独立纹理和精灵纹理、静态和动画纹理、*.png.mcmeta 元数据：texture.blur 最近邻/双线性过滤、texture.clamp 重复/钳制边缘、texture.mipmap_strategy mipmap策略 mean/dark_cutout/cutout/strict_cutout/auto、texture.alpha_cutoff_bias alpha截止偏移、texture.palette.base_palette 盔甲装饰基础调色板）、Texture Atlases 纹理图集（F3+S 转储图集+精灵映射、图集引用 minecraft:atlas/<id>、图集加载纹理可动画）、Animated Textures 动画纹理（必须是精灵 帧网格布局 frame 0=左上角、*.png.mcmeta 元数据 animation.height/width 帧尺寸、animation.frames 播放顺序、animation.frametime 每帧刻数、animation.interpolate 帧间混合）、Animated-eligible Categories 可动画类别（方块/物品纹理、旗帜/盾牌纹理、部分方块实体、物品展示框/画作、GUI精灵+状态效果图标、地图图标、粒子、盔甲装饰、天体）、Special Textures 特殊纹理（Missing texture minecraft:missingno 自动生成16x16 紫色/黑色、Loading screen logo assets/minecraft/gui/title/mojangstudios.png 仅游戏JAR、Color maps 颜色映射 colormap/grass/foliage/dry_foliage 256x256）、GUI Sprite Textures GUI精灵纹理（textures/gui/sprites/ *.png.mcmeta gui.scaling.type：nine_slice 九切片缩放 border/width/height/stretch_inner、stretch 拉伸、tile 平铺 width/height）、Villager Textures 村民纹理（生物群系服装+职业服装+职业徽章 帽子层冲突需元数据 villager.hat none/partial/full）。"
whenToUse: "Use when authoring textures and their .mcmeta metadata for resource packs."

---

# Texture

Textures compose almost every visible element of the game. Java Edition only.

## Directory Structure

Under `assets/<namespace>/textures/`: `colormap/` (biome color maps), `effect/` (post-processing input textures), `entity/` (entity and dynamic-model block textures), `environment/` (clouds, rain, End sky), `font/`, `gui/` (+ `gui/sprites/`), `item/`, `map/`, `misc/` (glint, spyglass overlay...), `mob_effect/`, `painting/`, `particle/`, `trims/` (`color_palettes/`, `entity/`, `items/`).

## Texture Properties

Textures are either **independent** (loaded alone: title texture, `misc/` files) or **sprites** (merged into atlases); and either **static** or **animated** (frames uploaded repeatedly). Independent textures can set properties via `*.png.mcmeta`:

- `texture.blur` (default false) — nearest-neighbor vs (bi)linear filtering.
- `texture.clamp` (default false) — repeat the texture vs clamp/stretch the edges outside UV range.
- `texture.mipmap_strategy` (default `auto`) — `mean` (average 2×2 groups; vanilla solid/translucent blocks), `dark_cutout` (like mean but darkens cutout pixels; mangrove roots), `cutout` (generated from the original texture), `strict_cutout` (stricter alpha cutoff, invisible at high mip levels; flowers), `auto` (mean for fully-transparent pixels, cutout otherwise).
- `texture.alpha_cutoff_bias` (default 0) — cutoff alpha bias for distant cutout textures (lower mip levels only).
- `texture.palette.base_palette` — base palette texture ID for armor trims.

Sprites cannot set their own properties (the atlas handles filtering; nearest-neighbor). Texture **size**: for block/item textures non-square sizes can render unexpectedly; sprite sizes also limit atlas mipmaps (not divisible by 2 → no mipmaps; divisible by 2 but not 4 → max mip level 1, etc.).

## Texture Atlases

See the atlas skill. F3+S dumps atlases + sprite mapping; atlases are referenced as `minecraft:atlas/<id>`. Atlas-loaded textures can be animated (GUI atlas also supports GUI properties).

## Animated Textures

Animated textures must be sprites (independent textures can never animate, even with metadata). Frames are laid out in a grid; frame 0 = top-left, numbering left-to-right then next row. Frame dimensions must be equal and the whole image a multiple of them (else the texture is replaced with the missing texture).

Metadata (`*.png.mcmeta`, e.g. `stone.png.mcmeta`):

- `animation.height` (>0) / `animation.width` (>0) — frame size in pixels (one unspecified → full other dimension; both unspecified → square with the smaller side; larger than the texture → static; −1 = unset).
- `animation.frames` — playback order list (absent/empty = natural order): each entry an int frame index (out of range → skipped) or `{index (≥0), time (>0, overrides frametime)}`.
- `animation.frametime` (>0, default 1) — ticks per frame.
- `animation.interpolate` (default false) — blend between adjacent frames.

Animated-eligible categories (vanilla): block/item textures, banner/shield textures, some block entities (beds, chests, conduit, decorated pot, enchantment book, bell, shulker boxes, signs), item frames and paintings, GUI sprites + mob effect icons, map icons, particles, armor trims (but vanilla's `paletted_permutations` source doesn't support animation), celestial bodies (sun, moon, End flash).

## Special Textures

- **Missing texture** (`minecraft:missingno`) — auto-generated, added to all atlases; 16×16; purple `#F800F8` bottom-left/top-right, black top-left/bottom-right. Used when a texture or its metadata fails to load.
- **Loading screen logo** — `assets/minecraft/gui/title/mojangstudios.png`; only loaded from the game JAR (not resource-pack-replaceable).
- **Color maps** — `colormap/grass.png`, `colormap/foliage.png` (note the wiki's "foilage" typo), `colormap/dry_foliage.png`; 256×256, independent, no metadata. Out-of-range indices use `#FF00FF` / `#48B518` / `#B269D2` when the texture has fewer than 65536 pixels.

## GUI Sprite Textures

`textures/gui/sprites/` — all sprites; extra metadata in `*.png.mcmeta`:

- `gui.scaling.type`:
  - `nine_slice` — 9-slice scaling: `border` (int shorthand) or `left`/`top`/`right`/`bottom` (≥0), `width`/`height` (>0; texture stretches to these then slices), `stretch_inner` (default false — stretch instead of tiling the center).
  - `stretch` — stretch to fit.
  - `tile` — tile the texture: `width`/`height` (>0 per tile; texture stretches to the tile size first).

## Villager Textures

Villagers (incl. zombie villagers) combine biome clothing, profession clothing, and profession badge textures. The hat layers of biome/profession clothing can conflict, so both need metadata:

- `villager.hat` — `none`, `partial`, or `full` (default `none`).

The biome clothing hat renders only when the profession hat is `none`, or `partial` while the biome hat is not `full`; otherwise it is hidden.

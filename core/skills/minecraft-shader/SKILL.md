---

name: minecraft-shader
description: "Minecraft Shader 着色器系统：Using Shaders 使用着色器（渲染两个资源包可修改步骤：使用渲染类型核心着色器渲染对象→运行后处理管线、着色器加载失败禁用所有资源包关闭Fabulous!图形）、Shader Format 着色器格式（核心着色器 core shaders assets/<ns>/shaders/core/ 每个渲染类型一个、后处理着色器 post-processing shaders assets/<ns>/shaders/post/、包含着色器 include shaders #moj_import 导入 assets/<ns>/shaders/include/*.glsl 9个默认包含）、Render Type Parameters 渲染类型参数（Texture state 纹理状态 Sampler0-Sampler11、Shader state 着色器状态、Transparency (blend) state 透明混合状态 无混合/加法/闪电/光泽/崩塌/半透明、Depth test state 深度测试状态 none/equal/less-equal/greater、Cull state 剔除状态、Lightmap state 光照贴图状态 Sampler2、Overlay state 覆盖层状态 Sampler1、Layering state 分层状态 顶点偏移避免z-fighting、Output state 输出状态 目标帧缓冲、Texturing state 纹理状态、Write mask state 写入掩码状态、Line state 线宽、Color logic state 颜色逻辑）、Vertex Format 顶点格式 Position/Color/UV/UV1/UV2/Normal/Padding、Render Type Uniforms 渲染类型 Uniforms（ModelViewMat/ProjMat/ColorModulator/GlintAlpha/FogStart/FogEnd/FogColor/TextureMat/ScreenSize/Light0_Direction/Light1_Direction/ModelOffset）、Block Render Types 方块渲染类型（solid/cutout_mipped/cutout/translucent/translucent_moving_block/tripwire/end_portal/end_gateway）、Block Effect Render Types 方块效果渲染类型（crumbling/beacon_beam）、Entity Render Types 实体渲染类型（entity_solid/entity_cutout/entity_cutout_no_cull/entity_cutout_no_cull_z_offset/entity_smooth_cutout/entity_no_outline/eyes/entity_translucent_emissive/entity_alpha/entity_decal/entity_translucent/item_entity_translucent_cull/armor_cutout_no_cull/armor_decal_cutout_no_cull/lightning）、Entity Effect Render Types 实体效果渲染类型（entity_shadow/leash/water_mask/breeze_wind/energy_swirl/outline）、Glint Render Types 光泽渲染类型（glint/glint_translucent/armor_entity_glint/entity_glint）、Text Render Types 文本渲染类型（text/text_polygon_offset/text_see_through/text_intensity/text_intensity_polygon_offset/text_intensity_see_through/text_background/text_background_see_through）、GUI Render Types GUI渲染类型（gui/gui_overlay/gui_text_highlight/gui_ghost_recipe_overlay）、Misc Render Types 其他渲染类型（clouds/lines/line_strip/world_border）、Non-Render-Type Core Shaders 非渲染类型核心着色器（particle/position/position_color/position_tex/position_tex_color/blit_screen/lightmap/position_color_lightmap/position_color_tex_lightmap）、Post-Processing Pipeline 后处理管线（targets 自定义渲染目标、passes 传递列表 output/inputs/vertex_shader/fragment_shader/uniforms、Available Pipelines 可用管线 transparency/entity_outline/blur/creeper/spider/invert）。"
whenToUse: "Use when modifying shaders, render types, or post-processing effects via resource packs."

---

# Shader

Shaders control the game's rendering. Java Edition only. All shader files live under `assets/minecraft/shaders/` (core shaders in `shaders/core/`, post-processing in `shaders/post/`, include files in `shaders/include/`). Note: this page was flagged as missing 1.21.5+ core shader information.

## Using Shaders

Rendering has two resource-pack-modifiable steps (the order is hardcoded):

1. Render objects using their render type's core shader.
2. After the whole scene, run the post-processing pipeline.

If a shader fails to load, the game immediately disables all resource packs (to avoid corruption) and turns off Fabulous! graphics.

## Shader Format

Two kinds, otherwise identical: a shader = a vertex shader (`.vsh`) file + a fragment shader (`.fsh`) file.

- **Core shaders** — `assets/<ns>/shaders/core/`, one per render type (e.g. `rendertype_solid.json` before 25w07a; the JSON pairs a vertex and fragment shader).
- **Post-processing shaders** — `assets/<ns>/shaders/post/`, used for framebuffer post effects.

### Include Shaders

Vertex/fragment shaders can import include files (usually `*.glsl`, normal GLSL syntax) from `assets/<ns>/shaders/include/`:

```glsl
#moj_import <minecraft:fog.glsl>
#moj_import "minecraft:fog.glsl"
```

Missing/failed imports log `Could not open GLSL import <name>: <reason>`. Include files cannot import other include files — expansion happens once. The game ships 9 default includes (replaceable by resource packs).

## Render Type Parameters

A render type's behavior is defined by states:

- **Texture state** — sampler textures bound for the shader: none (empty), single (bound to `Sampler0`), or multi (`Sampler0`..`Sampler11` in order).
- **Shader state** — the core shader used.
- **Transparency (blend) state** — one of: no blending; additive (`one`, `one`); lightning (`srcalpha`, `one`); glint (`srccolor`/`zero` → `one`/`one`); crumbling (`dstcolor`/`one` → `srccolor`/`zero`); translucent (`srcalpha`/`one` → `1-srcalpha`/`1-srcalpha`).
- **Depth test state** — none; equal (`GL_EQUAL`); less-equal (`GL_LEQUAL`, default); greater (`GL_GREATER`).
- **Cull state** — culling enabled by default.
- **Lightmap state** — uses the 16×16 dynamic lightmap texture (x = block light, y = sky light) bound to `Sampler2` (overriding the texture state's `Sampler2`).
- **Overlay state** — uses the 16×16 overlay texture (top: semi-transparent red rgba(255,0,0,0.69804) for damage flash; bottom: white gradient for TNT flash) bound to `Sampler1` (overriding `Sampler1`).
- **Layering state** — vertex offset to avoid z-fighting: none; polygon offset (`glPolygonOffset`, factor −1, units −10); view offset Z (view matrix scaled 0.99975586); view offset Z forward (scaled 1.0002441).
- **Output state** — target framebuffer: main; outline; translucent/particles/weather/clouds/item entity (Fabulous! only).
- **Texturing state** — texture matrix transform: none; offset; glint (item/block glint); entity glint.
- **Write mask state** — whether color and depth buffers are written (default: both).
- **Line state** — line width (default 1).
- **Color logic state** — none (`GL_COPY`) or `GL_OR_REVERSE`.

Other parameters:

- **Vertex format** — attributes passed to the vertex shader: `Position` (vec3), `Color` (vec4), `UV`/`UV0` (vec2, Sampler0 coords), `UV1` (ivec2, usually overlay), `UV2` (ivec2, usually lightmap), `Normal` (vec3), `Padding` (float).
- **Mode** — mostly quads (4 indexed vertices); some use triangle strips or lines.
- **Buffer size** — max buffer size per draw; mostly 1536.

### Render Type Uniforms

Available to render type shaders: `mat4 ModelViewMat`, `mat4 ProjMat`, `vec4 ColorModulator` (default (1,1,1,1); e.g. sky color), `float GlintAlpha` (enchanted glint flicker setting), `float FogStart`, `float FogEnd`, `vec4 FogColor`, `mat4 TextureMat`, `vec2 ScreenSize`, `vec3 Light0_Direction`, `vec3 Light1_Direction`. Block render types also get `vec3 ModelOffset` (sub-chunk coordinates).

## Render Type List

Since 25w07a the block render types' shaders are `shaders/core/terrain.fsh` + `terrain.vsh`. Block rendering has three categories: opaque, fully transparent (alpha-tested), and translucent — plain texture edits cannot change the category. Member lists below are representative; for complete lists see the Minecraft Wiki "Shader" page.

### Block Render Types

- `solid` (pre-25w07a shader `rendertype_solid`) — all solid-rendered blocks incl. moving ones; alpha channel ignored (RGB always drawn). Pre-25w07a: `shaders/core/rendertype_solid.json` could define `ALPHA_CUTOUT` (0–1) to discard fragments below that alpha. Buffer 4194304 B; rendered per sub-chunk.
- `cutout_mipped` (pre-25w07a `rendertype_cutout_mipped`) — alpha-tested blocks with mipmapping; discards fragments with alpha < 0.5 by default (threshold configurable pre-25w07a). Used by grass block, iron bars, glass panes, tripwire hooks, hoppers, chains, mangrove roots, leaves (High/Fabulous). Buffer 4194304 B.
- `cutout` (pre-25w07a `rendertype_cutout`) — alpha-tested blocks without mipmaps; discards alpha < 0.1 (configurable pre-25w07a). Used by flowers, mushrooms, grass/ferns, crops, kelp/seagrass, vines/weeping vines/nether sprouts, stems, big dripleaf, azalea, sweet berries, chorus plant/flower, saplings, bamboo, cave vines, glow lichen, lily pad, moss, spore blossom, pink petal block, hanging roots, coral, sea pickles, cobweb, glass, redstone dust/wire, doors, ladders, trapdoors, rails, torches, fire, lanterns, campfires, spawners/vault, brewing stand, beacon, conduit, end rod, flower pot, scaffolding, stonecutter, lightning rod, turtle eggs, pointed dripstone, amethyst buds/clusters, sculk sensors/shriekers/veins, frogspawn. Buffer 786432 B.
- `translucent` (`rendertype_translucent`) — translucent blocks with blending and far-to-near sorting; Fabulous!: translucent target. Used by ice/frosted ice, nether portal, stained glass (panes), tinted glass, slime block, honey block, bubble column, water/flowing water. Buffer 786432 B.
- `translucent_moving_block` (`rendertype_translucent_moving_block`) — moving translucent blocks (moving piston, falling blocks); batched, not per sub-chunk. Fabulous!: item entity target.
- `tripwire` (`rendertype_tripwire`) — tripwire strings (hooks use cutout_mipped). Fabulous!: weather target.
- `end_portal` (`rendertype_end_portal`) — end portal block; multi-texture (Sampler0 `environment/end_sky.png`, Sampler1 `entity/end_portal.png`); texture coords computed from the player's view position; no breaking cracks.
- `end_gateway` (`rendertype_end_gateway`) — end gateway block; same algorithm; no breaking animation.

### Block Effect Render Types

- `crumbling` (`rendertype_crumbling`) — block breaking animation; texture `block/destroy_stage_<0-10>.png` by progress; crumbling blending, polygon-offset layering, color buffer only; unaffected by AO/light (Color fixed white, no lightmap).
- `beacon_beam` (`rendertype_beacon_beam`) — beacon/end gateway beams; texture `entity/beacon_beam.png`; outer beam translucent + color-only, inner beam opaque.

### Entity Render Types

- `entity_solid` (`rendertype_entity_solid`) — opaque entity parts: inactive conduit, beds, decorated pots, shields, tridents, bell clapper, banner poles, books on enchanting tables/lecterns, item frame/painting backgrounds, player cape, etc.
- `entity_cutout` (`rendertype_entity_cutout`) — entity parts with alpha-tested textures: bats, arrows, bobbers, chests, all non-terrain block/block-item rendering inside entities, burning entity flame layers.
- `entity_cutout_no_cull` (`rendertype_entity_cutout_no_cull`) — default render type for most entity layers; no face culling. Also guardian beams, active conduit, shulker boxes, sign backgrounds.
- `entity_cutout_no_cull_z_offset` (`rendertype_entity_cutout_no_cull_z_offset`) — depth-conflict-prone layers: shulker shells, mob heads (except player heads) and their items.
- `entity_smooth_cutout` (`rendertype_entity_smooth_cutout`) — end crystal beam (`entity/end_crystal/end_crystal_beam.png`); no culling.
- `entity_no_outline` (`rendertype_entity_no_outline`) — banner/shield colors and patterns; never writes to the outline buffer.
- `eyes` (`rendertype_eyes`) — Enderman, Phantom, Spider, Ender Dragon eyes; additive blending over the full model rendered twice.
- `entity_translucent_emissive` (`rendertype_entity_translucent_emissive`) — Warden glowing parts, Breeze eyes; full model rendered twice like eyes.
- `entity_alpha` (`rendertype_entity_alpha`) — Ender Dragon death animation first pass; Color goes black→white; fragments darker than Color are filtered out.
- `entity_decal` (`rendertype_entity_decal`) — Ender Dragon death animation second pass with equal depth test, keeping only fragments matching the depth written by entity_alpha.
- `entity_translucent` (`rendertype_entity_translucent`) — most translucent entities: Vex, Allay, Breeze, wind charges, most player layers, slime/shulker bullet outer layers, horse markings, wolf armor, player heads, elder guardian mining fatigue particles.
- `item_entity_translucent_cull` (`rendertype_item_entity_translucent_cull`) — items/blocks not qualifying for entity_cutout, XP orbs, invisible mobs for players who can see them. Fabulous!: item entity target.
- `armor_cutout_no_cull` / `armor_decal_cutout_no_cull` (`rendertype_armor_cutout_no_cull`) — armor and elytra (and trim decals with `decal: true`); view-offset layering; decal uses equal depth test.
- `lightning` (`rendertype_lightning`) — lightning bolts and the Ender Dragon death flash; lightning blending; Fabulous!: weather target.

### Entity Effect Render Types

- `entity_shadow` (`rendertype_entity_shadow`) — entity shadows (`textures/misc/shadow.png`); translucent, view-offset layering, color only. Rendered only when: entity shadows enabled, entity not in inventory, visible, radius/strength > 0, within 256 blocks. Max radius 32; per-block criteria: has model, full collision box, outline box, internal light level > 3.
- `leash` (`rendertype_leash`) — leads (not the knot); triangle strip mode.
- `water_mask` (`rendertype_water_mask`) — water patch inside boats; writes depth only (shader color output has no effect; only vertex offset or fragment discard works).
- `breeze_wind` (`rendertype_breeze_wind`) — the wind swirl around Breeze and wind charges.
- `energy_swirl` (`rendertype_energy_swirl`) — Creeper charge arcs and half-health Wither armor; additive.
- `outline` (`rendertype_outline`) — entity outlines (and invisible glowing mobs' parts); no depth test, output to the outline target.

### Glint Render Types

- `glint` (`rendertype_glint`) — item glint (`textures/misc/enchanted_glint_item.png`); glint blending, equal depth test, glint texturing, color only. Non-Fabulous: all items except tridents; Fabulous: items not using item_entity_translucent_cull.
- `glint_translucent` (`rendertype_glint_translucent`) — Fabulous! only: glint for items using item_entity_translucent_cull; outputs to item entity target.
- `armor_entity_glint` (`rendertype_armor_entity_glint`) — armor/elytra glint (`textures/misc/enchanted_glint_entity.png`); entity glint texturing.
- `entity_glint` (`rendertype_entity_glint`) — has no effect.

### Text Render Types

- `text` (`rendertype_text`) — text with non-grayscale bitmap/unihex/missing fonts: map backgrounds and map graphics, most text (excluding see_through text displays, non-sneaking nameplates, and signs). Buffer 786432 B.
- `text_polygon_offset` (`rendertype_text`) — same with polygon-offset layering; sign text of those fonts.
- `text_see_through` (`rendertype_text_see_through`) — see_through text displays and non-sneaking nameplates; no depth test, color only.
- `text_intensity` (`rendertype_text_intensity`) — grayscale bitmap / vector font text (same exclusions as `text`).
- `text_intensity_polygon_offset` (`rendertype_text_intensity`) — sign text for intensity fonts.
- `text_intensity_see_through` (`rendertype_text_intensity_see_through`) — see_through intensity text.
- `text_background` (`rendertype_text_background`) — backgrounds of text displays with `see_through: false`.
- `text_background_see_through` (`rendertype_text_background_see_through`) — backgrounds of see_through text displays.

### GUI Render Types

- `gui` (`rendertype_gui`) — solid/gradient GUI elements (lines, backgrounds).
- `gui_overlay` (`rendertype_gui_overlay`) — overlays: hover highlight, durability bars/cooldowns, loading screen background, debug charts, text cursor, sleeping/spyglass overlays. No depth test, color only.
- `gui_text_highlight` (`rendertype_gui_text_highlight`) — text selection highlight; `GL_OR_REVERSE` color logic.
- `gui_ghost_recipe_overlay` (`rendertype_gui_ghost_recipe_overlay`) — ghost recipe items in crafting slots; greater depth test.

### Misc Render Types

- `clouds` (`rendertype_clouds`) — clouds (`environment/clouds.png`); translucent; Fabulous!: clouds target; High quality: depth only.
- `lines` (`rendertype_lines`) — lines (block outlines, debug chunk corners, entity hitboxes, crosshair, structure bounds); extra uniform `LineWidth`; Fabulous!: item entity target.
- `line_strip` (`rendertype_lines`) — line strips (fishing line).
- `world_border` (`rendertype_world_border`) — world border (`misc/forcefield.png`); Fabulous!: weather target.

## Non-Render-Type Core Shaders

Not used by render types (or only conditionally); they don't start with `rendertype`. Same vertex-format/uniform conventions; states vary by use.

- `particle` — all particles and rain/snow; affected by the lightmap (Sampler2).
- `position` — Overworld sky and stars, void darkness below sea level.
- `position_color` — solid colors: sunrise/sunset sky tint, debug pie chart, debug chunk borders.
- `position_tex` — unshaded textures: sun and moon, world border, underwater screen effect, all GUI sprites (buttons, backgrounds, icons).
- `position_tex_color` — tinted textures: panoramas, End sky, suffocation overlay, fire overlay, tinted GUI sprites.
- `blit_screen` — copies framebuffers for the post pipeline; cannot be overridden (loaded from vanilla data at preload; a failure crashes the game).
- `lightmap` — generates the lightmap texture; if it fails, the lightmap never updates. Extra uniforms: `AmbientLightFactor` (dimension `ambient_light`), `SkyFactor`, `BlockFactor`, `NightVisionFactor`, `DarknessScale`, `DarkenWorldFactor` (Boss bar `DarkenScreen`), `BrightnessFactor` (Brightness option), `SkyLightColor`, `AmbientColor` (End sky flash).
- `position_color_lightmap`, `position_color_tex_lightmap` — have no effect.

## Post-Processing Pipeline

Invoked after rendering the whole scene or for screen effects; the debug screen's `post_effect` line shows the active pipeline. Pipeline programs live in `assets/minecraft/post_effect/`; new pipelines cannot be added, existing ones can be modified.

### Pipeline JSON Format

- `targets` — custom render targets (`<namespace id>: {}` for window-sized, or `{width, height, persistent (default false), clear_color (default [0,0,0,0])}`). Duplicate target names block the resource pack (`<name> is already defined`). `minecraft:main` (the screen) is always provided; other pipelines provide extra targets (see below); a user-defined target with the same name as a provided one is ignored.
- `passes` — list of passes, each:
  - `output` (required) — output target namespace ID (should differ from inputs; use a temporary target for in-place edits).
  - `inputs` — list of inputs: `sampler_name` (required), `bilinear` (default false), and either a target (`target`, `use_depth_buffer` default false) or a texture (`location` → `assets/<ns>/textures/effect/<path>.png`; `width`, `height` required; missing texture fails pack loading with `Texture '<path>' does not exist`).
  - `vertex_shader`, `fragment_shader` (required) — names mapped to `assets/<ns>/shaders/<path>.vsh` / `.fsh`.
  - `uniforms` — grouped lists of `{name, type, value}`; uniforms set here override shader defaults; max length 4 (no mat3/mat4), floats only.

Pass execution: bind input targets as samplers → set provided uniforms → apply pass uniforms → run the shader writing to the output target. Provided uniforms: `sampler2D <input>Sampler`, `vec2 <input>Size`, `vec2 OutSize`, `vec2 ScreenSize`, `float GameTime` (0–1, resets every 20 minutes), `mat4 ProjMat` (orthographic, near 0.1, far 1000).

### Available Pipelines

- `transparency` — Fabulous!: combines translucent, item_entity, particles, weather, clouds targets into the world render; must write to `minecraft:main`. Failure to load crashes the game and downgrades graphics to High.
- `entity_outline` — post-processes the outline target; extra target `final` (result merged into the main target by the game — do not write `minecraft:main`). Failure: warning only; no outlines rendered.
- `blur` — GUI blur background; extra uniform `Radius` (float, matches the menu background blur setting). Failure: warning only; no GUI blur.
- `creeper` / `spider` / `invert` — spectator-view effects (Creeper, Spider, Enderman perspectives); must write to `minecraft:main`. Failure: warning only.

---
name: minecraft-model
description: Model format — baked models, inheritance, elements, transforms, dispatch, tinting.
whenToUse: Use when authoring or editing resource pack block/item models, blockstate JSON, or item model definitions.
---

# Model (Java Edition)

Models define the geometry of objects in the game world. This page covers Java Edition; Bedrock models are part of Add-Ons.

## Model Categories

By rendering behavior:

- **Baked model** — geometry is fixed once created. Controls most blocks and items; geometry and texture bindings can be modified via resource packs.
- **Dynamic model** — geometry can change with environment/state. Controls some block entities and all entities; geometry is hardcoded in game logic (not resource-pack-editable), but textures can be replaced.

By purpose:

- **Block model** — renders blocks, some block entities, and parts of block entities.
- **Item model** — renders items in inventories and in mob hands.
- **Entity model** — renders all entities and some block entities.

Relationship: all entity models are dynamic (possibly with baked parts — only textures modifiable); item models are a special case of block models, and most block models are baked.

## Baked Models

Baked model files live under `assets/<namespace>/models/` with this basic JSON structure:

- `parent` — namespace ID of the parent model (see Inheritance).
- `ambientocclusion` (default `true`) — whether to use ambient occlusion ("smooth lighting").
- `textures` — texture variables (see Texture Variables). Block models must use textures from the `blocks` atlas; item models may use `blocks` or `items` atlas, but a single item model cannot mix atlases.
  - `<name>` — direct texture variable, or with options: `sprite` (required, same atlas rules), `force_translucent` (default `false` — force translucent rendering for all elements using this texture).
- `elements` — model elements (see Elements).
- `display` — render transforms per display mode (default: no transform for all modes).
- `gui_light` (default `side`) — lighting direction in GUI rendering (see Display Transforms).

### Model Inheritance

- A child model missing `ambientocclusion`, `elements`, or `gui_light` uses the parent's value.
- A child model missing a specific `display` mode uses the parent's transform for that mode.
- `textures` of child and parent are merged and resolved together.
- A model with no parent is a **root model**; missing data uses defaults or stays empty.
- Cyclic inheritance is detected and broken: the last model in the chain is re-parented to the invalid model, with the warning `Found 'parent' loop while loading model '<model>' in chain: ...`.
- A missing parent also re-parents to the invalid model, with `No parent '<parent>' while loading model '<model>'`.

### Texture Variables

Instead of direct texture paths, models define named texture variables in `textures` to reduce texture loading. A child variable with the same name overrides the parent's.

- A variable maps to a namespace path, e.g. `"top": "block/cake_top"` → file `assets/<namespace>/textures/<path>.png`, packed into the atlas; missing textures become the missing texture.
- A variable can reference another variable with a `#` prefix, e.g. `"particle": "#texture"`. If the referenced variable is not found in the child or any parent, the variable maps to the missing texture.
- Cyclic references are invalid (warning `Unable to resolve texture due to reference chain ...`).

### Elements

Elements must be rectangular cuboids; each face can have independent texture mapping. Units are "pixels" (1/16 of a block). Block center is `[8, 8, 8]`, grid range `[0, 0, 0]`–`[16, 16, 16]`; elements may be defined within `[-16, -16, -16]`–`[32, 32, 32]` and render outside the block grid (up to the 3×3×3 grid around their block unless rotated).

- `from` / `to` (required) — start/end corners `[x, y, z]`. Each component of `from` must be ≤ the corresponding component of `to`: out-of-order corners change texture mapping and face normal direction, causing wrongly culled faces.
- `rotation` — element rotation:
  - `origin` (required) — rotation center (can be anywhere, allowing elements to render outside the 3×3×3 grid).
  - `rescale` (default `false`) — rescale after rotation to compensate visual shrinking.
  - Single-axis format: `angle` (degrees) + `axis` (`x`, `y`, or `z`); multi-axis format: `x`/`y`/`z` angles applied in x→y→z order. Rotation follows the right-hand rule.
- `shade` (default `true`) — render shading. Standard face shading by final world orientation: north/south faces 80%, east/west 60% brightness; with fixed ambient light (e.g. the End), up/down become 90%; otherwise down 50%, up unchanged. Unshaded elements: all directions 90% with fixed ambient, else full brightness.
- `light_emission` (0–15) — emissive light level; combined per-channel with sky/block light by taking the max (error if outside 0–15: `Expected light_emission to be an Integer between (inclusive) 0 and 15`).
- `faces` (required) — faces of the element: `up`, `down`, `north`, `south`, `west`, `east` (by unrotated orientation). Undefined faces are not rendered. Each face:
  - `texture` (required) — texture variable name with `#` prefix.
  - `uv` — `[u1, v1, u2, v2]` texture mapping (units: 1/16 of the texture; top-left `[0, 0]`, bottom-right `[16, 16]`). Out-of-range coordinates render wrong atlas regions. Swapping a component pair mirrors the texture.
  - `rotation` (default 0) — rotate the texture mapping: 0, 90, 180, or 270 (vertex permutation; non-square mappings distort at 90/270).
  - `tintindex` (default -1) — hardcoded tint index for recoloring; -1 disables tinting. Item models may reference item model tints by index.
  - `cullface` — occlusion direction for face culling (see Face Culling).

### Display Transforms

Display modes:

- `thirdperson_lefthand` / `thirdperson_righthand` — item held in mob hands.
- `firstperson_lefthand` / `firstperson_righthand` — item in player hands in first person.
- `head` — item on a mob head, Snow Golem pumpkin, spyglass in use.
- `gui` — item in GUIs.
- `ground` — item entities, item projectiles, Eyes of Ender, firework rockets, carried items, Vault contents, ominous item spawner items.
- `fixed` — item frames, campfires, suspicious blocks.
- `on_shelf` — item on a chiseled bookshelf.

If `thirdperson_righthand` is defined but `thirdperson_lefthand` is not, the left-hand transform copies the right-hand one (same for firstperson).

Each display mode transform:

- `scale` (default `[1, 1, 1]`) — per-axis scale, clamped to -4..4.
- `rotation` (default `[0, 0, 0]`) — per-axis rotation in degrees.
- `translation` (default `[0, 0, 0]`) — per-axis translation in pixels (1/16 block), clamped to -80..80.

Applied in order: scale → rotation → translation, then a world transform from the mode's base position.

`gui_light`: `side` = 3D model lighting, `front` = flat item lighting.

### Invalid Model

If a model is missing or fails to load, it is replaced by the invalid model `builtin/missing`: a cube whose 6 faces use the missing texture (hardcoded definition available; `textures: { "particle": "missingno", "missingno": "missingno" }`, full-cube element with `cullface` on every face).

## Block Models

### Blockstate Dispatch

Blockstate mapping files live under `assets/<namespace>/blockstates/<path>.json`; their namespace ID identifies the bound block. Every block needs a mapping (even without properties); missing mappings render the invalid model. Two modes — `variants` (direct) or `multipart` (combination); at least one required (warning `Neither 'variants' nor 'multipart' found`). If both are given, `variants` wins; unmatched states fall through to `multipart`.

#### Variants (direct state mapping)

`variants` maps blockstate keys to candidate models:

- Property groups joined with `,`: `prop=value`. Both must be valid for the block, or the whole key is invalid (warnings `Unknown blockstate property: ...` / `Unknown value: ... for blockstate property: ...`).
- A block without properties uses the empty string `""` as its key.
- Keys need not cover all properties; matching is partial. Mapping is checked in file order; a state already mapped produces an error (`Overlapping definition on state: ...`) and stops processing of the variants section. If no key matches, the game tries the next resource pack's blockstate file.

Example keys (redstone wire): `"power=0,east=none,west=none,north=none,south=none"`, `"east=none"`, `"power=0,west=up"`, `"power=15"`, `""`.

#### Multipart (model combination)

`multipart` is a list of parts: `{ "when": <condition>, "apply": <candidate models> }`.

`when` conditions, one of:

- `AND` — all sub-conditions must pass (must be an array).
- `OR` — any sub-condition passes (must be an array).
- Plain property groups — each `"prop": "value|value2|..."` pair must pass; `!` prefix negates the list; invalid values warn; an empty list warns.
- No elements in the selector warns `No elements found in selector`.
- Absent `when` — the part applies to all states.

Example: `{ "AND": [ { "OR": [ { "power": "0|1|2|3", "north": "!none" }, { "power": "!12|13|14|15", "west": "side" } ] }, { "east": "side" } ] }`.

A state matching no part has **no model** — nothing renders (unlike the invalid model, which still renders the missing cube), and later resource packs are not consulted.

#### Candidate Models

Each matched variant/part selects from candidate models — either one object or a weighted list:

- `model` (required) — model file namespace ID → `assets/<namespace>/models/<path>.json` (usually under `block/`).
- `uvlock` (default `false`) — keep texture rotation locked.
- `x`, `y`, `z` (default 0) — rotation around the respective axis, must be multiples of 90.
- `weight` (default 1, >0) — selection weight (list form only). Probability = weight / total weight; selection is deterministic per block position.

Rotation happens clockwise around Y then X at the block center `[8, 8, 8]`, keeping texture mappings fixed (vertices rotate). With `uvlock`, texture bindings are re-computed (rotated in texture space around `[8, 8]`) so the displayed texture does not rotate with the model.

#### Item Frame Mapping

Item frames use two fake blocks, `item_frame` and `glow_item_frame`, with a fake boolean property `map` (`false` = no map, `true` = map), so their frame model is overridable via `assets/minecraft/blockstates/item_frame.json`.

### Face Culling

Faces without `cullface` are never culled (inner faces such as stairs' step faces; interior faces of composters and cauldrons that prevent see-through). A face with `cullface` (one of `up`/`down`/`north`/`south`/`west`/`east`) is not rendered when the occlusion shape of the neighbor in that direction fully covers the block's own shape in that direction. Culling depends only on `cullface` and the occlusion shapes — not on the face's actual position.

### Block Particle Texture Variable

The special `particle` texture variable (usable normally too; missing → missing texture) is used for: `block`, `block_marker`, and `dust_pillar` particles; the screen overlay of view-blocking blocks; the Nether portal overlay and dimension-loading screen (nether portal block, north/south state); and still water/lava.

### Block Tinting

Blocks with hardcoded tint (tintindex -1 disables; other indices share the same mode):

- Grass, tall grass, large fern, fern, potted fern, bush, sugar cane, vines, grass block, oak/dark oak/jungle/acacia/mangrove/birch/spruce leaves, dead bush — biome foliage color.
- Pink petal block, wildflowers (index 0 also disabled) — biome foliage color.
- Water, bubble column, water cauldron — biome water color.
- Redstone wire — colored by `power` n: n=0 → `#4C0000`; else RGB `(⌊10.2n+102⌋, ⌊clamp(357n²−573/75450, 0, 255)⌋, ⌊clamp(102n²−267/75150, 0, 255)⌋)`.
- Melon stem, pumpkin stem — by `age` n: `(32n, 255−8n, 4n)`; attached stems fixed `#E0C71C`.
- Lily pad — fixed `#208030`.

## Item Models

Item models are baked models like block models, but item stacks carry more data, so item model mappings live in `assets/<namespace>/items/<item ID>.json` under the `model` key. Every item needs a mapping; otherwise the item renders the invalid model.

### Defining Item Models

- **Inheriting a block model** — e.g. `{ "parent": "block/grass_block" }`; the block model's transforms carry over, and the game computes the 2D projection for GUI rendering. Child models may override parent data (e.g. `elements`). Vanilla block items pass the block model itself (not a wrapper) when no item model is defined.
- **Built-in generation** — the root model `builtin/generated` generates a flat item model from texture layers (equivalent baked form: `textures: { "particle": "#layer0" }`, `gui_light: "front"`). Layers `layer0`–`layer4` (at most 5); `layer0` is required. Layers are read in order — a gap stops further layers (`layer0`, `layer1`, `layer4` uses only the first two). Each layer has a tint index matching its number. Most vanilla item models inherit `item/generated`, which inherits `builtin/generated` and adds the needed display transforms.

### Item Particle Texture Variable

The `particle` variable works as for blocks (inherited from a block parent if any) and is used by particles `item`, `item_slime` (slime ball), `item_cobweb` (cobweb), `item_snowball` (snowball).

## Dynamic Models

Geometry is not resource-pack-modifiable. Structure: cube elements (belonging to a model part, texture binding origin, cuboid range relative to part origin, scale factor, mirror flag, rendered faces) grouped into **model parts**, organized as a tree; parent part transforms propagate to children (e.g. enchantment table book rotates while its pages flip).

Entirely dynamic-model block entities: Conduit (animation), Banner (patterns), Chest/Trapped Chest/Ender Chest/Shulker Box (open animation), Decorated Pot, Sign (text), Moving Piston, Mob Head, End Gateway/End Portal (special shaders).

Mixed (baked part + dynamic animations): Bell, Beacon (beam), Suspicious Gravel/Sand (brushed item), Campfire/Soul Campfire (cooking item), Enchanting Table/Lectern (book), Spawner/Trial Spawner (inner entity), Vault (item).

Fluid blocks use dynamic models entirely; fluid height is computed from surroundings.

## History

Before 24w45a, item tinting was hardcoded by item ID (examples: short/tall grass, ferns, vines, grass block `#7CBD6B`; oak/dark oak/jungle/acacia leaves `#48B518`; mangrove `#92C648`; birch `#80A755`; spruce `#619961`; lily pad `#71C35C`; leather armor dye (index ≤0 or <−1); wolf armor index 1; firework star index 1; potions/splash/lingering/tipped arrows; spawn eggs (0 = base, others = highlight); map tint). See the Minecraft Wiki "Model" page for the full historical table.

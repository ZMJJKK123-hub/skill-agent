---

name: forge-blocks
description: "Forge Block 机制：Block 创建（BlockBehaviour$Properties、strength/sound/lightLevel/friction 属性）、Block 注册（RegistryObject、BlockItem 关联、asItem 方法）、Block 状态系统（Property<?>、BlockState、StateDefinition$Builder、IntegerProperty/BooleanProperty/EnumProperty/DirectionProperty）、状态定义（createBlockStateDefinition、registerDefaultState、getStateForPlacement）、状态读写（getValue/setValue、Level#setBlockAndUpdate）、CreativeModeTab 配置、FeatureFlag 使用、元数据系统演进。"
whenToUse: "Use when creating Forge blocks or working with block states."

---

# Blocks

Blocks make up the Minecraft world: terrain, structures, machines.

## Creating a block

### Basic blocks

Simple blocks need no custom class — instantiate `Block` with a `BlockBehaviour$Properties` (via `#of`) and chain:

- `strength(hardness, resistance)`: hardness controls break time (stone 1.5, dirt 0.5; −1.0 = unbreakable like bedrock); resistance controls explosion resistance (stone 6.0, dirt 0.5).
- `sound(SoundType)`: punch/break/place sounds.
- `lightLevel(state -> value)`: light emission 0–15.
- `friction(value)`: slipperiness (ice 0.98).

> Blocks have no creative tab setter (handled by `BuildCreativeModeTabContentsEvent` when a `BlockItem` exists) and no translation key setter (generated from the registry name via `Block#getDescriptionId`).

### Advanced blocks

For functionality (interaction, etc.), subclass `Block`.

## Registering a block

A registered block has no item automatically. Create a `BlockItem` (registry name matching the block) to hold it in inventories; `Block#asItem` retrieves it (returns `Items#AIR` if absent). A `Block` without a `BlockItem` exists (e.g. `minecraft:water`).

Register all blocks; for config-disabling, disable the crafting recipe or use a `FeatureFlag` in the creative tab instead of skipping registration.

# Block States

The metadata system (pre-1.8) was replaced by the block state system (1.8+). Each block property is a `Property<?>`; a `Block` + property-value map = a `BlockState` (e.g. `minecraft:stone_button[facing=east,powered=true]`).

`BlockState`s are immutable; all combinations generate at startup, so keep properties minimal — a rule of thumb: **if it has a different name, it should be a separate block** (chair direction = property; wood types = separate blocks).

## Implementing

- Create `static final` properties: `IntegerProperty#create(name, min, max)`, `BooleanProperty#create(name)`, `EnumProperty#create(name, enumClass)`, `DirectionProperty#create(name, plane/axis)`. Reuse `BlockStateProperties` vanilla properties where possible.
- Override `Block#createBlockStateDefinition(StateDefinition$Builder)` and `#add(...)` every property.
- Set the default state via `Block#registerDefaultState(BlockState)` in the constructor (see `DoorBlock`).
- Override `Block#getStateForPlacement(BlockPlaceContext)` to choose the placed state.
- Read/write states via `BlockState#getValue`/`#setValue`, `Level#setBlockAndUpdate`/`#getBlockState`; compare with `==` (reference equality is valid).

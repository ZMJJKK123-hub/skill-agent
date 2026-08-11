---
name: forge-blocks
description: |
  Forge 方块（Block）完整指南。
  
  【涵盖内容】
  - Block 创建：Block 直接实例化 vs 继承 Block 子类
  - BlockBehaviour.Properties 属性：mapColor, strength(硬度), sound, noOcclusion, noCollission, instabreak, lightLevel, requiresCorrectToolForDrops 等
  - Block 注册（DeferredRegister<Block>）与 BlockItem 注册（DeferredRegister<Item>），Block 与 BlockItem 的关联（默认 `new BlockItem(block, new Item.Properties())`）
  - 方块物品的属性（稀有度、堆叠上限）
  - BlockState 属性系统：
    - Property 类型（BooleanProperty / IntegerProperty / EnumProperty / DirectionProperty）
    - createBlockStateDefinition 声明状态属性
    - 默认状态 provider（getStateDefinition().getDefault() 与 makeDefaultState）
    - 放置时设置状态（getStateForPlacement 或 updater）
    - 使用 BlockState 的 getValue / setValue
  - 方块被放置/破坏时更新相邻方块（updateNeighbours）
  
  【关键 API】
  Block, BlockBehaviour, BlockBehaviour.Properties, BlockItem, DeferredRegister, RegistryObject, BlockState, Property, BooleanProperty, IntegerProperty, EnumProperty, DirectionProperty, createBlockStateDefinition, getStateForPlacement, ResourceLocation
  
  【适用场景】需要添加自定义方块（基础方块、拥有状态的方块、可交互方块）时
  【不涵盖】方块实体数据（forge-blockentities）、物品系统（forge-items）、方块模型 JSON（forge-resources-client）
---

Blocks
======

Blocks are, obviously, essential to the Minecraft world. They make up all of the terrain, structures, and machines. Chances are if you are interested in making a mod, then you will want to add some blocks. This page will guide you through the creation of blocks, and some of the things you can do with them.

Creating a Block
----------------

### Basic Blocks

For simple blocks, which need no special functionality (think cobblestone, wooden planks, etc.), a custom class is not necessary. You can create a block by instantiating the `Block` class with a `BlockBehaviour$Properties` object. This `BlockBehaviour$Properties` object can be made using `BlockBehaviour$Properties#of`, and it can be customized by calling its methods. For instance:

- `strength` - The hardness controls the time it takes to break the block. It is an arbitrary value. For reference, stone has a hardness of 1.5, and dirt 0.5. If the block should be unbreakable a hardness of -1.0 should be used, see the definition of `Blocks#BEDROCK` as an example. The resistance controls the explosion resistance of the block. For reference, stone has a resistance of 6.0, and dirt 0.5.
- `sound` - Controls the sound the block makes when it is punched, broken, or placed. Requires a `SoundType` argument, see the [sounds] page for more details.
- `lightLevel` - Controls the light emission of the block. Takes a function with a `BlockState` parameter that returns a value from zero to fifteen.
- `friction` - Controls how slippery the block is. For reference, ice has a slipperiness of 0.98.

All these methods are *chainable* which means you can call them in series. See the `Blocks` class for examples of this.

!!! note
    Blocks have no setter for their `CreativeModeTab`. This is handled by the [`BuildCreativeModeTabContentsEvent`][creativetabs] if the block has an associated item (e.g. `BlockItem`). Furthermore, there is no setter for translation key of the block as it is generated from the registry name via `Block#getDescriptionId`.

### Advanced Blocks

Of course, the above only allows for extremely basic blocks. If you want to add functionality, like player interaction, a custom class is required. However, the `Block` class has many methods and unfortunately not every single one can be documented here. See the rest of the pages in this section for things you can do with blocks.

Registering a Block
-------------------

Blocks must be [registered][registering] to function.

!!! important
    A block in the level and a "block" in an inventory are very different things. A block in the level is represented by an `BlockState`, and its behavior defined by an instance of `Block`. Meanwhile, an item in an inventory is an `ItemStack`, controlled by an `Item`. As a bridge between the different worlds of `Block` and `Item`, there exists the class `BlockItem`. `BlockItem` is a subclass of `Item` that has a field `block` that holds a reference to the `Block` it represents. `BlockItem` defines some of the behavior of a "block" as an item, like how a right click places the block. It's possible to have a `Block` without an `BlockItem`. (E.g. `minecraft:water` exists a block, but not an item. It is therefore impossible to hold it in an inventory as one.)

    When a block is registered, *only* a block is registered. The block does not automatically have an `BlockItem`. To create a basic `BlockItem` for a block, one should set the registry name of the `BlockItem` to that of its `Block`. Custom subclasses of `BlockItem` may be used as well. Once an `BlockItem` has been registered for a block, `Block#asItem` can be used to retrieve it. `Block#asItem` will return `Items#AIR` if there is no `BlockItem` for the `Block`, so if you are not certain that there is an `BlockItem` for the `Block` you are using, check for if `Block#asItem` returns `Items#AIR`.

#### Optionally Registering Blocks

In the past there have been several mods that have allowed users to disable blocks/items in a configuration file. However, you shouldn't do this. There is no limit on the amount of blocks that can be register, so register all blocks in your mod! If you want a block to be disabled through a configuration file, you should disable the crafting recipe. If you would like to disable the block in the creative tab, use a `FeatureFlag` when building the contents within [`BuildCreativeModeTabContentsEvent`][creativetabs].

Further Reading
---------------

For information about block properties, such as those used for vanilla blocks like fences, walls, and many more, see the section on [blockstates].

[sounds]: ../gameeffects/sounds.md
[creativetabs]: ../items/index.md#creative-tabs
[registering]: ../concepts/registries.md#methods-for-registering
[blockstates]: states.md

---

Block States
============

Legacy Behavior
---------------------------------------

In Minecraft 1.7 and previous versions, blocks which need to store placement or state data that did not have BlockEntities used **metadata**. Metadata was an extra number stored with the block, allowing different rotations, facings, or even completely separate behaviors within a block.

However, the metadata system was confusing and limited, since it was stored as only a number alongside the block ID, and had no meaning except what was commented in the code. For example, to implement a block that can face a direction and be on either the upper or lower half of a block space (such as a stair): 

```Java
switch (meta) {
  case 0: { ... } // south and on the lower half of the block
  case 1: { ... } // south on the upper side of the block
  case 2: { ... } // north and on the lower half of the block
  case 3: { ... } // north and on the upper half of the block
  // ... etc. ...
}
```

Because the numbers carry no meaning by themselves, no one could know what they represent unless they had access to the source code and comments.

Introduction of States
---------------------------------------

In Minecraft 1.8 and above, the metadata system, along with the block ID system, was deprecated and eventually replaced with the **block state system**. The block state system abstracts out the details of the block's properties from the other behaviors of the block.

Each *property* of a block is described by an instance of `Property<?>`. Examples of block properties include instruments (`EnumProperty<NoteBlockInstrument>`), facing (`DirectionProperty`), poweredness (`Property<Boolean>`), etc. Each property has the value of the type `T` parametrized by `Property<T>`.

A unique pair can be constructed from the `Block` and a map of the `Property<?>` to their associated values. This unique pair is called a `BlockState`.

The previous system of meaningless metadata values were replaced by a system of block properties, which are easier to interpret and deal with. Previously, a stone button which is facing east and is powered or held down was represented by "`minecraft:stone_button` with metadata `9`". Now, this is represented by "`minecraft:stone_button[facing=east,powered=true]`".

Proper Usage of Block States
---------------------------------------

The `BlockState` system is a flexible and powerful system, but it also has limitations. `BlockState`s are immutable, and all combinations of their properties are generated on startup of the game. This means that having a `BlockState` with many properties and possible values will slow down the loading of the game, and befuddle anyone trying to make sense of your block logic.

Not all blocks and situations require the usage of `BlockState`; only the most basic properties of a block should be put into a `BlockState`, and any other situation is better off with having a `BlockEntity` or being a separate `Block`. Always consider if you actually need to use blockstates for your purposes.

!!! note
    A good rule of thumb is: **if it has a different name, it should be a separate block**.

An example is making chair blocks: the *direction* of the chair should be a *property*, while the different *types of wood* should be separated into different blocks.
An "Oak Chair" facing east (`oak_chair[facing=east]`) is different from a "Spruce Chair" facing west (`spruce_chair[facing=west]`).

Implementing Block States
---------------------------------------

In your Block class, create or reference `static final` `Property<?>` objects for every property that your Block has. You are free to make your own `Property<?>` implementations, but the means to do that are not covered in this article. The vanilla code provides several convenience implementations:

* `IntegerProperty`
    * Implements `Property<Integer>`. Defines a property that holds an integer value.
    * Created by calling `IntegerProperty#create(String propertyName, int minimum, int maximum)`.
* `BooleanProperty`
    * Implements `Property<Boolean>`. Defines a property that holds a `true` or `false` value.
    * Created by calling `BooleanProperty#create(String propertyName)`.
* `EnumProperty<E extends Enum<E>>`
    * Implements `Property<E>`. Defines a property that can take on the values of an Enum class.
    * Created by calling `EnumProperty#create(String propertyName, Class<E> enumClass)`.
    * It is also possible to use only a subset of the Enum values (e.g. 4 out of 16 `DyeColor`s). See the overloads of `EnumProperty#create`.
* `DirectionProperty`
    * This is a convenience implementation of `EnumProperty<Direction>`
    * Several convenience predicates are also provided. For example, to get a property that represents the cardinal directions, call `DirectionProperty.create("<name>", Direction.Plane.HORIZONTAL)`; to get the X directions, `DirectionProperty.create("<name>", Direction.Axis.X)`.

The class `BlockStateProperties` contains shared vanilla properties which should be used or referenced whenever possible, in place of creating your own properties.

When you have your desired `Property<>` objects, override `Block#createBlockStateDefinition(StateDefinition$Builder)` in your Block class. In that method, call `StateDefinition$Builder#add(...);`  with the parameters as every `Property<?>` you wish the block to have.

Every block will also have a "default" state that is automatically chosen for you. You can change this "default" state by calling the `Block#registerDefaultState(BlockState)` method from your constructor. When your block is placed it will become this "default" state. An example from `DoorBlock`:

```Java
this.registerDefaultState(
  this.stateDefinition.any()
    .setValue(FACING, Direction.NORTH)
    .setValue(OPEN, false)
    .setValue(HINGE, DoorHingeSide.LEFT)
    .setValue(POWERED, false)
    .setValue(HALF, DoubleBlockHalf.LOWER)
);
```

If you wish to change what `BlockState` is used when placing your block, you can overwrite `Block#getStateForPlacement(BlockPlaceContext)`. This can be used to, for example, set the direction of your block depending on where the player is standing when they place it.

Because `BlockState`s are immutable, and all combinations of their properties are generated on startup of the game, calling `BlockState#setValue(Property<T>, T)` will simply go to the `Block`'s `StateHolder` and request the `BlockState` with the set of values you want.

Because all possible `BlockState`s are generated at startup, you are free and encouraged to use the reference equality operator (`==`) to check if two `BlockState`s are equal.

Using `BlockState`'s
---------------------

You can get the value of a property by calling `BlockState#getValue(Property<?>)`, passing it the property you want to get the value of.
If you want to get a `BlockState` with a different set of values, simply call `BlockState#setValue(Property<T>, T)` with the property and its value.

You can get and place `BlockState`'s in the level using `Level#setBlockAndUpdate(BlockPos, BlockState)` and `Level#getBlockState(BlockPos)`. If you are placing a `Block`, call `Block#defaultBlockState()` to get the "default" state, and use subsequent calls to `BlockState#setValue(Property<T>, T)` as stated above to achieve the desired state.

---
name: forge-rendering-modelloaders
description: |
  Forge 自定义模型加载器（Model Loaders）指南。
  
  【涵盖内容】
  - BakedModel：自定义烘焙模型（IBakedModel 与 ModelState）
  - loadModel / ModelLoader：注册自定义模型加载器（ModelLoaderRegistry）
  - ItemOverrides：物品模型覆写（按 NBT / 物品状态返回不同模型）、ItemOverrides 自定义
  - BakedOverride：覆写条件与结果（BakedOverride 列表）
  - 变换：模型 transform（ModelState / Transformation）与 ItemTransform
  - 与 BlockState / ItemStack 关联的模型选择逻辑
  
  【关键 API】
  BakedModel, IBakedModel, ModelLoader, ModelLoaderRegistry, ItemOverrides, BakedOverride, ModelState, Transformation, IModelGeometry, ItemTransform
  
  【适用场景】需要自定义模型加载/烘焙逻辑（程序化生成模型、按数据选择模型）时
  【不涵盖】模型扩展（forge-rendering-modelextensions）、基础模型 JSON（forge-resources-client）
---

`BakedModel`
=============

`BakedModel` is the result of calling `UnbakedModel#bake` for the vanilla model loader or `IUnbakedGeometry#bake` for custom model loaders. Unlike `UnbakedModel` or `IUnbakedGeometry`, which purely represents a shape without any concept of items or blocks, `BakedModel` is not as abstract. It represents geometry that has been optimized and reduced to a form where it is (almost) ready to go to the GPU. It can also process the state of an item or block to change the model.

In a majority of cases, it is not really necessary to implement this interface manually. One can instead use one of the existing implementations.

### `getOverrides`

Returns the [`ItemOverrides`][overrides] to use for this model. This is only used if this model is being rendered as an item.

### `useAmbientOcclusion`

If the model is rendered as a block in the level, the block in question does not emit any light, and ambient occlusion is enabled. This causes the model to be rendered with [ambient occlusion](ambocc).

### `isGui3d`

If the model is rendered as an item in an inventory, on the ground as an entity, on an item frame, etc., this makes the model look "flat." In GUIs, this also disables the lighting.

### `isCustomRenderer`

!!! important
    Unless you know what you're doing, just `return false` from this and continue on.

When rendering this as an item, returning `true` causes the model to not be rendered, instead falling back to `BlockEntityWithoutLevelRenderer#renderByItem`. For certain vanilla items such as chests and banners, this method is hardcoded to copy data from the item into a `BlockEntity`, before using a `BlockEntityRenderer` to render that BE in place of the item. For all other items, it will use the `BlockEntityWithoutLevelRenderer` instance provided by `IClientItemExtensions#getCustomRenderer`. Refer to [BlockEntityWithoutLevelRenderer][bewlr] page for more information.

### `getParticleIcon`

Whatever texture should be used for the particles. For blocks, this shows when an entity falls on it, when it breaks, etc. For items, this shows when it breaks or when it's eaten.

!!! important
    The vanilla method with no parameters has been deprecated in favor of `#getParticleIcon(ModelData)` since model data can have an effect on how a particular model might be rendered.

### <s>`getTransforms`</s>

Deprecated in favor of implementing `#applyTransform`. The default implementation is fine if `#applyTransform` is implemented. See [Transform][transform].

### `applyTransform`

See [Transform][transform].

### `getQuads`

This is the main method of `BakedModel`. It returns a list of `BakedQuad`s: objects which contain the low-level vertex data that will be used to render the model. If the model is being rendered as a block, then the `BlockState` passed in is non-null. If the model is being rendered as an item, the `ItemOverrides` returned from `#getOverrides` is responsible for handling the state of the item, and the `BlockState` parameter will be `null`.

!!! note 
    The origin point for the vertices in a `BakedQuad` is the bottom, northwest corner. Vertex coordinate values less than 0 or greater than 1 will position the vertex outside of the block. To avoid lighting issues, provide the vertices in counterclockwise order.

The `Direction` passed in is used for face culling. If the block against the given side of another block being rendered is opaque, then the faces associated with that side are not rendered. If that parameter is `null`, all faces not associated with a side are returned (that will never be culled).

The `rand` parameter is an instance of Random.

It also takes in a non null `ModelData` instance. This can be used to define extra data when rendering the specific model via `ModelProperty`s. For example, one such property is `CompositeModel$Data`, which is used to store any additional submodel data for a model using the `forge:composite` model loader.

Note that this method is called very often: once for every combination of non-culled face and supported block render layer (anywhere between 0 to 28 times) *per block in a level*. This method should be as fast as possible, and should probably cache heavily.

[overrides]: ./itemoverrides.md
[ambocc]: https://en.wikipedia.org/wiki/Ambient_occlusion
[bewlr]: ../../items/bewlr.md
[transform]: ./transform.md

---

Custom Model Loaders
====================

A "model" is simply a shape. It can be a simple cube, it can be several cubes, it can be a truncated icosidodecahedron, or anything in between. Most models you'll see will be in the vanilla JSON format. Models in other formats are loaded into `IUnbakedGeometry`s by an `IGeometryLoader` at runtime. Forge provides default implementations for WaveFront OBJ files, buckets, composite models, models in different render layers, and a reimplementation of Vanilla's `builtin/generated` item model. Most things do not care about what loaded the model or what format it's in as they are all eventually represented by an `BakedModel` in code.

!!! warning
    Specifying a custom model loader through the top-level `loader` entry in a model JSON will cause the `elements` entry to be ignored unless it is consumed by the custom loader. All other vanilla entries will still be loaded and available in the unbaked `BlockModel` representation and may be consumed outside of the custom loader.

WaveFront OBJ Models
--------------------

Forge adds a loader for the `.obj` file format. To use these models, the JSON must reference the `forge:obj` loader. This loader accepts any model location that is in a registered namespace and whose path ends in `.obj`. The `.mtl` file should be placed in the same location with the same name as the `.obj` to be used automatically. The `.mtl` file will probably have to be manually edited to change the paths pointing to textures defined within the JSON. Additionally, the V axis for textures may be flipped depending on the external program that created the model (i.e. V = 0 may be the bottom edge, not the top). This may be rectified in the modelling program itself or done in the model JSON like so:

```js
{
  // Add the following line on the same level as a 'model' declaration
  "loader": "forge:obj",
  "flip_v": true,
  "model": "examplemod:models/block/model.obj",
  "textures": {
    // Can refer to in .mtl using #texture0
    "texture0": "minecraft:block/dirt",
    "particle": "minecraft:block/dirt"
  }
}
```

---

`ItemOverrides`
==================

`ItemOverrides` provides a way for an [`BakedModel`][baked] to process the state of an `ItemStack` and return a new `BakedModel`; thereafter, the returned model replaces the old one. `ItemOverrides` represents an arbitrary function `(BakedModel, ItemStack, ClientLevel, LivingEntity, int)` → `BakedModel`, making it useful for dynamic models. In vanilla, it is used to implement item property overrides.

### `ItemOverrides()`

Given a list of `ItemOverride`s, the constructor copies and bakes the list. The baked overrides may be accessed with `#getOverrides`.

### `resolve`

This takes an `BakedModel`, an `ItemStack`, a `ClientLevel`, a `LivingEntity`, and an `int` to produce another `BakedModel` to use for rendering. This is where models can handle the state of their items.

This should not mutate the level.

### `getOverrides`

Returns an immutable list containing all the [`BakedOverride`][override]s used by this `ItemOverrides`. If none are applicable, this returns the empty list.

## `BakedOverride`

This class represents a vanilla item override, which holds several `ItemOverrides$PropertyMatcher` for the properties on an item and a model to use in case those matchers are satisfied. They are the objects in the `overrides` array of a vanilla item JSON model:

```js
{
  // Inside a vanilla JSON item model
  "overrides": [
    {
      // This is an ItemOverride
      "predicate": {
        // This is the Map<ResourceLocation, Float>, containing the names of properties and their minimum values
        "example1:prop": 0.5
      },
      // This is the 'location', or target model, of the override, which is used if the predicate above matches
      "model": "example1:item/model"
    },
    {
      // This is another ItemOverride
      "predicate": {
        "example2:prop": 1
      },
      "model": "example2:item/model"
    }
  ]
}
```

[baked]: ./bakedmodel.md
[override]: #bakedoverride

---

Transform
==========

When an [`BakedModel`][bakedmodel] is being rendered as an item, it can apply special handling depending on which transform it is being rendered in. "Transform" means in what context the model is being rendered. The possible transforms are represented in code by the `ItemDisplayContext` enum. There are two systems for handling transform: the deprecated vanilla system, constituted by `BakedModel#getTransforms`, `ItemTransforms`, and `ItemTransform`, and the Forge system, embodied by the method `IForgeBakedModel#applyTransform`. The vanilla code is patched to favor using `applyTransform` over the vanilla system whenever possible.

`ItemDisplayContext`
---------------

`NONE` - Used for the display entity by default when no context is set and by Forge when a `Block`'s `RenderShape` is set to `#ENTITYBLOCK_ANIMATED`.

`THIRD_PERSON_LEFT_HAND`/`THIRD_PERSON_RIGHT_HAND`/`FIRST_PERSON_LEFT_HAND`/`FIRST_PERSON_RIGHT_HAND` - The first person values represent when the player is holding the item in their own hand. The third person values represent when another player is holding the item and the client is looking at them in the 3rd person. Hands are self-explanatory.

`HEAD` - Represents when any player is wearing the item in the helmet slot (e.g. pumpkins).

`GUI` - Represents when the item is being rendered in a `Screen`.

`GROUND` - Represents when the item is being rendered in the level as an `ItemEntity`.

`FIXED` - Used for item frames.

The Vanilla Way
---------------

The vanilla way of handling transform is through `BakedModel#getTransforms`. This method returns an `ItemTransforms`, which is a simple object that contains various `ItemTransform`s as `public final` fields. An `ItemTransform` represents a rotation, a translation, and a scale to be applied to the model. The `ItemTransforms` is a container for these, holding one for each of the `ItemDisplayContext`s except `NONE`. In the vanilla implementation, calling `#getTransform` for `NONE` results in the default transform, `ItemTransform#NO_TRANSFORM`.

The entire vanilla system for handling transforms is deprecated by Forge, and most implementations of `BakedModel` should simply `return ItemTransforms#NO_TRANSFORMS` (which is the default implementation) from `BakedModel#getTransforms`. Instead, they should implement `#applyTransform`.

The Forge Way
-------------

The Forge way of handling transforms is `#applyTransform`, a method patched into `BakedModel`. It supersedes the `#getTransforms` method.

#### `BakedModel#applyTransform`

Given a `ItemDisplayContext`, `PoseStack`, and a boolean to determine whether to apply the transform for the left hand, this method produces an `BakedModel` to be rendered. Because the returned `BakedModel` can be a totally new model, this method is more flexible than the vanilla method (e.g. a piece of paper that looks flat in hand but crumpled on the ground).

[bakedmodel]: ./bakedmodel.md

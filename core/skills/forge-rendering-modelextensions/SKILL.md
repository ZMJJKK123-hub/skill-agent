---
name: forge-rendering-modelextensions
description: |
  Forge 模型扩展（Model Extensions）指南。
  
  【涵盖内容】
  - 模型变换（Transforms）：模型在特定显示上下文（ItemDisplayContext：第三人称、第一人称、GUI、地面等）中的旋转/平移/缩放
  - 渲染类型（Render Types）：为模型不同部分指定不同渲染管线（solid / cutout / translucent / translucent_no_crumbling）
  - 部件可见性（Part Visibility）：按 ItemDisplayContext 条件控制模型子部件是否可见（ItemPartVisibility）
  - Face Data 自定义：修改模型面的渲染数据（面朝向、纹理 UV、着色）
  - 根变换（Root Transforms）与模型根节点变换
  
  【关键 API】
  IItemRenderProperties, ItemDisplayContext, RenderTypes, ModelPartVisibility, FaceData, Transformation, ModelState
  
  【适用场景】需要高级模型外观定制（不同视角不同显示、部分隐藏、半透明、面数据修改）时
  【不涵盖】模型加载器（forge-rendering-modelloaders）、基础模型 JSON（forge-resources-client）
---

Face Data
=========

In a vanilla "elements" model, additional data about an element's faces can be specified at either the element level or the face level. Faces which do not specify their own face data will fall back to the element's face data or a default if no face data is specified at the element level.

To use this extension for a generated item model, the model must be loaded through the `forge:item_layers` model loader due to the vanilla item model generator not being extended to read this additional data.

All values of the face data are optional.

Elements Model
--------------

In vanilla "elements" models, the face data applies to the face it is specified in or all faces of the element it is specified in which don't have their own face data.

!!!note
    If `forge_data` is specified on a face, it will not inherit any parameters from the element-level `forge_data` declaration.

The additional data can be specified in the two ways shown in this example:
```js
{
  "elements": [
    {
      "forge_data": {
        "color": "0xFFFF0000",
        "block_light": 15,
        "sky_light": 15,
        "ambient_occlusion": false
      },
      "faces": {
        "north": {
          "forge_data": {
            "color": "0xFFFF0000",
            "block_light": 15,
            "sky_light": 15,
            "ambient_occlusion": false
          },
          // ...
        },
        // ...
      },
      // ...
    }
  ]
}
```

Generated Item Model
--------------------

In item models generated using the `forge:item_layers` loader, face data is specified for each texture layer and applies to all of the geometry (front/back facing quads and edge quads).

The `forge_data` field must be located at the top level of the model JSON, with each key-value pair associating a face data object to a layer index.

In the following example, layer 1 will be tinted red and glow at full brightness:
```js
{
  "textures": {
    "layer0": "minecraft:item/stick",
    "layer1": "minecraft:item/glowstone_dust"
  },
  "forge_data": {
    "1": {
      "color": "0xFFFF0000",
      "block_light": 15,
      "sky_light": 15,
      "ambient_occlusion": false
    }
  }
}
```

Parameters
----------

### Color

Specifying a color value with the `color` entry will apply that color as a tint to the quads. Defaults to `0xFFFFFFFF` (white, fully opaque). The color must be in the `ARGB` format packed into a 32-bit integer and can be specified as either a hexadecimal string (`"0xAARRGGBB"`) or as a decimal integer literal (JSON does not support hexadecimal integer literals).

!!! warning
    The four color components are multiplied with the texture's pixels. Omitting the alpha component is equivalent to making it 0, which will make the geometry fully transparent.

This can be used as a replacement for tinting with [`BlockColor` and `ItemColor`][tinting] if the color values are constant.

### Block and Sky Light

Specifying a block and/or sky light value with the `block_light` and `sky_light` entry respectively will override the respective light value of the quads. Both values default to 0. The values must be in the range 0-15 (inclusive) and are treated as a minimum value for the respective light type when the face is rendered, meaning that a higher in-world value of the respective light type will override the specified value.

The specified light values are purely client-side and affect neither the server's light level nor the brightness of surrounding blocks.

### Ambient Occlusion

Specifying the `ambient_occlusion` flag will configure [AO] for the quads. Defaults to `true`. The behaviour of this flag is equivalent to the top-level `ambientocclusion` flag of the vanilla format.

![Ambient occlusion in action][ao_img]  
*Ambient occlusion enabled on the left and disabled on the right, demonstrated with the Smooth Lighting graphics setting*

!!! note
    If the top-level AO flag is set to false, specifying this flag as true on an element or face won't be able to override the top-level flag.
    ```js
    {
      "ambientocclusion": false,
      "elements": [
        {
          "forge_data": {
            "ambient_occlusion": true // Has no effect
          }
        }
      ]
    }
    ```

[tinting]: ../../resources/client/models/tinting.md
[AO]: https://en.wikipedia.org/wiki/Ambient_occlusion
[ao_img]: ./ambientocclusion_annotated.png

---

Render Types
============

Adding the `render_type` entry at the top level of the JSON suggests to the loader what render type the model should use. If not specified, the loader gets to pick the render type(s) used, often falling back to the render types returned by `ItemBlockRenderTypes#getRenderLayers()`.

Custom model loaders may ignore this field entirely.

!!! note
    Since 1.19 this is preferred over the deprecated method of setting the applicable render type(s) via `ItemBlockRenderTypes#setRenderLayer()` for blocks.

Example of a model for a cutout block with the glass texture

```js
{
  "render_type": "minecraft:cutout",
  "parent": "block/cube_all",
  "textures": {
    "all": "block/glass"
  }
}
```

Vanilla Values
--------------

The following options with the respective chunk and entity render type are supplied by Forge (`NamedRenderTypeManager#preRegisterVanillaRenderTypes()`):

* `minecraft:solid`
    * Chunk render type: `RenderType#solid()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_SOLID`
    * Used for fully solid blocks (i.e. Stone)
* `minecraft:cutout`
    * Chunk render type: `RenderType#cutout()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_CUTOUT`
    * Used for blocks where any given pixel is either fully transparent or fully opaque (i.e. Glass Block)
* `minecraft:cutout_mipped`
    * Chunk render type: `RenderType#cutoutMipped()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_CUTOUT`
    * Chunk and entity render type differ due to mipmapping on the entity render type making items look weird
    * Used for blocks where any given pixel is either fully transparent or fully opaque and the texture should be scaled down at larger distances ([mipmapping]) to avoid visual artifacts (i.e. Leaves)
* `minecraft:cutout_mipped_all`
    * Chunk render type: `RenderType#cutoutMipped()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_CUTOUT_MIPPED`
    * Used in similar cases as `minecraft:cutout_mipped` when the item representation should also have mipmapping applied
* `minecraft:translucent`
    * Chunk render type: `RenderType#translucent()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_TRANSLUCENT`
    * Used for blocks where any given pixel may be partially transparent (i.e. Stained Glass)
* `minecraft:tripwire`
    * Chunk render type: `RenderType#tripwire()`
    * Entity render type: `ForgeRenderTypes#ITEM_LAYERED_TRANSLUCENT`
    * Chunk and entity render type differ due to the tripwire render type not being feasible as an entity render type
    * Used for blocks with the special requirement of being rendered to the weather render target (i.e. Tripwire)

Custom Values
-------------

Custom named render types to be specified in a model can be registered in the `RegisterNamedRenderTypesEvent`. This event is fired on the mod event bus.

A custom named render type consists of two or three components:

* A chunk render type - any of the types in the list returned by `RenderType.chunkBufferLayers()` can be used
* A render type with the `DefaultVertexFormat.NEW_ENTITY` vertex format ("entity render type")
* A render type with the `DefaultVertexFormat.NEW_ENTITY` vertex format for use when the *Fabulous!* graphics mode is selected (optional)

The chunk render type is used when a block using this named render type is rendered as part of the chunk geometry.  
The required entity render type is used when an item using this named render type is rendered in the Fast and Fancy graphics modes (inventory, ground, item frame, etc.).  
The optional entity render type is used the same way as the required entity render type when the *Fabulous!* graphics mode is selected. This render type is needed in cases where the required entity render type does not work in the *Fabulous!* graphics mode (typically only applies to translucent render types).

```java
public static void onRegisterNamedRenderTypes(RegisterNamedRenderTypesEvent event)
{
  event.register("special_cutout", RenderType.cutout(), Sheets.cutoutBlockSheet());
  event.register("special_translucent", RenderType.translucent(), Sheets.translucentCullBlockSheet(), Sheets.translucentItemSheet());
}
```

These can then be addressed in JSON as `<your_mod_id>:special_cutout` and `<your_mod_id>:special_translucent`.

[mipmapping]: https://en.wikipedia.org/wiki/Mipmap

---

Root Transforms
===============

Adding the `transform` entry at the top level of a model JSON suggests to the loader that a transformation should be applied to all geometry right before the rotations in the [blockstate] file in the case of a block model, and before the [display transforms][displaytransform] in the case of an item model. The transformation is available through `IGeometryBakingContext#getRootTransform()` in `IUnbakedGeometry#bake()`.

Custom model loaders may ignore this field entirely.

The root transforms can be specified in two formats:

1. A JSON object containing a singular `matrix` entry containing a raw transformation matrix in the form of a nested JSON array with the last row omitted (3*4 matrix, row major order). The matrix is the composition of the translation, left rotation, scale, right rotation and the transformation origin in that order. Example demonstrating the structure:
    ```js
    "transform": {
        "matrix": [
            [ 0, 0, 0, 0 ],
            [ 0, 0, 0, 0 ],
            [ 0, 0, 0, 0 ]
        ]
    }
    ```
2. A JSON object containing any combination of the following optional entries:
    * `origin`: origin point used for the rotations and scaling
    * `translation`: relative translation
    * `rotation` or `left_rotation`: rotation around the translated origin to be applied before scaling
    * `scale`: scale relative to the translated origin
    * `right_rotation` or `post_rotation`: rotation around the translated origin to be applied after scaling

Element-wise specification
-------------------------

If the transformation is specified as a combination of the entries mentioned in option 4, these entries will be applied in the order of `translation`, `left_rotation`, `scale`, `right_rotation`.  
The transformation is moved to the specified origin as a last step.

```js
{
    "transform": {
        "origin": "center",
        "translation": [ 0, 0.5, 0 ],
        "rotation": { "y": 45 }
    },
    // ...
}
```

The elements are expected to be defined as follows:

### Origin

The origin can be specified either as an array of 3 floating point values representing a three-dimensional vector: `[ x, y, z ]` or as one of the three default values:

* `"corner"` (0, 0, 0)
* `"center"` (.5, .5, .5)
* `"opposing-corner"` (1, 1, 1)

If the origin is not specified, it defaults to `"opposing-corner"`.

### Translation

The translation must be specified as an array of 3 floating point values representing a three-dimensional vector: `[ x, y, z ]` and defaults to (0, 0, 0) if not present.

### Left and Right Rotation

The rotations can be specified in any one of the following four ways:

* Single JSON object with a single axis => rotation degree mapping: `{ "x": 90 }`
* Array of an arbitrary amount of JSON objects with the above format (applied in the order they are specified in): `[ { "x": 90 }, { "y": 45 }, { "x": -22.5 } ]`
* Array of 3 floating point values specifying the rotation in degrees around each axis: `[ 90, 180, 45 ]`
* Array of 4 floating point values specifying a quaternion directly: `[ 0.38268346, 0, 0, 0.9238795 ]` (example equals 45 degrees around the X axis)

If the respective rotation is not specified, it will default to no rotation.

### Scale

The scale must be specified as an array of 3 floating point values representing a three-dimensional vector: `[ x, y, z ]` and defaults to (1, 1, 1) if not present.

[blockstate]: https://minecraft.wiki/w/Tutorials/Models#Block_states
[displaytransform]: ../modelloaders/transform.md

---

Part Visibility
===============

Adding the `visibility` entry at the top level of a model JSON allows control over the visibility of different parts of the model to decide whether they should be baked into the final [`BakedModel`][bakedmodel]. The definition of a "part" is dependent on the model loader loading this model and custom model loaders are free to ignore this entry completely. Out of the model loaders provided by Forge only the [composite model loader][composite] and the [OBJ model loader][obj] make use of this functionality. The visibility entries are specified as `"part name": boolean` entries.

Example of a composite model with two parts, the second of which will not be baked into the final model, and two child models overriding this visibility to have only the first part and both parts visible respectively:
```js
// mycompositemodel.json
{
  "loader": "forge:composite",
  "children": {
    "part_one": {
      "parent": "mymod:mypartmodel_one"
    },
    "part_two": {
      "parent": "mymod:mypartmodel_two"
    }
  },
  "visibility": {
    "part_two": false
  }
}

// mycompositechild_one.json
{
  "parent": "mymod:mycompositemodel",
  "visibility": {
    "part_one": false,
    "part_two": true
  }
}

// mycompositechild_two.json
{
  "parent": "mymod:mycompositemodel",
  "visibility": {
    "part_two": true
  }
}
```

The visibility of a given part is determined by checking whether the model specifies a visibility for this part and, if not present, recursively checking the model's parent until either an entry is found or there is no further parent to check, in which case it defaults to true.

This allows setups like the following where multiple models use different parts of a single composite model:

1. A composite model specifies multiple components
2. Multiple models specify this composite model as their parent
3. These child models individually specify different visibilities for the parts

[bakedmodel]: ../modelloaders/bakedmodel.md
[composite]: ../modelloaders/index.md/#composite-models
[obj]: ../modelloaders/index.md/#wavefront-obj-models

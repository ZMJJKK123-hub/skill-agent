---
name: forge-resources-client
description: 'Forge client-side resources: assets directory, pack.mcmeta, block/item models, texture tinting, item model properties and model JSON.'
---

Resource Packs
==============

[Resource Packs][respack] allow for the customization of client resources through the `assets` directory. This includes textures, models, sounds, localizations, and others. Your mod (as well as Forge itself) can also have resource packs. Any user can therefore modify all the textures, models, and other assets defined within this directory.

### Creating a Resource Pack
Resource Packs are stored within your project's resources. The `assets` directory contains the contents of the pack, while the pack itself is defined by the `pack.mcmeta` alongside the `assets` folder.
Your mod can have multiple asset domains, since you can add or modify already existing resource packs, like vanilla's, Forge's, or another mod's.
You can then follow the steps found [at the Minecraft Wiki][createrespack] to create any resource pack.

Additional reading: [Resource Locations][resourcelocation]

[respack]: https://minecraft.wiki/w/Resource_Pack
[createrespack]: https://minecraft.wiki/w/Tutorials/Creating_a_resource_pack
[resourcelocation]: ../../concepts/resources.md#ResourceLocation

---

Models
======

The [model system][models] is Minecraft's way of giving blocks and items their shapes. Through the model system, blocks and items are mapped to their models, which define how they look. One of the main goals of the model system is to allow not only textures but the entire shape of a block/item to be changed by resource packs. Indeed, any mod that adds items or blocks also contains a mini-resource pack for their blocks and items.

Model Files
-----------

Models and textures are linked through [`ResourceLocation`][resloc]s but are stored in the `ModelManager` using `ModelResourceLocation`s. Models are referenced in different locations through the block or item's registry name depending on whether they are referencing [block states][statemodel] or [item models][itemmodels]. Blocks will have their `ModelResourceLocation` represent their registry name along with a stringified version of its current [`BlockState`][state] while items will use their registry name followed by `inventory`.

!!! note
    JSON models only support cuboid elements; there is no way to express a triangular wedge or anything like it. To have more complicated models, another format must be used.

### Textures

Textures, like models, are contained within resource packs and are referred to with `ResourceLocation`s. In Minecraft, the [UV coordinates][uv] (0,0) are taken to mean the **top-left** corner. UVs are *always* from 0 to 16. If a texture is larger or smaller, the coordinates are scaled to fit. A texture should also be square, and the side length of a texture should be a power of two, as doing otherwise breaks mipmapping (e.g. 1x1, 2x2, 8x8, 16x16, and 128x128 are good. 5x5 and 30x30 are not recommended because they are not powers of 2. 5x10 and 4x8 are completely broken as they are not square.). Textures should only ever be not a square if it is [animated][animated].

[models]: https://minecraft.wiki/w/Tutorials/Models#File_path
[resloc]: ../../../concepts/resources.md#resourcelocation
[statemodel]: https://minecraft.wiki/w/Tutorials/Models#Block_states
[itemmodels]: https://minecraft.wiki/w/Tutorials/Models#Item_models
[state]: ../../../blocks/states.md
[uv]: https://en.wikipedia.org/wiki/UV_mapping
[animated]: https://minecraft.wiki/w/Resource_Pack?so=search#Animation

---

Item Properties
===============

Item properties are a way for the "properties" of items to be exposed to the model system. An example is the bow, where the most important property is how far the bow has been pulled. This information is then used to choose a model for the bow, creating an animation for pulling it.

An item property assigns a certain `float` value to every `ItemStack` it is registered for, and vanilla item model definitions can use these values to define "overrides", where an item defaults to a certain model, but if an override matches, it overrides the model and uses another. They are useful mainly because they are continuous. For example, bows use item properties to define their pull animation. The item models are decided by the 'float' number predicates, it is not limited but generally between `0.0F` and `1.0F`. This allows resource packs to add as many models as they want for the bow pulling animation along that spectrum, instead of being stuck with four "slots" for their models in the animation. The same is true of the compass and clock.

Adding Properties to Items
--------------------------

`ItemProperties#register` is used to add a property to a certain item. The `Item` parameter is the item the property is being attached to (e.g. `ExampleItems#APPLE`). The `ResourceLocation` parameter is the name given to the property (e.g. `new ResourceLocation("pull")`). The `ItemPropertyFunction` is a functional interface that takes the `ItemStack`, the `ClientLevel` it is in (may be null), the `LivingEntity` that holds it (may be null), and the `int` containing the id of the holding entity (may be `0`), returning the `float` value for the property. For modded item properties, it is recommended that the mod id of the mod is used as the namespace (e.g. `examplemod:property` and not just `property`, as that really means `minecraft:property`). These should be done in `FMLClientSetupEvent`.
There's also another method `ItemProperties#registerGeneric` that is used to add properties to all items, and it does not take `Item` as its parameter since all items will apply this property.

!!! important
    Use `FMLClientSetupEvent#enqueueWork` to proceed with the tasks, since the data structures in `ItemProperties` are not thread-safe.

!!! note
    `ItemPropertyFunction` is deprecated by Mojang in favor of using the subinterface `ClampedItemPropertyFunction` which clamps the result between `0` and `1`.

Using Overrides
---------------

The format of an override can be seen on the [wiki][format], and a good example can be found in `model/item/bow.json`. For reference, here is a hypothetical example of an item with an `examplemod:power` property. If the values have no match, the default is the current model, but if there are multiple matches, the last match in the list will be selected.

!!! important
    A predicate applies to all values *greater than or equal to* the given value.

```js
{
  "parent": "item/generated",
  "textures": {
    // Default
    "layer0": "examplemod:items/example_partial"
  },
  "overrides": [
    {
      // power >= .75
      "predicate": {
        "examplemod:power": 0.75
      },
      "model": "examplemod:item/example_powered"
    }
  ]
}
```

And here is a hypothetical snippet from the supporting code. Unlike the older versions (lower than 1.16.x), this needs to be done on client side only because `ItemProperties` does not exist on server.

```java
private void setup(final FMLClientSetupEvent event)
{
  event.enqueueWork(() ->
  {
    ItemProperties.register(ExampleItems.APPLE, 
      ResourceLocation.fromNamespaceAndPath(ExampleMod.MODID, "pulling"), (stack, level, living, id) -> {
        return living != null && living.isUsingItem() && living.getUseItem() == stack ? 1.0F : 0.0F;
      });
  });
}
```

[format]: https://minecraft.wiki/w/Tutorials/Models#Item_models

---

Coloring Textures
=================

Many blocks and items in vanilla change their texture color depending on where they are or what properties they have, such as grass. Models support specifying "tint indices" on faces, which are integers that can then be handled by `BlockColor`s and `ItemColor`s. See the [wiki][] for information on how tint indices are defined in vanilla models.

### `BlockColor`/`ItemColor`

Both of these are single-method interfaces. `BlockColor` takes a `BlockState`, a (nullable) `BlockAndTintGetter`, and a (nullable) `BlockPos`. `ItemColor` takes an `ItemStack`. Both of them take an `int` parameter `tintIndex`, which is the tint index of the face being colored. Both of them return an `int`, a color multiplier. This `int` is treated as 4 unsigned bytes, alpha, red, green, and blue, in that order, from most significant byte to least. For each pixel in the tinted face, the value of each color channel is `(int)((float) base * multiplier / 255.0)`, where `base` is the original value for the channel, and `multiplier` is the associated byte from the color multiplier. Note that blocks do not use the alpha channel. For example, the grass texture, untinted, looks white and gray. The `BlockColor` and `ItemColor` for grass return color multipliers with low red and blue components, but high alpha and green components, (at least in warm biomes) so when the multiplication is performed, the green is brought out and the red/blue diminished.

If an item inherits from the `builtin/generated` model, each layer ("layer0", "layer1", etc.) has a tint index corresponding to its layer index.

### Creating Color Handlers

`BlockColor`s need to be registered to the `BlockColors` instance of the game. `BlockColors` can be acquired through `RegisterColorHandlersEvent$Block`, and an `BlockColor` can be registered by `#register`. Note that this does not cause the `BlockItem` for the given block to be colored. `BlockItem`s are items and need to be colored with an `ItemColor`.

```java
@SubscribeEvent
public void registerBlockColors(RegisterColorHandlersEvent.Block event){
  event.register(myBlockColor, coloredBlock1, coloredBlock2, ...);
}
```

`ItemColor`s need to be registered to the `ItemColors` instance of the game. `ItemColors` can be acquired through `RegisterColorHandlersEvent$Item`, and an `ItemColor` can be registered by `#register`. This method is overloaded to also take `Block`s, which simply registers the color handler for the item `Block#asItem` (i.e. the block's `BlockItem`).

```java
@SubscribeEvent
public void registerItemColors(RegisterColorHandlersEvent.Item event){
  event.register(myItemColor, coloredItem1, coloredItem2, ...);
}
```

[wiki]: https://minecraft.wiki/w/Tutorials/Models#Block_models

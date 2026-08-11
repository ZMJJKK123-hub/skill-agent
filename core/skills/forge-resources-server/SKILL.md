---
name: forge-resources-server
description: |
  Forge 服务端数据（data 数据包）指南。
  
  【涵盖内容】
  - 数据包结构：data/<modid>/ 下各目录（recipes、loot_tables、tags、advancements、loot_modifiers 等）
  - 配方：JSON 配方（shaped / shapeless / smelting / smithing / stonecutting 等）、Ingredient 条件（ItemPredicate、count、tag）、非数据包配方（代码内 Recipe 实现）
  - 战利品表：loot_tables/blocks/<block>.json 或 entities/<entity>.json、LootPool 条件（randomChance、ExplosionCondition、survives_explosion）、战利品函数（set_count、looting_enchant）
  - 标签（Tags）：tags/blocks/*.json、tags/items/*.json、TagKey 引用、Forge 提供的标签（forge: 命名空间）
  - 全局战利品修改器（Global Loot Modifiers）：loot_modifiers.json 声明 + 代码实现（LootModifier）
  - 进度：advancements/*.json（条件、奖励、父进度）
  - 条件数据与数据包内容校验（advancement 条件 component）
  
  【关键 API】
  data, recipes JSON, Ingredient, ItemPredicate, LootTable, LootPool, LootContext, TagKey, GlobalLootModifiers, GlobalLootModifierProvider, Advancement, ItemTags, BlockTags
  
  【适用场景】需要编写/理解服务端数据 JSON（配方、战利品、标签、进度、全局战利品修改器）时
  【不涵盖】客户端资源（forge-resources-client）、数据生成器（forge-datagen-server）
---

Advancements
============

Advancements are tasks that can be achieved by the player which may advance the progress of the game. Advancements can trigger based on any action the player may be directly involved in.

All advancement implementations within vanilla are data driven via JSON. This means that a mod is not necessary to create a new advancement, only a [data pack][datapack]. A full list on how to create and put these advancements within the mod's `resources` can be found on the [Minecraft Wiki][wiki]. Additionally, advancements can be [loaded conditionally and defaulted][conditional] depending on what information is present (mod loaded, item exists, etc.).

Advancement Criteria
--------------------

To unlock an advancement, the specified criteria must be met. Criteria are tracked through triggers which execute when a certain action is performed: killing an entity, changing an inventory, breading animals, etc. Any time an advancement is loaded into the game, the criteria defined are read and added as listeners to the trigger. Afterwards a trigger function is called (usually named `#trigger`) which checks all listeners as to whether the current state meets the conditions of the advancement criteria. The criteria listeners for the advancement are only removed once the advancement has been obtained by completing all requirements.

Requirements are defined as an array of string arrays representing the name of the criteria specified on the advancement. An advancement is completed once one string array of criteria has been met:

```js
// In some advancement JSON

// List of defined criteria to meet
"criteria": {
  "example_criterion1": { /*...*/ },
  "example_criterion2": { /*...*/ },
  "example_criterion3": { /*...*/ },
  "example_criterion4": { /*...*/ }
},

// This advancement is only unlocked once
// - Criteria 1 AND 2 have been met
// OR
// - Criteria 3 and 4 have been met
"requirements": [
  [
    "example_criterion1",
    "example_criterion2"
  ],
  [
    "example_criterion3",
    "example_criterion4"
  ]
]
```

A list of criteria triggers defined by vanilla can be found in `CriteriaTriggers`. Additionally, the JSON formats are defined on the [Minecraft Wiki][triggers].

### Custom Criteria Triggers

Custom criteria triggers can be created by implementing `SimpleCriterionTrigger` for the created `AbstractCriterionTriggerInstance` subclass.

### AbstractCriterionTriggerInstance Subclass

The `AbstractCriterionTriggerInstance` represents a single criteria defined in the `criteria` object. Trigger instances are responsible for holding the defined conditions, returning whether the inputs match the condition, and writing the instance to JSON for data generation.

Conditions are usually passed in through the constructor. The `AbstractCriterionTriggerInstance` super constructor requires the instance to define the registry name of the trigger and the conditions the player must meet as an `ContextAwarePredicate`. The registry name of the trigger should be supplied to the super directly while the conditions of the player should be a constructor parameter.

```java
// Where ID is the registry name of the trigger
public ExampleTriggerInstance(ContextAwarePredicate player, ItemPredicate item) {
  super(ID, player);
  // Store the item condition that must be met
}
```

!!! note
    Typically, trigger instances have a static constructor which allow these instances to be easily created for data generation. These static factory methods can also be statically imported instead of the class itself.

    ```java
    public static ExampleTriggerInstance instance(ContextAwarePredicate player, ItemPredicate item) {
      return new ExampleTriggerInstance(player, item);
    }
    ```

Additionally, the `#serializeToJson` method should be overridden. The method should add the conditions of the instance to the other JSON data.

```java
@Override
public JsonObject serializeToJson(SerializationContext context) {
  JsonObject obj = super.serializeToJson(context);
  // Write conditions to json
  return obj;
}
```

Finally, a method should be added which takes in the current data state and returns whether the user has met the necessary conditions. The conditions of the player are already checked through `SimpleCriterionTrigger#trigger(ServerPlayer, Predicate)`. Most trigger instances call this method `#matches`.

```java
// This method is unique for each instance and is as such not overridden
public boolean matches(ItemStack stack) {
  // Since ItemPredicate matches a stack, a stack is the input
  return this.item.matches(stack);
}
```

### SimpleCriterionTrigger

The `SimpleCriterionTrigger<T>` subclass, where `T` is the type of the trigger instance, is responsible for specifying the registry name of the trigger, creating a trigger instance, and a method to check trigger instances and run attached listeners on success.

The registry name of the trigger is supplied to `#getId`. This should match the registry name supplied to the trigger instance.

A trigger instance is created via `#createInstance`. This method reads a criteria from JSON.

```java
@Override
public ExampleTriggerInstance createInstance(JsonObject json, ContextAwarePredicate player, DeserializationContext context) {
  // Read conditions from JSON: item
  return new ExampleTriggerInstance(player, item);
}
```

Finally, a method is defined to check all trigger instances and run the listeners if their condition is met. This method takes in the `ServerPlayer` and whatever other data defined by the matching method in the `AbstractCriterionTriggerInstance` subclass. This method should internally call `SimpleCriterionTrigger#trigger` to properly handle checking all listeners. Most trigger instances call this method `#trigger`.

```java
// This method is unique for each trigger and is as such not overridden
public void trigger(ServerPlayer player, ItemStack stack) {
  this.trigger(player,
    // The condition checker method within the AbstractCriterionTriggerInstance subclass
    triggerInstance -> triggerInstance.matches(stack)
  );
}
```

Afterwards, an instance should be registered using `CriteriaTriggers#register` during `FMLCommonSetupEvent`.

!!! important
    `CriteriaTriggers#register` must be enqueued to the synchronous work queue via `FMLCommonSetupEvent#enqueueWork` as the method is not thread-safe.

### Calling the Trigger

Whenever the action being checked is performed, the `#trigger` method defined by the `SimpleCriterionTrigger` subclass should be called.

```java
// In some piece of code where the action is being performed
// Where EXAMPLE_CRITERIA_TRIGGER is the custom criteria trigger
public void performExampleAction(ServerPlayer player, ItemStack stack) {
  // Run code to perform action
  EXAMPLE_CRITERIA_TRIGGER.trigger(player, stack);
}
```

Advancement Rewards
-------------------

When an advancement is completed, rewards may be given out. These can be a combination of experience points, loot tables, recipes for the recipe book, or a [function] executed as a creative player.

```js
// In some advancement JSON
"rewards": {
  "experience": 10,
  "loot": [
    "minecraft:example_loot_table",
    "minecraft:example_loot_table2"
    // ...
  ],
  "recipes": [
    "minecraft:example_recipe",
    "minecraft:example_recipe2"
    // ...
  ],
  "function": "minecraft:example_function"
}
```

[datapack]: https://minecraft.wiki/w/Data_pack
[wiki]: https://minecraft.wiki/w/Advancement/JSON_format
[conditional]: ./conditional.md#implementations
[function]: https://minecraft.wiki/w/Function_(Java_Edition)
[triggers]: https://minecraft.wiki/w/Advancement/JSON_format#List_of_triggers

---

Conditionally-Loaded Data
=========================

There are times when modders may want to include data-driven objects using information from another mod without having to explicitly make that mod a dependency. Other cases may be to swap out certain objects with other modded entries when they are present. This can be done through the conditional subsystem.

Implementations
---------------

Currently, conditional loading is implemented for recipes and advancements. For any conditional recipe or advancement, a list of conditions to datum pair is loaded. If the conditions specified for a datum in the list is true, then that datum is returned. Otherwise, the datum is discarded.

```js
{
  // The type needs to be specified for recipes as they can have custom serializers
  // Advancements do not need this type
  "type": "forge:conditional",
  
  "recipes": [ // Or 'advancements' for Advancements
    {
      // The conditions to check
      "conditions": [
        // Conditions in the list are ANDed together
        {
          // Condition 1
        },
        {
          // Condition 2
        }
      ],
      "recipe": { // Or 'advancement' for Advancements
        // The recipe to use if all conditions succeed
      }
    },
    {
      // Next condition to check if the previous fails
    },
  ]
}
```

Conditionally-loaded data additionally have wrappers for [data generation][datagen] through `ConditionalRecipe$Builder` and `ConditionalAdvancement$Builder`.

Conditions
----------

Conditions are specified by setting `type` to the name of the condition as specified by [`IConditionSerializer#getID`][serializer].

### True and False

Boolean conditions consist of no data and return the expected value of the condition. They are represented by `forge:true` and `forge:false`.

```js
// For some condition
{
  // Will always return true (or false for 'forge:false')
  "type": "forge:true"
}
```

### Not, And, and Or

Boolean operator conditions consist of the condition(s) being operated upon and apply the following logic. They are represented by `forge:not`, `forge:and`, and `forge:or`.


```js
// For some condition
{
  // Inverts the result of the stored condition
  "type": "forge:not",
  "value": {
    // A condition
  }
}
```

```js
// For some condition
{
  // ANDs the stored conditions together (or ORs for 'forge:or')
  "type": "forge:and",
  "values": [
    {
      // First condition
    },
    {
      // Second condition to be ANDed (or ORed for 'forge:or')
    }
  ]
}
```

### Mod Loaded

`ModLoadedCondition` returns true whenever the specified mod with the given id is loaded in the current application. This is represented by `forge:mod_loaded`.

```js
// For some condition
{
  "type": "forge:mod_loaded",
   // Returns true if 'examplemod' is loaded
  "modid": "examplemod"
}
```

### Item Exists

`ItemExistsCondition` returns true whenever the given item has been registered in the current application. This is represented by `forge:item_exists`.

```js
// For some condition
{
  "type": "forge:item_exists",
   // Returns true if 'examplemod:example_item' has been registered
  "item": "examplemod:example_item"
}
```

### Tag Empty

`TagEmptyCondition` returns true whenever the given item tag has no items within it. This is represented by `forge:tag_empty`.

```js
// For some condition
{
  "type": "forge:tag_empty",
   // Returns true if 'examplemod:example_tag' is an item tag with no entries
  "tag": "examplemod:example_tag"
}
```

Creating Custom Conditions
--------------------------

Custom conditions can be created by implementing `ICondition` and its associated `IConditionSerializer`.

### ICondition

Any condition only need to implement two methods:

Method | Description
:---:  | :---
getID  | The registry name of the condition. Must be equivalent to [`IConditionSerializer#getID`][serializer]. Used only for [data generation][datagen].
test   | Returns true if the condition has been satisfied.

!!! note
    Every `#test` has access to some `IContext` representing the state of the game. Currently, only tags can be obtained from a registry.

### IConditionSerializer

Serializers need to implement three methods:

Method | Description
:---:  | :---
getID  | The registry name of the condition. Must be equivalent to [`ICondition#getID`][condition].
read   | Reads the condition data from JSON.
write  | Writes the given condition data to JSON.

!!! note
    Condition serializers are not responsible for writing or reading the type of the serializer, similar to other serializer implementations in Minecraft.

Afterwards, a static instance should be declared to hold the initialized serializer and then registered using `CraftingHelper#register` either during the `RegisterEvent` for `RecipeSerializer`s or during `FMLCommonSetupEvent`.

```java
// In some serializer class
public static final ExampleConditionSerializer INSTANCE = new ExampleConditionSerializer();

// In some handler class
public void registerSerializers(RegisterEvent event) {
  event.register(ForgeRegistries.Keys.RECIPE_SERIALIZERS,
    helper -> CraftingHelper.register(INSTANCE)
  );
}
```

!!! important
    If using `FMLCommonSetupEvent` to register a condition serializer, it must be enqueued to the synchronous work queue via `FMLCommonSetupEvent#enqueueWork` as `CraftingHelper#register` is not thread-safe.

[datagen]: ../../datagen/server/recipes.md
[serializer]: #iconditionserializer
[condition]: #icondition

---

Global Loot Modifiers
===========

Global Loot Modifiers are a data-driven method of handling modification of harvested drops without the need to overwrite dozens to hundreds of vanilla loot tables or to handle effects that would require interactions with another mod's loot tables without knowing what mods may be loaded. Global Loot Modifiers are also stacking, rather than last-load-wins, similar to tags.

Registering a Global Loot Modifier
-------------------------------

You will need 4 things:

1. Create a `global_loot_modifiers.json`.
    * This will tell Forge about your modifiers and works similar to [tags].
2. A serialized json representing your modifier.
    * This will contain all of the data about your modification and allows data packs to tweak your effect.
3. A class that extends `IGlobalLootModifier`.
    * The operational code that makes your modifier work. Most modders can extend `LootModifier` as it supplies base functionality.
4. Finally, a codec to encode and decode your operational class.
    * This is [registered] as any other `IForgeRegistryEntry`.

The `global_loot_modifiers.json`
-------------------------------

The `global_loot_modifiers.json` represents all loot modifiers to be loaded into the game. This file **MUST** be placed within `data/forge/loot_modifiers/global_loot_modifiers.json`.

!!! important
    `global_loot_modifiers.json` will only be read in the `forge` namespace. The file will be neglected if it is under the mod's namespace.

`entries` is an *ordered list* of the modifiers that will be loaded. The [ResourceLocation][resloc]s specified points to their associated entry within `data/<namespace>/loot_modifiers/<path>.json`. This is primarily relevant to data pack makers for resolving conflicts between modifiers from separate mods.

`replace`, when `true`, changes the behavior from appending loot modifiers to the global list to replacing the global list entries entirely. Modders will want to use `false` for compatibility with other mod implementations. Datapack makers may want to specify their overrides with `true`.

```js
{
  "replace": false, // Must be present
  "entries": [
    // Represents a loot modifier in 'data/examplemod/loot_modifiers/example_glm.json'
    "examplemod:example_glm",
    "examplemod:example_glm2"
    // ...
  ]
}
```

The Serialized JSON
-------------------------------

This file contains all of the potential variables related to your modifier, including the conditions that must be met prior to modifying any loot. Avoid hard-coded values wherever possible so that data pack makers can adjust balance if they wish to.

`type` represents the registry name of the [codec] used to read the associated JSON file. This must always be present.

`conditions` should represent the loot table conditions for this modifier to activate. Conditions should avoid being hardcoded to allow datapack creators as much flexibility to adjust the criteria. This must also be always present.

!!! important
    Although `conditions` should represent what is needed for the modifier to activate, this is only the case if using the bundled Forge classes. If using `LootModifier` as a subclass, all conditions will be **ANDed** together and checked to see if the modifier should be applied.

Any additional properties read by the serializer and defined by the modifier can also be specified.

```js
// Within data/examplemod/loot_modifiers/example_glm.json
{
  "type": "examplemod:example_loot_modifier",
  "conditions": [
    // Normal loot table conditions
    // ...
  ],
  "prop1": "val1",
  "prop2": 10,
  "prop3": "minecraft:dirt"
}
```

`IGlobalLootModifier`
---------------------

To supply the functionality a global loot modifier specifies, a `IGlobalLootModifier` implementation must be specified. These are instances generated each time a serializer decodes the information from JSON and supplies it into this object.

There are two methods that needs to be defined in order to create a new modifier: `#apply` and `#codec`. `#apply` takes in the current loot that will be generated along with the context information such as the currently level or additional defined parameters. It returns the list of drops to generate.

!!! note
    The returned list of drops from any one modifier is fed into other modifiers in the order they are registered. As such, modified loot can be modified by another loot modifier.

`#codec` returns the registered [codec] used to encode and decode the modifier to/from JSON.

### The `LootModifier` Subclass

`LootModifier` is an abstract implementation of `IGlobalLootModifier` to provide the base functionality which most modders can easily extend and implement. This expands upon the existing interface by defining the `#apply` method to check the conditions to determine whether or not to modify the generated loot.

There are two things of note within the subclass implementation: the constructor which must take in an array of `LootItemCondition`s and the `#doApply` method.

The array of `LootItemCondition`s define the list of conditions that must be true before the loot can be modified. The supplied conditions are **ANDed** together, meaning that all conditions must be true.

The `#doApply` method works the same as the `#apply` method except that it only executes once all conditions return true.

```java
public class ExampleModifier extends LootModifier {

  public ExampleModifier(LootItemCondition[] conditionsIn, String prop1, int prop2, Item prop3) {
    super(conditionsIn);
    // Store the rest of the parameters
  }

  @NotNull
  @Override
  protected ObjectArrayList<ItemStack> doApply(ObjectArrayList<ItemStack> generatedLoot, LootContext context) {
    // Modify the loot and return the new drops
  }

  @Override
  public Codec<? extends IGlobalLootModifier> codec() {
    // Return the codec used to encode and decode this modifier
  }
}
```

The Loot Modifier Codec
-----------------------

The connector between the JSON and the `IGlobalLootModifier` instance is a [`Codec<T>`][codecdef], where `T` represents the type of the `IGlobalLootModifier` to use.

For ease of convenience, a loot conditions codec has been provided for an easy addition to a record-like codec via `LootModifier#codecStart`. This is utilized for [data generation][datagen] of the associated loot modifier.

```java
// For some DeferredRegister<Codec<? extends IGlobalLootModifier>> REGISTRAR
public static final RegistryObject<Codec<ExampleModifier>> = REGISTRAR.register("example_codec", () ->
  RecordCodecBuilder.create(
    inst -> LootModifier.codecStart(inst).and(
      inst.group(
        Codec.STRING.fieldOf("prop1").forGetter(m -> m.prop1),
        Codec.INT.fieldOf("prop2").forGetter(m -> m.prop2),
        ForgeRegistries.ITEMS.getCodec().fieldOf("prop3").forGetter(m -> m.prop3)
      )
    ).apply(inst, ExampleModifier::new)
  )
);
```

[Examples][examples] can be found on the Forge Git repository, including silk touch and smelting effects.

[tags]: ./tags.md
[resloc]: ../../concepts/resources.md#ResourceLocation
[codec]: #the-loot-modifier-codec
[registered]: ../../concepts/registries.md#methods-for-registering
[codecdef]: ../../datastorage/codecs.md
[datagen]: ../../datagen/server/glm.md
[examples]: https://github.com/MinecraftForge/MinecraftForge/blob/1.20.x/src/test/java/net/minecraftforge/debug/gameplay/loot/GlobalLootModifiersTest.java

---

Datapacks
=========
In 1.13, Mojang added [datapacks][datapack] to the base game. They allow for the modification of the files for logical servers through the `data` directory. This includes advancements, loot_tables, structures, recipes, tags, etc. Forge, and your mod, can also have datapacks. Any user can therefore modify all the recipes, loot tables, and other data defined within this directory.

### Creating a Datapack
Datapacks are stored within the `data` directory within your project's resources.
Your mod can have multiple data domains, since you can add or modify already existing datapacks, like vanilla's, forge's, or another mod's.
You can then follow the steps found [here][createdatapack] to create any datapack.

Additional reading: [Resource Locations][resourcelocation]

[datapack]: https://minecraft.wiki/w/Data_pack
[createdatapack]: https://minecraft.wiki/w/Tutorials/Creating_a_data_pack
[resourcelocation]: ../../concepts/resources.md#ResourceLocation

---

Loot Tables
===========

Loot tables are logic files which dictate what should happen when various actions or scenarios occur. Although the vanilla system deals purely with item generation, the system can be expanded to perform any number of defined actions.

Data-Driven Tables
------------------

Most loot tables within vanilla are data driven via JSON. This means that a mod is not necessary to create a new loot table, only a [Data pack][datapack]. A full list on how to create and put these loot tables within the mod's `resources` folder can be found on the [Minecraft Wiki][wiki].

Using a Loot Table
------------------

A loot table is referenced by its `ResourceLocation` which points to `data/<namespace>/loot_tables/<path>.json`. The `LootTable` associated with the reference can be obtained using `LootDataResolver#getLootTable`, where `LootDataResolver` can be obtained via `MinecraftServer#getLootData`.

A loot table is always generated with given parameters. The `LootParams` contains the level the table is generated in, luck for better generation, the `LootContextParam`s which define scenario context, and any dynamic information that should occur on activation. The `LootParams` can be created using the constructor of the `LootParams$Builder` builder, and built via `LootParams$Builder#create` by passing in the `LootContextParamSet`.

A loot table may also have some context. The `LootContext` takes in the built `LootParams` and can set some random seeded instance. The context is created via the builder `LootContext$Builder` and built using `LootContext$Builder#create` by passing in a nullable `ResourceLocation` representing the random instance to use.

A `LootTable` can be used to generate `ItemStack`s using one of the available methods which may take in a `LootParams` or a `LootContext`:

Method              | Description
:---:               | :---
`getRandomItemsRaw` | Consumes the items generated by the loot table.
`getRandomItems`    | Returns the items generated by the loot table.
`fill`              | Fills a container with the generated loot table.

!!! note
    Loot tables were built for generating items, so the methods expect some handling for the `ItemStack`s.

Additional Features
-------------------

Forge provides some additional behavior to loot tables for greater control of the system.

### `LootTableLoadEvent`

`LootTableLoadEvent` is an [event] fired on the Forge event bus which is fired whenever a loot table is loaded. If the event is canceled, then an empty loot table will be loaded instead.

!!! important
    Do **not** modify a loot table's drops through this event. Those modifications should be done using [global loot modifiers][glm].

### Loot Pool Names

Loot pools can be named using the `name` key. Any non-named loot pool will be the hash code of the pool prefixed by `custom#`.

```js
// For some loot pool
{
  "name": "example_pool", // Pool will be named 'example_pool'
  "rolls": {
    // ...
  },
  "entries": {
    // ...
  }
}
```

### Looting Modifiers

Loot tables are now affected by the `LootingLevelEvent`, on the Forge event bus, in addition to the looting enchantment.

### Additional Context Parameters

Forge extends certain parameter sets to account for missing contexts which may be applicable. `LootContextParamSets#CHEST` now allows for a `LootContextParams#KILLER_ENTITY` as chest minecarts are entities which can be broken (or 'killed'). `LootContextParamSets#FISHING` also allows for a `LootContextParams#KILLER_ENTITY` since the fishing hook is also an entity which is retracted (or 'killed') when the player retrieves it.

### Multiple Items on Smelting

When using the `SmeltItemFunction`, a smelted recipe will now return the actual number of items from the result instead of a single smelted item (e.g. if a smelting recipe returns 3 items and there are 3 drops, then the result would be 9 smelted items instead of 3).

### Loot Table Id Condition

Forge adds an additional `LootItemCondition` which allows certain items to generate for a specific table. This is typically used within [global loot modifiers][glm].

```js
// In some loot pool or pool entry
{
  "conditions": [
    {
      "condition": "forge:loot_table_id",
      // Will apply when the loot table is for dirt
      "loot_table_id": "minecraft:blocks/dirt"
    }
  ]
}
```

### Can Tool Perform Action Condition

Forge adds an additional `LootItemCondition` which checks whether the given `LootContextParams#TOOL` can perform the specified `ToolAction`.

```js
// In some loot pool or pool entry
{
  "conditions": [
    {
      "condition": "forge:can_tool_perform_action",
      // Will apply when the tool can strip a log like an axe
      "action": "axe_strip"
    }
  ]
}
```

[datapack]: https://minecraft.wiki/w/Data_pack
[wiki]: https://minecraft.wiki/w/Loot_table
[event]: ../../concepts/events.md#creating-an-event-handler
[glm]: ./glm.md

---

Tags
====

Tags are generalized sets of objects in the game used for grouping related things together and providing fast membership checks.

Finding Tags
------------
When looking for existing tags, there's two main places to check:

### Vanilla Tags
Vanilla tags are declared in the `net.minecraft.tags` package. For example, `BlockTags` contains all the Vanilla block tags, `BiomeTags` contains all the Vanilla biome tags, and so on.

### Forge Tags
Forge bundles additional tags useful for mods, both Forge-specific and de-facto common tags that apply across all major mod loaders. You can find all of them in the `net.minecraftforge.common.Tags` class. The method names for each of the fields as well as code comment groups should make it clear which is a Forge-specific tag and which is a common tag.

!!! warning
    The common `c` namespaced tags seen in Forge are common across all loaders, however other loaders may have additional loader-specific tags under the same `c` namespace. When making a multi-loader mod, it is recommended to check the tags for each loader to ensure compatibility if you are considering a `c` tag you saw on other loaders that is missing in Forge. Loader-specific `c` tags may be in Forge under the `forge` namespace until they become common across all loaders.

### Full list of tags in Forge
You can find a full list of tags Forge adds on top of Vanilla Minecraft [here][forgebundledtagslist].

Declaring Your Own Groupings
----------------------------
Tags are declared in your mod's [datapack][datapack]. For example, a `TagKey<Block>` with a given identifier of  `modid:foo/tagname` will reference a tag at `/data/<modid>/tags/blocks/foo/tagname.json`. Tags for `Block`s, `Item`s, `EntityType`s, `Fluid`s, and `GameEvent`s use the plural forms for their folder location while all other registries use the singular version (`EntityType` uses the folder `entity_types` while `Potion` would use the folder `potion`).
Similarly, you may append to or override tags declared in other domains, such as Vanilla, by declaring your own JSONs.
For example, to add your own mod's saplings to the Vanilla sapling tag, you would specify it in `/data/minecraft/tags/blocks/saplings.json`, and Vanilla will merge everything into one tag at reload, if the `replace` option is false.
If `replace` is true, then all entries before the json specifying `replace` will be removed.
Values listed that are not present will cause the tag to error unless the value is listed using an `id` string and `required` boolean set to false, as in the following example:

```js
{
  "replace": false,
  "values": [
    "minecraft:gold_ingot",
    "mymod:my_ingot",
    {
      "id": "othermod:ingot_other",
      "required": false
    }
  ]
}
```

See the [Vanilla wiki][tags] for a description of the base syntax.

There is also a Forge extension on the Vanilla syntax.
You may declare a `remove` array of the same format as the `values` array. Any values listed here will be removed from the tag. This acts as a finer grained version of the Vanilla `replace` option.


Using Tags In Code
------------------
Tags for all registries are automatically sent from the server to any remote clients on login and reload. `Block`s, `Item`s, `EntityType`s, `Fluid`s, and `GameEvent`s are special cased as they have `Holder`s allowing for available tags to be accessible through the object itself.

!!! note
    Intrusive `Holder`s may be removed in a future version of Minecraft. If they are, the below methods can be used instead to query the associated `Holder`s.

### ITagManager

Forge wrapped registries provide an additional helper for creating and managing tags through `ITagManager` which can be obtained via `IForgeRegistry#tags`. Tags can be created using using `#createTagKey` or `#createOptionalTagKey`. Tags or registry objects can also be checked for either or using `#getTag` or `#getReverseTag` respectively.

#### Custom Registries

Custom registries can create tags when constructing their `DeferredRegister` via `#createTagKey` or `#createOptionalTagKey` respectively. Their tags or registry objects can then checked for either using the `IForgeRegistry` obtained by calling `DeferredRegister#makeRegistry`.

### Referencing Tags

There are four methods of creating a tag wrapper:

Method                          | For
:---:                           | :---
`*Tags#create`                  | `BannerPattern`, `Biome`, `Block`, `CatVariant`, `DamageType`, `EntityType`, `FlatLevelGeneratorPreset`, `Fluid`, `GameEvent`, `Instrument`, `Item`, `PaintingVariant`, `PoiType`, `Structure`, and `WorldPreset` where `*` represents one of these types.
`ITagManager#createTagKey`      | Forge wrapped vanilla registries, registries can be obtained from `ForgeRegistries`.
`DeferredRegister#createTagKey` | Custom forge registries.
`TagKey#create`                 | Vanilla registries without forge wrappers, registries can be obtained from `Registry`.

Registry objects can check their tags or registry objects either through their `Holder` or through `ITag`/`IReverseTag` for vanilla or forge registry objects respectively.

Vanilla registry objects can grab their associated holder using either `Registry#getHolder` or `Registry#getHolderOrThrow` and then compare if the registry object has a tag using `Holder#is`.

Forge registry objects can grab their tag definition using either `ITagManager#getTag` or `ITagManager#getReverseTag` and then compare if a registry object has a tag using `ITag#contains` or `IReverseTag#containsTag` respectively.

Tag-holding registry objects contain a method called `#is` in either their registry object or state-aware class to check whether the object belongs to a certain tag.

As an example:
```java
public static final TagKey<Item> myItemTag = ItemTags.create(ResourceLocation.fromNamespaceAndPath("mymod", "myitemgroup"));

public static final TagKey<Potion> myPotionTag = ForgeRegistries.POTIONS.tags().createTagKey(ResourceLocation.fromNamespaceAndPath("mymod", "mypotiongroup"));

public static final TagKey<VillagerType> myVillagerTypeTag = TagKey.create(Registries.VILLAGER_TYPE, ResourceLocation.fromNamespaceAndPath("mymod", "myvillagertypegroup"));

// In some method:

ItemStack stack = /*...*/;
boolean isInItemGroup = stack.is(myItemTag);

Potion potion = /*...*/;
boolean isInPotionGroup  = ForgeRegistries.POTIONS.tags().getTag(myPotionTag).contains(potion);

ResourceKey<VillagerType> villagerTypeKey = /*...*/;
boolean isInVillagerTypeGroup = BuiltInRegistries.VILLAGER_TYPE.getHolder(villagerTypeKey).map(holder -> holder.is(myVillagerTypeTag)).orElse(false);
```

Conventions
-----------

There are several conventions that will help facilitate compatibility in the ecosystem:

* If there is a Vanilla tag that fits your block or item, add it to that tag. See the [list of Vanilla tags][taglist].
* If there is a Forge tag that fits your block or item, add it to that tag. The list of tags declared by Forge can be seen on [GitHub][forgetags].
* If there is a group of something you feel should be shared by the community, use the `forge` namespace instead of your mod id.
* Tag naming conventions should follow Vanilla conventions. In particular, item and block groupings are plural instead of singular (e.g. `minecraft:logs`, `minecraft:saplings`).
* Item tags should be sorted into subdirectories according to their type (e.g. `forge:ingots/iron`, `forge:nuggets/brass`, etc.).


Migration from OreDictionary
----------------------------

* For recipes, tags can be used directly in the vanilla recipe format (see below).
* For matching items in code, see the section above.
* If you are declaring a new type of item grouping, follow a couple naming conventions:
  * Use `domain:type/material`. When the name is a common one that all modders should adopt, use the `forge` domain.
  * For example, brass ingots should be registered under the `forge:ingots/brass` tag and cobalt nuggets under the `forge:nuggets/cobalt` tag.


Using Tags in Recipes and Advancements
--------------------------------------

Tags are directly supported by Vanilla. See the respective Vanilla wiki pages for [recipes] and [advancements] for usage details.

[datapack]: ./index.md
[tags]: https://minecraft.wiki/w/Tag#JSON_format
[taglist]: https://minecraft.wiki/w/Tag#List_of_tags
[forgetags]: https://github.com/MinecraftForge/MinecraftForge/tree/1.19.x/src/generated/resources/data/forge/tags
[recipes]: https://minecraft.wiki/w/Recipe#JSON_format
[advancements]: https://minecraft.wiki/w/Advancement
[forgebundledtagslist]: ./tagslist.md

---

Tags list
=========
Forge bundles many tags useful for mods, both Forge-specific and de-facto common tags that apply across all major mod loaders. You can find all of them in the `net.minecraftforge.common.Tags` class. This page lists all those tags and their contents.

!!! note
    This page does not include Vanilla tags. Refer to the `net.minecraft.tags` package for those.

This page is generated from the [CommonTagsDumper][commontagsdumper] and is correct as of Forge 52.0.20. Note that not all builds of Forge contain tag changes, so just because this page references an older build does not mean this page is outdated. However, you should treat the actual generated JSONs on the Forge GitHub repository found [here][tagsrepo] as the ground truth. This page is provided for convenience and is not guaranteed to be up-to-date.

block
-----
- `c:barrels`
    - `minecraft:barrel`
- `c:barrels/wooden`
    - `minecraft:barrel`
- `c:bookshelves`
    - `minecraft:bookshelf`
- `c:budding_blocks`
    - `minecraft:budding_amethyst`
- `c:buds`
    - `minecraft:large_amethyst_bud`
    - `minecraft:medium_amethyst_bud`
    - `minecraft:small_amethyst_bud`
- `c:chains`
    - `minecraft:chain`
- `c:chests`
    - `minecraft:chest`
    - `minecraft:ender_chest`
    - `minecraft:trapped_chest`
- `c:chests/wooden`
    - `minecraft:chest`
    - `minecraft:trapped_chest`
- `c:clusters`
    - `minecraft:amethyst_cluster`
- `c:cobblestones`
    - `minecraft:cobbled_deepslate`
    - `minecraft:cobblestone`
    - `minecraft:infested_cobblestone`
    - `minecraft:mossy_cobblestone`
- `c:concretes`
    - `minecraft:black_concrete`
    - `minecraft:blue_concrete`
    - `minecraft:brown_concrete`
    - `minecraft:cyan_concrete`
    - `minecraft:gray_concrete`
    - `minecraft:green_concrete`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_gray_concrete`
    - `minecraft:lime_concrete`
    - `minecraft:magenta_concrete`
    - `minecraft:orange_concrete`
    - `minecraft:pink_concrete`
    - `minecraft:purple_concrete`
    - `minecraft:red_concrete`
    - `minecraft:white_concrete`
    - `minecraft:yellow_concrete`
- `c:dyed`
    - `minecraft:black_banner`
    - `minecraft:black_bed`
    - `minecraft:black_candle`
    - `minecraft:black_carpet`
    - `minecraft:black_concrete`
    - `minecraft:black_concrete_powder`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:black_shulker_box`
    - `minecraft:black_stained_glass`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:black_terracotta`
    - `minecraft:black_wall_banner`
    - `minecraft:black_wool`
    - `minecraft:blue_banner`
    - `minecraft:blue_bed`
    - `minecraft:blue_candle`
    - `minecraft:blue_carpet`
    - `minecraft:blue_concrete`
    - `minecraft:blue_concrete_powder`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:blue_shulker_box`
    - `minecraft:blue_stained_glass`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:blue_terracotta`
    - `minecraft:blue_wall_banner`
    - `minecraft:blue_wool`
    - `minecraft:brown_banner`
    - `minecraft:brown_bed`
    - `minecraft:brown_candle`
    - `minecraft:brown_carpet`
    - `minecraft:brown_concrete`
    - `minecraft:brown_concrete_powder`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:brown_shulker_box`
    - `minecraft:brown_stained_glass`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:brown_terracotta`
    - `minecraft:brown_wall_banner`
    - `minecraft:brown_wool`
    - `minecraft:cyan_banner`
    - `minecraft:cyan_bed`
    - `minecraft:cyan_candle`
    - `minecraft:cyan_carpet`
    - `minecraft:cyan_concrete`
    - `minecraft:cyan_concrete_powder`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:cyan_shulker_box`
    - `minecraft:cyan_stained_glass`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:cyan_terracotta`
    - `minecraft:cyan_wall_banner`
    - `minecraft:cyan_wool`
    - `minecraft:gray_banner`
    - `minecraft:gray_bed`
    - `minecraft:gray_candle`
    - `minecraft:gray_carpet`
    - `minecraft:gray_concrete`
    - `minecraft:gray_concrete_powder`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:gray_shulker_box`
    - `minecraft:gray_stained_glass`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:gray_terracotta`
    - `minecraft:gray_wall_banner`
    - `minecraft:gray_wool`
    - `minecraft:green_banner`
    - `minecraft:green_bed`
    - `minecraft:green_candle`
    - `minecraft:green_carpet`
    - `minecraft:green_concrete`
    - `minecraft:green_concrete_powder`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:green_shulker_box`
    - `minecraft:green_stained_glass`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:green_terracotta`
    - `minecraft:green_wall_banner`
    - `minecraft:green_wool`
    - `minecraft:light_blue_banner`
    - `minecraft:light_blue_bed`
    - `minecraft:light_blue_candle`
    - `minecraft:light_blue_carpet`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_blue_concrete_powder`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_blue_shulker_box`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_blue_terracotta`
    - `minecraft:light_blue_wall_banner`
    - `minecraft:light_blue_wool`
    - `minecraft:light_gray_banner`
    - `minecraft:light_gray_bed`
    - `minecraft:light_gray_candle`
    - `minecraft:light_gray_carpet`
    - `minecraft:light_gray_concrete`
    - `minecraft:light_gray_concrete_powder`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:light_gray_shulker_box`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:light_gray_terracotta`
    - `minecraft:light_gray_wall_banner`
    - `minecraft:light_gray_wool`
    - `minecraft:lime_banner`
    - `minecraft:lime_bed`
    - `minecraft:lime_candle`
    - `minecraft:lime_carpet`
    - `minecraft:lime_concrete`
    - `minecraft:lime_concrete_powder`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:lime_shulker_box`
    - `minecraft:lime_stained_glass`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:lime_terracotta`
    - `minecraft:lime_wall_banner`
    - `minecraft:lime_wool`
    - `minecraft:magenta_banner`
    - `minecraft:magenta_bed`
    - `minecraft:magenta_candle`
    - `minecraft:magenta_carpet`
    - `minecraft:magenta_concrete`
    - `minecraft:magenta_concrete_powder`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:magenta_shulker_box`
    - `minecraft:magenta_stained_glass`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:magenta_terracotta`
    - `minecraft:magenta_wall_banner`
    - `minecraft:magenta_wool`
    - `minecraft:orange_banner`
    - `minecraft:orange_bed`
    - `minecraft:orange_candle`
    - `minecraft:orange_carpet`
    - `minecraft:orange_concrete`
    - `minecraft:orange_concrete_powder`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:orange_shulker_box`
    - `minecraft:orange_stained_glass`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:orange_terracotta`
    - `minecraft:orange_wall_banner`
    - `minecraft:orange_wool`
    - `minecraft:pink_banner`
    - `minecraft:pink_bed`
    - `minecraft:pink_candle`
    - `minecraft:pink_carpet`
    - `minecraft:pink_concrete`
    - `minecraft:pink_concrete_powder`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:pink_shulker_box`
    - `minecraft:pink_stained_glass`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:pink_terracotta`
    - `minecraft:pink_wall_banner`
    - `minecraft:pink_wool`
    - `minecraft:purple_banner`
    - `minecraft:purple_bed`
    - `minecraft:purple_candle`
    - `minecraft:purple_carpet`
    - `minecraft:purple_concrete`
    - `minecraft:purple_concrete_powder`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:purple_shulker_box`
    - `minecraft:purple_stained_glass`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:purple_terracotta`
    - `minecraft:purple_wall_banner`
    - `minecraft:purple_wool`
    - `minecraft:red_banner`
    - `minecraft:red_bed`
    - `minecraft:red_candle`
    - `minecraft:red_carpet`
    - `minecraft:red_concrete`
    - `minecraft:red_concrete_powder`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:red_shulker_box`
    - `minecraft:red_stained_glass`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:red_terracotta`
    - `minecraft:red_wall_banner`
    - `minecraft:red_wool`
    - `minecraft:white_banner`
    - `minecraft:white_bed`
    - `minecraft:white_candle`
    - `minecraft:white_carpet`
    - `minecraft:white_concrete`
    - `minecraft:white_concrete_powder`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:white_shulker_box`
    - `minecraft:white_stained_glass`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:white_terracotta`
    - `minecraft:white_wall_banner`
    - `minecraft:white_wool`
    - `minecraft:yellow_banner`
    - `minecraft:yellow_bed`
    - `minecraft:yellow_candle`
    - `minecraft:yellow_carpet`
    - `minecraft:yellow_concrete`
    - `minecraft:yellow_concrete_powder`
    - `minecraft:yellow_glazed_terracotta`
    - `minecraft:yellow_shulker_box`
    - `minecraft:yellow_stained_glass`
    - `minecraft:yellow_stained_glass_pane`
    - `minecraft:yellow_terracotta`
    - `minecraft:yellow_wall_banner`
    - `minecraft:yellow_wool`
- `c:dyed/black`
    - `minecraft:black_banner`
    - `minecraft:black_bed`
    - `minecraft:black_candle`
    - `minecraft:black_carpet`
    - `minecraft:black_concrete`
    - `minecraft:black_concrete_powder`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:black_shulker_box`
    - `minecraft:black_stained_glass`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:black_terracotta`
    - `minecraft:black_wall_banner`
    - `minecraft:black_wool`
- `c:dyed/blue`
    - `minecraft:blue_banner`
    - `minecraft:blue_bed`
    - `minecraft:blue_candle`
    - `minecraft:blue_carpet`
    - `minecraft:blue_concrete`
    - `minecraft:blue_concrete_powder`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:blue_shulker_box`
    - `minecraft:blue_stained_glass`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:blue_terracotta`
    - `minecraft:blue_wall_banner`
    - `minecraft:blue_wool`
- `c:dyed/brown`
    - `minecraft:brown_banner`
    - `minecraft:brown_bed`
    - `minecraft:brown_candle`
    - `minecraft:brown_carpet`
    - `minecraft:brown_concrete`
    - `minecraft:brown_concrete_powder`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:brown_shulker_box`
    - `minecraft:brown_stained_glass`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:brown_terracotta`
    - `minecraft:brown_wall_banner`
    - `minecraft:brown_wool`
- `c:dyed/cyan`
    - `minecraft:cyan_banner`
    - `minecraft:cyan_bed`
    - `minecraft:cyan_candle`
    - `minecraft:cyan_carpet`
    - `minecraft:cyan_concrete`
    - `minecraft:cyan_concrete_powder`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:cyan_shulker_box`
    - `minecraft:cyan_stained_glass`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:cyan_terracotta`
    - `minecraft:cyan_wall_banner`
    - `minecraft:cyan_wool`
- `c:dyed/gray`
    - `minecraft:gray_banner`
    - `minecraft:gray_bed`
    - `minecraft:gray_candle`
    - `minecraft:gray_carpet`
    - `minecraft:gray_concrete`
    - `minecraft:gray_concrete_powder`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:gray_shulker_box`
    - `minecraft:gray_stained_glass`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:gray_terracotta`
    - `minecraft:gray_wall_banner`
    - `minecraft:gray_wool`
- `c:dyed/green`
    - `minecraft:green_banner`
    - `minecraft:green_bed`
    - `minecraft:green_candle`
    - `minecraft:green_carpet`
    - `minecraft:green_concrete`
    - `minecraft:green_concrete_powder`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:green_shulker_box`
    - `minecraft:green_stained_glass`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:green_terracotta`
    - `minecraft:green_wall_banner`
    - `minecraft:green_wool`
- `c:dyed/light_blue`
    - `minecraft:light_blue_banner`
    - `minecraft:light_blue_bed`
    - `minecraft:light_blue_candle`
    - `minecraft:light_blue_carpet`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_blue_concrete_powder`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_blue_shulker_box`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_blue_terracotta`
    - `minecraft:light_blue_wall_banner`
    - `minecraft:light_blue_wool`
- `c:dyed/light_gray`
    - `minecraft:light_gray_banner`
    - `minecraft:light_gray_bed`
    - `minecraft:light_gray_candle`
    - `minecraft:light_gray_carpet`
    - `minecraft:light_gray_concrete`
    - `minecraft:light_gray_concrete_powder`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:light_gray_shulker_box`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:light_gray_terracotta`
    - `minecraft:light_gray_wall_banner`
    - `minecraft:light_gray_wool`
- `c:dyed/lime`
    - `minecraft:lime_banner`
    - `minecraft:lime_bed`
    - `minecraft:lime_candle`
    - `minecraft:lime_carpet`
    - `minecraft:lime_concrete`
    - `minecraft:lime_concrete_powder`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:lime_shulker_box`
    - `minecraft:lime_stained_glass`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:lime_terracotta`
    - `minecraft:lime_wall_banner`
    - `minecraft:lime_wool`
- `c:dyed/magenta`
    - `minecraft:magenta_banner`
    - `minecraft:magenta_bed`
    - `minecraft:magenta_candle`
    - `minecraft:magenta_carpet`
    - `minecraft:magenta_concrete`
    - `minecraft:magenta_concrete_powder`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:magenta_shulker_box`
    - `minecraft:magenta_stained_glass`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:magenta_terracotta`
    - `minecraft:magenta_wall_banner`
    - `minecraft:magenta_wool`
- `c:dyed/orange`
    - `minecraft:orange_banner`
    - `minecraft:orange_bed`
    - `minecraft:orange_candle`
    - `minecraft:orange_carpet`
    - `minecraft:orange_concrete`
    - `minecraft:orange_concrete_powder`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:orange_shulker_box`
    - `minecraft:orange_stained_glass`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:orange_terracotta`
    - `minecraft:orange_wall_banner`
    - `minecraft:orange_wool`
- `c:dyed/pink`
    - `minecraft:pink_banner`
    - `minecraft:pink_bed`
    - `minecraft:pink_candle`
    - `minecraft:pink_carpet`
    - `minecraft:pink_concrete`
    - `minecraft:pink_concrete_powder`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:pink_shulker_box`
    - `minecraft:pink_stained_glass`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:pink_terracotta`
    - `minecraft:pink_wall_banner`
    - `minecraft:pink_wool`
- `c:dyed/purple`
    - `minecraft:purple_banner`
    - `minecraft:purple_bed`
    - `minecraft:purple_candle`
    - `minecraft:purple_carpet`
    - `minecraft:purple_concrete`
    - `minecraft:purple_concrete_powder`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:purple_shulker_box`
    - `minecraft:purple_stained_glass`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:purple_terracotta`
    - `minecraft:purple_wall_banner`
    - `minecraft:purple_wool`
- `c:dyed/red`
    - `minecraft:red_banner`
    - `minecraft:red_bed`
    - `minecraft:red_candle`
    - `minecraft:red_carpet`
    - `minecraft:red_concrete`
    - `minecraft:red_concrete_powder`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:red_shulker_box`
    - `minecraft:red_stained_glass`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:red_terracotta`
    - `minecraft:red_wall_banner`
    - `minecraft:red_wool`
- `c:dyed/white`
    - `minecraft:white_banner`
    - `minecraft:white_bed`
    - `minecraft:white_candle`
    - `minecraft:white_carpet`
    - `minecraft:white_concrete`
    - `minecraft:white_concrete_powder`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:white_shulker_box`
    - `minecraft:white_stained_glass`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:white_terracotta`
    - `minecraft:white_wall_banner`
    - `minecraft:white_wool`
- `c:dyed/yellow`
    - `minecraft:yellow_banner`
    - `minecraft:yellow_bed`
    - `minecraft:yellow_candle`
    - `minecraft:yellow_carpet`
    - `minecraft:yellow_concrete`
    - `minecraft:yellow_concrete_powder`
    - `minecraft:yellow_glazed_terracotta`
    - `minecraft:yellow_shulker_box`
    - `minecraft:yellow_stained_glass`
    - `minecraft:yellow_stained_glass_pane`
    - `minecraft:yellow_terracotta`
    - `minecraft:yellow_wall_banner`
    - `minecraft:yellow_wool`
- `c:glass_blocks`
    - `minecraft:black_stained_glass`
    - `minecraft:blue_stained_glass`
    - `minecraft:brown_stained_glass`
    - `minecraft:cyan_stained_glass`
    - `minecraft:glass`
    - `minecraft:gray_stained_glass`
    - `minecraft:green_stained_glass`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:lime_stained_glass`
    - `minecraft:magenta_stained_glass`
    - `minecraft:orange_stained_glass`
    - `minecraft:pink_stained_glass`
    - `minecraft:purple_stained_glass`
    - `minecraft:red_stained_glass`
    - `minecraft:tinted_glass`
    - `minecraft:white_stained_glass`
    - `minecraft:yellow_stained_glass`
- `c:glass_blocks/cheap`
    - `minecraft:black_stained_glass`
    - `minecraft:blue_stained_glass`
    - `minecraft:brown_stained_glass`
    - `minecraft:cyan_stained_glass`
    - `minecraft:glass`
    - `minecraft:gray_stained_glass`
    - `minecraft:green_stained_glass`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:lime_stained_glass`
    - `minecraft:magenta_stained_glass`
    - `minecraft:orange_stained_glass`
    - `minecraft:pink_stained_glass`
    - `minecraft:purple_stained_glass`
    - `minecraft:red_stained_glass`
    - `minecraft:white_stained_glass`
    - `minecraft:yellow_stained_glass`
- `c:glass_blocks/colorless`
    - `minecraft:glass`
- `c:glass_blocks/tinted`
    - `minecraft:tinted_glass`
- `c:glass_panes`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:glass_pane`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:yellow_stained_glass_pane`
- `c:glass_panes/colorless`
    - `minecraft:glass_pane`
- `c:glazed_terracottas`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:yellow_glazed_terracotta`
- `c:hidden_from_recipe_viewers`
- `c:obsidians`
    - `minecraft:crying_obsidian`
    - `minecraft:obsidian`
- `c:obsidians/crying`
    - `minecraft:crying_obsidian`
- `c:obsidians/normal`
    - `minecraft:obsidian`
- `c:ores`
    - `minecraft:ancient_debris`
    - `minecraft:coal_ore`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:lapis_ore`
    - `minecraft:nether_gold_ore`
    - `minecraft:nether_quartz_ore`
    - `minecraft:redstone_ore`
- `c:ores/netherite_scrap`
    - `minecraft:ancient_debris`
- `c:ores/quartz`
    - `minecraft:nether_quartz_ore`
- `c:player_workstations/crafting_tables`
    - `minecraft:crafting_table`
- `c:player_workstations/furnaces`
    - `minecraft:furnace`
- `c:relocation_not_supported`
- `c:ropes`
- `c:sandstone/blocks`
    - `minecraft:chiseled_red_sandstone`
    - `minecraft:chiseled_sandstone`
    - `minecraft:cut_red_sandstone`
    - `minecraft:cut_sandstone`
    - `minecraft:red_sandstone`
    - `minecraft:sandstone`
    - `minecraft:smooth_red_sandstone`
    - `minecraft:smooth_sandstone`
- `c:sandstone/red_blocks`
    - `minecraft:chiseled_red_sandstone`
    - `minecraft:cut_red_sandstone`
    - `minecraft:red_sandstone`
    - `minecraft:smooth_red_sandstone`
- `c:sandstone/red_slabs`
    - `minecraft:cut_red_sandstone_slab`
    - `minecraft:red_sandstone_slab`
    - `minecraft:smooth_red_sandstone_slab`
- `c:sandstone/red_stairs`
    - `minecraft:red_sandstone_stairs`
    - `minecraft:smooth_red_sandstone_stairs`
- `c:sandstone/slabs`
    - `minecraft:cut_red_sandstone_slab`
    - `minecraft:cut_sandstone_slab`
    - `minecraft:red_sandstone_slab`
    - `minecraft:sandstone_slab`
    - `minecraft:smooth_red_sandstone_slab`
    - `minecraft:smooth_sandstone_slab`
- `c:sandstone/stairs`
    - `minecraft:red_sandstone_stairs`
    - `minecraft:sandstone_stairs`
    - `minecraft:smooth_red_sandstone_stairs`
    - `minecraft:smooth_sandstone_stairs`
- `c:sandstone/uncolored_blocks`
    - `minecraft:chiseled_sandstone`
    - `minecraft:cut_sandstone`
    - `minecraft:sandstone`
    - `minecraft:smooth_sandstone`
- `c:sandstone/uncolored_slabs`
    - `minecraft:cut_sandstone_slab`
    - `minecraft:sandstone_slab`
    - `minecraft:smooth_sandstone_slab`
- `c:sandstone/uncolored_stairs`
    - `minecraft:sandstone_stairs`
    - `minecraft:smooth_sandstone_stairs`
- `c:skulls`
    - `minecraft:creeper_head`
    - `minecraft:creeper_wall_head`
    - `minecraft:dragon_head`
    - `minecraft:dragon_wall_head`
    - `minecraft:piglin_head`
    - `minecraft:piglin_wall_head`
    - `minecraft:player_head`
    - `minecraft:player_wall_head`
    - `minecraft:skeleton_skull`
    - `minecraft:skeleton_wall_skull`
    - `minecraft:wither_skeleton_skull`
    - `minecraft:wither_skeleton_wall_skull`
    - `minecraft:zombie_head`
    - `minecraft:zombie_wall_head`
- `c:stones`
    - `minecraft:andesite`
    - `minecraft:deepslate`
    - `minecraft:diorite`
    - `minecraft:granite`
    - `minecraft:stone`
    - `minecraft:tuff`
- `c:storage_blocks`
    - `minecraft:bone_block`
    - `minecraft:coal_block`
    - `minecraft:copper_block`
    - `minecraft:diamond_block`
    - `minecraft:dried_kelp_block`
    - `minecraft:emerald_block`
    - `minecraft:gold_block`
    - `minecraft:hay_block`
    - `minecraft:iron_block`
    - `minecraft:lapis_block`
    - `minecraft:netherite_block`
    - `minecraft:raw_copper_block`
    - `minecraft:raw_gold_block`
    - `minecraft:raw_iron_block`
    - `minecraft:redstone_block`
    - `minecraft:slime_block`
- `c:storage_blocks/bone_meal`
    - `minecraft:bone_block`
- `c:storage_blocks/coal`
    - `minecraft:coal_block`
- `c:storage_blocks/copper`
    - `minecraft:copper_block`
- `c:storage_blocks/diamond`
    - `minecraft:diamond_block`
- `c:storage_blocks/dried_kelp`
    - `minecraft:dried_kelp_block`
- `c:storage_blocks/emerald`
    - `minecraft:emerald_block`
- `c:storage_blocks/gold`
    - `minecraft:gold_block`
- `c:storage_blocks/iron`
    - `minecraft:iron_block`
- `c:storage_blocks/lapis`
    - `minecraft:lapis_block`
- `c:storage_blocks/netherite`
    - `minecraft:netherite_block`
- `c:storage_blocks/raw_copper`
    - `minecraft:raw_copper_block`
- `c:storage_blocks/raw_gold`
    - `minecraft:raw_gold_block`
- `c:storage_blocks/raw_iron`
    - `minecraft:raw_iron_block`
- `c:storage_blocks/redstone`
    - `minecraft:redstone_block`
- `c:storage_blocks/slime`
    - `minecraft:slime_block`
- `c:storage_blocks/wheat`
    - `minecraft:hay_block`
- `c:villager_job_sites`
    - `minecraft:barrel`
    - `minecraft:blast_furnace`
    - `minecraft:brewing_stand`
    - `minecraft:cartography_table`
    - `minecraft:cauldron`
    - `minecraft:composter`
    - `minecraft:fletching_table`
    - `minecraft:grindstone`
    - `minecraft:lava_cauldron`
    - `minecraft:lectern`
    - `minecraft:loom`
    - `minecraft:powder_snow_cauldron`
    - `minecraft:smithing_table`
    - `minecraft:smoker`
    - `minecraft:stonecutter`
    - `minecraft:water_cauldron`
- `forge:chests/ender`
    - `minecraft:ender_chest`
- `forge:chests/trapped`
    - `minecraft:trapped_chest`
- `forge:cobblestone/deepslate`
    - `minecraft:cobbled_deepslate`
- `forge:cobblestone/infested`
    - `minecraft:infested_cobblestone`
- `forge:cobblestone/mossy`
    - `minecraft:mossy_cobblestone`
- `forge:cobblestone/normal`
    - `minecraft:cobblestone`
- `forge:end_stones`
    - `minecraft:end_stone`
- `forge:enderman_place_on_blacklist`
- `forge:fence_gates`
    - `minecraft:acacia_fence_gate`
    - `minecraft:bamboo_fence_gate`
    - `minecraft:birch_fence_gate`
    - `minecraft:cherry_fence_gate`
    - `minecraft:crimson_fence_gate`
    - `minecraft:dark_oak_fence_gate`
    - `minecraft:jungle_fence_gate`
    - `minecraft:mangrove_fence_gate`
    - `minecraft:oak_fence_gate`
    - `minecraft:spruce_fence_gate`
    - `minecraft:warped_fence_gate`
- `forge:fence_gates/wooden`
    - `minecraft:acacia_fence_gate`
    - `minecraft:bamboo_fence_gate`
    - `minecraft:birch_fence_gate`
    - `minecraft:cherry_fence_gate`
    - `minecraft:crimson_fence_gate`
    - `minecraft:dark_oak_fence_gate`
    - `minecraft:jungle_fence_gate`
    - `minecraft:mangrove_fence_gate`
    - `minecraft:oak_fence_gate`
    - `minecraft:spruce_fence_gate`
    - `minecraft:warped_fence_gate`
- `forge:fences`
    - `minecraft:acacia_fence`
    - `minecraft:bamboo_fence`
    - `minecraft:birch_fence`
    - `minecraft:cherry_fence`
    - `minecraft:crimson_fence`
    - `minecraft:dark_oak_fence`
    - `minecraft:jungle_fence`
    - `minecraft:mangrove_fence`
    - `minecraft:nether_brick_fence`
    - `minecraft:oak_fence`
    - `minecraft:spruce_fence`
    - `minecraft:warped_fence`
- `forge:fences/nether_brick`
    - `minecraft:nether_brick_fence`
- `forge:fences/wooden`
    - `minecraft:acacia_fence`
    - `minecraft:bamboo_fence`
    - `minecraft:birch_fence`
    - `minecraft:cherry_fence`
    - `minecraft:crimson_fence`
    - `minecraft:dark_oak_fence`
    - `minecraft:jungle_fence`
    - `minecraft:mangrove_fence`
    - `minecraft:oak_fence`
    - `minecraft:spruce_fence`
    - `minecraft:warped_fence`
- `forge:gravel`
    - `minecraft:gravel`
- `forge:netherrack`
    - `minecraft:netherrack`
- `forge:ore_bearing_ground/deepslate`
    - `minecraft:deepslate`
- `forge:ore_bearing_ground/netherrack`
    - `minecraft:netherrack`
- `forge:ore_bearing_ground/stone`
    - `minecraft:stone`
- `forge:ore_rates/dense`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:lapis_ore`
    - `minecraft:redstone_ore`
- `forge:ore_rates/singular`
    - `minecraft:ancient_debris`
    - `minecraft:coal_ore`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:nether_quartz_ore`
- `forge:ore_rates/sparse`
    - `minecraft:nether_gold_ore`
- `forge:ores/coal`
    - `minecraft:coal_ore`
    - `minecraft:deepslate_coal_ore`
- `forge:ores/copper`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_copper_ore`
- `forge:ores/diamond`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:diamond_ore`
- `forge:ores/emerald`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:emerald_ore`
- `forge:ores/gold`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:gold_ore`
    - `minecraft:nether_gold_ore`
- `forge:ores/iron`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:iron_ore`
- `forge:ores/lapis`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:lapis_ore`
- `forge:ores/redstone`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:redstone_ore`
- `forge:ores_in_ground/deepslate`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
- `forge:ores_in_ground/netherrack`
    - `minecraft:nether_gold_ore`
    - `minecraft:nether_quartz_ore`
- `forge:ores_in_ground/stone`
    - `minecraft:coal_ore`
    - `minecraft:copper_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:lapis_ore`
    - `minecraft:redstone_ore`
- `forge:sand`
    - `minecraft:red_sand`
    - `minecraft:sand`
- `forge:sand/colorless`
    - `minecraft:sand`
- `forge:sand/red`
    - `minecraft:red_sand`

enchantment
-----------
- `c:entity_auxiliary_movement_enhancements`
    - `minecraft:feather_falling`
    - `minecraft:frost_walker`
- `c:entity_defense_enhancements`
    - `minecraft:blast_protection`
    - `minecraft:feather_falling`
    - `minecraft:fire_protection`
    - `minecraft:projectile_protection`
    - `minecraft:protection`
    - `minecraft:respiration`
- `c:entity_speed_enhancements`
    - `minecraft:depth_strider`
    - `minecraft:soul_speed`
    - `minecraft:swift_sneak`
- `c:increase_block_drops`
    - `minecraft:fortune`
- `c:increase_entity_drops`
    - `minecraft:looting`
- `c:weapon_damage_enhancements`
    - `minecraft:bane_of_arthropods`
    - `minecraft:impaling`
    - `minecraft:power`
    - `minecraft:sharpness`
    - `minecraft:smite`

entitytype
-----------
- `c:boats`
    - `minecraft:boat`
    - `minecraft:chest_boat`
- `c:bosses`
    - `minecraft:ender_dragon`
    - `minecraft:wither`
- `c:capturing_not_supported`
- `c:minecarts`
    - `minecraft:chest_minecart`
    - `minecraft:command_block_minecart`
    - `minecraft:furnace_minecart`
    - `minecraft:hopper_minecart`
    - `minecraft:minecart`
    - `minecraft:spawner_minecart`
    - `minecraft:tnt_minecart`
- `c:teleporting_not_supported`

fluid
-----
- `c:hidden_from_recipe_viewers`
- `c:honey`
- `c:lava`
    - `minecraft:flowing_lava`
    - `minecraft:lava`
- `c:milk`
- `c:water`
    - `minecraft:flowing_water`
    - `minecraft:water`
- `forge:beetroot_soup`
- `forge:gaseous`
- `forge:mushroom_stew`
- `forge:potion`
- `forge:rabbit_stew`
- `forge:suspicious_stew`

item
----
- `c:animal_foods`
    - `minecraft:allium`
    - `minecraft:apple`
    - `minecraft:azure_bluet`
    - `minecraft:bamboo`
    - `minecraft:beef`
    - `minecraft:beetroot`
    - `minecraft:beetroot_seeds`
    - `minecraft:blue_orchid`
    - `minecraft:cactus`
    - `minecraft:carrot`
    - `minecraft:cherry_leaves`
    - `minecraft:chicken`
    - `minecraft:chorus_flower`
    - `minecraft:cod`
    - `minecraft:cooked_beef`
    - `minecraft:cooked_chicken`
    - `minecraft:cooked_mutton`
    - `minecraft:cooked_porkchop`
    - `minecraft:cooked_rabbit`
    - `minecraft:cornflower`
    - `minecraft:crimson_fungus`
    - `minecraft:dandelion`
    - `minecraft:enchanted_golden_apple`
    - `minecraft:flowering_azalea`
    - `minecraft:flowering_azalea_leaves`
    - `minecraft:glow_berries`
    - `minecraft:golden_apple`
    - `minecraft:golden_carrot`
    - `minecraft:hay_block`
    - `minecraft:lilac`
    - `minecraft:lily_of_the_valley`
    - `minecraft:mangrove_propagule`
    - `minecraft:melon_seeds`
    - `minecraft:mutton`
    - `minecraft:orange_tulip`
    - `minecraft:oxeye_daisy`
    - `minecraft:peony`
    - `minecraft:pink_petals`
    - `minecraft:pink_tulip`
    - `minecraft:pitcher_plant`
    - `minecraft:pitcher_pod`
    - `minecraft:poppy`
    - `minecraft:porkchop`
    - `minecraft:potato`
    - `minecraft:pumpkin_seeds`
    - `minecraft:rabbit`
    - `minecraft:red_tulip`
    - `minecraft:rose_bush`
    - `minecraft:rotten_flesh`
    - `minecraft:salmon`
    - `minecraft:seagrass`
    - `minecraft:slime_ball`
    - `minecraft:spider_eye`
    - `minecraft:spore_blossom`
    - `minecraft:sugar`
    - `minecraft:sunflower`
    - `minecraft:sweet_berries`
    - `minecraft:torchflower`
    - `minecraft:torchflower_seeds`
    - `minecraft:tropical_fish_bucket`
    - `minecraft:warped_fungus`
    - `minecraft:wheat`
    - `minecraft:wheat_seeds`
    - `minecraft:white_tulip`
    - `minecraft:wither_rose`
- `c:armors`
    - `minecraft:chainmail_boots`
    - `minecraft:chainmail_chestplate`
    - `minecraft:chainmail_helmet`
    - `minecraft:chainmail_leggings`
    - `minecraft:diamond_boots`
    - `minecraft:diamond_chestplate`
    - `minecraft:diamond_helmet`
    - `minecraft:diamond_leggings`
    - `minecraft:golden_boots`
    - `minecraft:golden_chestplate`
    - `minecraft:golden_helmet`
    - `minecraft:golden_leggings`
    - `minecraft:iron_boots`
    - `minecraft:iron_chestplate`
    - `minecraft:iron_helmet`
    - `minecraft:iron_leggings`
    - `minecraft:leather_boots`
    - `minecraft:leather_chestplate`
    - `minecraft:leather_helmet`
    - `minecraft:leather_leggings`
    - `minecraft:netherite_boots`
    - `minecraft:netherite_chestplate`
    - `minecraft:netherite_helmet`
    - `minecraft:netherite_leggings`
    - `minecraft:turtle_helmet`
- `c:barrels`
    - `minecraft:barrel`
- `c:barrels/wooden`
    - `minecraft:barrel`
- `c:bookshelves`
    - `minecraft:bookshelf`
- `c:bricks`
    - `minecraft:brick`
    - `minecraft:nether_brick`
- `c:bricks/nether`
    - `minecraft:nether_brick`
- `c:bricks/normal`
    - `minecraft:brick`
- `c:buckets`
    - `minecraft:axolotl_bucket`
    - `minecraft:bucket`
    - `minecraft:cod_bucket`
    - `minecraft:lava_bucket`
    - `minecraft:milk_bucket`
    - `minecraft:powder_snow_bucket`
    - `minecraft:pufferfish_bucket`
    - `minecraft:salmon_bucket`
    - `minecraft:tadpole_bucket`
    - `minecraft:tropical_fish_bucket`
    - `minecraft:water_bucket`
- `c:buckets/empty`
    - `minecraft:bucket`
- `c:buckets/entity_water`
    - `minecraft:axolotl_bucket`
    - `minecraft:cod_bucket`
    - `minecraft:pufferfish_bucket`
    - `minecraft:salmon_bucket`
    - `minecraft:tadpole_bucket`
    - `minecraft:tropical_fish_bucket`
- `c:buckets/lava`
    - `minecraft:lava_bucket`
- `c:buckets/milk`
    - `minecraft:milk_bucket`
- `c:buckets/powder_snow`
    - `minecraft:powder_snow_bucket`
- `c:buckets/water`
    - `minecraft:water_bucket`
- `c:budding_blocks`
    - `minecraft:budding_amethyst`
- `c:buds`
    - `minecraft:large_amethyst_bud`
    - `minecraft:medium_amethyst_bud`
    - `minecraft:small_amethyst_bud`
- `c:chains`
    - `minecraft:chain`
- `c:chests`
    - `minecraft:chest`
    - `minecraft:ender_chest`
    - `minecraft:trapped_chest`
- `c:chests/wooden`
    - `minecraft:chest`
    - `minecraft:trapped_chest`
- `c:clusters`
    - `minecraft:amethyst_cluster`
- `c:cobblestones`
    - `minecraft:cobbled_deepslate`
    - `minecraft:cobblestone`
    - `minecraft:infested_cobblestone`
    - `minecraft:mossy_cobblestone`
- `c:concrete_powders`
    - `minecraft:black_concrete_powder`
    - `minecraft:blue_concrete_powder`
    - `minecraft:brown_concrete_powder`
    - `minecraft:cyan_concrete_powder`
    - `minecraft:gray_concrete_powder`
    - `minecraft:green_concrete_powder`
    - `minecraft:light_blue_concrete_powder`
    - `minecraft:light_gray_concrete_powder`
    - `minecraft:lime_concrete_powder`
    - `minecraft:magenta_concrete_powder`
    - `minecraft:orange_concrete_powder`
    - `minecraft:pink_concrete_powder`
    - `minecraft:purple_concrete_powder`
    - `minecraft:red_concrete_powder`
    - `minecraft:white_concrete_powder`
    - `minecraft:yellow_concrete_powder`
- `c:concretes`
    - `minecraft:black_concrete`
    - `minecraft:blue_concrete`
    - `minecraft:brown_concrete`
    - `minecraft:cyan_concrete`
    - `minecraft:gray_concrete`
    - `minecraft:green_concrete`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_gray_concrete`
    - `minecraft:lime_concrete`
    - `minecraft:magenta_concrete`
    - `minecraft:orange_concrete`
    - `minecraft:pink_concrete`
    - `minecraft:purple_concrete`
    - `minecraft:red_concrete`
    - `minecraft:white_concrete`
    - `minecraft:yellow_concrete`
- `c:crops`
    - `minecraft:beetroot`
    - `minecraft:cactus`
    - `minecraft:carrot`
    - `minecraft:cocoa_beans`
    - `minecraft:melon`
    - `minecraft:nether_wart`
    - `minecraft:potato`
    - `minecraft:pumpkin`
    - `minecraft:sugar_cane`
    - `minecraft:wheat`
- `c:crops/beetroot`
    - `minecraft:beetroot`
- `c:crops/cactus`
    - `minecraft:cactus`
- `c:crops/carrot`
    - `minecraft:carrot`
- `c:crops/cocoa_bean`
    - `minecraft:cocoa_beans`
- `c:crops/melon`
    - `minecraft:melon`
- `c:crops/nether_wart`
    - `minecraft:nether_wart`
- `c:crops/potato`
    - `minecraft:potato`
- `c:crops/pumpkin`
    - `minecraft:pumpkin`
- `c:crops/sugar_cane`
    - `minecraft:sugar_cane`
- `c:crops/wheat`
    - `minecraft:wheat`
- `c:dusts`
    - `minecraft:glowstone_dust`
    - `minecraft:redstone`
- `c:dusts/glowstone`
    - `minecraft:glowstone_dust`
- `c:dusts/redstone`
    - `minecraft:redstone`
- `c:dyed`
    - `minecraft:black_banner`
    - `minecraft:black_bed`
    - `minecraft:black_candle`
    - `minecraft:black_carpet`
    - `minecraft:black_concrete`
    - `minecraft:black_concrete_powder`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:black_shulker_box`
    - `minecraft:black_stained_glass`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:black_terracotta`
    - `minecraft:black_wool`
    - `minecraft:blue_banner`
    - `minecraft:blue_bed`
    - `minecraft:blue_candle`
    - `minecraft:blue_carpet`
    - `minecraft:blue_concrete`
    - `minecraft:blue_concrete_powder`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:blue_shulker_box`
    - `minecraft:blue_stained_glass`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:blue_terracotta`
    - `minecraft:blue_wool`
    - `minecraft:brown_banner`
    - `minecraft:brown_bed`
    - `minecraft:brown_candle`
    - `minecraft:brown_carpet`
    - `minecraft:brown_concrete`
    - `minecraft:brown_concrete_powder`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:brown_shulker_box`
    - `minecraft:brown_stained_glass`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:brown_terracotta`
    - `minecraft:brown_wool`
    - `minecraft:cyan_banner`
    - `minecraft:cyan_bed`
    - `minecraft:cyan_candle`
    - `minecraft:cyan_carpet`
    - `minecraft:cyan_concrete`
    - `minecraft:cyan_concrete_powder`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:cyan_shulker_box`
    - `minecraft:cyan_stained_glass`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:cyan_terracotta`
    - `minecraft:cyan_wool`
    - `minecraft:gray_banner`
    - `minecraft:gray_bed`
    - `minecraft:gray_candle`
    - `minecraft:gray_carpet`
    - `minecraft:gray_concrete`
    - `minecraft:gray_concrete_powder`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:gray_shulker_box`
    - `minecraft:gray_stained_glass`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:gray_terracotta`
    - `minecraft:gray_wool`
    - `minecraft:green_banner`
    - `minecraft:green_bed`
    - `minecraft:green_candle`
    - `minecraft:green_carpet`
    - `minecraft:green_concrete`
    - `minecraft:green_concrete_powder`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:green_shulker_box`
    - `minecraft:green_stained_glass`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:green_terracotta`
    - `minecraft:green_wool`
    - `minecraft:light_blue_banner`
    - `minecraft:light_blue_bed`
    - `minecraft:light_blue_candle`
    - `minecraft:light_blue_carpet`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_blue_concrete_powder`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_blue_shulker_box`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_blue_terracotta`
    - `minecraft:light_blue_wool`
    - `minecraft:light_gray_banner`
    - `minecraft:light_gray_bed`
    - `minecraft:light_gray_candle`
    - `minecraft:light_gray_carpet`
    - `minecraft:light_gray_concrete`
    - `minecraft:light_gray_concrete_powder`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:light_gray_shulker_box`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:light_gray_terracotta`
    - `minecraft:light_gray_wool`
    - `minecraft:lime_banner`
    - `minecraft:lime_bed`
    - `minecraft:lime_candle`
    - `minecraft:lime_carpet`
    - `minecraft:lime_concrete`
    - `minecraft:lime_concrete_powder`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:lime_shulker_box`
    - `minecraft:lime_stained_glass`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:lime_terracotta`
    - `minecraft:lime_wool`
    - `minecraft:magenta_banner`
    - `minecraft:magenta_bed`
    - `minecraft:magenta_candle`
    - `minecraft:magenta_carpet`
    - `minecraft:magenta_concrete`
    - `minecraft:magenta_concrete_powder`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:magenta_shulker_box`
    - `minecraft:magenta_stained_glass`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:magenta_terracotta`
    - `minecraft:magenta_wool`
    - `minecraft:orange_banner`
    - `minecraft:orange_bed`
    - `minecraft:orange_candle`
    - `minecraft:orange_carpet`
    - `minecraft:orange_concrete`
    - `minecraft:orange_concrete_powder`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:orange_shulker_box`
    - `minecraft:orange_stained_glass`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:orange_terracotta`
    - `minecraft:orange_wool`
    - `minecraft:pink_banner`
    - `minecraft:pink_bed`
    - `minecraft:pink_candle`
    - `minecraft:pink_carpet`
    - `minecraft:pink_concrete`
    - `minecraft:pink_concrete_powder`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:pink_shulker_box`
    - `minecraft:pink_stained_glass`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:pink_terracotta`
    - `minecraft:pink_wool`
    - `minecraft:purple_banner`
    - `minecraft:purple_bed`
    - `minecraft:purple_candle`
    - `minecraft:purple_carpet`
    - `minecraft:purple_concrete`
    - `minecraft:purple_concrete_powder`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:purple_shulker_box`
    - `minecraft:purple_stained_glass`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:purple_terracotta`
    - `minecraft:purple_wool`
    - `minecraft:red_banner`
    - `minecraft:red_bed`
    - `minecraft:red_candle`
    - `minecraft:red_carpet`
    - `minecraft:red_concrete`
    - `minecraft:red_concrete_powder`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:red_shulker_box`
    - `minecraft:red_stained_glass`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:red_terracotta`
    - `minecraft:red_wool`
    - `minecraft:white_banner`
    - `minecraft:white_bed`
    - `minecraft:white_candle`
    - `minecraft:white_carpet`
    - `minecraft:white_concrete`
    - `minecraft:white_concrete_powder`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:white_shulker_box`
    - `minecraft:white_stained_glass`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:white_terracotta`
    - `minecraft:white_wool`
    - `minecraft:yellow_banner`
    - `minecraft:yellow_bed`
    - `minecraft:yellow_candle`
    - `minecraft:yellow_carpet`
    - `minecraft:yellow_concrete`
    - `minecraft:yellow_concrete_powder`
    - `minecraft:yellow_glazed_terracotta`
    - `minecraft:yellow_shulker_box`
    - `minecraft:yellow_stained_glass`
    - `minecraft:yellow_stained_glass_pane`
    - `minecraft:yellow_terracotta`
    - `minecraft:yellow_wool`
- `c:dyed/black`
    - `minecraft:black_banner`
    - `minecraft:black_bed`
    - `minecraft:black_candle`
    - `minecraft:black_carpet`
    - `minecraft:black_concrete`
    - `minecraft:black_concrete_powder`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:black_shulker_box`
    - `minecraft:black_stained_glass`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:black_terracotta`
    - `minecraft:black_wool`
- `c:dyed/blue`
    - `minecraft:blue_banner`
    - `minecraft:blue_bed`
    - `minecraft:blue_candle`
    - `minecraft:blue_carpet`
    - `minecraft:blue_concrete`
    - `minecraft:blue_concrete_powder`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:blue_shulker_box`
    - `minecraft:blue_stained_glass`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:blue_terracotta`
    - `minecraft:blue_wool`
- `c:dyed/brown`
    - `minecraft:brown_banner`
    - `minecraft:brown_bed`
    - `minecraft:brown_candle`
    - `minecraft:brown_carpet`
    - `minecraft:brown_concrete`
    - `minecraft:brown_concrete_powder`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:brown_shulker_box`
    - `minecraft:brown_stained_glass`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:brown_terracotta`
    - `minecraft:brown_wool`
- `c:dyed/cyan`
    - `minecraft:cyan_banner`
    - `minecraft:cyan_bed`
    - `minecraft:cyan_candle`
    - `minecraft:cyan_carpet`
    - `minecraft:cyan_concrete`
    - `minecraft:cyan_concrete_powder`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:cyan_shulker_box`
    - `minecraft:cyan_stained_glass`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:cyan_terracotta`
    - `minecraft:cyan_wool`
- `c:dyed/gray`
    - `minecraft:gray_banner`
    - `minecraft:gray_bed`
    - `minecraft:gray_candle`
    - `minecraft:gray_carpet`
    - `minecraft:gray_concrete`
    - `minecraft:gray_concrete_powder`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:gray_shulker_box`
    - `minecraft:gray_stained_glass`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:gray_terracotta`
    - `minecraft:gray_wool`
- `c:dyed/green`
    - `minecraft:green_banner`
    - `minecraft:green_bed`
    - `minecraft:green_candle`
    - `minecraft:green_carpet`
    - `minecraft:green_concrete`
    - `minecraft:green_concrete_powder`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:green_shulker_box`
    - `minecraft:green_stained_glass`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:green_terracotta`
    - `minecraft:green_wool`
- `c:dyed/light_blue`
    - `minecraft:light_blue_banner`
    - `minecraft:light_blue_bed`
    - `minecraft:light_blue_candle`
    - `minecraft:light_blue_carpet`
    - `minecraft:light_blue_concrete`
    - `minecraft:light_blue_concrete_powder`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_blue_shulker_box`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_blue_terracotta`
    - `minecraft:light_blue_wool`
- `c:dyed/light_gray`
    - `minecraft:light_gray_banner`
    - `minecraft:light_gray_bed`
    - `minecraft:light_gray_candle`
    - `minecraft:light_gray_carpet`
    - `minecraft:light_gray_concrete`
    - `minecraft:light_gray_concrete_powder`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:light_gray_shulker_box`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:light_gray_terracotta`
    - `minecraft:light_gray_wool`
- `c:dyed/lime`
    - `minecraft:lime_banner`
    - `minecraft:lime_bed`
    - `minecraft:lime_candle`
    - `minecraft:lime_carpet`
    - `minecraft:lime_concrete`
    - `minecraft:lime_concrete_powder`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:lime_shulker_box`
    - `minecraft:lime_stained_glass`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:lime_terracotta`
    - `minecraft:lime_wool`
- `c:dyed/magenta`
    - `minecraft:magenta_banner`
    - `minecraft:magenta_bed`
    - `minecraft:magenta_candle`
    - `minecraft:magenta_carpet`
    - `minecraft:magenta_concrete`
    - `minecraft:magenta_concrete_powder`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:magenta_shulker_box`
    - `minecraft:magenta_stained_glass`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:magenta_terracotta`
    - `minecraft:magenta_wool`
- `c:dyed/orange`
    - `minecraft:orange_banner`
    - `minecraft:orange_bed`
    - `minecraft:orange_candle`
    - `minecraft:orange_carpet`
    - `minecraft:orange_concrete`
    - `minecraft:orange_concrete_powder`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:orange_shulker_box`
    - `minecraft:orange_stained_glass`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:orange_terracotta`
    - `minecraft:orange_wool`
- `c:dyed/pink`
    - `minecraft:pink_banner`
    - `minecraft:pink_bed`
    - `minecraft:pink_candle`
    - `minecraft:pink_carpet`
    - `minecraft:pink_concrete`
    - `minecraft:pink_concrete_powder`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:pink_shulker_box`
    - `minecraft:pink_stained_glass`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:pink_terracotta`
    - `minecraft:pink_wool`
- `c:dyed/purple`
    - `minecraft:purple_banner`
    - `minecraft:purple_bed`
    - `minecraft:purple_candle`
    - `minecraft:purple_carpet`
    - `minecraft:purple_concrete`
    - `minecraft:purple_concrete_powder`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:purple_shulker_box`
    - `minecraft:purple_stained_glass`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:purple_terracotta`
    - `minecraft:purple_wool`
- `c:dyed/red`
    - `minecraft:red_banner`
    - `minecraft:red_bed`
    - `minecraft:red_candle`
    - `minecraft:red_carpet`
    - `minecraft:red_concrete`
    - `minecraft:red_concrete_powder`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:red_shulker_box`
    - `minecraft:red_stained_glass`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:red_terracotta`
    - `minecraft:red_wool`
- `c:dyed/white`
    - `minecraft:white_banner`
    - `minecraft:white_bed`
    - `minecraft:white_candle`
    - `minecraft:white_carpet`
    - `minecraft:white_concrete`
    - `minecraft:white_concrete_powder`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:white_shulker_box`
    - `minecraft:white_stained_glass`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:white_terracotta`
    - `minecraft:white_wool`
- `c:dyed/yellow`
    - `minecraft:yellow_banner`
    - `minecraft:yellow_bed`
    - `minecraft:yellow_candle`
    - `minecraft:yellow_carpet`
    - `minecraft:yellow_concrete`
    - `minecraft:yellow_concrete_powder`
    - `minecraft:yellow_glazed_terracotta`
    - `minecraft:yellow_shulker_box`
    - `minecraft:yellow_stained_glass`
    - `minecraft:yellow_stained_glass_pane`
    - `minecraft:yellow_terracotta`
    - `minecraft:yellow_wool`
- `c:dyes`
    - `minecraft:black_dye`
    - `minecraft:blue_dye`
    - `minecraft:brown_dye`
    - `minecraft:cyan_dye`
    - `minecraft:gray_dye`
    - `minecraft:green_dye`
    - `minecraft:light_blue_dye`
    - `minecraft:light_gray_dye`
    - `minecraft:lime_dye`
    - `minecraft:magenta_dye`
    - `minecraft:orange_dye`
    - `minecraft:pink_dye`
    - `minecraft:purple_dye`
    - `minecraft:red_dye`
    - `minecraft:white_dye`
    - `minecraft:yellow_dye`
- `c:dyes/black`
    - `minecraft:black_dye`
- `c:dyes/blue`
    - `minecraft:blue_dye`
- `c:dyes/brown`
    - `minecraft:brown_dye`
- `c:dyes/cyan`
    - `minecraft:cyan_dye`
- `c:dyes/gray`
    - `minecraft:gray_dye`
- `c:dyes/green`
    - `minecraft:green_dye`
- `c:dyes/light_blue`
    - `minecraft:light_blue_dye`
- `c:dyes/light_gray`
    - `minecraft:light_gray_dye`
- `c:dyes/lime`
    - `minecraft:lime_dye`
- `c:dyes/magenta`
    - `minecraft:magenta_dye`
- `c:dyes/orange`
    - `minecraft:orange_dye`
- `c:dyes/pink`
    - `minecraft:pink_dye`
- `c:dyes/purple`
    - `minecraft:purple_dye`
- `c:dyes/red`
    - `minecraft:red_dye`
- `c:dyes/white`
    - `minecraft:white_dye`
- `c:dyes/yellow`
    - `minecraft:yellow_dye`
- `c:enchantables`
    - `minecraft:bow`
    - `minecraft:brush`
    - `minecraft:carrot_on_a_stick`
    - `minecraft:carved_pumpkin`
    - `minecraft:chainmail_boots`
    - `minecraft:chainmail_chestplate`
    - `minecraft:chainmail_helmet`
    - `minecraft:chainmail_leggings`
    - `minecraft:compass`
    - `minecraft:creeper_head`
    - `minecraft:crossbow`
    - `minecraft:diamond_axe`
    - `minecraft:diamond_boots`
    - `minecraft:diamond_chestplate`
    - `minecraft:diamond_helmet`
    - `minecraft:diamond_hoe`
    - `minecraft:diamond_leggings`
    - `minecraft:diamond_pickaxe`
    - `minecraft:diamond_shovel`
    - `minecraft:diamond_sword`
    - `minecraft:dragon_head`
    - `minecraft:elytra`
    - `minecraft:fishing_rod`
    - `minecraft:flint_and_steel`
    - `minecraft:golden_axe`
    - `minecraft:golden_boots`
    - `minecraft:golden_chestplate`
    - `minecraft:golden_helmet`
    - `minecraft:golden_hoe`
    - `minecraft:golden_leggings`
    - `minecraft:golden_pickaxe`
    - `minecraft:golden_shovel`
    - `minecraft:golden_sword`
    - `minecraft:iron_axe`
    - `minecraft:iron_boots`
    - `minecraft:iron_chestplate`
    - `minecraft:iron_helmet`
    - `minecraft:iron_hoe`
    - `minecraft:iron_leggings`
    - `minecraft:iron_pickaxe`
    - `minecraft:iron_shovel`
    - `minecraft:iron_sword`
    - `minecraft:leather_boots`
    - `minecraft:leather_chestplate`
    - `minecraft:leather_helmet`
    - `minecraft:leather_leggings`
    - `minecraft:mace`
    - `minecraft:netherite_axe`
    - `minecraft:netherite_boots`
    - `minecraft:netherite_chestplate`
    - `minecraft:netherite_helmet`
    - `minecraft:netherite_hoe`
    - `minecraft:netherite_leggings`
    - `minecraft:netherite_pickaxe`
    - `minecraft:netherite_shovel`
    - `minecraft:netherite_sword`
    - `minecraft:piglin_head`
    - `minecraft:player_head`
    - `minecraft:shears`
    - `minecraft:shield`
    - `minecraft:skeleton_skull`
    - `minecraft:stone_axe`
    - `minecraft:stone_hoe`
    - `minecraft:stone_pickaxe`
    - `minecraft:stone_shovel`
    - `minecraft:stone_sword`
    - `minecraft:trident`
    - `minecraft:turtle_helmet`
    - `minecraft:warped_fungus_on_a_stick`
    - `minecraft:wither_skeleton_skull`
    - `minecraft:wooden_axe`
    - `minecraft:wooden_hoe`
    - `minecraft:wooden_pickaxe`
    - `minecraft:wooden_shovel`
    - `minecraft:wooden_sword`
    - `minecraft:zombie_head`
- `c:ender_pearls`
    - `minecraft:ender_pearl`
- `c:fertilizers`
    - `minecraft:bone_meal`
- `c:foods`
    - `minecraft:apple`
    - `minecraft:baked_potato`
    - `minecraft:beef`
    - `minecraft:beetroot`
    - `minecraft:beetroot_soup`
    - `minecraft:bread`
    - `minecraft:cake`
    - `minecraft:carrot`
    - `minecraft:chicken`
    - `minecraft:chorus_fruit`
    - `minecraft:cod`
    - `minecraft:cooked_beef`
    - `minecraft:cooked_chicken`
    - `minecraft:cooked_cod`
    - `minecraft:cooked_mutton`
    - `minecraft:cooked_porkchop`
    - `minecraft:cooked_rabbit`
    - `minecraft:cooked_salmon`
    - `minecraft:cookie`
    - `minecraft:dried_kelp`
    - `minecraft:enchanted_golden_apple`
    - `minecraft:glow_berries`
    - `minecraft:golden_apple`
    - `minecraft:golden_carrot`
    - `minecraft:honey_bottle`
    - `minecraft:melon_slice`
    - `minecraft:mushroom_stew`
    - `minecraft:mutton`
    - `minecraft:ominous_bottle`
    - `minecraft:poisonous_potato`
    - `minecraft:porkchop`
    - `minecraft:potato`
    - `minecraft:pufferfish`
    - `minecraft:pumpkin_pie`
    - `minecraft:rabbit`
    - `minecraft:rabbit_stew`
    - `minecraft:rotten_flesh`
    - `minecraft:salmon`
    - `minecraft:spider_eye`
    - `minecraft:suspicious_stew`
    - `minecraft:sweet_berries`
    - `minecraft:tropical_fish`
- `c:foods/berry`
    - `minecraft:glow_berries`
    - `minecraft:sweet_berries`
- `c:foods/bread`
    - `minecraft:bread`
- `c:foods/candy`
- `c:foods/cooked_fish`
    - `minecraft:cooked_cod`
    - `minecraft:cooked_salmon`
- `c:foods/cooked_meat`
    - `minecraft:cooked_beef`
    - `minecraft:cooked_chicken`
    - `minecraft:cooked_mutton`
    - `minecraft:cooked_porkchop`
    - `minecraft:cooked_rabbit`
- `c:foods/cookie`
    - `minecraft:cookie`
- `c:foods/edible_when_placed`
    - `minecraft:cake`
- `c:foods/food_poisoning`
    - `minecraft:chicken`
    - `minecraft:poisonous_potato`
    - `minecraft:pufferfish`
    - `minecraft:rotten_flesh`
    - `minecraft:spider_eye`
- `c:foods/fruit`
    - `minecraft:apple`
    - `minecraft:chorus_fruit`
    - `minecraft:enchanted_golden_apple`
    - `minecraft:golden_apple`
    - `minecraft:melon_slice`
- `c:foods/golden`
    - `minecraft:enchanted_golden_apple`
    - `minecraft:golden_apple`
    - `minecraft:golden_carrot`
- `c:foods/raw_fish`
    - `minecraft:cod`
    - `minecraft:pufferfish`
    - `minecraft:salmon`
    - `minecraft:tropical_fish`
- `c:foods/raw_meat`
    - `minecraft:beef`
    - `minecraft:chicken`
    - `minecraft:mutton`
    - `minecraft:porkchop`
    - `minecraft:rabbit`
- `c:foods/soup`
    - `minecraft:beetroot_soup`
    - `minecraft:mushroom_stew`
    - `minecraft:rabbit_stew`
    - `minecraft:suspicious_stew`
- `c:foods/vegetable`
    - `minecraft:beetroot`
    - `minecraft:carrot`
    - `minecraft:golden_carrot`
    - `minecraft:potato`
- `c:gems`
    - `minecraft:amethyst_shard`
    - `minecraft:diamond`
    - `minecraft:emerald`
    - `minecraft:lapis_lazuli`
    - `minecraft:prismarine_crystals`
    - `minecraft:quartz`
- `c:gems/amethyst`
    - `minecraft:amethyst_shard`
- `c:gems/diamond`
    - `minecraft:diamond`
- `c:gems/emerald`
    - `minecraft:emerald`
- `c:gems/lapis`
    - `minecraft:lapis_lazuli`
- `c:gems/prismarine`
    - `minecraft:prismarine_crystals`
- `c:gems/quartz`
    - `minecraft:quartz`
- `c:glass_blocks`
    - `minecraft:black_stained_glass`
    - `minecraft:blue_stained_glass`
    - `minecraft:brown_stained_glass`
    - `minecraft:cyan_stained_glass`
    - `minecraft:glass`
    - `minecraft:gray_stained_glass`
    - `minecraft:green_stained_glass`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:lime_stained_glass`
    - `minecraft:magenta_stained_glass`
    - `minecraft:orange_stained_glass`
    - `minecraft:pink_stained_glass`
    - `minecraft:purple_stained_glass`
    - `minecraft:red_stained_glass`
    - `minecraft:tinted_glass`
    - `minecraft:white_stained_glass`
    - `minecraft:yellow_stained_glass`
- `c:glass_blocks/cheap`
    - `minecraft:black_stained_glass`
    - `minecraft:blue_stained_glass`
    - `minecraft:brown_stained_glass`
    - `minecraft:cyan_stained_glass`
    - `minecraft:glass`
    - `minecraft:gray_stained_glass`
    - `minecraft:green_stained_glass`
    - `minecraft:light_blue_stained_glass`
    - `minecraft:light_gray_stained_glass`
    - `minecraft:lime_stained_glass`
    - `minecraft:magenta_stained_glass`
    - `minecraft:orange_stained_glass`
    - `minecraft:pink_stained_glass`
    - `minecraft:purple_stained_glass`
    - `minecraft:red_stained_glass`
    - `minecraft:white_stained_glass`
    - `minecraft:yellow_stained_glass`
- `c:glass_blocks/colorless`
    - `minecraft:glass`
- `c:glass_blocks/tinted`
    - `minecraft:tinted_glass`
- `c:glass_panes`
    - `minecraft:black_stained_glass_pane`
    - `minecraft:blue_stained_glass_pane`
    - `minecraft:brown_stained_glass_pane`
    - `minecraft:cyan_stained_glass_pane`
    - `minecraft:glass_pane`
    - `minecraft:gray_stained_glass_pane`
    - `minecraft:green_stained_glass_pane`
    - `minecraft:light_blue_stained_glass_pane`
    - `minecraft:light_gray_stained_glass_pane`
    - `minecraft:lime_stained_glass_pane`
    - `minecraft:magenta_stained_glass_pane`
    - `minecraft:orange_stained_glass_pane`
    - `minecraft:pink_stained_glass_pane`
    - `minecraft:purple_stained_glass_pane`
    - `minecraft:red_stained_glass_pane`
    - `minecraft:white_stained_glass_pane`
    - `minecraft:yellow_stained_glass_pane`
- `c:glass_panes/colorless`
    - `minecraft:glass_pane`
- `c:glazed_terracottas`
    - `minecraft:black_glazed_terracotta`
    - `minecraft:blue_glazed_terracotta`
    - `minecraft:brown_glazed_terracotta`
    - `minecraft:cyan_glazed_terracotta`
    - `minecraft:gray_glazed_terracotta`
    - `minecraft:green_glazed_terracotta`
    - `minecraft:light_blue_glazed_terracotta`
    - `minecraft:light_gray_glazed_terracotta`
    - `minecraft:lime_glazed_terracotta`
    - `minecraft:magenta_glazed_terracotta`
    - `minecraft:orange_glazed_terracotta`
    - `minecraft:pink_glazed_terracotta`
    - `minecraft:purple_glazed_terracotta`
    - `minecraft:red_glazed_terracotta`
    - `minecraft:white_glazed_terracotta`
    - `minecraft:yellow_glazed_terracotta`
- `c:hidden_from_recipe_viewers`
- `c:ingots`
    - `minecraft:copper_ingot`
    - `minecraft:gold_ingot`
    - `minecraft:iron_ingot`
    - `minecraft:netherite_ingot`
- `c:ingots/copper`
    - `minecraft:copper_ingot`
- `c:ingots/gold`
    - `minecraft:gold_ingot`
- `c:ingots/iron`
    - `minecraft:iron_ingot`
- `c:ingots/netherite`
    - `minecraft:netherite_ingot`
- `c:leathers`
    - `minecraft:leather`
- `c:music_discs`
    - `minecraft:music_disc_11`
    - `minecraft:music_disc_13`
    - `minecraft:music_disc_5`
    - `minecraft:music_disc_blocks`
    - `minecraft:music_disc_cat`
    - `minecraft:music_disc_chirp`
    - `minecraft:music_disc_creator`
    - `minecraft:music_disc_creator_music_box`
    - `minecraft:music_disc_far`
    - `minecraft:music_disc_mall`
    - `minecraft:music_disc_mellohi`
    - `minecraft:music_disc_otherside`
    - `minecraft:music_disc_pigstep`
    - `minecraft:music_disc_precipice`
    - `minecraft:music_disc_relic`
    - `minecraft:music_disc_stal`
    - `minecraft:music_disc_strad`
    - `minecraft:music_disc_wait`
    - `minecraft:music_disc_ward`
- `c:nuggets`
    - `minecraft:gold_nugget`
    - `minecraft:iron_nugget`
- `c:nuggets/gold`
    - `minecraft:gold_nugget`
- `c:nuggets/iron`
    - `minecraft:iron_nugget`
- `c:obsidians`
    - `minecraft:crying_obsidian`
    - `minecraft:obsidian`
- `c:obsidians/crying`
    - `minecraft:crying_obsidian`
- `c:obsidians/normal`
    - `minecraft:obsidian`
- `c:ores`
    - `minecraft:ancient_debris`
    - `minecraft:coal_ore`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:lapis_ore`
    - `minecraft:nether_gold_ore`
    - `minecraft:nether_quartz_ore`
    - `minecraft:redstone_ore`
- `c:ores/netherite_scrap`
    - `minecraft:ancient_debris`
- `c:ores/quartz`
    - `minecraft:nether_quartz_ore`
- `c:player_workstations/crafting_tables`
    - `minecraft:crafting_table`
- `c:player_workstations/furnaces`
    - `minecraft:furnace`
- `c:raw_materials`
    - `minecraft:raw_copper`
    - `minecraft:raw_gold`
    - `minecraft:raw_iron`
- `c:raw_materials/copper`
    - `minecraft:raw_copper`
- `c:raw_materials/gold`
    - `minecraft:raw_gold`
- `c:raw_materials/iron`
    - `minecraft:raw_iron`
- `c:rods`
    - `minecraft:blaze_rod`
    - `minecraft:breeze_rod`
    - `minecraft:stick`
- `c:rods/blaze`
    - `minecraft:blaze_rod`
- `c:rods/breeze`
    - `minecraft:breeze_rod`
- `c:rods/wooden`
    - `minecraft:stick`
- `c:ropes`
- `c:sandstone/blocks`
    - `minecraft:chiseled_red_sandstone`
    - `minecraft:chiseled_sandstone`
    - `minecraft:cut_red_sandstone`
    - `minecraft:cut_sandstone`
    - `minecraft:red_sandstone`
    - `minecraft:sandstone`
    - `minecraft:smooth_red_sandstone`
    - `minecraft:smooth_sandstone`
- `c:sandstone/red_blocks`
    - `minecraft:chiseled_red_sandstone`
    - `minecraft:cut_red_sandstone`
    - `minecraft:red_sandstone`
    - `minecraft:smooth_red_sandstone`
- `c:sandstone/red_slabs`
    - `minecraft:cut_red_sandstone_slab`
    - `minecraft:red_sandstone_slab`
    - `minecraft:smooth_red_sandstone_slab`
- `c:sandstone/red_stairs`
    - `minecraft:red_sandstone_stairs`
    - `minecraft:smooth_red_sandstone_stairs`
- `c:sandstone/slabs`
    - `minecraft:cut_red_sandstone_slab`
    - `minecraft:cut_sandstone_slab`
    - `minecraft:red_sandstone_slab`
    - `minecraft:sandstone_slab`
    - `minecraft:smooth_red_sandstone_slab`
    - `minecraft:smooth_sandstone_slab`
- `c:sandstone/stairs`
    - `minecraft:red_sandstone_stairs`
    - `minecraft:sandstone_stairs`
    - `minecraft:smooth_red_sandstone_stairs`
    - `minecraft:smooth_sandstone_stairs`
- `c:sandstone/uncolored_blocks`
    - `minecraft:chiseled_sandstone`
    - `minecraft:cut_sandstone`
    - `minecraft:sandstone`
    - `minecraft:smooth_sandstone`
- `c:sandstone/uncolored_slabs`
    - `minecraft:cut_sandstone_slab`
    - `minecraft:sandstone_slab`
    - `minecraft:smooth_sandstone_slab`
- `c:sandstone/uncolored_stairs`
    - `minecraft:sandstone_stairs`
    - `minecraft:smooth_sandstone_stairs`
- `c:shulker_boxes`
    - `minecraft:black_shulker_box`
    - `minecraft:blue_shulker_box`
    - `minecraft:brown_shulker_box`
    - `minecraft:cyan_shulker_box`
    - `minecraft:gray_shulker_box`
    - `minecraft:green_shulker_box`
    - `minecraft:light_blue_shulker_box`
    - `minecraft:light_gray_shulker_box`
    - `minecraft:lime_shulker_box`
    - `minecraft:magenta_shulker_box`
    - `minecraft:orange_shulker_box`
    - `minecraft:pink_shulker_box`
    - `minecraft:purple_shulker_box`
    - `minecraft:red_shulker_box`
    - `minecraft:shulker_box`
    - `minecraft:white_shulker_box`
    - `minecraft:yellow_shulker_box`
- `c:slime_balls`
    - `minecraft:slime_ball`
- `c:stones`
    - `minecraft:andesite`
    - `minecraft:deepslate`
    - `minecraft:diorite`
    - `minecraft:granite`
    - `minecraft:stone`
    - `minecraft:tuff`
- `c:storage_blocks`
    - `minecraft:bone_block`
    - `minecraft:coal_block`
    - `minecraft:copper_block`
    - `minecraft:diamond_block`
    - `minecraft:dried_kelp_block`
    - `minecraft:emerald_block`
    - `minecraft:gold_block`
    - `minecraft:hay_block`
    - `minecraft:iron_block`
    - `minecraft:lapis_block`
    - `minecraft:netherite_block`
    - `minecraft:raw_copper_block`
    - `minecraft:raw_gold_block`
    - `minecraft:raw_iron_block`
    - `minecraft:redstone_block`
    - `minecraft:slime_block`
- `c:storage_blocks/bone_meal`
    - `minecraft:bone_block`
- `c:storage_blocks/coal`
    - `minecraft:coal_block`
- `c:storage_blocks/copper`
    - `minecraft:copper_block`
- `c:storage_blocks/diamond`
    - `minecraft:diamond_block`
- `c:storage_blocks/dried_kelp`
    - `minecraft:dried_kelp_block`
- `c:storage_blocks/emerald`
    - `minecraft:emerald_block`
- `c:storage_blocks/gold`
    - `minecraft:gold_block`
- `c:storage_blocks/iron`
    - `minecraft:iron_block`
- `c:storage_blocks/lapis`
    - `minecraft:lapis_block`
- `c:storage_blocks/netherite`
    - `minecraft:netherite_block`
- `c:storage_blocks/raw_copper`
    - `minecraft:raw_copper_block`
- `c:storage_blocks/raw_gold`
    - `minecraft:raw_gold_block`
- `c:storage_blocks/raw_iron`
    - `minecraft:raw_iron_block`
- `c:storage_blocks/redstone`
    - `minecraft:redstone_block`
- `c:storage_blocks/slime`
    - `minecraft:slime_block`
- `c:storage_blocks/wheat`
    - `minecraft:hay_block`
- `c:strings`
    - `minecraft:string`
- `c:tools`
    - `minecraft:bow`
    - `minecraft:brush`
    - `minecraft:crossbow`
    - `minecraft:diamond_axe`
    - `minecraft:diamond_hoe`
    - `minecraft:diamond_pickaxe`
    - `minecraft:diamond_shovel`
    - `minecraft:diamond_sword`
    - `minecraft:fishing_rod`
    - `minecraft:flint_and_steel`
    - `minecraft:golden_axe`
    - `minecraft:golden_hoe`
    - `minecraft:golden_pickaxe`
    - `minecraft:golden_shovel`
    - `minecraft:golden_sword`
    - `minecraft:iron_axe`
    - `minecraft:iron_hoe`
    - `minecraft:iron_pickaxe`
    - `minecraft:iron_shovel`
    - `minecraft:iron_sword`
    - `minecraft:mace`
    - `minecraft:netherite_axe`
    - `minecraft:netherite_hoe`
    - `minecraft:netherite_pickaxe`
    - `minecraft:netherite_shovel`
    - `minecraft:netherite_sword`
    - `minecraft:shears`
    - `minecraft:shield`
    - `minecraft:stone_axe`
    - `minecraft:stone_hoe`
    - `minecraft:stone_pickaxe`
    - `minecraft:stone_shovel`
    - `minecraft:stone_sword`
    - `minecraft:trident`
    - `minecraft:wooden_axe`
    - `minecraft:wooden_hoe`
    - `minecraft:wooden_pickaxe`
    - `minecraft:wooden_shovel`
    - `minecraft:wooden_sword`
- `c:tools/bow`
    - `minecraft:bow`
- `c:tools/brush`
    - `minecraft:brush`
- `c:tools/crossbow`
    - `minecraft:crossbow`
- `c:tools/fishing_rod`
    - `minecraft:fishing_rod`
- `c:tools/igniter`
    - `minecraft:flint_and_steel`
- `c:tools/mace`
    - `minecraft:mace`
- `c:tools/melee_weapon`
    - `minecraft:diamond_axe`
    - `minecraft:diamond_sword`
    - `minecraft:golden_axe`
    - `minecraft:golden_sword`
    - `minecraft:iron_axe`
    - `minecraft:iron_sword`
    - `minecraft:mace`
    - `minecraft:netherite_axe`
    - `minecraft:netherite_sword`
    - `minecraft:stone_axe`
    - `minecraft:stone_sword`
    - `minecraft:trident`
    - `minecraft:wooden_axe`
    - `minecraft:wooden_sword`
- `c:tools/mining_tool`
    - `minecraft:diamond_pickaxe`
    - `minecraft:golden_pickaxe`
    - `minecraft:iron_pickaxe`
    - `minecraft:netherite_pickaxe`
    - `minecraft:stone_pickaxe`
    - `minecraft:wooden_pickaxe`
- `c:tools/ranged_weapon`
    - `minecraft:bow`
    - `minecraft:crossbow`
    - `minecraft:trident`
- `c:tools/shear`
    - `minecraft:shears`
- `c:tools/shield`
    - `minecraft:shield`
- `c:tools/spear`
    - `minecraft:trident`
- `c:villager_job_sites`
    - `minecraft:barrel`
    - `minecraft:blast_furnace`
    - `minecraft:brewing_stand`
    - `minecraft:cartography_table`
    - `minecraft:cauldron`
    - `minecraft:composter`
    - `minecraft:fletching_table`
    - `minecraft:grindstone`
    - `minecraft:lectern`
    - `minecraft:loom`
    - `minecraft:smithing_table`
    - `minecraft:smoker`
    - `minecraft:stonecutter`
- `forge:bones`
    - `minecraft:bone`
- `forge:chests/ender`
    - `minecraft:ender_chest`
- `forge:chests/trapped`
    - `minecraft:trapped_chest`
- `forge:cobblestone/deepslate`
    - `minecraft:cobbled_deepslate`
- `forge:cobblestone/infested`
    - `minecraft:infested_cobblestone`
- `forge:cobblestone/mossy`
    - `minecraft:mossy_cobblestone`
- `forge:cobblestone/normal`
    - `minecraft:cobblestone`
- `forge:eggs`
    - `minecraft:egg`
- `forge:enchanting_fuels`
    - `minecraft:lapis_lazuli`
- `forge:end_stones`
    - `minecraft:end_stone`
- `forge:feathers`
    - `minecraft:feather`
- `forge:fence_gates`
    - `minecraft:acacia_fence_gate`
    - `minecraft:bamboo_fence_gate`
    - `minecraft:birch_fence_gate`
    - `minecraft:cherry_fence_gate`
    - `minecraft:crimson_fence_gate`
    - `minecraft:dark_oak_fence_gate`
    - `minecraft:jungle_fence_gate`
    - `minecraft:mangrove_fence_gate`
    - `minecraft:oak_fence_gate`
    - `minecraft:spruce_fence_gate`
    - `minecraft:warped_fence_gate`
- `forge:fence_gates/wooden`
    - `minecraft:acacia_fence_gate`
    - `minecraft:bamboo_fence_gate`
    - `minecraft:birch_fence_gate`
    - `minecraft:cherry_fence_gate`
    - `minecraft:crimson_fence_gate`
    - `minecraft:dark_oak_fence_gate`
    - `minecraft:jungle_fence_gate`
    - `minecraft:mangrove_fence_gate`
    - `minecraft:oak_fence_gate`
    - `minecraft:spruce_fence_gate`
    - `minecraft:warped_fence_gate`
- `forge:fences`
    - `minecraft:acacia_fence`
    - `minecraft:bamboo_fence`
    - `minecraft:birch_fence`
    - `minecraft:cherry_fence`
    - `minecraft:crimson_fence`
    - `minecraft:dark_oak_fence`
    - `minecraft:jungle_fence`
    - `minecraft:mangrove_fence`
    - `minecraft:nether_brick_fence`
    - `minecraft:oak_fence`
    - `minecraft:spruce_fence`
    - `minecraft:warped_fence`
- `forge:fences/nether_brick`
    - `minecraft:nether_brick_fence`
- `forge:fences/wooden`
    - `minecraft:acacia_fence`
    - `minecraft:bamboo_fence`
    - `minecraft:birch_fence`
    - `minecraft:cherry_fence`
    - `minecraft:crimson_fence`
    - `minecraft:dark_oak_fence`
    - `minecraft:jungle_fence`
    - `minecraft:mangrove_fence`
    - `minecraft:oak_fence`
    - `minecraft:spruce_fence`
    - `minecraft:warped_fence`
- `forge:foods/pie`
    - `minecraft:pumpkin_pie`
- `forge:gravel`
    - `minecraft:gravel`
- `forge:gunpowder`
    - `minecraft:gunpowder`
- `forge:mushrooms`
    - `minecraft:brown_mushroom`
    - `minecraft:red_mushroom`
- `forge:nether_stars`
    - `minecraft:nether_star`
- `forge:netherrack`
    - `minecraft:netherrack`
- `forge:ore_bearing_ground/deepslate`
    - `minecraft:deepslate`
- `forge:ore_bearing_ground/netherrack`
    - `minecraft:netherrack`
- `forge:ore_bearing_ground/stone`
    - `minecraft:stone`
- `forge:ore_rates/dense`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:lapis_ore`
    - `minecraft:redstone_ore`
- `forge:ore_rates/singular`
    - `minecraft:ancient_debris`
    - `minecraft:coal_ore`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:nether_quartz_ore`
- `forge:ore_rates/sparse`
    - `minecraft:nether_gold_ore`
- `forge:ores/coal`
    - `minecraft:coal_ore`
    - `minecraft:deepslate_coal_ore`
- `forge:ores/copper`
    - `minecraft:copper_ore`
    - `minecraft:deepslate_copper_ore`
- `forge:ores/diamond`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:diamond_ore`
- `forge:ores/emerald`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:emerald_ore`
- `forge:ores/gold`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:gold_ore`
    - `minecraft:nether_gold_ore`
- `forge:ores/iron`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:iron_ore`
- `forge:ores/lapis`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:lapis_ore`
- `forge:ores/redstone`
    - `minecraft:deepslate_redstone_ore`
    - `minecraft:redstone_ore`
- `forge:ores_in_ground/deepslate`
    - `minecraft:deepslate_coal_ore`
    - `minecraft:deepslate_copper_ore`
    - `minecraft:deepslate_diamond_ore`
    - `minecraft:deepslate_emerald_ore`
    - `minecraft:deepslate_gold_ore`
    - `minecraft:deepslate_iron_ore`
    - `minecraft:deepslate_lapis_ore`
    - `minecraft:deepslate_redstone_ore`
- `forge:ores_in_ground/netherrack`
    - `minecraft:nether_gold_ore`
    - `minecraft:nether_quartz_ore`
- `forge:ores_in_ground/stone`
    - `minecraft:coal_ore`
    - `minecraft:copper_ore`
    - `minecraft:diamond_ore`
    - `minecraft:emerald_ore`
    - `minecraft:gold_ore`
    - `minecraft:iron_ore`
    - `minecraft:lapis_ore`
    - `minecraft:redstone_ore`
- `forge:sand`
    - `minecraft:red_sand`
    - `minecraft:sand`
- `forge:sand/colorless`
    - `minecraft:sand`
- `forge:sand/red`
    - `minecraft:red_sand`
- `forge:seeds`
    - `minecraft:beetroot_seeds`
    - `minecraft:melon_seeds`
    - `minecraft:pumpkin_seeds`
    - `minecraft:wheat_seeds`
- `forge:seeds/beetroot`
    - `minecraft:beetroot_seeds`
- `forge:seeds/melon`
    - `minecraft:melon_seeds`
- `forge:seeds/pumpkin`
    - `minecraft:pumpkin_seeds`
- `forge:seeds/wheat`
    - `minecraft:wheat_seeds`

worldgen/biome
--------------
- `c:hidden_from_locator_selection`
- `c:is_aquatic`
    - `minecraft:cold_ocean`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:deep_lukewarm_ocean`
    - `minecraft:deep_ocean`
    - `minecraft:frozen_ocean`
    - `minecraft:frozen_river`
    - `minecraft:lukewarm_ocean`
    - `minecraft:ocean`
    - `minecraft:river`
    - `minecraft:warm_ocean`
- `c:is_aquatic_icy`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:frozen_ocean`
    - `minecraft:frozen_river`
- `c:is_badlands`
    - `minecraft:badlands`
    - `minecraft:eroded_badlands`
    - `minecraft:wooded_badlands`
- `c:is_beach`
    - `minecraft:beach`
    - `minecraft:snowy_beach`
- `c:is_birch_forest`
    - `minecraft:birch_forest`
    - `minecraft:old_growth_birch_forest`
- `c:is_cave`
    - `minecraft:deep_dark`
    - `minecraft:dripstone_caves`
    - `minecraft:lush_caves`
- `c:is_cold`
    - `minecraft:cold_ocean`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
    - `minecraft:frozen_ocean`
    - `minecraft:frozen_peaks`
    - `minecraft:frozen_river`
    - `minecraft:grove`
    - `minecraft:ice_spikes`
    - `minecraft:jagged_peaks`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:small_end_islands`
    - `minecraft:snowy_beach`
    - `minecraft:snowy_plains`
    - `minecraft:snowy_slopes`
    - `minecraft:snowy_taiga`
    - `minecraft:stony_shore`
    - `minecraft:taiga`
    - `minecraft:the_end`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
- `c:is_cold/end`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
    - `minecraft:small_end_islands`
    - `minecraft:the_end`
- `c:is_cold/overworld`
    - `minecraft:cold_ocean`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:frozen_ocean`
    - `minecraft:frozen_peaks`
    - `minecraft:frozen_river`
    - `minecraft:grove`
    - `minecraft:ice_spikes`
    - `minecraft:jagged_peaks`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:snowy_beach`
    - `minecraft:snowy_plains`
    - `minecraft:snowy_slopes`
    - `minecraft:snowy_taiga`
    - `minecraft:stony_shore`
    - `minecraft:taiga`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
- `c:is_dead`
- `c:is_deep_ocean`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:deep_lukewarm_ocean`
    - `minecraft:deep_ocean`
- `c:is_dense_vegetation`
    - `minecraft:bamboo_jungle`
    - `minecraft:dark_forest`
    - `minecraft:jungle`
    - `minecraft:mangrove_swamp`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:old_growth_spruce_taiga`
- `c:is_dense_vegetation/overworld`
    - `minecraft:bamboo_jungle`
    - `minecraft:dark_forest`
    - `minecraft:jungle`
    - `minecraft:mangrove_swamp`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:old_growth_spruce_taiga`
- `c:is_desert`
    - `minecraft:desert`
- `c:is_dry`
    - `minecraft:badlands`
    - `minecraft:basalt_deltas`
    - `minecraft:crimson_forest`
    - `minecraft:desert`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
    - `minecraft:eroded_badlands`
    - `minecraft:nether_wastes`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:small_end_islands`
    - `minecraft:soul_sand_valley`
    - `minecraft:the_end`
    - `minecraft:warped_forest`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_dry/end`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
    - `minecraft:small_end_islands`
    - `minecraft:the_end`
- `c:is_dry/nether`
    - `minecraft:basalt_deltas`
    - `minecraft:crimson_forest`
    - `minecraft:nether_wastes`
    - `minecraft:soul_sand_valley`
    - `minecraft:warped_forest`
- `c:is_dry/overworld`
    - `minecraft:badlands`
    - `minecraft:desert`
    - `minecraft:eroded_badlands`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_end`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
    - `minecraft:small_end_islands`
    - `minecraft:the_end`
- `c:is_floral`
    - `minecraft:cherry_grove`
    - `minecraft:flower_forest`
    - `minecraft:meadow`
    - `minecraft:sunflower_plains`
- `c:is_flower_forest`
    - `minecraft:flower_forest`
- `c:is_forest`
    - `minecraft:birch_forest`
    - `minecraft:dark_forest`
    - `minecraft:flower_forest`
    - `minecraft:forest`
    - `minecraft:grove`
    - `minecraft:old_growth_birch_forest`
- `c:is_hill`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
- `c:is_hot`
    - `minecraft:badlands`
    - `minecraft:bamboo_jungle`
    - `minecraft:basalt_deltas`
    - `minecraft:crimson_forest`
    - `minecraft:desert`
    - `minecraft:eroded_badlands`
    - `minecraft:jungle`
    - `minecraft:mangrove_swamp`
    - `minecraft:nether_wastes`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:soul_sand_valley`
    - `minecraft:sparse_jungle`
    - `minecraft:stony_peaks`
    - `minecraft:swamp`
    - `minecraft:warm_ocean`
    - `minecraft:warped_forest`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_hot/nether`
    - `minecraft:basalt_deltas`
    - `minecraft:crimson_forest`
    - `minecraft:nether_wastes`
    - `minecraft:soul_sand_valley`
    - `minecraft:warped_forest`
- `c:is_hot/overworld`
    - `minecraft:badlands`
    - `minecraft:bamboo_jungle`
    - `minecraft:desert`
    - `minecraft:eroded_badlands`
    - `minecraft:jungle`
    - `minecraft:mangrove_swamp`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:sparse_jungle`
    - `minecraft:stony_peaks`
    - `minecraft:swamp`
    - `minecraft:warm_ocean`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_icy`
    - `minecraft:frozen_peaks`
    - `minecraft:ice_spikes`
- `c:is_jungle`
    - `minecraft:bamboo_jungle`
    - `minecraft:jungle`
    - `minecraft:sparse_jungle`
- `c:is_mountain`
    - `minecraft:cherry_grove`
    - `minecraft:frozen_peaks`
    - `minecraft:grove`
    - `minecraft:jagged_peaks`
    - `minecraft:meadow`
    - `minecraft:snowy_slopes`
    - `minecraft:stony_peaks`
- `c:is_mountain/peak`
    - `minecraft:frozen_peaks`
    - `minecraft:jagged_peaks`
    - `minecraft:stony_peaks`
- `c:is_mountain/slope`
    - `minecraft:cherry_grove`
    - `minecraft:grove`
    - `minecraft:meadow`
    - `minecraft:snowy_slopes`
- `c:is_mushroom`
    - `minecraft:mushroom_fields`
- `c:is_nether`
    - `minecraft:basalt_deltas`
    - `minecraft:crimson_forest`
    - `minecraft:nether_wastes`
    - `minecraft:soul_sand_valley`
    - `minecraft:warped_forest`
- `c:is_nether_forest`
    - `minecraft:crimson_forest`
    - `minecraft:warped_forest`
- `c:is_ocean`
    - `minecraft:cold_ocean`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:deep_lukewarm_ocean`
    - `minecraft:deep_ocean`
    - `minecraft:frozen_ocean`
    - `minecraft:lukewarm_ocean`
    - `minecraft:ocean`
    - `minecraft:warm_ocean`
- `c:is_old_growth`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
- `c:is_outer_end_island`
    - `minecraft:end_barrens`
    - `minecraft:end_highlands`
    - `minecraft:end_midlands`
- `c:is_overworld`
    - `minecraft:badlands`
    - `minecraft:bamboo_jungle`
    - `minecraft:beach`
    - `minecraft:birch_forest`
    - `minecraft:cherry_grove`
    - `minecraft:cold_ocean`
    - `minecraft:dark_forest`
    - `minecraft:deep_cold_ocean`
    - `minecraft:deep_dark`
    - `minecraft:deep_frozen_ocean`
    - `minecraft:deep_lukewarm_ocean`
    - `minecraft:deep_ocean`
    - `minecraft:desert`
    - `minecraft:dripstone_caves`
    - `minecraft:eroded_badlands`
    - `minecraft:flower_forest`
    - `minecraft:forest`
    - `minecraft:frozen_ocean`
    - `minecraft:frozen_peaks`
    - `minecraft:frozen_river`
    - `minecraft:grove`
    - `minecraft:ice_spikes`
    - `minecraft:jagged_peaks`
    - `minecraft:jungle`
    - `minecraft:lukewarm_ocean`
    - `minecraft:lush_caves`
    - `minecraft:mangrove_swamp`
    - `minecraft:meadow`
    - `minecraft:mushroom_fields`
    - `minecraft:ocean`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:plains`
    - `minecraft:river`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:snowy_beach`
    - `minecraft:snowy_plains`
    - `minecraft:snowy_slopes`
    - `minecraft:snowy_taiga`
    - `minecraft:sparse_jungle`
    - `minecraft:stony_peaks`
    - `minecraft:stony_shore`
    - `minecraft:sunflower_plains`
    - `minecraft:swamp`
    - `minecraft:taiga`
    - `minecraft:warm_ocean`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_plains`
    - `minecraft:plains`
    - `minecraft:sunflower_plains`
- `c:is_river`
    - `minecraft:frozen_river`
    - `minecraft:river`
- `c:is_savanna`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:windswept_savanna`
- `c:is_shallow_ocean`
    - `minecraft:cold_ocean`
    - `minecraft:frozen_ocean`
    - `minecraft:lukewarm_ocean`
    - `minecraft:ocean`
    - `minecraft:warm_ocean`
- `c:is_snowy`
    - `minecraft:frozen_peaks`
    - `minecraft:grove`
    - `minecraft:ice_spikes`
    - `minecraft:jagged_peaks`
    - `minecraft:snowy_beach`
    - `minecraft:snowy_plains`
    - `minecraft:snowy_slopes`
    - `minecraft:snowy_taiga`
- `c:is_snowy_plains`
    - `minecraft:snowy_plains`
- `c:is_sparse_vegetation`
    - `minecraft:frozen_peaks`
    - `minecraft:jagged_peaks`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:snowy_slopes`
    - `minecraft:sparse_jungle`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_sparse_vegetation/overworld`
    - `minecraft:frozen_peaks`
    - `minecraft:jagged_peaks`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:snowy_slopes`
    - `minecraft:sparse_jungle`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
    - `minecraft:windswept_savanna`
    - `minecraft:wooded_badlands`
- `c:is_stony_shores`
    - `minecraft:stony_shore`
- `c:is_swamp`
    - `minecraft:mangrove_swamp`
    - `minecraft:swamp`
- `c:is_taiga`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:snowy_taiga`
    - `minecraft:taiga`
- `c:is_tree/coniferous`
    - `minecraft:grove`
    - `minecraft:old_growth_pine_taiga`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:snowy_taiga`
    - `minecraft:taiga`
- `c:is_tree/deciduous`
    - `minecraft:birch_forest`
    - `minecraft:dark_forest`
    - `minecraft:flower_forest`
    - `minecraft:forest`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:windswept_forest`
- `c:is_tree/jungle`
    - `minecraft:bamboo_jungle`
    - `minecraft:jungle`
    - `minecraft:sparse_jungle`
- `c:is_tree/savanna`
    - `minecraft:savanna`
    - `minecraft:savanna_plateau`
    - `minecraft:windswept_savanna`
- `c:is_underground`
    - `minecraft:deep_dark`
    - `minecraft:dripstone_caves`
    - `minecraft:lush_caves`
- `c:is_void`
    - `minecraft:the_void`
- `c:is_wasteland`
- `c:is_wet`
    - `minecraft:bamboo_jungle`
    - `minecraft:beach`
    - `minecraft:dripstone_caves`
    - `minecraft:jungle`
    - `minecraft:lush_caves`
    - `minecraft:mangrove_swamp`
    - `minecraft:sparse_jungle`
    - `minecraft:swamp`
- `c:is_wet/overworld`
    - `minecraft:bamboo_jungle`
    - `minecraft:beach`
    - `minecraft:dripstone_caves`
    - `minecraft:jungle`
    - `minecraft:lush_caves`
    - `minecraft:mangrove_swamp`
    - `minecraft:sparse_jungle`
    - `minecraft:swamp`
- `c:is_windswept`
    - `minecraft:windswept_forest`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_hills`
    - `minecraft:windswept_savanna`
- `c:no_default_monsters`
    - `minecraft:deep_dark`
    - `minecraft:mushroom_fields`
- `forge:is_cold/nether`
- `forge:is_dense/end`
- `forge:is_dense/nether`
- `forge:is_hot/end`
- `forge:is_lush`
    - `minecraft:lush_caves`
- `forge:is_magical`
- `forge:is_modified`
- `forge:is_plateau`
    - `minecraft:meadow`
    - `minecraft:savanna_plateau`
    - `minecraft:wooded_badlands`
- `forge:is_rare`
    - `minecraft:bamboo_jungle`
    - `minecraft:deep_dark`
    - `minecraft:eroded_badlands`
    - `minecraft:flower_forest`
    - `minecraft:ice_spikes`
    - `minecraft:mushroom_fields`
    - `minecraft:old_growth_birch_forest`
    - `minecraft:old_growth_spruce_taiga`
    - `minecraft:savanna_plateau`
    - `minecraft:sparse_jungle`
    - `minecraft:sunflower_plains`
    - `minecraft:windswept_gravelly_hills`
    - `minecraft:windswept_savanna`
- `forge:is_sandy`
    - `minecraft:badlands`
    - `minecraft:beach`
    - `minecraft:desert`
    - `minecraft:wooded_badlands`
- `forge:is_sparse/end`
- `forge:is_sparse/nether`
- `forge:is_spooky`
    - `minecraft:dark_forest`
    - `minecraft:deep_dark`
- `forge:is_wet/end`
- `forge:is_wet/nether`

worldgen/structure
------------------
- `c:hidden_from_displayers`
- `c:hidden_from_locator_selection`

[commontagsdumper]: https://github.com/PaintNinja/CommonTagsDumper
[tagsrepo]: https://github.com/MinecraftForge/MinecraftForge/tree/1.21.x/src/main/generated/data

---

Custom Recipes
==============

Every recipe definition is made up of three components: the `Recipe` implementation which holds the data and handles the execution logic with the provided inputs, the `RecipeType` which represents the category or context the recipe will be used in, and the `RecipeSerializer` which handles decoding and network communication of the recipe data. How one chooses to use the recipe is up to the implementor.

Recipe
------

The `Recipe` interface describes the recipe data and the execution logic. This includes matching the inputs and providing the associated result. As the recipe subsystem performs item transformations by default, the inputs are supplied through a `Container` subtype.

!!! important
    The `Container`s passed into the recipe should be treated as if its contents were immutable. Any mutable operations should be performed on a copy of the input through `ItemStack#copy`.

To be able to obtain a recipe instance from the manager, `#matches` must return true. This method checks against the provided container to see whether the associated inputs are valid. `Ingredient`s can be used for validation by calling `Ingredient#test`.

If the recipe has been chosen, it is then built using `#assemble` which may use data from the inputs to create the result.

!!! tip
    `#assemble` should always produce a unique `ItemStack`. If unsure whether `#assemble` does so, call `ItemStack#copy` on the result before returning.

Most of the other methods are purely for integration with the recipe book.

```java
public record ExampleRecipe(Ingredient input, int data, ItemStack output) implements Recipe<Container> {
  // Implement methods here
}
```

!!! note
    While a record is used in the above example, it is not required to do so in your own implementation.

RecipeType
----------

`RecipeType` is responsible for defining the category or context the recipe will be used within. For example, if a recipe was going to be smelted in a furnace, it would have a type of `RecipeType#SMELTING`. Being blasted in a blast furnace would have a type of `RecipeType#BLASTING`.

If none of the existing types match what context the recipe will be used within, then a new `RecipeType` must be [registered][forge].

The `RecipeType` instance must then be returned by `Recipe#getType` in the new recipe subtype.

```java
// For some RegistryObject<RecipeType> EXAMPLE_TYPE
// In ExampleRecipe
@Override
public RecipeType<?> getType() {
  return EXAMPLE_TYPE.get();
}
```

RecipeSerializer
----------------

A `RecipeSerializer` is responsible for decoding JSONs and communicating across the network for an associated `Recipe` subtype. Each recipe decoded by the serializer is saved as a unique instance within the `RecipeManager`. A `RecipeSerializer` must be [registered][forge].

Only three methods need to be implemented for a `RecipeSerializer`:

 Method     | Description
 :---:      | :---
fromJson    | Decodes a JSON into the `Recipe` subtype.
toNetwork   | Encodes a `Recipe` to the buffer to send to the client. The recipe identifier does not need to be encoded.
fromNetwork | Decodes a `Recipe` from the buffer sent from the server. The recipe identifier does not need to be decoded.

The `RecipeSerializer` instance must then be returned by `Recipe#getSerializer` in the new recipe subtype.

```java
// For some RegistryObject<RecipeSerializer> EXAMPLE_SERIALIZER
// In ExampleRecipe
@Override
public RecipeSerializer<?> getSerializer() {
  return EXAMPLE_SERIALIZER.get();
}
```

!!! tip
    There are some useful methods to make reading and writing data for recipes easier. `Ingredient`s can use `#fromJson`, `#toNetwork`, and `#fromNetwork` while `ItemStack`s can use `CraftingHelper#getItemStack`, `FriendlyByteBuf#writeItem`, and `FriendlyByteBuf#readItem`.

Building the JSON
-----------------

Custom Recipe JSONs are stored in the same place as other [recipes][json]. The specified `type` should represent the registry name of the **recipe serializer**. Any additional data is specified by the serializer during decoding.

```js
{
  // The custom serializer registry name
  "type": "examplemod:example_serializer",
  "input": {
    // Some ingredient input
  },
  "data": 0, // Some data wanted for the recipe
  "output": {
    // Some stack output
  }
}
```

Non-Item Logic
--------------

If items are not used as part of the input or result of a recipe, then the normal methods provided in [`RecipeManager`][manager] will not be useful. Instead, an additional method for testing a recipe's validity and/or supplying the result should be added to the custom `Recipe` instance. From there, all the recipes for that specific `RecipeType` can be obtained via `RecipeManager#getAllRecipesFor` and then checked and/or supplied the result using the newly implemented methods.

```java
// In some Recipe subimplementation ExampleRecipe

// Checks the block at the position to see if it matches the stored data
boolean matches(Level level, BlockPos pos);

// Creates the block state to set the block at the specified position to
BlockState assemble(RegistryAccess access);

// In some manager class
public Optional<ExampleRecipe> getRecipeFor(Level level, BlockPos pos) {
  return level.getRecipeManager()
    .getAllRecipesFor(exampleRecipeType) // Gets all recipes
    .stream() // Looks through all recipes for types
    .filter(recipe -> recipe.matches(level, pos)) // Checks if the recipe inputs are valid
    .findFirst(); // Finds the first recipe whose inputs match
}
```

Data Generation
---------------

All custom recipes, regardless of input or output data, can be created into a `FinishedRecipe` for [data generation][datagen] using the `RecipeProvider`.

[forge]: ../../../concepts/registries.md#methods-for-registering
[json]: https://minecraft.wiki/w/Recipe#JSON_format
[manager]: ./index.md#recipe-manager
[datagen]: ../../../datagen/server/recipes.md#custom-recipe-serializers

---

Non-Datapack Recipes
====================

Not all recipes are simplistic enough or migrated to using data-driven recipes. Some subsystems still need to be patched within the codebase to provide support for adding new recipes.

Brewing Recipes
---------------

Brewing is one of the few recipes that still exist in code. Brewing recipes are added as part of a bootstrap within `PotionBrewing` for their containers, container recipes, and potion mixes. To expand upon the existing system, Forge allows brewing recipes to be added by calling `BrewingRecipeRegistry#addRecipe` in `FMLCommonSetupEvent`.

!!! warning
    `BrewingRecipeRegistry#addRecipe` must be called within the synchronous work queue via `#enqueueWork` as the method is not thread-safe.

The default implementation takes in an input ingredient, a catalyst ingredient, and a stack output for a standard implementation. Additionally, an `IBrewingRecipe` instance can be supplied instead to do the transformations.

### IBrewingRecipe

`IBrewingRecipe` is a pseudo-[`Recipe`][recipe] interface that checks whether the input and catalyst is valid and provides the associated output if so. This is provided through `#isInput`, `#isIngredient`, and `#getOutput` respectively. The output method has access to the input and catalyst stacks to construct the result.

!!! important
    When copying data between `ItemStack`s or `CompoundTag`s, make sure to use their respective `#copy` methods to create unique instances.

There is no wrapper for adding additional potion containers or potion mixes similar to vanilla. A new `IBrewingRecipe` implementation will need to be added to replicate this behavior.

Anvil Recipes
-------------

Anvils are responsible for taking a damaged input and given some material or a similar input, remove some of the damage on the input result. As such, its system is not easily data-driven. However, as anvil recipes are an input with some number of materials equals some output when the user has the required experience levels, it can be modified to create a pseudo-recipe system via `AnvilUpdateEvent`. This takes in the input and materials and allows the modder to specify the output, experience level cost, and number of materials to use for the output. The event can also prevent any output by [canceling][cancel] it.

```java
// Checks whether the left and right items are correct
// When true, sets the output, level experience cost, and material amount
public void updateAnvil(AnvilUpdateEvent event) {
  if (event.getLeft().is(...) && event.getRight().is(...)) {
    event.setOutput(...);
    event.setCost(...);
    event.setMaterialCost(...);
  }
}
```

The update event must be [attached] to the Forge event bus.

Loom Recipes
------------

Looms are responsible for applying a dye and pattern (either from the loom or from an item) to a banner. While the banner and the dye must be a `BannerItem` or `DyeItem` respectively, custom patterns can be created and applied in the loom. Banner Patterns can be created by [registering] a `BannerPattern`.

!!! important
    `BannerPattern`s which are in the `minecraft:no_item_required` tag appear as an option in the loom. Patterns not in this tag must have an accompanying `BannerPatternItem` to be used along with an associated tag.

```java
private static final DeferredRegister<BannerPattern> REGISTER = DeferredRegister.create(Registries.BANNER_PATTERN, "examplemod");

// Takes in the pattern name to send over the network
public static final BannerPattern EXAMPLE_PATTERN = REGISTER.register("example_pattern", () -> new BannerPattern("examplemod:ep"));
```

[recipe]: ./custom.md#recipe
[cancel]: ../../../concepts/events.md#canceling
[attached]: ../../../concepts/events.md#creating-an-event-handler
[registering]: ../../../concepts/registries.md#registries-that-arent-forge-registries

---

Recipes
=======

Recipes are a way to transform some number of objects into other objects within a Minecraft world. Although the vanilla system deals purely with item transformations, the system as a whole can be expanded to use any object the programmer creates.

Data-Driven Recipes
-------------------

Most recipe implementations within vanilla are data driven via JSON. This means that a mod is not necessary to create a new recipe, only a [Data pack][datapack]. A full list on how to create and put these recipes within the mod's `resources` folder can be found on the [Minecraft Wiki][wiki].

A recipe can be obtained within the Recipe Book as a reward for completing an [advancement][advancement]. Recipe advancements always have `minecraft:recipes/root` as their parent, to not to appear on the advancement screen. The default criteria to gain the recipe advancement is a check if the user has unlocked the recipe from using it once or receiving it through a command like `/recipe`:

```js
// Within some recipe advancement json
"has_the_recipe": { // Criteria label
  // Succeeds if examplemod:example_recipe is used
  "trigger": "minecraft:recipe_unlocked",
  "conditions": {
    "recipe": "examplemod:example_recipe"
  }
}
//...
"requirements": [
  [
    "has_the_recipe"
    // ... Other criteria labels to be ORed against to unlock recipe
  ]
]
```

Data-driven recipes and their unlocking advancement can be [generated][datagen] via `RecipeProvider`.

Recipe Manager
--------------

Recipes are loaded and stored via the `RecipeManager`. Any operations relating to getting available recipe(s) are handled by this manager. There are two important methods to know of:

 Method         | Description
 :---:          | :---
`getRecipeFor`  | Gets the first recipe that matches the current input.
`getRecipesFor` | Gets all recipes that match the current input.

Each method takes in a `RecipeType`, which denotes what method is being applied to use the recipe (crafting, smelting, etc.), a `Container` which holds the configuration of the inputs, and the current level which is passed to `Recipe#matches` along with the container.

!!! important
    Forge provides the `RecipeWrapper` utility class which extends `Container` for wrapping around `IItemHandler`s and passing them to methods which requires a `Container` parameter.

    ```java
    // Within some method with IItemHandlerModifiable handler
    recipeManger.getRecipeFor(RecipeType.CRAFTING, new RecipeWrapper(handler), level);
    ```

Additional Features
-------------------

Forge provides some additional behavior to the recipe schema and its implementations for greater control of the system.

### Recipe ItemStack Result

Except for `minecraft:stonecutting` recipes, all vanilla recipe serializers expand the `result` tag to take in a full `ItemStack` as a `JsonObject` instead of just the item name and amount in some cases.

```js
// In some recipe JSON
"result": {
  // The name of the registry item to give as a result
  "item": "examplemod:example_item",
  // The number of items to return
  "count": 4,
  // The tag data of the stack, can also be a string
  "nbt": {
      // Add tag data here
  }
}
```

!!! note
    The `nbt` tag can alternatively be a string containing a stringified NBT (or SNBT) for data which cannot be properly represented as a JSON object (such as `IntArrayTag`s).

### Conditional Recipes

Recipes and their unlocking advancement can be [loaded conditionally and defaulted][conditional] depending on what information is present (mod loaded, item exists, etc.).

### Larger Crafting Grids

By default, vanilla declares a maximum width and height for a crafting grid to be a 3x3 square. This can be expanded by calling `ShapedRecipe#setCraftingSize` with the new width and height in `FMLCommonSetupEvent`.

!!! warning
    `ShapedRecipe#setCraftingSize` is **NOT** thread-safe. As such, it should be enqueued to the synchronous work queue via `FMLCommonSetupEvent#enqueueWork`.

Larger crafting grids in recipes can be [data generated][datagen].

### Ingredient Types

A few additional [ingredient types][ingredients] are added to allow recipes to have inputs which check tag data or combine multiple ingredients into a single input checker.

[datapack]: https://minecraft.wiki/w/Data_pack
[wiki]: https://minecraft.wiki/w/Recipe
[advancement]: ../advancements.md
[datagen]: ../../../datagen/server/recipes.md
[cap]: ../../../datastorage/capabilities.md
[conditional]: ../conditional.md#implementations
[ingredients]: ./ingredients.md#forge-types

---

Ingredients
===========

`Ingredient`s are predicate handlers for item-based inputs which check whether a certain `ItemStack` meets the condition to be a valid input in a recipe. All [vanilla recipes][recipes] that take inputs use an `Ingredient` or a list of `Ingredient`s, which is then merged into a single `Ingredient`.

Custom Ingredients
------------------

Custom ingredients can be specified by setting `type` to the name of the [ingredient's serializer][serializer], with the exception of [compound ingredients][compound]. When no type is specified, `type` defaults to the vanilla ingredient `minecraft:item`. Custom ingredients can also easily be used in [data generation][datagen].

### Forge Types

Forge provides a few additional `Ingredient` types for programmers to implement. 

#### CompoundIngredient

Though they are functionally identical, Compound ingredients replaces the way one would implement a list of ingredients would in a recipe. They work as a set OR where the passed in stack must be within at least one of the supplied ingredients. This change was made to allow custom ingredients to work correctly within lists. As such, **no type** needs to be specified.

```js
// For some input
[
  // At least one of these ingredients must match to succeed
  {
    // Ingredient
  },
  {
    // Custom ingredient
    "type": "examplemod:example_ingredient"
  }
]
```

#### StrictNBTIngredient

`StrictNBTIngredient`s compare the item, damage, and the share tags (as defined by `IForgeItem#getShareTag`) on an `ItemStack` for exact equivalency. This can be used by specifying the `type` as `forge:nbt`.

```js
// For some input
{
  "type": "forge:nbt",
  "item": "examplemod:example_item",
  "nbt": {
    // Add nbt data (must match exactly what is on the stack)
  }
}
```

### PartialNBTIngredient

`PartialNBTIngredient`s are a looser version of [`StrictNBTIngredient`][nbt] as they compare against a single or set of items and only keys specified within the share tag (as defined by `IForgeItem#getShareTag`). This can be used by specifying the `type` as `forge:partial_nbt`.

```js
// For some input
{
  "type": "forge:partial_nbt",

  // Either 'item' or 'items' must be specified
  // If both are specified, only 'item' will be read
  "item": "examplemod:example_item",
  "items": [
    "examplemod:example_item",
    "examplemod:example_item2"
    // ...
  ],

  "nbt": {
    // Checks only for equivalency on 'key1' and 'key2'
    // All other keys in the stack will not be checked
    "key1": "data1",
    "key2": {
      // Data 2
    }
  }
}
```

### IntersectionIngredient

`IntersectionIngredient`s work as a set AND where the passed in stack must match all supplied ingredients. There must be at least two ingredients supplied to this. This can be used by specifying the `type` as `forge:intersection`.

```js
// For some input
{
  "type": "forge:intersection",

  // All of these ingredients must return true to succeed
  "children": [
    {
      // Ingredient 1
    },
    {
      // Ingredient 2
    }
    // ...
  ]
}
```

### DifferenceIngredient

`DifferenceIngredient`s work as a set subtraction (SUB) where the passed in stack must match the first ingredient but must not match the second ingredient. This can be used by specifying the `type` as `forge:difference`.

```js
// For some input
{
  "type": "forge:difference",
  "base": {
    // Ingredient the stack is in
  },
  "subtracted": {
    // Ingredient the stack is NOT in
  }
}
```

Creating Custom Ingredients
---------------------------

Custom ingredients can be created by implementing `IIngredientSerializer` for the created `Ingredient` subclass.

!!! tip
    Custom ingredients should subclass `AbstractIngredient` as it provides some useful abstractions for ease of implementation.

### Ingredient Subclass

There are three important methods to implement for each ingredient subclass:

 Method       | Description
 :---:        | :---
getSerializer | Returns the [serializer] used to read and write the ingredient.
test          | Returns true if the input is valid for this ingredient.
isSimple      | Returns false if the ingredient matches on the stack's tag. `AbstractIngredient` subclasses will need to define this behavior, while `Ingredient` subclasses return `true` by default.

All other defined methods are left as an exercise to the reader to use as required for the ingredient subclass.

### IIngredientSerializer

`IIngredientSerializer` subtypes must implement three methods:

 Method         | Description
 :---:          | :---
parse (JSON)    | Converts a `JsonObject` to an `Ingredient`.
parse (Network) | Reads the network buffer to decode an `Ingredient`.
write           | Writes an `Ingredient` to the network buffer.

Additionally, `Ingredient` subclasses should implement `Ingredient#toJson` for use with [data generation][datagen]. `AbstractIngredient` subclasses make `#toJson` an abstract method requiring the method to be implemented.

Afterwards, a static instance should be declared to hold the initialized serializer and then registered using `CraftingHelper#register` either during the `RegisterEvent` for `RecipeSerializer`s or during `FMLCommonSetupEvent`. The `Ingredient` subclass return the static instance of the serializer in `Ingredient#getSerializer`.

```java
// In some serializer class
public static final ExampleIngredientSerializer INSTANCE = new ExampleIngredientSerializer();

// In some handler class
public void registerSerializers(RegisterEvent event) {
  event.register(ForgeRegistries.Keys.RECIPE_SERIALIZERS,
    helper -> CraftingHelper.register(registryName, INSTANCE)
  );
}

// In some ingredient subclass
@Override
public IIngredientSerializer<? extends Ingredient> getSerializer() {
  return INSTANCE;
}
```

!!! tip
    If using `FMLCommonSetupEvent` to register an ingredient serializer, it must be enqueued to the synchronous work queue via `FMLCommonSetupEvent#enqueueWork` as `CraftingHelper#register` is not thread-safe.

[recipes]: https://minecraft.wiki/w/Recipe#List_of_recipe_types
[nbt]: #strictnbtingredient
[serializer]: #iingredientserializer
[compound]: #compoundingredient
[datagen]: ../../../datagen/server/recipes.md

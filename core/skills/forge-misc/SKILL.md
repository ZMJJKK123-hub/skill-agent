---
name: forge-misc
description: 'Forge miscellaneous features: configuration (ForgeConfigSpec), key mappings, game tests, update checker and debug profiler.'
---

Configuration
=============

Configurations define settings and consumer preferences that can be applied to a mod instance. Forge uses a configuration system using [TOML][toml] files and read with [NightConfig][nightconfig].

Creating a Configuration
------------------------

A configuration can be created using a subtype of `IConfigSpec`. Forge implements the type via `ForgeConfigSpec` and enables its construction through `ForgeConfigSpec$Builder`. The builder can separate the config values into sections via `Builder#push` to create a section and `Builder#pop` to leave a section. Afterwards, the configuration can be built using one of two methods:

 Method     | Description
 :---       | :---
`build`     | Creates the `ForgeConfigSpec`.
`configure` | Creates a pair of the class holding the config values and the `ForgeConfigSpec`.

!!! note
    `ForgeConfigSpec$Builder#configure` is typically used with a `static` block and a class that takes in `ForgeConfigSpec$Builder` as part of its constructor to attach and hold the values:

    ```java
    // In some config class
    ExampleConfig(ForgeConfigSpec.Builder builder) {
      // Define values here in final fields
    }

    // Somewhere the constructor is accessible
    static {
      Pair<ExampleConfig, ForgeConfigSpec> pair = new ForgeConfigSpec.Builder()
        .configure(ExampleConfig::new);
      // Store pair values in some constant field
    }
    ```

Each config value can be supplied with additional context to provide additional behavior. Contexts must be defined before the config value is fully built:

Method       | Description
:---         | :---
`comment`      | Provides a description of what the config value does. Can provide multiple strings for a multiline comment.
`translation`  | Provides a translation key for the name of the config value.
`worldRestart` | The world must be restarted before the config value can be changed.

### ConfigValue

Config values can be built with the provided contexts (if defined) using any of the `#define` methods.

All config value methods take in at least two components:

* A path representing the name of the variable: a `.` separated string representing the sections the config value is in
* The default value when no valid configuration is present

The `ConfigValue` specific methods take in two additional components:

* A validator to make sure the deserialized object is valid
* A class representing the data type of the config value

```java
// For some ForgeConfigSpec$Builder builder
ConfigValue<T> value = builder.comment("Comment")
  .define("config_value_name", defaultValue);
```

The values themselves can be obtained using `ConfigValue#get`. The values are additionally cached to prevent multiple readings from files.

#### Additional Config Value Types

* **Range Values**
    * Description: Value must be between the defined bounds
    * Class Type: `Comparable<T>`
    * Method Name: `#defineInRange`
    * Additional Components:
      * The minimum and maximum the config value may be
      * A class representing the data type of the config value

!!! note
    `FloatValue`s, `DoubleValue`s, `ByteValue`s, `ShortValue`s, `IntValue`s, and `LongValue`s are range values which specify the class as `Float`, `Double`, `Byte`, `Short`, `Integer`, and `Long` respectively.

* **Whitelisted Values**
    * Description: Value must be in supplied collection
    * Class Type: `T`
    * Method Name: `#defineInList`
    * Additional Components:
      * A collection of the allowed values the configuration can be

* **List Values**
    * Description: Value is a list of entries
    * Class Type: `List<T>`
    * Method Name: `#defineList`, `#defineListAllowEmpty` if list can be empty
    * Additional Components:
      * A validator to make sure a deserialized element from the list is valid

* **Enum Values**
    * Description: An enum value in the supplied collection
    * Class Type: `Enum<T>`
    * Method Name: `#defineEnum`
    * Additional Components:
      * A getter to convert a string or integer into an enum
      * A collection of the allowed values the configuration can be

* **Boolean Values**
    * Description: A `boolean` value
    * Class Type: `Boolean`
    * Method Name: `#define`

Registering a Configuration
---------------------------

Once a `ForgeConfigSpec` has been built, it must be registered to allow Forge to load, track, and sync the configuration settings as required. Configurations should be registered in the mod constructor via `ModLoadingContext#registerConfig`. A configuration can be registered with a given type representing the side the config belongs to, the `ForgeConfigSpec`, and optionally a specific file name for the configuration.

```java
// In the mod constructor with a ForgeConfigSpec CONFIG and FMLJavaModLoadingContext context
context.registerConfig(Type.COMMON, CONFIG);
```

Here is a list of the available configuration types:

Type   | Loaded           | Synced to Client | Client Location                              | Server Location                      | Default File Suffix
:---:  | :---:            | :---:            | :---:                                        | :---:                                | :---
CLIENT | Client Side Only | No               | `.minecraft/config`                          | N/A                                  | `-client`
COMMON | On Both Sides    | No               | `.minecraft/config`                          | `<server_folder>/config`             | `-common`
SERVER | Server Side Only | Yes              | `.minecraft/saves/<level_name>/serverconfig` | `<server_folder>/world/serverconfig` | `-server`

!!! tip
    Forge documents the [config types][type] within their codebase.

Configuration Events
--------------------

Operations that occur whenever a config is loaded or reloaded can be done using the `ModConfigEvent$Loading` and `ModConfigEvent$Reloading` events. The events must be [registered][events] to the mod event bus.

!!! warning
    These events are called for all configurations for the mod; the `ModConfig` object provided should be used to denote which configuration is being loaded or reloaded.

[toml]: https://toml.io/
[nightconfig]: https://github.com/TheElectronWill/night-config
[type]: https://github.com/MinecraftForge/MinecraftForge/blob/c3e0b071a268b02537f9d79ef8e7cd9b100db416/fmlcore/src/main/java/net/minecraftforge/fml/config/ModConfig.java#L108-L136
[events]: ../concepts/events.md#creating-an-event-handler

---

# Debug Profiler

Minecraft provides a Debug Profiler that provides system data, current game settings, JVM data, level data, and sided tick information to find time consuming code. Considering things like `TickEvent`s and ticking `BlockEntities`, this can be very useful for modders and server owners that want to find a lag source.

## Using the Debug Profiler

The Debug Profiler is very simple to use. It requires the debug keybind `F3 + L` to start the profiler. After 10 seconds, it will automatically stop; however, it can be stopped earlier by pressing the keybind again.

!!! note
    Naturally, you can only profile code paths that are actually being reached. `Entities` and `BlockEntities` that you want to profile must exist in the level to show up in the results.

After you have stopped the debugger, it will create a new zip within the `debug/profiling` subdirectory in your run directory.
The file name will be formatted with the date and time as `yyyy-mm-dd_hh_mi_ss-WorldName-VersionNumber.zip`

## Reading a Profiling result

Within each sided folder (`client` and `server`), you will find a `profiling.txt` file containing the result data. At the top, it first tells you how long in milliseconds it was running and how many ticks ran in that time.

Below that, you will find information similar to the snippet below:
```
[00] levels - 96.70%/96.70%
[01] |   Level Name - 99.76%/96.47%
[02] |   |   tick - 99.31%/95.81%
[03] |   |   |   entities - 47.72%/45.72%
[04] |   |   |   |   regular - 98.32%/44.95%
[04] |   |   |   |   blockEntities - 0.90%/0.41%
[05] |   |   |   |   |   unspecified - 64.26%/0.26%
[05] |   |   |   |   |   minecraft:furnace - 33.35%/0.14%
[05] |   |   |   |   |   minecraft:chest - 2.39%/0.01%
```
Here is a small explanation of what each part means

| [02]                     | tick                  | 99.31%       | 95.81%       |
| :----------------------- | :---------------------- | :----------- | :----------- |
| The Depth of the section | The Name of the Section | The percentage of time it took in relation to it's parent. For Layer 0, it is the percentage of the time a tick takes. For Layer 1, it is the percentage of the time its parent takes. | The second percentage tells you how much time it took from the entire tick.

## Profiling your own code

The Debug Profiler has basic support for `Entity` and `BlockEntity`. If you would like to profile something else, you may need to manually create your sections like so:
```java
ProfilerFiller#push(yourSectionName : String);
//The code you want to profile
ProfilerFiller#pop();
```
You can obtain the `ProfilerFiller` instance from a `Level`, `MinecraftServer`, or `Minecraft` instance.
Now you just need to search the results file for your section name.

---

Game Tests
==========

Game Tests are a way to run in-game unit tests. The system was designed to be scalable and in parallel to run large numbers of different tests efficiently. Testing object interactions and behaviors are simply a few of the many applications of this framework.

Creating a Game Test
--------------------

A standard Game Test follows three basic steps:

1. A structure, or template, is loaded holding the scene on which the interaction or behavior is tested.
1. A method conducts the logic to perform on the scene.
1. The method logic executes. If a successful state is reached, then the test succeeds. Otherwise, the test fails and the result is stored within a lectern adjacent to the scene.

As such, to create a Game Test, there must be an existing template holding the initial start state of the scene and a method which provides the logic of execution.

### The Test Method

A Game Test method is a `Consumer<GameTestHelper>` reference, meaning it takes in a `GameTestHelper` and returns nothing. For a Game Test method to be recognized, it must have a `@GameTest` annotation:

```java
public class ExampleGameTests {
  @GameTest
  public static void exampleTest(GameTestHelper helper) {
    // Do stuff
  }
}
```

The `@GameTest` annotation also contains members which configure how the game test should run.

```java
// In some class
@GameTest(
  setupTicks = 20L, // The test spends 20 ticks to set up for execution
  required = false // The failure is logged but does not affect the execution of the batch
)
public static void exampleConfiguredTest(GameTestHelper helper) {
  // Do stuff
}
```

#### Relative Positioning

All `GameTestHelper` methods translate relative coordinates within the structure template scene to its absolute coordinates using the structure block's current location. To allow for easy conversion between relative and absolute positioning, `GameTestHelper#absolutePos` and `GameTestHelper#relativePos` can be used respectively.

The relative position of a structure template can be obtained in-game by loading the structure via the [test command][test], placing the player at the wanted location, and finally running the `/test pos` command. This will grab the coordinates of the player relative to the closest structure within 200 blocks of the player. The command will export the relative position as a copyable text component in the chat to be used as a final local variable.

!!! tip
    The local variable generated by `/test pos` can specify its reference name by appending it to the end of the command:

    ```bash
    /test pos <var> # Exports 'final BlockPos <var> = new BlockPos(...);'
    ```

#### Successful Completion

A Game Test method is responsible for one thing: marking the test was successful on a valid completion. If no success state was achieved before the timeout is reached (as defined by `GameTest#timeoutTicks`), then the test automatically fails.

There are many abstracted methods within `GameTestHelper` which can be used to define a successful state; however, four are extremely important to be aware of.

Method               | Description
:---:                | :---
`#succeed`           | The test is marked as successful.
`#succeedIf`         | The supplied `Runnable` is tested immediately and succeeds if no `GameTestAssertException` is thrown. If the test does not succeed on the immediate tick, then it is marked as a failure.
`#succeedWhen`       | The supplied `Runnable` is tested every tick until timeout and succeeds if the check on one of the ticks does not throw a `GameTestAssertException`.
`#succeedOnTickWhen` | The supplied `Runnable` is tested on the specified tick and will succeed if no `GameTestAssertException` is thrown. If the `Runnable` succeeds on any other tick, then it is marked as a failure.

!!! important
    Game Tests are executed every tick until the test is marked as a success. As such, methods which schedule success on a given tick must be careful to always fail on any previous tick.

#### Scheduling Actions

Not all actions will occur when a test begins. Actions can be scheduled to occur at specific times or intervals:

Method           | Description
:---:            | :---
`#runAtTickTime` | The action is ran on the specified tick.
`#runAfterDelay` | The action is ran `x` ticks after the current tick.
`#onEachTick`    | The action is ran every tick.

#### Assertions

At any time during a Game Test, an assertion can be made to check if a given condition is true. There are numerous assertion methods within `GameTestHelper`; however, it simplifies to throwing a `GameTestAssertException` whenever the appropriate state is not met.

### Generated Test Methods

If Game Test methods need to be generated dynamically, a test method generator can be created. These methods take in no parameters and return a collection of `TestFunction`s. For a test method generator to be recognized, it must have a `@GameTestGenerator` annotation:

```java
public class ExampleGameTests {
  @GameTestGenerator
  public static Collection<TestFunction> exampleTests() {
    // Return a collection of TestFunctions
  }
}
```

#### TestFunction

A `TestFunction` is the boxed information held by the `@GameTest` annotation and the method running the test.

!!! tip
    Any methods annotated using `@GameTest` are translated into a `TestFunction` using `GameTestRegistry#turnMethodIntoTestFunction`. That method can be used as a reference for creating `TestFunction`s without the use of the annotation.

### Batching

Game Tests can be executed in batches instead of registration order. A test can be added to a batch by having the same supplied `GameTest#batch` string.

On its own, batching does not provide anything useful. However, batching can be used to perform setup and teardown states on the current level the tests are running in. This is done by annotating a method with either `@BeforeBatch` for setup or `@AfterBatch` for takedown. The `#batch` methods must match the string supplied to the game test.

Batch methods are `Consumer<ServerLevel>` references, meaning they take in a `ServerLevel` and return nothing:

```java
public class ExampleGameTests {
  @BeforeBatch(batch = "firstBatch")
  public static void beforeTest(ServerLevel level) {
    // Perform setup
  }

  @GameTest(batch = "firstBatch")
  public static void exampleTest2(GameTestHelper helper) {
    // Do stuff
  }
}
```

Registering a Game Test
-----------------------

A Game Test must be registered to be ran in-game. There are two methods of doing so: via the `@GameTestHolder` annotation or `RegisterGameTestsEvent`. Both registration methods still require the test methods to be annotated with either `@GameTest`, `@GameTestGenerator`, `@BeforeBatch`, or `@AfterBatch`.

### GameTestHolder

The `@GameTestHolder` annotation registers any test methods within the type (class, interface, enum, or record). `@GameTestHolder` contains a single method which has multiple uses. In this instance, the supplied `#value` must be the mod id of the mod; otherwise, the test will not run under default configurations.

```java
@GameTestHolder(MODID)
public class ExampleGameTests {
  // ...
}
```

### RegisterGameTestsEvent

`RegisterGameTestsEvent` can also register either classes or methods using `#register`. The event listener must be [added][event] to the mod event bus. Test methods registered this way must supply their mod id to `GameTest#templateNamespace` on every method annotated with `@GameTest`.

```java
// In some class
public void registerTests(RegisterGameTestsEvent event) {
  event.register(ExampleGameTests.class);
}

// In ExampleGameTests
@GameTest(templateNamespace = MODID)
public static void exampleTest3(GameTestHelper helper) {
  // Perform setup
}
```

!!! note
    The value supplied to `GameTestHolder#value` and `GameTest#templateNamespace` can be different from the current mod id. The configuration within the [buildscript][namespaces] would need to be changed.

Structure Templates
-------------------

Game Tests are performed within scenes loaded by structures, or templates. All templates define the dimensions of the scene and the initial data (blocks and entities) that will be loaded. The template must be stored as an `.nbt` file within `data/<namespace>/structures`.

!!! tip
    A structure template can be created and saved using a structure block.

The location of the template is specified by a few factors:

* If the namespace of the template is specified.
* If the class should be prepended to the name of the template.
* If the name of the template is specified.

The namespace of the template is determined by `GameTest#templateNamespace`, then `GameTestHolder#value` if not specified, then `minecraft` if neither is specified.

The simple class name is not prepended to the name of the template if the `@PrefixGameTestTemplate` is applied to a class or method with the test annotations and set to `false`. Otherwise, the simple class name is made lowercase and prepended and followed by a dot before the template name.

The name of the template is determined by `GameTest#template`. If not specified, then the lowercase name of the method is used instead.

```java
// Modid for all structures will be MODID
@GameTestHolder(MODID)
public class ExampleGameTests {

  // Class name is prepended, template name is not specified
  // Template Location at 'modid:examplegametests.exampletest'
  @GameTest
  public static void exampleTest(GameTestHelper helper) { /*...*/ }

  // Class name is not prepended, template name is not specified
  // Template Location at 'modid:exampletest2'
  @PrefixGameTestTemplate(false)
  @GameTest
  public static void exampleTest2(GameTestHelper helper) { /*...*/ }

  // Class name is prepended, template name is specified
  // Template Location at 'modid:examplegametests.test_template'
  @GameTest(template = "test_template")
  public static void exampleTest3(GameTestHelper helper) { /*...*/ }

  // Class name is not prepended, template name is specified
  // Template Location at 'modid:test_template2'
  @PrefixGameTestTemplate(false)
  @GameTest(template = "test_template2")
  public static void exampleTest4(GameTestHelper helper) { /*...*/ }
}
```

Running Game Tests
------------------

Game Tests can be run using the `/test` command. The `test` command is highly configurable; however, only a few are of importance to running tests:

Subcommand  | Description
:---:       | :---
`run`       | Runs the specified test: `run <test_name>`.
`runall`    | Runs all available tests.
`runthis`   | Runs the nearest test to the player within 15 blocks.
`runthese`  | Runs tests within 200 blocks of the player.
`runfailed` | Runs all tests that failed in the previous run.

!!! note
    Subcommands follow the test command: `/test <subcommand>`.

Buildscript Configurations
--------------------------

Game Tests provide additional configuration settings within a buildscript (the `build.gradle` file) to run and integrate into different settings.

### Enabling Other Namespaces

If the buildscript was [setup as recommended][buildscript], then only Game Tests under the current mod id would be enabled. To enable other namespaces to load Game Tests from, a run configuration must set the property `forge.enabledGameTestNamespaces` to a string specifying each namespace separated by a comma. If the property is empty or not set, then all namespaces will be loaded.

```gradle
// Inside a run configuration
property 'forge.enabledGameTestNamespaces', 'modid1,modid2,modid3'
```

!!! warning
    There must be no spaces in-between namespaces; otherwise, the namespace will not be loaded correctly.

### Game Test Server Run Configuration

The Game Test Server is a special configuration which runs a build server. The build server returns an exit code of the number of required, failed Game Tests. All failed tests, whether required or optional, are logged. This server can be run using `gradlew runGameTestServer`.

### Enabling Game Tests in Other Run Configurations

By default, only the `client`, `server`, and `gameTestServer` run configurations have Game Tests enabled. If another run configuration should run Game Tests, then the `forge.enableGameTest` property must be set to `true`.

```gradle
// Inside a run configuration
property 'forge.enableGameTest', 'true'
```

[test]: #running-game-tests
[namespaces]: #enabling-other-namespaces
[event]: ../concepts/events.md#creating-an-event-handler
[buildscript]: ../gettingstarted/index.md#simple-buildgradle-customizations

---

# Key Mappings

A key mapping, or key binding, defines a particular action that should be tied to an input: mouse click, key press, etc. Each action defined by a key mapping can be checked whenever the client can take an input. Furthermore, each key mapping can be assigned to any input through the [Controls option menu][controls].

## Registering a `KeyMapping`

A `KeyMapping` can be registered by listening to the `RegisterKeyMappingsEvent` on the [**mod event bus**][modbus] only on the physical client and calling `#register`.

```java
// In some physical client only class

// Key mapping is lazily initialized so it doesn't exist until it is registered
public static final Lazy<KeyMapping> EXAMPLE_MAPPING = Lazy.of(() -> /*...*/);

// Event is on the mod event bus only on the physical client
@SubscribeEvent
public void registerBindings(RegisterKeyMappingsEvent event) {
  event.register(EXAMPLE_MAPPING.get());
}
```

## Creating a `KeyMapping`

A `KeyMapping` can be created using it's constructor. The `KeyMapping` takes in a [translation key][tk] defining the name of the mapping, the default input of the mapping, and the [translation key][tk] defining the category the mapping will be put within in the [Controls option menu][controls].

!!! tip
    A `KeyMapping` can be added to a custom category by providing a category [translation key][tk] not provided by vanilla. Custom category translation keys should contain the mod id (e.g. `key.categories.examplemod.examplecategory`).

### Default Inputs

Each key mapping has a default input associated with it. This is provided through `InputConstants$Key`. Each input consists of an `InputConstants$Type`, which defines what device is providing the input, and an integer, which defines the associated identifier of the input on the device.

Vanilla provides three types of inputs: `KEYSYM`, which defines a keyboard through the provided `GLFW` key tokens, `SCANCODE`, which defines a keyboard through the platform-specific scancode, and `MOUSE`, which defines a mouse.

!!! note
    It is highly recommended to use `KEYSYM` over `SCANCODE` for keyboards as `GLFW` key tokens are not tied to any particular system. You can read more on the [GLFW docs][keyinput].

The integer is dependent on the type provided. All input codes are defined in `GLFW`: `KEYSYM` tokens are prefixed with `GLFW_KEY_*` while `MOUSE` codes are prefixed with `GLFW_MOUSE_*`.

```java
new KeyMapping(
  "key.examplemod.example1", // Will be localized using this translation key
  InputConstants.Type.KEYSYM, // Default mapping is on the keyboard
  GLFW.GLFW_KEY_P, // Default key is P
  "key.categories.misc" // Mapping will be in the misc category
)
```

!!! note
    If the key mapping should not be mapped to a default, the input should be set to `InputConstants#UNKNOWN`. The vanilla constructor will require you to extract the input code via `InputConstants$Key#getValue` while the Forge constructor can be supplied the raw input field.

### `IKeyConflictContext`

Not all mappings are used in every context. Some mappings are only used in a GUI, while others are only used purely in game. To avoid mappings of the same key used in different contexts conflicting with each other, an `IKeyConflictContext` can be assigned.

Each conflict context contains two methods: `#isActive`, which defines if the mapping can be used in the current game state, and `#conflicts`, which defines whether the mapping conflicts with a key in the same or different conflict context.

Currently, Forge defines three basic contexts through `KeyConflictContext`: `UNIVERSAL`, which is the default meaning the key can be used in every context, `GUI`, which means the mapping can only be used when a `Screen` is open, and `IN_GAME`, which means the mapping can only be used if a `Screen` is not open. New conflict contexts can be created by implementing `IKeyConflictContext`.

```java
new KeyMapping(
  "key.examplemod.example2",
  KeyConflictContext.GUI, // Mapping can only be used when a screen is open
  InputConstants.Type.MOUSE, // Default mapping is on the mouse
  GLFW.GLFW_MOUSE_BUTTON_LEFT, // Default mouse input is the left mouse button
  "key.categories.examplemod.examplecategory" // Mapping will be in the new example category
)
```

### `KeyModifier`

Modders may not want mappings to have the same behavior if a modifier key is held at the same (e.g. `G` vs `CTRL + G`). To remedy this, Forge adds an additional parameter to the constructor to take in a `KeyModifier` which can apply control (`KeyModifier#CONTROL`), shift (`KeyModifier#SHIFT`), or alt (`KeyModifier#ALT`) to any input. `KeyModifier#NONE` is the default and will apply no modifier.

A modifier can be added in the [controls option menu][controls] by holding down the modifier key and the associated input.

```java
new KeyMapping(
  "key.examplemod.example3",
  KeyConflictContext.UNIVERSAL,
  KeyModifier.SHIFT, // Default mapping requires shift to be held down
  InputConstants.Type.KEYSYM, // Default mapping is on the keyboard
  GLFW.GLFW_KEY_G, // Default key is G
  "key.categories.misc"
)
```

## Checking a `KeyMapping`

A `KeyMapping` can be checked to see whether it has been clicked. Depending on when, the mapping can be used in a conditional to apply the associated logic.

### Within the Game

Within the game, a mapping should be checked by listening to `ClientTickEvent` on the [**Forge event bus**][forgebus] and checking `KeyMapping#consumeClick` within a while loop. `#consumeClick` will return `true` only the number of times the input was performed and not already previously handled, so it won't infinitely stall the game.

```java
// Event is on the Forge event bus only on the physical client
public void onClientTick(ClientTickEvent event) {
  if (event.phase == TickEvent.Phase.END) { // Only call code once as the tick event is called twice every tick
    while (EXAMPLE_MAPPING.get().consumeClick()) {
      // Execute logic to perform on click here
    }
  }
}
```

!!! warning
    Do not use the `InputEvent`s as an alternative to `ClientTickEvent`. There are separate events for keyboard and mouse inputs only, so they wouldn't handle any additional inputs.

### Inside a GUI

Within a GUI, a mapping can be checked within one of the `GuiEventListener` methods using `IForgeKeyMapping#isActiveAndMatches`. The most common methods which can be checked are `#keyPressed` and `#mouseClicked`. 

`#keyPressed` takes in the `GLFW` key token, the platform-specific scan code, and a bitfield of the held down modifiers. A key can be checked against a mapping by creating the input using `InputConstants#getKey`. The modifiers are already checked within the mapping methods itself.

```java
// In some Screen subclass
@Override
public boolean keyPressed(int key, int scancode, int mods) {
  if (EXAMPLE_MAPPING.get().isActiveAndMatches(InputConstants.getKey(key, scancode))) {
    // Execute logic to perform on key press here
    return true;
  }
  return super.keyPressed(x, y, button);
} 
```

!!! note
    If you do not own the screen which you are trying to check a **key** for, you can listen to the `Pre` or `Post` events of `ScreenEvent$KeyPressed` on the [**Forge event bus**][forgebus] instead.

`#mouseClicked` takes in the mouse's x position, y position, and the button clicked. A mouse button can be checked against a mapping by creating the input using `InputConstants$Type#getOrCreate` with the `MOUSE` input.

```java
// In some Screen subclass
@Override
public boolean mouseClicked(double x, double y, int button) {
  if (EXAMPLE_MAPPING.get().isActiveAndMatches(InputConstants.TYPE.MOUSE.getOrCreate(button))) {
    // Execute logic to perform on mouse click here
    return true;
  }
  return super.mouseClicked(x, y, button);
} 
```

!!! note
    If you do not own the screen which you are trying to check a **mouse** for, you can listen to the `Pre` or `Post` events of `ScreenEvent$MouseButtonPressed` on the [**Forge event bus**][forgebus] instead.

[modbus]: ../concepts/events.md#mod-event-bus
[controls]: https://minecraft.wiki/w/Options#Controls
[tk]: ../concepts/internationalization.md#translatablecontents
[keyinput]: https://www.glfw.org/docs/3.3/input_guide.html#input_key
[forgebus]: ../concepts/events.md#creating-an-event-handler

---

Forge Update Checker
====================

Forge provides a very lightweight, opt-in, update-checking framework. If any mods have an available update, it will show a flashing icon on the 'Mods' button of the main menu and mod list along with the respective changelogs. It *does not* download updates automatically.

Getting Started
---------------

The first thing you want to do is specify the `updateJSONURL` parameter in your `mods.toml` file. The value of this parameter should be a valid URL pointing to an update JSON file. This file can be hosted on your own web server, GitHub, or wherever you want as long as it can be reliably reached by all users of your mod.

Update JSON format
------------------

The JSON itself has a relatively simple format as follows:

```js
{
  "homepage": "<homepage/download page for your mod>",
  "<mcversion>": {
    "<modversion>": "<changelog for this version>", 
    // List all versions of your mod for the given Minecraft version, along with their changelogs
    // ...
  },
  "promos": {
    "<mcversion>-latest": "<modversion>",
    // Declare the latest "bleeding-edge" version of your mod for the given Minecraft version
    "<mcversion>-recommended": "<modversion>",
    // Declare the latest "stable" version of your mod for the given Minecraft version
    // ...
  }
}
```

This is fairly self-explanatory, but some notes:
 
* The link under `homepage` is the link the user will be shown when the mod is outdated.
* Forge uses an internal algorithm to determine whether one version string of your mod is "newer" than another. Most versioning schemes should be compatible, but see the `ComparableVersion` class if you are concerned about whether your scheme is supported. Adherence to [Maven versioning][mvnver] is highly recommended.
* The changelog string can be separated into lines using `\n`. Some prefer to include a abbreviated changelog, then link to an external site that provides a full listing of changes.
* Manually inputting data can be chore. You can configure your `build.gradle` to automatically update this file when building a release as Groovy has native JSON parsing support. Doing this is left as an exercise to the reader.

- Some examples can be found here for [nocubes][], [Forge][forge] and [Corail Tombstone][corail].

Retrieving Update Check Results
-------------------------------

You can retrieve the results of the Forge Update Checker using `VersionChecker#getResult(IModInfo)`. You can obtain your `IModInfo` via `ModContainer#getModInfo`. You can get your `ModContainer` using `ModLoadingContext.get().getActiveContainer()` inside your constructor, `ModList.get().getModContainerById(<your modId>)`, or `ModList.get().getModContainerByObject(<your mod instance>)`. You can obtain any other mod's `ModContainer` using `ModList.get().getModContainerById(<modId>)`. The returned object has a method `#status` which indicates the status of the version check.

|          Status | Description |
|----------------:|:------------|
|        `FAILED` | The version checker could not connect to the URL provided. |
|    `UP_TO_DATE` | The current version is equal to the recommended version. |
|         `AHEAD` | The current version is newer than the recommended version if there is not latest version. |
|      `OUTDATED` | There is a new recommended or latest version. |
| `BETA_OUTDATED` | There is a new latest version. |
|          `BETA` | The current version is equal to or newer than the latest version. |
|       `PENDING` | The result requested has not finished yet, so you should try again in a little bit. |

The returned object will also have the target version and any changelog lines as specified in `update.json`.

[mvnver]: ../gettingstarted/versioning.md
[nocubes]: https://cadiboo.github.io/projects/nocubes/update.json
[forge]: https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json
[corail]: https://github.com/Corail31/tombstone_lite/blob/master/update.json

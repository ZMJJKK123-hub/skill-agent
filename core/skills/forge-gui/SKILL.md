---

name: forge-gui
description: "Forge GUI guide: menus (MenuType, AbstractContainerMenu), screens and HUD, data synchronization."
whenToUse: "Use when implementing containers/menus, screens, or HUD elements."

---

# Menus

Menus are one type of backend for Graphical User Interfaces, or GUIs; they handle the logic involved in interacting with some represented data holder. Menus themselves are not data holders. They are views which allow to user to indirectly modify the internal data holder state. As such, a data holder should not be directly coupled to any menu, instead passing in the data references to invoke and modify.

## `MenuType`

Menus are created and removed dynamically and as such are not registry objects. As such, another factory object is registered instead to easily create and refer to the *type* of the menu. For a menu, these are `MenuType`s.

`MenuType`s must be [registered].

### `MenuSupplier`

A `MenuType` is created by passing in a `MenuSupplier` and a `FeatureFlagSet` to its constructor. A `MenuSupplier` represents a function which takes in the id of the container and the inventory of the player viewing the menu, and returns a newly created [`AbstractContainerMenu`][acm].

```java
// For some DeferredRegister<MenuType<?>> REGISTER
public static final RegistryObject<MenuType<MyMenu>> MY_MENU = REGISTER.register("my_menu", () -> new MenuType(MyMenu::new, FeatureFlags.DEFAULT_FLAGS));

// In MyMenu, an AbstractContainerMenu subclass
public MyMenu(int containerId, Inventory playerInv) {
  super(MY_MENU.get(), containerId);
  // ...
}
```

!!! note
    The container identifier is unique for an individual player. This means that the same container id on two different players will represent two different menus, even if they are viewing the same data holder.

The `MenuSupplier` is usually responsible for creating a menu on the client with dummy data references used to store and interact with the synced information from the server data holder.

### `IContainerFactory`

If additional information is needed on the client (e.g. the position of the data holder in the world), then the subclass `IContainerFactory` can be used instead. In addition to the container id and the player inventory, this also provides a `FriendlyByteBuf` which can store additional information that was sent from the server. A `MenuType` can be created using an `IContainerFactory` via `IForgeMenuType#create`.

```java
// For some DeferredRegister<MenuType<?>> REGISTER
public static final RegistryObject<MenuType<MyMenuExtra>> MY_MENU_EXTRA = REGISTER.register("my_menu_extra", () -> IForgeMenuType.create(MyMenu::new));

// In MyMenuExtra, an AbstractContainerMenu subclass
public MyMenuExtra(int containerId, Inventory playerInv, FriendlyByteBuf extraData) {
  super(MY_MENU_EXTRA.get(), containerId);
  // Store extra data from buffer
  // ...
}
```

## `AbstractContainerMenu`

All menus are extended from `AbstractContainerMenu`. A menu takes in two parameters, the [`MenuType`][mt], which represents the type of the menu itself, and the container id, which represents the unique identifier of the menu for the current accessor.

!!! important
    The player can only have 100 unique menus open at once.

Each menu should contain two constructors: one used to initialize the menu on the server and one used to initialize the menu on the client. The constructor used to initialize the menu on the client is the one supplied to the `MenuType`. Any fields that the server menu constructor contains should have some default for the client menu constructor.

```java
// Client menu constructor
public MyMenu(int containerId, Inventory playerInventory) {
  this(containerId, playerInventory);
}

// Server menu constructor
public MyMenu(int containerId, Inventory playerInventory) {
  // ...
}
```

Each menu implementation must implement two methods: `#stillValid` and [`#quickMoveStack`][qms].

### `#stillValid` and `ContainerLevelAccess`

`#stillValid` determines whether the menu should remain open for a given player. This is typically directed to the static `#stillValid` which takes in a `ContainerLevelAccess`, the player, and the `Block` this menu is attached to. The client menu must always return `true` for this method, which the static `#stillValid` does default to. This implementation checks whether the player is within eight blocks of where the data storage object is located.

A `ContainerLevelAccess` supplies the current level and location of the block within an enclosed scope. When constructing the menu on the server, a new access can be created by calling `ContainerLevelAccess#create`. The client menu constructor can pass in `ContainerLevelAccess#NULL`, which will do nothing.

```java
// Client menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory) {
  this(containerId, playerInventory, ContainerLevelAccess.NULL);
}

// Server menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory, ContainerLevelAccess access) {
  // ...
}

// Assume this menu is attached to RegistryObject<Block> MY_BLOCK
@Override
public boolean stillValid(Player player) {
  return AbstractContainerMenu.stillValid(this.access, player, MY_BLOCK.get());
}
```

### Data Synchronization

Some data needs to be present on both the server and the client to display to the player. To do this, the menu implements a basic layer of data synchronization such that whenever the current data does not match the data last synced to the client. For players, this is checked every tick.

Minecraft supports two forms of data synchronization by default: `ItemStack`s via `Slot`s and integers via `DataSlot`s. `Slot`s and `DataSlot`s are views which hold references to data storages that can be be modified by the player in a screen, assuming the action is valid. These can be added to a menu within the constructor through `#addSlot` and `#addDataSlot`.

!!! note
    Since `Container`s used by `Slot`s are deprecated by Forge in favor of using the [`IItemHandler` capability][cap], the rest of the explanation will revolve around using the capability variant: `SlotItemHandler`.

A `SlotItemHandler` contains four parameters: the `IItemHandler` representing the inventory the stacks are within, the index of the stack this slot is specifically representing, and the x and y position of where the top-left position of the slot will render on the screen relative to `AbstractContainerScreen#leftPos` and `#topPos`. The client menu constructor should always supply an empty instance of an inventory of the same size.

In most cases, any slots the menu contains is first added, followed by the player's inventory, and finally concluded with the player's hotbar. To access any individual `Slot` from the menu, the index must be calculated based upon the order of which slots were added.

A `DataSlot` is an abstract class which should implement a getter and setter to reference the data stored in the data storage object. The client menu constructor should always supply a new instance via `DataSlot#standalone`.

These, along with slots, should be recreated every time a new menu is initialized.

!!! warning
    Although a `DataSlot` stores an integer, it is effectively limited to a **short** (-32768 to 32767) because of how it sends the value across the network. The 16 high-order bits of the integer are ignored.

```java
// Assume we have an inventory from a data object of size 5
// Assume we have a DataSlot constructed on each initialization of the server menu

// Client menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory) {
  this(containerId, playerInventory, new ItemStackHandler(5), DataSlot.standalone());
}

// Server menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory, IItemHandler dataInventory, DataSlot dataSingle) {
  // Check if the data inventory size is some fixed value
  // Then, add slots for data inventory
  this.addSlot(new SlotItemHandler(dataInventory, /*...*/));

  // Add slots for player inventory
  this.addSlot(new Slot(playerInventory, /*...*/));

  // Add data slots for handled integers
  this.addDataSlot(dataSingle);

  // ...
}
```

#### `ContainerData`

If multiple integers need to be synced to the client, a `ContainerData` can be used to reference the integers instead. This interface functions as an index lookup such that each index represents a different integer. `ContainerData`s can also be constructed in the data object itself if the `ContainerData` is added to the menu through `#addDataSlots`. The method creates a new `DataSlot` for the amount of data specified by the interface. The client menu constructor should always supply a new instance via `SimpleContainerData`.

```java
// Assume we have a ContainerData of size 3

// Client menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory) {
  this(containerId, playerInventory, new SimpleContainerData(3));
}

// Server menu constructor
public MyMenuAccess(int containerId, Inventory playerInventory, ContainerData dataMultiple) {
  // Check if the ContainerData size is some fixed value
  checkContainerDataCount(dataMultiple, 3);

  // Add data slots for handled integers
  this.addDataSlots(dataMultiple);

  // ...
}
```

!!! warning
    As `ContainerData` delegates to `DataSlot`s, these are also limited to a **short** (-32768 to 32767).

#### `#quickMoveStack`

`#quickMoveStack` is the second method that must be implemented by any menu. This method is called whenever a stack has been shift-clicked, or quick moved, out of its current slot until the stack has been fully moved out of its previous slot or there is no other place for the stack to go. The method returns a copy of the stack in the slot being quick moved.

Stacks are typically moved between slots using `#moveItemStackTo`, which moves the stack into the first available slot. It takes in the stack to be moved, the first slot index (inclusive) to try and move the stack to, the last slot index (exclusive), and whether to check the slots from first to last (when `false`) or from last to first (when `true`).

Across Minecraft implementations, this method is fairly consistent in its logic:

```java
// Assume we have a data inventory of size 5
// The inventory has 4 inputs (index 1 - 4) which outputs to a result slot (index 0)
// We also have the 27 player inventory slots and the 9 hotbar slots
// As such, the actual slots are indexed like so:
//   - Data Inventory: Result (0), Inputs (1 - 4)
//   - Player Inventory (5 - 31)
//   - Player Hotbar (32 - 40)
@Override
public ItemStack quickMoveStack(Player player, int quickMovedSlotIndex) {
  // The quick moved slot stack
  ItemStack quickMovedStack = ItemStack.EMPTY;
  // The quick moved slot
  Slot quickMovedSlot = this.slots.get(quickMovedSlotIndex) 
  
   // If the slot is in the valid range and the slot is not empty
  if (quickMovedSlot != null && quickMovedSlot.hasItem()) {
    // Get the raw stack to move
    ItemStack rawStack = quickMovedSlot.getItem(); 
    // Set the slot stack to a copy of the raw stack
    quickMovedStack = rawStack.copy();

    /*
    The following quick move logic can be simplified to if in data inventory,
    try to move to player inventory/hotbar and vice versa for containers
    that cannot transform data (e.g. chests).
    */

    // If the quick move was performed on the data inventory result slot
    if (quickMovedSlotIndex == 0) {
      // Try to move the result slot into the player inventory/hotbar
      if (!this.moveItemStackTo(rawStack, 5, 41, true)) {
        // If cannot move, no longer quick move
        return ItemStack.EMPTY;
      }

      // Perform logic on result slot quick move
      slot.onQuickCraft(rawStack, quickMovedStack);
    }
    // Else if the quick move was performed on the player inventory or hotbar slot
    else if (quickMovedSlotIndex >= 5 && quickMovedSlotIndex < 41) {
      // Try to move the inventory/hotbar slot into the data inventory input slots
      if (!this.moveItemStackTo(rawStack, 1, 5, false)) {
        // If cannot move and in player inventory slot, try to move to hotbar
        if (quickMovedSlotIndex < 32) {
          if (!this.moveItemStackTo(rawStack, 32, 41, false)) {
            // If cannot move, no longer quick move
            return ItemStack.EMPTY;
          }
        }
        // Else try to move hotbar into player inventory slot
        else if (!this.moveItemStackTo(rawStack, 5, 32, false)) {
          // If cannot move, no longer quick move
          return ItemStack.EMPTY;
        }
      }
    }
    // Else if the quick move was performed on the data inventory input slots, try to move to player inventory/hotbar
    else if (!this.moveItemStackTo(rawStack, 5, 41, false)) {
      // If cannot move, no longer quick move
      return ItemStack.EMPTY;
    }

    if (rawStack.isEmpty()) {
      // If the raw stack has completely moved out of the slot, set the slot to the empty stack
      quickMovedSlot.set(ItemStack.EMPTY);
    } else {
      // Otherwise, notify the slot that that the stack count has changed
      quickMovedSlot.setChanged();
    }

    /*
    The following if statement and Slot#onTake call can be removed if the
    menu does not represent a container that can transform stacks (e.g.
    chests).
    */
    if (rawStack.getCount() == quickMovedStack.getCount()) {
      // If the raw stack was not able to be moved to another slot, no longer quick move
      return ItemStack.EMPTY;
    }
    // Execute logic on what to do post move with the remaining stack
    quickMovedSlot.onTake(player, rawStack);
  }

  return quickMovedStack; // Return the slot stack
}
```

## Opening a Menu

Once a menu type has been registered, the menu itself has been finished, and a [screen] has been attached, a menu can then be opened by the player. Menus can be opened by calling `ServerPlayer#openMenu` on the logical server. The method takes in the `MenuProvider` of the server side menu, and optionally a `FriendlyByteBuf` if extra data needs to be synced to the client.

!!! note
    `ServerPlayer#openMenu` with the `FriendlyByteBuf` parameter should only be used if a menu type was created using an [`IContainerFactory`][icf].

#### `MenuProvider`

A `MenuProvider` is an interface that contains two methods: `#createMenu`, which creates the server instance of the menu, and `#getDisplayName`, which returns a component containing the title of the menu to pass to the [screen]. The `#createMenu` method contains three parameter: the container id of the menu, the inventory of the player who opened the menu, and the player who opened the menu.

A `MenuProvider` can easily be created using `SimpleMenuProvider`, which takes in a method reference to create the server menu and the title of the menu.

```java
// In some implementation
serverPlayer.openMenu(new SimpleMenuProvider(
  (containerId, playerInventory, player) -> new MyMenu(containerId, playerInventory),
  Component.translatable("menu.title.examplemod.mymenu")
));
```

### Common Implementations

Menus are typically opened on a player interaction of some kind (e.g. when a block or entity is right-clicked).

#### Block Implementation

Blocks typically implement a menu by overriding `BlockBehaviour#use`. If on the logical client, the interaction returns `InteractionResult#SUCCESS`. Otherwise, it opens the menu and returns `InteractionResult#CONSUME`.

The `MenuProvider` should be implemented by overriding `BlockBehaviour#getMenuProvider`. Vanilla methods use this to view the menu in spectator mode.

```java
// In some Block subclass
@Override
public MenuProvider getMenuProvider(BlockState state, Level level, BlockPos pos) {
  return new SimpleMenuProvider(/* ... */);
}

@Override
public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult result) {
  if (!level.isClientSide && player instanceof ServerPlayer serverPlayer) {
    serverPlayer.openMenu(state.getMenuProvider(level, pos));
  }
  return InteractionResult.sidedSuccess(level.isClientSide);
}
```

!!! note
    This is the simplest way to implement the logic, not the only way. If you want the block to only open the menu under certain conditions, then some data will need to be synced to the client beforehand to return `InteractionResult#PASS` or `#FAIL` if the conditions are not met.

#### Mob Implementation

Mobs typically implement a menu by overriding `Mob#mobInteract`. This is done similarly to the block implementation with the only difference being that the `Mob` itself should implement `MenuProvider` to support spectator mode viewing.

```java
public class MyMob extends Mob implements MenuProvider {
  // ...

  @Override
  public InteractionResult mobInteract(Player player, InteractionHand hand) {
    if (!this.level.isClientSide && player instanceof ServerPlayer serverPlayer) {
      serverPlayer.openMenu(this);
    }
    return InteractionResult.sidedSuccess(this.level.isClientSide);
  }
}
```

!!! note
    Once again, this is the simplest way to implement the logic, not the only way.

[registered]: ../concepts/registries.md#methods-for-registering
[acm]: #abstractcontainermenu
[mt]: #menutype
[qms]: #quickmovestack
[cap]: ../datastorage/capabilities.md#forge-provided-capabilities
[screen]: ./screens.md
[icf]: #icontainerfactory

---

# Overlays
Sometimes, we may want to display information to the user without interrupting their movement or , much in the way that F3 or the scoreboard do. This type of GUI element is called an overlay.  Overlays render underneath any visible [screen] and so will be visibly hidden (though the may still be rendering!) when one is opened.

Rendering using `Gui Graphics` is covered in [screens], and so won't be repeated in this article.

# Context

Previously, Forge included two events. `RenderGuiOverlayEvent` and `RegisterGuiOverlayEvent`. The former would fire each time an overlay was rendered, allowing modders to add their own rendering or cancel as needed. The latter fired once at some time during initialization and allowed modders to, as the name suggests, register their own overlays for their own purposes.

Since 1.20.6, Mojang modified the way overlays are created and rendered, making this system obsolete, moving to the use of the `LayeredDraw` class and `Layer` interface. `LayeredDraw` uses an internal, anonymous list of render functions that adhere to the `Layer` interface. Because they are anonymous, there was no way to be sure which `Layer` in the list corresponded with a particular render method in `Gui`.

The behavior of `RegisterGuiOverlayEvent` has been restored, allowing modders to insert their own render layers into this list in a one time event.

!!! important As of 1.21.6, this system has changed again, removing `Layer` and `LayeredDraw`. As such, `Layer` must be replaced with `ForgeLayer` on versions 1.21.6 and up. However, the rest of this documentation is still applicable.
# Forge Layered Draw
A `LayeredDraw` represents a list of renderable `Layers`. During runtime,`LayeredDraw#render` will be called to execute the render code of the internal `Layer` list. Additionally, `LayeredDraws` may be added into the render list of another `LayeredDraw`, forming a tree of renderable nodes.

Forge extends this implementation with `ForgeLayeredDraw`, giving `ResourceLocations` to both vanilla `LayerdDraws` and `Layers` to allow ordering. To begin adding modded `Layers` and `ForgeLayeredDraws`, listen to `AddGuiOverlayLayersEvent`, which fires on the mod bus.


### Vanilla Draw Order
By default, vanilla contains three `LayeredDraw` instances. The instance provided by the event is `ForgeLayeredDraw#VANILLA_ROOT`. This ForgeLayeredDraw instance will be referred to as the global parent hereon. Its contents is as follows:

Internal Name |      Resource Location       | Type
:--- |:----------------------------:| :---
PRE_SLEEP_STACK | "minecraft:pre_sleep_phase"  | ForgeLayeredDraw
SLEEP_OVERLAY |  "minecraft:sleep_overlay"   | Layer
POST_SLEEP_STACK | "minecraft:post_sleep_phase" | ForgeLayeredDraw

The contents of `ForgeLayeredDraw#PRE_SLEEP_STACK` is made entirely of `Layer` instances and is as follows:

Internal Name |      Resource Location       | Note
:--- |:--- | :---
CAMERA_OVERLAY | "minecraft:camera_overlay"
CROSSHAIR | "minecraft:crosshair"
CHANGE_STRATUM | "stratum_change" | 1.21.6+ Only
HOTBAR | "minecraft:hotbar"
EXPERIENCE | "minecraft:experience"
POTION_EFFECTS | "minecraft:potion_effects"
BOSS_OVERLAY | "minecraft:boss_overlay"

After the sleep overlay is rendered, the contents of `ForgeLayeredDraw#POST_SLEEP_STACK` is rendered, also entirely `Layer` instances:

Internal Name | Resource Location
:--- | :---
DEMO_OVERLAY | "minecraft:demo"
DEBUG_OVERLAY | "minecraft:debug"
SCOREBOARD | "minecraft:scoreboard"
HOTBAR_MESSAGE | "minecraft:hotbar_message"
TITLE_OVERLAY | "minecraft:title"
CHAT_OVERLAY | "minecraft:chat_overlay"
TAB_LIST | "minecraft:tab_list"
SUBTITLE_OVERLAY | "minecraft:subtitle"

!!! important All information above is present in the javadocs for `ForgeLayeredDraw`. If you aren't sure what's included in a layer, check its render code in `Gui`. For 1.21.6+, the vanilla order initialization is also present at `ForgeLayeredDraw#init`.

### A Note About Layer Order

The finalized render order is only computed **after** all event listeners have finished. Attempting to add new layers after the event has passed will not have any effect.  Additionally, because it is possible (but heavily discouraged) to re-order existing layers with `ForgeLayeredDraw#move`, there is no absolute guarantee on where a layer is at any point.

Additionally, layers cannot be moved across `ForgeLayeredDraw` boundaries. Once a layer has a parent, it stays within that parent. If you wish to do such a thing, cancel the original layer, then add a new layer in the desired parent

Finally, if a target (which is to say, the thing being ordered against) is *not* present, an appropriate warning will be emitted and no changes will be made. This is the case for all method calls in `ForgeLayeredDraw`. No call to any method will ever leave the layer order in an invalid state.
### Adding To ForgeLayeredDraws

Several overloads exist for the `ForgeLayeredDraw#add` method. Two are for registering vanilla's layers and should not be used under any circumstances, they are marked as `@Deprecated` for this reason.

Adding `Layers` can look like this:
```java
class MyClass {
    public static void addMyLayers(AddGuiOverlayLayersEvent event) {
        // We aren't specifying any targets,
        // so this will go at the end of VANILLA_ROOT's list.
        event.getLayeredDraw().add(
                ResourceLocation.fromNamespaceAndPath(MY_MODID, "eye_blinder_supreme"),
                (guiGraphics, deltaTracker) -> {
                    // whatever rendering code we want
                }
        );
        event.getLayeredDraw().add(
                ResourceLocation.fromNamespaceAndPath(MY_MODID, "dancing_cat"),
                MyClass::renderMethod
        );
    }

    private static void renderMethod(GuiGraphics guiGraphics, DeltaTracker deltaTracker) {
        // some other render code
    }
}
```
Layer names are not globally unique, they may be re-used between different `ForgeLayeredDraw` instances, but may not be used within the same instance.

```java
// assume above code block has also ran
public static void addMyLayers(AddGuiOverlayLayersEvent event) {
    ResourceLocation rl = ResourceLocation.fromNamespaceAndPath(MY_MODID, "my_cool_layer_list");
    ForgeLayeredDraw myStack = new ForgeLayeredDraw(rl);
    myStack.add( 
            ResourceLocation.fromNamespaceAndPath(MY_MODID, "eye_blinder_supreme"),
            (guiGraphics, deltaTracker) -> {/* ... */}
    );
    // Because this layer lives in a different draw stack,
    // it's okay for the ResourceLocation to get re-used
    event.getLayeredDraw().add(myStack.getName(), myStack, () -> true);
    // The stack condition supplier is mandatory, so to tell it to always* render let it supply true
    // *unless another mod adds another condition. They can be stacked!
}
```

### Cancelling Layers

Previously, a modder would need to use the `RenderGuiOverlayEvent` to cancel an overlay's rendering. Now, modders can simply add a condition to existing `Layers` or entire `ForgeLayeredDraws`

To cancel an existing layer, use `ForgeLayeredDraw#addConditionTo`. Two method overloads are provided if, one for if the target layer exists in the caller (which is to say, the specific instance `addConditionTo` is called on) and one intended to be called on the  global parent. The provided `BooleanSupplier` represents if rendering should occur.

If a condition applied to a target that corresponds to a `ForgeLayeredDraw` object, the condition will apply to all child layers within the object. This is helpful for allowing many layers to be disabled with a single boolean check (this is how vanilla handles pressing F1!). In other words, if the parent is cancelled, all child layers are also automatically cancelled. None of the child `Layer#render` methods will be called in this case.

### Modifying Existing Layers

Directly modifying the rendered elements of already existing layers is *not supported* with `ForgeLayeredDraw`. If you wish to do so in a way that is API friendly, cancel the original layer wholesale and do the rendering yourself. 

[screens]: ./screens.md
[screen]: ./screens.md

---

# Screens

Screens are typically the base of all Graphical User Interfaces (GUIs) in Minecraft: taking in user input, verifying it on the server, and syncing the resulting action back to the client. They can be combined with [menus] to create an communication network for inventory-like views, or they can be standalone which modders can handle through their own [network] implementations.

Screens are made up of numerous parts, making it difficult to fully understand what a 'screen' actually is in Minecraft. As such, this document will go over each of the screen's components and how it is applied before discussing the screen itself.

## Relative Coordinates

Whenever anything is rendered, there needs to be some identifier which specifies where it will appear. With numerous abstractions, most of Minecraft's rendering calls takes in an x, y, and z value in a coordinate plane. X values increase from left to right, y from top to bottom, and z from far to near. However, the coordinates are not fixed to a specified range. They can change depending on the size of the screen and the scale at which is specified within the options. As such, extra care must be taken to make sure the values of the coordinates while rendering scale properly to the changeable screen size.

Information on how to relativize your coordinates will be within the [screen] section.

!!! important
    If you choose to use fixed coordinates or incorrectly scale the screen, the rendered objects may look strange or misplaced. An easy way to check if you relativized your coordinates correctly is to click the 'Gui Scale' button in your video settings. This value is used as the divisor to the width and height of your display when determining the scale at which a GUI should render.

## Gui Graphics

Any GUI rendered by Minecraft is typically done using `GuiGraphics`. `GuiGraphics` is the first parameter to almost all rendering methods; it contains basic methods to render commonly used objects. These fall into five categories: colored rectangles, strings, and textures, items, and tooltips. There is also an additional method for rendering a snippet of a component (`#enableScissor` / `#disableScissor`). `GuiGraphics` also exposes the `PoseStack` which applies the transformations necessary to properly render where the component should be rendered. Additionally, colors are in the [ARGB][argb] format.

### Colored Rectangles

Colored rectangles are drawn through a position color shader. There are three types of colored rectangles that can be drawn.

First, there is a colored horizontal and vertical one-pixel wide line, `#hLine` and `#vLine` respectively. `#hLine` takes in two x coordinates defining the left and right (inclusively), the top y coordinate, and the color. `#vLine` takes in the left x coordinate, two y coordinates defining the top and bottom (inclusively), and the color.

Second, there is the `#fill` method, which draws a rectangle to the screen. The line methods internally call this method. This takes in the left x coordinate, the top y coordinate, the right x coordinate, the bottom y coordinate, and the color.

Finally, there is the `#fillGradient` method, which draws a rectangle with a vertical gradient. This takes in the right x coordinate, the bottom y coordinate, the left x coordinate, the top y coordinate, the z coordinate, and the bottom and top colors.

### Strings

Strings are drawn through its `Font`, typically consisting of their own shaders for normal, see through, and offset mode. There are two alignment of strings that can be rendered, each with a back shadow: a left-aligned string (`#drawString`) and a center-aligned string (`#drawCenteredString`). These both take in the font the string will be rendered in, the string to draw, the x coordinate representing the left or center of the string respectively, the top y coordinate, and the color.

!!! note
    Strings should typically be passed in as [`Component`s][component] as they handle a variety of usecases, including the two other overloads of the method.

### Textures

Textures are drawn through blitting, hence the method name `#blit`, which, for this purpose, copies the bits of an image and draws them directly to the screen. These are drawn through a position texture shader. While there are many different `#blit` overloads, we will only discuss two static `#blit`s.

The first static `#blit` takes in six integers and assumes the texture being rendered is on a 256 x 256 PNG file. It takes in the left x and top y screen coordinate, the left x and top y coordinate within the PNG, and the width and height of the image to render.

!!! note
    The size of the PNG file must be specified so that the coordinates can be normalized to obtain the associated UV values.

The static `#blit` which the first calls expands this to nine integers, only assuming the image is on a PNG file. It takes in the left x and top y screen coordinate, the z coordinate (referred to as the blit offset), the left x and top y coordinate within the PNG, the width and height of the image to render, and the width and height of the PNG file.

#### Blit Offset

The z coordinate when rendering a texture is typically set to the blit offset. The offset is responsible for properly layering renders when viewing a screen. Renders with a smaller z coordinate are rendered in the background and vice versa where renders with a larger z coordinate are rendered in the foreground. The z offset can be set directly on the `PoseStack` itself via `#translate`. Some basic offset logic is applied internally in some methods of `GuiGraphics` (e.g. item rendering).

!!! important
    When setting the blit offset, you must reset it after rendering your object. Otherwise, other objects within the screen may be rendered in an incorrect layer causing graphical issues. It is recommended to push the current pose before translating and then popping after all rendering at the offset is completed.

## Renderable

`Renderable`s are essentially objects that are rendered. These include screens, buttons, chat boxes, lists, etc. `Renderable`s only have one method: `#render`. This takes in the `GuiGraphics` used to render things to the screen, the x and y positions of the mouse scaled to the relative screen size, and the tick delta (how many ticks have passed since the last frame).

Some common renderables are screens and 'widgets': interactable elements which typically render on the screen such as `Button`, its subtype `ImageButton`, and `EditBox` which is used to input text on the screen.

## GuiEventListener

Any screen rendered in Minecraft implements `GuiEventListener`. `GuiEventListener`s are responsible for handling user interaction with the screen. These include inputs from the mouse (movement, clicked, released, dragged, scrolled, mouseover) and keyboard (pressed, released, typed). Each method returns whether the associated action affected the screen successfully. Widgets like buttons, chat boxes, lists, etc. also implement this interface.

### ContainerEventHandler

Almost synonymous with `GuiEventListener`s are their subtype: `ContainerEventHandler`s. These are responsible for handling user interaction on screens which contain widgets, managing which is currently focused and how the associated interactions are applied. `ContainerEventHandler`s add three additional features: interactable children, dragging, and focusing.

Event handlers hold children which are used to determine the interaction order of elements. During the mouse event handlers (excluding dragging), the first child in the list that the mouse hovers over has their logic executed.

Dragging an element with the mouse, implemented via `#mouseClicked` and `#mouseReleased`, provides more precisely executed logic.

Focusing allows for a specific child to be checked first and handled during an event's execution, such as during keyboard events or dragging the mouse. Focus is typically set through `#setFocused`. In addition, interactable children can be cycled using `#nextFocusPath`, selecting the child based upon the `FocusNavigationEvent` passed in.

!!! note
    Screens implement `ContainerEventHandler` through `AbstractContainerEventHandler`, which adds in the setter and getter logic for dragging and focusing children.

## NarratableEntry

`NarratableEntry`s are elements which can be spoken about through Minecraft's accessibility narration feature. Each element can provide different narration depending on what is hovered or selected, prioritized typically by focus, hovering, and then all other cases.

`NarratableEntry`s have three methods: one which determines the priority of the element (`#narrationPriority`), one which determines whether to speak the narration (`#isActive`), and finally one which supplies the narration to its associated output, spoken or read (`#updateNarration`). 

!!! note
    All widgets from Minecraft are `NarratableEntry`s, so it typically does not need to be manually implemented if using an available subtype.

## The Screen Subtype

With all of the above knowledge, a basic screen can be constructed. To make it easier to understand, the components of a screen will be mentioned in the order they are typically encountered.

First, all screens take in a `Component` which represents the title of the screen. This component is typically drawn to the screen by one of its subtypes. It is only used in the base screen for the narration message.

```java
// In some Screen subclass
public MyScreen(Component title) {
    super(title);
}
```

### Initialization

Once a screen has been initialized, the `#init` method is called. The `#init` method sets the initial settings inside the screen from the `ItemRenderer` and `Minecraft` instance to the relative width and height as scaled by the game. Any setup such as adding widgets or precomputing relative coordinates should be done in this method. If the game window is resized, the screen will be reinitialized by calling the `#init` method.

There are three ways to add a widget to a screen, each serving a separate purpose:

Method                 | Description
:---:                  | :---
`#addWidget`           | Adds a widget that is interactable and narrated, but not rendered.
`#addRenderableOnly`   | Adds a widget that will only be rendered; it is not interactable or narrated.
`#addRenderableWidget` | Adds a widget that is interactable, narrated, and rendered.

Typically, `#addRenderableWidget` will be used most often.

```java
// In some Screen subclass
@Override
protected void init() {
    super.init();

    // Add widgets and precomputed values
    this.addRenderableWidget(new EditBox(/* ... */));
}
```

### Ticking Screens

Screens also tick using the `#tick` method to perform some level of client side logic for rendering purposes. The most common example is the `EditBox` for the blinking cursor.

```java
// In some Screen subclass
@Override
public void tick() {
    super.tick();

    // Add ticking logic for EditBox in editBox
    this.editBox.tick();
}
```

### Input Handling

Since screens are subtypes of `GuiEventListener`s, the input handlers can also be overridden, such as for handling logic on a specific [key press][keymapping].

### Rendering the Screen

Finally, screens are rendered through the `#render` method provided by being a `Renderable` subtype. As mentioned, the `#render` method draws the everything the screen has to render every frame, such as the background, widgets, tooltips, etc. By default, the `#render` method only renders the widgets to the screen.

The two most common things rendered within a screen that is typically not handled by a subtype is the background and the tooltips.

The background can be rendered using `#renderBackground`, with one method taking in a v Offset for the options background whenever a screen is rendered when the level behind it cannot be.

Tooltips are rendered through `GuiGraphics#renderTooltip` or `GuiGraphics#renderComponentTooltip` which can take in the text components being rendered, an optional custom tooltip component, and the x / y relative coordinates on where the tooltip should be rendered on the screen.

```java
// In some Screen subclass

// mouseX and mouseY indicate the scaled coordinates of where the cursor is in on the screen
@Override
public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
    // Background is typically rendered first
    this.renderBackground(graphics);

    // Render things here before widgets (background textures)

    // Then the widgets if this is a direct child of the Screen
    super.render(graphics, mouseX, mouseY, partialTick);

    // Render things after widgets (tooltips)
}
```

### Closing the Screen

When a screen is closed, two methods handle the teardown: `#onClose` and `#removed`.

`#onClose` is called whenever the user makes an input to close the current screen. This method is typically used as a callback to destroy and save any internal processes in the screen itself. This includes sending packets to the server.

`#removed` is called just before the screen changes and is released to the garbage collector. This handles anything that hasn't been reset back to its initial state before the screen was opened.

```java
// In some Screen subclass

@Override
public void onClose() {
    // Stop any handlers here

    // Call last in case it interferes with the override
    super.onClose();
}

@Override
public void removed() {
    // Reset initial states here

    // Call last in case it interferes with the override
    super.removed()
;}
```

## `AbstractContainerScreen`

If a screen is directly attached to a [menu][menus], then an `AbstractContainerScreen` should be subclassed instead. An `AbstractContainerScreen` acts as the renderer and input handler of a menu and contains logic for syncing and interacting with slots. As such, only two methods typically need to be overridden or implemented to have a working container screen. Once again, to make it easier to understand, the components of a container screen will be mentioned in the order they are typically encountered.

An `AbstractContainerScreen` typically requires three parameters: the container menu being opened (represented by the generic `T`), the player inventory (only for the display name), and the title of the screen itself. Within here, a number of positioning fields can be set:

Field             | Description
:---:             | :---
`imageWidth`      | The width of the texture used for the background. This is typically inside a PNG of 256 x 256 and defaults to 176.
`imageHeight`     | The width of the texture used for the background. This is typically inside a PNG of 256 x 256 and defaults to 166.
`titleLabelX`     | The relative x coordinate of where the screen title will be rendered.
`titleLabelY`     | The relative y coordinate of where the screen title will be rendered.
`inventoryLabelX` | The relative x coordinate of where the player inventory name will be rendered.
`inventoryLabelY` | The relative y coordinate of where the player inventory name will be rendered.

!!! important
    In a previous section, it mentioned that precomputed relative coordinates should be set in the `#init` method. This still remains true, as the values mentioned here are not precomputed coordinates but static values and relativized coordinates.

    The image values are static and non changing as they represent the background texture size. To make things easier when rendering, two additional values (`leftPos` and `topPos`) are precomputed in the `#init` method which marks the top left corner of where the background will be rendered. The label coordinates are relative to these values.

    The `leftPos` and `topPos` is also used as a convenient way to render the background as they already represent the position to pass into the `#blit` method.

```java
// In some AbstractContainerScreen subclass
public MyContainerScreen(MyMenu menu, Inventory playerInventory, Component title) {
    super(menu, playerInventory, title);

    this.titleLabelX = 10;
    this.inventoryLabelX = 10;

    /*
     * If the 'imageHeight' is changed, 'inventoryLabelY' must also be
     * changed as the value depends on the 'imageHeight' value.
     */
}
```

### Menu Access

As the menu is passed into the screen, any values that were within the menu and synced (either through slots, data slots, or a custom system) can now be accessed through the `menu` field.

### Container Tick

Container screens tick within the `#tick` method when the player is alive and looking at the screen via `#containerTick`. This essentially takes the place of `#tick` within container screens, with its most common usage being to tick the recipe book.

```java
// In some AbstractContainerScreen subclass
@Override
protected void containerTick() {
    super.containerTick();

    // Tick things here
}
```

### Rendering the Container Screen

The container screen is rendered across three methods: `#renderBg`, which renders the background textures, `#renderLabels`, which renders any text on top of the background, and `#render` which encompass the previous two methods in addition to providing a grayed out background and tooltips.

Starting with `#render`, the most common override (and typically the only case) adds the background, calls the super to render the container screen, and finally renders the tooltips on top of it.

```java
// In some AbstractContainerScreen subclass
@Override
public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
    this.renderBackground(graphics);
    super.render(graphics, mouseX, mouseY, partialTick);

    /*
     * This method is added by the container screen to render
     * the tooltip of the hovered slot.
     */
    this.renderTooltip(graphics, mouseX, mouseY);
}
```

Within the super, `#renderBg` is called to render the background of the screen. The most standard representation uses three method calls: two for setup and one to draw the background texture.

```java
// In some AbstractContainerScreen subclass

// The location of the background texture (assets/<namespace>/<path>)
private static final ResourceLocation BACKGROUND_LOCATION = new ResourceLocation(MOD_ID, "textures/gui/container/my_container_screen.png");

@Override
protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
    /*
     * Renders the background texture to the screen. 'leftPos' and
     * 'topPos' should already represent the top left corner of where
     * the texture should be rendered as it was precomputed from the
     * 'imageWidth' and 'imageHeight'. The two zeros represent the
     * integer u/v coordinates inside the 256 x 256 PNG file.
     */
    graphics.blit(BACKGROUND_LOCATION, this.leftPos, this.topPos, 0, 0, this.imageWidth, this.imageHeight);
}
```

Finally, `#renderLabels` is called to render any text above the background, but below the tooltips. This simply calls uses the font to draw the associated components.

```java
// In some AbstractContainerScreen subclass
@Override
protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
    super.renderLabels(graphics, mouseX, mouseY);

    // Assume we have some Component 'label'
    // 'label' is drawn at 'labelX' and 'labelY'
    graphics.drawString(this.font, this.label, this.labelX, this.labelY, 0x404040);
}
```

!!! note
    When rendering the label, you do **not** need to specify the `leftPos` and `topPos` offset. Those have already been translated within the `PoseStack` so everything within this method is drawn relative to those coordinates.

## Registering an AbstractContainerScreen

To use an `AbstractContainerScreen` with a menu, it needs to be registered. This can be done by calling `MenuScreens#register` within the `FMLClientSetupEvent` on the [**mod event bus**][modbus].

```java
// Event is listened to on the mod event bus
private void clientSetup(FMLClientSetupEvent event) {
    event.enqueueWork(
        // Assume RegistryObject<MenuType<MyMenu>> MY_MENU
        // Assume MyContainerScreen<MyMenu> which takes in three parameters
        () -> MenuScreens.register(MY_MENU.get(), MyContainerScreen::new)
    );
}
```

!!! warning
    `MenuScreens#register` is not thread-safe, so it needs to be called inside `#enqueueWork` provided by the parallel dispatch event.

[menus]: ./menus.md
[network]: ../networking/index.md
[screen]: #the-screen-subtype
[argb]: https://en.wikipedia.org/wiki/RGBA_color_model#ARGB32
[component]: ../concepts/internationalization.md#translatablecontents
[keymapping]: ../misc/keymappings.md#inside-a-gui
[modbus]: ../concepts/events.md#mod-event-bus

## HUD overlay when Forge client overlay classes are missing

In this local Forge 1.21.11 environment, `net.minecraftforge.client.*` overlay classes may not be on the compile classpath even though they exist in `mc_java_sources`. If `ForgeGui` / `IGuiOverlay` / `RegisterGuiOverlaysEvent` cannot be resolved, implement the HUD with a vanilla `net.minecraft.client.gui.Gui` subclass and inject it into `Minecraft.gui` via reflection. The class only needs to compile for GameTest (server-side), so avoid depending on Forge client-only APIs.
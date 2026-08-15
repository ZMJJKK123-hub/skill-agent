---

name: forge-concept-events
description: "Forge events: buses, handler registration, @EventBusSubscriber, cancellation, results, priority."
whenToUse: "Use when listening to Forge events or firing custom events."

---

# Events

Forge uses an event bus that lets mods intercept vanilla and mod behaviors. The main bus is `MinecraftForge#EVENT_BUS`; the mod-specific bus is `FMLJavaModLoadingContext#getModEventBus`.

## Creating an event handler

Handlers are single-parameter methods returning void, registered with `IEventBus#addListener` (or `#addGenericListener` for `GenericEvent<T>`, specifying the generic class) inside the mod constructor:

```java
modEventBus.addListener(this::modEventHandler);
forgeEventBus.addGenericListener(Entity.class, ExampleMod::forgeEventHandler);
```

### Annotated handlers

- **Instance**: `@SubscribeEvent` on an instance method; register with `MinecraftForge.EVENT_BUS.register(instance)`.
- **Static**: `@SubscribeEvent` on a static method; register with `...register(Class.class)`.
- **Automatic**: `@Mod.EventBusSubscriber(modid, bus, value = Dist.CLIENT)` auto-registers the class to the given bus at mod construction (methods must be static).

## Canceling

Cancelable events are `@Cancelable` (`Event#isCancelable()` true); use `Event#setCanceled(true/false)`. Canceling a non-cancelable event throws `UnsupportedOperationException` — always check first.

## Results

`@HasResult` events use `Event$Result`: `DENY` (stops the event), `DEFAULT` (vanilla behavior), `ALLOW` (forces the action). Set via `#setResult`; semantics differ per event — read the JavaDoc.

## Priority

`@SubscribeEvent(priority = EventPriority.X)`: `HIGHEST` first, descending to `LOWEST`, then `MONITOR` (read-only, last; mutating during MONITOR may throw).

## Sub events

Listening to a parent event class receives all subclasses (e.g. all `PlayerEvent` variants).

## Mod event bus

Used for lifecycle events implementing `IModBusEvent`. Lifecycle events run in parallel — defer cross-mod work to `#enqueueWork` or use `InterModComms`. Common lifecycle events: `FMLCommonSetupEvent`, `FMLClientSetupEvent`/`FMLDedicatedServerSetupEvent`, `InterModEnqueueEvent`, `InterModProcessEvent`. Non-parallel mod-bus events: `RegisterColorHandlersEvent`, `ModelEvent$BakingCompleted`, `TextureStitchEvent`, `RegisterEvent`. Rule of thumb: mod-bus events handle mod initialization.

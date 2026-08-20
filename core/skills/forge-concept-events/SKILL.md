---

name: forge-concept-events
description: "Forge events: buses, handler registration, @EventBusSubscriber, cancellation, results, priority."
whenToUse: "Use when listening to Forge events or firing custom events."

---

# Events

Forge uses an event bus that lets mods intercept vanilla and mod behaviors.

> ⚠️ **IMPORTANT (1.21.11):** the old `MinecraftForge.EVENT_BUS`, `FMLJavaModLoadingContext#getModEventBus`, `@SubscribeEvent`, and `@Mod.EventBusSubscriber` patterns below are LEGACY and generally NOT available in this Forge version. Use the **typed event bus** `SomeEvent.BUS.addListener(...)` shown in the "1.21.11+ current event bus" section at the bottom. Do NOT copy the legacy examples.

## Legacy event handler patterns (older Forge, not 1.21.11)

The main bus is `MinecraftForge#EVENT_BUS`; the mod-specific bus is `FMLJavaModLoadingContext#getModEventBus`.

## Creating an event handler (legacy)

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

## 1.21.11+ current event bus (verified from mc_java_sources)

In this Forge build, events are **typed record events with a static `BUS` field** instead of the old global `MinecraftForge.EVENT_BUS` + `@SubscribeEvent` pattern.

Each event class exposes:

```java
public static final EventBus<MyEvent> BUS = EventBus.create(MyEvent.class);
// cancellable events:
public static final CancellableEventBus<MyEvent> BUS = CancellableEventBus.create(MyEvent.class);
```

Subscribe directly:

```java
MyEvent.BUS.addListener((MyEvent event) -> {
    // handle
});
```

Common examples:
- `TickEvent.ServerTickEvent` / nested `Pre`/`Post` use `TickEvent.ServerTickEvent.BUS` or nested `TickEvent.ServerTickEvent.Pre.BUS`.
- `ServerTickEvent.Pre.BUS.addListener(...)`
- `RegisterCommandsEvent.BUS.addListener(...)`
- `LivingDeathEvent.BUS.addListener(...)` (cancellable via `CancellableEventBus`)
- `BuildCreativeModeTabContentsEvent.BUS.addListener(...)`

Prefer reading the exact event class first; the bus field name and type are always visible in `mc_java_sources`.
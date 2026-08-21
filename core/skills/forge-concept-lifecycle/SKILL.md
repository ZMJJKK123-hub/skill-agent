---

name: forge-concept-lifecycle
description: "Forge 模组生命周期：模组事件总线（Bus.MOD）、生命周期事件（FMLCommonSetupEvent、FMLClientSetupEvent、FMLDedicatedServerSetupEvent）、注册事件（NewRegistryEvent、DataPackRegistryEvent$NewRegistry、RegisterEvent）、DeferredRegister 使用、GatherDataEvent 数据生成、InterModComms 跨模组通信（InterModEnqueueEvent、InterModProcessEvent、IMCMessage）、ParallelDispatchEvent#enqueueWork 线程安全、FMLConstructModEvent、FMLLoadCompleteEvent、1.21.11+ typed event bus、FMLJavaModLoadingContext#getModBusGroup。"
whenToUse: "Use when initializing a Forge mod or registering lifecycle event listeners."

---

# Mod Lifecycle

During mod loading, lifecycle events fire on the mod-specific event bus. Register listeners via `@EventBusSubscriber(bus = Bus.MOD)` or in the mod constructor:

```java
@Mod.EventBusSubscriber(modid = "mymod", bus = Mod.EventBusSubscriber.Bus.MOD)
public class MyModEventSubscriber {
  @SubscribeEvent
  static void onCommonSetup(FMLCommonSetupEvent event) { ... }
}

@Mod("mymod")
public class MyMod {
  public MyMod(FMLModLoadingContext context) {
    context.getModEventBus().addListener(this::onCommonSetup);
  }
  private void onCommonSetup(FMLCommonSetupEvent event) { ... }
}
```

> **Warning**: most lifecycle events fire in parallel — all mods receive the same event concurrently. Mods must be thread-safe; defer work via `ParallelDispatchEvent#enqueueWork`.

## Registry events

Fired synchronously after mod construction, in order:

- `NewRegistryEvent`: register custom registries via `RegistryBuilder`.
- `DataPackRegistryEvent$NewRegistry`: register custom datapack registries by providing a `Codec` for JSON encode/decode.
- `RegisterEvent`: fired for each registry to register objects.

> Prefer `DeferredRegister` over registry events where possible — it handles timing and is less error-prone.

## Data generation

If data generators run, `GatherDataEvent` fires last (synchronously) to register data providers.

## Common setup

`FMLCommonSetupEvent`: actions common to client and server (e.g. registering capabilities).

## Sided setup

`FMLClientSetupEvent` (physical client) and `FMLDedicatedServerSetupEvent` (dedicated server): physical-side initialization such as key bindings.

## InterModComms

Cross-mod messages: `InterModEnqueueEvent` (send via `InterModComms#sendTo` with mod id, key, and a supplier of data) and `InterModProcessEvent` (receive via `InterModComms#getMessages`, optionally filtered by key predicate; returns `IMCMessage`s). Backed by a `ConcurrentMap`, safe during lifecycle events.

Also: `FMLConstructModEvent` (after mod construction, before `RegisterEvent`) and `FMLLoadCompleteEvent` (after InterModComms, when loading completes).

## 1.21.11+ mod lifecycle note

In this Forge build, do NOT use `context.getModEventBus()` or `FMLJavaModLoadingContext.get().getModEventBus()`. Use `FMLJavaModLoadingContext.get().getModBusGroup()` and typed event buses. For lifecycle listeners, read the event class's static `BUS` field or use the typed bus registration shown in the current event API guidance.
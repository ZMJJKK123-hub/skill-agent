---

name: forge-datastorage-capabilities
description: "Forge Capabilities 能力系统：ICapabilityProvider#getCapability 获取、CapabilityManager#get CapabilityToken、LazyOptional 可选值、Forge-provided capabilities（IItemHandler/IFluidHandler/IEnergyStorage）、Capability 暴露（#getCapability 重写、LazyOptional.of、Capability#orEmpty）、AttachCapabilitiesEvent 事件（Entity/BlockEntity/ItemStack/Level/LevelChunk 5种泛型类型、#addCapability、ICapabilitySerializable 持久化）、RegisterCapabilitiesEvent 注册、@AutoRegisterCapability 注解、LevelChunk/BlockEntity 持久化（标记脏位、setChanged）、客户端同步（网络包发送）、PlayerEvent$Clone 玩家死亡数据持久化、Direction 面向特定实例、Capability#isRegistered 注册检查。"
whenToUse: "Use when adding capabilities to items, entities, block entities, levels, or chunks."

---

# The Capability System

Capabilities expose features dynamically via interfaces, avoiding direct implementation of many interfaces. Forge adds capability support to BlockEntities, Entities, ItemStacks, Levels, and LevelChunks.

## Forge-provided capabilities

- `IItemHandler`: inventory slots (block entities, entities, item stacks); replaces the old `Container`/`WorldlyContainer`.
- `IFluidHandler`: fluid inventories.
- `IEnergyStorage`: energy containers (based on RedstoneFlux).

## Using an existing capability

Query via `ICapabilityProvider#getCapability(Capability<T>, Direction)`. Get the capability instance via `CapabilityManager#get(new CapabilityToken<>(){})` (e.g. `ForgeCapabilities#ITEM_HANDLER`). A non-null instance may still be unregistered — check `Capability#isRegistered`. The `Direction` requests a face-specific instance; `null` = side-agnostic. Returns a `LazyOptional` (empty when unavailable).

## Exposing a capability

Create an instance per object; override `#getCapability`, compare `cap == ForgeCapabilities.ITEM_HANDLER`, return `LazyOptional.of(supplier).cast()`, fall back to `super`. Use `Capability#orEmpty` for a single capability. Invalidate at lifecycle end: `LazyOptional#invalidate` (in `#invalidateCaps` for owned providers; via `AttachCapabilitiesEvent#addListener` otherwise).

Items: attach providers via `Item#initCapabilities` (stored on the ItemStack).

Use direct `cap ==` checks, not maps — capability tests run every tick.

## Attaching capabilities

`AttachCapabilitiesEvent` has 5 generic types: `Entity`, `BlockEntity`, `ItemStack`, `Level`, `LevelChunk` (no subtypes — check `instanceof` yourself). Use `#addCapability` with an `ICapabilityProvider` (or `ICapabilitySerializable<T>` for persistence with save/load).

## Creating your own capability

- `RegisterCapabilitiesEvent#register(IExampleCapability.class)` (mod event bus), or
- annotate the interface with `@AutoRegisterCapability`.

## Persisting LevelChunk/BlockEntity capabilities

These are only written when marked dirty — mark the owner dirty on state changes (e.g. `ItemStackHandler#onContentsChanged` → `setChanged()`).

## Synchronizing with clients

Capability data is not sent by default; sync via packets on: entity spawn/block place, data changes, and new viewers.

## Persisting across player deaths

Data does not persist by default — copy it in `PlayerEvent$Clone`, using `#isWasDeath` to avoid duplicating values when returning from the End.

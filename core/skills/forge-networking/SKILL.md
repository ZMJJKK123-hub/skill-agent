---

name: forge-networking
description: "Forge networking: SimpleChannel packets, spawn data, data parameters, sending and security."
whenToUse: "Use when implementing network packets or entity data sync in a Forge mod."

---

# Entities sync

## Spawn data

Forge handles modded entity spawning separately (extending a vanilla entity may not inherit all behavior). Implement `IEntityAdditionalSpawnData` (`#writeSpawnData`/`#readSpawnData`) to add static data to the spawn packet.

## Data parameters

The vanilla system for syncing entity data: create a `static final EntityDataAccessor<T>` via `SynchedEntityData#defineId(entityClass, serializer)` (serializers in `EntityDataSerializers`). **Only create parameters for your own entities, within that entity's class** — adding to others desyncs network IDs. Override `Entity#defineSynchedData`, call `super` first, then `this.entityData.define(param, initialValue)`. Read/write via `entityData`; changes sync automatically.

# Networking

## SimpleImpl (SimpleChannel)

Create the channel in a handler class:

```java
private static final String PROTOCOL_VERSION = "1";
public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
  ResourceLocation.fromNamespaceAndPath("mymodid", "main"),
  () -> PROTOCOL_VERSION, PROTOCOL_VERSION::equals, PROTOCOL_VERSION::equals
);
```

The version predicates must handle meta-versions: `ABSENT` (missing on the other Forge endpoint) and `ACCEPTVANILLA` (vanilla endpoint). Returning false for both requires the channel to be present.

Register messages with `INSTANCE#registerMessage(id++, MSG.class, encode, decode, handle)` — encode is a `BiConsumer<MSG, FriendlyByteBuf>`, decode a `Function<FriendlyByteBuf, MSG>`, handle a `BiConsumer<MSG, Supplier<NetworkEvent.Context>>`; method references work (e.g. `MSG#encode`).

### Handling packets

Packets run on the network thread — wrap game work in `ctx.get().enqueueWork(...)` and call `ctx.get().setPacketHandled(true)`. Server-side: be defensive — only access blocks/block entities when `Level#hasChunkAt` is true (arbitrary chunk generation exploits). Client-side handlers should be wrapped with `DistExecutor#unsafeRunWhenOn(Dist.CLIENT, ...)`.

### Sending

- To the server: `INSTANCE.sendToServer(new MyMessage())`.
- To clients: `INSTANCE.send(PacketDistributor.PLAYER.with(serverPlayer), msg)`, `TRACKING_CHUNK.with(levelChunk)`, `ALL.noArg()`, or directly via `HANDLER.sendTo(msg, connection, NetworkDirection.PLAY_TO_CLIENT)`.

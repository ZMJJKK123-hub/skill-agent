---
name: forge-networking
description: |
  Forge 网络（Networking）指南（Minecraft Wiki 中文版全量正文）。
  
  【概述】In addition to regular network messages, there are various other systems provided to handle synchronizing entity data.
  
  【涵盖内容】
  - IEntityAdditionalSpawnData
  - Data Parameters
  - Sending to the Server
  - Sending to Clients
  
  【适用场景】编写数据包 / 资源包 / Java 版自定义内容，需要 Forge 网络（Networking）指南 的完整规范时
---

Entities
========

In addition to regular network messages, there are various other systems provided to handle synchronizing entity data.

Spawn Data
----------

In general, the spawning of modded entities is handled separately, by Forge.

!!! note
    This means that simply extending a vanilla entity class may not inherit all its behavior. You may need to implement certain vanilla behaviors yourself.

You can add extra data to the spawn packet Forge sends by implementing the following interface.

### IEntityAdditionalSpawnData

If your entity has data that is needed on the client, but does not change over time, then it can be added to the entity spawn packet using this interface. `#writeSpawnData` and `#readSpawnData` control how the data should be encoded to/decoded from the network buffer.

Dynamic Data
------------

### Data Parameters

This is the main vanilla system for synchronizing entity data from the server to the client. As such, a number of vanilla examples are available to refer to.

Firstly, you need a `EntityDataAccessor<T>` for the data you wish to keep synchronized. This should be stored as a `static final` field in your entity class, obtained by calling `SynchedEntityData#defineId` and passing the entity class and a serializer for that type of data. The available serializer implementations can be found as static constants within the `EntityDataSerializers` class.

!!! warning
    You should __only__ create data parameters for your own entities, _within that entity's class_.
    Adding parameters to entities you do not control can cause the IDs used to send that data over the network to become desynchronized, causing difficult to debug crashes.

Then, override `Entity#defineSynchedData` and call `this.entityData.define(...)` for each of your data parameters, passing the parameter and an initial value to use. Remember to always call the `super` method first!

You can then get and set these values via your entity's `entityData` instance. Changes made will be synchronized to the client automatically.

---

Networking
==========

Communication between servers and clients is the backbone of a successful mod implementation.

There are two primary goals in network communication:

1. Making sure the client view is "in sync" with the server view
    - The flower at coordinates (X, Y, Z) just grew
2. Giving the client a way to tell the server that something has changed about the player
    - the player pressed a key

The most common way to accomplish these goals is to pass messages between the client and the server. These messages will usually be structured, containing data in a particular arrangement, for easy sending and receiving.

There are a variety of techniques provided by Forge to facilitate communication mostly built on top of [netty][].

The simplest, for a new mod, would be [SimpleImpl][channel], where most of the complexity of the netty system is abstracted away. It uses a message and handler style system.

[netty]: https://netty.io "Netty Website"
[channel]: ./simpleimpl.md "SimpleImpl in Detail"

---

SimpleImpl
==========

SimpleImpl is the name given to the packet system that revolves around the `SimpleChannel` class. Using this system is by far the easiest way to send custom data between clients and the server.

Getting Started
---------------

First you need to create your `SimpleChannel` object. We recommend that you do this in a separate class, possibly something like `ModidPacketHandler`. Create your `SimpleChannel` as a static field in this class, like so:

```java
private static final String PROTOCOL_VERSION = "1";
public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
  ResourceLocation.fromNamespaceAndPath("mymodid", "main"),
  () -> PROTOCOL_VERSION,
  PROTOCOL_VERSION::equals,
  PROTOCOL_VERSION::equals
);
```

The first argument is a name for the channel. The second argument is a `Supplier<String>` returning the current network protocol version. The third and fourth arguments respectively are `Predicate<String>` checking whether an incoming connection protocol version is network-compatible with the client or server, respectively.
Here, we simply compare with the `PROTOCOL_VERSION` field directly, meaning that the client and server `PROTOCOL_VERSION`s must always match or FML will deny login.

The Version Checker
-------------------

If your mod does not require the other side to have a specific network channel, or to be a Forge instance at all, you should take care that you properly define your version compatibility checkers (the `Predicate<String>` parameters) to handle additional "meta-versions" (defined in `NetworkRegistry`) that can be received by the version checker. These are:

* `ABSENT` - if this channel is missing on the other endpoint. Note that in this case, the endpoint is still a Forge endpoint, and may have other mods.
* `ACCEPTVANILLA` - if the endpoint is a vanilla (or non-Forge) endpoint.

Returning `false` for both means that this channel must be present on the other endpoint. If you just copy the code above, this is what it does. Note that these values are also used during the list ping compatibility check, which is responsible for showing the green check / red cross in the multiplayer server select screen.

Registering Packets
-------------------

Next, we must declare the types of messages that we would like to send and receive. This is done using `INSTANCE#registerMessage`, which takes 5 parameters:

- The first parameter is the discriminator for the packet. This is a per-channel unique ID for the packet. We recommend you use a local variable to hold the ID, and then call registerMessage using `id++`. This will guarantee 100% unique IDs.
- The second parameter is the actual packet class `MSG`.
- The third parameter is a `BiConsumer<MSG, FriendlyByteBuf>` responsible for encoding the message into the provided `FriendlyByteBuf`.
- The fourth parameter is a `Function<FriendlyByteBuf, MSG>` responsible for decoding the message from the provided `FriendlyByteBuf`.
- The final parameter is a `BiConsumer<MSG, Supplier<NetworkEvent.Context>>` responsible for handling the message itself.

The last three parameters can be method references to either static or instance methods in Java. Remember that an instance method `MSG#encode(FriendlyByteBuf)` still satisfies `BiConsumer<MSG, FriendlyByteBuf>`; the `MSG` simply becomes the implicit first argument.

Handling Packets
----------------

There are a couple things to highlight in a packet handler. A packet handler has both the message object and the network context available to it. The context allows access to the player that sent the packet (if on the server), and a way to enqueue thread-safe work.

```java
public static void handle(MyMessage msg, Supplier<NetworkEvent.Context> ctx) {
  ctx.get().enqueueWork(() -> {
    // Work that needs to be thread-safe (most work)
    ServerPlayer sender = ctx.get().getSender(); // the client that sent this packet
    // Do stuff
  });
  ctx.get().setPacketHandled(true);
}
```

Packets sent from the server to the client should be handled in another class and wrapped via `DistExecutor#unsafeRunWhenOn`.

```java
// In Packet class
public static void handle(MyClientMessage msg, Supplier<NetworkEvent.Context> ctx) {
  ctx.get().enqueueWork(() ->
    // Make sure it's only executed on the physical client
    DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> ClientPacketHandlerClass.handlePacket(msg, ctx))
  );
  ctx.get().setPacketHandled(true);
}

// In ClientPacketHandlerClass
public static void handlePacket(MyClientMessage msg, Supplier<NetworkEvent.Context> ctx) {
  // Do stuff
}
```

Note the presence of `#setPacketHandled`, which is used to tell the network system that the packet has successfully completed handling.

!!! warning
    As of Minecraft 1.8 packets are by default handled on the network thread.

    That means that your handler can _not_ interact with most game objects directly. Forge provides a convenient way to make your code execute on the main thread instead through the supplied `NetworkEvent$Context`. Simply call `NetworkEvent$Context#enqueueWork(Runnable)`, which will call the given `Runnable` on the main thread at the next opportunity.

!!! warning
    Be defensive when handling packets on the server. A client could attempt to exploit the packet handling by sending unexpected data.

    A common problem is vulnerability to **arbitrary chunk generation**. This typically happens when the server is trusting a block position sent by a client to access blocks and block entities. When accessing blocks and block entities in unloaded areas of the level, the server will either generate or load this area from disk, then promptly write it to disk. This can be exploited to cause **catastrophic damage** to a server's performance and storage space without leaving a trace.

    To avoid this problem, a general rule of thumb is to only access blocks and block entities if `Level#hasChunkAt` is true.


Sending Packets
---------------

### Sending to the Server

There is but one way to send a packet to the server. This is because there is only ever *one* server the client can be connected to at once. To do so, we must again use that `SimpleChannel` that was defined earlier. Simply call `INSTANCE.sendToServer(new MyMessage())`. The message will be sent to the handler for its type, if one exists.

### Sending to Clients

Packets can be sent directly to a client using the `SimpleChannel`: `HANDLER.sendTo(new MyClientMessage(), serverPlayer.connection.getConnection(), NetworkDirection.PLAY_TO_CLIENT)`. However, this can be quite inconvenient. Forge has some convenience functions that can be used:

```java
// Send to one player
INSTANCE.send(PacketDistributor.PLAYER.with(serverPlayer), new MyMessage());

// Send to all players tracking this level chunk
INSTANCE.send(PacketDistributor.TRACKING_CHUNK.with(levelChunk), new MyMessage());

// Send to all connected players
INSTANCE.send(PacketDistributor.ALL.noArg(), new MyMessage());
```

There are additional `PacketDistributor` types available; check the documentation on the `PacketDistributor` class for more details.

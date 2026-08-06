# Forge 网络通信指南 (SimpleChannel)

> **加载器**: Forge 65.x (MC 26.2)  
> **用途**: 服务端↔客户端数据同步。

---

## SimpleChannel 注册模板

```java
public class ModNetworking {
    private static final String PROTOCOL_VERSION = "1";
    public static final SimpleChannel CHANNEL = ChannelBuilder.named(
            ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "main"))
        .serverAcceptedVersions((s, v) -> true)
        .clientAcceptedVersions((s, v) -> true)
        .networkProtocolVersion(1)
        .simpleChannel();

    private static int packetId = 0;

    public static void register() {
        CHANNEL.messageBuilder(MyS2CPacket.class, packetId++, NetworkDirection.PLAY_TO_CLIENT)
            .encoder(MyS2CPacket::encode)
            .decoder(MyS2CPacket::new)
            .consumerMainThread(MyS2CPacket::handle)
            .add();

        CHANNEL.messageBuilder(MyC2SPacket.class, packetId++, NetworkDirection.PLAY_TO_SERVER)
            .encoder(MyC2SPacket::encode)
            .decoder(MyC2SPacket::new)
            .consumerMainThread(MyC2SPacket::handle)
            .add();
    }
}
```

---

## 数据包定义模板

### S2C (Server to Client)
```java
public class SyncDataPacket {
    private final int data;
    public SyncDataPacket(int data) { this.data = data; }
    public SyncDataPacket(FriendlyByteBuf buf) { this.data = buf.readVarInt(); }
    public void encode(FriendlyByteBuf buf) { buf.writeVarInt(data); }
    public static void handle(SyncDataPacket msg, CustomPacketPayload.Context ctx) {
        ctx.enqueueWork(() -> ClientDataHolder.set(msg.data));
    }
}
```

### C2S (Client to Server)
```java
public class RequestDataPacket {
    public RequestDataPacket() {}
    public RequestDataPacket(FriendlyByteBuf buf) {}
    public void encode(FriendlyByteBuf buf) {}
    public static void handle(RequestDataPacket msg, CustomPacketPayload.Context ctx) {
        ctx.enqueueWork(() -> {
            ServerPlayer player = ctx.getSender();
            // 服务端处理
        });
    }
}
```

---

## 发送方式

```java
// 发给特定玩家
PacketDistributor.PLAYER.with(() -> serverPlayer).send(new SyncDataPacket(42));

// 发给追踪实体的所有玩家
PacketDistributor.TRACKING_ENTITY.with(() -> entity).send(new SyncDataPacket(42));

// 发给追踪区块的所有玩家
PacketDistributor.TRACKING_CHUNK.with(() -> chunk).send(new SyncDataPacket(42));

// 发给所有玩家
PacketDistributor.ALL.noArg().send(new SyncDataPacket(42));

// 客户端发给服务端
PacketDistributor.sendToServer(new RequestDataPacket());
```

---

## 序列化方法速查

| 类型 | write | read |
|------|-------|------|
| int | `writeVarInt(v)` | `readVarInt()` |
| String | `writeUtf(s)` | `readUtf()` |
| boolean | `writeBoolean(b)` | `readBoolean()` |
| BlockPos | `writeBlockPos(p)` | `readBlockPos()` |
| ItemStack | `writeItemStack(s)` | `readItemStack()` |
| CompoundTag | `writeNbt(t)` | `readNbt()` |
| UUID | `writeUUID(u)` | `readUUID()` |
| Enum | `writeEnum(e)` | `readEnum(Class)` |
| float | `writeFloat(f)` | `readFloat()` |
| long | `writeVarLong(v)` | `readVarLong()` |

# Forge Capability 系统指南

> **加载器**: Forge 65.x (MC 26.2) ★ Forge独有  
> **用途**: 给Entity/BlockEntity/ItemStack/Level/Chunk附加自定义数据和行为。

---

## 定义 Capability

### 接口定义
```java
public interface IManaStorage {
    int getMana();
    int getMaxMana();
    void setMana(int mana);
    default boolean canUse(int amount) { return getMana() >= amount; }
}
```

### 实现
```java
public class ManaStorage implements IManaStorage {
    private int mana;
    private final int maxMana;
    public ManaStorage(int max) { this.maxMana = max; }
    @Override public int getMana() { return mana; }
    @Override public int getMaxMana() { return maxMana; }
    @Override public void setMana(int m) { this.mana = Math.min(m, maxMana); }
}
```

### 注册
```java
public class ModCapabilities {
    public static final Capability<IManaStorage> MANA = CapabilityManager.get(new CapabilityToken<>(){});
}
```

---

## 附加到实体

### Provider
```java
public class ManaProvider implements ICapabilitySerializable<CompoundTag> {
    private final IManaStorage mana = new ManaStorage(100);
    private final LazyOptional<IManaStorage> optional = LazyOptional.of(() -> mana);

    @Override
    public <T> LazyOptional<T> getCapability(Capability<T> cap, @Nullable Direction side) {
        return cap == ModCapabilities.MANA ? optional.cast() : LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("mana", mana.getMana());
        return tag;
    }

    @Override
    public void deserializeNBT(CompoundTag tag) {
        mana.setMana(tag.getInt("mana"));
    }
}
```

### 附加事件
```java
@SubscribeEvent
public static void onAttachCapabilities(AttachCapabilitiesEvent<Entity> event) {
    if (event.getObject() instanceof Player) {
        event.addCapability(
            ResourceLocation.fromNamespaceAndPath(MyMod.MODID, "mana"),
            new ManaProvider()
        );
    }
}
```

---

## 读取 Capability

```java
// 从实体读取
player.getCapability(ModCapabilities.MANA).ifPresent(mana -> {
    int current = mana.getMana();
    mana.setMana(current - 10);
});

// 从物品读取
itemStack.getCapability(ModCapabilities.MANA).ifPresent(mana -> { ... });
```

---

## 死亡时保留数据

```java
@SubscribeEvent
public static void onPlayerClone(PlayerEvent.Clone event) {
    event.getOriginal().reviveCaps();
    event.getOriginal().getCapability(ModCapabilities.MANA).ifPresent(old ->
        event.getEntity().getCapability(ModCapabilities.MANA).ifPresent(newM ->
            newM.setMana(old.getMana())
        )
    );
    event.getOriginal().invalidateCaps();
}
```

---

## Agent 使用指南

| 需求场景 | Capability附着目标 |
|---------|------------------|
| 玩家魔力/技能/货币 | `Player` Entity |
| 自定义能量存储 | `BlockEntity` |
| 工具充能 | `ItemStack` |
| 世界全局数据 | `Level` |

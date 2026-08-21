---

name: forge-datastorage-saveddata
description: "Forge SavedData 持久化数据机制：SavedData 类继承、save 方法写入 NBT、setDirty 标记脏位、DimensionDataStorage#computeIfAbsent 动态加载/附加、ServerLevel#getDataStorage 获取数据存储、.dat 文件存储路径、数据加载函数（NBT → SD）、数据创建函数（Supplier）、跨维度持久化（Overworld 附加）、1.21.11+ SavedDataType 新 API（Codec<T> 定义、SavedDataType<T> 静态类型、DataFixTypes.SAVED_DATA_MAP_DATA）、旧版 DimensionDataStorage#computeIfAbsent 兼容方法、NBT 序列化/反序列化。"
whenToUse: "Use when attaching persistent data to a level in a Forge mod."

---

# Saved Data

The Saved Data (SD) system is an alternative to level capabilities for attaching data per level.

## Declaration

Each SD implementation must subtype the `SavedData` class:

- `save`: writes NBT data to the level.
- `setDirty`: must be called after changing data to mark it for writing; without it, `#save` is not called.

## Attaching to a level

`SavedData`s are loaded/attached dynamically — if never created on a level, they don't exist. Create or load one via `DimensionDataStorage#computeIfAbsent`, obtained from `ServerChunkCache#getDataStorage` or `ServerLevel#getDataStorage`. `computeIfAbsent` takes a load function (NBT → SD), a supplier (new instance), and the `.dat` file name in the level's `data` folder.

Example (SD named "example" in the Nether creates `./<level_folder>/DIM-1/data/example.dat`):

```java
public ExampleSavedData create() {
  return new ExampleSavedData();
}

public ExampleSavedData load(CompoundTag tag) {
  ExampleSavedData data = this.create();
  // Load saved data
  return data;
}

netherDataStorage.computeIfAbsent(this::load, this::create, "example");
```

To persist across levels, attach the SD to the Overworld (`MinecraftServer#overworld`) — the only dimension never fully unloaded.

## 1.21.11+ SavedData current API (verified from mc_java_sources)

In Forge 1.21.11, define a `Codec<MyData>` and a static `SavedDataType<MyData>`, then load with `computeIfAbsent(TYPE)`:

```java
public static final Codec<MyData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
    Codec.BOOL.optionalFieldOf("active", false).forGetter(d -> d.active)
).apply(instance, MyData::new));

public static final SavedDataType<MyData> TYPE = new SavedDataType<>(
    "mydata", MyData::new, CODEC, DataFixTypes.SAVED_DATA_MAP_DATA);

public static MyData get(ServerLevel level) {
    return level.getDataStorage().computeIfAbsent(TYPE);
}
```

The old `DimensionDataStorage#computeIfAbsent(String, Supplier, DataFixTypes)` still exists for compatibility, but the codec-based `SavedDataType` is the current pattern used by vanilla.
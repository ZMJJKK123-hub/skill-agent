---
name: forge-datastorage-saveddata
description: Forge SavedData: per-level persistent data via computeIfAbsent, save/setDirty.
whenToUse: Use when attaching persistent data to a level in a Forge mod.
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

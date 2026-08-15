---

name: forge-concept-registries
description: "Forge registries: DeferredRegister, RegisterEvent, RegistryObject, @ObjectHolder, custom registries."
whenToUse: "Use when registering Forge objects (items, blocks, etc.) or referencing registered objects."

---

# Registries

Registration makes a mod's objects known to the game. Registries map `ResourceLocation` keys to values; each registrable type has its own registry (`ForgeRegistries` lists Forge-wrapped ones). Names must be unique within a registry; different registries don't collide. Registering a second object with the same name overrides the first.

## Methods for registering

### DeferredRegister (recommended)

Maintains suppliers and registers during `RegisterEvent`:

```java
private static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, MODID);
public static final RegistryObject<Block> ROCK_BLOCK = BLOCKS.register("rock", () -> new Block(BlockBehaviour.Properties.of().mapColor(MapColor.STONE)));

public ExampleMod(FMLJavaModLoadingContext context) {
  BLOCKS.register(context.getModEventBus());
}
```

### RegisterEvent

Fired for each registry after mod constructors, before config loading. Register via `#register(registryKey, helper)` on the mod event bus:

```java
event.register(ForgeRegistries.Keys.BLOCKS, helper -> {
  helper.register(ResourceLocation.fromNamespaceAndPath(MODID, "example_block_1"), new Block(...));
});
```

### Registries that aren't Forge registries

- Static registries (e.g. `LootItemConditionType`): safe; use `DeferredRegister.create(Registries.LOOT_CONDITION_TYPE, MODID)`.
- Dynamic registries (worldgen JSON registries): **only registerable via data files, never in code**.

Some classes register `*Type` factories instead (e.g. `BlockEntityType`, `EntityType`), created via their builders:

```java
REGISTER.register("example_block_entity", () -> BlockEntityType.Builder.of(ExampleBlockEntity::new, EXAMPLE_BLOCK.get()).build(null));
```

## Referencing registered objects

Never store registered objects in fields at registration; always reference via `RegistryObject` or `@ObjectHolder`.

- `RegistryObject#create(resourceLocation, registry)` → store in `public static final` fields, call `#get()`.
- `@ObjectHolder(registryName = "...", value = "...")` on `public static` fields injects objects after `RegisterEvent`. Class-level `@ObjectHolder` or `@Mod` provides the default namespace. Missing registry/name → compile-time exception; missing object at injection → debug log, no injection.

## Creating custom Forge registries

Use `RegistryBuilder` via `NewRegistryEvent` or `DeferredRegister`:

- `NewRegistryEvent#create(builder)` returns a supplier-wrapped registry (null before the event finishes).
- `DeferredRegister#makeRegistry(builder)` (must be called before `#register` on the bus).
- Datapack registries: `DataPackRegistryEvent$NewRegistry#dataPackRegistry(resourceKey, codec, optionalSyncCodec)` — **cannot** use `DeferredRegister`.

## Missing entries

`MissingMappingsEvent` (fired on the **Forge** bus) handles removed registry objects: `#getMappings(registryKey, modid)` / `#getAllMappings`. Per `Mapping`, choose: `IGNORE` (abandon), `WARN` (log warning), `FAIL` (block world load), `REMAP` (remap to an existing non-null object). Default action asks the user whether to load the world.

---

name: forge-blockentities
description: "Forge BlockEntity guide: registration, data storage, ticking, client sync, and BlockEntityRenderers."
whenToUse: "Use when implementing Forge block entities or block entity renderers."

---

# BlockEntities

`BlockEntities` are like simplified `Entities` bound to a Block: they store dynamic data, execute tick-based tasks, and do dynamic rendering (chest inventories, furnace smelting, beacon effects). They can cause lag when misused — avoid them when possible.

## Registering

Block entities are created/removed dynamically; you register a `BlockEntityType` (constructed with a `BlockEntityType$BlockEntitySupplier` and a `Set<Block>` of attachable blocks):

```java
public static final RegistryObject<BlockEntityType<MyBE>> MY_BE = REGISTER.register("mybe", () -> new BlockEntityType(MyBE::new, Set.of(validBlocks)));

// In MyBE
public MyBE(BlockPos pos, BlockState state) {
  super(MY_BE.get(), pos, state);
}
```

> Before 1.21.3, use `BlockEntityType$Builder#of(supplier, blocks...)` then `#build(null)`.

## Creating

Implement `EntityBlock#newBlockEntity(BlockPos, BlockState)` on the block to attach a block entity.

## Storing data

Override `BlockEntity#saveAdditional(CompoundTag)` and `BlockEntity#load(CompoundTag)`; call `BlockEntity#setChanged()` on data changes. **Always call the super methods** — `id`, `x`, `y`, `z`, `ForgeData`, `ForgeCaps` are reserved.

## Ticking

Implement `EntityBlock#getTicker(Level, BlockState, BlockEntityType)` returning a `BlockEntityTicker` (e.g. `type == MY_BE.get() ? MyBlockEntity::tick : null`). Keep per-tick work light; do complex calculations every X ticks.

## Synchronizing to the client

1. **On chunk load**: override `getUpdateTag()` and `IForgeBlockEntity#handleUpdateTag(CompoundTag)`. Send only needed data — inventories usually sync via `AbstractContainerMenu` instead.
2. **On block update**: `getUpdatePacket()` returning `ClientboundBlockEntityDataPacket.create(this)`, then notify with `Level#sendBlockUpdated(pos, oldState, newState, flags)` (flags containing `2` = `Block#UPDATE_CLIENTS`).
3. **Custom network message**: via `SimpleChannel#send(PacketDistributor, MSG)`. Safety-check that the block entity still exists and the chunk is loaded (`Level#hasChunkAt`).

# BlockEntityRenderer

A BER renders blocks that a static baked model cannot represent (JSON/OBJ/B3D). The block must have a block entity.

## Creating a BER

Subclass `BlockEntityRenderer<YourBlockEntity>`. One BER exists per `BlockEntityType` — store instance-specific values in the block entity, not the BER.

`render` parameters: `blockEntity`, `partialTick` (fraction of a tick since last full tick), `poseStack` (matrix stack offset to the block entity), `bufferSource`, `combinedLight`, `combinedOverlay` (usually `OverlayTexture#NO_OVERLAY` = 655,360).

## Registering a BER

Subscribe to `EntityRenderersEvent$RegisterRenderers` on the mod event bus and call `#registerBlockEntityRenderer`.

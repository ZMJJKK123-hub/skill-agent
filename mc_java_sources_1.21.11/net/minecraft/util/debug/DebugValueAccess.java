package net.minecraft.util.debug;

import java.util.function.BiConsumer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import org.jspecify.annotations.Nullable;

public interface DebugValueAccess {
    <T> void forEachChunk(DebugSubscription<T> p_431573_, BiConsumer<ChunkPos, T> p_427196_);

    <T> @Nullable T getChunkValue(DebugSubscription<T> p_422421_, ChunkPos p_425150_);

    <T> void forEachBlock(DebugSubscription<T> p_423780_, BiConsumer<BlockPos, T> p_422845_);

    <T> @Nullable T getBlockValue(DebugSubscription<T> p_426579_, BlockPos p_424108_);

    <T> void forEachEntity(DebugSubscription<T> p_429971_, BiConsumer<Entity, T> p_427937_);

    <T> @Nullable T getEntityValue(DebugSubscription<T> p_431438_, Entity p_424713_);

    <T> void forEachEvent(DebugSubscription<T> p_425113_, DebugValueAccess.EventVisitor<T> p_427490_);

    @FunctionalInterface
    public interface EventVisitor<T> {
        void accept(T p_425042_, int p_431703_, int p_425916_);
    }
}

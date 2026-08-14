package net.minecraft.world.level.chunk.storage;

import java.util.function.Supplier;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.ChunkPos;

@FunctionalInterface
public interface LegacyTagFixer {
    Supplier<LegacyTagFixer> EMPTY = () -> p_456738_ -> p_456738_;

    CompoundTag applyFix(CompoundTag p_455082_);

    default void markChunkDone(ChunkPos p_456889_) {
    }

    default int targetDataVersion() {
        return -1;
    }
}

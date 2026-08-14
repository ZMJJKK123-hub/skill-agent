package net.minecraft.server.level.progress;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import org.jspecify.annotations.Nullable;

public interface ChunkLoadStatusView {
    void moveTo(ResourceKey<Level> p_428992_, ChunkPos p_430352_);

    @Nullable ChunkStatus get(int p_426164_, int p_424998_);

    int radius();
}

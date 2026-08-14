package net.minecraft.world.level.chunk;

import net.minecraft.core.SectionPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LightLayer;
import org.jspecify.annotations.Nullable;

public interface LightChunkGetter {
    @Nullable LightChunk getChunkForLighting(int p_63023_, int p_63024_);

    default void onLightUpdate(LightLayer p_63021_, SectionPos p_63022_) {
    }

    BlockGetter getLevel();
}

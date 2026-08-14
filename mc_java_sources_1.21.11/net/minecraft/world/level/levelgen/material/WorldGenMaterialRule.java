package net.minecraft.world.level.levelgen.material;

import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.NoiseChunk;
import org.jspecify.annotations.Nullable;

public interface WorldGenMaterialRule {
    @Nullable BlockState apply(NoiseChunk p_191553_, int p_191554_, int p_191555_, int p_191556_);
}

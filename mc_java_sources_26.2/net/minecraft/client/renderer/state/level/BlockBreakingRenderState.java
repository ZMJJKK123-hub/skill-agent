package net.minecraft.client.renderer.state.level;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.model.data.ModelData;

@OnlyIn(Dist.CLIENT)
public record BlockBreakingRenderState(BlockPos blockPos, BlockState blockState, int progress, ModelData data) {
   public BlockBreakingRenderState(BlockPos blockPos, BlockState blockState, int progress) {
      this(blockPos, blockState, progress, ModelData.EMPTY);
   }
}

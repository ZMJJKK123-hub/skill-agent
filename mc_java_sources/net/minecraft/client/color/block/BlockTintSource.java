package net.minecraft.client.color.block;

import java.util.Set;
import net.minecraft.client.renderer.block.BlockAndTintGetter;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface BlockTintSource {
   int color(BlockState var1);

   default int colorInWorld(BlockState state, BlockAndTintGetter level, BlockPos pos) {
      return this.color(state);
   }

   default int colorAsTerrainParticle(BlockState state, BlockAndTintGetter level, BlockPos pos) {
      return this.colorInWorld(state, level, pos);
   }

   default Set<Property<?>> relevantProperties() {
      return Set.of();
   }
}

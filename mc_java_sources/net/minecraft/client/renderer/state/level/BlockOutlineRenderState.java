package net.minecraft.client.renderer.state.level;

import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.event.RenderHighlightEvent;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public record BlockOutlineRenderState(
   BlockPos pos,
   boolean isTranslucent,
   boolean highContrast,
   VoxelShape shape,
   @Nullable VoxelShape collisionShape,
   @Nullable VoxelShape occlusionShape,
   @Nullable VoxelShape interactionShape,
   RenderHighlightEvent.@Nullable Callback customRenderer
) {
   public BlockOutlineRenderState(BlockPos pos, boolean isTranslucent, boolean highContrast, VoxelShape shape) {
      this(pos, isTranslucent, highContrast, shape, null, null, null);
   }

   public BlockOutlineRenderState(
      BlockPos pos,
      boolean isTranslucent,
      boolean highContrast,
      VoxelShape shape,
      @Nullable VoxelShape collisionShape,
      @Nullable VoxelShape occlusionShape,
      @Nullable VoxelShape interactionShape
   ) {
      this(pos, isTranslucent, highContrast, shape, collisionShape, occlusionShape, interactionShape, null);
   }
}

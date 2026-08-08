package net.minecraft.client.renderer.special;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.serialization.MapCodec;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface NoDataSpecialModelRenderer extends SpecialModelRenderer<Void> {
   default @Nullable Void extractArgument(ItemStack stack) {
      return null;
   }

   default void submit(
      @Nullable Void argument,
      PoseStack poseStack,
      SubmitNodeCollector submitNodeCollector,
      int lightCoords,
      int overlayCoords,
      boolean hasFoil,
      int outlineColor
   ) {
      this.submit(poseStack, submitNodeCollector, lightCoords, overlayCoords, hasFoil, outlineColor);
   }

   void submit(PoseStack var1, SubmitNodeCollector var2, int var3, int var4, boolean var5, int var6);

   @OnlyIn(Dist.CLIENT)
   interface Unbaked extends SpecialModelRenderer.Unbaked<Void> {
      @Override
      MapCodec<? extends NoDataSpecialModelRenderer.Unbaked> type();
   }
}

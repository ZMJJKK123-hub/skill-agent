package net.minecraft.client.renderer.feature;

import java.util.List;
import net.minecraft.client.renderer.feature.submit.SubmitNode;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface FeatureRenderer<Submit extends SubmitNode> extends AutoCloseable {
   default void beginPrepare(FeatureFrameContext context) {
   }

   void prepareGroup(FeatureFrameContext var1, List<Submit> var2, boolean var3);

   default void finishPrepare(FeatureFrameContext context) {
   }

   void executeGroup(FeatureFrameContext var1, int var2, List<Submit> var3, boolean var4);

   default void finishExecute(FeatureFrameContext context) {
   }

   @Override
   default void close() {
   }
}

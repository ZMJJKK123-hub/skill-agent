package net.minecraft.client.renderer.feature.phase;

import java.util.Collection;
import net.minecraft.client.renderer.feature.FeatureRendererType;
import net.minecraft.client.renderer.feature.submit.SubmitNode;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface FeatureRenderPhase<Submit extends SubmitNode> {
   void submit(Submit var1);

   void sortInto(FeatureRenderPhase.Output var1);

   boolean isEmpty();

   @FunctionalInterface
   @OnlyIn(Dist.CLIENT)
   interface Output {
      void accept(SubmitNode var1, boolean var2);

      default <Submit extends SubmitNode> void acceptFeatureGroup(FeatureRendererType<Submit> featureType, Collection<Submit> submits, boolean strictlyOrdered) {
         for (Submit submit : submits) {
            if (submit.featureType() != featureType) {
               throw new IllegalArgumentException(submit + " was not of feature type " + featureType);
            }

            this.accept(submit, strictlyOrdered);
         }
      }
   }
}

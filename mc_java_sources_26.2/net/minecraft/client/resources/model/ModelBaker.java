package net.minecraft.client.resources.model;

import net.minecraft.client.renderer.block.dispatch.BlockStateModelPart;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.sprite.MaterialBaker;
import net.minecraft.resources.Identifier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.RenderTypeGroup;
import org.jetbrains.annotations.Nullable;
import org.joml.Vector3fc;

@OnlyIn(Dist.CLIENT)
public interface ModelBaker {
   ResolvedModel getModel(Identifier var1);

   BlockStateModelPart missingBlockModelPart();

   MaterialBaker materials();

   ModelBaker.Interner interner();

   <T> T compute(ModelBaker.SharedOperationKey<T> var1);

   @Nullable
   default RenderTypeGroup renderType() {
      return null;
   }

   @Nullable
   default RenderTypeGroup renderTypeFast() {
      return null;
   }

   @OnlyIn(Dist.CLIENT)
   interface Interner {
      Vector3fc vector(Vector3fc var1);

      BakedQuad.MaterialInfo materialInfo(BakedQuad.MaterialInfo var1);
   }

   @FunctionalInterface
   @OnlyIn(Dist.CLIENT)
   interface SharedOperationKey<T> {
      T compute(ModelBaker var1);
   }
}

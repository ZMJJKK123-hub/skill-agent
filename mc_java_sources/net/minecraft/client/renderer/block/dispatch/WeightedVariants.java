package net.minecraft.client.renderer.block.dispatch;

import java.util.List;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.util.RandomSource;
import net.minecraft.util.random.Weighted;
import net.minecraft.util.random.WeightedList;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.model.data.ModelData;

@OnlyIn(Dist.CLIENT)
public class WeightedVariants implements BlockStateModel {
   private final WeightedList<BlockStateModel> list;
   private final Material.Baked particleMaterial;
   private final @BakedQuad.MaterialFlags int materialFlags;
   private final BlockStateModel first;

   public WeightedVariants(WeightedList<BlockStateModel> list) {
      this.list = list;
      BlockStateModel firstModel = list.unwrap().getFirst().value();
      this.particleMaterial = firstModel.particleMaterial();
      this.first = firstModel;
      this.materialFlags = computeMaterialFlags(list);
   }

   private static @BakedQuad.MaterialFlags int computeMaterialFlags(WeightedList<BlockStateModel> list) {
      int flags = 0;

      for (Weighted<BlockStateModel> entry : list.unwrap()) {
         flags |= entry.value().materialFlags();
      }

      return flags;
   }

   @Override
   public Material.Baked particleMaterial() {
      return this.particleMaterial;
   }

   @Override
   public Material.Baked particleMaterial(ModelData data) {
      return this.first.particleMaterial(data);
   }

   @Override
   public @BakedQuad.MaterialFlags int materialFlags() {
      return this.materialFlags;
   }

   @Override
   public void collectParts(RandomSource random, List<BlockStateModelPart> output) {
      this.list.getRandomOrThrow(random).collectParts(random, output);
   }

   @Override
   public void collectParts(RandomSource random, List<BlockStateModelPart> output, ModelData data) {
      this.list.getRandomOrThrow(random).collectParts(random, output, data);
   }

   @OnlyIn(Dist.CLIENT)
   public record Unbaked(WeightedList<BlockStateModel.Unbaked> entries) implements BlockStateModel.Unbaked {
      @Override
      public BlockStateModel bake(ModelBaker modelBakery) {
         return new WeightedVariants(this.entries.map(m -> m.bake(modelBakery)));
      }

      @Override
      public void resolveDependencies(ResolvableModel.Resolver resolver) {
         this.entries.unwrap().forEach(v -> v.value().resolveDependencies(resolver));
      }
   }
}

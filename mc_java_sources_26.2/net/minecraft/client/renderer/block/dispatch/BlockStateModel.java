package net.minecraft.client.renderer.block.dispatch;

import com.google.common.collect.Lists;
import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.util.RandomSource;
import net.minecraft.util.random.Weighted;
import net.minecraft.util.random.WeightedList;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.extensions.IForgeBlockStateModel;

@OnlyIn(Dist.CLIENT)
public interface BlockStateModel extends IForgeBlockStateModel {
   /** @deprecated */
   void collectParts(RandomSource var1, List<BlockStateModelPart> var2);

   /** @deprecated */
   Material.Baked particleMaterial();

   @BakedQuad.MaterialFlags int materialFlags();

   default boolean hasMaterialFlag(@BakedQuad.MaterialFlags int flag) {
      return (this.materialFlags() & flag) != 0;
   }

   @OnlyIn(Dist.CLIENT)
   class SimpleCachedUnbakedRoot implements BlockStateModel.UnbakedRoot {
      private final BlockStateModel.Unbaked contents;
      private final ModelBaker.SharedOperationKey<BlockStateModel> bakingKey = new ModelBaker.SharedOperationKey<BlockStateModel>() {
         public BlockStateModel compute(ModelBaker modelBakery) {
            return SimpleCachedUnbakedRoot.this.contents.bake(modelBakery);
         }
      };

      public SimpleCachedUnbakedRoot(BlockStateModel.Unbaked contents) {
         this.contents = contents;
      }

      @Override
      public void resolveDependencies(ResolvableModel.Resolver resolver) {
         this.contents.resolveDependencies(resolver);
      }

      @Override
      public BlockStateModel bake(BlockState blockState, ModelBaker modelBakery) {
         return modelBakery.compute(this.bakingKey);
      }

      @Override
      public Object visualEqualityGroup(BlockState blockState) {
         return this;
      }
   }

   @OnlyIn(Dist.CLIENT)
   interface Unbaked extends ResolvableModel {
      Codec<Weighted<Variant>> ELEMENT_CODEC = RecordCodecBuilder.create(
         i -> i.group(Variant.MAP_CODEC.forGetter(Weighted::value), ExtraCodecs.POSITIVE_INT.optionalFieldOf("weight", 1).forGetter(Weighted::weight))
            .apply(i, Weighted::new)
      );
      Codec<WeightedVariants.Unbaked> HARDCODED_WEIGHTED_CODEC = ExtraCodecs.nonEmptyList(ELEMENT_CODEC.listOf())
         .flatComapMap(w -> new WeightedVariants.Unbaked(WeightedList.of(Lists.transform(w, e -> e.map(SingleVariant.Unbaked::new)))), unbaked -> {
            List<Weighted<BlockStateModel.Unbaked>> entries = unbaked.entries().unwrap();
            List<Weighted<Variant>> result = new ArrayList<>(entries.size());

            for (Weighted<BlockStateModel.Unbaked> entry : entries) {
               if (!(entry.value() instanceof SingleVariant.Unbaked singleVariant)) {
                  return DataResult.error(() -> "Only single variants are supported");
               }

               result.add(new Weighted<>(singleVariant.variant(), entry.weight()));
            }

            return DataResult.success(result);
         });
      Codec<BlockStateModel.Unbaked> CODEC = Codec.either(HARDCODED_WEIGHTED_CODEC, SingleVariant.Unbaked.CODEC)
         .flatComapMap(v -> (BlockStateModel.Unbaked)v.map(l -> l, r -> r), o -> {
            return switch (o) {
               case SingleVariant.Unbaked single -> DataResult.success(Either.right(single));
               case WeightedVariants.Unbaked multiple -> DataResult.success(Either.left(multiple));
               default -> DataResult.error(() -> "Only a single variant or a list of variants are supported");
            };
         });

      BlockStateModel bake(ModelBaker var1);

      default BlockStateModel.UnbakedRoot asRoot() {
         return new BlockStateModel.SimpleCachedUnbakedRoot(this);
      }
   }

   @OnlyIn(Dist.CLIENT)
   interface UnbakedRoot extends ResolvableModel {
      BlockStateModel bake(BlockState var1, ModelBaker var2);

      Object visualEqualityGroup(BlockState var1);
   }
}

package net.minecraft.client.renderer.block.dispatch.multipart;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableList.Builder;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.ints.IntList;
import java.util.BitSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Predicate;
import net.minecraft.client.renderer.block.dispatch.BlockStateModel;
import net.minecraft.client.renderer.block.dispatch.BlockStateModelPart;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraft.client.resources.model.sprite.Material;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.model.data.ModelData;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public class MultiPartModel implements BlockStateModel {
   private final MultiPartModel.SharedBakedState shared;
   private final BlockState blockState;
   private @Nullable List<BlockStateModel> models;

   private MultiPartModel(MultiPartModel.SharedBakedState shared, BlockState blockState) {
      this.shared = shared;
      this.blockState = blockState;
   }

   @Override
   public Material.Baked particleMaterial() {
      return this.shared.particleMaterial;
   }

   @Override
   public Material.Baked particleMaterial(ModelData data) {
      if (this.models == null) {
         this.models = this.shared.selectModels(this.blockState);
      }

      return this.models.getFirst().particleMaterial(data);
   }

   @Override
   public @BakedQuad.MaterialFlags int materialFlags() {
      return this.shared.materialFlags;
   }

   @Override
   public void collectParts(RandomSource random, List<BlockStateModelPart> output) {
      this.collectParts(random, output, ModelData.EMPTY);
   }

   @Override
   public void collectParts(RandomSource random, List<BlockStateModelPart> output, ModelData data) {
      if (this.models == null) {
         this.models = this.shared.selectModels(this.blockState);
      }

      long seed = random.nextLong();

      for (BlockStateModel model : this.models) {
         random.setSeed(seed);
         model.collectParts(random, output, data);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public record Selector<T>(Predicate<BlockState> condition, T model) {
      public <S> MultiPartModel.Selector<S> with(S newModel) {
         return new MultiPartModel.Selector<>(this.condition, newModel);
      }
   }

   @OnlyIn(Dist.CLIENT)
   private static final class SharedBakedState {
      private final List<MultiPartModel.Selector<BlockStateModel>> selectors;
      private final Material.Baked particleMaterial;
      private final @BakedQuad.MaterialFlags int materialFlags;
      private final Map<BitSet, List<BlockStateModel>> subsets = new ConcurrentHashMap<>();

      private static BlockStateModel getFirstModel(List<MultiPartModel.Selector<BlockStateModel>> selectors) {
         if (selectors.isEmpty()) {
            throw new IllegalArgumentException("Model must have at least one selector");
         } else {
            return selectors.getFirst().model();
         }
      }

      private static @BakedQuad.MaterialFlags int computeMaterialFlags(List<MultiPartModel.Selector<BlockStateModel>> selectors) {
         int flags = 0;

         for (MultiPartModel.Selector<BlockStateModel> selector : selectors) {
            flags |= selector.model.materialFlags();
         }

         return flags;
      }

      public SharedBakedState(List<MultiPartModel.Selector<BlockStateModel>> selectors) {
         this.selectors = selectors;
         BlockStateModel firstModel = getFirstModel(selectors);
         this.particleMaterial = firstModel.particleMaterial();
         this.materialFlags = computeMaterialFlags(selectors);
      }

      public List<BlockStateModel> selectModels(BlockState state) {
         BitSet selectedModels = new BitSet();

         for (int i = 0; i < this.selectors.size(); i++) {
            if (this.selectors.get(i).condition.test(state)) {
               selectedModels.set(i);
            }
         }

         return this.subsets.computeIfAbsent(selectedModels, selected -> {
            Builder<BlockStateModel> result = ImmutableList.builder();

            for (int ix = 0; ix < this.selectors.size(); ix++) {
               if (selected.get(ix)) {
                  result.add(this.selectors.get(ix).model);
               }
            }

            return result.build();
         });
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class Unbaked implements BlockStateModel.UnbakedRoot {
      private final List<MultiPartModel.Selector<BlockStateModel.Unbaked>> selectors;
      private final ModelBaker.SharedOperationKey<MultiPartModel.SharedBakedState> sharedStateKey = new ModelBaker.SharedOperationKey<MultiPartModel.SharedBakedState>(
         
      ) {
         public MultiPartModel.SharedBakedState compute(ModelBaker modelBakery) {
            Builder<MultiPartModel.Selector<BlockStateModel>> selectors = ImmutableList.builderWithExpectedSize(Unbaked.this.selectors.size());

            for (MultiPartModel.Selector<BlockStateModel.Unbaked> selector : Unbaked.this.selectors) {
               selectors.add(selector.with(selector.model.bake(modelBakery)));
            }

            return new MultiPartModel.SharedBakedState(selectors.build());
         }
      };

      public Unbaked(List<MultiPartModel.Selector<BlockStateModel.Unbaked>> selectors) {
         this.selectors = selectors;
      }

      @Override
      public Object visualEqualityGroup(BlockState blockState) {
         IntList triggeredSelectors = new IntArrayList();

         for (int i = 0; i < this.selectors.size(); i++) {
            if (this.selectors.get(i).condition.test(blockState)) {
               triggeredSelectors.add(i);
            }
         }

         @OnlyIn(Dist.CLIENT)
         record Key(MultiPartModel.Unbaked model, IntList selectors) {
         }

         return new Key(this, triggeredSelectors);
      }

      @Override
      public void resolveDependencies(ResolvableModel.Resolver resolver) {
         this.selectors.forEach(s -> s.model.resolveDependencies(resolver));
      }

      @Override
      public BlockStateModel bake(BlockState blockState, ModelBaker modelBakery) {
         MultiPartModel.SharedBakedState shared = modelBakery.compute(this.sharedStateKey);
         return new MultiPartModel(shared, blockState);
      }
   }
}

package net.minecraft.client.renderer.block.model;

import java.util.function.Function;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.PlayerSkinRenderCache;
import net.minecraft.client.renderer.block.BlockModelRenderState;
import net.minecraft.client.renderer.block.dispatch.BlockStateModel;
import net.minecraft.client.renderer.special.SpecialModelRenderer;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4fc;

@OnlyIn(Dist.CLIENT)
public interface BlockModel {
   void update(BlockModelRenderState var1, BlockState var2, BlockDisplayContext var3, long var4);

   @OnlyIn(Dist.CLIENT)
   record BakingContext(
      EntityModelSet entityModelSet,
      SpriteGetter sprites,
      PlayerSkinRenderCache playerSkinRenderCache,
      Function<BlockState, BlockStateModel> modelGetter,
      BlockModel missingBlockModel
   ) implements SpecialModelRenderer.BakingContext {
   }

   @OnlyIn(Dist.CLIENT)
   interface Unbaked {
      BlockModel bake(BlockModel.BakingContext var1, Matrix4fc var2);
   }
}

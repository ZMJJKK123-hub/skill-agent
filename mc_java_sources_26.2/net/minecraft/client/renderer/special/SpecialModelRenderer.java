package net.minecraft.client.renderer.special;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.serialization.MapCodec;
import java.util.function.Consumer;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.PlayerSkinRenderCache;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface SpecialModelRenderer<T> {
   void submit(@Nullable T var1, PoseStack var2, SubmitNodeCollector var3, int var4, int var5, boolean var6, int var7);

   void getExtents(Consumer<Vector3fc> var1);

   @Nullable T extractArgument(ItemStack var1);

   @OnlyIn(Dist.CLIENT)
   interface BakingContext {
      EntityModelSet entityModelSet();

      SpriteGetter sprites();

      PlayerSkinRenderCache playerSkinRenderCache();
   }

   @OnlyIn(Dist.CLIENT)
   interface Unbaked<T> {
      @Nullable SpecialModelRenderer<T> bake(SpecialModelRenderer.BakingContext var1);

      MapCodec<? extends SpecialModelRenderer.Unbaked<T>> type();
   }
}

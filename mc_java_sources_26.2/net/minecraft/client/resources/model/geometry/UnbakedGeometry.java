package net.minecraft.client.resources.model.geometry;

import net.minecraft.client.renderer.block.dispatch.ModelState;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ModelDebugName;
import net.minecraft.client.resources.model.sprite.TextureSlots;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.model.geometry.IGeometryBakingContext;

@FunctionalInterface
@OnlyIn(Dist.CLIENT)
public interface UnbakedGeometry {
   UnbakedGeometry EMPTY = (var0, var1, var2, var3) -> QuadCollection.EMPTY;

   QuadCollection bake(TextureSlots var1, ModelBaker var2, ModelState var3, ModelDebugName var4);

   default QuadCollection bake(TextureSlots slots, ModelBaker baker, ModelState state, ModelDebugName name, IGeometryBakingContext context) {
      return this.bake(slots, baker, state, name);
   }
}

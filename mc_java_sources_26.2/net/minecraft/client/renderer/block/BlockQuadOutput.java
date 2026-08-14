package net.minecraft.client.renderer.block;

import com.mojang.blaze3d.vertex.QuadInstance;
import net.minecraft.client.resources.model.geometry.BakedQuad;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@FunctionalInterface
@OnlyIn(Dist.CLIENT)
public interface BlockQuadOutput {
   void put(float var1, float var2, float var3, BakedQuad var4, QuadInstance var5);
}

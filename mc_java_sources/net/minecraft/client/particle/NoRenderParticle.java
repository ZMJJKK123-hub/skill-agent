package net.minecraft.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class NoRenderParticle extends Particle {
   protected NoRenderParticle(ClientLevel level, double x, double y, double z) {
      super(level, x, y, z);
   }

   protected NoRenderParticle(ClientLevel level, double x, double y, double z, double xa, double ya, double za) {
      super(level, x, y, z, xa, ya, za);
   }

   @Override
   public ParticleRenderType getGroup() {
      return ParticleRenderType.NO_RENDER;
   }
}

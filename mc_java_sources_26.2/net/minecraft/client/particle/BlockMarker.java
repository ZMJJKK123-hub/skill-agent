package net.minecraft.client.particle;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class BlockMarker extends SingleQuadParticle {
   private final SingleQuadParticle.Layer layer;

   private BlockMarker(ClientLevel level, double x, double y, double z, BlockState state) {
      super(
         level,
         x,
         y,
         z,
         Minecraft.getInstance()
            .getModelManager()
            .getBlockStateModelSet()
            .get(state)
            .particleMaterial(level.getModelDataManager().getAtOrEmpty(x, y, z))
            .sprite()
      );
      this.gravity = 0.0F;
      this.lifetime = 80;
      this.hasPhysics = false;
      this.layer = SingleQuadParticle.Layer.bySprite(this.sprite);
   }

   @Override
   public SingleQuadParticle.Layer getLayer() {
      return this.layer;
   }

   @Override
   public float getQuadSize(float a) {
      return 0.5F;
   }

   @OnlyIn(Dist.CLIENT)
   public static class Provider implements ParticleProvider<BlockParticleOption> {
      public Particle createParticle(
         BlockParticleOption option, ClientLevel level, double x, double y, double z, double xAux, double yAux, double zAux, RandomSource random
      ) {
         return new BlockMarker(level, x, y, z, option.getState());
      }
   }
}

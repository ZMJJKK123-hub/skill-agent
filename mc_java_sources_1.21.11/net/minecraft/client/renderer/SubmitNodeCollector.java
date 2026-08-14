package net.minecraft.client.renderer;

import com.mojang.blaze3d.systems.RenderPass;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.feature.ParticleFeatureRenderer;
import net.minecraft.client.renderer.state.QuadParticleRenderState;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface SubmitNodeCollector extends OrderedSubmitNodeCollector {
    OrderedSubmitNodeCollector order(int p_426215_);

    @OnlyIn(Dist.CLIENT)
    public interface CustomGeometryRenderer {
        void render(PoseStack.Pose p_431077_, VertexConsumer p_431267_);
    }

    @OnlyIn(Dist.CLIENT)
    public interface ParticleGroupRenderer {
        QuadParticleRenderState.@Nullable PreparedBuffers prepare(ParticleFeatureRenderer.ParticleBufferCache p_430891_);

        void render(
            QuadParticleRenderState.PreparedBuffers p_425250_,
            ParticleFeatureRenderer.ParticleBufferCache p_425963_,
            RenderPass p_422972_,
            TextureManager p_423419_,
            boolean p_430242_
        );
    }
}

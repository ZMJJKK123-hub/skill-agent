package net.minecraft.client.renderer.state;

import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface ParticleGroupRenderState {
    void submit(SubmitNodeCollector p_426352_, CameraRenderState p_429869_);

    default void clear() {
    }
}

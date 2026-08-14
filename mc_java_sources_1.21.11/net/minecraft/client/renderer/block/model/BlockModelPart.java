package net.minecraft.client.renderer.block.model;

import java.util.List;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.ModelBaker;
import net.minecraft.client.resources.model.ResolvableModel;
import net.minecraft.core.Direction;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface BlockModelPart extends net.minecraftforge.client.extensions.IForgeBlockModelPart {
    List<BakedQuad> getQuads(@Nullable Direction p_395320_);

    boolean useAmbientOcclusion();

    TextureAtlasSprite particleIcon();

    @OnlyIn(Dist.CLIENT)
    public interface Unbaked extends ResolvableModel {
        BlockModelPart bake(ModelBaker p_395936_);
    }
}

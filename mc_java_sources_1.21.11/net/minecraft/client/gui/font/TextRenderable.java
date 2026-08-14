package net.minecraft.client.gui.font;

import com.mojang.blaze3d.pipeline.RenderPipeline;
import com.mojang.blaze3d.textures.GpuTextureView;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public interface TextRenderable {
    void render(Matrix4f p_428862_, VertexConsumer p_426044_, int p_427532_, boolean p_423132_);

    RenderType renderType(Font.DisplayMode p_427618_);

    GpuTextureView textureView();

    RenderPipeline guiPipeline();

    float left();

    float top();

    float right();

    float bottom();

    @OnlyIn(Dist.CLIENT)
    public interface Styled extends ActiveArea, TextRenderable {
        @Override
        default float activeLeft() {
            return this.left();
        }

        @Override
        default float activeTop() {
            return this.top();
        }

        @Override
        default float activeRight() {
            return this.right();
        }

        @Override
        default float activeBottom() {
            return this.bottom();
        }
    }
}

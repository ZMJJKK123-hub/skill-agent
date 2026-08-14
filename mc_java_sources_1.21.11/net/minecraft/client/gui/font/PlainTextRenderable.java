package net.minecraft.client.gui.font;

import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public interface PlainTextRenderable extends TextRenderable.Styled {
    float DEFAULT_WIDTH = 8.0F;
    float DEFAULT_HEIGHT = 8.0F;
    float DEFUAULT_ASCENT = 8.0F;

    @Override
    default void render(Matrix4f p_426104_, VertexConsumer p_423605_, int p_430551_, boolean p_424881_) {
        float f = 0.0F;
        if (this.shadowColor() != 0) {
            this.renderSprite(p_426104_, p_423605_, p_430551_, this.shadowOffset(), this.shadowOffset(), 0.0F, this.shadowColor());
            if (!p_424881_) {
                f += 0.03F;
            }
        }

        this.renderSprite(p_426104_, p_423605_, p_430551_, 0.0F, 0.0F, f, this.color());
    }

    void renderSprite(Matrix4f p_426271_, VertexConsumer p_428953_, int p_422827_, float p_431490_, float p_429259_, float p_426189_, int p_426135_);

    float x();

    float y();

    int color();

    int shadowColor();

    float shadowOffset();

    default float width() {
        return 8.0F;
    }

    default float height() {
        return 8.0F;
    }

    default float ascent() {
        return 8.0F;
    }

    @Override
    default float left() {
        return this.x();
    }

    @Override
    default float right() {
        return this.left() + this.width();
    }

    @Override
    default float top() {
        return this.y() + 7.0F - this.ascent();
    }

    @Override
    default float bottom() {
        return this.activeTop() + this.height();
    }
}

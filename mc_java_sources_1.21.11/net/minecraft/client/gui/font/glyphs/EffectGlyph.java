package net.minecraft.client.gui.font.glyphs;

import net.minecraft.client.gui.font.TextRenderable;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface EffectGlyph {
    TextRenderable createEffect(float p_423100_, float p_429751_, float p_427046_, float p_431540_, float p_431747_, int p_424219_, int p_429883_, float p_423514_);
}

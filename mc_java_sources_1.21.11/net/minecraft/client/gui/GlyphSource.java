package net.minecraft.client.gui;

import net.minecraft.client.gui.font.glyphs.BakedGlyph;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface GlyphSource {
    BakedGlyph getGlyph(int p_425124_);

    BakedGlyph getRandomGlyph(RandomSource p_424554_, int p_428604_);
}

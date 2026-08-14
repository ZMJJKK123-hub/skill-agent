package com.mojang.blaze3d.font;

import net.minecraft.client.gui.font.glyphs.BakedGlyph;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface UnbakedGlyph {
    GlyphInfo info();

    BakedGlyph bake(UnbakedGlyph.Stitcher p_425453_);

    @OnlyIn(Dist.CLIENT)
    public interface Stitcher {
        BakedGlyph stitch(GlyphInfo p_430620_, GlyphBitmap p_422783_);

        BakedGlyph getMissing();
    }
}

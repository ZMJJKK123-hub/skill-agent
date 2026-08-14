package com.mojang.blaze3d.opengl;

import com.mojang.blaze3d.textures.GpuTexture;
import com.mojang.blaze3d.textures.TextureFormat;
import it.unimi.dsi.fastutil.ints.Int2IntArrayMap;
import it.unimi.dsi.fastutil.ints.Int2IntMap;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public class GlTexture extends GpuTexture {
    private static final int EMPTY = -1;
    protected final int id;
    private int firstFboId = -1;
    private int firstFboDepthId = -1;
    private @Nullable Int2IntMap fboCache;
    protected boolean closed;
    private int views;

    protected GlTexture(
        @GpuTexture.Usage int p_394590_, String p_393950_, TextureFormat p_392837_, int p_391379_, int p_391947_, int p_396659_, int p_408255_, int p_408889_
    ) {
        this(p_394590_, p_393950_, p_392837_, p_391379_, p_391947_, p_396659_, p_408255_, p_408889_, false);
    }

    protected GlTexture(int p_394590_, String p_393950_, TextureFormat p_392837_, int p_391379_, int p_391947_, int p_396659_, int p_408255_, int p_408889_, boolean stencil) {
        super(p_394590_, p_393950_, p_392837_, p_391379_, p_391947_, p_396659_, p_408255_);
        this.id = p_408889_;
        this.stencilEnabled = stencil;
    }

    @Override
    public void close() {
        if (!this.closed) {
            this.closed = true;
            if (this.views == 0) {
                this.destroyImmediately();
            }
        }
    }

    private void destroyImmediately() {
        GlStateManager._deleteTexture(this.id);
        if (this.firstFboId != -1) {
            GlStateManager._glDeleteFramebuffers(this.firstFboId);
        }

        if (this.fboCache != null) {
            for (int i : this.fboCache.values()) {
                GlStateManager._glDeleteFramebuffers(i);
            }
        }
    }

    @Override
    public boolean isClosed() {
        return this.closed;
    }

    public int getFbo(DirectStateAccess p_393100_, @Nullable GpuTexture p_394451_) {
        int i = p_394451_ == null ? 0 : ((GlTexture)p_394451_).id;
        if (this.firstFboDepthId == i) {
            return this.firstFboId;
        } else if (this.firstFboId == -1) {
            this.firstFboId = this.createFbo(p_393100_, i);
            this.firstFboDepthId = i;
            return this.firstFboId;
        } else {
            if (this.fboCache == null) {
                this.fboCache = new Int2IntArrayMap();
            }

            return this.fboCache.computeIfAbsent(i, p_447708_ -> this.createFbo(p_393100_, p_447708_));
        }
    }

    private int createFbo(DirectStateAccess p_457028_, int p_457100_) {
        int i = p_457028_.createFrameBufferObject();
        p_457028_.bindFrameBufferTextures(i, this.id, p_457100_, 0, 0);
        return i;
    }

    public int glId() {
        return this.id;
    }

    public void addViews() {
        this.views++;
    }

    public void removeViews() {
        this.views--;
        if (this.closed && this.views == 0) {
            this.destroyImmediately();
        }
    }

    private final boolean stencilEnabled;

    @Override
    public boolean isStencilEnabled() {
        return this.stencilEnabled;
    }
}

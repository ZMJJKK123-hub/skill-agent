package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.DontObfuscate;
import com.mojang.blaze3d.buffers.GpuBuffer;
import com.mojang.blaze3d.buffers.GpuBufferSlice;
import com.mojang.blaze3d.buffers.GpuFence;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.textures.GpuTexture;
import com.mojang.blaze3d.textures.GpuTextureView;
import java.nio.ByteBuffer;
import java.util.OptionalDouble;
import java.util.OptionalInt;
import java.util.function.Supplier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
@DontObfuscate
public interface CommandEncoder {
    RenderPass createRenderPass(Supplier<String> p_408252_, GpuTextureView p_408607_, OptionalInt p_391786_);

    RenderPass createRenderPass(
        Supplier<String> p_406437_, GpuTextureView p_408297_, OptionalInt p_396918_, @Nullable GpuTextureView p_406509_, OptionalDouble p_393174_
    );

    void clearColorTexture(GpuTexture p_391899_, int p_397741_);

    void clearColorAndDepthTextures(GpuTexture p_395746_, int p_392725_, GpuTexture p_397792_, double p_397966_);

    void clearColorAndDepthTextures(
        GpuTexture p_407303_, int p_409423_, GpuTexture p_409838_, double p_410593_, int p_409867_, int p_406326_, int p_406188_, int p_409755_
    );

    void clearDepthTexture(GpuTexture p_391685_, double p_396385_);

    void writeToBuffer(GpuBufferSlice p_410432_, ByteBuffer p_393079_);

    GpuBuffer.MappedView mapBuffer(GpuBuffer p_408744_, boolean p_410195_, boolean p_407193_);

    GpuBuffer.MappedView mapBuffer(GpuBufferSlice p_408740_, boolean p_408864_, boolean p_406417_);

    void copyToBuffer(GpuBufferSlice p_410799_, GpuBufferSlice p_410779_);

    void writeToTexture(GpuTexture p_391309_, NativeImage p_391647_);

    void writeToTexture(
        GpuTexture p_391668_,
        NativeImage p_410403_,
        int p_394216_,
        int p_392784_,
        int p_392071_,
        int p_396859_,
        int p_395354_,
        int p_408849_,
        int p_410117_,
        int p_407888_
    );

    void writeToTexture(
        GpuTexture p_396696_,
        ByteBuffer p_426181_,
        NativeImage.Format p_408407_,
        int p_397972_,
        int p_396110_,
        int p_393128_,
        int p_395682_,
        int p_393388_,
        int p_392125_
    );

    void copyTextureToBuffer(GpuTexture p_396423_, GpuBuffer p_392049_, long p_458966_, Runnable p_397413_, int p_394917_);

    void copyTextureToBuffer(
        GpuTexture p_395042_,
        GpuBuffer p_394803_,
        long p_450414_,
        Runnable p_394723_,
        int p_396820_,
        int p_395841_,
        int p_395584_,
        int p_392863_,
        int p_391285_
    );

    void copyTextureToTexture(
        GpuTexture p_391458_, GpuTexture p_397369_, int p_397601_, int p_394677_, int p_395197_, int p_393477_, int p_392763_, int p_394739_, int p_395091_
    );

    void presentTexture(GpuTextureView p_406848_);

    GpuFence createFence();

    GpuQuery timerQueryBegin();

    void timerQueryEnd(GpuQuery p_460334_);
}

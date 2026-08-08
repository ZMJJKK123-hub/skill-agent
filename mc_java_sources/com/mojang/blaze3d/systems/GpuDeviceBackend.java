package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.GpuFormat;
import com.mojang.blaze3d.buffers.GpuBuffer;
import com.mojang.blaze3d.pipeline.CompiledRenderPipeline;
import com.mojang.blaze3d.pipeline.RenderPipeline;
import com.mojang.blaze3d.shaders.ShaderSource;
import com.mojang.blaze3d.textures.AddressMode;
import com.mojang.blaze3d.textures.FilterMode;
import com.mojang.blaze3d.textures.GpuSampler;
import com.mojang.blaze3d.textures.GpuTexture;
import com.mojang.blaze3d.textures.GpuTextureView;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.OptionalDouble;
import java.util.function.Supplier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface GpuDeviceBackend {
   GpuSurfaceBackend createSurface(long var1);

   CommandEncoderBackend createCommandEncoder();

   GpuSampler createSampler(AddressMode var1, AddressMode var2, FilterMode var3, FilterMode var4, int var5, OptionalDouble var6);

   GpuTexture createTexture(@Nullable Supplier<String> var1, @GpuTexture.Usage int var2, GpuFormat var3, int var4, int var5, int var6, int var7);

   default GpuTexture createTexture(
      @Nullable Supplier<String> label, @GpuTexture.Usage int usage, GpuFormat format, int width, int height, int depthOrLayers, int mipLevels, boolean stencil
   ) {
      return this.createTexture(label, usage, format, width, height, depthOrLayers, mipLevels);
   }

   GpuTexture createTexture(@Nullable String var1, @GpuTexture.Usage int var2, GpuFormat var3, int var4, int var5, int var6, int var7);

   default GpuTexture createTexture(
      @Nullable String label, @GpuTexture.Usage int usage, GpuFormat format, int width, int height, int depthOrLayers, int mipLevels, boolean stencil
   ) {
      return this.createTexture(label, usage, format, width, height, depthOrLayers, mipLevels);
   }

   GpuTextureView createTextureView(GpuTexture var1);

   GpuTextureView createTextureView(GpuTexture var1, int var2, int var3);

   GpuBuffer createBuffer(@Nullable Supplier<String> var1, @GpuBuffer.Usage int var2, long var3);

   GpuBuffer createBuffer(@Nullable Supplier<String> var1, @GpuBuffer.Usage int var2, ByteBuffer var3);

   List<String> getLastDebugMessages();

   boolean isDebuggingEnabled();

   CompiledRenderPipeline precompilePipeline(RenderPipeline var1, @Nullable ShaderSource var2);

   void clearPipelineCache();

   void close();

   GpuQueryPool createTimestampQueryPool(int var1);

   long getTimestampNow();

   DeviceInfo getDeviceInfo();
}

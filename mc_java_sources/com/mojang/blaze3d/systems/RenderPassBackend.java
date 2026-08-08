package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.IndexType;
import com.mojang.blaze3d.buffers.GpuBuffer;
import com.mojang.blaze3d.buffers.GpuBufferSlice;
import com.mojang.blaze3d.pipeline.RenderPipeline;
import com.mojang.blaze3d.textures.GpuSampler;
import com.mojang.blaze3d.textures.GpuTextureView;
import java.nio.IntBuffer;
import java.util.Collection;
import java.util.function.Supplier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;
import org.lwjgl.PointerBuffer;

@OnlyIn(Dist.CLIENT)
public interface RenderPassBackend {
   void pushDebugGroup(Supplier<String> var1);

   void popDebugGroup();

   void setPipeline(RenderPipeline var1);

   void bindTexture(String var1, @Nullable GpuTextureView var2, @Nullable GpuSampler var3);

   void setUniform(String var1, GpuBuffer var2);

   void setUniform(String var1, GpuBufferSlice var2);

   void enableScissor(int var1, int var2, int var3, int var4);

   void disableScissor();

   void setVertexBuffer(int var1, @Nullable GpuBufferSlice var2);

   void setIndexBuffer(GpuBuffer var1, IndexType var2);

   void drawIndexed(int var1, int var2, int var3, int var4, int var5);

   void multiDrawIndexed(IntBuffer var1, int var2, int var3, int var4);

   void multiDrawIndexed(PointerBuffer var1, IntBuffer var2, IntBuffer var3, int var4);

   void drawIndexedIndirect(GpuBufferSlice var1, int var2);

   <T> void drawMultipleIndexed(Collection<RenderPass.Draw<T>> var1, @Nullable GpuBuffer var2, @Nullable IndexType var3, Collection<String> var4, T var5);

   void draw(int var1, int var2, int var3, int var4);

   void multiDraw(IntBuffer var1, int var2, int var3, int var4);

   void multiDraw(IntBuffer var1, IntBuffer var2, int var3);

   void drawIndirect(GpuBufferSlice var1, int var2);

   void writeTimestamp(GpuQueryPool var1, int var2);
}

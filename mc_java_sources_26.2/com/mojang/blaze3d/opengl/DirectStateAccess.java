package com.mojang.blaze3d.opengl;

import com.mojang.blaze3d.buffers.GpuBuffer;
import java.nio.ByteBuffer;
import java.util.Set;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;
import org.lwjgl.opengl.ARBBufferStorage;
import org.lwjgl.opengl.ARBDirectStateAccess;
import org.lwjgl.opengl.GL33C;
import org.lwjgl.opengl.GLCapabilities;

@OnlyIn(Dist.CLIENT)
public abstract class DirectStateAccess {
   public static DirectStateAccess create(GLCapabilities capabilities, Set<String> enabledExtensions, GlHeuristics heuristics) {
      if (capabilities.GL_ARB_direct_state_access && GlDevice.USE_GL_ARB_direct_state_access && !heuristics.isGlOnDx12()) {
         enabledExtensions.add("GL_ARB_direct_state_access");
         return new DirectStateAccess.Core();
      } else {
         return new DirectStateAccess.Emulated();
      }
   }

   public abstract int createBuffer();

   public abstract void bufferData(int var1, long var2, @GpuBuffer.Usage int var4);

   public abstract void bufferData(int var1, ByteBuffer var2, @GpuBuffer.Usage int var3);

   public abstract void bufferSubData(int var1, long var2, ByteBuffer var4, @GpuBuffer.Usage int var5);

   public abstract void bufferStorage(int var1, long var2, @GpuBuffer.Usage int var4);

   public abstract void bufferStorage(int var1, ByteBuffer var2, @GpuBuffer.Usage int var3);

   public abstract @Nullable ByteBuffer mapBufferRange(int var1, long var2, long var4, int var6, @GpuBuffer.Usage int var7);

   public abstract void unmapBuffer(int var1, @GpuBuffer.Usage int var2);

   public abstract int createFrameBufferObject();

   public abstract void bindFrameBufferTextures(int var1, int[] var2, int[] var3, int var4, int var5, int var6);

   public void bindFrameBufferTextures(int fbo, int color, int depth, int mipLevel, int bindSlot) {
      this.bindFrameBufferTextures(fbo, new int[]{color}, new int[]{mipLevel}, depth, mipLevel, bindSlot);
   }

   public abstract void blitFrameBuffers(
      int var1, int var2, int var3, int var4, int var5, int var6, int var7, int var8, int var9, int var10, int var11, int var12
   );

   public abstract void flushMappedBufferRange(int var1, long var2, long var4, @GpuBuffer.Usage int var6);

   public abstract void copyBufferSubData(int var1, int var2, long var3, long var5, long var7);

   @OnlyIn(Dist.CLIENT)
   private static class Core extends DirectStateAccess {
      @Override
      public int createBuffer() {
         GlStateManager.incrementTrackedBuffers();
         return ARBDirectStateAccess.glCreateBuffers();
      }

      @Override
      public void bufferData(int buffer, long size, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glNamedBufferData(buffer, size, GlConst.bufferUsageToGlEnum(usage));
      }

      @Override
      public void bufferData(int buffer, ByteBuffer data, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glNamedBufferData(buffer, data, GlConst.bufferUsageToGlEnum(usage));
      }

      @Override
      public void bufferSubData(int buffer, long offset, ByteBuffer data, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glNamedBufferSubData(buffer, offset, data);
      }

      @Override
      public void bufferStorage(int buffer, long size, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glNamedBufferStorage(buffer, size, GlConst.bufferUsageToGlFlag(usage));
      }

      @Override
      public void bufferStorage(int buffer, ByteBuffer data, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glNamedBufferStorage(buffer, data, GlConst.bufferUsageToGlFlag(usage));
      }

      @Override
      public @Nullable ByteBuffer mapBufferRange(int buffer, long offset, long length, int flags, @GpuBuffer.Usage int usage) {
         return ARBDirectStateAccess.glMapNamedBufferRange(buffer, offset, length, flags);
      }

      @Override
      public void unmapBuffer(int buffer, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glUnmapNamedBuffer(buffer);
      }

      @Override
      public int createFrameBufferObject() {
         return ARBDirectStateAccess.glCreateFramebuffers();
      }

      @Override
      public void bindFrameBufferTextures(int fbo, int[] color, int[] colorMipLevels, int depth, int depthMipLevel, int bindSlot) {
         for (int i = 0; i < color.length; i++) {
            ARBDirectStateAccess.glNamedFramebufferTexture(fbo, 36064 + i, color[i], colorMipLevels[i]);
         }

         ARBDirectStateAccess.glNamedFramebufferTexture(fbo, 36096, depth, depthMipLevel);
         if (bindSlot != 0) {
            GlStateManager._glBindFramebuffer(bindSlot, fbo);
         }
      }

      @Override
      public void blitFrameBuffers(
         int source, int dest, int srcX0, int srcY0, int srcX1, int srcY1, int dstX0, int dstY0, int dstX1, int dstY1, int mask, int filter
      ) {
         ARBDirectStateAccess.glBlitNamedFramebuffer(source, dest, srcX0, srcY0, srcX1, srcY1, dstX0, dstY0, dstX1, dstY1, mask, filter);
      }

      @Override
      public void flushMappedBufferRange(int handle, long offset, long length, @GpuBuffer.Usage int usage) {
         ARBDirectStateAccess.glFlushMappedNamedBufferRange(handle, offset, length);
      }

      @Override
      public void copyBufferSubData(int source, int target, long sourceOffset, long targetOffset, long length) {
         ARBDirectStateAccess.glCopyNamedBufferSubData(source, target, sourceOffset, targetOffset, length);
      }
   }

   @OnlyIn(Dist.CLIENT)
   private static class Emulated extends DirectStateAccess {
      @Override
      public int createBuffer() {
         return GlStateManager._glGenBuffers();
      }

      @Override
      public void bufferData(int buffer, long size, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         GlStateManager._glBufferData(target, size, GlConst.bufferUsageToGlEnum(usage));
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void bufferData(int buffer, ByteBuffer data, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         GlStateManager._glBufferData(target, data, GlConst.bufferUsageToGlEnum(usage));
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void bufferSubData(int buffer, long offset, ByteBuffer data, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         GlStateManager._glBufferSubData(target, offset, data);
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void bufferStorage(int buffer, long size, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         ARBBufferStorage.glBufferStorage(target, size, GlConst.bufferUsageToGlFlag(usage));
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void bufferStorage(int buffer, ByteBuffer data, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         ARBBufferStorage.glBufferStorage(target, data, GlConst.bufferUsageToGlFlag(usage));
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public @Nullable ByteBuffer mapBufferRange(int buffer, long offset, long length, int access, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         ByteBuffer byteBuffer = GlStateManager._glMapBufferRange(target, offset, length, access);
         GlStateManager._glBindBuffer(target, 0);
         return byteBuffer;
      }

      @Override
      public void unmapBuffer(int buffer, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         GlStateManager._glUnmapBuffer(target);
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void flushMappedBufferRange(int buffer, long offset, long length, @GpuBuffer.Usage int usage) {
         int target = GlUtil.selectBufferBindTarget(usage);
         GlStateManager._glBindBuffer(target, buffer);
         GL33C.glFlushMappedBufferRange(target, offset, length);
         GlStateManager._glBindBuffer(target, 0);
      }

      @Override
      public void copyBufferSubData(int source, int target, long sourceOffset, long targetOffset, long length) {
         GlStateManager._glBindBuffer(36662, source);
         GlStateManager._glBindBuffer(36663, target);
         GL33C.glCopyBufferSubData(36662, 36663, sourceOffset, targetOffset, length);
         GlStateManager._glBindBuffer(36662, 0);
         GlStateManager._glBindBuffer(36663, 0);
      }

      @Override
      public int createFrameBufferObject() {
         return GlStateManager.glGenFramebuffers();
      }

      @Override
      public void bindFrameBufferTextures(int fbo, int[] color, int[] colorMipLevels, int depth, int depthMipLevel, int bindSlot) {
         int tempBindSlot = bindSlot == 0 ? 36009 : bindSlot;
         int oldFbo = GlStateManager.getFrameBuffer(tempBindSlot);
         GlStateManager._glBindFramebuffer(tempBindSlot, fbo);

         for (int i = 0; i < color.length; i++) {
            GlStateManager._glFramebufferTexture2D(tempBindSlot, 36064 + i, 3553, color[i], colorMipLevels[i]);
         }

         GlStateManager._glFramebufferTexture2D(tempBindSlot, 36096, 3553, depth, depthMipLevel);
         if (bindSlot == 0) {
            GlStateManager._glBindFramebuffer(tempBindSlot, oldFbo);
         }
      }

      @Override
      public void blitFrameBuffers(
         int source, int dest, int srcX0, int srcY0, int srcX1, int srcY1, int dstX0, int dstY0, int dstX1, int dstY1, int mask, int filter
      ) {
         int oldRead = GlStateManager.getFrameBuffer(36008);
         int oldDraw = GlStateManager.getFrameBuffer(36009);
         GlStateManager._glBindFramebuffer(36008, source);
         GlStateManager._glBindFramebuffer(36009, dest);
         GlStateManager._glBlitFrameBuffer(srcX0, srcY0, srcX1, srcY1, dstX0, dstY0, dstX1, dstY1, mask, filter);
         GlStateManager._glBindFramebuffer(36008, oldRead);
         GlStateManager._glBindFramebuffer(36009, oldDraw);
      }
   }
}

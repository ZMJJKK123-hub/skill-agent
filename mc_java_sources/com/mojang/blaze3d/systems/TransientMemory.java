package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.buffers.GpuBuffer;
import com.mojang.blaze3d.buffers.GpuBufferSlice;
import java.nio.ByteBuffer;
import java.util.List;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface TransientMemory {
   default ByteBuffer allocateCpu(long size, long alignment) {
      return this.allocateCpu(size, alignment, size, 1L);
   }

   ByteBuffer allocateCpu(long var1, long var3, long var5, long var7);

   default GpuBufferSlice.MappedView allocateStaging(long size, long alignment, @GpuBuffer.Usage int usage) {
      return this.allocateStaging(size, alignment, usage, size, 1L);
   }

   GpuBufferSlice.MappedView allocateStaging(long var1, long var3, @GpuBuffer.Usage int var5, long var6, long var8);

   default GpuBufferSlice allocateGpu(long size, long alignment, @GpuBuffer.Usage int usage) {
      return this.allocateGpu(size, alignment, usage, size, 1L);
   }

   GpuBufferSlice allocateGpu(long var1, long var3, @GpuBuffer.Usage int var5, long var6, long var8);

   default GpuBufferSlice.MappedView allocateGpuMapped(long size, long alignment, @GpuBuffer.Usage int usage) {
      return this.allocateGpuMapped(size, alignment, usage, size, 1L);
   }

   GpuBufferSlice.MappedView allocateGpuMapped(long var1, long var3, @GpuBuffer.Usage int var5, long var6, long var8);

   default GpuBufferSlice uploadStaging(ByteBuffer data, long alignment, @GpuBuffer.Usage int usage) {
      return this.uploadStaging(data, alignment, usage, data.remaining(), 1L);
   }

   default GpuBufferSlice uploadStaging(ByteBuffer data, long alignment, @GpuBuffer.Usage int usage, long minimumAllocation, long elementSize) {
      return this.uploadStaging(List.of(data), alignment, usage, minimumAllocation, elementSize);
   }

   default GpuBufferSlice uploadStaging(List<ByteBuffer> data, long alignment, @GpuBuffer.Usage int usage) {
      long totalSize = 0L;

      for (ByteBuffer buffer : data) {
         totalSize += buffer.remaining();
      }

      return this.uploadStaging(data, alignment, usage, totalSize, 1L);
   }

   GpuBufferSlice uploadStaging(List<ByteBuffer> var1, long var2, @GpuBuffer.Usage int var4, long var5, long var7);

   default GpuBufferSlice uploadGpu(ByteBuffer data, long alignment, @GpuBuffer.Usage int usage) {
      return this.uploadGpu(data, alignment, usage, data.remaining(), 1L);
   }

   default GpuBufferSlice uploadGpu(ByteBuffer data, long alignment, @GpuBuffer.Usage int usage, long minimumAllocation, long elementSize) {
      return this.uploadGpu(List.of(data), alignment, usage, minimumAllocation, elementSize);
   }

   default GpuBufferSlice uploadGpu(List<ByteBuffer> data, long alignment, @GpuBuffer.Usage int usage) {
      long totalSize = 0L;

      for (ByteBuffer buffer : data) {
         totalSize += buffer.remaining();
      }

      return this.uploadGpu(data, alignment, usage, totalSize, 1L);
   }

   GpuBufferSlice uploadGpu(List<ByteBuffer> var1, long var2, @GpuBuffer.Usage int var4, long var5, long var7);

   List<GpuBufferSlice> multiUploadStaging(List<ByteBuffer> var1, long var2, @GpuBuffer.Usage int var4);

   List<GpuBufferSlice> multiUploadGpu(List<ByteBuffer> var1, long var2, @GpuBuffer.Usage int var4);
}

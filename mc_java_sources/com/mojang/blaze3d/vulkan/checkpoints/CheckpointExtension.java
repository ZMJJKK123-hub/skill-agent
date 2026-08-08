package com.mojang.blaze3d.vulkan.checkpoints;

import com.mojang.blaze3d.vulkan.VulkanDevice;
import com.mojang.blaze3d.vulkan.VulkanQueue;
import java.util.List;
import java.util.function.Supplier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.lwjgl.vulkan.VkCommandBuffer;

@OnlyIn(Dist.CLIENT)
public interface CheckpointExtension extends AutoCloseable {
   CheckpointExtension.CheckpointStorage createStorage(VulkanDevice var1, VulkanQueue var2, int var3);

   List<CheckpointExtension.QueueCheckpoints> retrieveCheckpoints(boolean var1);

   @Override
   void close();

   @OnlyIn(Dist.CLIENT)
   interface CheckpointStorage {
      void rotate();

      void recordCheckpoint(VkCommandBuffer var1, CheckpointExtension.CheckpointType var2, Supplier<String> var3);
   }

   @OnlyIn(Dist.CLIENT)
   enum CheckpointType {
      BEGIN_RENDER_PASS,
      END_RENDER_PASS;
   }

   @OnlyIn(Dist.CLIENT)
   record QueueCheckpoints(long queue, List<CheckpointExtension.StageCheckpoint> checkpoints) {
   }

   @OnlyIn(Dist.CLIENT)
   record StageCheckpoint(long stage, CheckpointExtension.CheckpointType type, String label) {
   }
}

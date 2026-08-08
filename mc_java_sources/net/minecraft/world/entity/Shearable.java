package net.minecraft.world.entity;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;

public interface Shearable {
   void shear(ServerLevel var1, SoundSource var2, ItemStack var3);

   boolean readyForShearing();

   default List<ItemStack> shearItems(ServerLevel level, SoundSource soundSource, ItemStack tool) {
      Entity self = (Entity)this;
      ArrayList<ItemEntity> entities = new ArrayList<>();
      self.captureDrops(entities);
      this.shear(level, soundSource, tool);
      self.captureDrops(null);
      ArrayList<ItemStack> items = new ArrayList<>(entities.size());

      for (ItemEntity entity : entities) {
         items.add(entity.getItem());
      }

      return items;
   }
}

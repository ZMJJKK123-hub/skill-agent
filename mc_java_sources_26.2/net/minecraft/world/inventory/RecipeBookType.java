package net.minecraft.world.inventory;

import net.minecraft.stats.RecipeBookSettings;
import net.minecraftforge.common.IExtensibleEnum;

public enum RecipeBookType implements IExtensibleEnum {
   CRAFTING,
   FURNACE,
   BLAST_FURNACE,
   SMOKER;

   public static RecipeBookType create(String name) {
      throw new IllegalStateException("Enum not extended!");
   }

   @Override
   public void init() {
      RecipeBookSettings.register(this);
   }
}

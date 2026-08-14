package net.minecraft.world.inventory;

public enum RecipeBookType implements net.minecraftforge.common.IExtensibleEnum {
    CRAFTING,
    FURNACE,
    BLAST_FURNACE,
    SMOKER;

   public static RecipeBookType create(String name) {
      throw new IllegalStateException("Enum not extended!");
   }

   @Override
   public void init() {
       net.minecraft.stats.RecipeBookSettings.register(this);
   }
}

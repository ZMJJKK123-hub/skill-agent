package net.minecraft.world.phys.shapes;

import it.unimi.dsi.fastutil.doubles.DoubleList;

public interface IndexMerger {
   DoubleList getList();

   boolean forMergedIndexes(IndexMerger.IndexConsumer var1);

   int size();

   interface IndexConsumer {
      boolean merge(int var1, int var2, int var3);
   }
}

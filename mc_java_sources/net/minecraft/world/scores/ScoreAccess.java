package net.minecraft.world.scores;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.numbers.NumberFormat;
import org.jspecify.annotations.Nullable;

public interface ScoreAccess {
   int get();

   void set(int var1);

   default int add(int count) {
      int newValue = this.get() + count;
      this.set(newValue);
      return newValue;
   }

   default int increment() {
      return this.add(1);
   }

   default void reset() {
      this.set(0);
   }

   boolean locked();

   void unlock();

   void lock();

   @Nullable Component display();

   void display(@Nullable Component var1);

   void numberFormatOverride(@Nullable NumberFormat var1);
}

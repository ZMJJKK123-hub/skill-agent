package net.minecraft.world.level.levelgen;

import com.google.common.annotations.VisibleForTesting;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.util.RandomSource;

public interface PositionalRandomFactory {
   default RandomSource at(BlockPos pos) {
      return this.at(pos.getX(), pos.getY(), pos.getZ());
   }

   default RandomSource fromHashOf(Identifier name) {
      return this.fromHashOf(name.toString());
   }

   RandomSource fromHashOf(String var1);

   RandomSource fromSeed(long var1);

   RandomSource at(int var1, int var2, int var3);

   @VisibleForTesting
   void parityConfigString(StringBuilder var1);
}

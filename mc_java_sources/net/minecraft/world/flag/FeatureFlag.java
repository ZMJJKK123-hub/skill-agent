package net.minecraft.world.flag;

public class FeatureFlag {
   final FeatureFlagUniverse universe;
   final long mask;

   FeatureFlag(FeatureFlagUniverse universe, int bit) {
      this.universe = universe;
      this.mask = 1L << bit;
   }
}

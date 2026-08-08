package net.minecraft.world.level.levelgen;

import com.mojang.serialization.Codec;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.RegistryFileCodec;
import net.minecraft.util.KeyDispatchDataCodec;
import net.minecraft.world.level.levelgen.synth.NormalNoise;
import org.jspecify.annotations.Nullable;

public interface DensityFunction {
   Codec<DensityFunction> CODEC = RegistryFileCodec.create(Registries.DENSITY_FUNCTION, DensityFunctions.DIRECT_CODEC).xmap(holder -> {
      return switch (holder) {
         case Holder.Direct<DensityFunction> direct -> (DensityFunction)direct.value();
         case Holder.Reference<DensityFunction> reference -> new DensityFunctions.HolderHolder(reference);
         default -> throw new MatchException(null, null);
      };
   }, value -> {
      return switch (value) {
         case DensityFunctions.HolderHolder(Holder<DensityFunction> function) -> function;
         default -> Holder.direct(value);
      };
   });

   double compute(DensityFunction.FunctionContext var1);

   void fillArray(double[] var1, DensityFunction.ContextProvider var2);

   DensityFunction mapChildren(DensityFunction.Visitor var1);

   default DensityFunction mapAll(final DensityFunction.Visitor visitor) {
      class RecursiveVisitor implements DensityFunction.Visitor {
         @Override
         public DensityFunction apply(DensityFunction input) {
            return visitor.apply(input.mapChildren(this));
         }

         @Override
         public DensityFunction.NoiseHolder visitNoise(DensityFunction.NoiseHolder noise) {
            return visitor.visitNoise(noise);
         }
      }

      return new RecursiveVisitor().apply(this);
   }

   double minValue();

   double maxValue();

   KeyDispatchDataCodec<? extends DensityFunction> codec();

   default DensityFunction clamp(double min, double max) {
      return new DensityFunctions.Clamp(this, min, max);
   }

   default DensityFunction abs() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.ABS);
   }

   default DensityFunction square() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.SQUARE);
   }

   default DensityFunction cube() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.CUBE);
   }

   default DensityFunction halfNegative() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.HALF_NEGATIVE);
   }

   default DensityFunction quarterNegative() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.QUARTER_NEGATIVE);
   }

   default DensityFunction invert() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.INVERT);
   }

   default DensityFunction squeeze() {
      return DensityFunctions.map(this, DensityFunctions.Mapped.Type.SQUEEZE);
   }

   interface ContextProvider {
      DensityFunction.FunctionContext forIndex(int var1);

      void fillAllDirectly(double[] var1, DensityFunction var2);
   }

   interface FunctionContext {
      int blockX();

      int blockY();

      int blockZ();
   }

   record NoiseHolder(Holder<NormalNoise.NoiseParameters> noiseData, @Nullable NormalNoise noise) {
      public static final Codec<DensityFunction.NoiseHolder> CODEC = NormalNoise.NoiseParameters.CODEC
         .xmap(data -> new DensityFunction.NoiseHolder(data, null), DensityFunction.NoiseHolder::noiseData);

      public NoiseHolder(Holder<NormalNoise.NoiseParameters> noiseData) {
         this(noiseData, null);
      }

      public double getValue(double x, double y, double z) {
         return this.noise == null ? 0.0 : this.noise.getValue(x, y, z);
      }

      public double maxValue() {
         return this.noise == null ? 2.0 : this.noise.maxValue();
      }
   }

   interface SimpleFunction extends DensityFunction {
      @Override
      default void fillArray(double[] output, DensityFunction.ContextProvider contextProvider) {
         contextProvider.fillAllDirectly(output, this);
      }

      @Override
      default DensityFunction mapChildren(DensityFunction.Visitor visitor) {
         return this;
      }
   }

   record SinglePointContext(int blockX, int blockY, int blockZ) implements DensityFunction.FunctionContext {
   }

   interface Visitor {
      DensityFunction apply(DensityFunction var1);

      default DensityFunction.NoiseHolder visitNoise(DensityFunction.NoiseHolder noise) {
         return noise;
      }
   }
}

package net.minecraft.world.level.saveddata;

import com.mojang.serialization.Codec;
import java.util.function.Supplier;
import net.minecraft.resources.Identifier;
import net.minecraft.util.datafix.DataFixTypes;

public record SavedDataType<T extends SavedData>(Identifier id, Supplier<T> constructor, Codec<T> codec, DataFixTypes dataFixType) {
   @Override
   public boolean equals(Object obj) {
      return obj instanceof SavedDataType<?> type && this.id.equals(type.id);
   }

   @Override
   public int hashCode() {
      return this.id.hashCode();
   }

   @Override
   public String toString() {
      return "SavedDataType[" + this.id + "]";
   }
}

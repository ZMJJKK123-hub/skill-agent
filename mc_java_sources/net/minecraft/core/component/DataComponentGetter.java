package net.minecraft.core.component;

import org.jspecify.annotations.Nullable;

public interface DataComponentGetter {
   <T> @Nullable T get(DataComponentType<? extends T> var1);

   default <T> T getOrDefault(DataComponentType<? extends T> type, T defaultValue) {
      T value = this.get(type);
      return value != null ? value : defaultValue;
   }

   default <T> @Nullable TypedDataComponent<T> getTyped(DataComponentType<T> type) {
      T value = this.get(type);
      return value != null ? new TypedDataComponent<>(type, value) : null;
   }
}

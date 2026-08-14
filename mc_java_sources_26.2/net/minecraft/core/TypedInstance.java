package net.minecraft.core;

import java.util.stream.Stream;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;

public interface TypedInstance<T> {
   Holder<T> typeHolder();

   default Stream<TagKey<T>> tags() {
      return this.typeHolder().tags();
   }

   default boolean is(TagKey<T> tag) {
      return this.typeHolder().is(tag);
   }

   default boolean is(HolderSet<T> set) {
      return set.contains(this.typeHolder());
   }

   default boolean is(T rawType) {
      return this.typeHolder().value() == rawType;
   }

   default boolean is(Holder<T> type) {
      return this.typeHolder() == type;
   }

   default boolean is(ResourceKey<T> type) {
      return this.typeHolder().is(type);
   }
}

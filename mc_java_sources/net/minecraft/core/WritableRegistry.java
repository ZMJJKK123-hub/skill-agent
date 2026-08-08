package net.minecraft.core;

import java.util.List;
import java.util.Map;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;

public interface WritableRegistry<T> extends Registry<T> {
   Holder.Reference<T> register(ResourceKey<T> var1, T var2, RegistrationInfo var3);

   void bindTags(Map<TagKey<T>, List<Holder<T>>> var1);

   boolean isEmpty();

   HolderGetter<T> createRegistrationLookup();
}

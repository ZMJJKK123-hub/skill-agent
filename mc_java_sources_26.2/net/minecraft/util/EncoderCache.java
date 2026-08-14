package net.minecraft.util;

import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import net.minecraft.nbt.Tag;

public class EncoderCache {
   private final LoadingCache<EncoderCache.Key<?, ?>, DataResult<?>> cache;

   public EncoderCache(int maximumSize) {
      this.cache = CacheBuilder.newBuilder()
         .maximumSize(maximumSize)
         .concurrencyLevel(1)
         .softValues()
         .build(new CacheLoader<EncoderCache.Key<?, ?>, DataResult<?>>() {
            public DataResult<?> load(EncoderCache.Key<?, ?> key) {
               return key.resolve();
            }
         });
   }

   public <A> Codec<A> wrap(final Codec<A> codec) {
      return new Codec<A>() {
         public <T> DataResult<Pair<A, T>> decode(DynamicOps<T> ops, T input) {
            return codec.decode(ops, input);
         }

         public <T> DataResult<T> encode(A input, DynamicOps<T> ops, T prefix) {
            return ((DataResult)EncoderCache.this.cache.getUnchecked(new EncoderCache.Key(codec, input, ops)))
               .map(value -> value instanceof Tag tag ? tag.copy() : value);
         }
      };
   }

   private record Key<A, T>(Codec<A> codec, A value, DynamicOps<T> ops) {
      public DataResult<T> resolve() {
         return this.codec.encodeStart(this.ops, this.value);
      }

      @Override
      public boolean equals(Object obj) {
         if (this == obj) {
            return true;
         } else {
            return obj instanceof EncoderCache.Key<?, ?> key ? this.codec == key.codec && this.value.equals(key.value) && this.ops.equals(key.ops) : false;
         }
      }

      @Override
      public int hashCode() {
         int result = System.identityHashCode(this.codec);
         result = 31 * result + this.value.hashCode();
         return 31 * result + this.ops.hashCode();
      }
   }
}

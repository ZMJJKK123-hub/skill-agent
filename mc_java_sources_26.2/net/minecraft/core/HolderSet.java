package net.minecraft.core;

import com.google.common.annotations.VisibleForTesting;
import com.mojang.datafixers.util.Either;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.Spliterator;
import java.util.function.Function;
import java.util.stream.Stream;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.util.Util;
import net.minecraftforge.common.extensions.IForgeHolderSet;
import org.jspecify.annotations.Nullable;

public interface HolderSet<T> extends Iterable<Holder<T>>, IForgeHolderSet<T> {
   Stream<Holder<T>> stream();

   int size();

   boolean isBound();

   Either<TagKey<T>, List<Holder<T>>> unwrap();

   Optional<Holder<T>> getRandomElement(RandomSource var1);

   Holder<T> get(int var1);

   boolean contains(Holder<T> var1);

   boolean canSerializeIn(HolderOwner<T> var1);

   Optional<TagKey<T>> unwrapKey();

   @Deprecated
   @VisibleForTesting
   static <T> HolderSet.Named<T> emptyNamed(HolderOwner<T> owner, TagKey<T> key) {
      return new HolderSet.Named<T>(owner, key) {
         @Override
         protected List<Holder<T>> contents() {
            throw new UnsupportedOperationException("Tag " + this.key() + " can't be dereferenced during construction");
         }
      };
   }

   static <T> HolderSet<T> empty() {
      return (HolderSet<T>)HolderSet.Direct.EMPTY;
   }

   @SafeVarargs
   static <T> HolderSet.Direct<T> direct(Holder<T>... values) {
      return new HolderSet.Direct<>(List.of(values));
   }

   static <T> HolderSet.Direct<T> direct(List<? extends Holder<T>> values) {
      return new HolderSet.Direct<>(List.copyOf(values));
   }

   @SafeVarargs
   static <E, T> HolderSet.Direct<T> direct(Function<E, Holder<T>> holderGetter, E... elements) {
      return direct(Stream.of(elements).map(holderGetter).toList());
   }

   static <E, T> HolderSet.Direct<T> direct(Function<E, Holder<T>> holderGetter, Collection<E> elements) {
      return direct(elements.stream().map(holderGetter).toList());
   }

   final class Direct<T> extends HolderSet.ListBacked<T> {
      private static final HolderSet.Direct<?> EMPTY = new HolderSet.Direct(List.of());
      private final List<Holder<T>> contents;
      private @Nullable Set<Holder<T>> contentsSet;

      private Direct(List<Holder<T>> contents) {
         this.contents = contents;
      }

      @Override
      protected List<Holder<T>> contents() {
         return this.contents;
      }

      @Override
      public boolean isBound() {
         return true;
      }

      @Override
      public Either<TagKey<T>, List<Holder<T>>> unwrap() {
         return Either.right(this.contents);
      }

      @Override
      public Optional<TagKey<T>> unwrapKey() {
         return Optional.empty();
      }

      @Override
      public boolean contains(Holder<T> value) {
         if (this.contentsSet == null) {
            this.contentsSet = Set.copyOf(this.contents);
         }

         return this.contentsSet.contains(value);
      }

      @Override
      public String toString() {
         return "DirectSet[" + this.contents + "]";
      }

      @Override
      public boolean equals(Object obj) {
         return this == obj ? true : obj instanceof HolderSet.Direct<?> direct && this.contents.equals(direct.contents);
      }

      @Override
      public int hashCode() {
         return this.contents.hashCode();
      }
   }

   abstract class ListBacked<T> implements HolderSet<T> {
      protected abstract List<Holder<T>> contents();

      @Override
      public int size() {
         return this.contents().size();
      }

      @Override
      public Spliterator<Holder<T>> spliterator() {
         return this.contents().spliterator();
      }

      @Override
      public Iterator<Holder<T>> iterator() {
         return this.contents().iterator();
      }

      @Override
      public Stream<Holder<T>> stream() {
         return this.contents().stream();
      }

      @Override
      public Optional<Holder<T>> getRandomElement(RandomSource random) {
         return Util.getRandomSafe(this.contents(), random);
      }

      @Override
      public Holder<T> get(int index) {
         return this.contents().get(index);
      }

      @Override
      public boolean canSerializeIn(HolderOwner<T> owner) {
         return true;
      }
   }

   class Named<T> extends HolderSet.ListBacked<T> {
      private final HolderOwner<T> owner;
      private final TagKey<T> key;
      private @Nullable List<Holder<T>> contents;
      private List<Runnable> invalidationCallbacks = new ArrayList<>();

      public Named(HolderOwner<T> owner, TagKey<T> key) {
         this.owner = owner;
         this.key = key;
      }

      public void bind(List<Holder<T>> contents) {
         this.contents = List.copyOf(contents);
         this.invalidationCallbacks.forEach(Runnable::run);
      }

      public TagKey<T> key() {
         return this.key;
      }

      @Override
      protected List<Holder<T>> contents() {
         if (this.contents == null) {
            throw new IllegalStateException("Trying to access unbound tag '" + this.key + "' from registry " + this.owner);
         } else {
            return this.contents;
         }
      }

      @Override
      public boolean isBound() {
         return this.contents != null;
      }

      @Override
      public Either<TagKey<T>, List<Holder<T>>> unwrap() {
         return Either.left(this.key);
      }

      @Override
      public Optional<TagKey<T>> unwrapKey() {
         return Optional.of(this.key);
      }

      @Override
      public boolean contains(Holder<T> value) {
         return value.is(this.key);
      }

      @Override
      public String toString() {
         return "NamedSet(" + this.key + ")[" + this.contents + "]";
      }

      @Override
      public boolean canSerializeIn(HolderOwner<T> context) {
         return this.owner.canSerializeIn(context);
      }

      @Override
      public void addInvalidationListener(Runnable runnable) {
         this.invalidationCallbacks.add(runnable);
      }
   }
}

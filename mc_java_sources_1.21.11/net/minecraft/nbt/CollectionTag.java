package net.minecraft.nbt;

import java.util.Iterator;
import java.util.NoSuchElementException;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public sealed interface CollectionTag extends Iterable<Tag>, Tag permits ListTag, ByteArrayTag, IntArrayTag, LongArrayTag {
    void clear();

    boolean setTag(int p_128305_, Tag p_128306_);

    boolean addTag(int p_128310_, Tag p_128311_);

    Tag remove(int p_128313_);

    Tag get(int p_392245_);

    int size();

    default boolean isEmpty() {
        return this.size() == 0;
    }

    @Override
    default Iterator<Tag> iterator() {
        return new Iterator<Tag>() {
            private int index;

            @Override
            public boolean hasNext() {
                return this.index < CollectionTag.this.size();
            }

            public Tag next() {
                if (!this.hasNext()) {
                    throw new NoSuchElementException();
                } else {
                    return CollectionTag.this.get(this.index++);
                }
            }
        };
    }

    default Stream<Tag> stream() {
        return StreamSupport.stream(this.spliterator(), false);
    }
}

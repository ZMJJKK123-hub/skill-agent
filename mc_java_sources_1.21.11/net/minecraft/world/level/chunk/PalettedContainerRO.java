package net.minecraft.world.level.chunk;

import com.google.common.annotations.VisibleForTesting;
import com.mojang.serialization.DataResult;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Predicate;
import java.util.stream.LongStream;
import net.minecraft.network.FriendlyByteBuf;

public interface PalettedContainerRO<T> {
    T get(int p_238291_, int p_238292_, int p_238293_);

    void getAll(Consumer<T> p_238353_);

    void write(FriendlyByteBuf p_238417_);

    int getSerializedSize();

    @VisibleForTesting
    int bitsPerEntry();

    boolean maybeHas(Predicate<T> p_238437_);

    void count(PalettedContainer.CountConsumer<T> p_238355_);

    PalettedContainer<T> copy();

    PalettedContainer<T> recreate();

    PalettedContainerRO.PackedData<T> pack(Strategy<T> p_428427_);

    public record PackedData<T>(List<T> paletteEntries, Optional<LongStream> storage, int bitsPerEntry) {
        public static final int UNKNOWN_BITS_PER_ENTRY = -1;

        public PackedData(List<T> p_238381_, Optional<LongStream> p_238382_) {
            this(p_238381_, p_238382_, -1);
        }
    }

    public interface Unpacker<T, C extends PalettedContainerRO<T>> {
        DataResult<C> read(Strategy<T> p_430654_, PalettedContainerRO.PackedData<T> p_238366_);
    }
}

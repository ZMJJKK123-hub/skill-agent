package net.minecraft.world.level.storage;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import java.util.Optional;
import java.util.stream.Stream;
import net.minecraft.core.HolderLookup;

public interface ValueInput {
    <T> Optional<T> read(String p_409470_, Codec<T> p_406709_);

    @Deprecated
    <T> Optional<T> read(MapCodec<T> p_408358_);

    Optional<ValueInput> child(String p_408431_);

    ValueInput childOrEmpty(String p_408553_);

    Optional<ValueInput.ValueInputList> childrenList(String p_408321_);

    ValueInput.ValueInputList childrenListOrEmpty(String p_406881_);

    <T> Optional<ValueInput.TypedInputList<T>> list(String p_406297_, Codec<T> p_406564_);

    <T> ValueInput.TypedInputList<T> listOrEmpty(String p_407257_, Codec<T> p_408194_);

    boolean getBooleanOr(String p_409092_, boolean p_407041_);

    byte getByteOr(String p_408791_, byte p_406064_);

    int getShortOr(String p_409869_, short p_410430_);

    Optional<Integer> getInt(String p_407742_);

    int getIntOr(String p_406082_, int p_407517_);

    long getLongOr(String p_408395_, long p_408466_);

    Optional<Long> getLong(String p_409338_);

    float getFloatOr(String p_410467_, float p_408769_);

    double getDoubleOr(String p_409117_, double p_406402_);

    Optional<String> getString(String p_409768_);

    String getStringOr(String p_406799_, String p_409397_);

    Optional<int[]> getIntArray(String p_408524_);

    @Deprecated
    HolderLookup.Provider lookup();

    public interface TypedInputList<T> extends Iterable<T> {
        boolean isEmpty();

        Stream<T> stream();
    }

    public interface ValueInputList extends Iterable<ValueInput> {
        boolean isEmpty();

        Stream<ValueInput> stream();
    }
}

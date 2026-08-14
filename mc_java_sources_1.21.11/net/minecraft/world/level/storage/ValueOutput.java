package net.minecraft.world.level.storage;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import org.jspecify.annotations.Nullable;

public interface ValueOutput {
    <T> void store(String p_406559_, Codec<T> p_410310_, T p_409569_);

    <T> void storeNullable(String p_406385_, Codec<T> p_408165_, @Nullable T p_407725_);

    @Deprecated
    <T> void store(MapCodec<T> p_410307_, T p_410068_);

    void putBoolean(String p_409636_, boolean p_406905_);

    void putByte(String p_407145_, byte p_406118_);

    void putShort(String p_409710_, short p_407656_);

    void putInt(String p_408708_, int p_406617_);

    void putLong(String p_407557_, long p_408874_);

    void putFloat(String p_410219_, float p_408821_);

    void putDouble(String p_408742_, double p_410497_);

    void putString(String p_407659_, String p_407753_);

    void putIntArray(String p_407318_, int[] p_410462_);

    ValueOutput child(String p_407220_);

    ValueOutput.ValueOutputList childrenList(String p_409163_);

    <T> ValueOutput.TypedOutputList<T> list(String p_410506_, Codec<T> p_407980_);

    void discard(String p_408615_);

    boolean isEmpty();

    public interface TypedOutputList<T> {
        void add(T p_408164_);

        boolean isEmpty();
    }

    public interface ValueOutputList {
        ValueOutput addChild();

        void discardLast();

        boolean isEmpty();
    }
}

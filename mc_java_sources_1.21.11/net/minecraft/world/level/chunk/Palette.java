package net.minecraft.world.level.chunk;

import java.util.List;
import java.util.function.Predicate;
import net.minecraft.core.IdMap;
import net.minecraft.network.FriendlyByteBuf;

public interface Palette<T> {
    int idFor(T p_63061_, PaletteResize<T> p_423264_);

    boolean maybeHas(Predicate<T> p_63062_);

    T valueFor(int p_63060_);

    void read(FriendlyByteBuf p_63064_, IdMap<T> p_425249_);

    void write(FriendlyByteBuf p_63065_, IdMap<T> p_424375_);

    int getSerializedSize(IdMap<T> p_428842_);

    int getSize();

    Palette<T> copy();

    public interface Factory {
        <A> Palette<A> create(int p_188027_, List<A> p_188030_);
    }
}

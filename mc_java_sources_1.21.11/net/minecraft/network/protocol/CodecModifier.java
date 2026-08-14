package net.minecraft.network.protocol;

import net.minecraft.network.codec.StreamCodec;

@FunctionalInterface
public interface CodecModifier<B, V, C> {
    StreamCodec<? super B, V> apply(StreamCodec<? super B, V> p_396150_, C p_394792_);
}

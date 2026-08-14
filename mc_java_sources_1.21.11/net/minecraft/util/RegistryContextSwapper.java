package net.minecraft.util;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import net.minecraft.core.HolderLookup;

public interface RegistryContextSwapper {
    <T> DataResult<T> swapTo(Codec<T> p_395617_, T p_391965_, HolderLookup.Provider p_392950_);
}

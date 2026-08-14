package net.minecraft.core;

import net.minecraft.resources.Identifier;
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;

public interface DefaultedRegistry<T> extends Registry<T> {
    @Override
    @NonNull Identifier getKey(T p_122330_);

    @Override
    @NonNull T getValue(@Nullable Identifier p_453863_);

    @Override
    @NonNull T byId(int p_122317_);

    Identifier getDefaultKey();
}

package net.minecraft.util.debug;

import net.minecraft.server.level.ServerLevel;
import org.jspecify.annotations.Nullable;

public interface DebugValueSource {
    void registerDebugValues(ServerLevel p_425337_, DebugValueSource.Registration p_424865_);

    public interface Registration {
        <T> void register(DebugSubscription<T> p_424310_, DebugValueSource.ValueGetter<T> p_427087_);
    }

    public interface ValueGetter<T> {
        @Nullable T get();
    }
}

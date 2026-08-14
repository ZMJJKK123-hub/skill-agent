package net.minecraft.world.level.timers;

import com.mojang.serialization.MapCodec;

public interface TimerCallback<T> {
    void handle(T p_82213_, TimerQueue<T> p_82214_, long p_82215_);

    MapCodec<? extends TimerCallback<T>> codec();
}

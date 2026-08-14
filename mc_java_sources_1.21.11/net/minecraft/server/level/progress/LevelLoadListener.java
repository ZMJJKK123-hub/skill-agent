package net.minecraft.server.level.progress;

import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;

public interface LevelLoadListener {
    static LevelLoadListener compose(final LevelLoadListener p_429594_, final LevelLoadListener p_431373_) {
        return new LevelLoadListener() {
            @Override
            public void start(LevelLoadListener.Stage p_426534_, int p_425447_) {
                p_429594_.start(p_426534_, p_425447_);
                p_431373_.start(p_426534_, p_425447_);
            }

            @Override
            public void update(LevelLoadListener.Stage p_430353_, int p_430736_, int p_423071_) {
                p_429594_.update(p_430353_, p_430736_, p_423071_);
                p_431373_.update(p_430353_, p_430736_, p_423071_);
            }

            @Override
            public void finish(LevelLoadListener.Stage p_425779_) {
                p_429594_.finish(p_425779_);
                p_431373_.finish(p_425779_);
            }

            @Override
            public void updateFocus(ResourceKey<Level> p_431068_, ChunkPos p_430648_) {
                p_429594_.updateFocus(p_431068_, p_430648_);
                p_431373_.updateFocus(p_431068_, p_430648_);
            }
        };
    }

    void start(LevelLoadListener.Stage p_426163_, int p_429286_);

    void update(LevelLoadListener.Stage p_429099_, int p_428116_, int p_424708_);

    void finish(LevelLoadListener.Stage p_423578_);

    void updateFocus(ResourceKey<Level> p_425177_, ChunkPos p_427331_);

    public static enum Stage {
        START_SERVER,
        PREPARE_GLOBAL_SPAWN,
        LOAD_INITIAL_CHUNKS,
        LOAD_PLAYER_CHUNKS;
    }
}

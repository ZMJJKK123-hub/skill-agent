package net.minecraft.world.level.border;

public interface BorderChangeListener {
    void onSetSize(WorldBorder p_427796_, double p_430257_);

    void onLerpSize(WorldBorder p_427113_, double p_427031_, double p_431742_, long p_424057_, long p_460376_);

    void onSetCenter(WorldBorder p_423195_, double p_427988_, double p_427130_);

    void onSetWarningTime(WorldBorder p_426976_, int p_430636_);

    void onSetWarningBlocks(WorldBorder p_422341_, int p_429953_);

    void onSetDamagePerBlock(WorldBorder p_423255_, double p_424357_);

    void onSetSafeZone(WorldBorder p_422460_, double p_427259_);
}

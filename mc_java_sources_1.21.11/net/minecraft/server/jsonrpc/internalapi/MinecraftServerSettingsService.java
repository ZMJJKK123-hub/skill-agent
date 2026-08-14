package net.minecraft.server.jsonrpc.internalapi;

import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.permissions.LevelBasedPermissionSet;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.GameType;

public interface MinecraftServerSettingsService {
    boolean isAutoSave();

    boolean setAutoSave(boolean p_426283_, ClientInfo p_429580_);

    Difficulty getDifficulty();

    Difficulty setDifficulty(Difficulty p_428640_, ClientInfo p_425521_);

    boolean isEnforceWhitelist();

    boolean setEnforceWhitelist(boolean p_431569_, ClientInfo p_423099_);

    boolean isUsingWhitelist();

    boolean setUsingWhitelist(boolean p_429455_, ClientInfo p_430513_);

    int getMaxPlayers();

    int setMaxPlayers(int p_425772_, ClientInfo p_423069_);

    int getPauseWhenEmptySeconds();

    int setPauseWhenEmptySeconds(int p_431138_, ClientInfo p_426340_);

    int getPlayerIdleTimeout();

    int setPlayerIdleTimeout(int p_425105_, ClientInfo p_429993_);

    boolean allowFlight();

    boolean setAllowFlight(boolean p_431088_, ClientInfo p_426536_);

    int getSpawnProtectionRadius();

    int setSpawnProtectionRadius(int p_423180_, ClientInfo p_431652_);

    String getMotd();

    String setMotd(String p_426488_, ClientInfo p_428645_);

    boolean forceGameMode();

    boolean setForceGameMode(boolean p_431346_, ClientInfo p_431394_);

    GameType getGameMode();

    GameType setGameMode(GameType p_429803_, ClientInfo p_424644_);

    int getViewDistance();

    int setViewDistance(int p_428779_, ClientInfo p_430831_);

    int getSimulationDistance();

    int setSimulationDistance(int p_422820_, ClientInfo p_423690_);

    boolean acceptsTransfers();

    boolean setAcceptsTransfers(boolean p_426746_, ClientInfo p_428416_);

    int getStatusHeartbeatInterval();

    int setStatusHeartbeatInterval(int p_422980_, ClientInfo p_427171_);

    LevelBasedPermissionSet getOperatorUserPermissions();

    LevelBasedPermissionSet setOperatorUserPermissions(LevelBasedPermissionSet p_459214_, ClientInfo p_457989_);

    boolean hidesOnlinePlayers();

    boolean setHidesOnlinePlayers(boolean p_426787_, ClientInfo p_430469_);

    boolean repliesToStatus();

    boolean setRepliesToStatus(boolean p_424117_, ClientInfo p_429901_);

    int getEntityBroadcastRangePercentage();

    int setEntityBroadcastRangePercentage(int p_427504_, ClientInfo p_429330_);
}

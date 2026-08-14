package net.minecraft.server.notifications;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.players.IpBanListEntry;
import net.minecraft.server.players.NameAndId;
import net.minecraft.server.players.ServerOpListEntry;
import net.minecraft.server.players.UserBanListEntry;
import net.minecraft.world.level.gamerules.GameRule;

public interface NotificationService {
    void playerJoined(ServerPlayer p_422652_);

    void playerLeft(ServerPlayer p_426985_);

    void serverStarted();

    void serverShuttingDown();

    void serverSaveStarted();

    void serverSaveCompleted();

    void serverActivityOccured();

    void playerOped(ServerOpListEntry p_427779_);

    void playerDeoped(ServerOpListEntry p_429304_);

    void playerAddedToAllowlist(NameAndId p_422656_);

    void playerRemovedFromAllowlist(NameAndId p_427732_);

    void ipBanned(IpBanListEntry p_422858_);

    void ipUnbanned(String p_431508_);

    void playerBanned(UserBanListEntry p_431753_);

    void playerUnbanned(NameAndId p_425110_);

    <T> void onGameRuleChanged(GameRule<T> p_455748_, T p_461030_);

    void statusHeartbeat();
}

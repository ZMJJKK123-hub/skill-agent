package net.minecraft.server.jsonrpc.internalapi;

import java.util.Collection;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.players.IpBanListEntry;
import net.minecraft.server.players.NameAndId;
import net.minecraft.server.players.UserBanListEntry;

public interface MinecraftBanListService {
    void addUserBan(UserBanListEntry p_426775_, ClientInfo p_425866_);

    void removeUserBan(NameAndId p_424707_, ClientInfo p_424743_);

    Collection<UserBanListEntry> getUserBanEntries();

    Collection<IpBanListEntry> getIpBanEntries();

    void addIpBan(IpBanListEntry p_431257_, ClientInfo p_422885_);

    void clearIpBans(ClientInfo p_427101_);

    void removeIpBan(String p_422733_, ClientInfo p_424771_);

    void clearUserBans(ClientInfo p_425588_);
}

package net.minecraft.server.jsonrpc.internalapi;

import java.util.Collection;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.players.NameAndId;
import net.minecraft.server.players.UserWhiteListEntry;

public interface MinecraftAllowListService {
    Collection<UserWhiteListEntry> getEntries();

    boolean add(UserWhiteListEntry p_426274_, ClientInfo p_429915_);

    void clear(ClientInfo p_430854_);

    void remove(NameAndId p_426177_, ClientInfo p_428967_);

    void kickUnlistedPlayers(ClientInfo p_423213_);
}

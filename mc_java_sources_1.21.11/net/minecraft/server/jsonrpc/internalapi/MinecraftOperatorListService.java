package net.minecraft.server.jsonrpc.internalapi;

import java.util.Collection;
import java.util.Optional;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.permissions.PermissionLevel;
import net.minecraft.server.players.NameAndId;
import net.minecraft.server.players.ServerOpListEntry;

public interface MinecraftOperatorListService {
    Collection<ServerOpListEntry> getEntries();

    void op(NameAndId p_424317_, Optional<PermissionLevel> p_428225_, Optional<Boolean> p_428440_, ClientInfo p_428353_);

    void op(NameAndId p_424987_, ClientInfo p_427350_);

    void deop(NameAndId p_431385_, ClientInfo p_429454_);

    void clear(ClientInfo p_425545_);
}

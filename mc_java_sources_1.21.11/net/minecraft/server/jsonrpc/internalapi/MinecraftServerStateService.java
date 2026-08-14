package net.minecraft.server.jsonrpc.internalapi;

import java.util.Collection;
import net.minecraft.network.chat.Component;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.level.ServerPlayer;

public interface MinecraftServerStateService {
    boolean isReady();

    boolean saveEverything(boolean p_426842_, boolean p_428239_, boolean p_430536_, ClientInfo p_429738_);

    void halt(boolean p_423775_, ClientInfo p_426874_);

    void sendSystemMessage(Component p_427537_, ClientInfo p_429301_);

    void sendSystemMessage(Component p_423422_, boolean p_423639_, Collection<ServerPlayer> p_429466_, ClientInfo p_426003_);

    void broadcastSystemMessage(Component p_422757_, boolean p_428858_, ClientInfo p_423624_);
}

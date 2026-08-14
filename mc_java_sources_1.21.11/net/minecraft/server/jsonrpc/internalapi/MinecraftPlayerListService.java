package net.minecraft.server.jsonrpc.internalapi;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.players.NameAndId;
import net.minecraft.util.Util;
import org.jspecify.annotations.Nullable;

public interface MinecraftPlayerListService {
    List<ServerPlayer> getPlayers();

    @Nullable ServerPlayer getPlayer(UUID p_425386_);

    default CompletableFuture<Optional<NameAndId>> getUser(Optional<UUID> p_423451_, Optional<String> p_426430_) {
        if (p_423451_.isPresent()) {
            Optional<NameAndId> optional = this.getCachedUserById(p_423451_.get());
            return optional.isPresent()
                ? CompletableFuture.completedFuture(optional)
                : CompletableFuture.supplyAsync(() -> this.fetchUserById(p_423451_.get()), Util.nonCriticalIoPool());
        } else {
            return p_426430_.isPresent()
                ? CompletableFuture.supplyAsync(() -> this.fetchUserByName(p_426430_.get()), Util.nonCriticalIoPool())
                : CompletableFuture.completedFuture(Optional.empty());
        }
    }

    Optional<NameAndId> fetchUserByName(String p_427056_);

    Optional<NameAndId> fetchUserById(UUID p_430045_);

    Optional<NameAndId> getCachedUserById(UUID p_430785_);

    Optional<ServerPlayer> getPlayer(Optional<UUID> p_428200_, Optional<String> p_428758_);

    List<ServerPlayer> getPlayersWithAddress(String p_430471_);

    @Nullable ServerPlayer getPlayerByName(String p_422387_);

    void remove(ServerPlayer p_428232_, ClientInfo p_429514_);
}

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

   @Nullable ServerPlayer getPlayer(UUID var1);

   default CompletableFuture<Optional<NameAndId>> getUser(Optional<UUID> id, Optional<String> name) {
      if (id.isPresent()) {
         Optional<NameAndId> nameAndId = this.getCachedUserById(id.get());
         return nameAndId.isPresent()
            ? CompletableFuture.completedFuture(nameAndId)
            : CompletableFuture.supplyAsync(() -> this.fetchUserById(id.get()), Util.nonCriticalIoPool());
      } else {
         return name.isPresent()
            ? CompletableFuture.supplyAsync(() -> this.fetchUserByName(name.get()), Util.nonCriticalIoPool())
            : CompletableFuture.completedFuture(Optional.empty());
      }
   }

   Optional<NameAndId> fetchUserByName(String var1);

   Optional<NameAndId> fetchUserById(UUID var1);

   Optional<NameAndId> getCachedUserById(UUID var1);

   Optional<ServerPlayer> getPlayer(Optional<UUID> var1, Optional<String> var2);

   List<ServerPlayer> getPlayersWithAddress(String var1);

   @Nullable ServerPlayer getPlayerByName(String var1);

   void remove(ServerPlayer var1, ClientInfo var2);
}

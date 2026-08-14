package net.minecraft.server.players;

import java.util.Optional;
import java.util.UUID;

public interface UserNameToIdResolver {
    void add(NameAndId p_430113_);

    Optional<NameAndId> get(String p_430708_);

    Optional<NameAndId> get(UUID p_431458_);

    void resolveOfflineUsers(boolean p_426674_);

    void save();
}

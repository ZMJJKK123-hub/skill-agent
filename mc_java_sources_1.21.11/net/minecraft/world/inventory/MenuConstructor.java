package net.minecraft.world.inventory;

import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import org.jspecify.annotations.Nullable;

@FunctionalInterface
public interface MenuConstructor {
    @Nullable AbstractContainerMenu createMenu(int p_39954_, Inventory p_39955_, Player p_39956_);
}

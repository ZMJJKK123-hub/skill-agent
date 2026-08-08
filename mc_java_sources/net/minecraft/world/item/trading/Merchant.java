package net.minecraft.world.item.trading;

import java.util.OptionalInt;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

public interface Merchant {
   void setTradingPlayer(@Nullable Player var1);

   @Nullable Player getTradingPlayer();

   MerchantOffers getOffers();

   void overrideOffers(MerchantOffers var1);

   void notifyTrade(MerchantOffer var1);

   void notifyTradeUpdated(ItemStack var1);

   int getVillagerXp();

   void overrideXp(int var1);

   boolean showProgressBar();

   SoundEvent getNotifyTradeSound();

   default boolean canRestock() {
      return false;
   }

   default void openTradingScreen(Player player, Component title, int level) {
      OptionalInt containerId = player.openMenu(new SimpleMenuProvider((id, inventory, p) -> new MerchantMenu(id, inventory, this), title));
      if (containerId.isPresent()) {
         MerchantOffers offers = this.getOffers();
         if (!offers.isEmpty()) {
            player.sendMerchantOffers(containerId.getAsInt(), offers, level, this.getVillagerXp(), this.showProgressBar(), this.canRestock());
         }
      }
   }

   boolean isClientSide();

   boolean stillValid(Player var1);
}

package net.minecraft.world.entity.monster;

import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

public interface CrossbowAttackMob extends RangedAttackMob {
   void setChargingCrossbow(boolean var1);

   @Nullable LivingEntity getTarget();

   void onCrossbowAttackPerformed();

   default void performCrossbowAttack(LivingEntity body, float crossbowPower) {
      InteractionHand hand = ProjectileUtil.getWeaponHoldingHand(body, item -> item instanceof CrossbowItem);
      ItemStack usedItem = body.getItemInHand(hand);
      if (body.isHolding(is -> is.getItem() instanceof CrossbowItem)) {
         CrossbowItem crossbow = (CrossbowItem)usedItem.getItem();
         crossbow.performShooting(body.level(), body, hand, usedItem, crossbowPower, 14 - body.level().getDifficulty().getId() * 4, this.getTarget());
      }

      this.onCrossbowAttackPerformed();
   }
}

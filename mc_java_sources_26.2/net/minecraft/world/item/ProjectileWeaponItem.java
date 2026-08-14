package net.minecraft.world.item;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Unit;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

public abstract class ProjectileWeaponItem extends Item {
   public static final Predicate<ItemStack> ARROW_ONLY = itemStack -> itemStack.is(ItemTags.ARROWS);
   public static final Predicate<ItemStack> ARROW_OR_FIREWORK = ARROW_ONLY.or(itemStack -> itemStack.is(Items.FIREWORK_ROCKET));

   public ProjectileWeaponItem(Item.Properties properties) {
      super(properties);
   }

   public Predicate<ItemStack> getSupportedHeldProjectiles() {
      return this.getAllSupportedProjectiles();
   }

   public abstract Predicate<ItemStack> getAllSupportedProjectiles();

   public static ItemStack getHeldProjectile(LivingEntity entity, Predicate<ItemStack> valid) {
      if (valid.test(entity.getItemInHand(InteractionHand.OFF_HAND))) {
         return entity.getItemInHand(InteractionHand.OFF_HAND);
      } else {
         return valid.test(entity.getItemInHand(InteractionHand.MAIN_HAND)) ? entity.getItemInHand(InteractionHand.MAIN_HAND) : ItemStack.EMPTY;
      }
   }

   public abstract int getDefaultProjectileRange();

   protected void shoot(
      ServerLevel level,
      LivingEntity shooter,
      InteractionHand hand,
      ItemStack weapon,
      List<ItemStack> projectiles,
      float power,
      float uncertainty,
      boolean isCrit,
      @Nullable LivingEntity targetOverride
   ) {
      float maxAngle = EnchantmentHelper.processProjectileSpread(level, weapon, shooter, 0.0F);
      float angleStep = projectiles.size() == 1 ? 0.0F : 2.0F * maxAngle / (projectiles.size() - 1);
      float angleOffset = (projectiles.size() - 1) % 2 * angleStep / 2.0F;
      float direction = 1.0F;

      for (int i = 0; i < projectiles.size(); i++) {
         ItemStack projectile = projectiles.get(i);
         if (!projectile.isEmpty()) {
            float angle = angleOffset + direction * ((i + 1) / 2) * angleStep;
            direction = -direction;
            int index = i;
            Projectile.spawnProjectile(
               this.createProjectile(level, shooter, weapon, projectile, isCrit),
               level,
               projectile,
               projectileEntity -> this.shootProjectile(shooter, projectileEntity, index, power, uncertainty, angle, targetOverride)
            );
            weapon.hurtAndBreak(this.getDurabilityUse(projectile), shooter, hand.asEquipmentSlot());
            if (weapon.isEmpty()) {
               break;
            }
         }
      }
   }

   protected int getDurabilityUse(ItemStack projectile) {
      return 1;
   }

   protected abstract void shootProjectile(LivingEntity var1, Projectile var2, int var3, float var4, float var5, float var6, @Nullable LivingEntity var7);

   protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack weapon, ItemStack projectile, boolean isCrit) {
      ArrowItem arrowItem = projectile.getItem() instanceof ArrowItem arrow ? arrow : (ArrowItem)Items.ARROW;
      AbstractArrow arrow = arrowItem.createArrow(level, projectile, shooter, weapon);
      arrow = this.customArrow(arrow);
      if (isCrit) {
         arrow.setCritArrow(true);
      }

      return arrow;
   }

   protected static List<ItemStack> draw(ItemStack weapon, ItemStack projectile, LivingEntity shooter) {
      if (projectile.isEmpty()) {
         return List.of();
      }

      int numProjectiles = shooter.level() instanceof ServerLevel serverLevel ? EnchantmentHelper.processProjectileCount(serverLevel, weapon, shooter, 1) : 1;
      List<ItemStack> drawn = new ArrayList<>(numProjectiles);
      ItemStack projectileCopy = projectile.copy();
      boolean infinite = projectile.getItem() instanceof ArrowItem arrow && arrow.isInfinite(projectile, weapon, shooter);

      for (int i = 0; i < numProjectiles; i++) {
         ItemStack drawnStack = useAmmo(weapon, i == 0 ? projectile : projectileCopy, shooter, i > 0 || infinite);
         if (!drawnStack.isEmpty()) {
            drawn.add(drawnStack);
         }
      }

      return drawn;
   }

   protected static ItemStack useAmmo(ItemStack weapon, ItemStack projectile, LivingEntity holder, boolean forceInfinite) {
      int ammoToUse = !forceInfinite && !holder.hasInfiniteMaterials() && holder.level() instanceof ServerLevel serverLevel
         ? EnchantmentHelper.processAmmoUse(serverLevel, weapon, projectile, 1)
         : 0;
      if (ammoToUse > projectile.getCount()) {
         return ItemStack.EMPTY;
      }

      if (ammoToUse == 0) {
         ItemStack copy = projectile.copyWithCount(1);
         copy.set(DataComponents.INTANGIBLE_PROJECTILE, Unit.INSTANCE);
         return copy;
      }

      ItemStack used = projectile.split(ammoToUse);
      if (projectile.isEmpty() && holder instanceof Player player) {
         player.getInventory().removeItem(projectile);
      }

      return used;
   }

   public AbstractArrow customArrow(AbstractArrow arrow) {
      return arrow;
   }
}

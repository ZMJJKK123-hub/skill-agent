package net.minecraft.world.item;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Bucketable;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

public class MobBucketItem extends BucketItem {
   private final Supplier<? extends EntityType<? extends Mob>> entityTypeSupplier;
   private final Supplier<? extends SoundEvent> emptySoundSupplier;

   @Deprecated
   public MobBucketItem(EntityType<? extends Mob> type, Fluid content, SoundEvent emptySound, Item.Properties properties) {
      this(() -> type, () -> content, () -> emptySound, properties);
   }

   public MobBucketItem(
      Supplier<? extends EntityType<? extends Mob>> entitySupplier,
      Supplier<? extends Fluid> fluidSupplier,
      Supplier<? extends SoundEvent> soundSupplier,
      Item.Properties properties
   ) {
      super(fluidSupplier, properties);
      this.emptySoundSupplier = soundSupplier;
      this.entityTypeSupplier = entitySupplier;
   }

   @Override
   public void checkExtraContent(@Nullable LivingEntity user, Level level, ItemStack itemStack, BlockPos pos) {
      if (level instanceof ServerLevel serverLevel) {
         this.spawn(serverLevel, itemStack, pos);
         level.gameEvent(user, GameEvent.ENTITY_PLACE, pos);
      }
   }

   @Override
   protected void playEmptySound(@Nullable LivingEntity user, LevelAccessor level, BlockPos pos) {
      level.playSound(user, pos, this.getEmptySound(), SoundSource.NEUTRAL, 1.0F, 1.0F);
   }

   private void spawn(ServerLevel level, ItemStack itemStack, BlockPos spawnPos) {
      Mob mob = this.getFishType().create(level, EntityType.createDefaultStackConfig(level, itemStack, null), spawnPos, EntitySpawnReason.BUCKET, true, false);
      if (mob instanceof Bucketable bucketable) {
         CustomData entityData = itemStack.getOrDefault(DataComponents.BUCKET_ENTITY_DATA, CustomData.EMPTY);
         bucketable.loadFromBucketTag(entityData.copyTag());
         bucketable.setFromBucket(true);
      }

      if (mob != null) {
         level.addFreshEntityWithPassengers(mob);
         mob.playAmbientSound();
      }
   }

   protected EntityType<? extends Mob> getFishType() {
      return (EntityType<? extends Mob>)this.entityTypeSupplier.get();
   }

   protected SoundEvent getEmptySound() {
      return this.emptySoundSupplier.get();
   }

   @Override
   public boolean emptyContents(@Nullable LivingEntity user, Level level, BlockPos pos, @Nullable BlockHitResult hitResult) {
      if (this.getContent() == Fluids.EMPTY) {
         this.playEmptySound(user, level, pos);
         return true;
      } else {
         return super.emptyContents(user, level, pos, hitResult);
      }
   }

   @Override
   public ClipContext.Fluid getFluidContext() {
      return ClipContext.Fluid.NONE;
   }
}

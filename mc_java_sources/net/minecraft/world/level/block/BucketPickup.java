package net.minecraft.world.level.block;

import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.extensions.IForgeBucketPickup;
import org.jspecify.annotations.Nullable;

public interface BucketPickup extends IForgeBucketPickup {
   ItemStack pickupBlock(@Nullable LivingEntity var1, LevelAccessor var2, BlockPos var3, BlockState var4);

   @Deprecated
   Optional<SoundEvent> getPickupSound();
}

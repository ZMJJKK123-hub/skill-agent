package net.minecraft.world.item;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.extensions.IForgeDispensibleContainerItem;
import org.jspecify.annotations.Nullable;

public interface DispensibleContainerItem extends IForgeDispensibleContainerItem {
   default void checkExtraContent(@Nullable LivingEntity user, Level level, ItemStack itemStack, BlockPos pos) {
   }

   @Deprecated
   boolean emptyContents(@Nullable LivingEntity var1, Level var2, BlockPos var3, @Nullable BlockHitResult var4);
}

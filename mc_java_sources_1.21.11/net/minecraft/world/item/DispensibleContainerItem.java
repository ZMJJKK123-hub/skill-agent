package net.minecraft.world.item;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

public interface DispensibleContainerItem extends net.minecraftforge.common.extensions.IForgeDispensibleContainerItem {
    default void checkExtraContent(@Nullable LivingEntity p_391486_, Level p_150818_, ItemStack p_150819_, BlockPos p_150820_) {
    }

    @Deprecated //Forge: use the ItemStack sensitive version
    boolean emptyContents(@Nullable LivingEntity p_396492_, Level p_150822_, BlockPos p_150823_, @Nullable BlockHitResult p_150824_);
}

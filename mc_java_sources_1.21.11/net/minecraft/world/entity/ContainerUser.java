package net.minecraft.world.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.ContainerOpenersCounter;

public interface ContainerUser {
    boolean hasContainerOpen(ContainerOpenersCounter p_426586_, BlockPos p_424102_);

    double getContainerInteractionRange();

    default LivingEntity getLivingEntity() {
        if (this instanceof LivingEntity) {
            return (LivingEntity)this;
        } else {
            throw new IllegalStateException("A container user must be a LivingEntity");
        }
    }
}

package net.minecraft.world.entity.vehicle.boat;

import java.util.function.Supplier;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;

public class ChestBoat extends AbstractChestBoat {
    public ChestBoat(EntityType<? extends ChestBoat> p_455226_, Level p_456059_, Supplier<Item> p_455414_) {
        super(p_455226_, p_456059_, p_455414_);
    }

    @Override
    protected double rideHeight(EntityDimensions p_451474_) {
        return p_451474_.height() / 3.0F;
    }

    private net.minecraftforge.common.util.LazyOptional<?> itemHandler = net.minecraftforge.common.util.LazyOptional.of(() -> new net.minecraftforge.items.wrapper.InvWrapper(this));

    @Override
    public <T> net.minecraftforge.common.util.LazyOptional<T> getCapability(net.minecraftforge.common.capabilities.Capability<T> capability, @org.jetbrains.annotations.Nullable net.minecraft.core.Direction facing) {
        if (capability == net.minecraftforge.common.capabilities.ForgeCapabilities.ITEM_HANDLER && this.isAlive()) {
             return itemHandler.cast();
        }
        return super.getCapability(capability, facing);
    }

    @Override
    public void invalidateCaps() {
        super.invalidateCaps();
        itemHandler.invalidate();
    }

    @Override
    public void reviveCaps() {
        super.reviveCaps();
        itemHandler = net.minecraftforge.common.util.LazyOptional.of(() -> new net.minecraftforge.items.wrapper.InvWrapper(this));
    }
}

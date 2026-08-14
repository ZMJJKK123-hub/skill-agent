package net.minecraft.world.entity.vehicle.boat;

import java.util.function.Supplier;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.wrapper.InvWrapper;
import org.jetbrains.annotations.Nullable;

public class ChestBoat extends AbstractChestBoat {
   private LazyOptional<?> itemHandler = LazyOptional.of(() -> new InvWrapper(this));

   public ChestBoat(EntityType<? extends ChestBoat> type, Level level, Supplier<Item> dropItem) {
      super(type, level, dropItem);
   }

   @Override
   protected double rideHeight(EntityDimensions dimensions) {
      return dimensions.height() / 3.0F;
   }

   @Override
   public <T> LazyOptional<T> getCapability(Capability<T> capability, @Nullable Direction facing) {
      return capability == ForgeCapabilities.ITEM_HANDLER && this.isAlive() ? this.itemHandler.cast() : super.getCapability(capability, facing);
   }

   @Override
   public void invalidateCaps() {
      super.invalidateCaps();
      this.itemHandler.invalidate();
   }

   @Override
   public void reviveCaps() {
      super.reviveCaps();
      this.itemHandler = LazyOptional.of(() -> new InvWrapper(this));
   }
}

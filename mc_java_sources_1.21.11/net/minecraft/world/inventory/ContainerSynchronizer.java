package net.minecraft.world.inventory;

import java.util.List;
import net.minecraft.world.item.ItemStack;

public interface ContainerSynchronizer {
    void sendInitialData(AbstractContainerMenu p_392895_, List<ItemStack> p_393946_, ItemStack p_392183_, int[] p_397284_);

    void sendSlotChange(AbstractContainerMenu p_150530_, int p_150531_, ItemStack p_150532_);

    void sendCarriedChange(AbstractContainerMenu p_150533_, ItemStack p_150534_);

    void sendDataChange(AbstractContainerMenu p_150527_, int p_150528_, int p_150529_);

    RemoteSlot createSlot();
}

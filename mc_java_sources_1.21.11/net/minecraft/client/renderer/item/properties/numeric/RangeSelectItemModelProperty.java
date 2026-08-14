package net.minecraft.client.renderer.item.properties.numeric;

import com.mojang.serialization.MapCodec;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.entity.ItemOwner;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface RangeSelectItemModelProperty {
    float get(ItemStack p_376822_, @Nullable ClientLevel p_376153_, @Nullable ItemOwner p_430583_, int p_376174_);

    MapCodec<? extends RangeSelectItemModelProperty> type();
}

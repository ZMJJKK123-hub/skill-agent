// Starter: SwapGame minimal mod skeleton (copy into src/main/java/com/swapgame/SwapGameMod.java)
// This is intentionally minimal: it registers the chaos_book item so the project compiles.
// Expand from here: config, GUI, game state, HUD, packets.
package com.swapgame;

import net.minecraft.world.item.Item;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(SwapGameMod.MODID)
public class SwapGameMod {
    public static final String MODID = "swapgame";
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

    public static final RegistryObject<Item> CHAOS_BOOK = ITEMS.register("chaos_book",
        () -> new Item(new Item.Properties().setId(ITEMS.key("chaos_book")).stacksTo(1)));

    public SwapGameMod() {
        ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());
    }
}
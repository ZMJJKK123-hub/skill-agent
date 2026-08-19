// Starter: simple item main mod class (copy into src/main/java/com/<pkg>/<YourMod>.java)
// Rename package, modid, item id.
package com.rubymod;

import net.minecraft.world.item.Item;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(RubyMod.MODID)
public class RubyMod {
    public static final String MODID = "rubymod";
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

    public static final RegistryObject<Item> RUBY = ITEMS.register("ruby",
        () -> new Item(new Item.Properties().setId(ITEMS.key("ruby"))));

    public RubyMod() {
        ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());
    }
}
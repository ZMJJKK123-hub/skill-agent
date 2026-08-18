// Starter: Copper Tools main mod class (copy into src/main/java/com/<pkg>/CopperToolsMod.java)
// Rename package, modid, and paste into your @Mod project. It registers sword/pickaxe/axe.
package com.coppertools;

import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(CopperToolsMod.MODID)
public class CopperToolsMod {
    public static final String MODID = "coppertools";
    public static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

    public static final RegistryObject<Item> COPPER_SWORD =
        ITEMS.register("copper_sword", () -> new Item(new Item.Properties()
            .setId(ITEMS.key("copper_sword"))
            .sword(ToolMaterial.COPPER, 3.0F, -2.4F)));

    public static final RegistryObject<Item> COPPER_PICKAXE =
        ITEMS.register("copper_pickaxe", () -> new Item(new Item.Properties()
            .setId(ITEMS.key("copper_pickaxe"))
            .pickaxe(ToolMaterial.COPPER, 1.0F, -2.8F)));

    public static final RegistryObject<Item> COPPER_AXE =
        ITEMS.register("copper_axe", () -> new AxeItem(ToolMaterial.COPPER, 7.0F, -3.2F,
            new Item.Properties().setId(ITEMS.key("copper_axe"))));

    public CopperToolsMod() {
        ITEMS.register(FMLJavaModLoadingContext.get().getModBusGroup());
    }
}
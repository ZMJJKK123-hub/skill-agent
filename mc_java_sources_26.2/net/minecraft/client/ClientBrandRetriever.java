package net.minecraft.client;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.internal.BrandingControl;

@OnlyIn(Dist.CLIENT)
public class ClientBrandRetriever {
   public static final String VANILLA_NAME = "vanilla";

   public static String getClientModName() {
      return BrandingControl.getBranding();
   }
}

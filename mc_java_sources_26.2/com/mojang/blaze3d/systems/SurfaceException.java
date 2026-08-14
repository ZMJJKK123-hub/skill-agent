package com.mojang.blaze3d.systems;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class SurfaceException extends Exception {
   public SurfaceException(String message) {
      super(message);
   }

   public SurfaceException(Throwable cause) {
      super(cause);
   }
}

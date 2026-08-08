package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.GLFWErrorCapture;
import com.mojang.blaze3d.shaders.GpuDebugOptions;
import com.mojang.blaze3d.shaders.ShaderSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface GpuBackend {
   String getName();

   void setWindowHints();

   void handleWindowCreationErrors(GLFWErrorCapture.Error var1) throws BackendCreationException;

   GpuDevice createDevice(long var1, ShaderSource var3, GpuDebugOptions var4, Runnable var5) throws BackendCreationException;
}

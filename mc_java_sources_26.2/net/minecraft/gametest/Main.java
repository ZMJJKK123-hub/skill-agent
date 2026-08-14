package net.minecraft.gametest;

import net.minecraft.SharedConstants;
import net.minecraft.gametest.framework.GameTestMainUtil;

public class Main {
   public static void main(String[] args) throws Exception {
      System.setProperty("forge.enableGameTest", "true");
      System.setProperty("forge.gameTestServer", "true");
      SharedConstants.tryDetectVersion();
      GameTestMainUtil.runGameTestServer(args, path -> {});
   }
}

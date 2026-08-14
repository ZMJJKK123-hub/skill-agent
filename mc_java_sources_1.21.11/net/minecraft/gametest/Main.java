package net.minecraft.gametest;

import net.minecraft.SharedConstants;
import net.minecraft.gametest.framework.GameTestMainUtil;
import net.minecraft.obfuscate.DontObfuscate;

public class Main {
    @DontObfuscate
    public static void main(String[] p_393417_) throws Exception {
        System.setProperty("forge.enableGameTest", "true");
        System.setProperty("forge.gameTestServer", "true");
        SharedConstants.tryDetectVersion();
        GameTestMainUtil.runGameTestServer(p_393417_, p_393535_ -> {});
    }
}

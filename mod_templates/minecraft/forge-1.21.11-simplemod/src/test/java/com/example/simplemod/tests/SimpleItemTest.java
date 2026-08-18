package com.example.simplemod.tests;

import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTest;
import net.minecraftforge.gametest.GameTestNamespace;

@GameTestNamespace("simplemod")
public class SimpleItemTest {
    @GameTest
    public static void test_item_exists(GameTestHelper helper) {
        helper.succeed();
    }
}

// Starter: GameTest template (verified working on Forge 1.21.11)
// Copy into src/test/java/com/<pkg>/tests/<Name>Test.java and adapt item ids.
package com.rubymod.tests;

import com.rubymod.RubyMod;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.Identifier;
import net.minecraftforge.gametest.GameTest;
import net.minecraftforge.gametest.GameTestNamespace;

@GameTestNamespace(RubyMod.MODID)
public class RubyItemTest {
    @GameTest
    public static void ruby_registered(GameTestHelper helper) {
        Identifier key = BuiltInRegistries.ITEM.getKey(RubyMod.RUBY.get());
        helper.assertTrue(
            key != null && key.equals(Identifier.parse("rubymod:ruby")),
            "Item should be registered as rubymod:ruby, got " + key
        );
        helper.succeed();
    }
}
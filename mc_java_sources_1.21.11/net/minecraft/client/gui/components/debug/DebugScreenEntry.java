package net.minecraft.client.gui.components.debug;

import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface DebugScreenEntry {
    void display(DebugScreenDisplayer p_427172_, @Nullable Level p_427695_, @Nullable LevelChunk p_423462_, @Nullable LevelChunk p_426762_);

    default boolean isAllowed(boolean p_424604_) {
        return !p_424604_;
    }

    default DebugEntryCategory category() {
        return DebugEntryCategory.SCREEN_TEXT;
    }
}

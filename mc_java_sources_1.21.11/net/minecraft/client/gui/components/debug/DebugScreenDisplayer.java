package net.minecraft.client.gui.components.debug;

import java.util.Collection;
import net.minecraft.resources.Identifier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface DebugScreenDisplayer {
    void addPriorityLine(String p_429600_);

    void addLine(String p_425268_);

    void addToGroup(Identifier p_451284_, Collection<String> p_458137_);

    void addToGroup(Identifier p_460199_, String p_454980_);
}

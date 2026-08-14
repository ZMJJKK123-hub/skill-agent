package net.minecraft.client.gui.screens.dialog;

import java.util.Optional;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.Holder;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.ServerLinks;
import net.minecraft.server.dialog.Dialog;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface DialogConnectionAccess {
    void disconnect(Component p_405901_);

    void runCommand(String p_407865_, @Nullable Screen p_407353_);

    void openDialog(Holder<Dialog> p_407019_, @Nullable Screen p_410729_);

    void sendCustomAction(Identifier p_458846_, Optional<Tag> p_405814_);

    ServerLinks serverLinks();
}

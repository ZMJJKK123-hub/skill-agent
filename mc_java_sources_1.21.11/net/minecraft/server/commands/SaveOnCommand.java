package net.minecraft.server.commands;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.SimpleCommandExceptionType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

public class SaveOnCommand {
    private static final SimpleCommandExceptionType ERROR_ALREADY_ON = new SimpleCommandExceptionType(Component.translatable("commands.save.alreadyOn"));

    public static void register(CommandDispatcher<CommandSourceStack> p_138293_) {
        p_138293_.register(Commands.literal("save-on").requires(Commands.hasPermission(Commands.LEVEL_OWNERS)).executes(p_421347_ -> {
            CommandSourceStack commandsourcestack = p_421347_.getSource();
            boolean flag = commandsourcestack.getServer().setAutoSave(true);
            if (!flag) {
                throw ERROR_ALREADY_ON.create();
            } else {
                commandsourcestack.sendSuccess(() -> Component.translatable("commands.save.enabled"), true);
                return 1;
            }
        }));
    }
}

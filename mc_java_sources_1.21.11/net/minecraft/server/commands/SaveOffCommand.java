package net.minecraft.server.commands;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.SimpleCommandExceptionType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

public class SaveOffCommand {
    private static final SimpleCommandExceptionType ERROR_ALREADY_OFF = new SimpleCommandExceptionType(Component.translatable("commands.save.alreadyOff"));

    public static void register(CommandDispatcher<CommandSourceStack> p_138285_) {
        p_138285_.register(Commands.literal("save-off").requires(Commands.hasPermission(Commands.LEVEL_OWNERS)).executes(p_421346_ -> {
            CommandSourceStack commandsourcestack = p_421346_.getSource();
            boolean flag = commandsourcestack.getServer().setAutoSave(false);
            if (!flag) {
                throw ERROR_ALREADY_OFF.create();
            } else {
                commandsourcestack.sendSuccess(() -> Component.translatable("commands.save.disabled"), true);
                return 1;
            }
        }));
    }
}
